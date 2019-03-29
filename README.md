# Game project, part 1
This is small "model" (or even framework... because it's too small for model) of strategy game.

## How to run?
1. If you want to "play", run `main.py`
2. If you want to run tests, run `tester.py`

## Structure of the code
1. Abstract base classes
* General classes (`Unit`, `MovableUnit`, `SelfMovableUnit`)
* Battle specializations (`BattleUnit`, `MovableBattleUnit`)
* `UnitFactory`
2. Example classes
* `Infantry`, `Vehicle` (two types of units)
* `Headquarters` (unit factory that adds attribute "color" which is represented by integer; I recommend using it as RGB code)
3. Main file (does effectively nothing)
4. Testing class (uses `unittest` module for obvious goal)

This "model" is not a final version. It will be (probably) extended (and even rewritten).
