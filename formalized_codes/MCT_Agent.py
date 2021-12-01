import random
import math
from collections import defaultdict as dd

infotext = (
    'name="xiaocilao", '
    'author="XL", '
    'version="3.0", '
    'country="China", '
)
#######################################################################################################################
"""
The scores restored in this file can be altered to attain a better performance
Method applied to revaluate the results includes: Monto carlo
"""

score_ONE = 10
score_TWO = 100
scoreTHREE = 1000
scoreFOUR = 100000
scoreFIVE = 10000000
score_SINGLE_ONE = 1
scoreSINGLE_TWO = 10
score_SINGLE_THREE = 100
score_INGLE_FOUR = 10000

# store all information about the place we are going to place
shape2score = {
    'ONE': score_ONE, 'TWO': score_TWO, 'THREE': scoreTHREE, 'FOUR': scoreFOUR,
    'FIVE': scoreFIVE, 'SINGLE_ONE': score_SINGLE_ONE, 'SINGLE_TWO': scoreSINGLE_TWO,
    'SINGLE_THREE': score_SINGLE_THREE, 'SINGLE_FOUR': score_INGLE_FOUR
}

score = {
    'ONE': score_ONE, 'TWO': score_TWO, 'THREE': scoreTHREE, 'FOUR': scoreFOUR,
    'FIVE': scoreFIVE, 'BLOCKED_ONE': score_SINGLE_ONE, 'BLOCKED_TWtaO': scoreSINGLE_TWO,
    'BLOCKED_THREE': score_SINGLE_THREE, 'BLOCKED_FOUR': score_INGLE_FOUR
}

INF = float("inf")

################################################# board and other definition ###########################################

nodes_num = 0
checkmate_node = 0

switcher = (
    {1: shape2score['ONE'], 2: shape2score['TWO'], 3: shape2score['THREE'], 4: shape2score['FOUR']},
    {1: shape2score['SINGLE_ONE'], 2: shape2score['SINGLE_TWO'], 3: shape2score['SINGLE_THREE'],
     4: shape2score['SINGLE_FOUR']},
    {2: shape2score['TWO'] / 2, 3: shape2score['THREE'], 4: shape2score['SINGLE_FOUR'], 5: shape2score['FOUR']},
    {2: shape2score['SINGLE_TWO'], 3: shape2score['SINGLE_THREE'], 4: shape2score['SINGLE_FOUR'],
     5: shape2score['SINGLE_FOUR']},
    {3: shape2score['THREE'], 4: 0, 5: shape2score['SINGLE_FOUR'], 6: shape2score['FOUR']},
    {3: shape2score['SINGLE_THREE'], 4: shape2score['SINGLE_FOUR'], 5: shape2score['SINGLE_FOUR'],
     6: shape2score['FOUR']
     },
    {4: 0, 5: 0, 6: shape2score['SINGLE_FOUR']},
    {4: 0, 5: shape2score['THREE'], 6: shape2score['SINGLE_FOUR'], 7: shape2score['FOUR']},
    {4: 0, 5: 0, 6: shape2score['SINGLE_FOUR'], 7: shape2score['FOUR']},
    {4: 0, 5: 0, 6: 0, 7: shape2score['SINGLE_FOUR']},
    {5: 0, 6: 0, 7: 0, 8: shape2score['FOUR']},
    {4: 0, 5: 0, 6: 0, 7: shape2score['SINGLE_FOUR'], 8: shape2score['FOUR']},
    {5: 0, 6: 0, 7: 0, 8: shape2score['SINGLE_FOUR']}
)


