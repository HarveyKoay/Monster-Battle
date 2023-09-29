from __future__ import annotations

from enum import auto
from typing import Optional

from base_enum import BaseEnum

from data_structures.referential_array import ArrayR
from data_structures.array_sorted_list import ArraySortedList

class Element(BaseEnum):
    """
    Element Class to store all different elements as constants, and associate indicies with them.
    Example:
    ```
    print(Element.FIRE.value)         # 1
    print(Element.GRASS.value)        # 3

    print(Element.from_string("Ice")) # Element.ICE
    ```
    """

    FIRE = auto()
    WATER = auto()
    GRASS = auto()
    BUG = auto()
    DRAGON = auto()
    ELECTRIC = auto()
    FIGHTING = auto()
    FLYING = auto()
    GHOST = auto()
    GROUND = auto()
    ICE = auto()
    NORMAL = auto()
    POISON = auto()
    PSYCHIC = auto()
    ROCK = auto()
    FAIRY = auto()
    DARK = auto()
    STEEL = auto()

    @classmethod
    def from_string(cls, string: str) -> Element:
        """
        Returns the element corresponding to the string.
        e is the the number of elements in the list of elements
        It is not a constant as the number of elements can increase

        Best case:  O(1) is when the element is the first element in the list
        Worst case: O(e) is when the element is the last element in the list
        """
        for elem in Element:
            if elem.name.lower() == string.lower():
                return elem
        raise ValueError(f"Unexpected string {string}")

class EffectivenessCalculator:
    """
    Helper class for calculating the element effectiveness for two elements.

    This class follows the singleton pattern.

    Usage:
        EffectivenessCalculator.get_effectiveness(elem1, elem2)
    """

    instance: Optional[EffectivenessCalculator] = None

    def __init__(self, element_names: ArrayR[str], effectiveness_values: ArrayR[float]) -> None:
        """
        Initialise the Effectiveness Calculator.

        The first parameter is an ArrayR of size n containing all element_names.
        The second parameter is an ArrayR of size n*n, containing all effectiveness values.
            The first n values in the array is the effectiveness of the first element
            against all other elements, in the same order as element_names.
            The next n values is the same, but the effectiveness of the second element, and so on.

        Example:
        element_names: ['Fire', 'Water', 'Grass']
        effectivness_values: [0.5, 0.5, 2, 2, 0.5, 0.5, 0.5, 2, 0.5]
        Fire is half effective to Fire and Water, and double effective to Grass [0.5, 0.5, 2]
        Water is double effective to Fire, and half effective to Water and Grass [2, 0.5, 0.5]
        Grass is half effective to Fire and Grass, and double effective to Water [0.5, 2, 0.5]

        Best = Worst = O(1), as there are only assignments and arithmetic operations which are constant time
        """
        self.elements_names = element_names
        self.effectiveness_values = effectiveness_values

    @classmethod
    def get_effectiveness(cls, type1: Element, type2: Element) -> float:

        """
        Returns the effectivness of elem1 attacking elem2.
        O(e), where e is the number of elemental types in cls.instance.elements_names. which is not a constant as the number of elements can increase
        Thus when a for loop is running to loop through the element names and find the index of the element, it is O(e)
        Best case:  O(1) is when the element is the first element in the list
        Worst case: O(e) is when the element is the last element in the list

        Example: EffectivenessCalculator.get_effectiveness(Element.FIRE, Element.WATER) == 0.5
        """
        # loop through the elements names to find the index of the element1 using index function=
        index1 = cls.instance.elements_names.index(type1.name.title())

        # loop through the elements names to find the index of the element2 using index function
        index2 = cls.instance.elements_names.index(type2.name.title())

        # calculate the effectiveness by multiplying the index of element1 and the length of the elements names
        # and adding the index of element2 to get the effectiveness based on type_effectiveness.csv
        effective_index = index1 * len(cls.instance.elements_names) + index2
        effectiveness = cls.instance.effectiveness_values[effective_index]

        return effectiveness

    @classmethod
    def from_csv(cls, csv_file: str) -> EffectivenessCalculator:
        # NOTE: This is a terrible way to open csv files, if writing your own code use the `csv` module.
        # This is done this way to facilitate the second half of the task, the __init__ definition.
        with open(csv_file, "r") as file:
            header, rest = file.read().strip().split("\n", maxsplit=1)
            header = header.split(",")
            rest = rest.replace("\n", ",").split(",")
            a_header = ArrayR(len(header))
            a_all = ArrayR(len(rest))
            for i in range(len(header)):
                a_header[i] = header[i]
            for i in range(len(rest)):
                a_all[i] = float(rest[i])
            return EffectivenessCalculator(a_header, a_all)

    @classmethod
    def make_singleton(cls):
        cls.instance = EffectivenessCalculator.from_csv("type_effectiveness.csv")

EffectivenessCalculator.make_singleton()


if __name__ == "__main__":
    print(EffectivenessCalculator.get_effectiveness(Element.FIRE, Element.WATER))

