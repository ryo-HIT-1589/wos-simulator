import json
import os

class JsonUtil:
    # Load JSON assets from 'assets/' directory
    
    @staticmethod
    def _get_asset(file_name: str):
        ASSET_DIR = "assets"
        path = os.path.join(ASSET_DIR, file_name)
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Import assets
    troop_stats = _get_asset('troop_stats.json')
    troop_skills = _get_asset('troop_skills.json')

    # # Get asset by id
    # @staticmethod
    # def by_id(assets_json, key: str, val: str):
    #     for o in assets_json:
    #         v = o.get(key)
    #         if isinstance(v, str) and v == val or str(v) == val:
    #             return o
    #     return None
