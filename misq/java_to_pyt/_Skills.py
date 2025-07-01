from typing import Optional, Dict, Any

from simulator.unit_type import UnitType
from simulator.fighter import Fighter

class Skill:
    def __init__(self, unit_type: UnitType, round_freq: int):
        self.unit_type = unit_type
        self.round_freq = round_freq
        self.value: float = 0.0
        self.effect: int = 0
        self.effect_target: int = 0
        self.round_lag: int = 0
        self.trigger: Optional[UnitType] = None
        self.target: Optional[UnitType] = None
        self.order: int = 1
        self.effect_relation: int = 0
        self.protect: float = 0.0
        self.last_round: int = -1

    def from_json(self, data: Dict[str, Any]) -> None:
        self.value = float(data.get("EffectAttr", 0))
        self.effect = int(data.get("EffectResult", 0))
        self.round_lag = int(data.get("EffectLag", 0))
        self.effect_target = int(data.get("EffectTarget", 0))
        self.target = UnitType.decode_string(data.get("EffectTargetData", ""))
        self.trigger = UnitType.decode_string(data.get("EffectTriggerData", ""))
        self.order = int(data.get("EffectLag", 0))
        self.effect_relation = int(data.get("EffectRelation", 0))

    @staticmethod
    def damage(fighter: Fighter, unit_type: UnitType, vs: UnitType, round_: int) -> float:
        coef = 1.0
        for skill in fighter.get_skills_details():
            if skill._condition(fighter, unit_type, vs, False, round_):
                eff = skill.effect
                val_pct = skill.value / 100.0
                if eff == 101 and unit_type == skill.unit_type:
                    if skill.last_round == round_:
                        coef -= 1.0
                    coef *= (1 + val_pct)
                    skill.last_round = round_
                elif eff == 201:
                    coef += val_pct
                elif eff == 221:
                    coef += (skill.value / 3) / 100.0
                elif eff == 301:
                    coef += val_pct
                elif eff == 211 and unit_type == skill.unit_type:
                    coef += (skill.value * 1.4) / 100.0
        return coef

    @staticmethod
    def defense(fighter: Fighter, unit_type: UnitType, vs: UnitType, round_: int) -> float:
        coef = 0.0
        for skill in fighter.get_skills_details():
            if skill._condition(fighter, unit_type, vs, True, round_):
                if skill.effect in (202, 302):
                    coef += skill.value / 100.0
        return coef

    @staticmethod
    def protect(fighter: Fighter, unit_type: UnitType, vs: UnitType, round_: int, dead: int) -> int:
        total_protect = 0.0
        remain_dead = float(dead)
        for skill in fighter.get_skills_details():
            if skill._condition(fighter, unit_type, vs, True, round_):
                if skill.effect in (801, 901):
                    if round_ != skill.last_round:
                        skill.protect = dead * skill.value / 100.0
                        skill.last_round = round_
                    if remain_dead > 0 and skill.protect > 0:
                        if skill.protect > remain_dead:
                            total_protect += remain_dead
                            skill.protect -= remain_dead
                        else:
                            total_protect += skill.protect
                            skill.protect = 0.0
                        remain_dead -= total_protect
        return int(total_protect)

    @staticmethod
    def need_continue(fighter: Fighter, unit_type: UnitType, vs: UnitType, round_: int) -> bool:
        for skill in fighter.get_skills_details():
            if skill._condition(fighter, unit_type, vs, False, round_):
                if skill.effect_target == 40 and skill.effect == 101 and skill.unit_type == unit_type:
                    return True
        return False

    def _condition(self, fighter: Fighter, unit_type: UnitType, vs: UnitType,
                   is_defense: bool, round_: int) -> bool:
        # Exclude same unit when effect_target == 31
        if self.effect_target == 31 and self.unit_type == unit_type:
            return False

        # If unit decimated and relation requires alive
        if fighter.get_round()[round_ - 1].get(unit_type).get_nb_unit() <= 0 and self.effect_relation == 2:
            return False

        # Round frequency & lag check
        if (round_ - self.round_lag) > 0 and (round_ - self.round_lag) % self.round_freq == 0:
            # Target check
            expected_target = vs if self.effect_target == 20 else unit_type
            if self.target is None or self.target == expected_target:
                # Trigger check
                if self.trigger is None or self.trigger == vs:
                    # Source alive check
                    if fighter.get_round()[round_ - 1].get(unit_type).get_nb_unit() > 0:
                        return True
        return False

    def __str__(self) -> str:
        return f"{self.unit_type}\t {self.round_freq}\t{self.round_lag}\t{self.value}\t{self.effect}\t{self.effect_target}\t{self.target or ''}"
