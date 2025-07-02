from Base_classes.Fighter import Fighter
from Base_classes.UnitType import UnitType, prettify
from Base_classes.StatsBonus import StatsBonus
from Base_classes.BattleRound import BattleRound
import math

class Fight:
    def __init__(self, attacker: Fighter, defender: Fighter, max_round = 1500):
        self.attacker = attacker
        self.defender = defender
        self.max_round = max_round

    def battle(self, show_rounds_freq = 0):
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

            # print details
            if round_idx == 0 or (show_rounds_freq and round_idx % show_rounds_freq == 0):
                print(f'Round {round_idx} --- ATT: {self.attacker.rounds[round_idx].print_round()}   ---   DEF: {self.defender.rounds[round_idx].print_round()}')

            round_idx += 1
        
        # print results
        print('\n--------------- BATTLE ENDED  ----------------')
        att_remaining = {k: math.ceil(v) for k,v in self.attacker.rounds[round_idx].round_troops.items()}
        sum_att = sum(att_remaining.values())
        def_remaining = {k: math.ceil(v) for k,v in self.defender.rounds[round_idx].round_troops.items()}
        sum_def = sum(def_remaining.values())

        print(f'Result: ({round_idx} rounds)    Attacker : {sum_att} ({prettify(att_remaining)})   -   Defender: {sum_def} ({prettify(def_remaining)})  ')

        return sum_att, sum_def
    
    def print_skills_report(self):
        print('\n---------- ATTACKER SKILLS')
        for skill in self.attacker.skills:
            # if skill.skill_name == 'Ambusher': print('Ambusher_uses = ', skill.uses_count)
            if skill.activations_count != 0:
                print(f'- {skill.skill_name} : {skill.activations_count} {f"({skill.extra_damage:.1f} extra)" if skill.extra_damage else ""} ')
                
        print('\n---------- DEFENDER SKILLS')
        for skill in self.defender.skills:
            if skill.activations_count != 0:
                print(f'- {skill.skill_name} : {skill.activations_count} {f"({skill.extra_damage:.1f} extra)" if skill.extra_damage else ""} ')