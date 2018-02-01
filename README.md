# Snakepit for PyCon SK

Online multiplayer snake game written in [Python](https://www.python.org/) and [asyncio](https://docs.python.org/3/library/asyncio.html).

## Installation

```bash
git clone https://github.com/pyconsk/snakepit-game
cd snakepit-game
python3.6 -m venv env
source env/bin/activate
pip install -r doc/requirements.txt
export PYTHONPATH=$(pwd -P)
bin/run.py
```


## PyCon SK Programming Contest

Refactored code and added support for robot snakes:

    bin/run_robot.py --help


## Original Snakepit

The game and tutorial was originally written by Kyrylo Subbotin.

Original game source code: https://github.com/7WebPages/snakepit-game

Demo of the original game: http://snakepit-game.com

### Tutorial

- Part 1: https://7webpages.com/blog/writing-online-multiplayer-game-with-python-asyncio-getting-asynchronous/
- Part 2: https://7webpages.com/blog/writing-online-multiplayer-game-with-python-and-asyncio-writing-game-loop/
- Part 3 (game explanation): https://7webpages.com/blog/writing-online-multiplayer-game-with-python-and-asyncio-part-3/
