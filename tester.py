# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
import unittest

from code import units
from code.units import abc


class TestMethods(unittest.TestCase):
    def test_point_addition(self):
        point1 = abc.Vector(1, 2)
        point2 = abc.Vector(3, 4)
        point3 = abc.Vector(4, 6)
        self.assertEqual(point1 + point2, point3)

    def test_change_position(self):
        let_me_test_move = units.abc.MovableUnit("test", (3, 4))
        let_me_test_move.position = (1, 1,)
        self.assertEqual(let_me_test_move.position, (1, 1,))

    def test_move(self):
        troop = units.abc.SelfMovableUnit("troop", (3, 4), (1, 1))
        troop.move()
        self.assertEqual(troop.position, (4, 5,))

    def test_coloring(self):
        # pylint: disable=invalid-name
        unit_dict = {"infantry": units.Infantry}
        RED = 0xFF0000
        red_HQ = units.Headquarters(RED, unit_dict)
        red_unit = red_HQ.create_unit("infantry", (0, 0))
        self.assertEqual(red_unit.__class__.__name__, "ColoredInfantry")
        self.assertEqual(red_unit.color, RED)


if __name__ == "__main__":
    unittest.main()
