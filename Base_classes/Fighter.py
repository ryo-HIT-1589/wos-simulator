from Base_classes.Skill import Skill, Effect
from Base_classes.StatsBonus import StatsBonus
from Base_classes.Hero import Hero
from Base_classes.UnitType import UnitType, _to_unitx
from Base_classes.JsonUtil import JsonUtil
import math, json

class Fighter:
    def __init__(self, name, load_fighter_data = True):

        self.load_fighter = load_fighter_data
        self.name = name
        self._troops = {}
        self.stats = StatsBonus.from_list(JsonUtil.fighter_stats[self.name]) if self.load_fighter else StatsBonus()
        self._heroes = {}
        self._joiner_heroes = {}
        
        self.skills = []
        self.effects = []

        self.attack_by_troop = {}
        self.defense_by_troop = {}

        self.troops_by_type = {}
        self.attack_by_type = {}
        self.defense_by_type = {}

        self.rounds = {}
        self.cumul_attacks = {ut:0 for ut in UnitType}
        self.cumul_received_attacks = {ut:0 for ut in UnitType}

    def add_heroes_stats(self):
        heroes_stats = JsonUtil.fighter_heroes
        if self.name not in heroes_stats:
            print(f"\n⚠️  fighter '{self.name}' not found in '{JsonUtil.fighters_heroes_path}' ")
            exit()
        for hero in self.heroes:
            _found = False
            for hero_n in heroes_stats[self.name]:
                if hero in hero_n.lower().capitalize() :
                    _found = True
                    h_type = _to_unitx(JsonUtil.hero_registery[hero][0]['skill_troop_type'])
                    h_stats = heroes_stats[self.name][hero_n]['stats']
                    for _stat, _value in h_stats.items():
                        self.stats.add_bonus(h_type, _stat, _value)
            if not _found:
                print(f"\n⚠️  '{hero}' stats not found in '{self.name}' data ({JsonUtil.fighters_heroes_path}) ")
                exit()

    def calc(self, opponent):
        self.calc_skills()
        for troop_name in self.troops:
            self.calc_by_troop(troop_name, opponent)
        self.calc_by_type()
    
    def calc_skills(self):
        self._calc_hero_skills()
        self._calc_troops_skills()
        self._calc_effects()

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
            
    def _calc_hero_skills(self):
        heroes_registry = JsonUtil.hero_registery
        # Fighter heroes
        for hero, levels in self.heroes.items():
            for skill in heroes_registry[hero]:
                if f"skill_{skill['skill_num']}" in levels.keys():
                    self.skills.append(Skill(skill,level = levels[f"skill_{skill['skill_num']}"]))
        # Joiners heroes
        for hero, levels in self.joiner_heroes.items():
            for skill in heroes_registry[hero]:
                if skill['skill_num'] in levels.keys():
                    self.skills.append(Skill(skill,level = levels[skill['skill_num']]))

    def _calc_troops_skills(self):
        _troop_skills_data = JsonUtil.troop_skills
        for troop_skill in _troop_skills_data:
            level = 0
            for troop_name in self.troops:
                if _to_unitx(troop_name) == _to_unitx(troop_skill['skill_troop_type']):
                    troop = JsonUtil.troop_stats[troop_name]
                    for condition in troop_skill['skill_conditions']:
                        if troop[condition['condition_type']] >= condition['condition_value']:
                            level = max(level, int(condition['level']))
            if level:
                self.skills.append(Skill(troop_skill, level))

    def _calc_effects(self):
        for skill in self.skills:
            for _effect in skill.skill_effects_data:
                self.effects.append(Effect(skill,_effect))

    def get_sum_army(self, round = 0):
        if round: return sum(math.ceil(v) for v in self.rounds[round].round_troops.values())
        return sum(self.troops_by_type.values())
    
    def get_skill_by_name(self, skill_name):
        for skill in self.skills:
            if skill.skill_name == skill_name: return skill
    
    def print_skills_list(self):
        for skill in self.skills:
            print(f"{skill.skill_hero or 'TROOP SKILL:'} - {skill.skill_name} : Level {skill.skill_level}")

    @property
    def troops(self):
        return self._troops

    @troops.setter
    def troops(self, troop_dict):
        for troop_name in troop_dict:
            if troop_name not in JsonUtil.troop_stats:
                print(f"⚠️  Error : no data found for troop '{troop_name}' (P.S: FC6+ troops are not yet supported)")
                exit()
            if troop_dict[troop_name] > 0:
                self._troops[troop_name] = troop_dict[troop_name]

    @property
    def heroes(self):
        return self._heroes
    
    @heroes.setter
    def heroes(self, _dict):
        self._heroes = Hero.get_heroes_skill_levels(_dict, fighter_name = (self.name if self.load_fighter else None), _joiners= False)

    @property
    def joiner_heroes(self):
        return self._joiner_heroes
    
    @joiner_heroes.setter
    def joiner_heroes(self, _dict):
        self._joiner_heroes = Hero.get_heroes_skill_levels(_dict, fighter_name = None, _joiners= True)