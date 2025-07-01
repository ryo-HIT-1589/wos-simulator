from Base_classes.UnitType import UnitType, _to_unitx

from random import random

class Skill:
    def __init__(self, skill_dict: dict, level: int = 0) -> None:
        self.skill_name = skill_dict['skill_name']
        self.skill_type = skill_dict['skill_type']
        self.skill_default_level = skill_dict['skill_default_level']
        self.skill_troop_type = skill_dict['skill_troop_type']
        self.skill_permanent = skill_dict['skill_permanent']
        self.skill_lag = skill_dict['skill_lag']
        self.skill_frequency = skill_dict['skill_frequency']
        self.skill_duration = skill_dict['skill_duration']
        self.skill_stackable = skill_dict['skill_stackable']
        self.skill_is_chance = skill_dict['skill_is_chance']
        self.skill_probability = skill_dict['skill_probability']
        self.skill_affects_opponent = skill_dict['skill_affects_opponent']
        self.skill_target_type = skill_dict['skill_target_type']            # The skill affects this type (of fighter)
        self.skill_trigger_type = skill_dict['skill_trigger_type']          # The skill activates against this type (of opponent)
        self.skill_type_relation = skill_dict['skill_type_relation']        # The skill only activates if the skill_troop_type is still present in the battle
        # self.skill_conditions = skill_dict['skill_conditions']
        self.skill_order = skill_dict['skill_order']
        self.skill_effects = skill_dict['skill_effects']

        self.skill_level = self.skill_default_level if level == 0 else level

        # trackers:
        self.last_round = None
        self.activations_count = 0
        self.stack = 0

    def _activate_condition(self, fighter, opponent, _round):
        # need_continue (unless stackable)
        if _round > 0 and self.skill_stackable == False and self.skill_name in fighter.rounds[_round - 1].need_continue_skills : return True

        # permanent skill : Skill that activates every round
        if not self.skill_permanent : 
            # start round
            if _round < self.skill_lag : return False
            # frequency
            if (_round - self.skill_lag) % self.skill_frequency != 0 : return False
            # chance
            if self.skill_is_chance and (random() >= self.skill_probability): return False
        
        # relation check : Skills that only work if their base_troop_type is still present in the battle
        if self.skill_type_relation and fighter.round[_round].round_troops[_to_unitx(self.skill_troop_type)] <= 0: 
            return False
        
        # check if target still present in battle
        if self.skill_target_type != "all":
            r_troops = fighter.rounds[_round].round_troops
            if self.skill_target_type != "friendly":
                if r_troops[_to_unitx(self.skill_target_type)] <= 0: return False
            else:
                if not any( (r_troops[_type] > 0) for _type in UnitType if _type != _to_unitx(self.skill_target_type) ): return False

        # check if trigger still present in battle
        if self.skill_trigger_type != "all":
            if opponent.rounds[_round].round_troops[_to_unitx(self.skill_trigger_type)] <= 0 : return False

        return True


class RoundSkill():
    def __init__(self, _skill:Skill, round:int) -> None:
        # trackers
        self._skill = _skill
        self.id = _skill.skill_name + "_" + str(_skill.stack + 1) # change later to support stackable skills
        self.round_idx = round
        self.remaining_duration = _skill.skill_duration
        self.need_continue = (self.remaining_duration > 1)
    
    def _apply_condition(self, fighter, opponent, ut, vs):
        # check target
        if self._skill.skill_target_type == "friendly":
            if _to_unitx(self._skill.skill_target_type) == ut : return False
        elif self._skill.skill_target_type != "all":
            if _to_unitx(self._skill.skill_target_type) != ut : return False
        # check trigger
        if self._skill.skill_trigger_type != "all" and _to_unitx(self._skill.skill_trigger_type) != vs : return False
        return True
    
    def _apply(self):
        self.remaining_duration = self.remaining_duration - 1
        self.need_continue = (self.remaining_duration > 0)
        return self.need_continue

    def get_effect(self, _effect_type):
        if "_effect_type" == "damage":
            return self._damage
        
        if "_effect_type" == "defense":
            return self._defense
        
        if "_effect_type" == "dodge":
            return self._dodge
        
        if "_effect_type" == "stunt":
            return self._stunt
        
        if "_effect_type" == "order":
            return self._damage
   