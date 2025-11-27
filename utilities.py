# import time
import pyautogui
import cv2
import math
import os
from time import *
import numpy as np
from collections import Counter


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
gap_x, gap_y = 10, 10

def add(a, b):
    if a and b:
        result = b[0] + a[0], b[1] + a[1]
        return result

def distance(a, b):
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

def difference(a, b):
    result = b[0] - a[0], b[1] - a[1]
    return result

def load_and_show_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        print("Error: Image file not found.")
        return

    cv2.imshow("Image", img)
    cv2.waitKey(0)  # Waits until a key is pressed
    cv2.destroyAllWindows()  # Closes the window

def show(image, file="Image", dur=500):
    cv2.imshow(file, image)
    cv2.waitKey(dur)  # Waits until a key is pressed
    cv2.destroyAllWindows()  # Closes the window

def coords(base, x, y):
    result_x = base[0] + x * gap_x + y * gap_x
    result_y = base[1] + x * gap_y - y * gap_y
    result = int(result_x), int(result_y)
    # print("Coords:", base, x, y, result)
    return result

def wait_for_images(images_to_click, destination_image, time_seconds):
    interval = 0.5
    found, count = False, 0
    while not found and count < time_seconds / interval:
        for image in images_to_click:
            if image.find(): image.click()
        found = destination_image.find()
        sleep(interval)
        print("Wait for image:", count * interval, destination_image)
        count += 1
    return found

def files_in_directory(directory_path):
    try:
        return [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    except:
        print(f"Directory not found: {directory_path}")
        return []



# def get_rgb(coord):
#     x, y = coord
#
#     screenshot = pyautogui.screenshot(region=(x-4, y-4, 9, 9))
#     img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
#     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#
#     avg_color = img_rgb.mean(axis=(0, 1))  # shape: (3,)
#     r, g, b = map(int, avg_color)  # Convert each to plain int
#     return r, g, b

def get_rgb(coord, image):
    x, y = coord

    # Crop the 9x9 region from the single screenshot
    region = image[y-4:y+5, x-4:x+5]

    avg_color = region.mean(axis=(0, 1))  # shape: (3,)
    r, g, b = map(int, avg_color)
    return r, g, b

def get_grandchildren(parent_set):
    children = []
    for parent in parent_set:
        for child in parent:
            children.append(child)
    return children

def most_frequent(input_list, no_to_return=3):
    freq = Counter(input_list)
    top_three = freq.most_common(no_to_return)
    return [element for element, count in top_three]

def remove_duplicates(list):
    result = []
    for item in list:
        if item not in result:
            result.append(item)
    return result

def split_by_length(list_of_lists):
    """
    Splits a list of lists into two groups:
    - single_element_lists: lists with exactly one item
    - multi_element_lists: lists with more than one item
    Returns a tuple of (single_element_lists, multi_element_lists)
    """
    single_element_lists = []
    multi_element_lists = []

    for sublist in list_of_lists:
        if len(sublist) == 1:
            single_element_lists.append(sublist)
        elif len(sublist) > 1:
            multi_element_lists.append(sublist)

    return single_element_lists, multi_element_lists

def freq_to_percent(freq_counter):
    total = sum(freq_counter.values())
    return {key: round((value / total) * 100, 1) for key, value in freq_counter.items()}

def add_dicts(d1, d2):
    result = d1.copy()
    for key, value in d2.items():
        result[key] = round(result.get(key, 0) + value, 1)
    return result
