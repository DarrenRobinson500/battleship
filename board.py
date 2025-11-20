used_spots = ["hit", "miss", "sunk"]
not_used = ["empty", "ship"]

class Boat:
    def __init__(self, board, boat_type, direction, x, y):
        # print("New boat:", boat_type, direction, x, y)
        self.board = board
        self.boat_type = boat_type
        self.direction = direction
        self.x = x
        self.y = y
        self.spots = self.get_spots()
        self.sunk = False

    def __str__(self):
        return f"Boat: Type: {self.boat_type}, Direction:{self.direction}, x:{self.x}, y:{self.y}. Spots: {self.spots}"

    def get_spots(self):
        spots = []
        if self.direction == 0:
            for i in range(self.boat_type):
                spots.append((self.x, self.y + i))
        else:
            for i in range(self.boat_type):
                spots.append((self.x + i, self.y))
        # print("Get spots:", self, spots)
        return spots


class Board:
    def __init__(self, add_boats = True):
        self.board = [["empty" for _ in range(10)] for _ in range(10)]
        self.scores = [[0 for _ in range(10)] for _ in range(10)]
        self.boats = []

    def shoot_salvo(self):
        shots = self.get_shots()

        for y, x in shots:
            if self.board[y][x] in ["ship", "hit"]: self.board[y][x] = "hit"
            else: self.board[y][x] = "miss"

    def get_shots(self, boat_type=4):
        shots = []
        shots = self.between_hits_shots(shots)
        shots = self.between_hits_and_misses_shots(shots)
        shots = self.surround_hit_shots(shots)
        shots = self.search_shots(shots, boat_type=boat_type)[0:6]
        shots = self.search_shots(shots, boat_type=2)[0:6]
        shots = self.any_spots(shots)[0:6]
        print("Shots:", shots)
        return shots

    def between_hits_shots(self, shots):
        for x in range(10):
            for y in range(10):
                if (y, x) not in shots:
                    north = self.get_spot(y - 1, x)
                    south = self.get_spot(y + 1, x)
                    east = self.get_spot(y, x + 1)
                    west = self.get_spot(y, x - 1)
                    if north == "hit" and south == "hit": shots.append((y, x))
                    if east == "hit" and west == "hit": shots.append((y, x))
        print("Between hits shots:", shots)
        return self.clean_shots(shots)

    def between_hits_and_misses_shots(self, shots):
        if len(shots) >= 6: return shots
        hits = [(y, x) for x in range(10) for y in range(10) if self.board[y][x] == "hit"]
        for y, x in hits:
            north = self.get_spot(y - 2, x)
            south = self.get_spot(y + 2, x)
            east = self.get_spot(y, x + 2)
            west = self.get_spot(y, x - 2)
            north_1 = self.get_spot(y - 1, x)
            south_1 = self.get_spot(y + 1, x)
            east_1 = self.get_spot(y, x + 1)
            west_1 = self.get_spot(y, x - 1)
            if north in not_used or south in not_used or east in not_used or west in not_used: continue
            if east in ["hit"] and west in ["miss", "sunk"]: shots.append((y, x-1))
            if east in ["miss", "sunk"] and west in ["hit"]: shots.append((y, x+1))
            if north in ["hit"] and south in ["miss", "sunk"]: shots.append((y+1, x))
            if north in ["miss", "sunk"] and south in ["hit"]: shots.append((y-1, x))
            if north in ["miss", "sunk"] or  north_1 in ["miss", "sunk"]:
                if south in ["miss", "sunk"] or south_1 in ["miss", "sunk"]:
                    if east in ["miss", "sunk"] or east_1 in ["miss", "sunk"]:
                        if west in ["miss", "sunk"] or west_1 in ["miss", "sunk"]:
                            shots.append((y, x - 1))
                            shots.append((y, x + 1))
                            shots.append((y + 1, x))
                            shots.append((y - 1, x))
        print("Between hits and misses shots:", shots)
        return self.clean_shots(shots)

    def surround_hit_shots(self, shots):
        if len(shots) >= 6: return shots
        hits = [(y, x) for x in range(10) for y in range(10) if self.board[y][x] == "hit"]
        for y, x in hits:
            deltas = [(-2, 0), (0, 2), (2, 0), (0, -2)]
            if (x + y ) % 2 == 0: deltas = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            for dy, dx in deltas:
                adj_y, adj_x = y + dy, x + dx
                if 0 <= adj_x <= 9 and 0 <= adj_y <= 9:
                    if self.board[adj_y][adj_x] in not_used and (adj_y, adj_x) not in shots:
                        shots.append((adj_y, adj_x))
        print("Surround Shots:", shots)
        return self.clean_shots(shots)

    def search_shots(self, shots, boat_type=4):
        if len(shots) >= 6:
            # print("Not searching, 6 shots:", shots)
            return shots
        for _ in range(6):
            for x in range(10):
                for y in range(10):
                    self.scores[y][x] = self.count_possible_hits(boat_type=boat_type, x=x, y=y, exclude_spots=shots) # + self.count_possible_hits(boat_type=2, x=x, y=y, exclude_spots=shots)
                    if (y, x) in shots: self.scores[y][x] = 0
                    if boat_type in [2, 4]:
                        if (x + y ) % 2 == 0: self.scores[y][x] = 0
            scored_positions = [(self.scores[y][x], y, x) for y in range(10) for x in range(10)]
            sorted_positions = sorted(scored_positions, key=lambda x: x[0], reverse=True)
            best_coords = sorted_positions[0][1:3]
            y, x = best_coords
            if self.scores[y][x] > 0:
                shots.append(best_coords)
        if boat_type == 2:
            print("Extended Search - sorted positions (top 6):", sorted_positions[0:6])
        else:
            print("Search - sorted positions (top 6):", sorted_positions[0:6])
        return self.clean_shots(shots)

    def any_spots(self, shots):
        print("Any spots:", len(shots), shots)
        if len(shots) >= 6:
            # print("Not searching, 6 shots:", shots)
            return shots
        for _ in range(6):
            for x in range(10):
                for y in range(10):
                    shots.append((y, x))
        return shots


    def clean_shots(self, shots):
        result = []
        for y, x in shots:
            if 0 <= x <= 9 and 0 <= y <= 9:
                # if self.scores[y][x] > 0:
                    if (y, x) not in result and self.board[y][x] not in used_spots:
                        # if self.board[y][x] != "hit":
                        # print("Adding", x, y, self.board[y][x])
                        result.append((y, x))
        return result

    def count_possible_hits(self, boat_type, x, y, exclude_spots=None):
        # print("Count possible positions:", x, y)
        count = 0
        # Direction 0
        for y1 in range(max(y - boat_type + 1, 0), y + 1):
            x1 = x
            valid = self.check_valid(boat_type, 0, x1, y1, exclude_spots)
            if valid: count += 1
        # Direction 1
        for x1 in range(max(x - boat_type + 1, 0), x + 1):
            y1 = y
            valid = self.check_valid(boat_type, 1, x1, y1, exclude_spots)
            if valid: count += 1
        return count

    def check_valid(self, boat_type, direction, x1, y1, exclude_spots):
        boat = Boat(board=self, boat_type=boat_type, direction=direction, x=x1, y=y1)
        spots = boat.get_spots()
        valid_position = True
        for x2, y2 in spots:
            if x2 < 0 or x2 > 9 or y2 < 0 or y2 > 9:
                valid_position = False
            elif exclude_spots and (y2, x2) in exclude_spots:
                valid_position = False
            elif self.board[y2][x2] in used_spots:
                valid_position = False
        # if valid_position:
            # print("Found valid position:", boat)
        return valid_position

    def get_spot(self, y, x):
        if 0 <= x <= 9 and 0 <= y <= 9:
            return self.board[y][x]
        else:
            return "miss"

    # def shoot_random(self):
    #     valid_shot = False
    #     while not valid_shot:
    #         x = random.randint(0, 9)
    #         y = random.randint(0, 9)
    #         if self.board[y][x] in ["empty", "ship"]:valid_shot = True
    #     if self.board[y][x] == "ship": self.board[y][x] = "hit"
    #     else: self.board[y][x] = "miss"

    # def add_boats(self):
    #     for boat_type in [5, 4, 3, 3, 2]:
    #         self.add_boat(boat_type)
    #
    # def get_random_boat(self, boat_type):
    #     direction = random.randint(0, 1)
    #     if direction == 0:
    #         x = random.randint(0, 9)
    #         y = random.randint(0, 9 - boat_type + 1)
    #     else:
    #         x = random.randint(0, 9 - boat_type + 1)
    #         y = random.randint(0, 9)
    #     return Boat(board=self, boat_type=boat_type, direction=direction, x=x, y=y)
    #
    # def add_boat(self, boat_type):
    #     found, count = False, 0
    #     while not found and count < 10:
    #         new_boat = self.get_random_boat(boat_type)
    #         all_spots_free = True
    #         spots = new_boat.get_spots()
    #         for x, y in spots:
    #             if self.board[y][x] == "ship": all_spots_free = False
    #         if all_spots_free: found = True
    #         count += 1
    #     if found:
    #         for x, y in spots: self.board[y][x] = "ship"
    #         self.boats.append(new_boat)

def add_all_positions(scenario, boat_type):
    for direction in [0, 1]:
        if direction == 0:
            for x in range(10):
                for y in range(10 - boat_type + 1):
                    boat = Boat(board=scenario, boat_type=boat_type, direction=direction, x=x, y=y)
                    spots = boat.get_spots()
                    for x1, y1 in spots:
                        scenario.scores[y1][x1] += 1
        else:
            for x in range(10 - boat_type + 1):
                for y in range(10):
                    # print("XY", x, y)
                    boat = Boat(board=scenario, boat_type=boat_type, direction=direction, x=x, y=y)
                    spots = boat.get_spots()
                    for x1, y1 in spots:
                        if 0 <= x1 <= 9 and 0 <= y1 <= 9:
                            scenario.scores[y1][x1] += 1



main = Board()
