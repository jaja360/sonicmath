import random
from dataclasses import dataclass


@dataclass(frozen=True)
class MathProblem:
    text: str
    answer: int


def _generate_division_problem(max_operand):
    # Avoid trivial division like x / 1 or x / x = 1.
    while True:
        answer = random.randint(2, max_operand // 2)
        max_divisor = max_operand // answer
        if max_divisor < 2:
            continue

        right = random.randint(2, max_divisor)
        left = answer * right
        return MathProblem(f"{left} / {right}", answer)


def generate_problem(level_config):
    operation = random.choice(tuple(level_config.max_operands))
    max_operand = level_config.max_operands[operation]

    if operation == "+":
        left = random.randint(0, max_operand)
        right = random.randint(0, max_operand)
        return MathProblem(f"{left} + {right}", left + right)

    if operation == "-":
        left = random.randint(0, max_operand)
        right = random.randint(0, left)
        return MathProblem(f"{left} - {right}", left - right)

    if operation == "*":
        left = random.randint(0, max_operand)
        right = random.randint(0, max_operand)
        return MathProblem(f"{left} * {right}", left * right)

    return _generate_division_problem(max_operand)
