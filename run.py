import pyautogui

from image import *
from coord import *
from board_new import *
from datetime import datetime, timedelta
from counter import *

def wait_for_next_round():
    count, found = 0, False
    while count < 100 and not found:
        sleep(0.2)
        if normal_ai.find():
            return False
        if rematch.find():
            # rematch.click()
            return True
        auto_click()
        count += 1
        # print("Wait:", count)
        if count in [99]:
            print("Blind click")
            pyautogui.click(1846, 132)
    print("Wait for next round:", found)
    return found

def check_boats():
    boats_not_sunk = []
    for boat in boats:
        if boat.find(confidence=0.9):
            boats_not_sunk.append(boat.name[0:6])

    if "boat_4" in boats_not_sunk or "boat_5" in boats_not_sunk:
        boat_size = 4
    elif "boat_1" not in boats_not_sunk:
        boat_size = 3
    else:
        boat_size = 2
    return boats_not_sunk, boat_size

def get_remaining_boats():
    remaining_boats = []
    for boat in boats:
        if boat.find(confidence=0.9):
            remaining_boats.append(boat.name[0:6])
    return remaining_boats


def finish_game(game_no=1):
    start_time = datetime.now()
    count, game_finished = 0, False
    while not game_finished and count < 40:
        remaining_boats = []
        while remaining_boats == []:
            game_finished = wait_for_next_round()
            if game_finished:
                persistent_counter()
                return count, datetime.now() - start_time
            read_board()
            remaining_boats = get_remaining_boats()
        print()
        print(f"Game: {game_no} Round: {count}")
        shots = main.get_shots(remaining_boats=remaining_boats)
        fire_shots(shots, shoot=True)
        # fire_shots(shots, shoot=False)
        count += 1

def one_round():
    read_board()
    remaining_boats = get_remaining_boats()
    shots = main.get_shots(remaining_boats=remaining_boats)
    fire_shots(shots, shoot=False)


def run(games=1):
    game_times = []
    rounds_list = []
    for x in range(1, 1 + games):
        if rematch.find():rematch.click()
        result = finish_game(x)
        if result:
            rounds, game_time = result
            game_times.append(game_time)
            rounds_list.append(rounds)
            print("\nGame times:")
            for rounds, game_time in zip(rounds_list, game_times):
                try:
                    total_seconds = game_time.total_seconds()
                    print(f"Rounds: {rounds} {int(total_seconds // 60)}m {int(total_seconds % 60)}s" )
                except:
                    pass
            average_time = (sum(game_times, timedelta()) / len(game_times)).total_seconds()
            average_rounds = round(sum(rounds_list) / len(rounds_list), 1)

            print(f"Rounds: {average_rounds} {int(average_time // 60)}m {int(average_time % 60)}s (Average over {len(rounds_list)})" )
        tasks_done_so_far()




pyautogui.hotkey('alt', 'tab')
sleep(0.5)

run(games=5)
# one_round()

sleep(1)
pyautogui.hotkey('alt', 'tab')

