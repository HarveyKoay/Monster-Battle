from __future__ import annotations
import abc
from elements import Element, EffectivenessCalculator
from math import ceil

class MonsterBase(abc.ABC):
    """
    Unless Stated otherwise all Complexity is O(1) 
    """

    def __init__(self, simple_mode=True, level:int=1) -> None:
        """
        Initialise an instance of a monster.

        :simple_mode: Whether to use the simple or complex stats of this monster
        :level: The starting level of this monster. Defaults to 1.
        """
        self.simple_mode = simple_mode
        self.level = level
        self.original_level = level
        self.current_hp = self.get_max_hp()


    def get_level(self):
        """The current level of this monster instance"""
        return self.level

    def level_up(self):
        """Increase the level of this monster instance by 1"""
        # remain the original difference of health and max health
        difference = self.get_max_hp() - self.get_hp()
        self.level += 1
        self.set_hp(self.get_max_hp() - difference)


    def get_hp(self):
        """Get the current HP of this monster instance"""
        return self.current_hp

    def set_hp(self, val):
        """Set the current HP of this monster instance"""
        self.current_hp = val

    def get_attack(self):
        """Get the attack of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_attack()
        else:
            return self.get_complex_stats().get_attack()

    def get_defense(self):
        """Get the defense of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_defense()
        else:
            return self.get_complex_stats().get_defense()

    def get_speed(self):
        """Get the speed of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_speed()
        else:
            return self.get_complex_stats().get_speed()
        
    def get_max_hp(self):
        """Get the maximum HP of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_max_hp()
        else:
            return self.get_complex_stats().get_max_hp()

    def alive(self) -> bool:
        """Whether the current monster instance is alive (HP > 0 )"""
        if self.hp > 0:
            return True

        return False

    def attack(self, other: MonsterBase):
        """
        Attack another monster instance
        e is the number of elemental types in cls.instance.elements_names. in the get_effectiveness method
        e is also the number of elements in the list of elements
        It is not a constant as the number of elements can increase
        All other get_ methods are O(1) as they are just returning a value

        Thus when a for loop is running to loop through the element names and find the index of the element, it is O(e)
        Best case:  O(1) is when the element is the first element in the element_names list and first element in the Element enum
        Worst case: O(e^2) is when the element is the last element in the list as the from_string method is also O(e)

        """

        dmg = 0
        # Step 1: Compute attack stat vs. defense stat
        if other.get_defense() < (self.get_attack())/2:
            dmg = self.get_attack() - other.get_defense()
        elif other.get_defense() < self.get_attack():
            dmg = self.get_attack() * 5 / 8 - other.get_defense()/4
        else:
            dmg = self.get_attack()/4
        # Step 2 & 3: Apply type effectiveness and ceil to int
        effectiveness = EffectivenessCalculator.get_effectiveness(Element.from_string(self.get_element()), Element.from_string(other.get_element()))
        total_dmg = int(ceil(dmg * effectiveness))
        # Step 4: Lose HP
        other.set_hp(other.get_hp() - total_dmg)
        

    def ready_to_evolve(self) -> bool:
        """Whether this monster is ready to evolve. See assignment spec for specific logic."""
        # if the level increased and get_evolutions is not None
        if self.level != self.original_level and self.get_evolution() != None:
            # set the original level into the new level
            self.original_level == self.level
            return True
        
        return False

    def evolve(self) -> MonsterBase:
        """Evolve this monster instance by returning a new instance of a monster class."""
        # if the monster is ready to evolve
        if self.ready_to_evolve() == True:
            # get the class of evolution of monster and instantiate it
            new_class = self.get_evolution()
            new_monster = new_class(simple_mode=self.simple_mode, level= self.level)
            # remain the original difference of health and max health
            difference = self.get_max_hp()- self.get_hp()
            new_monster.set_hp(new_monster.get_max_hp()- difference)

            return new_monster
        
    def __str__(self) -> str:
        """Returns a string when str(obj is called)"""
        return f"LV.{self.level} {self.get_name()}, {self.get_hp()}/{self.get_max_hp()} HP"
    ### NOTE
    # Below is provided by the factory - classmethods
    # You do not need to implement them
    # And you can assume they have implementations in the above methods.

    @classmethod
    @abc.abstractmethod
    def get_name(cls) -> str:
        """Returns the name of the Monster - Same for all monsters of the same type."""
        pass

    @classmethod
    @abc.abstractmethod
    def get_description(cls) -> str:
        """Returns the description of the Monster - Same for all monsters of the same type."""
        pass

    @classmethod
    @abc.abstractmethod
    def get_evolution(cls) -> type[MonsterBase]:
        """
        Returns the class of the evolution of the Monster, if it exists.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_element(cls) -> str:
        """
        Returns the element of the Monster.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def can_be_spawned(cls) -> bool:
        """
        Returns whether this monster type can be spawned on a team.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_simple_stats(cls) -> Stats:
        """
        Returns the simple stats class for this monster, if it exists.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_complex_stats(cls) -> Stats:
        """
        Returns the complex stats class for this monster, if it exists.
        Same for all monsters of the same type.
        """
        pass

