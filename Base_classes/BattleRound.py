import json
import math
from Base_classes.UnitType import UnitType, _to_unitx, prettify
from Base_classes.Skill import Skill, RoundSkill

class BattleRound():
    def __init__(self, fighter, opponent, round_idx, army_min) -> None:
        # Init
        self.fighter = fighter
        self.opponent = opponent
        self.round_idx = round_idx
        self.army_min = army_min

        # prepare
        self.round_troops = {}

        self.round_skills = []
        self.order_skills_index = []
        self.dodge_skills_index = []
        self.stun_skills_index = []

        # results
        self.round_kills = {}
        self.round_dmg_coef = {ut:0 for ut in UnitType}
        self.need_continue_skills = {}  # Not used for now

        # Calc Round troops
        self.calc_round_troops()

    def get_results(self, printing = False):
        self.calc_round_kills()
        if printing:
            self.print_round(printing)

    def calc_round_troops(self):
        # calc remaining troops by type
        if self.round_idx == 0 :
            self.round_troops = self.fighter.troops_by_type
        else :
            for ut in UnitType:
                self.round_troops[ut] = max(0, self.fighter.rounds[self.round_idx - 1].round_troops[ut] - sum(vs[ut] if ut in vs else 0 for vs in self.opponent.rounds[self.round_idx -1].round_kills.values()))
    
    def calc_skills(self) :
        # Previous round skills that are still active
        if self.round_idx > 0:
            for r_skill in self.fighter.rounds[self.round_idx - 1].round_skills:
                if r_skill.used :
                    if r_skill.need_continue :
                        self.add_round_skill(r_skill)
                    else:
                        if r_skill._skill.skill_stackable: r_skill._skill.stack -= 1
                else:
                    r_skill._skill.activations_count -= 1
    
        for skill in self.fighter.skills :
            if skill._activate_condition(self.fighter, self.opponent, self.round_idx) :
                self.add_round_skill(RoundSkill(skill, self.round_idx))
                if skill.skill_stackable: skill.stack += 1
                skill.activations_count += 1
                skill.last_round = self.round_idx - 1
    
    def add_round_skill(self, r_skill):
        self.round_skills.append(r_skill)
        self.round_skills[-1]._apply()
        for _effect in r_skill._skill.skill_effects:
            if _effect['effect_type'] == 'attack_order':
                self.order_skills_index.append(len(self.round_skills) - 1)
            if _effect['effect_type'] == 'dodge':
                self.dodge_skills_index.append(len(self.round_skills) - 1)
            if _effect['effect_type'] == 'stun':
                self.stun_skills_index.append(len(self.round_skills) - 1)


    def calc_round_kills(self):
        for ut in UnitType :
            # army size
            army = self.calc_round_army(ut)
            if army == 0:
                continue
            
            # get target
            target : UnitType = self.get_round_target(ut)
            
            # Special Skills :
            if self.dodge_skills_index or self.opponent.rounds[self.round_idx].stun_skills_index :
                # Edit later
                pass

            # troops base damage
            unit_base_dmg = army * self.fighter.attack_by_type[ut] / self.opponent.defense_by_type[target] / 100

            # Calc bonus dmg
            ut_kills = self.calc_bonus_dmg(unit_base_dmg, ut, target)

            # Fatigue
            ut_kills = ut_kills * (1 -  0.01/100 * self.round_idx)

            ### ROUNDING: Try later. PROBABLY NOT USED !
            # ut_kills = math.ceil(ut_kills)

            # store
            if ut_kills > 0:
                self.round_kills[ut] = { target : ut_kills }


    def calc_bonus_dmg(self, unit_base_dmg, ut: UnitType, vs: UnitType):
        bonus_effects = {
                # DamageUp
                "101" : [],
                "102" : [],
                "103" : [],
                # OppDefenseDown
                "211" : [],
                "212" : [],
                "213" : [],
            }
        opp_bonus_effects = {
                # DefenseUp
                "111" : [],
                "112" : [],
                "113" : [],
                # OpDamageDown
                "201" : [],
                "202" : [],
                "203" : [],
        }
        extra_attacks = []

        for r_skill in self.round_skills:
            if r_skill._apply_condition(ut, vs):
                for effect in r_skill._skill.skill_effects:
                    if effect['effect_op'] in bonus_effects:
                        r_skill._skill.uses_count += 1
                        r_skill.used = True
                        eff_value = effect['effect_values'][r_skill._skill.skill_level]
                        if r_skill._skill.skill_extra_attack:
                            extra_attacks.append(eff_value)
                            self.fighter.cumul_attacks[ut] += 1
                            self.opponent.cumul_received_attacks[vs] += 1
                            r_skill._skill.extra_damage += unit_base_dmg * eff_value /100
                        else:
                            bonus_effects[ effect['effect_op']].append(effect['effect_values'][r_skill._skill.skill_level])
        
        for opp_skill in self.opponent.rounds[self.round_idx].round_skills:
            if opp_skill._apply_condition(vs, ut):
                for opp_effect in opp_skill._skill.skill_effects:
                    if opp_effect['effect_op'] in opp_bonus_effects:
                        opp_skill._skill.uses_count += 1
                        opp_skill.used = True
                        opp_bonus_effects[ opp_effect['effect_op']].append(opp_effect['effect_values'][r_skill._skill.skill_level])
        
        ############### TO CONFIRM
        # ATTACK
        #   Attack up               : * (1 + Coef)  --> fighter_skill
        #   Op Attack down of Op    : / (1 + Coef)  --> opponent_skill
        # OPPPONENT DEFENSE
        #   Defense Up of Op        : * (1 - Coef)  --> opponent_skill
        #   Op defense down         : / (1 - Coef)  --> fighter_skill
        
        dmg_up = math.prod( (1.0 + sum(bonus_effects[_eff])/100.0) for _eff in bonus_effects.keys() if _eff.startswith("10"))
        opp_dfs_down = math.prod( (1.0 - sum(bonus_effects[_eff])/100.0) for _eff in bonus_effects.keys() if _eff.startswith("21"))
        opp_dfs_up = math.prod( (1.0 - sum(opp_bonus_effects[_eff])/100.0) for _eff in opp_bonus_effects.keys() if _eff.startswith("11"))
        dmg_down = math.prod( (1.0 + sum(opp_bonus_effects[_eff])/100.0) for _eff in opp_bonus_effects.keys() if _eff.startswith("20"))

        normal = dmg_up * opp_dfs_up / (dmg_down  * opp_dfs_down)
        extra = sum(extra_attacks) / 100.0
        
        coef = normal * (1 + extra)

        self.round_dmg_coef[ut] = coef
        self.fighter.cumul_attacks[ut] += 1
        self.opponent.cumul_received_attacks[vs] += 1
        
        return unit_base_dmg * coef

    def calc_round_army(self, ut: UnitType):
        if ut not in self.round_troops: return 0
        army = (self.round_troops[ut] ** 0.5) * (self.army_min ** 0.5)

        ##### OR 
        # # army = (self.round_troops[ut] * self.army_min) ** 0.5
        ##### MORE LOGICAL WITH PYTHON FLOATS, BUT IT HAS BEEEN PROVEN LOGIC AND WOS ARE NOT FRIENDS

        army = math.ceil(army)
        return army
    
    def get_round_target(self, ut):
        attack_order = UnitType.list()
        
        # For simplification: lancers only. To update later if needed
        if ut == UnitType.lanc:
            order_effect = self.has_order_skill()
            if order_effect :
                attack_order = [_to_unitx(_t) for _t in order_effect.split('/')]
        
        for vs in attack_order:
            if self.opponent.rounds[self.round_idx].round_troops[vs] > 0 : return vs

    def has_order_skill(self):
        if self.order_skills_index :
            _index = self.order_skills_index[0]
            for effect in self.round_skills[_index]._skill.skill_effects:
                if effect['effect_type'] == 'attack_order':
                    self.round_skills[_index]._skill.uses_count += 1  # Skill applied
                    self.round_skills[_index].used = True
                    return effect['effect_values'][self.round_skills[_index]._skill.skill_level]
        return None
        
    def total_troops(self):
        return sum(self.round_troops[ut] for ut in UnitType)
    
    def print_round(self):
        return f"{self.fighter.name}: {prettify(self.round_troops)} ___({prettify(self.round_dmg_coef)})"
    
