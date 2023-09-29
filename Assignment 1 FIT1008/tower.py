from __future__ import annotations
from random_gen import RandomGen
from team import MonsterTeam
from battle import Battle
from data_structures.bset import BSet
from data_structures.queue_adt import CircularQueue
from data_structures.stack_adt import ArrayStack
from data_structures.sorted_list_adt import ListItem

from elements import Element

from data_structures.referential_array import ArrayR

class BattleTower:

    MIN_LIVES = 2
    MAX_LIVES = 10
    
    def __init__(self, battle: Battle | None = None) -> None:
        """
        Initialise a battle tower instance.
        Best = Worst = O(1), as there are only assignments and arithmetic operations which are constant time
        """
        self.battle = battle or Battle(verbosity=0)
        self.player_lives = 0
        self.current_enemy = 0
        self.tower_elements = BSet()
    
    def place_element(self, queue, team, elements_bset) -> None:
        """
        Put the elements of the team into the elements_bset
        e is the elements in the list of elements
        n is the size or number of monsters in the team

        Best case: O(1) where there is only one monster in the team and the element is the first element in the Element enum
        As the rest of the assignments and arithmetic operations are constant time
        Worst case: O(e * n) where there are n monsters in the team and the element is the last element in the Element enum
        """
        # for all the monsters in the team
        for _ in range(len(team)): 
            #retrieve the monster
            monster = team.retrieve_from_team()
            queue.append(monster)
            # get the element of the monster
            monster_element = monster.get_element().upper()
            for element in Element:
                if monster_element == element.name:
                    value = element.value
                    # add the element to the elements_bset
                    elements_bset.add(value)

        # add the monsters back to the team
        for _ in range(len(queue)):
            monster = queue.serve()
            team.add_to_team(monster)


    def set_my_team(self, team: MonsterTeam) -> None:
        """
        Set the player's team.
        e is the elements in the list of elements
        n is the size or number of monsters in the team

        Best = Worst = O(e * n) where we take the worst case scenario from place_element which is O(e * n)
        """
        # Generate the team lives here too.
        self.my_team = team
        self.player_lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES)
        # Place the elements of the original team into self.original_elements
        self.original_elements = BSet()
        original_queue = CircularQueue(len(self.my_team))
        self.place_element(original_queue, self.my_team, self.original_elements)

    def generate_teams(self, n: int) -> None:
        """
        Generate n enemy teams.
        p is the number of enemy teams to generate
        n is the size of the team but it can be increased thus it is not constant
        m is the total amount of monster which also can be increased thus it is not a constant
        k is the complexity of get_all_monsters()

        Best case:  O(p + (k + n * m)) where n is the number of enemy teams to generate
        p is from the instantiation of CircularQueue where the the number of enemy teams can be any number
        Worst case: O(p * (k + n * m)) where n is the number of enemy teams to generate
        Other than p, the rest of the complexity is from 
        Those are all from MonsterTeam.SelectionMode.Random where it is O(k + n * m) accounting the worst case scenario
        """
        # Create a queue to store the enemy teams
        self.enemy_teams = CircularQueue(n)
        for _ in range(n):
            # Generate a random enemy team which TeamMode.Back
            enemy_team = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
            enemy_lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES)
            # Use the queue to store the enemy team and the enemy lives using List Item
            list_item = ListItem(enemy_team, enemy_lives)
            self.enemy_teams.append(list_item)
        

        
    def battles_remaining(self) -> bool:
        """
        Check if there are any battles remaining or if there is any more enemy teams remaining in the tower
        n is the size of enemy teams but it can be increased thus it is not constant
        p is the number of enemy teams to generate

        Best case: O(1) where the player lives == 0 and False is return immediately
        Worst case: O(n + p) where n is from the instantiation of CircularQueue
        p is from the loop of self.enemy_teams
        """
        # Check if player still has lives
        if self.player_lives == 0:
            return False
        else:
            # Check if there are any enemy teams left
            all_dead = len(self.enemy_teams)
            death_total = 0
            # Create a queue to temporarily store the enemy teams
            queue = CircularQueue(MonsterTeam.TEAM_LIMIT)
            for _ in range(len(self.enemy_teams)):
                # Check if the enemy team still has lives
                list_item = self.enemy_teams.serve()
                if list_item.key <= 0:
                    # if the enemy team has no lives, add 1 to death_total
                    death_total +=1
                else:
                    queue.append(list_item)

            for _ in range(len(queue)):
                list_item = queue.serve()
                self.enemy_teams.append(list_item)

            # Check if all enemy teams have no lives
            return death_total != all_dead
    
    def next_battle(self) -> tuple[Battle.Result, MonsterTeam, MonsterTeam, int, int]: 
        """
        Process the next battle.
        e is the elements in the list of elements
        k is how long the battle lasts for
        n is the size or number of monsters in the team

        Best = Worst = O(k * (e^2 + n)) where k is the number of turns the battle lasts for
        This is because the initial big O which is O(k * (e^2 + n) + n + n + n + e * n ) is shortened to O(k * (e^2 + n))
        where the other terms are not as significant and thus can be ignored as they also share the same n value
        """
        if self.battles_remaining():
            list_item = self.enemy_teams.serve()
            # Set both teams to battle
            battle_result = self.battle.battle(self.my_team, list_item.value)
            
            # Regenerate the teams
            self.my_team.regenerate_team()
            list_item.value.regenerate_team()

            # Check the battle result and subtract the lives of teams accordingly
            if battle_result == Battle.Result.TEAM1:
                list_item.key -= 1
            elif battle_result == Battle.Result.TEAM2:
                self.player_lives -= 1
            elif battle_result == Battle.Result.DRAW:
                self.player_lives -=1
                list_item.key -=1

            self.enemy_teams.append(list_item)

            # Check if all the enemies have already been fought and reset the current enemy to 0
            if self.current_enemy == len(self.enemy_teams):
                # All enemy teams have been fought, then clear the tower elements
                self.tower_elements = BSet()
                self.current_enemy = 0

            # current enemy is the index of the enemy team that is currently being fought
            self.current_enemy += 1

            # Place the elements of the enemy team into self.enemy_elements
            self.enemy_elements = BSet()
            next_queue = CircularQueue(len(list_item.value))
            self.place_element(next_queue, list_item.value, self.enemy_elements)
            # Add the elements of the enemy team to the tower elements
            self.tower_elements = self.tower_elements.union(self.enemy_elements)

            return (battle_result, self.my_team, list_item.value, self.player_lives, list_item.key)
    
    def out_of_meta(self) -> ArrayR[Element]:
        """
        Return the elements that are out of meta which basically means they are in the tower
        but are not in the player's team or the next enemy team
        e is the elements in the list of elements
        n is the size or number of monsters in the team

        Best case: O(n) when there are no elements in the tower due to no battle has been fought where n is from the instantiation of queue
        with the size of the enemy team with MonsterTeam.TEAM_LIMIT
        Worst case: O(n + e) where e is the number of elements in the list of elements and the element in out of meta loop through all the elements
        to find the element of monster in the tower
        """
        # Check the element of the next enemy team and add it to the next_elements
        list_item = self.enemy_teams.peek()
        self.next_elements = BSet()
        next_queue = CircularQueue(len(list_item.value))
        self.place_element(next_queue, list_item.value, self.next_elements)

        # Check the elements which are in meta by getting the union of the original elements and the next elements
        in_meta = self.original_elements.union(self.next_elements)
        # Check the elements which are out of meta by getting the difference of the tower elements and the elements in meta
        out_of_meta = self.tower_elements.difference(in_meta)
        # Create an array to store the elements which are out of meta
        final_elements = ArrayR(len(out_of_meta))
        index = 0
        for element in Element:
            if element.value in out_of_meta:
                # if the index is in the out of meta, add the element to the final_elements
                final_elements[index] = element
                index += 1
            
        return final_elements


    def sort_by_lives(self):
    #     # 1054 ONLY
        str = ''


def tournament_balanced(tournament_array: ArrayR[str]):
    #     # 1054 ONLY
    str = ''

if __name__ == "__main__":

    RandomGen.set_seed(129371)

    bt = BattleTower(Battle(verbosity=3))
    bt.set_my_team(MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM))
    bt.generate_teams(3)

    for result, my_team, tower_team, player_lives, tower_lives in bt.next_battle():
        print(result, my_team, tower_team, player_lives, tower_lives)

