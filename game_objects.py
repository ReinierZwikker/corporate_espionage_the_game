from OpenGL.GL import *
from game_util import read_texture
from PIL import Image


class SimpleObject:
    """
    Generates an object that can be manipulated and rendered.
    Requires definition of the object type that should be initialised. Current supported types are:
        - wireframe cube
        - solid cube
        - wire_plane
        - solid_plane
        - triangle
    """

    def __init__(self, object_type='solid_cube'):
        """
        This function initialises the object with all vectors as 0 and a white color. It also generates vertex maps.
        :param object_type: Type of object that should be generated ('wire_cube', 'solid_cube', 'wire_plane', 'solid_plane', 'triangle')
        """
        self.supported_object_types = ('wire_cube', 'solid_cube', 'wire_plane', 'solid_plane', 'triangle')
        if object_type in self.supported_object_types:
            self.object_type = object_type

        self.location = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.size = [1, 1, 1]

        self.location_speed = [0, 0, 0]
        self.rotation_speed = [0, 0, 0]
        self.size_speed = [0, 0, 0]

        self.color = [1, 1, 1, 1]

        self.texture_id = None
        self.texture_enabled = False

        self.cube_vertices = ((1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1), (-1, 1, 1), (-1, -1, -1), (-1, -1, 1), (-1, 1, -1))
        self.cube_normals = (())
        self.cube_edges = ((0, 1), (0, 3), (0, 4), (1, 2), (1, 7), (2, 5), (2, 3), (3, 6), (4, 6), (4, 7), (5, 6), (5, 7))
        self.cube_quads = ((0, 3, 6, 4), (2, 5, 6, 3), (1, 2, 5, 7), (1, 0, 4, 7), (7, 4, 6, 5), (2, 3, 0, 1))
        self.cube_texture_coordinates = ((0, 0), (1, 0), (0, 0), (1, 0), (0, 1), (0, 1), (1, 1), (1, 1))

        self.plane_vertices = ((1, 0, -1), (1, 0, 1), (-1, 0, 1), (-1, 0, -1))
        self.plane_normals = ((0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0))
        self.plane_edges = ((0, 1), (0, 3), (1, 2), (2, 3))
        self.plane_quad = (0, 1, 2, 3)
        self.plane_texture_coordinates = ((1, 0), (1, 1), (0, 1), (0, 0))

        self.triangle_vertices = ((0, 0, 0), (-1, 0, 1), (-1, 0, -1))
        self.triangle_edges = ((0, 1), (1, 2), (2, 0))
        self.triangle_tri = (0, 1, 2)

    def make_object_opaque(self):
        if self.object_type == 'wire_cube':
            self.wire_cube()
        if self.object_type == 'solid_cube':
            self.solid_cube()
        if self.object_type == 'wire_plane':
            self.wire_plane()
        if self.object_type == 'solid_plane':
            self.solid_plane()

    def make_object_translucent(self):
        if self.object_type == 'triangle':
            self.triangle()

    def solid_cube(self):
        # Push new matrix over main matrix (Translational statements take effect in reverse)
        glPushMatrix()
        # Move to object location
        glTranslatef(self.location[0], self.location[1], self.location[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(self.size[0], self.size[1], self.size[2])
        glColor4f(self.color[0], self.color[1], self.color[2], 1)
        if self.texture_enabled:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_QUADS)
        for cube_quad in self.cube_quads:
            for cube_vertex in cube_quad:
                if self.texture_enabled:
                    glTexCoord2fv(self.cube_texture_coordinates[cube_vertex])
                glVertex3fv(self.cube_vertices[cube_vertex])
        glEnd()
        glColor4f(1, 1, 1, 1)
        if self.texture_enabled:
            glDisable(GL_TEXTURE_2D)
        glPopMatrix()

    def wire_cube(self):
        # Same as solid_cube, but different object
        glPushMatrix()
        glTranslatef(self.location[0], self.location[1], self.location[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(self.size[0], self.size[1], self.size[2])
        glBegin(GL_LINES)
        for cube_edge in self.cube_edges:
            for cube_vertex in cube_edge:
                glVertex3fv(self.cube_vertices[cube_vertex])
        glEnd()
        glColor3f(1, 1, 1)
        glPopMatrix()

    def solid_plane(self):
        # Same as solid_cube, but different object
        glPushMatrix()
        glTranslatef(self.location[0], self.location[1], self.location[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(self.size[0], self.size[1], self.size[2])
        glColor3f(self.color[0], self.color[1], self.color[2])
        if self.texture_enabled:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_QUADS)
        for plane_vertex in self.plane_quad:
            if self.texture_enabled:
                glTexCoord2fv(self.plane_texture_coordinates[plane_vertex])
            glVertex3fv(self.plane_vertices[plane_vertex])
        glEnd()
        glColor3f(1, 1, 1)
        if self.texture_enabled:
            glDisable(GL_TEXTURE_2D)
        glPopMatrix()

    def wire_plane(self):
        # Same as solid_cube, but different object
        glPushMatrix()
        glTranslatef(self.location[0], self.location[1], self.location[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(self.size[0], self.size[1], self.size[2])
        glColor3f(self.color[0], self.color[1], self.color[2])
        glBegin(GL_LINES)
        for plane_edge in self.plane_edges:
            for plane_vertex in plane_edge:
                glVertex3fv(self.plane_vertices[plane_vertex])
        glEnd()
        glColor3f(1, 1, 1)
        glPopMatrix()

    def triangle(self):
        # Same as solid_cube, but different object
        glPushMatrix()
        glTranslatef(self.location[0], self.location[1], self.location[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(self.size[0], self.size[1], self.size[2])
        glColor4f(self.color[0], self.color[1], self.color[2], 0.4)
        if self.texture_enabled:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_TRIANGLES)
        for triangle_vertex in self.triangle_tri:
            glVertex3fv(self.triangle_vertices[triangle_vertex])
        glEnd()
        # glColor4f(self.color[0], self.color[1], self.color[2], 1)
        # glBegin(GL_LINES)
        # for triangle_edge in self.triangle_edges:
        #     for triangle_vertex in triangle_edge:
        #         glVertex3fv(self.triangle_vertices[triangle_vertex])
        # glEnd()
        glColor4f(1, 1, 1, 1)
        if self.texture_enabled:
            glDisable(GL_TEXTURE_2D)
        glPopMatrix()

    def update_object(self):
        self.transform(self.location_speed)
        self.rotate(self.rotation_speed)
        self.scale(self.size_speed)

    def transform(self, applied):
        self.location = [self.location[i] + applied[i] for i in range(len(self.location))]

    def rotate(self, applied):
        self.rotation = [self.rotation[i] + applied[i] for i in range(len(self.rotation))]

    def scale(self, applied):
        self.size = [self.size[i] + applied[i] for i in range(len(self.size))]

    def set_location(self, applied):
        self.location = [applied[i] for i in range(len(self.location))]

    def set_rotation(self, applied):
        self.rotation = [applied[i] for i in range(len(self.rotation))]

    def set_scale(self, applied):
        self.size = [applied[i] for i in range(len(self.size))]

    def transform_speed(self, applied):
        self.location_speed = [self.location_speed[i] + applied[i] for i in range(len(self.location_speed))]

    def rotate_speed(self, applied):
        self.rotation_speed = [self.rotation_speed[i] + applied[i] for i in range(len(self.rotation_speed))]

    def scale_speed(self, applied):
        self.size_speed = [self.size_speed[i] + applied[i] for i in range(len(self.size_speed))]

    def set_transform_speed(self, applied):
        self.location_speed = applied

    def set_rotate_speed(self, applied):
        self.rotation_speed = applied

    def set_scale_speed(self, applied):
        self.size_speed = applied

    def set_color(self, applied):
        if len(applied) == 3:
            self.color = [applied[0], applied[1], applied[2], 1]
        if len(applied) == 4:
            self.color = applied

    def set_texture(self, texture_filename):
        self.texture_id = read_texture(texture_filename)
        self.texture_enabled = True

    def unset_texture(self):
        self.texture_enabled = False


class Parent:  # AKA Jozef

    def __init__(self):
        self.location = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.size = [1, 1, 1]
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.pop(child)

    def make_object_opaque(self):
        glPushMatrix()
        glTranslatef(self.location[0], self.location[1], self.location[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(self.size[0], self.size[1], self.size[2])
        for child in self.children:
            child.make_object_opaque()
        glPopMatrix()

    def make_object_translucent(self):
        glPushMatrix()
        glTranslatef(self.location[0], self.location[1], self.location[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(self.size[0], self.size[1], self.size[2])
        for child in self.children:
            child.make_object_translucent()
        glPopMatrix()

    def update_object(self):
        for child in self.children:
            child.update_object()

    def transform(self, applied):
        self.location = [self.location[i] + applied[i] for i in range(len(self.location))]

    def rotate(self, applied):
        self.rotation = [self.rotation[i] + applied[i] for i in range(len(self.rotation))]

    def scale(self, applied):
        self.size = [self.size[i] + applied[i] for i in range(len(self.size))]

    def set_location(self, applied):
        self.location = [applied[i] for i in range(len(self.location))]

    def set_rotation(self, applied):
        self.rotation = [applied[i] for i in range(len(self.rotation))]

    def set_scale(self, applied):
        self.size = [applied[i] for i in range(len(self.size))]

    def set_color(self, color):
        for child in self.children:
            child.set_color(color)


class UIElement:

    def __init__(self, texture_filename, activated=False):
        self.plane_vertices = ((2, 0, -1), (2, 0, 1), (-2, 0, 1), (-2, 0, -1))
        self.plane_quad = (0, 1, 2, 3)
        self.plane_texture_coordinates = ((1, 0), (1, 1), (0, 1), (0, 0))

        self.location = (0, 0, 0)
        self.size = [1, 1, 1]

        self.offset = (0, 0)

        self.texture_id = read_texture(texture_filename)

        self.activated = activated

    def make_object_opaque(self):
        pass

    def make_object_translucent(self):
        if self.activated:
            glPushMatrix()
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTranslatef(self.location[0], self.location[1], self.location[2])
            glScalef(self.size[0], self.size[1], self.size[2])
            glBegin(GL_QUADS)
            for vertex in self.plane_quad:
                glTexCoord2fv(self.plane_texture_coordinates[vertex])
                glVertex3fv(self.plane_vertices[vertex])
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()

    def set_location(self, applied):
        self.location = [applied[i] for i in range(len(self.location))]

    def set_offset(self, applied):
        self.offset = [applied[i] for i in range(len(self.offset))]

    def set_scale(self, applied):
        self.size = [applied[i] for i in range(len(self.size))]

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

    def flip(self):
        self.activated = not self.activated


class TextElement:

    # Scratch build text rendering engine

    def __init__(self, text, activated=False, font='consolas'):
        self.text = text
        self.activated = activated
        self.font = font
        self.location = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.size = [1, 1, 1]
        self.offset = (0, 0)

        if font == 'consolas':
            # Load font bitmap
            self.texture_id = read_texture('./assets/UI/consolas_font.png')
            self.letter_height_pixel = 72
            # width of each letter in the bitmap
            self.letter_width_pixels = [47, 42, 44, 47, 40, 42, 46, 47, 41, 43, 48, 40, 48, 41, 47, 41, 47, 42, 44, 45, 41, 46, 43, 44, 47, 42, 44,
                                        44, 43, 47, 42, 44, 43, 44, 44, 44]
            img = Image.open('./assets/UI/consolas_font.png')
            # get letter bounding boxes
            self.letter_width_uv = [width_pixel / img.size[0] for width_pixel in self.letter_width_pixels]
            self.letter_height_uv = self.letter_height_pixel / img.size[1]
            self.letter_height = self.letter_height_uv
            self.letter_width = [0.7 for _ in self.letter_width_uv]
            img.close()

        self.letters = []
        self.letter_positions = []
        self.letter_vertices = []
        self.letter_face = (0, 1, 2, 3)
        self.letter_texture_coordinates = []

        self.generate_letters()

    def generate_letters(self):
        for letter in self.text:
            char = ord(letter) - 96
            if 1 <= char <= 26:
                self.letters.append(char)
            if char == -64:
                self.letters.append(0)
            if -47 <= char <= -39:
                self.letters.append(char + 48 + 26)
            if char == -48:
                self.letters.append(10 + 26)
            if char == -49:
                self.letters.append(-1)
        caret_position = [0, 0]
        for letter in self.letters:
            if letter == -1:
                # New line: move caret back to beginning and one line down
                caret_position[1] += 1
                caret_position[0] = 0
                self.letter_texture_coordinates.append(None)
                self.letter_vertices.append(None)
            elif letter == 0:
                # Space: move caret one space to the right
                caret_position[0] += 1
                self.letter_texture_coordinates.append(None)
                self.letter_vertices.append(None)
            else:
                uv_start_position = (sum(self.letter_width_uv[0:letter - 1]), 0)
                uv_end_position = (sum(self.letter_width_uv[0:letter]), self.letter_height_uv)
                self.letter_texture_coordinates.append(((uv_start_position[0], uv_start_position[1]),
                                                        (uv_end_position[0], uv_start_position[1]),
                                                        (uv_end_position[0], uv_end_position[1]),
                                                        (uv_start_position[0], uv_end_position[1])))
                letter_center_position = ((self.letter_width[letter - 1] / 2) + (caret_position[0] * self.letter_width[letter - 1]),
                                          (self.letter_height / 2) + (caret_position[1] * self.letter_height))
                self.letter_vertices.append(((letter_center_position[0] - self.letter_width[letter - 1] / 2, 0,
                                              letter_center_position[1] - self.letter_height / 2),

                                             (letter_center_position[0] + self.letter_width[letter - 1] / 2, 0,
                                              letter_center_position[1] - self.letter_height / 2),

                                             (letter_center_position[0] + self.letter_width[letter - 1] / 2, 0,
                                              letter_center_position[1] + self.letter_height / 2),

                                             (letter_center_position[0] - self.letter_width[letter - 1] / 2, 0,
                                              letter_center_position[1] + self.letter_height / 2)))
                caret_position[0] += 1

    def make_object_opaque(self):
        pass

    def make_object_translucent(self):
        if self.activated:
            glPushMatrix()
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTranslatef(self.location[0], self.location[1], self.location[2])
            glRotatef(self.rotation[0], 1, 0, 0)
            glRotatef(self.rotation[1], 0, 1, 0)
            glRotatef(self.rotation[2], 0, 0, 1)
            glScalef(self.size[0], self.size[1], self.size[2])
            glBegin(GL_QUADS)
            for letter_i in range(len(self.letters)):
                if self.letters[letter_i] > 0:
                    for vertex in self.letter_face:
                        glTexCoord2fv(self.letter_texture_coordinates[letter_i][vertex])
                        glVertex3fv(self.letter_vertices[letter_i][vertex])
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()

    def set_location(self, applied):
        self.location = [applied[i] for i in range(len(self.location))]

    def set_offset(self, applied):
        self.offset = [applied[i] for i in range(len(self.offset))]

    def rotate(self, applied):
        self.rotation = [self.rotation[i] + applied[i] for i in range(len(self.rotation))]

    def set_rotation(self, applied):
        self.rotation = [applied[i] for i in range(len(self.rotation))]

    def set_scale(self, applied):
        self.size = [applied[i] for i in range(len(self.size))]

    def set_text(self, text):
        self.text = text
        self.generate_letters()

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

    def flip_activated(self):
        self.activated = not self.activated
