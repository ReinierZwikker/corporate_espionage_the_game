"""
CORPORATE ESPIONAGE: THE GAME
BY REINIER ZWIKKER

for the competition project
"""

# Package imports
import pygame as pg
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from timeit import default_timer as timer

# Local imports
from game_util import RenderQueue, UpdateQueue, move_distance_player
from game_objects import UIElement
from game import Game


def run():
    # ------- SETTINGS -------

    # Window size
    width = 1920  # pixels
    height = 1080  # pixels
    fov = 60  # deg

    target_frame_rate = 45

    # Set to true to analyze timing and grid borders
    verbose_mode = True

    # ------------------------
    window_size = (width, height)

    target_frame_duration = target_frame_rate ** -1
    previous_frame_duration = target_frame_duration

    # Initialising PyGame
    pg.init()
    pg.display.set_caption('CORPORATE ESPIONAGE: THE GAME')
    pg.display.set_mode(window_size, FULLSCREEN | DOUBLEBUF | OPENGL)
    # Clearing the screen
    glClearColor(0.3, 0.3, 0.3, 0)
    glClearDepthf(1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    pg.display.flip()

    # Loading sounds
    pg.mixer.init(frequency=44100)
    theme_sound = pg.mixer.Sound('./assets/music/theme.wav')  # Theme from Mission:Impossible
    succes_sound = pg.mixer.Sound('./assets/music/succes.wav')  # Who Likes to Party from Kevin MacLeod
    failed_sounds = [pg.mixer.Sound('./assets/music/failed-001.wav'),  # Star Wars
                     pg.mixer.Sound('./assets/music/failed-002.wav'),  # Boiiing
                     pg.mixer.Sound('./assets/music/failed-003.wav'),  # Price is Wrong
                     pg.mixer.Sound('./assets/music/failed-004.wav')]  # Scratch

    # Setting the camera frustum
    gluPerspective(fov, (window_size[0] / window_size[1]), 0.1, 100)

    # Setting object occlusion parameters
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)
    glDepthFunc(GL_LEQUAL)
    glDepthRangef(0, 1)

    # Setting translucency parameters
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def event_handler():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    game.end_round()
                    game.start_round()
            else:
                pass
        keys = pg.key.get_pressed()
        mods = pg.key.get_mods()
        if keys[pg.K_w]:
            if mods & pg.KMOD_SHIFT:
                game.player.move(move_distance_player(previous_frame_duration, True), (0, 1))
            else:
                game.player.move(move_distance_player(previous_frame_duration, False), (0, 1))
        if keys[pg.K_s]:
            if mods & pg.KMOD_SHIFT:
                game.player.move(move_distance_player(previous_frame_duration, True), (0, -1))
            else:
                game.player.move(move_distance_player(previous_frame_duration, False), (0, -1))
        if keys[pg.K_a]:
            if mods & pg.KMOD_SHIFT:
                game.player.move(move_distance_player(previous_frame_duration, True), (1, 0))
            else:
                game.player.move(move_distance_player(previous_frame_duration, False), (1, 0))
        if keys[pg.K_d]:
            if mods & pg.KMOD_SHIFT:
                game.player.move(move_distance_player(previous_frame_duration, True), (-1, 0))
            else:
                game.player.move(move_distance_player(previous_frame_duration, False), (-1, 0))
        if keys[pg.K_SPACE] and verbose_mode:
            # Induced Latency for testing purposes
            pg.time.wait(50)
        if keys[pg.K_F4] and (mods & pg.KMOD_ALT):
            pg.quit()
            raise SystemExit
        pg.event.pump()

    running = True

    # Initialise render queue and update queue, for easy game tick management
    render_queue = RenderQueue()
    object_update_queue = UpdateQueue()

    # Display loading screen
    glClearColor(0.3, 0.3, 0.3, 0)
    glClearDepthf(1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glTranslatef(-0.05, -1.9, 0)
    titlescreen = UIElement('assets/UI/titlescreen.png', True)
    titlescreen.set_scale((1, 1, 1.1))
    render_queue.subscribe(titlescreen)
    render_queue.run_queue()
    pg.display.flip()
    glPopMatrix()
    titlescreen.deactivate()

    # Unload loading screen
    render_queue.unsubscribe(titlescreen)
    del titlescreen

    # Initialise game object
    game = Game(1, render_queue, object_update_queue, verbose_mode, window_size, theme_sound, succes_sound, failed_sounds)
    object_update_queue.subscribe(game)

    # Show waiting screen
    glClearColor(0.3, 0.3, 0.3, 0)
    glClearDepthf(1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glTranslatef(-0.05, -1.9, 0)
    titlescreen_done = UIElement('assets/UI/titlescreen_done.png', True)
    titlescreen_done.set_scale((1, 1, 1.1))
    render_queue.subscribe(titlescreen_done)
    render_queue.run_queue()
    pg.display.flip()
    glPopMatrix()

    # Unload waiting screen
    render_queue.unsubscribe(titlescreen_done)
    del titlescreen_done

    # Wait till player has read the text and wants to start
    waiting = True
    while waiting:
        pg.time.wait(50)
        for wait_event in pg.event.get():
            if wait_event.type == pg.KEYDOWN:
                waiting = False
            if wait_event.type == pg.QUIT:
                pg.quit()
                raise SystemExit

    # Start the first round
    game.start_round()

    # Timing for verbose mode
    timing_start = 0

    # Game loop
    while running:
        # Timer for framerate statistics
        frame_start = timer()

        if verbose_mode:
            timing_start = timer()

        # Handle keyboard events
        event_handler()

        if verbose_mode:
            print('1', timer() - timing_start)
            timing_start = timer()

        # Clear screen
        glClearColor(0.3, 0.3, 0.3, 0)
        glClearDepthf(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if verbose_mode:
            print('2', timer() - timing_start)
            timing_start = timer()

        # Update all subscribed objects
        object_update_queue.run_queue(previous_frame_duration)

        if verbose_mode:
            print('3', timer() - timing_start)
            timing_start = timer()

        # Render all subscribed objects
        render_queue.run_queue_culled()
        # Flip display
        pg.display.flip()

        if verbose_mode:
            print('4', timer() - timing_start)
            timing_start = timer()

        # Framerate statistics
        frame_duration = timer() - frame_start
        previous_frame_duration = frame_duration
        frame_rate = frame_duration ** -1
        if verbose_mode:
            print(f"target: {target_frame_duration}, frame: {frame_duration}, delay: {int((target_frame_duration - frame_duration) * 1000)}")
            print('6', timer() - timing_start, '\n\n')
        if frame_rate > target_frame_rate:
            pg.time.wait(int((target_frame_duration - frame_duration) * 1000))

    # To make sure the system exits correctly
    pg.quit()
    raise SystemExit


if __name__ == '__main__':
    run()
