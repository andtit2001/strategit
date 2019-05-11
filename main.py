# -*- coding: utf-8 -*-
"""A simple strategy game."""
import cmd
from collections import deque, namedtuple
import errno
import json
import shlex
import os
import random


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


class GameState:
    """
    Class that represents game state
    (number of players and units, their stats and so on)
    """

    filename = ""
    list_of_player_infos = []

    def __init__(self, player_count):
        self.list_of_player_infos = [PlayerInfo(
            random.randrange(0, 2**24), False, 1000,
            [], [], []
        )]
        for _ in range(player_count - 1):
            self.list_of_player_infos.append(PlayerInfo(
                random.randrange(0, 2**24), True, 1000,
                [], [], []
            ))

    def load(self, filename):
        """Replace current state with one loaded from file"""
        with open(filename, encoding="utf-8") as file:
            self.list_of_player_infos = json.load(file)
        self.filename = filename

    def save(self, filename):
        """Save state to the file"""
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.list_of_player_infos, file)


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
