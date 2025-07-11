from Base_classes.Skill import Skill
from Base_classes.StatsBonus import StatsBonus
from Base_classes.UnitType import UnitType, _to_unitx
from Base_classes.JsonUtil import JsonUtil
import math

class Fighter:
    def __init__(self, name):

        self.name = name
        self._troops = {}
        self.stats = StatsBonus()
        
        self.skills = []

        self.attack_by_troop = {}
        self.defense_by_troop = {}

        self.troops_by_type = {}
        self.attack_by_type = {}
        self.defense_by_type = {}

        self.rounds = {}
        self.cumul_attacks = {ut:0 for ut in UnitType}
        self.cumul_received_attacks = {ut:0 for ut in UnitType}

    def calc(self, opponent):
        self.calc_skills()
        for troop_name in self.troops:
            self.calc_by_troop(troop_name, opponent)
        self.calc_by_type()
    
    def calc_skills(self):
        self._calc_hero_skills()
        self._calc_troops_skills()

    def calc_by_troop(self, troop_name, opponent):
        troop = JsonUtil.troop_stats[troop_name]
        base_attack = troop["stats"].get("Attack")
        base_lethality = troop["stats"].get("Lethality")
        base_health = troop["stats"].get("Health")
        base_defense = troop["stats"].get("Defense")
        troop_type = _to_unitx(troop_name)

        fighter_stats = self.stats.__getattribute__(troop_type.name)
        bonus_attack = fighter_stats.attack / 100
        bonus_lethality = fighter_stats.lethality / 100
        bonus_health = fighter_stats.health / 100
        bonus_defense = fighter_stats.defense / 100

        attack_ret = base_attack * (1 + bonus_attack) * base_lethality * (1 + bonus_lethality) / 100.0
        defense_ret = base_health * (1 + bonus_health) * base_defense * (1 + bonus_defense) / 100.0

        self.attack_by_troop[troop_name] = attack_ret
        self.defense_by_troop[troop_name] = defense_ret

    def calc_by_type(self):
        # To-Do: Verify that skills do indeed work like stamps
        for ut in UnitType:
            total_attack = 0.0
            total_defense = 0.0
            count = 0

            for troop_name in self.troops:
                if ut == _to_unitx(troop_name):
                    num = self.troops[troop_name]
                    total_attack += num * self.attack_by_troop[troop_name]
                    total_defense += num * self.defense_by_troop[troop_name]
                    count += num
            
            # SOS Model: To confirm
            attack = 0.0
            defense = 0.0
            if total_attack > 0 and total_defense > 0:
                attack = 1.0
                defense = 1.0
                for troop_name in self.troops:
                    if ut == _to_unitx(troop_name):
                        num = self.troops[troop_name]
                        atk = self.attack_by_troop[troop_name]
                        defn = self.defense_by_troop[troop_name]
                        attack *= math.pow(atk, num * atk / total_attack)
                        defense *= math.pow(defn, num * defn / total_defense)

            self.attack_by_type[ut] = attack
            self.defense_by_type[ut] = defense
            self.troops_by_type[ut] = count

            
            ######## OTHERWISE, Try
            # self.attack_by_type[ut] = total_attack / count
            # self.defense_by_type[ut] = total_defense / count
            # self.troops_by_type[ut] = count
            ################## Try later
            

    def _calc_hero_skills(self):    # Add heroes logic
        pass

    def _calc_troops_skills(self):
        _troop_skills_data = JsonUtil.troop_skills
        for troop_name in self.troops:
            for troop_skill in _troop_skills_data:
                if _to_unitx(troop_name) == _to_unitx(troop_skill['skill_troop_type']):
                    troop = JsonUtil.troop_stats[troop_name]
                    condition = troop_skill['skill_conditions'][0]['condition_type']
                    if troop[condition] >= troop_skill['skill_conditions'][0]['condition_value']:
                        self.skills.append(Skill(troop_skill))

    def get_sum_army(self):
        return sum(self.troops_by_type.values())
    
    def get_skill_by_name(self, skill_name):
        for skill in self.skills:
            if skill.skill_name == skill_name: return skill

    @property
    def troops(self):
        return self._troops

    @troops.setter
    def troops(self, troop_dict):
        for troop_name in troop_dict:
            if troop_dict[troop_name] > 0:
                self._troops[troop_name] = troop_dict[troop_name]