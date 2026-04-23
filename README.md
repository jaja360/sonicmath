# SonicMath

SonicMath is a python game that allows you to practice your math skills while
having fun. The game is designed to be simple and easy to play, but also
challenging enough to keep you engaged.

## How to Play

The game consists of a series of arithmetic math problems that you need to solve.
The running Sonic character in the background will jump over obstacles only if
you answer the math problem correctly and in time. If you answer incorrectly or
take too long, Sonic will hit the obstacle and lose some of his health. The game
ends when Sonic's health reaches zero. Press `ESC` at any time during a run to
pause and resume the game.

## Installation

To run SonicMath, you will need to have Python installed on your computer.
You can clone the project and install the required dependencies using:
```bash
git clone git@github.com:jaja360/sonicmath.git
cd sonicmath
uv install
```

## Running the Game

To start the game, simply run the following command in your terminal:
```bash
uv run python main.py
```

You can also start the game with optional flags:
```bash
uv run python main.py --no-sound
uv run python main.py --start-level 10
uv run python main.py --start-hp 15
uv run python main.py --no-sound --start-level 10
uv run python main.py --start-level 10 --start-hp 30
```
