# -*- coding: utf-8 -*-
"""This module contains basic classes for managing game state"""
from collections import namedtuple
import json
import random
import sys

from . import units


FIELD_WIDTH = 20
FIELD_HEIGHT = 20


PlayerInfo = namedtuple(
    "PlayerInfo",
    [
        "color",
        "AI",
        "money",
    ]
)


class Wrapper:
    """Workaround for `namedtuple` serialization"""
    obj = None

    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, name):
        return getattr(self.obj, name)

    def _asdict(self):
        return self.obj._asdict()


class GameEncoder(json.JSONEncoder):
    """Custom JSON encoder for game objects"""
    # pylint: disable=protected-access
    # pylint: disable=method-hidden,arguments-differ

    def default(self, obj):
        if isinstance(obj, Wrapper):
            return {
                "__type__": "player_info",
                "__data__": obj._asdict()
            }
        if isinstance(obj, units.Headquarters):
            return {
                "__unittype__": "hq",
                "color": obj.color,
                "name": obj.name,
                "pos": obj.position,
                "allowed_units": obj._allowed_units_names
            }
        if isinstance(obj, units.Infantry):
            return {
                "__unittype__": "infantry",
                "color": obj.color,
                "name": obj.name,
                "pos": obj.position,
                "health": obj.health,
                "damage": obj.damage,
                "max_health": obj.max_health
            }
        if isinstance(obj, units.Vehicle):
            return {
                "__unittype__": "vehicle",
                "color": obj.color,
                "name": obj.name,
                "pos": obj.position,
                "health": obj.health,
                "damage": obj.damage,
                "max_health": obj.max_health
            }
        return json.JSONEncoder.default(self, obj)


def game_object_hook(dct):
    """Object hook for `json.load()`"""
    if "__type__" in dct:
        if dct["__type__"] == "player_info":
            return Wrapper(PlayerInfo(**dct["__data__"]))
    if "__unittype__" in dct:
        if dct["__unittype__"] == "hq":
            type_dict = {}
            for name in dct["allowed_units"]:
                type_dict[name.lower()] = getattr(
                    getattr(sys.modules[__name__], "units"), name)
            return units.Headquarters(
                dct["name"], dct["pos"],
                dct["color"], type_dict)
        if dct["__unittype__"] == "infantry":
            obj = units.Infantry(dct["name"], dct["pos"])
            obj.color = dct["color"]
            obj.health = dct["health"]
            obj.damage = dct["damage"]
            obj.max_health = dct["max_health"]
            return obj
        if dct["__unittype__"] == "vehicle":
            obj = units.Vehicle(dct["name"], dct["pos"])
            obj.color = dct["color"]
            obj.health = dct["health"]
            obj.damage = dct["damage"]
            obj.max_health = dct["max_health"]
            return obj
    return dct


class GameState:
    """
    Class that represents game state
    (number of players and units, their stats and so on)
    """

    current_player = 0
    list_of_player_infos = None
    game_field = None
    unit_count = 0
    unit_dict = None
    squad_dict = None
    width = 0
    height = 0

    def __init__(self, player_count, width, height):
        """Number of player is always equal to 2 or 4"""
        if player_count < 2:
            player_count = 2
        if player_count > 2:
            player_count = 4

        hq_pos = [
            (0, 0),
            (width - 1, height - 1),
            (height - 1, 0),
            (0, width - 1)
        ]
        if player_count == 4:
            hq_pos[1], hq_pos[2] = hq_pos[2], hq_pos[1]
        self.list_of_player_infos = []
        self.game_field = [[[] for _ in range(width)] for _ in range(height)]
        self.unit_dict = {}
        self.squad_dict = {}
        for i in range(player_count):
            color = random.randrange(0, 2**24)
            self.list_of_player_infos.append(Wrapper(PlayerInfo(
                color, False, 1000
            )))
            self.unit_dict[i] = units.Headquarters(
                "HQ", hq_pos[i], color,
                {"infantry": units.Infantry, "vehicle": units.Vehicle})
            self.game_field[hq_pos[i][1]][hq_pos[i][0]] = [i]
        self.width = width
        self.height = height
        self.unit_count = player_count

    def load(self, filename):
        """Replace current state with one loaded from file"""
        with open(filename, encoding="utf-8") as file:
            self.unit_count, self.game_field, self.list_of_player_infos,\
                self.unit_dict, self.squad_dict =\
                json.load(
                    file,
                    object_hook=game_object_hook)
        new_dict = {}
        for key, value in self.unit_dict.items():
            new_dict[int(key)] = value
        self.unit_dict = new_dict
        new_dict = {}
        for key, value in self.squad_dict.items():
            new_dict[int(key)] = value
        self.squad_dict = new_dict

        self.width = len(self.game_field[0])
        self.height = len(self.game_field)

    def save(self, filename):
        """Save state to the file"""
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(
                [self.unit_count, self.game_field, self.list_of_player_infos,
                 self.unit_dict, self.squad_dict],
                file, cls=GameEncoder)
