# -*- coding: utf-8 -*-
"""This module contains the only class, `GameShell`"""
import cmd
from collections import deque
import sys


class GameShell(cmd.Cmd):
    """Class for handling game commands"""
    intro = "You are in the game. Congratulations!"
    prompt = "Game> "

    game_state = None
    action_queue = deque()
    selected_unit = None

    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.prompt = "Game[{}]> ".format(game_state.current_player)

    @staticmethod
    def _get_ints(string, count):
        if not string:
            return None
        nums = string.split()[:count]
        if len(nums) < count:
            return None
        try:
            nums = list(map(int, nums))
            return nums
        except ValueError:
            return None

    @staticmethod
    def _validate_ints(ints, upper_bounds, lower_bounds=None):
        if not lower_bounds:
            lower_bounds = [0] * len(ints)
        for i, value in enumerate(ints):
            if not lower_bounds[i] <= value <= upper_bounds[i]:
                return i
        return len(ints)

    @staticmethod
    def do_abort(arg):
        """Usage: abort
Exit game without saving progress"""
        # pylint: disable=unused-argument
        sys.exit()

    def do_menu(self, arg):
        """Usage: menu
Return to the menu"""
        # pylint: disable=unused-argument
        self.stdout.write("Do not forget to save game before exiting!\n")
        return True

    def do_exit(self, arg):
        """Usage: exit
Return to the menu (use \"abort\" to exit game forcefully)"""
        # pylint: disable=unused-argument
        return self.do_menu(arg)

    def do_show(self, arg):
        """Usage: show <x1> <y1> <x2> <y2>
Show part of field as textual axis-aligned rectangle"""
        arg = self._get_ints(arg, 4)
        if not arg:
            self.stdout.write("""\
Please specify four integers as rectangle coordinates.\n""")
            return
        if arg[0] > arg[2]:
            arg[0], arg[2] = arg[2], arg[0]
        if arg[1] > arg[3]:
            arg[1], arg[3] = arg[3], arg[1]
        upper_bounds = (
            self.game_state.width - 1,
            self.game_state.height - 1,
            self.game_state.width - 1,
            self.game_state.height - 1,
        )
        index = self._validate_ints(arg, upper_bounds)
        if index < 2:
            self.stdout.write(
                "All coordinates should lie in range [0, {}).\n".format(
                    upper_bounds[index] + 1)
            )
            return
        for line in self.game_state.game_field[arg[1]:arg[3] + 1]:
            self.stdout.write(' '.join(
                ['a' if unit else '_'
                 for unit in line[arg[0]:arg[2] + 1]]) + '\n')

    def do_inspect(self, arg):
        """Usage: inspect <x> <y>
Show info about unit(s) in specified cell."""
        arg = self._get_ints(arg, 2)
        if not arg:
            self.stdout.write(
                "Please specify two integers as cell coordinates.\n")
            return
        bounds = (self.game_state.width - 1, self.game_state.height - 1,)
        index = self._validate_ints(arg, bounds)
        if index < 2:
            self.stdout.write(
                "{} coordinate should lie in range [0, {}).\n".format(
                    ("Horizontal", "Vertical")[index], bounds[index] + 1)
            )
            return
        if self.game_state.game_field[arg[1]][arg[0]]:
            for unit_id in self.game_state.game_field[arg[1]][arg[0]]:
                self.stdout.write(
                    str(self.game_state.list_of_player_infos
                        [self.game_state.current_player].unit_list[unit_id])
                    + '\n')
        else:
            self.stdout.write("Nothing here.\n")

    def do_select(self, arg):
        """Usage: select <x> <y> [index]
Select unit in specified cell (use "inspect" to get index of the unit)"""

    def do_status(self, arg):
        """Usage: status
List all planned actions"""
        # pylint: disable=unused-argument
        for action in self.action_queue:
            self.stdout.write(str(action) + '\n')

    def do_undo(self, arg):
        """Usage: undo
Select unit in specified cell (use "inspect" to get index of the unit)"""
        # pylint: disable=unused-argument
        self.action_queue.pop()

    def do_commit(self, arg):
        """Apply all planned actions"""
        # pylint: disable=unused-argument
