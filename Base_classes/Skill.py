from Base_classes.UnitType import UnitType, _to_unitx

from random import random

class Skill:
    def __init__(self, skill_dict: dict, level: int = 0) -> None:
        self.skill_name = skill_dict['skill_name']
        self.skill_type = skill_dict['skill_type']
        self.skill_troop_type = skill_dict['skill_troop_type']
        self.skill_permanent = skill_dict['skill_permanent']
        self.skill_is_chance = skill_dict['skill_is_chance']
        self.skill_probability = skill_dict['skill_probability']
        self.skill_round_stackable = skill_dict['skill_round_stackable']
        self.skill_order = skill_dict['skill_order']
        self.skill_type_relation = skill_dict['skill_type_relation']        # The skill only activates if the skill_troop_type is still present in the battle
        self.skill_frequency = skill_dict['skill_frequency']
        self.skill_effects_data = skill_dict['skill_effects']

        self.skill_hero = skill_dict['skill_hero'] if skill_dict['skill_type'] == 'hero_skill' else None
        self.skill_level = str(level or (5 if skill_dict['skill_type'] == 'hero_skill' else 1))

        # trackers:
        self.procs = {}


    def r_skill_condition(self, fighter, _round):
        # Already active, unless stackable in the same round
        if _round > 0 and self.skill_round_stackable == False:
            for benefit in fighter.rounds[_round - 1].round_benefits:
                benefit:Benefit
                if (self.skill_name in benefit.id) and benefit.is_valid("any","any",_round):
                    return False

        # type-relation check : Skills that only work if their base_troop_type is still present in the battle
        if self.skill_type_relation and fighter.rounds[_round].round_troops[_to_unitx(self.skill_troop_type)] <= 0: 
            return False

        # Round conditions
        if not self.skill_permanent :
            # start round
            if 'skill_first_round' in self.skill_frequency and (_round + 1) < self.skill_frequency['skill_first_round'] : return False
            # last round
            if 'skill_last_round' in self.skill_frequency and (_round + 1) > self.skill_frequency['skill_last_round'] : return False
            # round frequency
            if self.skill_frequency['frequency_type'] in ['turn','round']:
                _start = 0 if 'skill_first_round' not in self.skill_frequency else min(self.skill_frequency['skill_first_round'] - 1,0)
                if (_round - _start) % self.skill_frequency['frequency_value'] != 0 : return False
            # chance
            if self.skill_is_chance :
                if not self.proc(_round): return False # do not return self.proc(_round), more checks could be added later 
        return True
    
    def proc(self, _round):
        if _round not in self.procs: 
            r = random()
            self.procs[_round] = (r < self.skill_probability / 100.0)
        return self.procs[_round]

