import json
import math
from Base_classes.Fighter import Fighter
from Base_classes.UnitType import UnitType, _to_unitx, prettify
from Base_classes.Skill import Skill, Effect, RoundEffect, Benefit

class BattleRound():
    DEBUG = False
    DEBUG_FREQ = 10
    DEBUG_MAX_ROUND = 10
    def __init__(self, fighter: Fighter, opponent: Fighter, round_idx, army_min) -> None:
        # Init
        self.fighter = fighter
        self.opponent = opponent
        self.round_idx = round_idx
        self.army_min = army_min

        # prepare
        self.round_troops = {}
        self.stunned = {ut:False for ut in UnitType}
        self.targets = {}

        # effects
        self.round_effects = []
        self.order_effects = []
        self.dodge_effects = []
        # benefits
        self.round_benefits = []

        # results
        self.round_kills = {}
        self.round_dmg_coef = {ut:0 for ut in UnitType}
        # self.need_continue_skills = {}  # Not used for now

        # Calc Round troops
        self.calc_round_troops()


    def get_results(self):
        self.calc_round_kills()
        
    def calc_round_troops(self):
        # calc remaining troops by type
        if self.round_idx == 0 :
            self.round_troops = self.fighter.troops_by_type
        else :
            for ut in UnitType:
                self.round_troops[ut] = max(0, self.fighter.rounds[self.round_idx - 1].round_troops[ut] - sum(vs[ut] if ut in vs else 0 for vs in self.opponent.rounds[self.round_idx -1].round_kills.values()) )
    
    def calc_stunned(self):
        # Check if any unit is stunned for the round
        if self.round_idx < 1: return
        for ut in UnitType:
            if self.stunned[ut] : continue
            for benefit in self.opponent.rounds[self.round_idx - 1].round_benefits:
                benefit: Benefit
                if 'stun' not in benefit.benefit_type.lower(): continue
                if benefit.is_valid('any', ut, self.round_idx):
                    self.stunned[ut] = True
                    benefit.use()
                    # DEBUG
                    if BattleRound.DEBUG and self.round_idx % BattleRound.DEBUG_FREQ == 0 and self.round_idx < self.DEBUG_MAX_ROUND:
                        print(f'STUN ----> R{self.round_idx}-{self.fighter.name}- {ut.name} Stunned')
                    break
        
    def calc_skills(self) :
        self.calc_stunned()
        self.calc_round_effects()
        self.calc_targets()

    def calc_round_effects(self):
        for effect in self.fighter.effects:
            if effect._skill.r_skill_condition(self.fighter, self.round_idx):
                if effect.r_effect_condition(self.fighter, self.opponent, self.round_idx):
                    self.add_round_effect(effect)
    
    def add_round_effect(self, effect:Effect):
        # print(f'round_effect: {effect.name} activated !')
        effect.activations_count += 1
        if 'attack_order' in effect.type.lower():
            self.order_effects.append(RoundEffect(effect, self.round_idx))
        elif 'dodge' in effect.type.lower():
            self.dodge_effects.append(RoundEffect(effect, self.round_idx))
        else:
            self.round_effects.append(RoundEffect(effect, self.round_idx))
    
    def calc_targets(self):
        for ut, num in self.round_troops.items():
            if not num: continue
            self.targets[ut] = self.get_unit_target(ut)
    
    def get_unit_target(self, ut: UnitType):
        attack_order = UnitType.list()
        if ut == UnitType.lanc:                 # For simplification: lancers only. To update later if needed
            if self.order_effects:
                ## PROBABLY NOT: ## if self.stunned[ut]: continue ## To check
                if self.order_effects[-1].trigger_condition(self.fighter, self.opponent, ut, UnitType.inf, self.round_idx):
                    attack_order = [_to_unitx(_t) for _t in self.order_effects[-1]._effect.value.split('/')]
                    self.order_effects[-1]._effect.trigger_count += 1
                    self.order_effects[-1]._effect.uses_count += 1
        for vs in attack_order:
            if self.opponent.rounds[self.round_idx].round_troops[vs] > 0 : return vs
        
    def calc_benefits(self):
        defense_effects = []
        for r_effect in self.round_effects:
            r_effect : RoundEffect
            if ('onDefense' in r_effect._effect.special) and r_effect._effect.special['onDefense'] :
                defense_effects.append(r_effect)
                continue
            for ut in UnitType:
                if not self.round_troops[ut]: continue
                ## PROBABLY NOT: ## if self.stunned[ut]: continue ## To check
                target = self.targets[ut]
                if r_effect.trigger_condition(self.fighter, self.opponent, ut, target, self.round_idx):
                    benefit = r_effect.activate_effect(self.fighter, ut, target)
                    self.round_benefits.append(benefit)
        
        for r_effect in defense_effects:
            r_effect : RoundEffect
            for vs in UnitType:
                if not self.opponent.rounds[self.round_idx].round_troops[vs]: continue
                victim = self.opponent.rounds[self.round_idx].targets[vs]
                if r_effect.trigger_condition(self.fighter, self.opponent, victim, vs, self.round_idx):
                    benefit = r_effect.activate_effect(self.fighter, victim, vs)
                    # print(f"___ (R{self.round_idx}-{self.fighter.name}) DEBUG: r_effect onDefense: {r_effect.r_eff_id} ACTIVATED for my {victim.name} vs {vs.name}, defense_effects = {defense_effects}")
                    self.round_benefits.append(benefit)
        
        if self.round_idx > 0:
            for benefit in self.fighter.rounds[self.round_idx - 1].round_benefits:
                benefit: Benefit
                if benefit.is_valid("any", "any", self.round_idx):
                    self.round_benefits.append(benefit)
        
        if BattleRound.DEBUG and self.round_idx % BattleRound.DEBUG_FREQ == 0 and self.round_idx < self.DEBUG_MAX_ROUND:
            print(f'\nBENEFITS ---> R{self.round_idx} - {self.fighter.name} ')
            for benefit in self.round_benefits:
                print(f"        - {benefit}")
    
    def calc_dodging_benefits(self, ut, target):
        # DODGING_BENEFITS
        opp_dodge_effects = self.opponent.rounds[self.round_idx].dodge_effects
        if opp_dodge_effects:
            for r_effect in opp_dodge_effects:
                r_effect: RoundEffect
                if r_effect.trigger_condition(self.fighter, self.opponent, target, ut, self.round_idx):
                    self.opponent.rounds[self.round_idx].round_benefits.append(r_effect.activate_effect(self.fighter, target, ut))

    def calc_round_kills(self):
        if BattleRound.DEBUG and self.round_idx % BattleRound.DEBUG_FREQ == 0 and self.round_idx < self.DEBUG_MAX_ROUND:
            print(f"\n🔹🔹🔹🔹🔹🔹🔹🔹  R{self.round_idx} : BONUS CALCS - {self.fighter.name}")
              
        for ut in UnitType:
            # army size
            army = self.calc_round_army(ut)
            if army == 0:
                continue

            # stunned
            if self.stunned[ut]: continue

            # get Target
            target = self.targets[ut]

            # check Dodging
            self.calc_dodging_benefits(ut, target)

            # calc Unit Base Damage
            unit_base_dmg = army * self.fighter.attack_by_type[ut] / self.opponent.defense_by_type[target] / 100

            # Calc kills with bonus dmg
            ut_kills = self.calc_bonus_dmg(unit_base_dmg, ut, target)

            # Fatigue
            ut_kills = ut_kills * (1 -  0.01/100 * self.round_idx)

            ### ROUNDING: Try later. PROBABLY NOT USED !
            # ut_kills = math.ceil(ut_kills)

            # store result
            if ut_kills > 0:
                self.round_kills[ut] = { target : ut_kills }

    def calc_bonus_dmg(self, unit_base_dmg, ut: UnitType, vs: UnitType):
        if BattleRound.DEBUG and self.round_idx % BattleRound.DEBUG_FREQ == 0 and self.round_idx < self.DEBUG_MAX_ROUND:
            print(f'\n🔸🔸🔸   {ut.name} / {vs.name}     ({self.fighter.name})')
        
        attack_effects_keys = ['DamageUp', 'OppDefenseDown']
        defense_effects_keys = ['DefenseUp', 'OppDamageDown']
        all_effects_keys = attack_effects_keys  + defense_effects_keys

        bonus_effects        = {key: {} for key in all_effects_keys}
        only_normal_effects  = {key: {} for key in all_effects_keys}
        extra_attack_effects = {key: {} for key in all_effects_keys}
        
        # Fighter benefits
        for benefit in self.round_benefits:
            benefit: Benefit
            if benefit.benefit_type not in attack_effects_keys: continue
            if not benefit.is_valid(ut, vs, self.round_idx): continue 
            ben_type = benefit.benefit_type
            ben_op = benefit.op
            ben_value = benefit.correct_value(self.round_idx)

            if benefit.extra_attack:
                if ben_op not in extra_attack_effects[ben_type]: extra_attack_effects[ben_type][ben_op] = 0
                extra_attack_effects[ben_type][ben_op] += ben_value
                self.fighter.cumul_attacks[ut] += 1
                self.opponent.cumul_received_attacks[vs] += 1
                benefit._effect.extra_kills += unit_base_dmg * benefit.correct_value(self.round_idx) /100

            elif benefit.only_normal:
                if ben_op not in only_normal_effects[ben_type]: only_normal_effects[ben_type][ben_op] = 0
                only_normal_effects[ben_type][ben_op] += ben_value
            else:
                if ben_op not in bonus_effects[ben_type]: bonus_effects[ben_type][ben_op] = 0
                bonus_effects[ben_type][ben_op] += ben_value
            benefit.use()
            if BattleRound.DEBUG and self.round_idx % BattleRound.DEBUG_FREQ == 0 and self.round_idx < self.DEBUG_MAX_ROUND:
                print(f"           APPLIED: ", benefit)
                
        # Opponent benefits
        dodging = 0
        for opp_benefit in self.opponent.rounds[self.round_idx].round_benefits:
            opp_benefit: Benefit
            if not opp_benefit.is_valid(vs, ut, self.round_idx): continue
            opp_ben_type = opp_benefit.benefit_type
            if 'dodge' in opp_ben_type.lower():
                dodging = max(1 if opp_benefit.only_normal else 2, dodging)
                opp_benefit.use()
                if BattleRound.DEBUG and self.round_idx % BattleRound.DEBUG_FREQ == 0 and self.round_idx < self.DEBUG_MAX_ROUND:
                    print(f"           OPP_DODGE: ", opp_benefit)
                continue

            if opp_ben_type not in defense_effects_keys: continue
            opp_ben_op = opp_benefit.op
            opp_ben_value = opp_benefit.correct_value(self.round_idx)
            
            if opp_ben_op not in bonus_effects[opp_ben_type]: bonus_effects[opp_ben_type][opp_ben_op] = 0
            bonus_effects[opp_ben_type][opp_ben_op] += opp_ben_value
            opp_benefit.use()

            if BattleRound.DEBUG and self.round_idx % BattleRound.DEBUG_FREQ == 0 and self.round_idx < self.DEBUG_MAX_ROUND:
                print(f"           OPP_APPLIED: ", opp_benefit)
        
        base = self.calc_coef(bonus_effects)
        normal_only = self.calc_coef(only_normal_effects)
        extra = self.calc_coef(extra_attack_effects)
        
        if dodging == 2:
            coef = 0
        elif dodging == 1:
            coef = base * (extra - 1)
        elif dodging == 0:
            coef = base * (extra + normal_only - 1)

        # coef = round(coef,4)
        
        self.round_dmg_coef[ut] = coef
        if dodging < 2:
            self.fighter.cumul_attacks[ut] += 1
            self.opponent.cumul_received_attacks[vs] += 1

        # DEBUG
        if BattleRound.DEBUG and self.round_idx % BattleRound.DEBUG_FREQ == 0 and self.round_idx < self.DEBUG_MAX_ROUND:
            print(f"\n           🔶 BONUS_COEF: R{self.round_idx} - {self.fighter.name} - {ut.name} / {vs.name} :    base:{base:.3f} - extra: {extra:.3f} - normal_only:{normal_only:.3f}  ---> 🔶 coef: {coef:.3f}")
        
        return unit_base_dmg * coef
    
    def calc_coef(self, stats_dict):

        damageUp =  math.prod((1.0 + val / 100.0) for val in stats_dict['DamageUp'].values())
        oppDamageDown = math.prod((1.0 - val / 100.0) for val in stats_dict['OppDamageDown'].values())
        defenseUp = math.prod((1.0 + val / 100.0) for val in stats_dict['DefenseUp'].values())
        oppDefenseDown = math.prod((1.0 - val / 100.0) for val in stats_dict['OppDefenseDown'].values())

        # ### ORRRR :     TO BE ISOLATED AND TESTED
        # dmg_up      = 1 + sum((val / 100) for val in stats_dict['DamageUp'].values()) - sum((val / 100) for val in stats_dict['OppDamageDown'].values())
        # defense_up  = 1 + sum((val / 100) for val in stats_dict['DefenseUp'].values()) - sum((val / 100) for val in stats_dict['OppDefenseDown'].values())
        # coef = dmg_up / defense_up


        # DEBUG
        if BattleRound.DEBUG:
            pass
            # if self.round_idx % 5 == 0:
            #     print(f'------------------------------------- R{self.round_idx} - {self.fighter}')
            #     print('dmg_up:',damageUp)
            #     print('opp_dfs_up:',defenseUp)
            #     print('dmg_down:',oppDamageDown)
            #     print('opp_dfs_down:',stats_dict['OppDefenseDown'])
            #     print(math.prod([]))
    
        coef = damageUp * oppDamageDown / (defenseUp * oppDefenseDown)
        return coef


    def calc_round_army(self, ut: UnitType):
        if ut not in self.round_troops: return 0
        army = (self.round_troops[ut] ** 0.5) * (self.army_min ** 0.5)

        ##### OR 
        # # army = (self.round_troops[ut] * self.army_min) ** 0.5
        ##### MORE LOGICAL WITH PYTHON FLOATS, BUT IT HAS BEEEN PROVEN LOGIC AND WOS ARE NOT FRIENDS

        army = math.ceil(army)
        return army
            
    def total_troops(self):
        return sum(self.round_troops[ut] for ut in UnitType)
    
    def print_round_troops(self):
        return ' / '.join("{:6.0f}".format(round(self.round_troops[v],1)) for v in UnitType) 
    
    def print_round_coef(self):
        return ' / '.join("{:6.2f}".format(round(self.round_dmg_coef[v],1)) for v in UnitType)
    
