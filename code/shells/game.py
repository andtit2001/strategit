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
    current_player = 0
    action_queue = deque()
    selected_unit = None

    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.current_player = game_state.current_player
        self.prompt = "Game[{}]> ".format(self.current_player)

    @staticmethod
    def _get_ints(string, count):
        if not string:
            return None
        nums = string.split()[:count]
        try:
            nums = list(map(int, nums))
        except ValueError:
            return None
        nums.extend([None] * (count - len(nums)))
        return nums

    @staticmethod
    def _validate_ints(ints, upper_bounds, lower_bounds=None):
        if not lower_bounds:
            lower_bounds = [0] * len(ints)
        for i, value in enumerate(ints):
            if value not in range(lower_bounds[i], upper_bounds[i]):
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
Return to the menu (use "abort" to exit game forcefully)"""
        # pylint: disable=unused-argument
        return self.do_menu(arg)

    def do_show(self, arg):
        """Usage: show <x1> <y1> <x2> <y2>
Show part of field as textual axis-aligned rectangle"""
        arg = self._get_ints(arg, 4)
        if not arg or not arg[-1]:
            self.stdout.write("""\
Please specify four integers as rectangle coordinates.\n""")
            return
        if arg[0] > arg[2]:
            arg[0], arg[2] = arg[2], arg[0]
        if arg[1] > arg[3]:
            arg[1], arg[3] = arg[3], arg[1]
        upper_bounds = (
            self.game_state.width,
            self.game_state.height,
            self.game_state.width,
            self.game_state.height
        )
        index = self._validate_ints(arg, upper_bounds)
        if index < 2:
            self.stdout.write(
                "All coordinates should lie in range [0, {}).\n".format(
                    upper_bounds[index])
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
        if not arg or not arg[-1]:
            self.stdout.write(
                "Please specify two integers as cell coordinates.\n")
            return
        bounds = (self.game_state.width, self.game_state.height,)
        index = self._validate_ints(arg, bounds)
        if index < 2:
            self.stdout.write(
                "{} coordinate should lie in range [0, {}).\n".format(
                    ("Horizontal", "Vertical")[index], bounds[index])
            )
            return

        if self.game_state.game_field[arg[1]][arg[0]]:
            for unit_id in self.game_state.game_field[arg[1]][arg[0]]:
                self.stdout.write(
                    str(self.game_state.list_of_player_infos
                        [self.current_player].unit_list[unit_id])
                    + '\n')
        else:
            self.stdout.write("Nothing here.\n")

    def do_select(self, arg):
        """Usage: select <x> <y> [index]
Select unit in specified cell (use "inspect" to get index of the unit)
If index is omitted, it is equal to 0."""
        arg = self._get_ints(arg, 3)
        if not arg or not arg[1]:
            self.stdout.write("""\
Please specify two or three integers as cell coordinates and index.\n""")
            return
        bounds = (self.game_state.width, self.game_state.height,)
        index = self._validate_ints(arg[:2], bounds)
        if index < 2:
            self.stdout.write(
                "{} coordinate should lie in range [0, {}).\n".format(
                    ("Horizontal", "Vertical")[index], bounds[index])
            )
            return

        if not self.game_state.game_field[arg[1]][arg[0]]:
            self.stdout.write("Nothing to select.\n")
            return
        arg[2] = arg[2] if arg[2] else 0
        if arg[2] not in range(len(
                self.game_state.game_field[arg[1]][arg[0]])):
            self.stdout.write(
                "Index should lie in range [0, {}).\n".format(
                    len(self.game_state.game_field[arg[1]][arg[0]]))
            )
            return

        self.selected_unit = self.game_state.game_field[arg[1]][arg[0]][arg[2]]
        self.prompt = "Game[{}].Unit[{}]> ".format(
            self.current_player, self.selected_unit)

    def do_deselect(self, arg):
        """Usage: deselect
Deselect currently selected unit"""
        # pylint: disable=unused-argument
        self.selected_unit = None
        self.prompt = "Game[{}]> ".format(self.current_player)

    def do_status(self, arg):
        """Usage: status
List all planned actions"""
        # pylint: disable=unused-argument
        for action in self.action_queue:
            self.stdout.write(str(action) + '\n')

    def do_undo(self, arg):
        """Usage: undo
Cancel last planned action"""
        # pylint: disable=unused-argument
        try:
            self.action_queue.pop()
        except IndexError:
            self.stdout.write("Nothing to cancel.\n")

    def do_commit(self, arg):
        """Apply all planned actions"""
        # pylint: disable=unused-argument
