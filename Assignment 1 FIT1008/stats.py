import abc

from data_structures.referential_array import ArrayR
from data_structures.stack_adt import ArrayStack
import math 
class Stats(abc.ABC):

    @abc.abstractmethod
    def get_attack(self):
        pass

    @abc.abstractmethod
    def get_defense(self):
        pass

    @abc.abstractmethod
    def get_speed(self):
        pass

    @abc.abstractmethod
    def get_max_hp(self):
        pass


class SimpleStats(Stats):
    """
    SimpleStats is a class that represents the simple stats of a Pokemon.
    """
    def __init__(self, attack, defense, speed, max_hp) -> None:
        """
        Constructor of the class.
        Best = Worst = O(1) as there are only assignments and arithmetic operations which are constant time
        """
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.max_hp = max_hp

    def get_attack(self):
        return self.attack

    def get_defense(self):
        return self.defense

    def get_speed(self):
        return self.speed
    
    def get_max_hp(self):
        return self.max_hp

class ComplexStats(Stats):
    """
    ComplexStats is a class that represents the complex stats of a Pokemon.
    """

    def __init__(
        self,
        attack_formula: ArrayR[str],
        defense_formula: ArrayR[str],
        speed_formula: ArrayR[str],
        max_hp_formula: ArrayR[str],
    ) -> None:
        self.attack_formula = attack_formula
        self.defense_formula = defense_formula
        self.speed_formula = speed_formula
        self.max_hp_formula = max_hp_formula

    def _evaluate_expression(self, formula, level):
        """
        Evaluates a given formula with a given level.
        Best = Worst = O(n) where n is the length of the formula as we iterate through the formula
        The rest is all O(1) as there are only assignments and arithmetic operations which are constant time
        """
        stack = ArrayStack(len(formula))

        for token in formula:

            if token == 'level':
                stack.push(level)
            elif token == 'power':
                b = stack.pop()
                a = stack.pop()
                stack.push(a ** b)
            elif token == 'sqrt':
                a = stack.pop()
                stack.push(int(math.sqrt(a)))
            elif token == 'middle':
                c = stack.pop()
                b = stack.pop()
                a = stack.pop()
                if (a <= b and b <= c) or (c <= b and b <= a):
                    stack.push(b)
                elif (b <= a and a <= c) or (c <= a and a <= b):
                    stack.push(a)
                else:
                    stack.push(c)
            elif token == "+":
                b = stack.pop()
                a = stack.pop()
                stack.push(a+b)
            elif token == "-":
                b = stack.pop()
                a = stack.pop()
                stack.push(a-b)
            elif token == "*":
                b = stack.pop()
                a = stack.pop()
                stack.push(a*b)
            elif token == "/":
                b = stack.pop()
                a = stack.pop()
                stack.push(a/b)
            else:
                stack.push(int(token))

        return stack.pop()

    """
    All the below function has a time complexity of O(n) where n is the length of the formula as we call the _evaluate_expression function
    """
    def get_attack(self, level: int):
        return int(self._evaluate_expression(self.attack_formula, level))

    def get_defense(self, level: int):
        return int(self._evaluate_expression(self.defense_formula, level))

    def get_speed(self, level: int):
        return int(self._evaluate_expression(self.speed_formula, level))

    def get_max_hp(self, level: int):
        return int(self._evaluate_expression(self.max_hp_formula, level))


