# -*- coding: utf-8 -*-
"""This module contains the only class, `MenuShell`"""
import cmd
import errno
import os
from pathlib import Path
import shlex

from .game import GameShell
from ..state import FIELD_WIDTH, FIELD_HEIGHT, GameState


class MenuShell(cmd.Cmd):
    """Class for handling menu commands"""
    intro = "Welcome to the game! Please create new save file \
or load an existing one."
    prompt = "Menu> "

    game_state = None

    @staticmethod
    def do_exit(arg):
        """Usage: exit
Exit game without save (use "save" to explicitly save progress)"""
        # pylint: disable=unused-argument
        return True

    @staticmethod
    def do_EOF(arg):
        """Usage: EOF
Exit game without save (use "save" to explicitly save progress)"""
        # pylint: disable=invalid-name,unused-argument
        return True

    def do_ls(self, arg):
        """Usage: ls
List all saved games"""
        # pylint: disable=unused-argument
        for file in Path("saves").iterdir():
            self.stdout.write(file.stem + '\n')

    def do_touch(self, arg):
        """Usage: touch <filename>
Create new save file in directory \"saves\""""
        arg = "saves/{}.json".format(shlex.split(arg)[0])

        saves_path = Path("saves")
        if not saves_path.exists():
            try:
                saves_path.mkdir()
            # pylint: disable=broad-except
            except BaseException as err:
                self.stdout.write("System error: {}\n".format(err))
                return
        if not saves_path.is_dir():
            self.stdout.write("Please delete file 'saves' and try again.\n")
            return
        if Path(arg).exists():
            self.stdout.write("Error: {}\n".format(os.strerror(errno.EEXIST)))
            return

        self.game_state = GameState(2, FIELD_WIDTH, FIELD_HEIGHT)
        try:
            self.game_state.save(arg)
        except OSError as err:
            self.stdout.write("OSError: {}\n".format(err))
            self.game_state = None
            return

    def do_load(self, arg):
        """Usage: load <filename>
Load existing save file"""
        if not arg:
            self.stdout.write("Please specify name of save file.\n")
            return

        arg = "saves/{}.json".format(shlex.split(arg)[0])
        if not Path(arg).exists():
            self.stdout.write("Error: {}\n".format(os.strerror(errno.ENOENT)))
            return

        if not self.game_state:
            self.game_state = GameState(1, 1, 1)
        self.game_state.load(arg)

    def do_save(self, arg):
        """Usage: save [filename]
Save game to the specified file
(defaults to the file from which it was loaded)"""
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
        """Usage: rm <filename>
Remove specified save file"""
        if not arg:
            self.stdout.write("Please specify name of save file.\n")
            return

        arg = "saves/{}.json".format(shlex.split(arg)[0])
        try:
            Path(arg).unlink()
        except FileNotFoundError:
            self.stdout.write("There is no such save file.\n")
        except OSError as err:
            self.stdout.write("System error: {}\n".format(err))

    def do_start(self, arg):
        """Usage: start
Start game"""
        # pylint: disable=unused-argument
        if self.game_state is None:
            self.stdout.write("Please create or load save file to start.\n")
            return
        GameShell(self.game_state).cmdloop()
