from utilities import *
import heapq
from itertools import product
from itertools import combinations


used_spots = ["hit", "miss", "sunk"]
not_used = ["empty", "ship"]


class Board:
    def __init__(self, add_boats = True):
        self.board = [["empty" for _ in range(10)] for _ in range(10)]
        self.scores = [[0 for _ in range(10)] for _ in range(10)]
        self.boats = []
        Boat(board=self, name="boat_1", array=[[1,1]], size=2)
        Boat(board=self, name="boat_2", array=[[1,1,1]], size=3)
        Boat(board=self, name="boat_3a", array=[[1,1,1],[0,1,0]], size=3)
        Boat(board=self, name="boat_3b", array=[[0,1,0],[1,1,1]], size=3)
        Boat(board=self, name="boat_4", array=[[1,1,1,1]], size=4)
        Boat(board=self, name="boat_5", array=[[1,1,1,1,1]], size=5)
        Boat(board=self, name="boat_6", array=[[0,1,1,1],[1,1,1,0]], size=3)

    def print_boats(self):
        for boat in self.boats: print(boat)

    def boat_names(self):
        boat_names = []
        for boat in self.boats:
            boat_names.append(boat.name)
        return boat_names

    def get_shots(self, remaining_boats):
        # print("Remaining boats:", remaining_boats)
        hits = self.hits()
        groups = self.group_hits(hits)
        remaining_boats_count = len(remaining_boats)
        found_unsunk_boats = len(groups)
        unfound_boats = remaining_boats_count - found_unsunk_boats

        print(f"Unfound boats: {remaining_boats_count} - {found_unsunk_boats} = {unfound_boats}")

        group_one, group_multiple = split_by_length(groups)

        if unfound_boats == 0:
            print("All boats found")
            positions = self.best_boat_for_groups(group_multiple, remaining_boats=remaining_boats)
            shots = self.boats_to_shots(positions)
            for x in range(1):
                positions = self.best_boat_for_groups_multi(groups, remaining_boats=remaining_boats)
                shots = shots + self.boats_to_shots(positions)
        else:
            positions = self.best_boat_for_groups(group_multiple, remaining_boats=remaining_boats)
            shots = self.boats_to_shots(positions)

        shots = self.clean_shots(shots)
        # print("Post boats for hits shots:", shots)
        shots = self.surround_shots(groups, shots)
        # print("Post surround shots:", shots)
        shots = self.search_shots(shots, remaining_boats)
        # print("Post search shots:", shots)
        shots = self.any_spots(shots)
        # print("Post any shots:", shots)

        # print()
        print("Hits:", hits)
        print("Groups:", groups)
        print("Boats:", positions)
        print("Shots:", shots)
        return shots

    def search_shots(self, shots, remaining_boats):
        print("Search Remaining boats:", remaining_boats)
        # if remaining_boats == []: remaining_boats = ["boat_3"]
        # print("Search Remaining boats:", remaining_boats)
        for x in range(6):
            # if len(shots) >= 7: return shots
            freqs = {}
            for boat in self.boats:
                if boat.name[0:6] in remaining_boats:
                    freq = self.freq_one_boat(boat, shots, remaining_boats)
                    # print("Search:", boat, freq)
                    freqs = add_dicts(freqs, freq)
            freqs = dict(sorted(freqs.items(), key=lambda item: item[1], reverse=True))
            shots = shots + list(freqs.keys())[:1]

        print("Search shots:", shots)
        return self.clean_shots(shots)

    def search_shots_old(self, shots, remaining_boats):
        if len(shots) >= 7: return shots

        freqs = {}

        for boat in self.boats:
            if boat.name in remaining_boats:
                freq = self.freq_one_boat(boat, boat.size)
                freqs = add_dicts(freqs, freq)

        freqs = dict(sorted(freqs.items(), key=lambda item: item[1], reverse=True))
        print("Freqs:", freqs)

        shots = shots + list(freqs.keys())[:6]
        print("Search shots:", shots)

        return self.clean_shots(shots)

    def freq_one_boat(self, boat, shots, remaining_boats):
        result = boat.remaining_positions(shots)
        result = get_grandchildren(result)
        result = [tuple(item) for item in result]  # Make items hashable
        freq = Counter(result)
        if "boat_1" in remaining_boats or "boat_4" in remaining_boats:
            freq = {coord: v for coord, v in freq.items() if (coord[0] + coord[1]) % 2 == 0}
        freq = freq_to_percent(freq)

        return freq

    def best_boat_for_groups(self, groups, remaining_boats):
        # print("Best boat for group (Start):", remaining_boats, groups)
        best_boats = []
        for group in groups:
            loop_count = 0
            # print()
            # print("Best boat for group:", loop_count, len(group), group, groups)
            while loop_count < 4 and len(group) > 0:

                boat, count = self.best_boat_for_group(group, remaining_boats)
                # print("Best boat for groups 2:", group, boat, )
                if boat:
                    group = [item for item in group if item not in boat]
                    # print("Remaining hits:", group)
                    best_boats.append(boat)
                else:
                    loop_count = +6
                loop_count += 1

        return best_boats

    def best_boat_for_group(self, group, remaining_boats):
        best_count = 0
        best_position = None
        for boat in self.boats:
            if not remaining_boats or boat.name[0:6] in remaining_boats:
                position, count = boat.best_position_for_group(group)
                # print("Best position for group", boat, position, count)
                if count > best_count:
                    best_count = count
                    best_position = position
        return best_position, best_count

    def best_boat_for_groups_multi(self, groups, remaining_boats):
        positions = []
        for group in groups:
            positions += self.best_boat_for_group_multi(group, remaining_boats)
        return positions

    def best_boat_for_group_multi(self, group, remaining_boats):
        positions = []
        for boat in self.boats:
            if not remaining_boats or boat.name[0:6] in remaining_boats:
                positions += boat.best_positions_for_group(group)
                # print("Best position for group multi", positions)
        return positions

    def surround_shots_single(self, shot):
        y, x = shot
        if (x + y) % 2 != 0: return []
        shots = []
        deltas = [(-2, 0), (0, 2), (2, 0), (0, -2)]
        for dy, dx in deltas:
            adj_y, adj_x = y + dy, x + dx
            if adj_x < 0 or adj_x > 9 or adj_y < 0 or adj_y > 9: continue
            # print("Surround:", shot, adj_y, adj_x, self.board[adj_y][adj_x])
            if self.board[int(y + dy/2)][int(x + dx/2)] in used_spots:
                # print("Mini delta in used:", adj_y, adj_x)
                continue
            if 0 <= adj_x <= 9 and 0 <= adj_y <= 9:
                if self.board[adj_y][adj_x] in not_used:
                    shots.append((adj_y, adj_x))
        return shots

    def check_for_short_boats(self, shot, existing_shots):
        y, x = shot
        deltas = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for dy, dx in deltas:
            adj_y, adj_x = y + dy, x + dx
            if adj_x < 0 or adj_x > 9 or adj_y < 0 or adj_y > 9: continue
            if self.board[adj_y][adj_x] == "hit": return []

        # Existing shots already in the center
        deltas = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for dy, dx in deltas:
            adj_y, adj_x = y + dy, x + dx
            if adj_x < 0 or adj_x > 9 or adj_y < 0 or adj_y > 9: continue
            if (adj_y, adj_x) in existing_shots: return []

        shots = []
        deltas = [(-1, 0), (1, 0)]
        for dy, dx in deltas:
            adj_y, adj_x = y + dy, x + dx
            if adj_x < 0 or adj_x > 9 or adj_y < 0 or adj_y > 9: continue
            if self.board[adj_y][adj_x] == "empty": shots.append((adj_y, adj_x))
        if len(shots) > 0: return shots

        deltas = [(0, -1), (0, 1)]
        for dy, dx in deltas:
            adj_y, adj_x = y + dy, x + dx
            if adj_x < 0 or adj_x > 9 or adj_y < 0 or adj_y > 9: continue
            if self.board[adj_y][adj_x] == "empty": shots.append((adj_y, adj_x))
        return shots

    def surround_shots(self, groups, shots):
        # print("Surround shots:", groups, shots)
        if len(shots) >= 7: return shots
        for group in groups:
            for shot in group:
                result = self.surround_shots_single(shot)
                if len(result) > 0:
                    shots = shots + result
                else:
                    shots = shots + self.check_for_short_boats(shot, shots)

                # print("Surround shots:", shots)
        shots = self.clean_shots(shots)
        return shots

    def any_spots(self, shots):
        # print("Any spots:", len(shots), shots)
        if len(shots) >= 7:
            return shots
        for x in range(10):
            for y in range(10):
                if self.board[y][x] == "empty" and (y, x) not in shots:
                    shots.append((y, x))
                    if len(shots) >= 7:
                        return shots
        return shots



    def group_hits(self, hits):
        from collections import defaultdict

        parent = {}
        hits = list(hits)

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            root_x = find(x)
            root_y = find(y)
            if root_x != root_y:
                parent[root_y] = root_x

        # Initialize each hit as its own parent
        for hit in hits:
            parent[hit] = hit

        # Compare each pair of hits
        for i in range(len(hits)):
            for j in range(i + 1, len(hits)):
                x1, y1 = hits[i]
                x2, y2 = hits[j]
                dx = abs(x1 - x2)
                dy = abs(y1 - y2)

                if (dx <= 2 and dy == 0) or (dy <= 2 and dx == 0) or (dx == 1 and dy == 1):
                    union(hits[i], hits[j])

        # Group hits by root parent
        groups = defaultdict(list)
        for hit in hits:
            root = find(hit)
            groups[root].append(hit)

        return list(groups.values())

    def clean_shots(self, shots):
        result = []
        if shots is None: return result
        # print("Clean shots", shots, type(shots))
        for y, x in shots:
            if 0 <= x <= 9 and 0 <= y <= 9:
                # if self.scores[y][x] > 0:
                    if (y, x) not in result and self.board[y][x] not in used_spots:
                        # if self.board[y][x] != "hit":
                        # print("Adding", x, y, self.board[y][x])
                        result.append((y, x))
        return result[0:6]

    def boats_to_shots(self, boats, shots=[]):
        shots = shots + get_grandchildren(boats)
        return self.clean_shots(shots)

    def hits(self):
        hits = set()
        for x in range(10):
            for y in range(10):
                if self.board[y][x] == "hit":
                    hits.add((y, x))
        return hits



