__name__ = "units.abc"

from collections import namedtuple


class Point(namedtuple("Point", ["x", "y"])):
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)


class Unit:
    _name = None
    _position = None

    def __init__(self, name, pos):
        self._name = name
        self._position = Point(pos[0], pos[1])

    @property
    def name(self):
        return self._name

    @property
    def position(self):
        return self._position


class MovableUnit(Unit):
    def __init__(self, name, pos):
        super().__init__(name, pos)

    def move_to(self, x, y):
        self._position = Point(x, y)

    @Unit.position.setter
    def position(self, value):
        self._position = Point(value[0], value[1])


class SelfMovableUnit(MovableUnit):
    speed = None

    def __init__(self, name, pos, speed):
        super().__init__(name, pos)
        self.speed = Point(speed[0], speed[1])

    def move(self):
        self._position += self.speed


class BattleUnit(Unit):
    health = 100
    damage = 10

    max_health = 100

    def attack(self, other):
        other.health -= self.damage

    def heal(self, delta_hp):
        self.health = min(self.max_health, self.health + delta_hp)


class MovableBattleUnit(BattleUnit, MovableUnit):
    pass


class UnitFactory:
    def create_unit(self, name, pos):
        return Unit(name, pos)
