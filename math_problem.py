import random
from dataclasses import dataclass


@dataclass(frozen=True)
class MathProblem:
    text: str
    answer: int


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

    left = max_operand + 1
    while left > max_operand:
        answer = random.randint(1, max_operand)
        right = random.randint(1, max_operand)
        left = answer * right

    return MathProblem(f"{left} / {right}", answer)
