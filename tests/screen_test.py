from os import listdir
from settings import config


def screen_test(function):
    results = (
            ('PerimeterBreach', 'Lunatics', 'Terminal45'),
            ('SteelCradle', 'Scavengers', 'Factory'),
            ('FrontierDefense', 'Lunatics', 'Crater'),
            ('PerimeterBreach', 'DawnsChildren', 'Terminal45'),
            ('DataTheft', 'Lunatics', 'RockCity'),
            ('HitAndRun', 'DawnsChildren', 'DeadHighway'),
            ('SteelCradle', 'Steppenwolfs', 'Factory'),
            ('TheWarForFire', 'Lunatics', 'OldTown'),
            ('DataTheft', 'Steppenwolfs', 'Bridge'),
            ('SteelCradle', 'Nomads', 'ChemicalPlant'),
            ('DataTheft', 'DawnsChildren', 'Powerplant'),
               )
    test_dir = fr'{config["base_dir"]}\tests\screens'
    tests = listdir(test_dir)
    for filename, i in zip(tests, range(len(tests))):
        path = fr'{test_dir}\{filename}'
        assert (result := function(path)) == results[i], (path, result, results[i])
        print(f'test {i+1} passed')


from testScreenAnalyzer import check_screen
screen_test(check_screen)
