import json
from Base_classes.Fight import Fight
from Base_classes.Fighter import Fighter
from Base_classes.StatsBonus import StatsBonus
from Base_classes.UnitType import UnitType

with open("assets/fighters.json", "r+") as f:
    data = json.load(f)

# ATTACKER DATA
attacker = Fighter()
attacker.stats = StatsBonus().from_list(data['daut'])
attacker.troops = {
    "infantry_t6" : 500,
    "lancers_t6" : 460,
    "marksmen_t6" : 300
}

# DEFENDER DATA
defender = Fighter()
defender.stats = StatsBonus().from_list(data['viper'])
defender.troops = {
    "infantry_t6" : 50,
    "lancers_t6" : 50,
    "marksmen_t6" : 50
}

# # BATTLE
f = Fight(attacker, defender)
f.battle()
f.print_skills_report()