#######################################################################################
class Board:
    """
    Store the basic information and can use a certain strategy to get the best move in current state
    """

    def __init__(self, board=None, scale=20):
        if board is None:
            self._board = [[0 for i in range(scale)] for j in range(scale)]
            self.size = (scale, scale)
            self.step_count = 0
        else:
            self._board = board
            self.size = (len(board[0]), len(board))
            self.step_count = 0
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    if self[i, j] != 0:
                        self.step_count += 1
        self.xrange = range(self.size[0])
        self.yrange = range(self.size[1])
        self.score_1 = dd(lambda: 0.0)
        self.score_2 = dd(lambda: 0.0)
        self.score_cache = {
            1: {'h': dd(lambda: 0.0), 'v': dd(lambda: 0.0), 'r': dd(lambda: 0.0), 'l': dd(lambda: 0.0)},
            2: {'h': dd(lambda: 0.0), 'v': dd(lambda: 0.0), 'r': dd(lambda: 0.0), 'l': dd(lambda: 0.0)}
        }
        self._init_score()

    def evaluate(self, role=1):
        max_score_1 = 0
        max_score_2 = 0
        for i in self.xrange:
            for j in self.yrange:
                if self[i, j] == 1:
                    max_score_1 += self._fix_evaluation(self.score_1[(i, j)], i, j, 1)
                elif self[i, j] == 2:
                    max_score_2 += self._fix_evaluation(self.score_2[(i, j)], i, j, 2)
        mult = 1 if role == 1 else -1
        result = mult * (max_score_1 - max_score_2)
        return result

    def _init_score(self):
        for i in self.xrange:
            for j in self.yrange:
                if self[i, j] == 0:
                    self.score_1[(i, j)] = self._get_point_score(i, j, 1)
                    self.score_2[(i, j)] = self._get_point_score(i, j, 2)
                elif self[i, j] == 1:
                    self.score_1[(i, j)] = self._get_point_score(i, j, 1)
                elif self[i, j] == 2:
                    self.score_2[(i, j)] = self._get_point_score(i, j, 2)

    def _update_score(self, x, y, radius=6):
        scale = self.size[0]
        for i in range(-radius, radius):
            xi = x + i
            yi = y
            if xi < 0:
                continue
            if xi >= scale:
                break
            self._update_score_sub(xi, yi, 'h')
        for i in range(-radius, radius):
            xi = x
            yi = y + i
            if yi < 0:
                continue
            if yi >= scale:
                break
            self._update_score_sub(xi, yi, 'v')
        for i in range(-radius, radius):
            xi = x + i
            yi = y + i
            if xi < 0 or yi < 0:
                continue
            if xi >= scale or yi >= scale:
                break
            self._update_score_sub(xi, yi, 'r')
        for i in range(-radius, radius):
            xi = x + i
            yi = y - i
            if xi < 0 or yi >= scale:
                continue
            if xi >= scale or yi < 0:
                break
            self._update_score_sub(xi, yi, 'l')

        self._update_score_sub(x, y, None)

    def _update_score_sub(self, x, y, direction):
        role = self[x, y]
        if role == 0 or role == 1:
            if direction:
                self.score_1[(x, y)] -= self.score_cache[1][direction][(x, y)]
                self.score_1[(x, y)] += self._get_point_score(x, y, 1, direction)
            else:
                self.score_1[(x, y)] = self._get_point_score(x, y, 1)
        else:
            self.score_1[(x, y)] = 0

        if role == 0 or role == 2:
            if direction:
                self.score_2[(x, y)] -= self.score_cache[2][direction][(x, y)]
                self.score_2[(x, y)] += self._get_point_score(x, y, 2, direction)
            else:
                self.score_2[(x, y)] = self._get_point_score(x, y, 2)
        else:
            self.score_2[(x, y)] = 0

    def candidate(self):
        fives = list()
        fours = list()
        point_scores = list()
        if self.step_count == 0:
            return [(int(self.size[0] / 2), int(self.size[1] / 2))]
        for x in self.xrange:
            for y in self.yrange:
                if self._has_neighbor(x, y) and self[x, y] == 0:
                    score_1 = self.score_1[(x, y)]
                    score_2 = self.score_2[(x, y)]
                    if self._is_five(x, y, 1):
                        return [(x, y)]
                    elif self._is_five(x, y, 2):
                        fives.append((x, y))
                    elif score_1 >= shape2score['FOUR']:
                        fours.insert(0, (x, y))
                    elif score_2 >= shape2score['FOUR']:
                        fours.append((x, y))
                    else:
                        point_scores.append((x, y))
        if fives:
            return [fives[0]]
        if fours:
            return fours
        candidate = sorted(point_scores, key=lambda p: max(self.score_1[p], self.score_2[p]), reverse=True)
        return candidate

    def _has_neighbor(self, x, y, dist=1):
        for i in range(max(x - dist, 0), min(x + dist + 1, self.size[0])):
            for j in range(max(y - dist, 0), min(y + dist + 1, self.size[1])):
                if not (i == x and j == y) and self[i, j]:
                    return True
        return False

    def __getitem__(self, indices):
        y, x = indices
        if not isinstance(x, slice):  # Scalar
            return self._board[x][y]
        else:
            return [row[y] for row in self._board[x]]

    def __setitem__(self, indices, value):
        y, x = indices
        self._board[x][y] = value
        if value == 0:
            self.step_count -= 1
        else:
            self.step_count += 1
        self._update_score(y, x)

    def __eq__(self, obj):
        if type(self) == type(obj):
            return self._board == obj._board
        else:
            return self._board == obj

    def __repr__(self):
        if isinstance(self._board[0], list):
            l = [str(row) for row in self._board]
            return '\n'.join(l)
        else:
            return str(self._board)

    def _get_point_score(self, x, y, role, direction=None):
        result = 0
        count = 0
        block = 0
        second_count = 0
        scale = self.size[0]

        # horizental
        if direction == None or direction == 'h':
            count = 1
            block = 0
            empty = -1
            second_count = 0
            i = x
            while True:
                i += 1
                if i >= scale:
                    block += 1
                    break
                t = self[i, y]
                if t == 0:
                    if empty == -1 and i < scale - 1 and self[i + 1, y] == role:
                        empty = count
                        continue
                    else:
                        break
                if t == role:
                    count += 1
                    continue
                else:
                    block += 1
                    break
            i = x
            while True:
                i -= 1
                if i < 0:
                    block += 1
                    break
                t = self[i, y]
                if t == 0:
                    if empty == -1 and i > 0 and self[i - 1, y] == role:
                        empty = 0
                        continue
                    else:
                        break
                if t == role:
                    second_count += 1
                    if empty != -1 and empty:
                        empty += 1
                    continue
                else:
                    block += 1
                    break
            count += second_count
            v = self._count_to_score(count, block, empty, x, y, role)
            self.score_cache[role]['h'][(x, y)] = v
            result += v

        if direction == None or direction == 'v':
            count = 1
            block = 0
            empty = -1
            second_count = 0
            i = y
            while True:
                i += 1
                if i >= scale:
                    block += 1
                    break
                t = self[x, i]
                if t == 0:
                    if empty == -1 and i < scale - 1 and self[x, i + 1] == role:
                        empty = count
                        continue
                    else:
                        break
                if t == role:
                    count += 1
                    continue
                else:
                    block += 1
                    break
            i = y
            while True:
                i -= 1
                if i < 0:
                    block += 1
                    break
                t = self[x, i]
                if t == 0:
                    if empty == -1 and i > 0 and self[x, i - 1] == role:
                        empty = 0
                        continue
                    else:
                        break
                if t == role:
                    second_count += 1
                    if empty != -1 and empty:
                        empty += 1
                    continue
                else:
                    block += 1
                    break
            count += second_count
            v = self._count_to_score(count, block, empty, x, y, role)
            self.score_cache[role]['v'][(x, y)] = v
            result += v

        if direction is None or direction == 'r':
            count = 1
            block = 0
            empty = -1
            second_count = 0
            i = 0
            while True:
                i += 1
                xi = x + i
                yi = y + i
                if xi >= scale or yi >= scale:
                    block += 1
                    break
                t = self[xi, yi]
                if t == 0:
                    if empty == -1 and xi < scale - 1 and yi < scale - 1 and self[xi + 1, yi + 1] == role:
                        empty = count
                        continue
                    else:
                        break
                if t == role:
                    count += 1
                    continue
                else:
                    block += 1
                    break
            i = 0
            while True:
                i += 1
                xi = x - i
                yi = y - i
                if xi < 0 or yi < 0:
                    block += 1
                    break
                t = self[xi, yi]
                if t == 0:
                    if empty == -1 and xi > 0 and yi > 0 and self[xi - 1, yi - 1] == role:
                        empty = 0
                        continue
                    else:
                        break
                if t == role:
                    second_count += 1
                    if empty != -1 and empty:
                        empty += 1
                    continue
                else:
                    block += 1
                    break
            count += second_count
            v = self._count_to_score(count, block, empty, x, y, role)
            self.score_cache[role]['r'][(x, y)] = v
            result += v

        if direction is None or direction == 'l':
            count = 1
            block = 0
            empty = -1
            second_count = 0
            i = 0
            while True:
                i += 1
                xi = x + i
                yi = y - i
                if xi < 0 or yi < 0 or xi >= scale or yi >= scale:
                    block += 1
                    break
                t = self[xi, yi]
                if t == 0:
                    if empty == -1 and xi < scale - 1 and yi > 0 and self[xi + 1, yi - 1] == role:
                        empty = count
                        continue
                    else:
                        break
                if t == role:
                    count += 1
                    continue
                else:
                    block += 1
                    break
            i = 0
            while True:
                i += 1
                xi = x - i
                yi = y + i
                if xi < 0 or yi < 0 or xi >= scale or yi >= scale:
                    block += 1
                    break
                t = self[xi, yi]
                if t == 0:
                    if empty == -1 and xi > 0 and yi < scale - 1 and self[xi - 1, yi + 1] == role:
                        empty = 0
                        continue
                    else:
                        break
                if t == role:
                    second_count += 1
                    if empty != -1 and empty:
                        empty += 1
                    continue
                else:
                    block += 1
                    break
            count += second_count
            v = self._count_to_score(count, block, empty, x, y, role)
            self.score_cache[role]['l'][(x, y)] = v
            result += v

        return result

    def _count_to_score(self, count, block, empty, x, y, role):
        if not empty:
            empty = 0
        if empty <= 0:
            if count >= 5:
                return shape2score['FIVE']
            if block == 0 and count in switcher[0]:
                return switcher[0][count]
            if block == 1 and count in switcher[1]:
                return switcher[1][count]
        elif empty == 1 or empty == count - 1:
            if count >= 6:
                return shape2score['FIVE']
            if block == 0 and count in switcher[2]:
                return switcher[2][count]
            if block == 1 and count in switcher[3]:
                return switcher[3][count]
        elif empty == 2 or empty == count - 2:
            if count >= 7:
                return shape2score['FIVE']
            if block == 0 and count in switcher[4]:
                return switcher[4][count]
            if block == 1 and count in switcher[5]:
                return switcher[5][count]
            if block == 2 and count in switcher[6]:
                return switcher[6][count]
        elif empty == 3 or empty == count - 3:
            if count >= 8:
                return shape2score['FIVE']
            if block == 0 and count in switcher[7]:
                return switcher[7][count]
            if block == 1 and count in switcher[8]:
                return switcher[8][count]
            if block == 2 and count in switcher[9]:
                return switcher[9][count]
        elif empty == 4 or empty == count - 4:
            if count >= 9:
                return shape2score['FIVE']
            if block == 0 and count in switcher[10]:
                return switcher[10][count]
            if block == 1 and count in switcher[11]:
                return switcher[11][count]
            if block == 2 and count in switcher[12]:
                return switcher[12][count]
        elif empty == 5 or empty == count - 5:
            return shape2score['FIVE']

        return 0

    def _is_five(self, x, y, role):
        scale = self.size[0]
        count = 1
        i = y + 1
        while True:
            if i >= scale:
                break
            t = self[x, i]
            if t != role:
                break
            count += 1
            i += 1
        i = y - 1
        while True:
            if i < 0:
                break
            t = self[x, i]
            if t != role:
                break
            count += 1
            i -= 1
        if count >= 5:
            return role

        count = 1
        i = x + 1
        while True:
            if i >= scale:
                break
            t = self[i, y]
            if t != role:
                break
            count += 1
            i += 1
        i = x - 1
        while True:
            if i < 0:
                break
            t = self[i, y]
            if t != role:
                break
            count += 1
            i -= 1
        if count >= 5:
            return role

        count = 1
        i = 1
        while True:
            xi = x + i
            yi = y + i
            if xi >= scale or yi >= scale:
                break
            t = self[xi, yi]
            if t != role:
                break
            count += 1
            i += 1
        i = 1
        while True:
            xi = x - i
            yi = y - i
            if xi < 0 or yi < 0:
                break
            t = self[xi, yi]
            if t != role:
                break
            count += 1
            i += 1
        if count >= 5:
            return role

        count = 1
        i = 1
        while True:
            xi = x + i
            yi = y - i
            if xi < 0 or yi < 0 or xi >= scale or yi >= scale:
                break
            t = self[xi, yi]
            if t != role:
                break
            count += 1
            i += 1
        i = 1
        while True:
            xi = x - i
            yi = y + i
            if xi < 0 or yi < 0 or xi >= scale or yi >= scale:
                break
            t = self[xi, yi]
            if t != role:
                break
            count += 1
            i += 1
        if count >= 5:
            return role

        return False

    def win(self):
        for i in self.xrange:
            for j in self.yrange:
                r = self[i, j]
                if r != 0:
                    role = self._is_five(i, j, r)
                    if role:
                        return role
        return False

    def _fix_evaluation(self, s, x, y, role):
        if shape2score['SINGLE_FOUR'] <= s < shape2score['FOUR']:
            if s < shape2score['SINGLE_FOUR'] + shape2score['THREE']:
                return shape2score['THREE']
            elif shape2score['SINGLE_FOUR'] + shape2score['THREE'] <= s < shape2score['SINGLE_FOUR'] * 2:
                return shape2score['FOUR']
            else:
                return shape2score['FOUR'] * 2
        if s >= shape2score['FIVE'] and not self._is_five(x, y, role):
            return shape2score['SINGLE_FOUR'] * 4

        return s


