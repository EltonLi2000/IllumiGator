import numpy
import arcade

from character import Character
import worldobjects
import util
from util import WINDOW_WIDTH, WINDOW_HEIGHT


class Level:
    def __init__(
            self,
            wall_coordinate_list: list[list],
            mirror_coordinate_list: list[list],
            light_receiver_coordinate_list: list[list],
            light_source_coordinate_list: list[list],
            name='default'
    ):
        self.background = None
        self.name = name
        self.character = Character()
        self.mirror_list = []
        self.light_receiver_list = []
        self.light_sources_list = []

        wall_size = util.WALL_SPRITE_INFO[1] * util.WALL_SPRITE_INFO[2]
        self.wall_list: list[worldobjects.WorldObject] = [
            worldobjects.Wall(
                numpy.array([wall_size*0.5, WINDOW_HEIGHT*0.5 - wall_size*0.25]),
                numpy.array([1, WINDOW_HEIGHT//wall_size + 1]), 0
            ),
            worldobjects.Wall(
                numpy.array([WINDOW_WIDTH - wall_size*0.5, WINDOW_HEIGHT*0.5 - wall_size*0.25]),
                numpy.array([1, WINDOW_HEIGHT//wall_size + 1]), 0
            ),
            worldobjects.Wall(
                numpy.array([WINDOW_WIDTH*0.5, wall_size*0.5]),
                numpy.array([WINDOW_WIDTH//wall_size - 2, 1]), 0
            ),
            worldobjects.Wall(
                numpy.array([WINDOW_WIDTH*0.5, WINDOW_HEIGHT - wall_size*0.5]),
                numpy.array([WINDOW_WIDTH//wall_size - 2, 1]), 0
            ),
        ]
        # Animated Wall:
        animated_wall = worldobjects.Wall(
                numpy.array([WINDOW_WIDTH-176, WINDOW_HEIGHT-240]),
                numpy.array([1, 1]), 0
            )
        animated_wall.create_animation(numpy.array([128, 0]), 0.02)
        self.wall_list.append(animated_wall)

        for wall_coordinates in wall_coordinate_list:
            self.wall_list.append(worldobjects.Wall(
                numpy.array([wall_coordinates[0], wall_coordinates[1]]),
                numpy.array([wall_coordinates[2], wall_coordinates[3]]),
                wall_coordinates[4]
            ))

        for mirror_coordinates in mirror_coordinate_list:
            self.mirror_list.append(worldobjects.Mirror(
                numpy.array([mirror_coordinates[0], mirror_coordinates[1]]),
                mirror_coordinates[2]
            ))

        for light_receiver_coordinates in light_receiver_coordinate_list:
            self.light_receiver_list.append(worldobjects.LightReceiver(
                numpy.array([light_receiver_coordinates[0], light_receiver_coordinates[1]]),
                light_receiver_coordinates[2]
            ))

        for light_source_coordinates in light_source_coordinate_list:
            if len(light_source_coordinates) == 4:  # Has an angular spread argument
                self.light_sources_list.append(worldobjects.RadialLightSource(
                    numpy.array([light_source_coordinates[0], light_source_coordinates[1]]),
                    light_source_coordinates[2],
                    light_source_coordinates[3])
                )
            else:
                self.light_sources_list.append(worldobjects.ParallelLightSource(
                    numpy.array([light_source_coordinates[0], light_source_coordinates[1]]),
                    light_source_coordinates[2]))

    def update(self):
        self.move_character()
        for wall in self.wall_list:
            if wall.obj_animation is not None:
                wall.apply_object_animation(self.character)
        for light_source in self.light_sources_list:
            light_source.cast_rays(
                self.wall_list + self.mirror_list + self.light_receiver_list + self.light_sources_list)
        for light_receiver in self.light_receiver_list:
            light_receiver.charge *= util.CHARGE_DECAY

    def draw(self):
        for wall in self.wall_list:
            wall.draw()
        for mirror in self.mirror_list:
            mirror.draw()
        for light_source in self.light_sources_list:
            light_source.draw()
        for light_receiver in self.light_receiver_list:
            light_receiver.draw()
        self.character.draw()

    def check_collisions(self) -> bool:
        for wall in self.wall_list:
            if wall.check_collision(self.character.character_sprite):
                return True
        for mirror in self.mirror_list:
            if mirror.check_collision(self.character.character_sprite):
                return True
        for light_receiver in self.light_receiver_list:
            if light_receiver.check_collision(self.character.character_sprite):
                return True

    def move_character(self) -> None:
        direction = numpy.zeros(2)
        if self.character.right:
            self.character.character_sprite.texture = self.character.textures[0]
            direction[0] += 1
        if self.character.left:
            self.character.character_sprite.texture = self.character.textures[1]
            direction[0] -= 1
        if self.character.up:
            direction[1] += 1
        if self.character.down:
            direction[1] -= 1

        direction_mag = numpy.linalg.norm(direction)
        if direction_mag > 0:
            direction = direction * util.PLAYER_MOVEMENT_SPEED / direction_mag  # Normalize and scale with speed

            # Checking if x movement is valid
            self.character.character_sprite.center_x += direction[0]
            if self.check_collisions():
                self.character.character_sprite.center_x -= direction[0]

            # Checking if y movement is valid
            self.character.character_sprite.center_y += direction[1]
            if self.check_collisions():
                self.character.character_sprite.center_y -= direction[1]

            # Check if sound should be played
            if not arcade.Sound.is_playing(self.character.walking_sound, self.character.player):
                self.character.player = arcade.play_sound(self.character.walking_sound)

        else:
            # Check if sound should be stopped
            if arcade.Sound.is_playing(self.character.walking_sound, self.character.player):
                arcade.stop_sound(self.character.player)

    def rotate_surroundings(self) -> None:
        closest_distance_squared = util.STARTING_DISTANCE_VALUE  # arbitrarily large number
        closest_mirror = None
        for mirror in self.mirror_list:
            distance = mirror.distance_squared_to_center(self.character.character_sprite.center_x,
                                                         self.character.character_sprite.center_y)
            if distance < closest_distance_squared:
                closest_mirror = mirror
                closest_distance_squared = distance

        if closest_mirror is not None and closest_distance_squared <= util.PLAYER_REACH_DISTANCE_SQUARED:
            closest_mirror.move_if_safe(self, numpy.zeros(2),
                                        self.character.rotation_dir * util.OBJECT_ROTATION_AMOUNT *
                                        (2 ** self.character.rotation_factor))
