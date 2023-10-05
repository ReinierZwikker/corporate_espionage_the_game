from map_generation import Map
from persons import Player
from OpenGL.GL import *
from game_objects import UIElement
import pygame as pg
from random import randint


class Game:

    def __init__(self, game_difficulty, render_queue, object_update_queue, debug_mode, window_size, theme_sound, succes_sound, failed_sounds):
        self.game_difficulty = game_difficulty
        self.render_queue = render_queue
        self.object_update_queue = object_update_queue
        self.debug_mode = debug_mode
        self.window_size = window_size

        self.round_running = False

        self.round = 0
        self.round_difficulty = 1

        self.player = None
        self.map = None

        self.ui_elements = []

        self.theme_sound = theme_sound
        self.succes_sound = succes_sound
        self.failed_sounds = failed_sounds

        self.caught_screen_red = UIElement('./assets/UI/caught_red.png')
        self.caught_screen_red.set_offset((0, 0.8))
        self.caught_screen_white = UIElement('./assets/UI/caught_white.png')
        self.caught_screen_white.set_offset((0, 0.8))
        self.next_level_white = UIElement('assets/UI/next_level_white.png')
        self.next_level_white.set_offset((0, 0.8))
        self.next_level_green = UIElement('assets/UI/next_level_green.png')
        self.next_level_green.set_offset((0, 0.8))
        self.key_ui = UIElement('assets/UI/key.png')
        self.key_ui.set_scale((0.05, 1, 0.1))
        self.key_ui.set_offset((-1.75, -0.25))

        self.ui_elements.append(self.caught_screen_red)
        self.ui_elements.append(self.caught_screen_white)
        self.ui_elements.append(self.next_level_white)
        self.ui_elements.append(self.next_level_green)
        self.ui_elements.append(self.key_ui)

        for ui_element in self.ui_elements:
            self.render_queue.subscribe(ui_element)

    def start_round(self):
        glPushMatrix()

        # generate map and player instances
        self.theme_sound.play(-1)
        map_grid_size = (int(2 * self.round_difficulty + 5), int(4 * self.round_difficulty + 11))
        self.map = Map(self.render_queue, self.object_update_queue, map_grid_size=map_grid_size, difficulty=self.round_difficulty,
                       round_number=self.round, debug_mode=self.debug_mode)
        self.player = Player(self.map, self.render_queue, self.object_update_queue)
        self.map.set_player_object(self.player)
        self.render_queue.set_camera_focus(self.player)
        self.round += 1

        # Place camera in begin position
        glRotatef(85, 1, 0, 0)
        glTranslatef(0, -12, -(2 * self.map.starting_point[0] + 1))

        # Alternate camera position
        # glRotatef(65, 1, 0, 0)
        # glTranslatef(0, -6, -(2*self.map.starting_point[0]+4))

        self.round_running = True

    def end_round(self):
        # reset position, delete instances and flush queues
        self.theme_sound.stop()
        self.round_running = False
        glTranslatef(0, 12, (2 * self.map.starting_point[0] + 1))
        glRotatef(-85, 1, 0, 0)
        glPopMatrix()
        del self.map
        del self.player
        self.render_queue.flush()
        self.object_update_queue.flush()
        # After flushing, put necessary objects back
        self.object_update_queue.subscribe(self)
        for ui_element in self.ui_elements:
            ui_element.activated = False
            self.render_queue.subscribe(ui_element)

    def restart_screen(self):
        self.theme_sound.stop()
        song_select = randint(0, len(self.failed_sounds) - 1)
        self.failed_sounds[song_select].play()
        waiting = True
        self.caught_screen_white.activated = True
        self.caught_screen_red.activated = False
        while waiting:
            self.caught_screen_white.flip()
            self.caught_screen_red.flip()
            glClearColor(0.3, 0.3, 0.3, 0)
            glClearDepthf(1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.render_queue.run_queue_culled()
            pg.display.flip()
            pg.time.wait(500)
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    waiting = False
                if event.type == pg.QUIT:
                    glPopMatrix()
                    pg.quit()
                    raise SystemExit
        self.failed_sounds[song_select].stop()

    def next_level_screen(self):
        self.theme_sound.stop()
        self.succes_sound.play(-1)
        self.round_difficulty += self.game_difficulty
        waiting = True
        self.next_level_white.activated = True
        self.next_level_green.activated = False
        while waiting:
            self.next_level_white.flip()
            self.next_level_green.flip()
            glClearColor(0.3, 0.3, 0.3, 0)
            glClearDepthf(1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.render_queue.run_queue_culled()
            pg.display.flip()
            pg.time.wait(500)
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    waiting = False
                if event.type == pg.QUIT:
                    glPopMatrix()
                    pg.quit()
                    raise SystemExit
        self.succes_sound.stop()

    def update_object(self):
        for ui_element in self.ui_elements:
            ui_element.set_location((self.player.location[0] + ui_element.offset[0], 10, self.player.location[1] + ui_element.offset[1]))
        if self.round_running:
            if self.player.seen:
                self.restart_screen()
                self.end_round()
                self.start_round()
            if abs(self.player.location[0] - (self.map.key_location[1] * 2)) < 1 and abs(self.player.location[1] - self.map.key_location[0] * 2) < 1 \
                    and not self.player.got_key:
                self.player.got_key = True
                self.map.key_map.activated = False
                self.key_ui.activated = True
            if abs(self.player.location[0] - (self.map.ending_point[1] * 4 + 1)) < 0.5 and abs(
                    self.player.location[1] - self.map.ending_point[0] * 2) < \
                    0.5 and self.player.got_key:
                self.next_level_screen()
                self.end_round()
                self.start_round()
