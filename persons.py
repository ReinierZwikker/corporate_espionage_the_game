from game_objects import SimpleObject, Parent, TextElement
from game_util import move_distance_enemy

from random import uniform, randint, choice
import numpy as np
import copy
from OpenGL.GL import *


def get_grid_index(position):
    return (int((position[1] + 1) / 2) if (position[1] + 1) / 2 >= 0 else -1,
            int((position[0] + 1) / 2) if (position[0] + 1) / 2 >= 0 else -1)


def get_grid_position(grid_index):
    return [(grid_index[1] * 2), (grid_index[0] * 2)]


def get_location(location, distance, direction, bounding_box=0):
    return (location[0] - (direction[0] * (distance + abs(bounding_box))),
            location[1] - (direction[1] * (distance + abs(bounding_box))))


class Person:

    def __init__(self, map_object, render_queue, update_queue, color, starting_location):
        self.location = starting_location
        self.rotation = 180
        self.map_grid = map_object.map_grid
        self.render_queue = render_queue
        self.update_queue = update_queue

        self.color = color

        self.rotation_speed = 0.2

        self.limp_rotation = 0
        self.previous_limp_rotation = 0
        self.limp_rotation_target = 45
        self.leg_rotation_speed = 100

        self.body = Parent()

        self.torso = SimpleObject('solid_cube')
        self.torso.set_location((0, 0.1, 0))
        self.torso.set_scale((0.15, 0.2, 0.25))
        self.torso.set_color(self.color)

        self.arm_jointL = Parent()
        self.arm_jointL.set_location((0, 0.2, -0.3))
        self.arm_jointL.set_rotation((0, 180, self.limp_rotation))

        self.armL = SimpleObject('solid_cube')
        self.armL.set_location((0, -0.1, 0))
        self.armL.set_scale((0.1, 0.2, 0.1))
        self.armL.set_color(self.color)

        self.arm_jointL.add_child(self.armL)

        self.arm_jointR = Parent()
        self.arm_jointR.set_location((0, 0.2, 0.3))
        self.arm_jointR.set_rotation((0, 180, self.limp_rotation))

        self.armR = SimpleObject('solid_cube')
        self.armR.set_location((0, -0.1, 0))
        self.armR.set_scale((0.1, 0.2, 0.1))
        self.armR.set_color(self.color)

        self.arm_jointR.add_child(self.armR)

        self.leg_jointL = Parent()
        self.leg_jointL.set_location((0, -0.1, 0.15))
        self.leg_jointL.set_rotation((0, 180, self.limp_rotation))

        self.legL = SimpleObject('solid_cube')
        self.legL.set_location((0, -0.15, 0))
        self.legL.set_scale((0.1, 0.3, 0.1))
        self.legL.set_color(self.color)

        self.leg_jointL.add_child(self.legL)

        self.leg_jointR = Parent()
        self.leg_jointR.set_location((0, -0.1, -0.15))
        self.leg_jointR.set_rotation((0, -180, self.limp_rotation))

        self.legR = SimpleObject('solid_cube')
        self.legR.set_location((0, -0.15, 0))
        self.legR.set_scale((0.1, 0.3, 0.1))
        self.legR.set_color(self.color)

        self.leg_jointR.add_child(self.legR)

        self.head = SimpleObject('solid_cube')
        self.head.set_location((0, 0.5, 0))
        self.head.set_scale((0.25, 0.25, 0.25))
        self.head.set_color(self.color)

        self.body.add_child(self.torso)
        self.body.add_child(self.arm_jointL)
        self.body.add_child(self.arm_jointR)
        self.body.add_child(self.leg_jointL)
        self.body.add_child(self.leg_jointR)
        self.body.add_child(self.head)

        self.previous_location = copy.deepcopy(self.location)
        self.previous_rotation = copy.deepcopy(self.rotation)
        self.previous_target_rotation = copy.deepcopy(self.rotation)

        render_queue.subscribe(self.body)
        update_queue.subscribe(self)

    def update_object(self, previous_frame_duration):
        self.body.set_location((self.location[0], -0.5, self.location[1]))
        if abs(self.location[0] - self.previous_location[0]) > 0.005 or abs(self.location[1] - self.previous_location[1]) > 0.005:
            target_rotation = -np.rad2deg(np.arctan2(self.previous_location[1] - self.location[1], self.previous_location[0] - self.location[0]))
            if self.limp_rotation_target == 0:
                self.limp_rotation_target = 45
            if self.limp_rotation >= 45:
                self.limp_rotation_target = -45
            if self.limp_rotation <= -45:
                self.limp_rotation_target = 45
            self.limp_rotation = self.previous_limp_rotation + (self.leg_rotation_speed *
                                                                self.limp_rotation_target / 45 *
                                                                np.sqrt((self.location[0] - self.previous_location[0]) ** 2 +
                                                                        (self.location[1] - self.previous_location[1]) ** 2))
        else:
            self.limp_rotation_target = 0
            self.limp_rotation = self.previous_limp_rotation + (self.leg_rotation_speed * - self.limp_rotation_target / 90)
            target_rotation = copy.deepcopy(self.previous_target_rotation)
        if (target_rotation - self.previous_rotation) > 180:
            self.previous_rotation += 360
        if (target_rotation - self.previous_rotation) < -180:
            self.previous_rotation -= 360
        self.rotation = self.previous_rotation + self.rotation_speed * (target_rotation - self.previous_rotation)
        self.leg_jointR.set_rotation((0, 0, self.limp_rotation))
        self.leg_jointL.set_rotation((0, 180, self.limp_rotation))
        self.arm_jointR.set_rotation((0, 0, self.limp_rotation * 0.6))
        self.arm_jointL.set_rotation((0, 180, self.limp_rotation * 0.6))
        self.body.set_rotation((0, self.rotation, 0))
        self.previous_location = copy.deepcopy(self.location)
        self.previous_rotation = copy.deepcopy(self.rotation)
        self.previous_limp_rotation = copy.deepcopy(self.limp_rotation)
        self.previous_target_rotation = copy.deepcopy(target_rotation)

    def move(self, distance, direction):
        if not self.check_collision(distance, direction, 0.25):
            self.location[0] -= direction[0] * distance
            self.location[1] -= direction[1] * distance

    def check_collision(self, distance, direction, bounding_box):
        new_position = get_location(self.location, distance, direction, bounding_box)

        grid_position = get_grid_index(new_position)
        if 0 <= grid_position[0] < self.map_grid.shape[0] and 0 <= grid_position[1] < self.map_grid.shape[1]:
            return not self.map_grid[grid_position]
        else:
            return True


