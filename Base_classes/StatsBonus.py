import json
from Base_classes.UnitType import UnitType

# from enum import Enum

# class UnitType(Enum):
#     inf = "INFANTRY"
#     lanc = "LANCERS"
#     mark = "MARKSMEN"

class _Basic_stat_dict():
    def __init__(self) -> None:
        self.attack  = None
        self.defense = None
        self.lethality = None
        self.health  = None
    
    def _from_dict(self, _dict):
        self.attack  = _dict["attack"]
        self.defense = _dict["defense"]
        self.lethality = _dict["lethality"]
        self.health  = _dict["health"]
        return self
    
    def _from_list(self, _list) :
        self.attack    = _list[0]
        self.defense   = _list[1]
        self.lethality = _list[2]
        self.health    = _list[3]
        return self
    
    def __str__(self) -> str:
        return json.dumps({
            "attack" : self.attack,
            "defense" : self.defense,
            "lethality" : self.lethality,
            "health" : self.health,
        }, indent= 2)

    def __repr__(self) -> str:
        return {
            "attack" : self.attack,
            "defense" : self.defense,
            "lethality" : self.lethality,
            "health" : self.health,
        }
    

class StatsBonus():
    def __init__(self) -> None:
        for ut in UnitType :
            self.__setattr__(ut.name, _Basic_stat_dict())
    
    def from_dict(self, _dict):
        for ut in UnitType :
            self.__setattr__(ut.name, _Basic_stat_dict()._from_dict(_dict[ut.name]))
        return self
    
    def from_list(self, _dict):
        for ut in UnitType :
            self.__setattr__(ut.name, _Basic_stat_dict()._from_list(_dict[ut.name]))
        return self

    def __str__(self) -> str:
        return json.dumps({ut.name: self.__getattribute__(ut.name).__repr__() for ut in UnitType}, indent= 4)

# fighter_1_stats = StatsBonus()

# _stats_1 = {
#     "attack" : 12,
#     "defense" : 13,
#     "lethality" : 14,
#     "health" : 15,
# }

# fighter_1_stats.inf._from_dict(_stats_1)

# print(fighter_1_stats)

# print(fighter_1_stats)
# fighter_1_stats.inf._from_dict(_stats_1)
# print(fighter_1_stats.inf.attack)
# fighter_1_stats.inf.attack = 99
# print(fighter_1_stats.inf)
# print(fighter_1_stats)