board = Board(scale=20)
################################################# strategy  ############################################################
"""
MinMax iteration is our main strategy
Alpha-beta pruning is add to main efficiency
When we reach our max depth, we use random strategy to enhance. 
The value of the node is combined with two condition: a max value of the node and the sum of value of the node
"""


def minimax(minimax_depth=5, checkmate_depth=10):
    global nodes_num, checkmate_node
    nodes_num = 0
    checkmate_node = 0
    check_1 = checkmate(board, role=1, checkmate_depth=checkmate_depth)
    if check_1:
        return check_1, 1, None, (nodes_num, checkmate_node)
    else:
        (x, y), v, top5_points = _minimax(depth=minimax_depth)
        return (x, y), v, top5_points, (nodes_num, checkmate_node)


def _minimax(depth):
    x, y, v, top5_points = max_value(board, 0, depth, -INF, INF, return_pattern=True)
    return (x, y), v, top5_points


def max_value(board, depth, max_depth, alpha, beta, return_pattern=False):
    global nodes_num
    nodes_num += 1
    if depth == max_depth:
        return board.evaluate()
    v = -INF
    point_scores = {}
    candidates = board.candidate()
    if len(candidates) > 3:
        candidates = candidates[:min(10, math.ceil(len(candidates) * (1 / 3 + 1 / (3 * depth + 3))))]
    if depth == 0 and len(candidates) == 1:
        x, y = candidates[0]
        return x, y, board.evaluate(), candidates
    for x, y in candidates:
        board[x, y] = 1
        check_2 = False
        if depth == 0:
            check_2 = checkmate(board, role=2, checkmate_depth=10)
        if check_2:
            v_new = -INF + 1
        else:
            v_new = minValue(board, depth + 1, max_depth, alpha, beta)
        v = max(v, v_new)
        if return_pattern:
            point_scores[(x, y)] = v_new
        board[x, y] = 0
        if v >= beta:
            return v
        alpha = max(alpha, v)
    if return_pattern:
        scores = sorted(list(point_scores.items()), key=lambda x: x[1], reverse=True)
        next_x, next_y = scores[0][0]
        return next_x, next_y, v, scores[:5]
    else:
        return v


