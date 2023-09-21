import sqlite3
from time import strftime

from settings import config

db = sqlite3.connect(f'{config["base_dir"]}/CrossDataBase.db')


def translate(word):
    eng_ru_dict = {
        'Easy': 'Лёгкий',
        'Mid': 'Средний',
        'Hard': 'Тяжёлый',
        'DawnsChildren': 'Дети Рассвета',
        'FireStarters': 'Огнепоклонники',
        'Lunatics': 'Бешеные',
        'Nomads': 'Скитальцы',
        'Scavengers': 'Мусорщики',
        'Steppenwolfs': 'Степные волки',
        'Bridge': 'Мост',
        'ChemicalPlant': 'Химический завод',
        'Crater': 'Кратер',
        'CursedMines': 'Чертовы рудники',
        'DeadHighway': 'Мертвое шоссе',
        'EasternArray': 'Восточный ретранслятор',
        'Factory': 'Фабрика',
        'Fortress': 'Крепость',
        'FoundersCanyon': 'Каньон основателей',
        'LostCoast': 'Затерянный берег',
        'OldTown': 'Старый город',
        'Powerplant': 'ТЭЦ',
        'RockCity': 'Рок-Сити',
        'ShipGraveyard': 'Кладбище кораблей',
        'Terminal45': 'Терминал-45',
        'WrathOfKhan': 'Гнев Хана',
        'DataTheft': 'Похищение данных',
        'FrontierDefense': 'Оборона рубежа',
        'GoneInTwoMinutes': 'Угнать за пару минут',
        'HitAndRun': 'Бей и беги',
        'PerimeterBreach': 'Прорыв периметра',
        'SteelCradle': 'Стальная колыбель',
        'TheLastConvoy': 'Последний конвой',
        'TheWarForFire': 'Война за огонь'}
    return eng_ru_dict.get(word, word)


def write_to_log(file, event, description=None):
    if description:
        text = f'{strftime("%x %X")} | <{event}>: {description}\n'
    else:
        text = f'{strftime("%x %X")} |----<{event + ">":{"-"}{"<"}{40}}\n'
    with open(fr"logs\{file}.log", "a") as f:
        f.write(text)
        print(text)


def all_options(mode):
    options = {
        'GoneInTwoMinutes': '%CursedMines$DeadHighway$EasternArray$',
        'HitAndRun': '%CursedMines$DeadHighway$EasternArray$',
        'TheLastConvoy': '%CursedMines$DeadHighway$EasternArray$',
        'DataTheft': '%Bridge$Powerplant$OldTown$ChemicalPlant$WrathOfKhan$ShipGraveyard$FoundersCanyon$RockCity$',
        'TheWarForFire': '%Bridge$Powerplant$OldTown$ChemicalPlant$WrathOfKhan$ShipGraveyard$FoundersCanyon$RockCity$',
        'FrontierDefense': '%Bridge$ChemicalPlant$Crater$Fortress$ShipGraveyard$RockCity$',
        'PerimeterBreach': '%LostCoast$Terminal45$',
        'SteelCradle': '%ChemicalPlant$Factory$WrathOfKhan$ShipGraveyard$',
        'Easy': '%Lunatics$Nomads$Scavengers',
        'Mid': '%Lunatics$FireStarters$Nomads$DawnsChildren$Scavengers$Steppenwolfs$',
        'Hard': '%Lunatics$FireStarters$Nomads$DawnsChildren$Scavengers$Steppenwolfs$'
    }

    return options.get(mode, '%')
