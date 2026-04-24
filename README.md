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

## Items

Power-ups spawn in a separate lane and are collected automatically on contact.
They use their own spawn window, so they appear between hazards instead of at
the same time. Power-downs replace some hazard spawns; answer correctly to jump
over them and avoid their effect. Temporary effects last for a number of
resolved questions, whether the answer was correct or not.

### Power-ups

- Red potion: restore 10 HP
- Blue potion: restore 20 HP
- Coin+: boosts score rewards by 50% for 5 questions
- Gift: reduce obstacle damage for 5 questions
- Spring: reduce obstacle damage for 3 questions
- Medical cross: debuff immunity for 5 questions
- Pill: clear negative speed, damage, score and special effects
- Clover: clear the current status
- White square: clear negative effects and grant debuff immunity for 3 questions
- Stopwatch: slows the game for 5 questions
- Purple flask: clear all current negative effects
- Red gem: ignores the next hit

### Power-downs

- Fire: burned for 5 questions, lose 1 HP after each resolved question
- Mushroom: poisoned for 5 questions, lose 2 HP after each resolved question
- Crossed gift: increase obstacle damage for 5 questions
- Crossed spring: increase obstacle damage for 3 questions
- Crossed medical cross: buffs are blocked for 5 questions
- Crossed coin: reduce score rewards by 50% for 5 questions
- Grey bomb: speeds up the game for 5 questions
- Grey plus: healing is blocked for 5 questions
- Black cloud: hazards are dimmed for 5 questions
- Vortex: clears all active temporary effects

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
