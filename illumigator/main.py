import arcade
import numpy

from illumigator.menus import draw_title_menu, InGameMenu, WinScreen
from illumigator.util import WINDOW_WIDTH, WINDOW_HEIGHT
from illumigator import util
from illumigator.level import Level


class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, util.WINDOW_TITLE)
        self.elem_list = None
        self.game_state = None
        self.game_menu = None
        self.win_screen = None
        self.tile_map = None
        self.current_level = None
        self.background = None
        self.set_mouse_visible(False)

    def setup(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.game_state = 'menu'
        self.background = util.load_sprite("flowers.jpg", 0.333333, center_x=util.WINDOW_WIDTH / 2,
                                           center_y=util.WINDOW_HEIGHT / 2)
        self.background.alpha = 100
        self.game_menu = InGameMenu()
        self.win_screen = WinScreen()
        self.elem_list = arcade.SpriteList()

        # TODO: eventually JSON file
        mirror_coordinate_list = [
            [WINDOW_WIDTH / 4, (WINDOW_HEIGHT / 3) * 2, -numpy.pi / 4],
            [(WINDOW_WIDTH / 2) + 50, WINDOW_HEIGHT - 100, 0],
            [WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4, numpy.pi / 2],
            [((WINDOW_WIDTH / 4) * 3) + 20, WINDOW_HEIGHT / 5, 0]
        ]
        wall_coordinate_list = [
            [784, 176, 1, 9, 0],
            [496, WINDOW_HEIGHT - 176, 1, 9, 0],
            [880, WINDOW_HEIGHT - 176, 1, 9, 0]
        ]
        light_receiver_coordinate_list = [
            [WINDOW_WIDTH - 128, WINDOW_HEIGHT - 128, 0],
        ]
        light_source_coordinate_list = [
            # A 4th argument will make RadialLightSource with that angular spread instead of ParallelLightSource
            [WINDOW_WIDTH / 4, 48, numpy.pi / 2]
        ]

        self.current_level = Level(
            wall_coordinate_list,
            mirror_coordinate_list,
            light_receiver_coordinate_list,
            light_source_coordinate_list
        )

    def on_update(self, delta_time):
        if self.game_state == 'game':
            self.current_level.update()
            if any(light_receiver.charge >= util.RECEIVER_THRESHOLD
                   for light_receiver in self.current_level.light_receiver_list):
                self.game_state = 'win'

    def on_draw(self):
        self.clear()

        if self.game_state == 'menu':
            draw_title_menu()
        elif self.game_state == 'game' or self.game_state == 'paused':
            self.background.draw()
            self.current_level.draw()

            if self.game_state == 'paused':
                self.game_menu.draw()

        if self.game_state == 'win':
            self.win_screen.draw()

    def on_key_press(self, key, key_modifiers):
        if self.game_state == 'menu':
            if key == arcade.key.ENTER:
                self.game_state = 'game'
            if key == arcade.key.ESCAPE:
                arcade.close_window()

        elif self.game_state == 'game':
            if key == arcade.key.ESCAPE:
                self.game_state = 'paused'
            if key == arcade.key.W or key == arcade.key.UP:
                self.current_level.character.up = True
            if key == arcade.key.A or key == arcade.key.LEFT:
                self.current_level.character.left = True
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.current_level.character.down = True
            if key == arcade.key.D or key == arcade.key.RIGHT:
                self.current_level.character.right = True

            if key == arcade.key.Q:
                self.current_level.character.rotation_dir += 1
            if key == arcade.key.E:
                self.current_level.character.rotation_dir -= 1

        elif self.game_state == 'paused':
            if key == arcade.key.ESCAPE:
                self.game_state = 'game'
            if key == arcade.key.DOWN:
                self.game_menu.increment_selection()
            if key == arcade.key.UP:
                self.game_menu.decrement_selection()
            if key == arcade.key.ENTER:
                if self.game_menu.selection == 0:
                    self.game_state = 'game'
                elif self.game_menu.selection == 1:
                    self.game_state = 'menu'

        elif self.game_state == 'win':
            if key == arcade.key.DOWN:
                self.win_screen.increment_selection()
            if key == arcade.key.UP:
                self.win_screen.decrement_selection()
            if key == arcade.key.ENTER:
                if self.win_screen.selection == 0:
                    self.game_state = 'menu'
                elif self.win_screen.selection == 1:
                    self.setup()

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.current_level.character.up = False
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.current_level.character.left = False
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.current_level.character.down = False
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.current_level.character.right = False
        if key == arcade.key.Q:
            self.current_level.character.rotation_dir -= 1
        if key == arcade.key.E:
            self.current_level.character.rotation_dir += 1
        self.current_level.update()


def main():
    window = GameObject()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
