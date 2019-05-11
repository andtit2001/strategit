# -*- coding: utf-8 -*-
"""A simple strategy game."""
import cmd
from collections import deque, namedtuple
import errno
import json
import shlex
import os
import random


from game import units
# from game.units import abc as units_abs


PlayerInfo = namedtuple(
    "PlayerInfo",
    [
        "color",
        "AI",
        "money",
        "unit_list",
        "squad_list",
        "army_list"
    ]
)


# pylint: disable=missing-docstring
class GameEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, units.Headquarters):
            return {
                "__unittype__": "hq",
                "color": obj.color,
                "unit_dict": obj._unit_dict
            }
        return json.JSONEncoder.default(self, obj)


def game_object_hook(dct):
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
    list_of_player_infos = []

    def __init__(self, player_count):
        color = random.randrange(0, 2**24)
        self.list_of_player_infos = [PlayerInfo(
            color, False, 1000,
            [units.Headquarters(color, {})], [], []
        )]
        for _ in range(player_count - 1):
            color = random.randrange(0, 2**24)
            self.list_of_player_infos.append(PlayerInfo(
                color, True, 1000,
                [units.Headquarters(color, {})], [], []
            ))

    def load(self, filename):
        """Replace current state with one loaded from file"""
        with open(filename, encoding="utf-8") as file:
            self.list_of_player_infos = json.load(file,
                                                  object_hook=game_object_hook)
        self.filename = filename

    def save(self, filename=""):
        """Save state to the file"""
        if not filename:
            filename = self.filename
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.list_of_player_infos, file, cls=GameEncoder)


class MenuShell(cmd.Cmd):
    """Class for handling menu commands"""
    intro = "Welcome to the game! Please create new save file \
or load an existing one."
    prompt = "Menu> "
    game_state = None

    # pylint: disable=unused-argument
    @staticmethod
    def do_exit(arg):
        # pylint: disable=missing-docstring
        return True

    # pylint: disable=invalid-name,unused-argument
    @staticmethod
    def do_EOF(arg):
        # pylint: disable=missing-docstring
        return True

    def do_new(self, arg):
        """Create new save file"""
        arg = "saves/{}.json".format(shlex.split(arg)[0])

        if not os.path.exists("saves"):
            try:
                os.mkdir("saves")
            # pylint: disable=broad-except
            except BaseException as err:
                self.stdout.write("System error: {}\n".format(err))
                return
        if not os.path.isdir("saves"):
            self.stdout.write("Please delete file 'saves' and try again.")
            return
        if os.path.exists(arg):
            self.stdout.write("Error: {}\n".format(os.strerror(errno.EEXIST)))
            return

        self.game_state = GameState(2)
        try:
            self.game_state.save(arg)
        except OSError as err:
            self.stdout.write("OSError: {}\n".format(err))
            self.game_state = None
            return

    def do_load(self, arg):
        """Load existing save file"""
        if not arg:
            self.stdout.write("Please specify name of save file.")
            return

        arg = "saves/{}.json".format(shlex.split(arg)[0])
        if not os.path.exists(arg):
            self.stdout.write("Error: {}\n".format(os.strerror(errno.ENOENT)))
            return

        if not self.game_state:
            self.game_state = GameState(1)
        self.game_state.load(arg)

    def do_save(self, arg):
        """
        Save game to the specified file
        (defaults to the file from which it was loaded)
        """
        arg = shlex.split(arg)
        if not arg:
            arg = self.game_state.filename
        else:
            arg = "saves/{}.json".format(arg[0])
        try:
            self.game_state.save(arg)
        except OSError as err:
            self.stdout.write("OSError: {}\n".format(err))
            return

    def do_rm(self, arg):
        if not arg:
            self.stdout.write("Please specify name of save file.")
            return

        arg = "saves/{}.json".format(shlex.split(arg)[0])
        os.remove(arg)

    # pylint: disable=unused-argument
    def do_start(self, arg):
        """Start game"""
        if self.game_state is None:
            self.stdout.write("Please create or load save file to start.\n")
            return
        GameShell(self.game_state).cmdloop()


class GameShell(cmd.Cmd):
    """Class for handling game commands"""
    intro = "You are in the game. Congratulations!"
    prompt = "Game> "

    game_state = None
    action_queue = deque()

    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state

    # pylint: disable=unused-argument
    def do_exit(self, arg):
        # pylint: disable=missing-docstring
        self.stdout.write("Do not forget to save game before exiting!\n")
        return True

    # pylint: disable=unused-argument
    def do_commit(self, arg):
        """Start the battle!"""


random.seed()
MenuShell().cmdloop()
