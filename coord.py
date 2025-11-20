from image import *
from board_new import *

base = None

adj_x = -150
adj_y = 180

gap_x = 60
gap_y = 60

def coord(x, y):
    x, y = get_coord(x, y)
    if x and y:
        pyautogui.click((x, y))

def get_coord(x, y):
    global base
    if base is None:
        i, found = 0, False
        while i < 5 and found == False:
            normal_ai_coords = normal_ai.find()
            if normal_ai_coords:
                base = normal_ai_coords[0] + adj_x, normal_ai_coords[1] + adj_y
                found = True
            sleep(0.1)
            i += 1
    if base:
        x = base[0] + x * gap_x
        y = base[1] + y * gap_y
        return x, y

def set_coord(x,y):
    x1, y1 = get_coord(x, y)
    result = pyautogui.pixel(x1, y1)
    if result[0] > 150:
        result_text = "hit"
    else:
        result_text = "miss"
    main.board[y][x] = result_text
    print("Set coord", x, y, result_text)

    return

def set_coords(shots):
    for shot in shots:
        y, x = shot
        set_coord(x, y)
        sleep(0.1)

def fire_shots(shots, shoot=True):
    shots = list(shots)
    print("Fire shots:", shots)
    count, firing = 0, True
    while firing and count < 10:
        if count < len(shots):
            result = shots[count]
            if result:
                y, x = result
                coord(x, y)
                sleep(0.1)
        if fire.find():
            firing = False
            if shoot:
                fire.click()
            sleep(2)
        count += 1

def get_result(colours):
    r, g, b = colours
    result = "b", "sunk"
    if r > 5: result = " ", "empty"
    if r > 50: result = "X", "miss"
    if r > 150: result = "H", "hit"
    return result

def read_board():
    for y in range(10):
        # text = ""
        for x in range(10):
            coord = get_coord(x, y)
            colours = get_rgb(coord)
            result = get_result(colours)
            main.board[y][x] = result[1]

