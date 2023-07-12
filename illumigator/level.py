import numpy
import json
from typing import List, Union

from pydantic import BaseModel
from illumigator import worldobjects, geometry, entity, util

WALL_SIZE = util.WALL_SIZE


class Level:
    def __init__(
        self,
        wall_coordinate_list: list[list] = None,
        mirror_coordinate_list: list[list] = None,
        light_receiver_coordinate_list: list[list] = None,
        light_source_coordinate_list: list[list] = None,
        name="default",
    ):
        self.background = None
        self.name = name

        self.mirror_list = []
        self.light_receiver_list = []
        self.light_sources_list = []
        self.wall_list: list[worldobjects.WorldObject] = [
            worldobjects.Wall(
                numpy.array([WALL_SIZE / 2, 720 / 2]),
                numpy.array([1, 720 / WALL_SIZE]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([1280 - WALL_SIZE / 2, 720 / 2]),
                numpy.array([1, 720 / WALL_SIZE]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([1280 / 2, WALL_SIZE / 2]),
                numpy.array([1280 / WALL_SIZE - 2, 1]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([1280 / 2, 720 - WALL_SIZE / 2]),
                numpy.array([1280 / WALL_SIZE - 2, 1]),
                0,
            ),
        ]

        for (
            wall_coordinates
        ) in (
            wall_coordinate_list
        ):  # TODO: Handle animated walls somehow. For now they're hand-made in the functions
            self.wall_list.append(
                worldobjects.Wall(
                    numpy.array([wall_coordinates[0], wall_coordinates[1]]),
                    numpy.array([wall_coordinates[2], wall_coordinates[3]]),
                    wall_coordinates[4],
                )
            )

        for mirror_coordinates in mirror_coordinate_list:
            self.mirror_list.append(
                worldobjects.Mirror(
                    numpy.array([mirror_coordinates[0], mirror_coordinates[1]]),
                    mirror_coordinates[2],
                )
            )

        for light_receiver_coordinates in light_receiver_coordinate_list:
            self.light_receiver_list.append(
                worldobjects.LightReceiver(
                    numpy.array(
                        [light_receiver_coordinates[0], light_receiver_coordinates[1]]
                    ),
                    light_receiver_coordinates[2],
                )
            )

        for light_source_coordinates in light_source_coordinate_list:
            if len(light_source_coordinates) == 4:  # Has an angular spread argument
                self.light_sources_list.append(
                    worldobjects.RadialLightSource(
                        numpy.array(
                            [light_source_coordinates[0], light_source_coordinates[1]]
                        ),
                        light_source_coordinates[2],
                        light_source_coordinates[3],
                    )
                )
            else:
                self.light_sources_list.append(
                    worldobjects.ParallelLightSource(
                        numpy.array(
                            [light_source_coordinates[0], light_source_coordinates[1]]
                        ),
                        light_source_coordinates[2],
                    )
                )

    def update(self, character: entity.Character, mouse_x, mouse_y):
        for wall in self.wall_list:
            if wall.obj_animation is not None:
                wall.apply_object_animation(character)
        for light_source in self.light_sources_list:
            if util.DEBUG_LIGHT_SOURCES:
                light_source.move(
                    numpy.array(
                        [
                            mouse_x - light_source._position[0],
                            mouse_y - light_source._position[1],
                        ]
                    )
                )
            light_source.cast_rays(
                self.wall_list
                + self.mirror_list
                + self.light_receiver_list
                + self.light_sources_list
            )
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

    def check_collisions(self, character: entity.Character):
        for wall in self.wall_list:
            if wall.check_collision(character.character_sprite):
                return True
        for mirror in self.mirror_list:
            if mirror.check_collision(character.character_sprite):
                return True
        for light_receiver in self.light_receiver_list:
            if light_receiver.check_collision(character.character_sprite):
                return True


class LevelDef(BaseModel):
    """
    Model for single level definition in json file.
    ```
        {
            "name": name of level (defaults to 'default'),
            "wall_coordinate_list": [],
            "mirror_coordinate_list": [],
            "light_receiver_coordinate_list": [],
            "light_source_coordinate_list": []
        }
    ```
    """

    wall_coordinate_list: List[List[float]]
    mirror_coordinate_list: List[List[float]]
    light_receiver_coordinate_list: List[List[float]]
    light_source_coordinate_list: List[List[float]]
    name: str = "default"


class LevelsJson(BaseModel):
    """
    Model for the levels definition json file.
    Format of json data is
    ```
        {
            levels_definition: ...List of Levels,
            level_orders: null (for default ordering) or list of level names to specify level orders.
        }
    ```
    """

    levels_definition: List[LevelDef]
    level_order: Union[None, List[str]]


def load_levels(file: str):
    """
    Yield a generator to cycle through levels infinitely.
    """
    data = json.load(open(file))
    levels_data = LevelsJson(**data)
    levels = levels_data.levels_definition

    def sort_levels_fn(level: Level):
        if levels_data.level_order is None:
            return 0
        for i, lvl in enumerate(levels_data.level_order):
            if level.name == lvl:
                return i
        return i + 1

    levels = sorted(levels, key=sort_levels_fn)
    i = 0
    while True:
        yield Level(**levels[i].dict())
        i = (i + 1) % len(levels)


