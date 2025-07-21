import json
import csv

skills_dict = {}

skill_keys = [
    'skill_hero',
    'skill_num',
    'skill_name',
    'skill_description',
    'skill_troop_type',
    'skill_permanent',
    'skill_is_chance',
    'skill_probability',
    'skill_round_stackable',
    'skill_type_relation',
    'skill_order'
    ]

effect_keys = [
    #'effect_num',
    'affects_opponent',
    # 'for_unit_type',
    # 'vs_unit_unit',
    'effect_type',
    'effect_op',
    'extra_attack',
    # 'effect_lag',
    'effect_is_chance',
    #'proba_1','proba_2','proba_3','proba_4','proba_5',
    #'effect_1','effect_2','effect_3','effect_4','effect_5',
    # 'special'
]

def convert_value(v):
    if v.upper() == "TRUE": return True
    if v.upper() == "FALSE": return False
    if v.upper() in ["NONE","-"]: return None
    try:
        if ',' not in v: return int(v)
        return float(v.replace(',','.'))
    except:
        pass
    if v[-1:] == ' ': return v[:-1]
    return v

def make_hero_dicts(csv_file_path = 'skills/Fitz_hero_skills.csv', export_dicts_path = "assets/hero_skills/"):

    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            # print(row)
            # exit()
            hero_name = convert_value(row['skill_hero']).lower().capitalize()
            if hero_name not in skills_dict:
                skills_dict[hero_name] = []
                # print(skills_dict)
            if convert_value(row['skill_name']) not in [s['skill_name'] for s in skills_dict[hero_name]]:
                sk = {k: convert_value(row[k]) for k in skill_keys}
                sk['skill_type'] = "hero_skill"
                sk['skill_frequency'] = {
                    'frequency_type': convert_value(row['skill_frequency_type']),
                    'frequency_value': convert_value(row['skill_frequency'])
                }
                if convert_value(row['skill_first_round']) : sk['skill_frequency']['skill_first_round'] = convert_value(row['skill_first_round'])
                if convert_value(row['skill_last_round']) : sk['skill_frequency']['skill_last_round'] = convert_value(row['skill_last_round'])

                sk['skill_effects'] = []
                skills_dict[hero_name].append(sk)
            
            _effect = {k: convert_value(row[k]) for k in effect_keys}

            _effect['effect_num'] = convert_value(row['skill_name']) + '/' + str(convert_value(row['effect_num']))

            _effect['trigger_types'] = {
                'trigger_for': convert_value(row['trig_by_unit']),
                'trigger_vs': convert_value(row['trig_vs_unit']),
            }

            _effect['benefit_types'] = {
                'benefit_for': convert_value(row['benefit_for_unit']),
                'benefit_vs': convert_value(row['benefit_vs_unit']),
            }

            _effect['effect_duration'] = {
                    'duration_type': convert_value(row['effect_duration_type']),
                    'duration_value': convert_value(row['effect_duration']),
                    'effect_lag': convert_value(row['effect_lag'])
                }

            _effect['effect_probabilities'] = {}
            if int(row['proba_1']):
                for i in range(1,6):
                    _effect['effect_probabilities'][i] = convert_value(row['proba_' + str(i)])

            _effect['effect_values'] = {}
            if int(row['effect_1']):
                for i in range(1,6):
                    _effect['effect_values'][i] = convert_value(row['effect_' + str(i)])
            
            _effect['special'] = {}
            if convert_value(row['special']):
                # print('Special:', row['special'])
                _effect['special'] = json.loads(row['special'])

            skills_dict[hero_name][-1]['skill_effects'].append(_effect)

    # print(json.dumps(skills_dict['Gwen'], indent=4))

    for hero in skills_dict.keys():
        with open(export_dicts_path + hero + ".json", "w+") as f:
            json.dump(skills_dict[hero], f, indent= 4)

if __name__ == '__main__':
    
    csv_file_path = 'skills/Fitz_hero_skills.csv'
    export_dicts_path = "assets/hero_skills/"

    make_hero_dicts(csv_file_path, export_dicts_path)