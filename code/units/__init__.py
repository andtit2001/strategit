# -*- coding: utf-8 -*-
"""Real classes for game"""
from . import abc


class Headquarters(abc.Unit, abc.UnitFactory):
    """Factory which can create units from given list with given color"""
    _color = None
    _allowed_units_dict = None
    _allowed_units_names = None
    _colored_unit = None

    def __init__(self, name, pos, color, unit_dict):
        super().__init__(name, pos)
        self._color = color
        self._allowed_units_dict = {}
        self._allowed_units_names = []
        self._char = 'H'

        def getcolor(self):
            return self._color
        for key, value in unit_dict.items():
            self._allowed_units_dict[key] = type(
                "Colored" + value.__name__,
                (value,),
                {"_color": color,
                 "color": property(getcolor)})
            self._allowed_units_names.append(value.__name__)
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
        if self.can_create(name):
            new_unit = self._allowed_units_dict[name](name, pos)
        else:
            new_unit = self._colored_unit(name, pos)
        return new_unit

    def can_create(self, name):
        """Check if unit with given name can be created"""
        return name in self._allowed_units_dict

    def __str__(self):
        return "Headquarters\n\tColor: #{:X}".format(self.color)


class Infantry(abc.MovableBattleUnit):
    # pylint: disable=missing-docstring
    def __init__(self, name, pos):
        super().__init__(name, pos)
        self._char = 'I'

    def __str__(self):
        # pylint: disable=no-member
        return "Infantry\n\tColor: #{:X}\n\tHealth: {}/{}\n\tDamage: {}"\
            .format(self.color, self.health, self.max_health, self.damage)


class Vehicle(abc.MovableBattleUnit):
    # pylint: disable=missing-docstring
    def __init__(self, name, pos):
        super().__init__(name, pos)
        self.max_health = 200
        self.damage = 5
        self._char = 'V'

        self.health = self.max_health

    def __str__(self):
        # pylint: disable=no-member
        return "Vehicle\n\tColor: #{:X}\n\tHealth: {}/{}\n\tDamage: {}"\
            .format(self.color, self.health, self.max_health, self.damage)
