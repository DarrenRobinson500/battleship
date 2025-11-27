from utilities import *

confidence = 0.8
full_screen_region = (0, 0, pyautogui.size().width, pyautogui.size().height)
auto_images = []
boats = []
small_screen = True
image_dir = "images"
if small_screen:
    image_dir = "images small"


class Image:
    def __init__(self, file_locations, name=None):
        if type(file_locations) != list:
            file_locations = [file_locations]
        if not name: name = file_locations[0]
        self.name = name
        self.file_locations = file_locations
        self.loaded_images = {file: self.load_image(file) for file in self.file_locations}
        self.image = self.load_image(file_locations[0])

    def __str__(self):
        return self.name

    def wait(self, duration=20):
        freq = 4
        count = 0
        while count < duration * freq:
            result = self.find()
            if result: return
            sleep(1 / freq)

    def load_image(self, file_path):
        try:
            # print("Load image:", os.path.join(BASE_DIR, file_path))
            image = cv2.imread(os.path.join(BASE_DIR, file_path), cv2.IMREAD_COLOR)

            if image is None:
                print(f"Error: Could not load '{file_path}'.")
            return image
        except Exception as e:
            print(f"Error loading image '{file_path}': {e}")
            return None

    def show(self, dur=500):
        for file, image in self.loaded_images.items():
            show(image, file, dur)

    def find(self, confidence=confidence, region=full_screen_region, use_implied=True):
        best_match = None
        best_confidence = 0

        for file, image in self.loaded_images.items():
            # print("Find", self, file)
            if image is None:
                continue  # Skip if the image couldn't be loaded

            try:
                for x in range(3):
                    location = pyautogui.locateCenterOnScreen(file, confidence=confidence, region=region)
                    if location:
                        match_confidence = confidence
                        if match_confidence > best_confidence:
                            best_match = (int(location.x), int(location.y))
                            best_confidence = match_confidence
                    # print("Image confidence:", self, best_confidence, confidence)
                # if best_confidence < confidence:
                #     print("Image confidence:", self, file, best_confidence, confidence)
            except: pass
            # except Exception as e:
            #     print(f"Did not find: '{file}'")

        return best_match

    def find_all(self, confidence=confidence):
        all_matches = []
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        for file, image in self.loaded_images.items():
            if image is None: continue

            # Convert images to grayscale
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Template matching
            result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= confidence)

            # Store detected positions
            detected_points = list(zip(locations[1], locations[0]))  # (x, y) coordinates

            # Filter out close detections
            min_distance = 20
            filtered_points = []
            for point in detected_points:
                if all(np.linalg.norm(np.array(point) - np.array(existing)) > min_distance for existing in all_matches):
                    all_matches.append(point)

        return all_matches

    def click(self, confidence=confidence, click_offset=(0, 0)):
        position = self.find(confidence)

        if position:
            position_offset = position[0] + click_offset[0], position[1] + click_offset[1]
            # print("Position offset:", position, position_offset)
            pyautogui.click(position_offset)
            # print(f"Clicked on {self} image at {position}")
            return position
        else:
            # print("Image not found. No click performed.")
            return False

def auto_click():
    y_limit = 90
    for image in auto_images:
        result = image.find()
        if result and result[1] > y_limit:
            image.click()
            print("Auto click:", image.name)
            # if image.name == "images/auto/google_back.jpg":
            #     sleep(0.5)
            #     home.click()


for image_sub_dir, image_list in [('auto', auto_images), ('boats', boats)]:
    dir = f"{image_dir}/{image_sub_dir}/"
    for file in files_in_directory(dir):
        image = Image(dir + file, name=file)
        image_list.append(image)


normal_ai = Image(f'{image_dir}/nav/normal_ai.jpg')
fire = Image(f'{image_dir}/nav/fire.jpg')
rematch = Image(f'{image_dir}/nav/rematch.jpg')
main_icon = Image(f'{image_dir}/auto/main_icon.jpg') # Done
