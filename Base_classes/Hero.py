from Base_classes.JsonUtil import JsonUtil

class Hero:
    registry = JsonUtil.hero_registery

    @staticmethod
    def get_heroes_skill_levels(_heroes_dict, fighter_name, _joiners = False):
        if _joiners :
            if len(_heroes_dict) > 4:
                print(f"⚠️  Error:  only use 4 joiners !")
                exit() 
        else:
            if len(_heroes_dict) > 3:
                print(f"⚠️  Error:  only use 3 heroes !")
                exit() 
        skills_levels_dict = {}
        types = []
        for hero_n in _heroes_dict:
            hero = hero_n.lower().capitalize()
            if hero not in Hero.registry:
                print(f"⚠️  Error:  Hero named '{hero}' not found !")
                exit()
            if (not _joiners) and (hero in skills_levels_dict.keys()):
                print(f"⚠️  Error:  Hero '{hero}' was used twice !")
                exit()
            if not _joiners:
                _type = Hero.registry[hero][0]['skill_troop_type'].lower()[:4]
                if _type in types:
                    print(f"⚠️  Error:  You used 2 heroes of same type: {_type} !")
                    exit()
                types.append(_type)
            skills_levels_dict[hero] = Hero._hero_skill_level(hero, fighter_name, {} if isinstance(_heroes_dict, list) else _heroes_dict[hero_n], _joiners)
        return skills_levels_dict

    @staticmethod
    def _hero_skill_level(hero_name: str, fighter_name, hero_skill_levels: dict = {}, _joiner = False):
        h_skill_nums = [s['skill_num'] for s in Hero.registry[hero_name]]
        if (not hero_skill_levels) and fighter_name and (fighter_name in JsonUtil.fighter_heroes):
            for hero in JsonUtil.fighter_heroes[fighter_name]:
                if hero.lower() in hero_name.lower():
                    if 'skill_levels' in JsonUtil.fighter_heroes[fighter_name][hero]: 
                        hero_skill_levels = JsonUtil.fighter_heroes[fighter_name][hero]['skill_levels']
        return Hero._get_levels(hero_skill_levels, h_skill_nums, hero_name, _joiner=_joiner)

    @staticmethod
    def _get_levels(hero_skill_levels, h_skill_nums, hero_name, _joiner):
        if not hero_skill_levels:
            return {"skill_1":5} if _joiner else {f"skill_{num}":5 for num in h_skill_nums}
        
        skill_levels = {}
        for s_num_str, s_level in hero_skill_levels.items():
            _num = s_num_str.split('_')[1]
            if (not _num.isdigit()) or int(_num) > 3 or int(_num) < 1 or (not isinstance(s_level, int)) or s_level < 0 or s_level > 5:
                print(f"⚠️  Error (for hero : {hero_name}): skill levels should specified in the format: 'skill_X_level' : Y ")
                print(f"                               X: skill number, Y: skill level (both integers) ")
                exit()
            _num = int(_num)
            if _num not in h_skill_nums:
                print(f"⚠️  Error : hero '{hero_name}' doesn't have a 'skill_{_num}' !")
                exit()
            if _joiner and _num != 1: continue
            if s_level > 0: skill_levels[f"skill_{_num}"] = s_level
        return skill_levels

        
if __name__ == "__main__":
    # # heroes = {
    # #     "Jessie" : {
    # #         "skill_1_level": 5,
    # #         "skill_2_level": 4,
    # #     },
    # #     "Jasser" : {
    # #         "skill_1_level": 5,
    # #     },
    # #     "Zinman" : {
    # #         "skill_1_level": 5,
    # #         "skill_2_level": 4,
    # #     }
    # # }

    # # print(Hero.get_heroes_skill_levels(heroes))
    pass