import json
from Base_classes.Fight import Fight
from Base_classes.Fighter import Fighter
from Base_classes.StatsBonus import StatsBonus
from Base_classes.BattleRound import BattleRound
from Base_classes.UnitType import UnitType
from Base_classes.JsonUtil import JsonUtil

###############################################
# LOAD FIGHTERS DATA
###############################################

JsonUtil.load_fighters_data(
    fighters_stats_path = "fighters_data/fighters_stats.json",      # File containing the fighters stats
    fighters_heroes_path = "fighters_data/fighters_heroes.json"     # File containing the fighters heroes stats
)


###############################################
# ATTACKER DATA
###############################################

attacker_name = "Nitro"
attacker = Fighter(attacker_name)

# attacker.heroes = ["Sergey"]  #["Jessie", "Sergey", "Molly"]      # if this format is used, skill levels are fetched at 'fighter_heroes.json'; Level 5 if not found

### OR you can specify skill levels by using:
# attacker.heroes = {
#     "Jessie" : {
#         "skill_1_level": 2,
#         "skill_2_level": 2,
#     }
# }

attacker.troops = {
    "infantry_t10_fc5" : 50000,
    "lancer_t10_fc5" : 0,
    "marksman_t10_fc5" : 0
}

### Add heroes stats. # If this is used, hero stats are added. All heroes stats should be specified in 'fighters_heroes.json'
### Use only if heroes stats are not included in fighters_data/fighter_stats.json
# attacker.add_heroes_stats()           


# attacker.joiner_heroes = ['Jessie', 'Jasser', 'mOLLY', "mia"]   ## If this form is used, all joiners first skill are considered at level 5

###############################################
# DEFENDER DATA
###############################################

defender = Fighter("Beast_30")

# defender.heroes = ["Hector"] # ["Flint", "Patrick", "Seo-yoon"]     

defender.troops = {
    "infantry_t10"   : 6450,
    "lancer_t10"     : 7525,
    "lancer_t9"      : 30105,
    "marksman_t10"   : 7525,
    "marksman_t9"    : 30105
	
}


# defender.add_heroes_stats()           

# defender.joiner_heroes = ['Jessie', 'Jasser', 'Molly', "mia"]   


###############################################
### BATTLE & Print results
###############################################

BattleRound.DEBUG = True
f = Fight(attacker, defender)
f.battle(show_rounds_freq = 1)

f.format_report()


###############################################
# Save test case for future checking : Type 'yes' to confirm
###############################################

# f.save_testcase(
#     file = "4-testcases_no-heroes_fc_mixed",                 #"3-testcases_mixed-heroes-not-verified.json", # "heroes_unittests/Jessie_tc_nc.json",
#     result = [{
#         "attacker": 0,
#         "defender": 45772
#     }])
