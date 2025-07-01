from Base_classes.Fighter import Fighter
from Base_classes.UnitType import UnitType
from Base_classes.StatsBonus import StatsBonus
from Base_classes.BattleRound import BattleRound
import math

class Fight:
    def __init__(self, attacker: Fighter, defender: Fighter, battle_type = 'standart', max_round = 1500):
        self.attacker = attacker
        self.defender = defender
        self.battle_type = battle_type
        self.max_round = max_round

        # self.attacker.set_battle_type(battle_type)
        # self.defender.set_battle_type(battle_type.get_oponent())  # To update


    def battle(self, show_rounds = False):
        self.attacker.calc(self.defender)
        self.defender.calc(self.attacker)
        print('\n--------------- BATTLE  ----------------')

        army_min = min(self.attacker.get_sum_army(), self.defender.get_sum_army())
        end = False
        round_idx = 0

        while not end:            
            # Prepare
            self.attacker.rounds[round_idx] = BattleRound(self.attacker, self.defender, round_idx, army_min)
            self.defender.rounds[round_idx] = BattleRound(self.defender, self.attacker, round_idx, army_min)

            if round_idx == 0 or show_rounds:
                print(f'Round {round_idx}:   ATTACKER: {self.attacker.rounds[round_idx].str_start_troops()}   ---   DEFENDER: {self.defender.rounds[round_idx].str_start_troops()}')

            att_troops = self.attacker.rounds[round_idx].total_troops()
            def_troops = self.defender.rounds[round_idx].total_troops() 
            
            end = (att_troops == 0) or (def_troops == 0)
            if end or round_idx > self.max_round:
                break

            # Calc skills
            self.attacker.rounds[round_idx].calc_skills()
            self.defender.rounds[round_idx].calc_skills()

            # Get results
            self.attacker.rounds[round_idx].get_results()
            self.defender.rounds[round_idx].get_results()

            round_idx += 1
        
        print('\n--------------- BATTLE ENDED  ----------------')
        print(f'Result :    Attacker : {math.ceil(att_troops)}   -   Defender: {math.ceil(def_troops)}       ({round_idx} rounds)')
