import json
from Base_classes.Fight import Fight
from Base_classes.Fighter import Fighter
from Base_classes.StatsBonus import StatsBonus
from Base_classes.UnitType import UnitType

with open("assets/fighters.json", "r+") as f:
    data = json.load(f)


# ATTACKER DATA
attacker = Fighter("daut2")
attacker.stats = StatsBonus().from_list(data[attacker.name])
attacker.troops = {
    "infantry_t7" : 1000,
    "lancer_t7" : 10,
    "marksman_t7_fc1" : 200
}

# DEFENDER DATA
defender = Fighter("viper2")
defender.stats = StatsBonus().from_list(data[defender.name])
defender.troops = {
    "infantry_t7" : 100, 
    "lancer_t7" : 0,
    "marksman_t7" : 30
}

# # BATTLE

f = Fight(attacker, defender)
f.battle(show_rounds_freq = 10)
f.print_skills_report()
