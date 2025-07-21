from Base_classes.Fighter import Fighter
from Base_classes.Fight import Fight
from Base_classes.BattleRound import BattleRound
from Base_classes.StatsBonus import StatsBonus
from Base_classes.UnitType import prettify
from tabulate import tabulate
import math
import json
import glob
import statistics

BattleRound.DEBUG = False

def measure_distance(sim_result, game_result, winner_init_count, ignore_one_diff):
    # SQRT(SUM-SQUARE((sim.att-game.att);(sim.def-game.def)))
    diff = math.sqrt(sum(math.pow( sim_result[key] - game_result[key] ,2) for key in ['attacker', 'defender']))
    if ignore_one_diff and diff <= 1: diff = 0
    diff_ratio = diff / winner_init_count
    return round(diff,1) , round(diff_ratio * 100,2)

def get_testcases(file_list, TESTCASES_PATH = 'testcases'):
    if file_list == "all": file_list = glob.glob(TESTCASES_PATH + '/**/*.json', recursive=True)
    else: file_list = [TESTCASES_PATH + '/' + f for f in file_list]
    
    testcases_files = {}
    for file in file_list:
        with open(file, 'r+') as f:
            _f = f.read()
            if _f: testcases_files[file] = json.loads(_f)
            else: print(f"⚠️  Attention: file '{file}' is not a proper testcases file !")
    return testcases_files

def fight_from_testcase(testcase, ignore_one_diff=False):
    # attacker
    attacker = Fighter(None, load_fighter_data=False)
    attacker.stats = StatsBonus.from_dict(testcase['attacker']['stats'])
    attacker.troops = testcase['attacker']['troops']
    attacker.heroes = testcase['attacker']['heroes']
    attacker.joiner_heroes = testcase['attacker']['joiner_heroes']

    # defender
    defender = Fighter(None, load_fighter_data=False)
    defender.stats = StatsBonus.from_dict(testcase['defender']['stats'])
    defender.troops = testcase['defender']['troops']
    defender.heroes = testcase['defender']['heroes']
    defender.joiner_heroes = testcase['defender']['joiner_heroes']

    # Fight
    f = Fight(attacker, defender, dont_save=True)
    _att, _def = f.battle(show_rounds_freq=-1)
    sim_result = {'attacker': _att, 'defender': _def}
    winner = attacker if _att else defender
    winner_init_count = winner.get_sum_army()

    if isinstance(testcase['game_report_result'], list):
        game_result = {
            'attacker': round(statistics.fmean(r['attacker'] for r in testcase['game_report_result']),2),
            'defender': round(statistics.fmean(r['defender'] for r in testcase['game_report_result']),2),
        }
    else: game_result = testcase['game_report_result']


    # Measure difference between game result and simulator result
    diff, diff_ratio = measure_distance(sim_result, game_result, winner_init_count, ignore_one_diff=ignore_one_diff)

    result = []
    result.append("_".join(x[:2] for x in testcase['test_id'].split("_")[2:]))
    result.append(prettify(attacker.troops_by_type))
    result.append(prettify(defender.troops_by_type))
    result.append('✦✦')
    result.append('/'.join(x[:] for x in attacker.heroes.keys()) or '-')
    result.append('/'.join(x[:] for x in defender.heroes.keys()) or '-')
    result.append('✦✦')
    result.append(game_result['attacker'] or '-')
    result.append(game_result['defender'] or '-')
    result.append('✦✦')
    result.append(sim_result['attacker'] or '-')
    result.append(sim_result['defender'] or '-')
    result.append('✦✦')
    result.append(diff or '-')
    result.append(diff_ratio)

    return result

