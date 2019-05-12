# -*- coding: utf-8 -*-
"""This module contains basic classes for managing game state"""
from collections import namedtuple
import json
import random

from . import units
# from .units import abc as units_abc

FIELD_WIDTH = 20
FIELD_HEIGHT = 20


PlayerInfo = namedtuple(
    "PlayerInfo",
    [
        "color",
        "AI",
        "money",
        "unit_list",
        "squad_list",
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
                "unit_dict": obj._unit_dict
            }
        return json.JSONEncoder.default(self, obj)


def game_object_hook(dct):
    """Object hook for `json.load()`"""
    if "__type__" in dct:
        if dct["__type__"] == "player_info":
            return PlayerInfo._make(dct["__data__"])
    if "__unittype__" in dct:
        if dct["__unittype__"] == "hq":
            return units.Headquarters(dct["color"], dct["unit_dict"])
    return dct


class GameState:
    """
    Class that represents game state
    (number of players and units, their stats and so on)
    """

    filename = ""
    current_player = 0
    list_of_player_infos = []
    game_field = []
    width = 0
    height = 0

    def __init__(self, player_count, width, height):
        """Number of player is always equal to 2 or 4"""
        if player_count < 2:
            player_count = 2
        if player_count > 2:
            player_count = 4
        for _ in range(player_count):
            color = random.randrange(0, 2**24)
            self.list_of_player_infos.append(Wrapper(PlayerInfo(
                color, True, 1000,
                [units.Headquarters(color, {})], [],
            )))
        self.game_field = [[None] * width for _ in range(height)]
        self.game_field[0][0] = [0]
        self.game_field[height - 1][width - 1] = [0]
        if player_count == 4:
            self.game_field[height - 1][0] = [0]
            self.game_field[0][width - 1] = [0]
        self.width = width
        self.height = height

    def load(self, filename):
        """Replace current state with one loaded from file"""
        with open(filename, encoding="utf-8") as file:
            self.game_field, self.list_of_player_infos = json.load(
                file,
                object_hook=game_object_hook)
        self.filename = filename
        self.width = len(self.game_field[0])
        self.height = len(self.game_field)

    def save(self, filename=None):
        """Save state to the file"""
        if not filename:
            filename = self.filename
        with open(filename, "w", encoding="utf-8") as file:
            json.dump([self.game_field, self.list_of_player_infos],
                      file, cls=GameEncoder)


random.seed()