def minValue(board, depth, max_depth, alpha, beta):
    global nodes_num
    nodes_num += 1
    if depth == max_depth:
        return board.evaluate()
    v = INF
    candidates = board.candidate()
    candidates = candidates[:6]
    if len(candidates) > 3:
        candidates = candidates[:min(10, math.ceil(len(candidates) * (1 / 3 + 1 / (3 * depth + 3))))]
    for x, y in candidates:
        board[x, y] = 2
        v_new = max_value(board, depth + 1, max_depth, alpha, beta)
        v = min(v, v_new)
        board[x, y] = 0
        if v <= alpha:
            return v
        beta = min(beta, v)
    return v


def checkmate(board, role, checkmate_depth=6):
    return maxNode_more(board, role, 0, checkmate_depth)  # True/False


def maxNode_more(board, role, depth, max_depth):
    global checkmate_node
    checkmate_node += 1
    winner = board.win()
    if winner == role:
        return True
    elif winner == 3 - role:
        return False
    if depth >= max_depth:
        return False
    for x, y in board.candidate():
        if role == 1:
            point_role_score = board.score_1[(x, y)]
        elif role == 2:
            point_role_score = board.score_2[(x, y)]
        if point_role_score >= 2 * score['THREE']:
            board[x, y] = role
            m = minNode_more(board, role, depth + 1, max_depth)
            board[x, y] = 0
            if m:
                if depth == 0:  # 可以斩杀
                    return x, y
                else:
                    return True
    return False


def minNode_more(board, role, depth, max_depth):
    global checkmate_node
    checkmate_node += 1
    winner = board.win()
    if winner == role:
        return True
    elif winner == 3 - role:
        return False
    if depth >= max_depth:
        return False
    cand = []
    for x, y in board.candidate():
        if board.score_2[(x, y)] + board.score_1[(x, y)] >= score['BLOCKED_FOUR']:
            board[x, y] = 3 - role  # opponent
            m = maxNode_more(board, role, depth + 1, max_depth)
            board[x, y] = 0
            if m:
                cand.append((x, y))
            else:
                return False
    if cand == []:
        return False
    else:
        return random.choice(cand)


