# -*- coding: utf-8 -*-
"""Abstract base classes for game"""
from collections import namedtuple


class Vector(namedtuple("Vector", ["x", "y"])):
    """2D Vector (represents position or velocity)"""

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)


class Unit:
    """Abstract unit which can't do anything"""
    _name = None
    _position = None

    def __init__(self, name, pos):
        self._name = name
        self._position = Vector(pos[0], pos[1])

    @property
    def name(self):
        # pylint: disable=missing-docstring
        return self._name

    @property
    def position(self):
        # pylint: disable=missing-docstring
        return self._position


class MovableUnit(Unit):
    """Unit which position can be changed"""

    def move_to(self, x, y):
        # pylint: disable=invalid-name
        """Change position of unit (function call)"""
        self._position = Vector(x, y)

    # pylint: disable=no-member
    @Unit.position.setter
    def position(self, value):
        """Change position of unit (assignment)"""
        self._position = Vector(value[0], value[1])


class SelfMovableUnit(MovableUnit):
    """Unit which can change its position"""
    speed = None

    def __init__(self, name, pos, speed):
        super().__init__(name, pos)
        self.speed = Vector(speed[0], speed[1])

    def move(self):
        """Tell unit to change its postion"""
        self._position += self.speed


class BattleUnit(Unit):
    """Unit which can give and take damage"""
    health = 100
    damage = 10

    max_health = 100

    def attack(self, other):
        """Give damage to another BattleUnit"""
        other.health -= self.damage

    def heal(self, delta_hp):
        """Increase current health points"""
        self.health = min(self.max_health, self.health + delta_hp)


class MovableBattleUnit(BattleUnit, MovableUnit):
    """Auxiliary class for units which can \"move and fight\""""


class UnitFactory:
    """Abstract factory which can create abstract Units"""

    def create_unit(self, name, pos):
        """Create abstract Unit"""
        return Unit(name, pos)
