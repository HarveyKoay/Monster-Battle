from __future__ import annotations
from enum import auto
from typing import Optional, TYPE_CHECKING

from base_enum import BaseEnum
from monster_base import MonsterBase
from random_gen import RandomGen
from helpers import get_all_monsters
from data_structures.stack_adt import ArrayStack
from data_structures.queue_adt import CircularQueue
from data_structures.sorted_list_adt import ListItem 
from data_structures.array_sorted_list import ArraySortedList
from data_structures.referential_array import ArrayR

if TYPE_CHECKING:
    from battle import Battle

class MonsterTeam:

    class TeamMode(BaseEnum): 

        FRONT = auto() #stack
        BACK = auto() # queue
        OPTIMISE = auto() #array sorted list

    class SelectionMode(BaseEnum):

        RANDOM = auto()
        MANUAL = auto()
        PROVIDED = auto()

    class SortMode(BaseEnum):

        HP = auto()
        ATTACK = auto()
        DEFENSE = auto()
        SPEED = auto()
        LEVEL = auto()

    TEAM_LIMIT = 6

    def __init__(self, team_mode: TeamMode, selection_mode, **kwargs) -> None:
        """
        initialiser for MonsterTeam
        Best case = Worst case = O(n) where n is the Team_limit which can be increased from recreating_team function
        As the rest are only assignments and arithmetic operations which are constant time
        """
        # Add any preinit logic here.
        self.team_mode = team_mode
        # creating team and original team based on teammode
        self.arr = self.recreate_team()
        self.original_team = self.recreate_team()

        # depending on sort key use lambda function to get the key
        self.sort_key = kwargs['sort_key'] if 'sort_key' in kwargs else None
        if self.sort_key == self.SortMode.HP:
            self.sort_key = lambda monster: monster.get_hp()
        elif self.sort_key == self.SortMode.ATTACK:
            self.sort_key = lambda monster: monster.get_attack()
        elif self.sort_key == self.SortMode.DEFENSE:
            self.sort_key = lambda monster: monster.get_defense()
        elif self.sort_key == self.SortMode.SPEED:
            self.sort_key = lambda monster: monster.get_speed()
        elif self.sort_key == self.SortMode.LEVEL:
            self.sort_key = lambda monster: monster.get_level()

        # depending on selection mode, call the respective function
        if selection_mode == self.SelectionMode.RANDOM:
            self.select_randomly(**kwargs)
        elif selection_mode == self.SelectionMode.MANUAL:
            self.select_manually(**kwargs)
        elif selection_mode == self.SelectionMode.PROVIDED:
            self.select_provided(**kwargs)
        else:
            raise ValueError(f"selection_mode {selection_mode} not supported.")
        
        
    def add_to_team(self, monster: MonsterBase):
        """
        Add a monster to the team.
        Best case = Worst case = O(1) as the push and push methods are O(1) for TeamMode.FRONT 
        Best case = Worst case = O(1) as the append and serve methods are O(1) for TeamMode.BACK
        
        TeamMode.OPTIMISE:
        n is the number of items in the list (self) because we assume that the team limit can be increased.
        Best case:  O(log n) as the add method is O(log n) where the list item is to be added to the back of the team
        Worst case: O(n) as the add method is O(n) where the list item is to be added to the front of the team
        """
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            self.arr.push(monster)
        elif self.team_mode == MonsterTeam.TeamMode.BACK:
            self.arr.append(monster)
        elif self.team_mode == MonsterTeam.TeamMode.OPTIMISE:
            # create list_item object
            list_item = ListItem(monster, self.sort_key(monster))
            # if the list is not empty and the key of first item is negative
            if not self.arr.is_empty() and self.arr[0].key < 0:
                # make the key of the new mmnster negative
                list_item.key *= -1
            self.arr.add(list_item)

    def retrieve_from_team(self) -> MonsterBase:
        """
        Retrieve a monster from the team.
        Best case = Worst case = O(1) as the pop and serve methods are O(1) for TeamMode.FRONT and TeamMode.BACK respectively.

        TeamMode.OPTIMISE:
        n is the number of items in the list (self) because we assume that the team limit can be increased.
        Best case = Worst case =  O(1) as the delete_at_index method is O(1) where the list item is to be deleted back of the team because it doesn't have to be shuffled
        """
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            return self.arr.pop()
        elif self.team_mode == MonsterTeam.TeamMode.BACK:
            return self.arr.serve()
        elif self.team_mode == MonsterTeam.TeamMode.OPTIMISE:
            # return the monster instead of list_item
            monster = self.arr.delete_at_index(len(self)-1)
            return monster.value

    def special(self) -> None:
        """
        For TeamMode.FRONT: 
        The first 3 monsters at the front are reversed (Up to the current capacity of the team)
        Best case = Worst case = O(n)  where n is the number of items in the list (self) because we assume that the team limit can be increased.
        This is because Circular queue based on TEAM_LIMIT is created

        For TeamMode.BACK:
        The first half of the team is swapped with the second half (in an odd team size, the middle monster is in the bottom half), 
        The original second half of the team is reversed.
        Best case = Worst case = O(n)  where n is the number of items in the list (self) because we assume that the team limit can be increased.
        This is because Circular queue and Array Stack based on TEAM_LIMIT is created
    

        For TeamMode.OPTIMISE:
        The original ascending list is changed to descending order based on the sort key
        Best case = Worst case = O(n)  where n is the number of items in the list (self) because we assume that the team limit can be increased.
        This is because Array Sorted List based on TEAM_LIMIT is created
        delete_at_index is still O(1) because no shuffling when deleted from the back of the list
        """
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            # create temperory queue to store the first 3 or less monsters
            temp_queue = CircularQueue(MonsterTeam.TEAM_LIMIT)
            # ensure it is 3 or less
            e_team_size = min(len(self), 3)
            while e_team_size > 0:
                monster = self.arr.pop()
                temp_queue.append(monster)
                e_team_size -=1
            # retrieving the monster for queue where the order is reversed 
            for _ in range(len(temp_queue)):
                # store it back to team
                monster = temp_queue.serve()
                self.arr.push(monster)

                
        elif self.team_mode == MonsterTeam.TeamMode.BACK:
            # create temperory stack and queue to store monsters
            temp_stack = ArrayStack(MonsterTeam.TEAM_LIMIT)
            temp_queue = CircularQueue(MonsterTeam.TEAM_LIMIT)
            # make sure the size is half of the team size where if length of team is odd the centre will be included as the back half
            e_team_size = len(self)//2
            # take first half and store it into queue to remain order
            while e_team_size > 0:
                monster = self.arr.serve()
                temp_queue.append(monster)
                e_team_size -=1
            # next half is stored in stack to reverse the order
            for _ in range(len(self)):
                monster = self.arr.serve()
                temp_stack.push(monster)
            # retrieving the monster from stack where the order is reversed
            for _ in range(len(temp_stack)):
                monster = temp_stack.pop()
                self.arr.append(monster)
            # retrieving the monster from queue where the order is the same
            for _ in range(len(temp_queue)):
                monster = temp_queue.serve()
                self.arr.append(monster)

        elif self.team_mode == MonsterTeam.TeamMode.OPTIMISE:
            # create temperory sorted list to store monsters
            temp_sorted_lst = ArraySortedList(MonsterTeam.TEAM_LIMIT)
            for _ in range(len(self)):
                list_item = self.arr.delete_at_index(len(self)-1)               
                # multiply the key by -1 to reverse the order which will not affect they actual stats                                    
                list_item.key *= -1
                # add it to temporary sorted list
                temp_sorted_lst.add(list_item)
            # retrieving the monster from sorted list where the order is reversed
            for _ in range(len(temp_sorted_lst)):
                list_item = temp_sorted_lst.delete_at_index(len(temp_sorted_lst)-1)
                # adding it back to self.team
                self.arr.add(list_item)

    def regenerate_team(self) -> None:
        """
        For TeamMode.FRONT: 
        The first 3 monsters at the front are reversed (Up to the current capacity of the team)
        Best case = Worst case = O(n)  where n is the number of items in the list (self) because we assume that the team limit can be increased.
        This is because Circular queue based on TEAM_LIMIT is created

        For TeamMode.BACK:
        The first half of the team is swapped with the second half (in an odd team size, the middle monster is in the bottom half), 
        The original second half of the team is reversed.
        Best case = Worst case = O(n)  where n is the number of items in the list (self) because we assume that the team limit can be increased.
        This is because Circular queue and Array Stack based on TEAM_LIMIT is created
    

        For TeamMode.OPTIMISE:
        The original ascending list is changed to descending order based on the sort key
        Best case = Worst case = O(n)  where n is the number of items in the list (self) because we assume that the team limit can be increased.
        This is because Array Sorted List based on TEAM_LIMIT is created
        delete_at_index is still O(1) because no shuffling when deleted from the back of the list
        """
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            # create temporary stack to store monsters
            temp_stack = ArrayStack(MonsterTeam.TEAM_LIMIT)
            new_stack = ArrayStack(MonsterTeam.TEAM_LIMIT)
            # loop based on original team size
            for _ in range(len(self.original_team)):
                # get the tyoe
                monster_class = type(self.original_team.pop())
                temp_stack.push(monster_class())

            for _ in range(len(temp_stack)):
                monster = temp_stack.pop()
                # store it back to new stack 
                new_stack.push(monster)
                # store it back to original team
                self.original_team.push(monster)

            # reference new stack to self.arr
            self.arr = new_stack
        
        elif self.team_mode == MonsterTeam.TeamMode.BACK:
            # create temporary queue to store monsters
            temp_queue = CircularQueue(MonsterTeam.TEAM_LIMIT)
            new_queue = CircularQueue(MonsterTeam.TEAM_LIMIT)
            for _ in range(len(self.original_team)):
                monster_class = type(self.original_team.serve())
                temp_queue.append(monster_class())
                new_queue.append(monster_class())
            
            for _ in range(len(temp_queue)):
                monster = temp_queue.serve()
                self.original_team.append(monster)

            self.arr = new_queue
        
        elif self.team_mode == MonsterTeam.TeamMode.OPTIMISE:
            # create temporary sorted list to store monsters
            temp_sorted_lst = ArraySortedList(MonsterTeam.TEAM_LIMIT)
            new_sorted_lst = ArraySortedList(MonsterTeam.TEAM_LIMIT)
            for _ in range(len(self.original_team)):
                monster_class = type((self.original_team.delete_at_index(len(self.original_team) -1)).value)
                list_item = ListItem(monster_class(), self.sort_key(monster_class()))
                new_sorted_lst.add(list_item)
                temp_sorted_lst.add(list_item)
            
            for _ in range(len(temp_sorted_lst)):
                monster = temp_sorted_lst.delete_at_index(len(temp_sorted_lst) -1)
                self.original_team.add(monster)
            
            self.arr = new_sorted_lst

    def select_randomly(self, sort_key=None):
        """
        Generate a team randomly.
        The team size should be between 1 and TEAM_LIMIT (inclusive).
        The monsters should be selected from the list of all monsters that can be spawned.
        Note:
        For my assumption, i assume that for the best case, it is possible for me to Generate 1 for team size as it is random and it finds the spawnable monster first try.
        n is the size of the team but it can be increased thus it is not constant
        m is the total amount of monster which also can be increased thus it is not a constant
        k is the complexity of get_all_monsters()
        
        TeamMode.FRONT and TeamMode.BACK:
        Best case:  O(k) as the random generates 1 for team size and it finds the spawnable monster first try
        Worst case: O(k + n * m) where the team size chosen is the maximum the spawnable monster is the last monster in the list
        where O(k + n + m*n) is simplified to O(k + n * m)

        TeamMode.OPTIMISE:
        Best case:  O(k) as the random generates 1 for team size and it finds the spawnable monster first try
        Worst case: O(k * n^2 * m) where the loop run for the range of team size, where within the loop,
        The for loop runs for the range of all monsters. Then, add to team for optimise will be O(n) when the monster is added to the front of the list.
        """
        # Randomly generate team in between 1, and maximum team limit
        team_size = RandomGen.randint(1, self.TEAM_LIMIT)
        # Get all monsters
        monsters = get_all_monsters()
        n_spawnable = 0

        # Count the number of spawnable monsters
        for x in range(len(monsters)):
            if monsters[x].can_be_spawned():
                n_spawnable += 1

        # For each monster in the team, randomly select a monster from the list of spawnable monsters
        for _ in range(team_size):
            # Randomly select a monster
            spawner_index = RandomGen.randint(0, n_spawnable-1)
            cur_index = -1
            for x in range(len(monsters)):
                if monsters[x].can_be_spawned():
                    cur_index += 1
                    if cur_index == spawner_index:
                        # add the monster to team and original team
                        self.add_to_team(monsters[x]())
                        self.add_to_original_team(monsters[x]())

                        break
            else:
                raise ValueError("Spawning logic failed.")
    

    def select_manually(self, sort_key=None):
        """
        Prompt the user for input on selecting the team.
        Any invalid input should have the code prompt the user again.

        First input: Team size. Single integer
        For _ in range(team size):
            Next input: Prompt selection of a Monster class.
                * Should take a single input, asking for an integer.
                    This integer corresponds to an index (1-indexed) of the helpers method
                    get_all_monsters()
                * If invalid of monster is not spawnable, should ask again.

        Add these monsters to the team in the same order input was provided. Example interaction:

        
        This monster cannot be spawned.
        Which monster are you spawning? 1

        For my assumption, i assume that for the best case, it is possible for me to generate 1 for team size as it is random and it finds the spawnable monster first try.
        n is the size of the team but it can be increased thus it is not constant
        m is the total amount of monster which also can be increased thus it is not a constant
        k is the complexity of get_all_monsters()
        
        TeamMode.FRONT and TeamMode.BACK:
        Best case:  O(k) as the random generates 1 for team size and it finds the spawnable monster first try
        Worst case: O(k + n * m) where the team size chosen is the maximum the spawnable monster is the last monster in the list
        where O(k + n + m*n) is simplified to O(k + n * m)

        TeamMode.OPTIMISE:
        Best case:  O(k) as the random generates 1 for team size and it finds the spawnable monster first try
        Worst case: O(k * n^2 * m) where the loop run for the range of team size, where within the loop,
        The for loop runs for the range of all monsters. Then, add to team for optimise will be O(n) when the monster is added to the front of the list.
        """
        bool = False
        monsters = get_all_monsters()
        while bool == False: 
            # prompt user to input team size
            total_monsters = int(input("How many monsters are there? \n"))
            # ensure user only inputs team size between 1 and team limit
            if total_monsters <= MonsterTeam.TEAM_LIMIT and total_monsters >= 1:
                bool = True
            else:
                print(f"Invalid input. Please choose a team size between 1 and {MonsterTeam.TEAM_LIMIT}")
        # when team size is valid, prompt user to input monster index
        while total_monsters > 0:
            monster_index = int(input(""" 
        # MONSTERS Are:
        # 1: Flamikin [✔️]
        # 2: Infernoth [❌]
        # 3: Infernox [❌]
        # 4: Aquariuma [✔️]
        # 5: Marititan [❌]
        # 6: Leviatitan [❌]
        # 7: Vineon [✔️]
        # 8: Treetower [❌]
        # 9: Treemendous [❌]
        # 10: Rockodile [✔️]
        # 11: Stonemountain [❌]
        # 12: Gustwing [✔️]
        # 13: Stormeagle [❌]
        # 14: Frostbite [✔️]
        # 15: Blizzarus [❌]
        # 16: Thundrake [✔️]
        # 17: Thunderdrake [❌]
        # 18: Shadowcat [✔️]
        # 19: Nightpanther [❌]
        # 20: Mystifly [✔️]
        # 21: Telekite [❌]
        # 22: Metalhorn [✔️]
        # 23: Ironclad [❌]
        # 24: Normake [❌]
        # 25: Strikeon [✔️]
        # 26: Venomcoil [✔️]
        # 27: Pythondra [✔️]
        # 28: Constriclaw [✔️]
        # 29: Shockserpent [✔️]
        # 30: Driftsnake [✔️]
        # 31: Aquanake [✔️]
        # 32: Flameserpent [✔️]
        # 33: Leafadder [✔️]
        # 34: Iceviper [✔️]
        # 35: Rockpython [✔️]
        # 36: Soundcobra [✔️]
        # 37: Psychosnake [✔️]
        # 38: Groundviper [✔️]
        # 39: Faeboa [✔️]
        # 40: Bugrattler [✔️]
        # 41: Darkadder [✔️]
        # Which monster are you spawning?\n""" ))
            for x in range(len(monsters)):
                #  ensure user only choose monster which can be spawned
                if x == monster_index -1 and monsters[x].can_be_spawned():
                    # add these monsters to team and original team
                    self.add_to_team(monsters[x]())
                    self.add_to_original_team(monsters[x]())
                    total_monsters -= 1
                    break


    def select_provided(self, provided_monsters:Optional[ArrayR[type[MonsterBase]]]=None, sort_key = None):
        """
        Generates a team based on a list of already provided monster classes.

        While the type hint imples the argument can be none, this method should never be called without the list.
        Monsters should be added to the team in the same order as the provided array.

        Example input:
        [Flamikin, Aquariuma, Gustwing] <- These are all classes.

        Example team if in TeamMode.FRONT:
        [Gustwing Instance, Aquariuma Instance, Flamikin Instance]
        

        For my assumption, i assume that for the best case, it is possible for me to generate 1 for team size as it is random and it finds the spawnable monster first try.
        n is the number of provided monsters and the size of team
        
        TeamMode.FRONT and TeamMode.BACK:
        Best case:  O(1) where provided monsters are more than 6 
        Worst case: O(n) as we assume the team size can increase. 

        TeamMode.OPTIMISE:
        Best case:  O(1) where provided monsters are more than 6
        Worst case: O(n^2) where the loop run for the range of team size, where within the loop,
        All the provided monsters are added to the front of the list.
        """
        # if len of provided monsters are more than team limit raise value error
        if len(provided_monsters) > MonsterTeam.TEAM_LIMIT:
            raise ValueError("Too many monsters")
        
        for i in range(len(provided_monsters)):       
            if not provided_monsters[i].can_be_spawned():
                raise ValueError("This monster cannot be spawned.")
            else:
                # add monsters to team and original team if it can be spawned
                self.add_to_team(provided_monsters[i]())
                self.add_to_original_team(provided_monsters[i]())



    def choose_action(self, currently_out: MonsterBase, enemy: MonsterBase) -> Battle.Action:
        """
        Choose an action for the currently out monster.
        If the currently out monster is faster than the enemy, or has more HP than the enemy, it should attack.
        Best case = Worst case = O(1) as it is just returning a value
        """
        # This is just a placeholder function that doesn't matter much for testing.

        from battle import Battle
        if currently_out.get_speed() >= enemy.get_speed() or currently_out.get_hp() >= enemy.get_hp():
            return Battle.Action.ATTACK
        return Battle.Action.SWAP

    def recreate_team(self) -> ArrayR:
        """
        Create the team based on the team mode.
        Best case = Worst case = O(n) where n is the Team_limit which can be increased
        """
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            return ArrayStack(MonsterTeam.TEAM_LIMIT)
        elif self.team_mode == MonsterTeam.TeamMode.BACK:
            return CircularQueue(MonsterTeam.TEAM_LIMIT)
        elif self.team_mode == MonsterTeam.TeamMode.OPTIMISE:
            return ArraySortedList(MonsterTeam.TEAM_LIMIT)
        else:
            raise ValueError("Invalid team mode")
    
    def add_to_original_team(self, monster):
        """
        Add a monster to the team.
        Best case = Worst case = O(1) as the push and push methods are O(1) for TeamMode.FRONT 
        Best case = Worst case = O(1) as the append and serve methods are O(1) for TeamMode.BACK
        
        TeamMode.OPTIMISE:
        n is the number of items in the list (self) because we assume that the team limit can be increased.
        Best case:  O(log n) as the add method is O(log n) where the list item is to be added to the back of the team
        Worst case: O(n) as the add method is O(n) where the list item is to be added to the front of the team
        """
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            self.original_team.push(monster)
        if self.team_mode == MonsterTeam.TeamMode.BACK:
            self.original_team.append(monster)
        if self.team_mode == MonsterTeam.TeamMode.OPTIMISE:
            list_item = ListItem(monster, self.sort_key(monster))     
            self.original_team.add(list_item)

    
    def __str__(self):
        """
        printing the team
        For TeamMode.FRONT: 
        Best case = Worst case = O(n)  where n is the number of items in the list (self) because we assume that the team limit can be increased.
        This is because Circular queue based on TEAM_LIMIT is created

        For TeamMode.BACK:
        The first half of the team is swapped with the second half (in an odd team size, the middle monster is in the bottom half), 
        Best case = Worst case = O(n)  where n is the number of items in the list (self) because we assume that the team limit can be increased.
        This is because Circular queue and Array Stack based on TEAM_LIMIT is created
    

        For TeamMode.OPTIMISE:
        Best case = Worst case = O(n)  where n is the number of items in the list (self) because we assume that the team limit can be increased.
        This is because Array Sorted List based on TEAM_LIMIT is created
        delete_at_index is still O(1) because no shuffling when deleted from the back of the list
        """
        str = ""
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            temp_stack = ArrayStack(MonsterTeam.TEAM_LIMIT)
            while not self.arr.is_empty():
                monster = self.arr.pop()
                temp_stack.push(monster)
                print(monster)
        
            while not temp_stack.is_empty():
                monster = temp_stack.pop()
                self.arr.push(monster)

        elif self.team_mode == MonsterTeam.TeamMode.BACK:
            temp_queue = CircularQueue(MonsterTeam.TEAM_LIMIT)
            while not self.arr.is_empty():
                monster = self.arr.serve()
                temp_queue.append(monster)
                print(monster)
        
            while not temp_queue.is_empty():
                monster = temp_queue.serve()
                self.arr.append(monster)

        elif self.team_mode == MonsterTeam.TeamMode.OPTIMISE:
            temp_array = ArraySortedList(MonsterTeam.TEAM_LIMIT)
            while not self.arr.is_empty():
                list_item = self.arr.delete_at_index(len(self) - 1)
                temp_array.add(list_item)
                # Get the actual monster instance from the ListItem
                monster = list_item.value 
                print(monster)

            while not temp_array.is_empty():
                list_item = temp_array.delete_at_index(len(temp_array) - 1)
                self.arr.add(list_item)
    
        return str

    
    def __len__(self):
        """
        return the length of the team
        Best case = Worst case = O(1) as it is just returning a value
        """
        return len(self.arr)
    
if __name__ == "__main__":
    team = MonsterTeam(
        team_mode=MonsterTeam.TeamMode.OPTIMISE,
        selection_mode=MonsterTeam.SelectionMode.RANDOM,
        sort_key=MonsterTeam.SortMode.HP,
    )
    print(team)
    while len(team):
        print(team.retrieve_from_team())