class Boat:
    def __init__(self, board, name, array, size):
        # print("New boat:", boat_type, direction, x, y)
        self.board = board
        self.name = name
        self.array = array
        self.board.boats.append(self)
        self.size = size

    def __str__(self):
        return f"Boat: {self.name}"

    def get_spots(self, x, y, direction):
        spots, valid = [], True
        x1, y1 = x, y
        if direction == 0: # horizontal
            for row in self.array:
                for spot in row:
                    if spot == 1:
                        spots.append((y1, x1))
                        if x1 > 9 or y1 > 9: valid = False
                        elif self.board.board[y1][x1] in ["miss", "sunk"]: valid = False
                    x1 += 1
                y1 += 1
                x1 = x
        else:
            for row in reversed(self.array):
                for spot in row:
                    if spot == 1:
                        spots.append((y1, x1))
                        if x1 > 9 or y1 > 9: valid = False
                        elif self.board.board[y1][x1] in ["miss", "sunk"]: valid = False
                    y1 += 1
                x1 += 1
                y1 = y

        if not valid: spots = None
        return spots

    def count_positions(self):
        count = 0
        for x in range(10):
            for y in range(10):
                for z in (0, 1):
                    if self.get_spots(x, y, z):
                        count += 1
        return count

    def count_possible_hits(self, x, y, exclude_spots=None):
        count = 0
        for y1 in range(10):
            for x1 in range(10):
                for z in (0, 1):
                    spots = self.get_spots(x1, y1, z)
                    if spots and (y, x) in spots:
                        okay_to_count = 1
                        if exclude_spots:
                            for exclusion in exclude_spots:
                                if exclusion in spots: okay_to_count = 0
                        count += okay_to_count
        return count

    def remaining_positions(self, exclusion_shots=[]):
        positions = []
        for x in range(10):
            for y in range(10):
                for z in (0, 1):
                    spots = self.get_spots(x, y, z)
                    if spots:
                        valid = True
                        for spot in spots:
                            if spot in exclusion_shots: valid = False
                        if valid: positions.append(spots)
        return positions

    def hit_boats(self):
        boats = self.remaining_positions()
        hit_boats = []
        for boat in boats:
            for y, x in boat:
                if self.board.board[y][x] == "hit": hit_boats.append((boat, self.name))
        return hit_boats

    def hit_boats_percent(self, exclusion_spots=[]):
        boats = self.remaining_positions()
        hit_boats = []
        for boat in boats:
            count = 0
            spots_not_hit = []
            for y, x in boat:
                if (y, x) not in exclusion_spots:
                    if self.board.board[y][x] == "hit":
                        count += 1
                    if self.board.board[y][x] == "empty":
                        spots_not_hit.append((y, x))
                        if self.name == "boat_1":
                            extra_spot = self.get_spot_on_other_side(not_hit=(y,x), boat=boat)
                            if extra_spot:
                                spots_not_hit.append(extra_spot)

            percent = round(count / len(boat), 2)

            if 0 < percent < 1:
                hit_boats.append((spots_not_hit, boat, count, self.name))
        return hit_boats

    def get_spot_on_other_side(self, not_hit, boat):
        extra_spot, hit, miss = None, None, None
        for y, x in boat:
            if self.board.board[y][x] == "hit":
                hit = (y, x)
            if self.board.board[y][x] == "empty":
                miss = (y, x)
        if hit and miss:
            extra_spot = (hit[0] * 2 - miss[0], hit[1] * 2 - miss[1])
        if extra_spot:
            try:
                extra_spot = self.board.clean_shots([extra_spot])[0]
            except:
                extra_spot = None
        return extra_spot

    def best_position_for_group(self, group):
        best_count = 0
        best_position = None
        for boat in self.remaining_positions():
            count_hit = 0
            count_miss = 0
            for spot in boat:
                if spot in group: count_hit += 1
                else: count_miss += 1
            if count_miss > 0 and count_hit > best_count:
                best_count = count_hit
                best_position = boat
        return (best_position, best_count)

    def best_positions_for_group(self, group):
        positions = []
        for boat in self.remaining_positions():
            count_hit = 0
            count_miss = 0
            for spot in boat:
                if spot in group: count_hit += 1
                else: count_miss += 1
            if count_miss > 0 and count_hit > 0:
                positions.append(boat)
        return positions



def convert_to_boat_positions_by_type(placements_with_type):
    from collections import defaultdict
    boat_positions = defaultdict(list)
    for placement, boat_type in placements_with_type:
        boat_positions[boat_type].append(placement)

    return dict(boat_positions)



main = Board()

# print(main.find_best_shots())

# boat = main.boats[0]
# for y, x in [(1,1), (1,2), (1,3), (2,0), (6,3)]:
# for y, x in [(1, 1),]:
#     main.board[y][x] = "hit"
#
# print("X")
# result = main.hit_boat_shots()
# print("Y")
# print(result)
# print()
# result = convert_to_boat_positions_by_type(result)
# print(result)

# for y, x in [(1,1), (1,2), (1,3), (2,0), (6,3)]:
#     main.board[y][x] = "hit"

# result = main.hit_boats_percent()

# result = main.hit_boats_many(remaining_boats=main.boat_names())
# print(result)


