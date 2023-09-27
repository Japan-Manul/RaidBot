import pyautogui
import pytesseract as ts
import cv2
from time import sleep
from difflib import SequenceMatcher

from tools import translate
from settings import config

ts.pytesseract.tesseract_cmd = config['tesseract']


def read_from_image(image_path, x, y, w, h):
    image = cv2.imread(image_path)
    cropped_image = image[y:y + h, x:x + w]
    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    ret, cropped_image = cv2.threshold(cropped_image, 55, 255, cv2.THRESH_TOZERO)
    result = ts.image_to_string(cropped_image, lang='rus')
    return result[:-1]


def similar(first_string, second_string):
    return SequenceMatcher(None, first_string, second_string).ratio()


def compare_with_template(image_path, template_path, x, y, w, h):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cropped_image = image[y:y + h, x:x + w]
    template = cv2.imread(template_path)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(cropped_image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return {'max_val': max_val, 'max_loc': max_loc}


def check_map(image_path, raid):
    if raid is None:
        return None
    map_raid_dict = {'DataTheft': (
        'Bridge', 'Powerplant', 'OldTown', 'ChemicalPlant', 'WrathOfKhan', 'ShipGraveyard', 'FoundersCanyon',
        'RockCity'),
        'FrontierDefense': ('Bridge', 'ChemicalPlant', 'Crater', 'Fortress', 'ShipGraveyard', 'RockCity'),
        'GoneInTwoMinutes': ('CursedMines', 'DeadHighway', 'EasternArray'),
        'HitAndRun': ('CursedMines', 'DeadHighway', 'EasternArray'),
        'TheLastConvoy': ('CursedMines', 'DeadHighway', 'EasternArray'),
        'PerimeterBreach': ('LostCoast', 'Terminal45'),
        'SteelCradle': ('ChemicalPlant', 'Factory', 'WrathOfKhan', 'ShipGraveyard'),
        'TheWarForFire': (
            'Bridge', 'Powerplant', 'OldTown', 'ChemicalPlant', 'WrathOfKhan', 'ShipGraveyard',
            'FoundersCanyon', 'RockCity')}
    max_max_val = -1
    max_map = ''
    result = read_from_image(image_path, 1500, 368, 410, 60)
    for _map in map_raid_dict[raid]:
        similarity = similar(result, translate(_map))
        if similarity > max_max_val:
            max_max_val = similarity
            max_map = _map
    if max_max_val < 0.65:
        return None
    return max_map


def check_raid(image_path):
    raids = ['DataTheft', 'FrontierDefense', 'GoneInTwoMinutes', 'HitAndRun', 'PerimeterBreach', 'SteelCradle',
             'TheLastConvoy', 'TheWarForFire']
    max_max_val = -1
    max_raid = ''
    result = read_from_image(image_path, 1500, 185, 330, 35)
    for raid in raids:
        similarity = similar(result, translate(raid))
        if similarity > max_max_val:
            max_max_val = similarity
            max_raid = raid
    if max_max_val < 0.65:
        return None
    return max_raid


def check_faction(image_path):
    factions = ['Lunatics', 'FireStarters', 'Nomads', 'DawnsChildren', 'Scavengers', 'Steppenwolfs']
    max_max_val = -1
    max_faction = ''
    for faction in factions:
        result = compare_with_template(image_path, f'{config["base_dir"]}/Templates/Factions/{faction}.jpg', 1841, 174, 60, 60)
        if result['max_val'] > max_max_val:
            max_max_val = result['max_val']
            max_faction = faction
    if max_max_val < 0.65:
        return None
    return max_faction


def check_screen(image_path):
    faction = check_faction(image_path)
    raid = check_raid(image_path)
    _map = check_map(image_path, raid)
    return raid, faction, _map


def analyze_cycle():
    sleep(2)
    result_dict = {}
    raids = ('Easy', 'Mid', 'Hard')

    pyautogui.click(80, 430)
    sleep(1)
    pyautogui.screenshot(f'{config["base_dir"]}/temp/ProcessScreenE.png')
    result_dict[raids[0]] = check_screen(f'{config["base_dir"]}/temp/ProcessScreenE.png')

    pyautogui.click(620, 430)
    sleep(1)
    pyautogui.screenshot(f'{config["base_dir"]}/temp/ProcessScreenM.png')
    result_dict[raids[1]] = check_screen(f'{config["base_dir"]}/temp/ProcessScreenM.png')

    pyautogui.click(850, 430)
    sleep(1)
    pyautogui.screenshot(f'{config["base_dir"]}/temp/ProcessScreenH.png')
    result_dict[raids[2]] = check_screen(f'{config["base_dir"]}/temp/ProcessScreenH.png')

    return result_dict


def build_image(difficulty, result):
    white_canvas = cv2.imread(f'{config["base_dir"]}/Images/white sample.jpg')
    error_image = cv2.imread(f'{config["base_dir"]}/Images/black sample.jpg')

    if result[0]:
        raid = cv2.imread(f'{config["base_dir"]}/Images/Raids/{result[0]} {difficulty}.jpg')
        white_canvas[2:102, 2:414] = raid
    else:
        white_canvas[2:102, 2:414] = error_image[2:102, 2:414]

    if result[1]:
        faction = cv2.imread(f'{config["base_dir"]}/Images/Factions/{result[1]}.png')
        white_canvas[104:190, 328:414] = faction
    else:
        white_canvas[104:190, 328:414] = error_image[104:190, 328:414]

    if result[2]:
        _map = cv2.imread(f'{config["base_dir"]}/Images/Maps/{result[2]}.png')
        white_canvas[104:190, 2:326] = cv2.resize(_map, dsize=[324, 86])
    else:
        white_canvas[104:190, 2:326] = error_image[104:190, 2:326]

    cv2.imwrite(f'temp/{difficulty}.png', white_canvas)
    return fr'{config["base_dir"]}/temp/{difficulty}.png'
