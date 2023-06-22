import arcade
import math
import numpy
import random

import light
import util.util as util
import geometry


class WorldObject:
    sprite: arcade.Sprite  # TODO: load sprites and display them
    geometry_segments: list[geometry.Geometry]

    position: numpy.array
    rotation_angle: float
    color: tuple[int, int, int]
    is_interactable: bool  # TODO: use for player pushing calculations

    def __init__(self, position, rotation_angle, color=random.choice(util.COLORS), is_interactable=False):
        self.position = position
        self.rotation_angle = rotation_angle
        self.color = color

        self.is_interactable = is_interactable

    def draw(self):
        for segment in self.geometry_segments:
            segment.draw()

    def move(self, move_distance: numpy.array, rotate_angle: float = 0):
        self.position += move_distance
        for segment in self.geometry_segments:
            segment.move(self.position, rotate_angle)





class Wall(WorldObject):
    def __init__(self, center_position: numpy.array, dimensions: numpy.array, rotation_angle,
                 sprite_path, scale_factor, image_width, image_height, is_interactable=False):
        super().__init__(center_position, rotation_angle, is_interactable=is_interactable)

        side_lengths = dimensions * image_width

        axis1_norm = numpy.array([math.cos(rotation_angle), math.sin(rotation_angle)])
        axis2_norm = numpy.array([-math.sin(rotation_angle), math.cos(rotation_angle)])

        axis1 = side_lengths[0] * 0.5 * axis1_norm
        axis2 = side_lengths[1] * 0.5 * axis2_norm

        self.geometry_segments = [
            geometry.Line(center_position - axis1 - axis2, center_position - axis1 + axis2),
            geometry.Line(center_position - axis1 + axis2, center_position + axis1 + axis2),
            geometry.Line(center_position + axis1 + axis2, center_position + axis1 - axis2),
            geometry.Line(center_position + axis1 - axis2, center_position - axis1 - axis2),
        ]

        self.sprite_list = arcade.SpriteList()
        for col in range(dimensions[0]):
            for row in range(dimensions[1]):
                sprite_center = center_position-axis1-axis2 + axis1_norm*(image_width/2 + col*image_width) + axis2_norm*(image_height/2 + row*image_height)

                self.sprite_list.append(
                    arcade.Sprite(sprite_path, scale_factor, image_width=image_width, image_height=image_height,
                                  center_x=sprite_center[0], center_y=sprite_center[1],
                                  angle=util.convert_angle_for_arcade(rotation_angle), hit_box_algorithm="Simple"
                                  ))


    def draw(self):
        for sprite in self.sprite_list:
            sprite.draw()
        for segment in self.geometry_segments:
            segment.draw()


class Mirror(Wall):
    def __init__(self, center_position: numpy.array, side_lengths: numpy.array, rotation_angle: float,
                 sprite_path, scale_factor, image_width, image_height, color=arcade.color.SILVER):
        super().__init__(center_position, side_lengths, rotation_angle,
                         sprite_path, scale_factor, image_width, image_height,
                         is_interactable=False)

        self.geometry_segments[2].is_reflective = True
        self.sprite = arcade.Sprite(sprite_path, scale_factor, image_width=image_width, image_height=image_height,
                                    center_x=center_position[0], center_y=center_position[1], hit_box_algorithm="Simple")

    def draw(self):
        self.sprite.draw()



class RadialLightSource(WorldObject):
    def __init__(self, position, rotation_angle, angular_spread):
        super().__init__(position, rotation_angle, arcade.color.BLACK)
        self.light_rays = [light.LightRay(numpy.array([0, 0]), numpy.array([0, 0])) for _ in range(light.NUM_LIGHT_RAYS)]
        self.angular_spread = angular_spread
        self.calculate_light_ray_positions(position, rotation_angle, angular_spread)


    def cast_rays(self, world_objects):
        for ray in self.light_rays:
            ray.cast_ray(world_objects)


    def calculate_light_ray_positions(self, move_distance, rotate_angle=0, new_angular_spread=None):
        self.rotation_angle += rotate_angle
        self.angular_spread = self.angular_spread if new_angular_spread is None else new_angular_spread
        self.position = self.position + move_distance

        num_rays = len(self.light_rays)
        for n in range(num_rays):
            ray_angle = (n/num_rays) * (self.rotation_angle - self.angular_spread/2) + (1 - n / num_rays) * (self.rotation_angle + self.angular_spread/2)
            ray_direction = numpy.array([math.cos(ray_angle), math.sin(ray_angle)])
            self.light_rays[n].origin = self.position
            self.light_rays[n].direction = ray_direction


    def draw(self):
        for ray in self.light_rays:
            ray.draw()
        arcade.draw_circle_filled(self.position[0], self.position[1], 10, arcade.color.BLACK)