class Effect():
    def __init__(self, skill:Skill, effect_dict):
        self._skill = skill
        self.name = effect_dict['effect_num']
        self.affects_opponent = effect_dict['affects_opponent']
        self.extra_attack = effect_dict['extra_attack']

        self.trig_for_unit = effect_dict['trigger_types']['trigger_for']
        # trig_for_unit values: All, once (only once per turn), inf, mark, lanc
        self.trig_vs_unit = effect_dict['trigger_types']['trigger_vs']  
        # trig_vs_unit values: All, inf, mark, lanc
        self.ben_for_unit = effect_dict['benefit_types']['benefit_for'] 
        # ben_for_unit values: All, friendly, trigger (benefit only applies to unit who triggered it), inf, lanc, mark
        self.ben_vs_unit = effect_dict['benefit_types']['benefit_vs']   
        # ben_vs_unit values: All, target (benefit only applies to unit aginst whom it was triggered), inf, lanc, mark

        self.type = effect_dict['effect_type']
        self.op = effect_dict['effect_op']
        self.duration = effect_dict['effect_duration']
        # # self.unit_stackable = effect_dict['effect_unit_stackable']      # DEPRECATED: Replaced by using 'once' for trig_for_units
        self.is_chance = effect_dict['effect_is_chance']
        self.special = effect_dict['special']

        self.level = skill.skill_level
        self.troop_type = skill.skill_troop_type
        self.is_permanent = skill.skill_permanent
        self.frequency = skill.skill_frequency
        if self.is_chance:
            self.probability = effect_dict['effect_probabilities'][self.level]
        if self.type.lower() in ['stun', 'dodge']:
            self.value = 0
        else:
            self.value = effect_dict['effect_values'][self.level]

        self.last_round = None
        self.trigger_count = 0
        self.activations_count = 0
        self.uses_count = 0
        self.extra_kills = 0
    
    def r_effect_condition(self, fighter, opponent, _round):
        # print(f'R{_round} ------ checking condition for effect {self.name}')
        # check if for_unit still present in battle
        if self.trig_for_unit not in  ["all", "once", "first"]:
            r_troops = fighter.rounds[_round].round_troops
            if self.trig_for_unit != "friendly":
                # print(f'R{_round} ------ FALSE: friendly')
                if r_troops[_to_unitx(self.trig_for_unit)] <= 0: return False
            else:
                if not any((r_troops[_type] > 0) for _type in UnitType if _type != _to_unitx(self.trig_for_unit) ): return False

        # check if opponent vs_unit still present in battle
        if self.trig_vs_unit != "all":
            if opponent.rounds[_round].round_troops[_to_unitx(self.trig_vs_unit)] <= 0 : return False
        
        return True
    
    def get_report(self):
        skill_name = f"{self._skill.skill_hero or self._skill.skill_troop_type.upper()}- {self.name}"
        skill_data = f"{self.trigger_count} ({self.uses_count}){f' - Extra: {self.extra_kills:.1f}' if self.extra_kills else ''}"
        skill_type = f"({self.type})"
        return f"{skill_name} {' '* max(0,30-len(skill_name))}:    {skill_data}{' '*max(0,10-len(skill_data))} {skill_type}"


class RoundEffect:
    def __init__(self, effect: Effect, round_idx: int):
        self._effect = effect
        self.round_idx = round_idx
        self.r_eff_id = f"{round_idx}_{effect.name}"

        self.activated_in_round = False
        self.attempted_in_round = False
        # self.remaining_duration = effect.duration
        # self._need_continue = False #(self.remaining_duration > 1) or _skill.skill_permanent

    def trigger_condition(self, fighter, opponent, ut, vs, _round):
        # Already attempted
        if self.attempted_in_round and (self._effect.trig_for_unit == 'first'): return False
        self.attempted_in_round = True
        # Already activated in round for unit, unless stackable in the same round
        if self.activated_in_round and (self._effect.trig_for_unit == 'once'): return False
        # attack frequency
        if not self._effect.is_permanent and 'attack' in self._effect.frequency['frequency_type']:
            if fighter.cumul_attacks[ut] % self._effect.frequency['frequency_value'] != 0 : return False
        
        # check if could be triggered by unit
        if self._effect.trig_for_unit == "friendly":
            if _to_unitx(self._effect.troop_type) == ut : return False
        elif self._effect.trig_for_unit not in ["all", "once", "first"]:
            if _to_unitx(self._effect.troop_type) != ut : return False
        # check if could be triggered against enemy unit
        if self._effect.trig_vs_unit != "all":
            if _to_unitx(self._effect.trig_vs_unit) != vs : return False
    
        # chance
        if self._effect.is_chance :
            r = random()
            if ( r >= self._effect.probability/100.0): 
                return False
        
        return True
    
    def activate_effect(self, fighter, ut, vs):
        self.activated_in_round = True

        if self._effect.is_permanent: self._effect.trigger_count = 1
        else: self._effect.trigger_count += 1

        return Benefit(self, fighter, ut, vs)

