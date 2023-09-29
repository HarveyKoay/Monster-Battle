from __future__ import annotations
from enum import auto
from typing import Optional

from base_enum import BaseEnum
from team import MonsterTeam
from data_structures.queue_adt import CircularQueue


class Battle:

    class Action(BaseEnum):
        ATTACK = auto()
        SWAP = auto()
        SPECIAL = auto()

    class Result(BaseEnum):
        TEAM1 = auto()
        TEAM2 = auto()
        DRAW = auto()

    def __init__(self, verbosity=0) -> None:
        """
        Initialise a battle instance.
        Best = Worst = O(1), as there are only assignments and arithmetic operations which are constant time
        """
        self.verbosity = verbosity

    def process_turn(self) -> Optional[Battle.Result]:
        """
        Process a single turn of the battle. Should:
        * process actions chosen by each team
        * level and evolve monsters
        * remove fainted monsters and retrieve new ones.
        * return the battle result if completed.
        
        e is the elements in the list of elements
        n is the size or number of monsters in the team

        Best case: O(e^2) where either one of the monsters attack and the other one swaps
        Worst case: O(n + e^2) where either one of the monsters attack and the other performs a special action

        Both best case scenario is provided where none of the monsters die and thus no retrieving of monsters are performed
        And the best case scenario is taking the worst case of attack which is O(e^2)
        """
        
        # Process the actions chosen by each team
        action1 = self.team1.choose_action(self.out1, self.out2)
        action2 = self.team2.choose_action(self.out2, self.out1)

        # Handle SWAP and SPECIAL actions
        if action1 in (Battle.Action.SWAP, Battle.Action.SPECIAL):
            # when swap is called 
            if action1 == Battle.Action.SWAP:
                # add the out monster to the team
                self.team1.add_to_team(self.out1)
                #  retrieve a new monster
                new_monster = self.team1.retrieve_from_team()
                self.out1 = new_monster
            # when spcial is called, ,, and 
            elif action1 == Battle.Action.SPECIAL:
                # add the out monster to the team
                self.team1.add_to_team(self.out1)
                # perform the special action
                self.team1.special()
                # retrieve a new monster
                new_monster = self.team1.retrieve_from_team()
                self.out1 = new_monster
        if action2 in (Battle.Action.SWAP, Battle.Action.SPECIAL):
            if action2 == Battle.Action.SWAP:
                self.team2.add_to_team(self.out2)
                new_monster = self.team2.retrieve_from_team()
                self.out2 = new_monster
            elif action2 == Battle.Action.SPECIAL:
                self.team2.add_to_team(self.out1)
                self.team2.special()
                new_monster = self.team2.retrieve_from_team()
                self.out2 = new_monster


        # Attack logic in the case of both monsters attacking
        if action1 == Battle.Action.ATTACK and action2 == Battle.Action.ATTACK:
            # if out1 is faster than out2
            if self.out1.get_speed() > self.out2.get_speed():
                # out1 attacks
                self.out1.attack(self.out2)
                # check if out2 is still alive
                if self.out2.get_hp() > 0:
                    self.out2.attack(self.out1)
            # if out2 is faster than out1
            elif self.out2.get_speed() > self.out1.get_speed():
                self.out2.attack(self.out1)
                if self.out1.get_hp() > 0:
                    self.out1.attack(self.out2)
            # if both out1 and out2 have the same speed
            else:
                self.out1.attack(self.out2)
                self.out2.attack(self.out1)

        # Attack logic in the case of one monster attacking
        elif action1 == Battle.Action.ATTACK:
            self.out1.attack(self.out2)
        elif action2 == Battle.Action.ATTACK:
            self.out2.attack(self.out1)
        
        # if both alive then minus one hp for both monsters
        if self.out1.get_hp() > 0 and self.out2.get_hp() > 0:
            self.out1.set_hp(self.out1.get_hp() -1)
            self.out2.set_hp(self.out2.get_hp() -1)

        # if either one of the monsters die
        # In this case if monster 2 die
        if self.out1.get_hp() > 0 and self.out2.get_hp() <= 0:
            # monster 1 level up and evolve
            self.out1.level_up()
            if self.out1.ready_to_evolve():
                self.out1 = self.out1.evolve()
            # if there are still monsters in team 2, retrieve a new monster
            if len(self.team2) > 0:
                self.out2 = self.team2.retrieve_from_team()

        elif self.out2.get_hp() > 0 and self.out1.get_hp() <= 0:
            self.out2.level_up()
            if self.out2.ready_to_evolve():
                self.out2 = self.out2.evolve() 
            if len(self.team1) > 0:
                self.out1 = self.team1.retrieve_from_team()
        
        # if both monsters die
        elif self.out2.get_hp() <= 0 and self.out1.get_hp() <= 0:
            # a new monster is retrieved from both teams if there are still monsters in the team
            if len(self.team1) > 0:
                self.out1 = self.team1.retrieve_from_team()
            if len(self.team2) > 0:
                self.out2 = self.team2.retrieve_from_team()

        # Check if there are any monsters left in either team
        # Also check if the out monsters are dead
        # return the respective output
        if len(self.team1) == 0 and self.out1.get_hp() <= 0 and len(self.team2) == 0 and self.out2.get_hp() <= 0:
            return Battle.Result.DRAW
        # Check if there any monsters left in team 1 and if the out monster is dead
        elif len(self.team1) == 0 and self.out1.get_hp() <= 0:
            return Battle.Result.TEAM2
        # Check if there any monsters left in team 2 and if the out monster is dead
        elif len(self.team2) == 0 and self.out2.get_hp() <= 0:
            return Battle.Result.TEAM1

        #return none if the battle is not completed
        return None
        

    def battle(self, team1: MonsterTeam, team2: MonsterTeam) -> Battle.Result:
        """
        Run a battle between two teams.
        e is the elements in the list of elements
        k is how long the battle lasts for
        n is the size or number of monsters in the team

        Best = O(e^2) where the battle is completed in one turn where either out1 or out2 dies in the first round
        Worst = O(k * (e^2 + n)) where the battle is completed in k turns where either out1 or out2 dies in the last round
        The worst case also includes where some monsters are swapped and perform special actions inbetween the battle

        """

        if self.verbosity > 0:
            print(f"Team 1: {team1} vs. Team 2: {team2}")
        # Add any pregame logic here.
        self.turn_number = 0
        self.team1 = team1
        self.team2 = team2
        self.out1 = team1.retrieve_from_team()
        self.out2 = team2.retrieve_from_team()
        result = None
        while result is None:
            result = self.process_turn()
        # Add any postgame logic here.
        return result

if __name__ == "__main__":
    t1 = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
    t2 = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
    b = Battle(verbosity=3)
    print(b.battle(t1, t2))

