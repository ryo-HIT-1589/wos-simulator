import math
from Base_classes.UnitType import UnitType, _to_unitx, prettify, very_prettify
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
        self.need_continue_skills = {}

        # Calc Round troops
        self.calc_round_troops()

    def get_results(self):
        self.calc_round_kills()

    def calc_round_troops(self):
        # calc remaining troops by type
        # RO-DO: Verify that skills work like stamps. If not? keep troop separated by ids?!
            if self.round_idx == 0 :
                self.round_troops = self.fighter.troops_by_type
            else :
                for ut in UnitType:
                    self.round_troops[ut] = max(0, self.fighter.rounds[self.round_idx - 1].round_troops[ut] - sum(vs[ut] if ut in vs else 0 for vs in self.opponent.rounds[self.round_idx -1].round_kills.values()))
    
    def calc_skills(self) :
        for skill in self.fighter.skills :
            if skill._activate_condition(self.fighter, self.opponent, self.round_idx) :
                self.round_skills.append(RoundSkill(skill, self.round_idx))
                skill.activations_count += 1
                skill.last_round = self.round_idx
                for _effect in skill.skill_effects:
                    if _effect['effect_type'] == 'attack_order':
                        self.order_skills_index.append(len(self.round_skills) - 1)
                    if _effect['effect_type'] == 'dodge':
                        self.dodge_skills_index.append(len(self.round_skills) - 1)
                    if _effect['effect_type'] == 'stun':
                        self.stun_skills_index.append(len(self.round_skills) - 1)


    def calc_round_kills(self):
        for ut in UnitType :
            army = self.calc_round_army(ut)
            # print("army:", army)
            if army == 0:
                continue

            target : UnitType = self.get_round_target(ut)
            
            # Special Skills :
            if self.dodge_skills_index or self.stun_skills_index :
                pass
            
            # Stats Skills
            # ATTACK 
            #   Attack up               : * (1 + Coef)  --> fighter_skill
            #   Op Attack down          : * (1 - Coef)  --> opponent_skill
            # OPPPONENT DEFENSE
            #   Defense Up of Op        : / (1 - Coef)  --> opponent_skill
            #   Op defense down of Op   : / (1 + Coef)  --> fighter_skill

            att_coef = 1
            def_coef = 1
            
            # kills
            ut_kills = army * self.fighter.attack_by_type[ut] * att_coef / (self.opponent.defense_by_type[target] / def_coef) / 100

            # Fatigue
            ut_kills = ut_kills * (1 -  0.01/100 * self.round_idx)

            ### ROUNDING
            # ut_kills = math.ceil(ut_kills)

            # store
            if ut_kills > 0:
                self.round_kills[ut] = { target : ut_kills }
        # print("Round kills: ", very_prettify(self.round_kills))

    def calc_round_army(self, ut: UnitType):
        if ut not in self.round_troops: return 0
        army = (self.round_troops[ut] ** 0.5) * (self.army_min ** 0.5)
        # OR # army = (self.round_troops[ut] * self.army_min) ** 0.5
        army = math.ceil(army)
        return army
    
    def get_round_target(self, ut):
        attack_order = UnitType.list()
        
        if ut == UnitType.lanc:
            order_effect = self.has_order_skill()
            if order_effect :
                attack_order = [_to_unitx(_t) for _t in order_effect.split('/')]
        
        for vs in attack_order:
            if self.opponent.rounds[self.round_idx].round_troops[vs] > 0 : return vs

    def has_order_skill(self):
        if self.order_skills_index :
            for effect in self.round_skills[self.order_skills_index[0]]._skill.skill_effects:
                if effect['effect_type'] == 'attack_order':
                    self.round_skills[self.order_skills_index[0]]._apply()  # Skill applied
                    return effect['effect_values'][1]
        return None
        
    def total_troops(self):
        return sum(self.round_troops[ut] for ut in UnitType)
    
    def str_start_troops(self):
        return f"{self.round_troops[UnitType.inf]:,.1f} / {self.round_troops[UnitType.lanc]:,.1f} / {self.round_troops[UnitType.mark]:,.1f}"