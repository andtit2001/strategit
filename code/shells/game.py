# -*- coding: utf-8 -*-
"""This module contains the only class, `GameShell`"""
import cmd
from collections import deque, namedtuple
import random
import sys

from .. import units
from ..units import abc as units_abc


class GameShell(cmd.Cmd):
    """Class for handling game commands"""
    intro = "You are in the game. Congratulations!"
    prompt = "Game> "

    game_state = None
    current_player = 0
    action_queue = None
    selected_unit = None
    selected_unit_id = None
    unit_count = 0

    def __init__(self, game_state, stdin=None, stdout=None):
        super().__init__(stdin=stdin, stdout=stdout)
        self.game_state = game_state
        self.current_player = game_state.current_player
        self.unit_count = game_state.unit_count
        self.prompt = "Game[{}]> ".format(self.current_player)
        self.action_queue = deque()

    @staticmethod
    def _get_ints(string, count):
        """Get list of not more than `count` integers"""
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
        """Check that `ints` lie in corresponding ranges"""
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
        if not arg or arg[-1] is None:
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
            str_list = []
            for cell in line[arg[0]:arg[2] + 1]:
                if not cell:
                    str_list.append('_')
                elif len(cell) > 1:
                    str_list.append('M')
                elif self.game_state.unit_dict[cell[0]].color == \
                    self.game_state\
                    .list_of_player_infos[self.current_player]\
                        .color:
                    str_list.append(self.game_state.unit_dict[cell[0]]
                                    .char.upper())
                else:
                    str_list.append(self.game_state.unit_dict[cell[0]]
                                    .char.lower())
            self.stdout.write(' '.join(str_list) + '\n')

    def do_inspect(self, arg):
        """Usage: inspect <x> <y>
Show info about unit(s) in specified cell."""
        arg = self._get_ints(arg, 2)
        if not arg or arg[-1] is None:
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
                self.stdout.write("Unit {} - ".format(unit_id)
                                  + str(self.game_state.unit_dict[unit_id])
                                  + '\n')
        else:
            self.stdout.write("Nothing here.\n")

    def do_select(self, arg):
        """Usage: select <x> <y> [index]
Select unit in specified cell (use "inspect" to get index of the unit)
If index is omitted, it is equal to 0."""
        arg = self._get_ints(arg, 3)
        if not arg or arg[1] is None:
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

        unit_id = self.game_state.game_field[arg[1]][arg[0]][arg[2]]
        if self.game_state.unit_dict[unit_id].color != \
                self.game_state\
                .list_of_player_infos[self.current_player].color:
            self.stdout.write("Please select YOUR unit.\n")
            return
        self.selected_unit = self.game_state.unit_dict[unit_id]
        self.selected_unit_id = unit_id
        self.prompt = "Game[{}].Unit[{}]> ".format(
            self.current_player, unit_id)

    def do_deselect(self, arg):
        """Usage: deselect
Deselect currently selected unit"""
        # pylint: disable=unused-argument
        self.selected_unit = None
        self.selected_unit_id = None
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

    def do_spawn(self, arg):
        """Usage: spawn <name>
Create unit with a given name.
List of allowed names: infantry, vehicle"""
        if not isinstance(self.selected_unit, units.Headquarters):
            self.stdout.write("Please select HQ unit.\n")
            return
        if not arg:
            self.stdout.write("Please specify a unit name.\n")
            return
        arg = arg.split()[0]
        if not self.selected_unit.can_create(arg):
            self.stdout.write("Error: invalid unit name \
(see help for allowed names)\n")
            return
        self.action_queue.append(Action(
            "spawn", self.selected_unit_id, {"class": arg}))

    def do_move(self, arg):
        """Usage: move <dx> <dy>
Move selected unit on vector (dx, dy)
(both numbers should be in range [-1, 1])"""
        if not isinstance(self.selected_unit, units_abc.MovableUnit):
            self.stdout.write("Please select infantry of vehicle unit.\n")
            return
        arg = self._get_ints(arg, 2)
        if not arg or arg[-1] is None:
            self.stdout.write(
                "Please specify two integers as cell coordinates.\n")
            return
        index = self._validate_ints(arg, (2, 2,), (-1, -1,))
        if index < 2:
            self.stdout.write(
                "{} should lie in range [-1, 1].\n".format(("dx", "dy")[index])
            )
            return
        bounds = (self.game_state.width, self.game_state.height,)
        index = self._validate_ints(
            self.selected_unit.position + units_abc.Vector(*arg), bounds)
        if index < 2:
            self.stdout.write(
                "New {} coordinate should lie in range [0, {}).\n".format(
                    ("horizontal", "vertical")[index], bounds[index])
            )
            return
        self.action_queue.append(Action(
            "move", self.selected_unit_id, {"delta": units_abc.Vector(*arg)}))

    def do_attack(self, arg):
        """Usage: attack <target_id>
Attack selected unit if it is located in adjacent cell"""
        if not isinstance(self.selected_unit, units_abc.BattleUnit):
            self.stdout.write("Please select infantry of vehicle unit.\n")
            return
        arg = self._get_ints(arg, 1)
        if not arg or arg[0] is None:
            self.stdout.write("Please specify unit ID.\n")
            return
        arg = arg[0]
        if arg not in self.game_state.unit_dict:
            self.stdout.write("Please specify ID of an existing unit.\n")
            return
        if not isinstance(self.game_state.unit_dict[arg],
                          units_abc.BattleUnit):
            self.stdout.write("Target must be infantry or vehicle unit.\n")
            return
        target_pos = self.game_state.unit_dict[arg].position
        if max(map(abs, target_pos - self.selected_unit.position)) > 1:
            self.stdout.write("Target must be located in adjacent cell.\n")
            return
        self.action_queue.append(Action(
            "attack", self.selected_unit_id, {"target_id": arg}))

    def do_commit(self, arg):
        """Apply all planned actions"""
        # pylint: disable=unused-argument
        for action in self.action_queue:
            if action.name == "spawn":
                hq = self.game_state.unit_dict[action.unit_id]
                possible_pos = []
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if (dy != 0 or dx != 0)\
                                and hq.position.x + dx\
                                in range(0, self.game_state.width)\
                                and hq.position.y + dy\
                                in range(0, self.game_state.height):
                            possible_pos.append(
                                (hq.position.x + dx,
                                 hq.position.y + dy,))
                selected_pos = random.choice(possible_pos)

                new_unit = hq.create_unit(action.params["class"], selected_pos)

                self.game_state.game_field[selected_pos[1]][selected_pos[0]]\
                    .append(self.unit_count)
                self.game_state.unit_dict[self.unit_count] = new_unit
                self.unit_count += 1
                self.game_state.unit_count = self.unit_count
            elif action.name == "move":
                old_pos = self.game_state.unit_dict[action.unit_id].position
                new_pos = old_pos + action.params["delta"]
                self.game_state.unit_dict[action.unit_id].position = new_pos
                self.game_state.game_field[old_pos[1]][old_pos[0]].remove(
                    action.unit_id)
                self.game_state.game_field[new_pos[1]][new_pos[0]].append(
                    action.unit_id)
            elif action.name == "attack":
                if action.params["target_id"] not in self.game_state.unit_dict:
                    continue
                target = self.game_state.unit_dict[action.params["target_id"]]
                self.game_state.unit_dict[action.unit_id].attack(target)
                if target.health <= 0:
                    self.game_state.game_field[target.position[1]]\
                        [target.position[0]].remove(action.params["target_id"])
                    del self.game_state.unit_dict[action.params["target_id"]]

        self.action_queue.clear()
        self.current_player += 1
        if self.current_player == len(
                self.game_state.list_of_player_infos):
            self.current_player = 0
        self.game_state.current_player = self.current_player
        self.do_deselect(None)


class Action(namedtuple("ActionTuple", ["name", "unit_id", "params"])):
    """Small class fot storing player's actions"""

    def __str__(self):
        if self.name == "spawn":
            return "Unit {}: Create unit of class \"{}\"".format(
                self.unit_id, self.params["class"])
        if self.name == "attack":
            return "Unit {}: Attack unit {}".format(
                self.unit_id, self.params["target_id"])
        return ""
