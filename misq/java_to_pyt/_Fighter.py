import math
from Base_classes.UnitType import UnitType

# Assumes existing helpers: JsonUtil, Skill, RoundUnit, BattleType

class Fighter:
    DEBUG = False

    def __init__(self):
        self.is_monster = False
        self.battle_type = None

        self.boost = {}
        self.used_boost = {}
        self.troops = {}

        self.troops_by_type = {}
        self.attack_by_troop = {}
        self.defense_by_troop = {}

        self.attack_by_type = {}
        self.defense_by_type = {}

        self.skills = {}
        self.skills_details = []

        self.round = []

    def calc(self, opponent):
        self._calc_skills()
        for troop_id in self.troops:
            self._calc_by_troop(troop_id, opponent)
        self._calc_by_type()

    def _calc_skills(self):
        for survivor_id in self.skills:
            survivor = JsonUtil.json_by_id(JsonUtil.survivors, "InternalId", str(survivor_id))
            unit_type = None
            for tag in survivor.get("ProfessionTag", []):
                tag_obj = JsonUtil.json_by_id(JsonUtil.survivorTag, "InternalId", str(tag))
                unit_type = self._to_unit_type(tag_obj.get("Id"))
                if unit_type:
                    break
            if not unit_type:
                raise Exception("UnitType not found for " + survivor.get("Id"))

            for skill_id in self.skills[survivor_id]:
                if skill_id is None:
                    continue
                main_skill = JsonUtil.json_by_id(JsonUtil.survivorSkillMain, "InternalId", str(skill_id))
                skill_new = main_skill.get("SkillNew")
                slg_skill = JsonUtil.json_by_id(JsonUtil.survivorSlgSkill, "InternalId", str(skill_new))
                for eff_id in slg_skill.get("SkillEffect_ID", []):
                    effect = JsonUtil.json_by_id(JsonUtil.survivorSlgEffect, "InternalId", str(eff_id))
                    skill = Skill(unit_type, slg_skill.get("SkillStart"))
                    skill.from_json(effect)
                    self.skills_details.append(skill)
                    if Fighter.DEBUG:
                        print(survivor.get("Id"), eff_id, skill, main_skill.get("Id"))

            self.skills_details.sort(key=lambda o: (o.effect == 101, o.order))

    def _calc_by_type(self):
        for utype in [UnitType.INFANTRY, UnitType.CAVALRY, UnitType.RANGED]:
            self._calc_by_type_unit(utype)

    def _calc_by_type_unit(self, unit_type):
        total_attack = 0.0
        total_defense = 0.0
        count = 0
        for tid in self.troops:
            unit = JsonUtil.json_by_id(JsonUtil.unitStats, "InternalId", str(tid))
            if unit_type == self._to_unit_type(unit.get("Id")):
                num = self.troops[tid]
                total_attack += num * self.attack_by_troop.get(tid, 0)
                total_defense += num * self.defense_by_troop.get(tid, 0)
                count += num

        attack = 1.0
        defense = 1.0
        if total_attack > 0 and total_defense > 0:
            for tid in self.troops:
                unit = JsonUtil.json_by_id(JsonUtil.unitStats, "InternalId", str(tid))
                if unit_type == self._to_unit_type(unit.get("Id")):
                    num = self.troops[tid]
                    atk = self.attack_by_troop[tid]
                    defn = self.defense_by_troop[tid]
                    attack *= math.pow(atk, num * atk / total_attack)
                    defense *= math.pow(defn, num * defn / total_defense)

        self.attack_by_type[unit_type] = attack
        self.defense_by_type[unit_type] = defense
        self.troops_by_type[unit_type] = count

    def _calc_by_troop(self, troop_id, opponent):
        unit = JsonUtil.json_by_id(JsonUtil.unitStats, "InternalId", str(troop_id))
        base_attack = unit.get("Attack")
        base_damage = unit.get("Damage")
        base_health = unit.get("Health")
        base_defense = unit.get("Defense")
        unit_type = self._to_unit_type(unit.get("Id"))

        bonus_attack = bonus_lethality = bonus_health = bonus_defense = 0.0
        if unit_type == UnitType.INFANTRY:
            bonus_attack += self._benefice_calc("calc_infantry_commando_attack", opponent)
            bonus_lethality += self._benefice_calc("calc_infantry_commando_damage", opponent)
            bonus_health += self._benefice_calc("calc_infantry_commando_health", opponent)
            bonus_defense += self._benefice_calc("calc_infantry_commando_defense", opponent)
        elif unit_type == UnitType.RANGED:
            bonus_attack += self._benefice_calc("calc_ranged_artilleryman_attack", opponent)
            bonus_lethality += self._benefice_calc("calc_ranged_artilleryman_damage", opponent)
            bonus_health += self._benefice_calc("calc_ranged_artilleryman_health", opponent)
            bonus_defense += self._benefice_calc("calc_ranged_artilleryman_defense", opponent)
        elif unit_type == UnitType.CAVALRY:
            bonus_attack += self._benefice_calc("calc_cavalry_velociraptor_rider_attack", opponent)
            bonus_lethality += self._benefice_calc("calc_cavalry_velociraptor_rider_damage", opponent)
            bonus_health += self._benefice_calc("calc_cavalry_velociraptor_rider_health", opponent)
            bonus_defense += self._benefice_calc("calc_cavalry_velociraptor_rider_defense", opponent)

        attack_ret = base_attack * (1 + bonus_attack) * base_damage * (1 + bonus_lethality) / 100.0
        defense_ret = base_health * (1 + bonus_health) * base_defense * (1 + bonus_defense) / 100.0

        self.attack_by_troop[troop_id] = attack_ret
        self.defense_by_troop[troop_id] = defense_ret

    def _benefice_calc(self, calc_id, opponent):
        benefit = JsonUtil.json_by_id(JsonUtil.benefitCalc, "Id", calc_id)
        return self.benefice_calc(benefit, "PercentParam") + opponent.benefice_calc(benefit, "OppPercentParam")

    def benefice_calc(self, benefit_calc, key):
        total = 0.0
        for bid in benefit_calc.get(key, []):
            val = self.boost.get(int(bid))
            if val is not None:
                self.used_boost[int(bid)] = val
                if Fighter.DEBUG:
                    print("Boost", bid, "=>", val)
                total += val
        return total

    def _to_unit_type(self, id_str):
        uid = id_str.upper()
        if "INFANTRY" in uid:
            return UnitType.INFANTRY
        if "CAVALRY" in uid:
            return UnitType.CAVALRY
        if "RANGED" in uid:
            return UnitType.RANGED
        return None

    def get_sum_army(self):
        return sum(self.troops_by_type.values())

    def has_bikers(self):
        for tid in self.troops:
            unit = JsonUtil.json_by_id(JsonUtil.unitStats, "InternalId", str(tid))
            if unit.get("TroopClass") == 1400005:
                return True
        return False

    def has_snipers(self):
        for tid in self.troops:
            unit = JsonUtil.json_by_id(JsonUtil.unitStats, "InternalId", str(tid))
            if unit.get("TroopClass") == 1400004:
                return True
        return False

    def get_result(self):
        first = self.round[0]
        last = self.round[-1]
        start = sum(u.get_nb_unit() for u in first.values())
        end = sum(u.get_nb_unit() for u in last.values())
        total = start - end

        battle_wounded = JsonUtil.json_by_id(JsonUtil.battleWounded, "Id", self.battle_type.code)
        wound_rate = battle_wounded.get("WoundRate")
        minor_rate = battle_wounded.get("MinorWoundRate")

        minor = round(minor_rate * total)
        if wound_rate + minor_rate == 1:
            wound = total - minor
            dead = 0
        else:
            wound = round(wound_rate * total)
            dead = total - wound - minor

        result = {
            "start": start,
            "end": end,
            "total": total,
            "dead": dead,
            "wound": wound,
            "minorWound": minor
        }
        for t in [UnitType.INFANTRY, UnitType.CAVALRY, UnitType.RANGED]:
            result["start" + t.title()] = first[t].get_nb_unit()
            result["end" + t.title()] = last[t].get_nb_unit()
        return result

    def add_boost(self, key, val):
        benefit = JsonUtil.json_by_id(JsonUtil.benefits, "InternalId", str(key))
        for code in benefit.get("BattleType", []):
            if code == "all" or code == self.battle_type.code:
                self.boost[key] = self.boost.get(key, 0.0) + val
                break

    def add_joiner_skill(self, skill_id):
        main = JsonUtil.json_by_id(JsonUtil.survivorSkillMain, "InternalId", str(skill_id))
        for ben in main.get("Benefits", []):
            bid = ben.get("benefit_id")
            if bid in [300662, 300869, 300781]:
                value = ben.get("benefit_value")
                skill = Skill(UnitType.INFANTRY, 1)
                skill.set_value(0.36 * (value * 100))
                skill.set_effect(302)
                skill.set_round_lag(0)
                skill.set_effect_target(30)
                skill.set_target(None)
                skill.set_trigger(None)
                self.skills_details.append(skill)

    def add_buff(self, buff_id):
        city = JsonUtil.json_by_id(JsonUtil.city_buff_main, "InternalId", str(buff_id))
        for k, v in city.get("Benefit", {}).items():
            self.add_boost(int(k), v)


