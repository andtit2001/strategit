__name__ = "units"

from . import abc


class Headquarters(abc.UnitFactory):
    _color = None
    __unit_dict = None
    __colored_unit = None

    def __init__(self, color, unit_dict):
        super().__init__()
        self._color = color
        self.__unit_dict = dict()

        def getcolor(self):
            return self._color
        for key, value in unit_dict.items():
            self.__unit_dict[key] = type(
                "Colored" + value.__name__,
                (value,),
                {"_color": color,
                 "color": property(getcolor)})
        self.__colored_unit = type(
            "ColoredUnit",
            (abc.Unit,),
            {"_color": color,
             "color": property(getcolor)})

    @property
    def color(self):
        return self._color

    def create_unit(self, name, pos):
        new_unit = None
        if name in self.__unit_dict:
            new_unit = self.__unit_dict[name](name, pos)
        else:
            new_unit = self.__colored_unit(name, pos)
        return new_unit


class Infantry(abc.MovableBattleUnit):
    pass

class Vehicle(abc.MovableBattleUnit):
    pass
