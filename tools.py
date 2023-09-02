from time import strftime
import sqlite3

db = sqlite3.connect('CrossDataBase.db')

def translate(word):
    ru_eng_dict = {
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
    return ru_eng_dict[word]

def write_to_log(file, event, description=None):
    if description:
        text = f'{strftime("%x %X")} | <{event}>: {description}\n'
    else:
        text = f'{strftime("%x %X")} |----<{event + ">":{"-"}{"<"}{40}}\n'
    with open(fr"logs\{file}.log", "a") as f:
        f.write(text)
        print(text)
