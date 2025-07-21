# Ryo's WOS Battle simulator

---

This is still a work in progress.
The simulator does not support FC troops yet. FC troops skills will be added soon.
Only the heroes and attributes in green in [Fitz Hero Skill Spreadsheet](https://docs.google.com/spreadsheets/d/1q-i8auhNUcwU6-eUGvqGdJ4Xf2yswV6oo6z-KG1RJMQ) have been tested (limited testing for now).
Feel free to test and give feedback.

# HOW TO USE

1. Edit `fighters_data\fighter_stats.json` to add your accounts bonus stats from a battle report
2. You can add heroes stats and skill levels in `fighters_data\fighters_heroes.json` (if the hero stats are not included in the previous step stats)
3. Edit fighters names, troops, heroes and joiner_heroes in `main.py`
4. You can change `BattleRound.DEBUG` and `show_rounds_freq` in `main.py` to show rounds and more details
5. run `main.py`
6. You can print the round report using `f.format_report()`
7. You can save a testcase using `f.save_testcase(testcase_file_path, result)`, by specifying the result from the actual game reports.

# Stats

Add your accounts stats to `fighters_data\fighter_stats.json`.
You can add stats from a battle report (A report from a beast attack without heroes works). BUT, for more precision (since battle report only show 1 digit) it's better if you calculate them from Bonus Overview Section (click the Power next to your PFP). For example, for infantry Attack, sum the following :

-   Troops Attack (from Bonus Overview section)
-   Infantry Attack (from Bonus Overview section)
    Also, you need to add:
-   Natalia's special bonus for Attack/defense (for example: +10% at 5 stars) ;
-   Jeronimo's special bonus for Lethality/Health (for example: +15% at 5 stars) ;

Add your heroes stats to `fighters_data\fighters_heroes.json` (Hero overall stats in Stats tab of each hero). Might as well add hero skill levels.
When using heroes, you then can simply specify the heroes names and the simulator will calculate the total bonus stats by adding fighters stats and heroes stats.
Be careful when you're saving testcases, make sure your stats didn't change (Buffs, Facilities, Research, Hero upgrades, etc). If they changed, you need to update them in `fighters_data`.

# Troops

You can specify the troops in the format `infantry_t7_fc2` (FC skills not yet supported but will be soon).

# Heroes and Joiner heroes

Heroes and Joiner_heroes could be specified in one of the two following formats:

1. `{'Jessie': { 'skill_1_level': 1, 'skill_2_level': 0 } }`
   If level specified is 0, the skill is skipped.

2. OR `['Jessie', 'Jasser', 'molly']`
   If this format is used, skill levels will be fetched in `fighters_data\fighters_heroes.json`. If not found, they will be considered at level 5 (only first skill for hero_joiners).

You can use `attacker.add_heroes_stats()` to add the specified heroes bonus stats (if they are not included already in `fighters_data\fighter_stats.json`).

# Skills

Improving the simulator accuracy means finding the correct attributes for the different hero and troop skills.

-   All hero skills attributes are summarized in one spreadsheet called 'Fitz_hero_skills.csv'.
-   Access the latest update of skills registery here: [Fitz Hero Skill Spreadsheet](https://docs.google.com/spreadsheets/d/1q-i8auhNUcwU6-eUGvqGdJ4Xf2yswV6oo6z-KG1RJMQ)
-   Save the spreadsheet in csv format in the `skills` folder.
-   run `skills/export_hero_skills_dicts.py` to export hero dicts from the csv file to assets folder.
-   Feel free to modify the hero skills attributes for testing, and share feedback with us.

# Testcases

The last battle report is always saved in `last_battle_report.json`

It's recommended to save the testcases reports by specifying the actual result from the game report of the battle using `f.save_testcase(testcase_file_path, result)` in `main.py`.
If you run `check_testcases.py`, it will re-run all battles in the specified files in `testcases` folder, and check the difference to actual game report results.
This is helpful if you intend to make changes to the skills data or the simulator logic. It allows you to make sure the simulator still works for previous testcases.

For testcases with chance skills, it's recommended to run multiple battles in the game with the same squads, and the different results in the testcase list `game_report_result`.

When using `check_testcases.py`:

-   You can specify the path to the testcases file or set it to 'all' to check all files in `testcases` folder
-   You can run simulations multiple times for each testcase by specifying `repeat`. This is recommeneded for chance skills. The simulation will not be repeated for files ending with `_nc` (not chance).
-   If a testcase dict contains a list of results in `game_report_result`, the average of these results will be considered for comparing against the simulations.
-   When repeating, if `combine_repeats = True` then the average result of the repeated simulation will be printed for each testcase, otherwise it will print individual repeated simulation result up to `max_show`.

# CREDITS

This is being made with the help of:

-   Expert nerds from [WOS Nerds Discord server](https://discord.gg/BW288dNExX)
-   Members from [HIT Alliance in State 1589](https://discord.gg/X6wpn7j3cC)
-   [SOS Simulator](https://github.com/request-laurent/sos.battle) by Request-Laurent

Programming is not my profession, so the code for this simulator might look ugly to some people lol
But I'm hoping that, with your help, we can at least make it an accuate and reliable simulator

[1589] HIT-Ryo
