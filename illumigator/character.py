import arcade
import numpy
import pyglet.media

from illumigator import util
from illumigator.util import WINDOW_WIDTH, WINDOW_HEIGHT


class Character:
    def __init__(self,
                 scale_factor=2,
                 image_width=24,
                 image_height=24,
                 center_x=WINDOW_WIDTH // 2,
                 center_y=WINDOW_HEIGHT // 2):

        self.textures = [
            util.load_texture(util.PLAYER_SPRITE_RIGHT),
            util.load_texture(util.PLAYER_SPRITE_LEFT)
        ]

        self.character_sprite = util.load_sprite(util.PLAYER_SPRITE_RIGHT, scale_factor, image_width=image_width,
                                                 image_height=image_height, center_x=center_x, center_y=center_y,
                                                 hit_box_algorithm="Simple")

        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.rotation_dir = 0
        self.rotation_factor = 0
        self.interactive_line = None

        self.player = pyglet.media.player.Player()
        self.walking_sound = util.load_sound('new_walk.wav')

    def draw(self):
        self.character_sprite.draw(pixelated=True)

    def update(self):
        if self.rotation_dir == 0:
            self.rotation_factor = 0
            return

        if self.rotation_factor < 3.00:
            self.rotation_factor += 1/15
