import json
import os

class JsonUtil:
    # Load JSON assets from assets directory
    @staticmethod
    def _get_asset(file_name: str, ASSET_DIR = "assets"):
        path = os.path.join(ASSET_DIR, file_name)
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Import assets
    troop_stats = _get_asset('troop_stats.json')
    troop_skills = _get_asset('troop_skills.json')
    # hero dicts
    hero_registery = {}
    hero_skills_dir_path = 'assets/hero_skills/'
    for file in os.listdir(hero_skills_dir_path):
        _hero_dict = _get_asset(file, ASSET_DIR= hero_skills_dir_path)
        hero_registery[_hero_dict[0]['skill_hero']] = _hero_dict
    
    fighters_stats_path = 'fighters_data/fighters_stats.json',
    fighters_heroes_path = 'fighters_data/fighters_heroes.json'
    fighter_stats = None
    fighter_heroes = None

    @classmethod
    def load_fighters_data(
        cls,
        fighters_stats_path = fighters_stats_path,
        fighters_heroes_path = fighters_heroes_path
        ):
        
        with open(fighters_stats_path, 'r+') as f:
            cls.fighter_stats = json.load(f)
        
        with open(fighters_heroes_path, 'r+') as f:
            cls.fighter_heroes = json.load(f)

    # # Get asset by id
    # @staticmethod
    # def by_id(assets_json, key: str, val: str):
    #     for o in assets_json:
    #         v = o.get(key)
    #         if isinstance(v, str) and v == val or str(v) == val:
    #             return o
    #     return None
