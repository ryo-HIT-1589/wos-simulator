import json
import os
from typing import Any, Dict, List, Optional

# Load JSON assets from 'asset/' directory
_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'asset')

def _get_asset(file_name: str) -> Any:
    path = os.path.join(_ASSET_DIR, file_name)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Preload JSON arrays
unit_stats = _get_asset('unit_stats.json')
survivor_skill_main = _get_asset('survivor_skill_main.json')
survivor_slg_skill = _get_asset('survivor_slg_skill.json')
survivor_slg_effect = _get_asset('survivor_slg_effect.json')
survivor_rank_main = _get_asset('survivor_rank_main.json')
survivors = _get_asset('survivor.json')
survivor_tag = _get_asset('survivor_tag.json')
benefits_json = _get_asset('benefits.json')
benefit_calc = _get_asset('benefit_calc.json')
survivor_equipment = _get_asset('survivor_equipment.json')
survivor_equipment_suit = _get_asset('survivor_equipment_suit.json')
survivor_equipment_group = _get_asset('survivor_equipment_group.json')
battle_wounded = _get_asset('battle_wounded.json')
survivor_skill_type = _get_asset('survivor_skill_type.json')
npc_monster = _get_asset('npc_monster.json')
itemlist = _get_asset('itemlist.json')
city_buff_main = _get_asset('city_buff_main.json')

# Utility to find a JSON object by key/value

def json_by_id(array: List[Dict], key: str, val: str) -> Optional[Dict]:
    for o in array:
        v = o.get(key)
        if isinstance(v, str) and v == val or str(v) == val:
            return o
    return None

# Converters
def _to_tier(tier: int, star: int) -> str:
    return f"T{tier}" + (f" {star}*" if star != 0 else "")

def _to_unit_name(val: str) -> str:
    if 'boss' in val:
        return 'plot_gallery_hunter_prey_subtitle_2'
    if 'infantry' in val:
        return 'troop_type_infantry_name'
    if 'ranged' in val:
        return 'troop_type_ranged_name'
    if 'cavalry' in val:
        return 'troop_type_cavalry_name'
    return 'troop_type_infantry_name'

# Data functions
def units() -> List[Dict]:
    lst = []
    for ju in unit_stats:
        unit = {
            'id': ju['InternalId'],
            'name': _to_unit_name(ju['Id']),
            'tier': _to_tier(ju['Tier'], ju['UnlockStar'])
        }
        lst.append(unit)
    return sorted(lst, key=lambda x: x['name'], reverse=True)


def heros() -> List[Dict]:
    lst = []
    for ju in survivor_rank_main:
        survivor = json_by_id(survivors, 'InternalId', str(ju['SurvivorType']))
        if not survivor:
            continue
        if survivor.get('WhatWeek', 0) >= 30:
            continue
        rank = f"{ju['Rank']}.{ju['RankSmall'] + 1}"
        unit = {
            'id': ju['InternalId'],
            'hero': survivor['InternalId'],
            'name': survivor['Name'],
            'profession': survivor['Profession'],
            'rank': rank,
            'rankName': f"survivor_rank_{rank.replace('.', '_')}",
            'image': f"img/{survivor['ImageSmall']}.png"
        }
        lst.append(unit)
    return sorted(lst, key=lambda x: x['name'] + x['rank'])


def skills() -> List[Dict]:
    lst = []
    for survivor in survivors:
        skill_config = survivor.get('SkillConfig', {})
        for key, config_no in skill_config.items():
            skill_type = json_by_id(survivor_skill_type, 'InternalId', key)
            if not skill_type or skill_type.get('Type') != 1:
                continue
            for skill_main in survivor_skill_main:
                if skill_main['SkillType'] == int(key):
                    lst.append({
                        'id': skill_main['InternalId'],
                        'name': skill_type['Name'],
                        'hero': survivor['InternalId'],
                        'lvl': skill_main['Level'],
                        'image': f"img/{skill_type['Icon']}.png",
                        'skillNo': config_no
                    })
    return sorted(lst, key=lambda x: x['lvl'])


def equipment() -> List[Dict]:
    lst = []
    for ju in survivor_equipment:
        eq_group = json_by_id(survivor_equipment_group, 'InternalId', str(ju['SurvivorEquipmentGroupNew']))
        if not eq_group:
            continue
        lst.append({
            'id': ju['InternalId'],
            'name': eq_group['EquipmentName'],
            'profession': eq_group['Profession'],
            'part': eq_group['Part'],
            'lvl': f"{eq_group['SurvivorEquipmentGroupLevel']}.{ju['Star']}",
            'image': f"img/{ju['Icon']}.png"
        })
    return sorted(lst, key=lambda x: x['name'] + x['lvl'])


def benefits() -> List[Dict]:
    return [{'id': b['InternalId'], 'name': b['LocKey']} for b in benefits_json]


def npc_monster_fighter(monster_id: int) -> 'SimulationFighter':
    # Placeholder: SimulationFighter must be implemented separately
    from simulator import SimulationFighter, SimulationTroop
    fighter = SimulationFighter()
    json_obj = json_by_id(npc_monster, 'InternalId', str(monster_id))
    if not json_obj:
        return fighter
    fighter.set_monster(True)
    fighter.set_stats_included(False)
    for b in json_obj.get('Benefit', []):
        fighter.get_boost()[b['benefit_id']] = b['benefit_value']
    for key, count in json_obj.get('Troops', {}).items():
        fighter.get_troops().append(SimulationTroop(int(key), count))
    return fighter


def template_npc() -> List[Dict]:
    lst = []
    for npc in npc_monster:
        nid = npc['Id']
        name = None
        lvl = None
        if 'world_monster_' in nid:
            name = 'id_wildness_infected'
            lvl = nid.replace('world_monster_', '')
        elif 'npc_monster_alliance_boss_' in nid:
            name = 'id_alliance_portal'
            parts = nid.replace('npc_monster_alliance_boss_', '').split('_')
            lvl = str((int(parts[0]) - 1) * 6 + int(parts[1]))
        elif 'npc_monster_gve_boss_' in nid:
            name = 'id_gve_camp'
            lvl = nid.replace('npc_monster_gve_boss_', '')
        if name:
            lst.append({'id': npc['InternalId'], 'name': name, 'type': 'npc', 'lvl': lvl})
    return lst

_extra_benefits = {300433, 300088, 300086, 300434, 300435, 300421,
                   300409, 300412, 300410, 300417, 300436, 300416,
                   300423, 300411, 300415, 300418, 300360, 300422, 300424}

def buff() -> List[Dict]:
    return [
        {'id': b['InternalId'], 'name': b['LocKey'], 'value': None}
        for b in benefits_json
        if b['InternalId'] in _extra_benefits
    ]
