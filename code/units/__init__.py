# -*- coding: utf-8 -*-
"""Real classes for game"""
from . import abc


class Headquarters(abc.UnitFactory):
    """Factory which can create units from given list with given color"""
    _color = None
    _unit_dict = None
    _colored_unit = None

    def __init__(self, color, unit_dict):
        super().__init__()
        self._color = color
        self._unit_dict = dict()

        def getcolor(self):
            return self._color
        for key, value in unit_dict.items():
            self._unit_dict[key] = type(
                "Colored" + value.__name__,
                (value,),
                {"_color": color,
                 "color": property(getcolor)})
        self._colored_unit = type(
            "ColoredUnit",
            (abc.Unit,),
            {"_color": color,
             "color": property(getcolor)})

    @property
    def color(self):
        # pylint: disable=missing-docstring
        return self._color

    def create_unit(self, name, pos):
        # pylint: disable=missing-docstring
        new_unit = None
        if name in self._unit_dict:
            new_unit = self._unit_dict[name](name, pos)
        else:
            new_unit = self._colored_unit(name, pos)
        return new_unit


class Infantry(abc.MovableBattleUnit):
    # pylint: disable=missing-docstring
    pass


class Vehicle(abc.MovableBattleUnit):
    # pylint: disable=missing-docstring
    pass