def check_testcases(testcases_files, TESTCASES_PATH = 'testcases', max_diff_ratio = 0.03, repeat = 0, combine_repeats=False, max_repeat_print=5, ignore_one_diff= False):
    if combine_repeats: max_repeat_print = 0
    print(f"\n ✦✦ Max difference ratio: {max_diff_ratio * 100} %")
    testcases_files = get_testcases(testcases_files, TESTCASES_PATH = TESTCASES_PATH)
    overall_prints = []
    overall_results = []

    for file, testcases in testcases_files.items():
        file_prints = []
        file_averages = []
        print(f"\n⏩⏩⏩ File '{file}' ")
        for testcase in testcases:
            num_tests = max(repeat, 1) if file.split('.')[-2][-3:] != '_nc' else 1
            tc_results = []
            for i in range(num_tests):
                result = fight_from_testcase(testcase, ignore_one_diff=ignore_one_diff)
                file_averages.append(result[-1])
                overall_results.append(result[-1])
                result.append("✅" if result[-1] <= (max_diff_ratio * 100) else "❌")
                result[-2]= (result[-2] or '-')
                tc_results.append(result)
                if i > 0 and i >= max_repeat_print: continue
                if num_tests > 1:
                    if combine_repeats: result[0] += f'_avg'
                    else: result[0] += f'_{i}'
                if not combine_repeats or i==0: file_prints.append(result)
            if combine_repeats:
                file_prints[-1][-6] = round(statistics.fmean([(x[-6] if isinstance(x[-6], int) else 0) for x in tc_results]),1) or '-'
                file_prints[-1][-5] = round(statistics.fmean([(x[-5] if isinstance(x[-5], int) else 0) for x in tc_results]),1) or '-'
                file_prints[-1][-3] = round(statistics.fmean([(x[-3] if isinstance(x[-3], float) else 0) for x in tc_results]),1) or '-'
                tc_ratio_avg = round(statistics.fmean([(x[-2] if isinstance(x[-2], float) else 0) for x in tc_results]),2)
                file_prints[-1][-2] = tc_ratio_avg or '-'
                file_prints[-1][-1] = "✅" if tc_ratio_avg <= (max_diff_ratio * 100) else "❌"
                
            if num_tests > 1 and max_repeat_print > 0: file_prints.append(['✦'] * 16)            
        
        headers = ['Test_ID', 'Att Troops', 'Def Troops','✦✦','Att hero','Def Her','✦✦','Game Att','Game Def','✦✦','Sim Att', 'Sim Def','✦✦', 'Diff', 'Diff %', '?']
        print(tabulate(file_prints, headers=headers, tablefmt="pretty"))

        file_average = statistics.fmean(file_averages)
        print(f"✦✦ Average difference ratio: {file_average:.2f} % ","✅" if file_average <= (max_diff_ratio * 100) else "❌")
        file_name = file.split('\\')[-1].split('/')[-1].replace('.json','').replace('testcases','').replace('tc','').replace('_',' ')
        if file_name in ['',' ']: continue
        overall_prints.append([file_name, round(file_average,2), f'{"✅" if file_average <= (max_diff_ratio * 100) else "❌"}'])
    
    print("\n🔹🔹🔹  RECAP 🔹🔹🔹")
    recap_headers = ['file','Avg Error %', "✦✦"]
    print(tabulate(overall_prints, headers=recap_headers, tablefmt="fancy_grid", colalign=("left", "center", "center")))
    glob_avg = statistics.fmean(overall_results)
    print(f"🔹  Overall Average error: {glob_avg:.2f} % ","✅" if glob_avg <= (max_diff_ratio * 100) else "❌")

if __name__ == '__main__':
    
    files = "all"
    # files = ["2-testcases_no-heroes_t6_mixed_nc.json"]
    # files = ["3-testcases_mixed-heroes-not-verified.json"]
    # files = ["heroes_unittests/Flint_tc.json"]
    # files = ["heroes_unittests/Alonso_tc.json",
    #          "heroes_unittests/Jessie_tc_nc.json"]
    # files = ["heroes_unittests/Mia_tc.json", "3-testcases_mixed-heroes-not-verified.json"]

    check_testcases(files,
                    max_diff_ratio      =   0.05,
                    repeat              =   100,
                    combine_repeats     =   True,
                    max_repeat_print    =   5,
                    ignore_one_diff     =   True)
    

    # If repeat is specified, the simulation will be run that many times for each test, unless file ends with '_nc' (no chance skills). But only 'max_repeat_print' will be printed !

    # When repeating, if combine_repeats = True then the average result of repeated simulation will be printed for each testcase (max_repeat_print is ignored), 
    #    otherwise it will print individual repeated simulation results up to the specified 'max_repeat_print'