class Benefit:
    def __init__(self, roundEff: RoundEffect, fighter, ut: UnitType, vs: UnitType):

        self.fighter = fighter
        self.id = roundEff.r_eff_id + '_' + str(roundEff.round_idx) + '_' + ut.value

        self.duration = roundEff._effect.duration['duration_value']
        self.duration_type = roundEff._effect.duration['duration_type']
        self.lag = roundEff._effect.duration['effect_lag']

        self.benefit_type = roundEff._effect.type
        self.op = str(roundEff._effect.op)
        self.value = roundEff._effect.value
        self.extra_attack = roundEff._effect.extra_attack

        self.only_normal = False
        if 'only_normal' in roundEff._effect.special:
            self.only_normal = True

        # for_units : Unit types the benefit applies for        
        if roundEff._effect.ben_for_unit == 'trigger':
            self.for_units = [ut]
        elif roundEff._effect.ben_for_unit == 'all':
            self.for_units = [_ut for _ut in UnitType]
        elif roundEff._effect.ben_for_unit == 'friendly':
            self.for_units = [_ut for _ut in UnitType if _ut != _to_unitx(roundEff._effect.troop_type)]
        elif _to_unitx(roundEff._effect.ben_for_unit) in UnitType.list():
            self.for_units = [_to_unitx(roundEff._effect.ben_for_unit)]
        else:
            raise ValueError(f"Unknown value for ben_for_units ({roundEff._effect.ben_for_unit}) for hero '{roundEff._effect._skill.skill_hero}' effeect '{roundEff.r_eff_id}' ")

        # vs_units : Unit types the benefit applies against
        if roundEff._effect.ben_vs_unit == 'target':
            self.vs_units = [vs]
        elif roundEff._effect.ben_vs_unit == 'all':
            self.vs_units = [_ut for _ut in UnitType]
        elif _to_unitx(roundEff._effect.ben_vs_unit) in UnitType.list():
            self.vs_units = [_to_unitx(roundEff._effect.ben_vs_unit)]
        else:
            raise ValueError(f"Unknown value for ben_for_units ({roundEff._effect.ben_vs_unit}) for hero '{roundEff._effect._skill.skill_hero}' effeect '{roundEff.r_eff_id}' ")
        
        self._effect = roundEff._effect
        self.start_round = roundEff.round_idx
        self.attack_counter = 0
        self.used = False

    def is_valid(self, ut, vs, _round, extra_attack = False):
        if ut != "any" and ut not in self.for_units: return False
        if vs != "any" and vs not in self.vs_units: return False
        if extra_attack and self.only_normal: return False
        if self.duration_type in ['turn', 'round'] and self.duration != -1:
            if (_round - self.start_round) < self.lag: return False
            if (_round - self.start_round - self.lag) >= self.duration: return False
        if 'attack' in self.duration_type:
            if self.attack_counter < self.lag: return False
            if (self.attack_counter - self.lag) >= self.duration: return False
        return True
    
    def use(self):
        self.used = True
        self._effect.uses_count += 1
        self.attack_counter += 1

    def correct_value(self, round_idx):
        if 'effect_evolution' not in self._effect.special: return self.value
        correct_value = self.value

        evo_category = self._effect.special['effect_evolution']["category"]
        if evo_category == 'effect_is_total_damage' : 
            correct_value -= 100
        elif evo_category == 'effect_decrease':
            evo_data = self._effect.special['effect_evolution']["data"]
            if evo_data['type'] == "pct_value_fixed_decrease":
                if evo_data['step'] == 'attack':
                    correct_value = max(self.value - self.attack_counter * evo_data['decrease_value'],0)
                if evo_data['step'] in ['round', 'turn']:
                    correct_value = max(self.value - (round_idx - self.start_round) * evo_data['decrease_value'],0)
            elif evo_data['type'] == "pct_value_pct_decrease":
                if evo_data['step'] == 'attack':
                    correct_value = self.value * (1 - self.attack_counter * evo_data['decrease_value']/100)
                if evo_data['step'] in ['round', 'turn']:
                    correct_value = max(self.value * (1 - (round_idx - self.start_round) * evo_data['decrease_value']),0)
        # To-do: Add more effect evolution types if needed
        elif evo_category == 'fixed_damage':
            pass
        elif evo_category == 'fixed_kills':
            pass
        return correct_value
    
    def __str__(self):
        return f"{self._effect._skill.skill_hero}:{self.id} - {self.benefit_type} - Op: {self.op} - Value: {self.value} - Extra: {self.extra_attack} ; duration: {self.duration} {self.duration_type} - ut: {[u.name for u in self.for_units] if self.for_units else None} - vs: {[u.name for u in self.vs_units] if self.vs_units else None}"
        

