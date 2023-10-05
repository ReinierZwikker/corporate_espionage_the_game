import numpy as np
import pygame as pg
from random import randint, choice

from game_objects import SimpleObject, TextElement, UIElement
from persons import Enemy


class Map:

    def __init__(self, render_queue, update_queue, map_grid_size=(7, 15), difficulty=0, round_number=0, wall_color=(0.15, 0.15, 0.15),
                 ground_color=(0.5, 0.5, 0.5), debug_mode=False):
        self.map_grid_size = map_grid_size
        # map_grid
        self.map_grid = np.zeros(map_grid_size).astype(bool)

        self.starting_point = (int(self.map_grid.shape[0] / 2), 0)
        self.ending_point = (int(self.map_grid.shape[0] / 2), self.map_grid.shape[0])

        self.difficulty = difficulty
        self.wall_color = wall_color
        self.ground_color = ground_color

        self.debug_mode = debug_mode

        # Generate the map using either algorithm (only digging works)
        # self.generate_map_quota_algorithm()
        self.generate_map_digging_algorithm()

        names = ['the bridge of/death', 'the cave of the/killer rabbit', 'castle camelot', 'the olympic stadium', 'the ministry of/silly walks',
                 'the parrot shop', 'the cheese shop', 'spam']

        self.name = TextElement("map " + str(round_number) + "/" + choice(names) + "/difficulty " + str(difficulty), activated=True)
        self.name.set_scale((0.5, 0.5, 0.5))
        self.name.set_location((-10, 0.5, self.map_grid.shape[0] - 1.5))
        render_queue.subscribe(self.name)

        self.objects = []

        key_place_found = False
        key_grid_index = None
        while not key_place_found:
            key_grid_index = [randint(0, self.map_grid.shape[0] - 1), randint(0, self.map_grid.shape[1] - 1)]
            if key_grid_index == self.starting_point or key_grid_index == self.ending_point:
                key_place_found = False
            else:
                key_place_found = self.map_grid[key_grid_index[0]][key_grid_index[1]]
        self.key_location = key_grid_index
        self.key_map = None

        self.generate_objects(render_queue)

        self.enemies = []
        for enemy in range(int(difficulty * 1.5)):
            self.enemies.append(Enemy(self, render_queue, update_queue, (difficulty + 1) / 20))

    def generate_map_quota_algorithm(self):
        # Fills the map in a smart way, until a specific quota of filled space has been reached (slow)
        self.map_grid = np.invert(self.map_grid)
        while np.sum(self.map_grid) > (0.6 * self.map_grid.shape[0] * self.map_grid.shape[1]):
            pg.event.pump()
            rand_pos = randint(0, self.map_grid.shape[0] - 1), randint(1, self.map_grid.shape[1] - 2)
            if rand_pos[0] != self.starting_point[0] and rand_pos[1] != self.starting_point[1] and rand_pos[1] != self.ending_point[1]:
                self.map_grid[rand_pos] = False
            for x_i in range(1, self.map_grid.shape[0] - 2):
                for y_i in range(1, self.map_grid.shape[1] - 2):
                    if self.map_grid[x_i][y_i] and self.map_grid[x_i + 1][y_i + 1] \
                            and not self.map_grid[x_i + 1][y_i] and not self.map_grid[x_i][y_i + 1]:
                        self.map_grid[x_i][y_i] = False
                    if not self.map_grid[x_i][y_i] and not self.map_grid[x_i + 1][y_i + 1] \
                            and self.map_grid[x_i + 1][y_i] and self.map_grid[x_i][y_i + 1]:
                        self.map_grid[x_i][y_i + 1] = False
            rand_line = randint(0, self.map_grid.shape[0] - 1), randint(3, self.map_grid.shape[1] - 4), randint(2, int(self.map_grid.shape[1] / 4)),
            for y_i in range(0, rand_line[2]):
                self.map_grid[rand_line[0]][rand_line[1] + y_i] = True

        for x_i in range(0, self.map_grid.shape[0] - 1):
            self.map_grid[x_i][self.starting_point[1]] = False
            self.map_grid[x_i][self.ending_point[1]] = False

        self.map_grid[self.starting_point] = True
        self.map_grid[self.ending_point] = True

    def generate_map_digging_algorithm(self):
        # Digs random points and tunnels in the map
        self.map_grid[self.starting_point] = True
        for y_i in range(self.map_grid.shape[1]):
            self.map_grid[self.starting_point[0], y_i] = True
        for _ in range(int(self.map_grid.shape[0] * self.map_grid.shape[1] * 0.6)):
            self.map_grid[randint(0, self.map_grid.shape[0] - 1), randint(1, self.map_grid.shape[1] - 2)] = True
        for _ in range(int(self.map_grid.shape[0] * self.map_grid.shape[1] * 0.05)):
            rand_line = randint(0, self.map_grid.shape[0] - 1), randint(3, self.map_grid.shape[1] - 4), randint(2, int(self.map_grid.shape[1] / 4)),
            for y_i in range(0, rand_line[2]):
                try:
                    self.map_grid[rand_line[0]][rand_line[1] + y_i] = True
                except IndexError:
                    pass
        for x_i in range(self.map_grid.shape[0]):
            for y_i in range(self.map_grid.shape[1]):
                try:
                    above = self.map_grid[x_i][y_i + 1]
                except IndexError:
                    above = False
                try:
                    bellow = self.map_grid[x_i][y_i - 1]
                except IndexError:
                    bellow = False
                try:
                    left = self.map_grid[x_i + 1][y_i]
                except IndexError:
                    left = False
                try:
                    right = self.map_grid[x_i + 1][y_i]
                except IndexError:
                    right = False
                if not above and not bellow and not left and not right and self.map_grid[x_i][y_i]:
                    self.map_grid[x_i][y_i] = False
                if above and bellow and left and right and not self.map_grid[x_i][y_i]:
                    self.map_grid[x_i][y_i] = True

    def generate_objects(self, render_queue):
        # Make left wall
        cube = SimpleObject('solid_cube')
        cube.transform((-1.5, 0.5, self.map_grid.shape[0] - 1))
        cube.set_color(self.wall_color)
        cube.set_scale((0.5, 1.4, self.map_grid.shape[0] + 1))
        self.objects.append(cube)
        render_queue.subscribe(cube)

        # Make right wall
        cube = SimpleObject('solid_cube')
        cube.transform((2 * self.map_grid.shape[1] - 0.5, 0.5, self.map_grid.shape[0] - 1))
        cube.set_color(self.wall_color)
        cube.set_scale((0.5, 1.4, self.map_grid.shape[0] + 1))
        self.objects.append(cube)
        render_queue.subscribe(cube)

        # Entrance door
        cube = SimpleObject('solid_cube')
        cube.transform((-1, -0.2, self.map_grid.shape[0] - 1))
        cube.set_scale((0.1, 0.8, 0.8))
        cube.set_color((1, 0, 0))
        self.objects.append(cube)
        render_queue.subscribe(cube)

        # Exit door
        cube = SimpleObject('solid_cube')
        cube.transform((2 * self.map_grid.shape[1] - 1, -0.2, self.map_grid.shape[0] - 1))
        cube.set_scale((0.1, 0.8, 0.8))
        cube.set_color((0, 1, 0))
        self.objects.append(cube)
        render_queue.subscribe(cube)
        cube = SimpleObject('solid_cube')
        cube.transform((2 * self.map_grid.shape[1] - 2, -1, self.map_grid.shape[0] - 1))
        cube.set_scale((0.8, 0.1, 0.8))
        cube.set_color((0, 1, 0))
        self.objects.append(cube)
        render_queue.subscribe(cube)

        # Place key
        self.key_map = UIElement('assets/UI/key.png')
        self.key_map.set_scale((0.2, 1, 0.4))
        self.key_map.set_location((2 * self.key_location[1], 0, 2 * self.key_location[0]))
        self.key_map.activate()
        render_queue.subscribe(self.key_map)

        # Place a cube for every wall
        for y_i in range(self.map_grid.shape[1]):
            # Make top wall
            cube = SimpleObject('solid_cube')
            cube.transform((2 * y_i, 0.5, -1.5))
            cube.set_color(self.wall_color)
            cube.set_scale((1, 1.4, 0.5))
            self.objects.append(cube)
            render_queue.subscribe(cube)

            # Make Bottom wall
            cube = SimpleObject('solid_cube')
            cube.transform((2 * y_i, 0.5, 2 * self.map_grid.shape[0] - 0.5))
            cube.set_color(self.wall_color)
            cube.set_scale((1, 1.4, 0.5))
            self.objects.append(cube)
            render_queue.subscribe(cube)

            for x_i in range(self.map_grid.shape[0]):
                if not self.map_grid[x_i][y_i]:
                    # Place cube if there is a wall
                    cube = SimpleObject('solid_cube')
                    cube.transform((2 * y_i, 0, 2 * x_i))
                    cube.set_color(self.wall_color)
                    # cube.set_texture('./assets/textures/wall.png')
                    self.objects.append(cube)
                    render_queue.subscribe(cube)

                    # Decorations
                    plane = SimpleObject('wire_plane')
                    plane.transform((2 * y_i, -0.99, 2 * x_i))
                    plane.set_scale((1.01, 1, 1.01))
                    self.objects.append(plane)
                    render_queue.subscribe(plane)

                    plane = SimpleObject('wire_plane')
                    plane.transform((2 * y_i, 0.99, 2 * x_i))
                    plane.set_scale((1.01, 1, 1.01))
                    self.objects.append(plane)
                    render_queue.subscribe(plane)

                if self.map_grid[x_i][y_i]:
                    # Make ground plane
                    ground_plane = SimpleObject('solid_plane')
                    ground_plane.transform((2 * y_i, -1, 2 * x_i))
                    ground_plane.set_color(self.ground_color)
                    # ground_plane.set_texture('./assets/textures/ground.png')
                    self.objects.append(ground_plane)
                    render_queue.subscribe(ground_plane)
                    if self.debug_mode:
                        cube = SimpleObject('wire_cube')
                        cube.transform((2 * y_i, 0, 2 * x_i))
                        cube.set_color(self.wall_color)
                        self.objects.append(cube)
                        render_queue.subscribe(cube)

    def make_object(self):
        pass

    def set_player_object(self, player_object):
        for enemy in self.enemies:
            enemy.set_player_object(player_object)

    def __del__(self):
        try:
            for enemy in self.enemies:
                del enemy
        except AttributeError:
            pass
