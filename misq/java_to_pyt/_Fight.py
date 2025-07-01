class Fight:
    def __init__(self, battle_type, max_round):
        self.attacker = Fighter()
        self.attacked = Fighter()
        self.battle_type = battle_type
        self.max_round = max_round

        self.attacker.set_battle_type(battle_type)
        self.attacked.set_battle_type(battle_type.get_oponent())

    def calc(self):
        self.attacker.calc(self.attacked)
        self.attacked.calc(self.attacker)
        self.round()

    def round(self):
        army_min = min(self.attacker.get_sum_army(), self.attacked.get_sum_army())
        end = False
        round_idx = 0

        while not end:
            self._round(self.attacker, self.attacked, army_min, round_idx)
            self._round(self.attacked, self.attacker, army_min, round_idx)

            end1 = self.calc_nb_unit(self.attacker, self.attacked, round_idx)
            end2 = self.calc_nb_unit(self.attacked, self.attacker, round_idx)

            end = end1 or end2
            round_idx += 1
            if round_idx > self.max_round:
                end = True

    def calc_nb_unit(self, fighter, opponent, round_idx):
        total_unit = 0
        for unit_type1 in UnitType.values():
            unit = fighter.get_round()[round_idx][unit_type1].get_nb_unit()

            for unit_type2 in UnitType.values():
                dead_unit = opponent.get_round()[round_idx][unit_type2].get_round_details()[unit_type1].get_dead()
                if unit < dead_unit:
                    dead_unit = unit
                    opponent.get_round()[round_idx][unit_type2].get_round_details()[unit_type1].set_dead(dead_unit)
                    if dead_unit == 0:
                        opponent.get_round()[round_idx][unit_type2].get_round_details()[unit_type1].set_damage(0)
                unit -= dead_unit

            total_unit += unit
            fighter.get_round()[round_idx][unit_type1].set_nb_unit(unit)

        return total_unit == 0

    def _round(self, fighter, opponent, army_min, round_idx):
        line = {}
        fighter.get_round().append(line)

        for unit_type in UnitType.values():
            round_unit = RoundUnit()
            line[unit_type] = round_unit
            self._unit_round(unit_type, fighter, opponent, army_min, round_idx, round_unit)

    def _unit_round(self, unit_type, fighter, opponent, army_min, round_idx, round_unit):
        if round_idx == 0:
            nb = fighter.get_troops_by_type().get(unit_type, 0)
            round_unit.set_nb_unit(nb)
            round_unit.set_round(round_idx)
            for vs in UnitType.values():
                round_unit.get_round_details()[vs] = RoundDetail()
        else:
            round_prev = fighter.get_round()[round_idx - 1][unit_type]
            nb_unit = round_prev.get_nb_unit()
            round_unit.set_nb_unit(nb_unit)
            round_unit.set_round(round_idx)
            continue_battle = True

            types = UnitType.values()
            if round_idx % 20 == 0:
                if unit_type == UnitType.CAVALRY and fighter.has_bikers():
                    types = [UnitType.RANGED, UnitType.INFANTRY, UnitType.CAVALRY]
                if unit_type == UnitType.RANGED and fighter.has_snipers():
                    types = [UnitType.CAVALRY, UnitType.INFANTRY, UnitType.RANGED]

            for vs in types:
                round_detail = RoundDetail()
                round_unit.get_round_details()[vs] = round_detail

                army = (nb_unit ** 0.5) * (army_min ** 0.5)

                if continue_battle and opponent.get_defense_by_type().get(vs, 0) > 0 and army > 0 and \
                        opponent.get_round()[round_idx - 1][vs].get_nb_unit() > 0:

                    attack = fighter.get_attack_by_type().get(unit_type, 0)
                    defense = opponent.get_defense_by_type().get(vs, 0)

                    coef_attack = Skill.damage(fighter, unit_type, vs, round_idx)
                    coef_defense = Skill.defense(opponent, vs, unit_type, round_idx)

                    attack *= coef_attack
                    defense = defense / (1 - coef_defense)

                    dead = self.calc_dead(round_idx, army, attack, defense)
                    protect = Skill.protect(opponent, unit_type, vs, round_idx, dead)
                    if dead > 0:
                        attack *= (dead - protect) / dead

                    round_detail.set_dead(self.calc_dead(round_idx, army, attack, defense))
                    round_detail.set_damage(army * attack * (1 - coef_defense))
                    continue_battle = Skill.need_continue(fighter, unit_type, vs, round_idx)

    def calc_dead(self, round_idx, army, attack, defense):
        dead_value = army * attack / defense / 100.0
        dead_value = dead_value - dead_value * 0.0001 * round_idx
        return int(-(-dead_value // 1))  # ceil without math.ceil

    def get_attacker(self):
        return self.attacker

    def get_attacked(self):
        return self.attacked

    def get_battle_type(self):
        return self.battle_type

    def set_battle_type(self, battle_type):
        self.battle_type = battle_type

    def get_result(self, is_attacker=True):
        return self.attacker.get_result() if is_attacker else self.attacked.get_result()

    def get_result_all(self):
        ret = []
        total = {}
        ret.append(total)
        r1 = self.attacker.get_result()
        ret.append(r1)
        r2 = self.attacked.get_result()
        ret.append(r2)

        total["success"] = r1["end"] > 0
        score = (r1["end"] / r1["start"]) if r1["end"] > 0 else -(r2["end"] / r2["start"])
        total["score"] = score
        return ret

    def get_stats(self):
        ret = []
        seen = set()

        for boost in self.attacker.get_used_boost().keys():
            stat = {
                "stat": boost,
                "attacker": self.attacker.get_used_boost().get(boost),
                "attacked": self.attacked.get_used_boost().get(boost),
            }
            ret.append(stat)
            seen.add(boost)

        for boost in self.attacked.get_used_boost().keys():
            if boost not in seen:
                stat = {
                    "stat": boost,
                    "attacker": self.attacker.get_used_boost().get(boost),
                    "attacked": self.attacked.get_used_boost().get(boost),
                }
                ret.append(stat)

        return sorted(ret, key=lambda x: x["stat"])
