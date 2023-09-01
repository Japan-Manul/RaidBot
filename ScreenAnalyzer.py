import cv2
from time import sleep
import pyautogui


def compare_with_template(image_path,template_path,x,y,w,h):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cropped_image = image[y:y + h, x:x + w]
    template = cv2.imread(template_path)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(cropped_image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return {'max_val' : max_val, 'max_loc' : max_loc}

def check_faction(image_path):
    factions = ['Lunatics','FireStarters','Nomads','DawnsChildren','Scavengers','Steppenwolfs']
    max_max_val = -1
    max_faction = ''
    for faction in factions:
        result = compare_with_template(image_path,f'Templates/Factions/{faction}.jpg',1841, 174, 60, 60)
        if result['max_val'] > max_max_val:
            max_max_val = result['max_val']
            max_faction = faction
    return max_faction, max_max_val

def check_raid(image_path):
    raids = ['DataTheft','FrontierDefense','GoneInTwoMinutes','HitAndRun','PerimeterBreach','SteelCradle','TheLastConvoy','TheWarForFire']
    max_max_val = -1
    max_raid = ''
    for raid in raids:
        result = compare_with_template(image_path,f'Templates/Raids/{raid}.jpg',1457, 169, 60, 60)
        if result['max_val'] > max_max_val:
            max_max_val = result['max_val']
            max_raid = raid
    return max_raid, max_max_val

def check_map(image_path, raid):
    map_raid_dict = {'DataTheft': ('Bridge', 'Powerplant', 'OldTown', 'ChemicalPlant', 'WrathOfKhan', 'ShipGraveyard', 'FoundersCanyon', 'RockCity'),    #8
                     'FrontierDefense': ('Bridge', 'ChemicalPlant', 'Crater', 'Fortress', 'ShipGraveyard', 'RockCity'),                                  #6
                     'GoneInTwoMinutes': ('CursedMines', 'DeadHighway', 'EasternArray'),                                                                 #3
                     'HitAndRun': ('CursedMines', 'DeadHighway', 'EasternArray'),                                                                        #3
                     'TheLastConvoy': ('CursedMines', 'DeadHighway', 'EasternArray'),                                                                    #3
                     'PerimeterBreach': ('LostCoast', 'Terminal45'),                                                                                     #2
                     'SteelCradle': ('ChemicalPlant', 'Factory', 'WrathOfKhan', 'ShipGraveyard'),                                                        #4
                     'TheWarForFire': ('Bridge', 'Powerplant', 'OldTown', 'ChemicalPlant', 'WrathOfKhan', 'ShipGraveyard', 'FoundersCanyon', 'RockCity')}#8
    max_max_val = -1
    max_map = ''
    for map in map_raid_dict[raid]:
        result = compare_with_template(image_path, f'Templates/Maps/{map}.jpg', 1500, 368, 410, 60)
        if result['max_val'] > max_max_val:
            max_max_val = result['max_val']
            max_map = map
    return max_map, max_max_val

def check_screen(image_path):
    faction = check_faction(image_path)
    raid = check_raid(image_path)
    map = check_map(image_path, raid[0])
    return (raid[0],faction[0],map[0])

def analyze_cycle():
    sleep(2)
    result_dict = {}
    raids = ('Easy', 'Mid', 'Hard')

    pyautogui.click(80,430)
    sleep(1)
    pyautogui.screenshot('temp/ProcessScreenE.jpg')
    result_dict[raids[0]] = check_screen('temp/ProcessScreenE.jpg')

    pyautogui.click(620, 430)
    sleep(1)
    pyautogui.screenshot('temp/ProcessScreenM.jpg')
    result_dict[raids[1]] = check_screen('temp/ProcessScreenM.jpg')

    pyautogui.click(850, 430)
    sleep(1)
    pyautogui.screenshot('temp/ProcessScreenH.jpg')
    result_dict[raids[2]] = check_screen('temp/ProcessScreenH.jpg')

    return result_dict

def build_image(difficulty,list):
    white_canvas = cv2.imread('Images/white sample.jpg')

    raid = cv2.imread(f'Images/Raids/{list[0]} {difficulty}.jpg')
    faction = cv2.imread(f'Images/Factions/{list[1]}.jpg')
    map = cv2.imread(f'Images/Maps/{list[2]}.png')

    white_canvas[2:102, 2:414] = raid
    white_canvas[104:190, 2:326] = cv2.resize(map, dsize=[324, 86])
    white_canvas[104:190, 328:414] = faction

    cv2.imwrite(f'temp/{difficulty}.jpg', white_canvas)
    return f'temp/{difficulty}.jpg'