class Player(Person):

    def __init__(self, map_object, render_queue, update_queue):
        self.seen = False
        self.got_key = False
        self.scroll_level = 1
        super().__init__(map_object, render_queue, update_queue, (0, 0, 1), [map_object.starting_point[1], 2 * map_object.starting_point[0]])

    def update_object(self, previous_frame_duration):
        glTranslatef(self.previous_location[0], 0, self.previous_location[1])
        glTranslatef(-self.location[0], 0, -self.location[1])
        super().update_object(previous_frame_duration)

    def is_here(self, location):
        distance = np.sqrt((self.location[0] - location[0]) ** 2 + (self.location[1] - location[1]) ** 2)
        if distance < 0.1:
            return True
        else:
            return False

    def spotted(self):
        self.body.set_color((0, 0, 0, 0.5))
        self.seen = True


class Enemy(Person):

    def __init__(self, map_object, render_queue, update_queue, rotation_speed):
        self.walking_direction = (randint(-1, 1), randint(-1, 1))
        place_found = False
        start_grid_index = [3, map_object.map_grid.shape[1] - 1]
        while not place_found:
            start_grid_index = [randint(0, map_object.map_grid.shape[0] - 1), randint(0, map_object.map_grid.shape[1] - 1)]
            if start_grid_index == map_object.starting_point or start_grid_index == map_object.ending_point:
                place_found = False
            else:
                place_found = map_object.map_grid[start_grid_index[0]][start_grid_index[1]]
        super().__init__(map_object, render_queue, update_queue, (1, 0, 0), get_grid_position(start_grid_index))

        self.vision_slices = []

        self.vision_slice_subdivision = 10
        self.enemy_fov = 60
        self.enemy_sight_distance = 4
        self.vision_slices_width = 0.21
        self.vision_slices_height = 0.5 + uniform(-0.01, 0.01)

        names = ['the spanish inquisition', 'king arthur', 'sir lancelot the brave', 'sir galahad the pure', 'knight who says ni',
                 'tim the enchanter', 'rabbit of caerbannog', 'the animator', 'biggus dickus', 'a gestapo officer', 'a different gestapo officer',
                 'joke brigade officer', 'sir notappearinginthisfilm', 'sir robin notquitesobraveassirlancelot', 'sir bedevere the wise', 'zoot',
                 'brian cohen', 'judith', 'an unladen african swallow', 'a laden european swallow', 'an insulting frenchman', 'spam']

        self.name = TextElement(choice(names), activated=True)
        self.name.set_scale((0.4, 0.4, 0.4))
        self.render_queue.subscribe(self.name)

        self.player_object = None

        for vision_slice_i in range(self.vision_slice_subdivision):
            vision_slice = SimpleObject('triangle')
            vision_slice.set_location((0, self.vision_slices_height, 0))
            vision_slice.set_rotation((0,
                                       self.enemy_fov / 2 -
                                       self.enemy_fov / self.vision_slice_subdivision / 2 -
                                       (self.enemy_fov / self.vision_slice_subdivision) * vision_slice_i,
                                       0))
            vision_slice.set_scale((self.enemy_sight_distance, 1, self.vision_slices_width))
            vision_slice.set_color((1, 0, 0))

            self.vision_slices.append(vision_slice)
            self.body.add_child(vision_slice)

        self.rotation_speed = rotation_speed

    def update_object(self, previous_frame_duration):
        def get_new_walking_direction():
            direction = [randint(-1, 1), randint(-1, 1)]
            if sum(direction) == 0 and uniform(0, 1) < 0.9:
                # If direction is opposite or otherwise zero, have another direction
                addition = randint(2, 3)
                if addition == 2:
                    addition = -1
                elif addition == 3:
                    addition = 1
                direction[1] = addition
            return tuple(direction)

        if uniform(0, 1) > 0.99:
            self.walking_direction = get_new_walking_direction()

        while super().check_collision(0.3, self.walking_direction, 0.25):
            self.walking_direction = get_new_walking_direction()

        super().move(move_distance_enemy(previous_frame_duration), self.walking_direction)

        self.trace_vision_cones()

        super().update_object(previous_frame_duration)

        self.name.set_location((self.location[0], 0.5, self.location[1] - 0.25))

    def trace_vision_cones(self):
        def trace(enemy_sight_distance, trace_direction):
            step_division = 10
            for trace_step in range(enemy_sight_distance * step_division):
                if self.player_object.is_here(get_location(self.location, 2 * trace_step / step_division, trace_direction)):
                    self.player_object.spotted()
                if self.check_collision(trace_step / step_division, trace_direction, 0.1):
                    return (trace_step + 3) / step_division
            return enemy_sight_distance + 3

        for vision_slice in self.vision_slices:
            direction_angle = self.rotation + vision_slice.rotation[1]
            direction = (np.cos(np.deg2rad(direction_angle)), -np.sin(np.deg2rad(direction_angle)))
            distance = trace(self.enemy_sight_distance, direction)
            vision_slice.set_scale((distance, 1, distance / self.enemy_sight_distance * self.vision_slices_width))

    def set_player_object(self, player_object):
        if isinstance(player_object, Player):
            self.player_object = player_object
        else:
            print('WARNING: Object not a player')
