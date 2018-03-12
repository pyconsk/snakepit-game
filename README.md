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

**NOTE**: The game is by default available under the URL: `http://0.0.0.0:8111/index.html` (requesting `/index.html` is necessary).


## PyCon SK 2018 Programming Contest

Refactored code and added support for robot snakes:

    bin/run_robot.py --help

The robot snake documentation is available here: https://github.com/pyconsk/snakepit-game/blob/master/doc/snake.md

### Winning Robot Snakes

- 1st place: https://gist.github.com/marekmichalik
- 2nd place: https://github.com/martin-sucha/pyconsk-2018-snakepit-bot
- 3rd place: https://github.com/Artimi/snakepit-game/blob/pyconsk2018/robots/number.py + http://www.petrsebek.cz/2018/03/snakepit-contest-at-pyconsk-2018.html


## Original Snakepit

The game and tutorial was originally written by Kyrylo Subbotin @ [7WebPages](https://7webpages.com/).

Original game source code: https://github.com/7WebPages/snakepit-game

Demo of the original game: http://snakepit-game.com

### Tutorial

- Part 1: https://7webpages.com/blog/writing-online-multiplayer-game-with-python-asyncio-getting-asynchronous/
- Part 2: https://7webpages.com/blog/writing-online-multiplayer-game-with-python-and-asyncio-writing-game-loop/
- Part 3 (game explanation): https://7webpages.com/blog/writing-online-multiplayer-game-with-python-and-asyncio-part-3/
