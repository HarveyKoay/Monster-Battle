from data_structures.referential_array import ArrayR
from random_gen import RandomGen
from team import MonsterTeam

from ed_utils.decorators import number, visibility, advanced
from ed_utils.timeout import timeout
from random_gen import RandomGen

from battle import Battle
from elements import Element
from tower import BattleTower
from helpers import Flamikin, Faeboa, Aquariuma, Vineon, Normake, Thundrake, Rockodile

for element in Element:
    print(element.name)