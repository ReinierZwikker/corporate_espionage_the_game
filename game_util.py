import numpy as np
from PIL import Image

from OpenGL.GL import *
from OpenGL.GLUT import *


textures = []


def move_distance_player(duration, sprint=False):
    if sprint:
        return 2 * duration ** 0.74
    else:
        return 1 * duration ** 0.74


def move_distance_enemy(duration):
    return 0.6 * duration ** 0.74


def clamp(value, low_limit, high_limit):
    if value > high_limit:
        return high_limit
    if value < low_limit:
        return low_limit
    else:
        return value


def read_texture(filename):
    global textures
    try:
        return textures.index(filename) + 1
    except ValueError:
        textures.append(filename)
        img = Image.open(filename)
        img_data = np.array(list(img.getdata()), np.int32)
        texture_id = glGenTextures(1)
        # print(f'New texture loaded, currently loaded {len(textures)} texture(s) at texture id {texture_id}')
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.size[0], img.size[1], 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        img.close()
        return texture_id


class RenderQueue:
    # The render queue runs the render function 'make_object()' for every object that is subscribed to the queue.
    def __init__(self):
        self.queue = []
        self.focus = None

    def subscribe(self, render_object):
        self.queue.append(render_object)

    def unsubscribe(self, render_object):
        self.queue.remove(render_object)

    def set_camera_focus(self, focus_object):
        self.focus = focus_object

    def run_queue(self):
        for render_object in self.queue:
            try:
                render_object.make_object_opaque()
            except AttributeError as e:
                print("Error", e)
            try:
                render_object.make_object_translucent()
            except AttributeError as e:
                print("Error", e)

    def run_queue_culled(self):
        # Only renders object if close enough to the player and thus the camera, to increase performance (by a lot).
        # Renders opaque objects first and translucent objects second, to make sure proper blending occurs.
        for render_object in self.queue:
            try:
                if abs(self.focus.location[0] - render_object.location[0]) < 15 and abs(self.focus.location[1] - render_object.location[2]) < 10:
                    render_object.make_object_opaque()
            except AttributeError:
                pass
            except NameError:
                print("Culling failed, reverting to normal rendering mode.")
                render_object.make_object_opaque()
        for render_object in self.queue:
            try:
                if abs(self.focus.location[0] - render_object.location[0]) < 15 and abs(self.focus.location[1] - render_object.location[2]) < 10:
                    render_object.make_object_translucent()
            except AttributeError:
                pass
            except NameError:
                print("Culling failed, reverting to normal rendering mode.")
                render_object.make_object_translucent()

    def flush(self):
        self.queue = []


class UpdateQueue:
    # The update queue runs the update function 'update_object()' for every object that is subscribed to the queue.
    def __init__(self):
        self.queue = []

    def subscribe(self, render_object):
        self.queue.append(render_object)

    def unsubscribe(self, render_object):
        self.queue.remove(render_object)

    def run_queue(self, previous_frame_duration):
        for render_object in self.queue:
            try:
                render_object.update_object(previous_frame_duration)
            except TypeError:
                render_object.update_object()
            except AttributeError as e:
                print("Error", e)

    def flush(self):
        self.queue = []
