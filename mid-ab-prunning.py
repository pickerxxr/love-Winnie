# -------------命令测试
# piskvork.exe -p xxx.exe FIVEROW.zip -opening 1 -rule 0 -memory 512 -timeturn 15000 -timematch 90
# -------------编译指令
# pyinstaller mid-ab-prunning.py pisqpipe.py --name pbrain-xiaocilao.exe --onefile
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL
import random

pp.infotext = 'name="pbrain-pyrandom", author="Jan Stransky", version="1.0", country="Czech Republic", www="https://github.com/stranskyjan/pbrain-pyrandom"'
MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
########################## self defined function ##############################################################

# test_board = ({(8, 8), (9, 9)}, {(8, 9)})
# test_playing = 1
# test_last_move = (8, 8)
# test_board_size = 15
# test_state = (test_board, test_last_move, test_playing, test_board_size)

def strategy(state):
    """ Information provided to you:
    state = (board, last_move, playing, board_size)
    board = (x_stones, o_stones)
    stones is a set contains positions of one player's stones. e.g.
        x_stones = {(8,8), (8,9), (8,10), (8,11)}
    playing = 0|1, the current player's index

    Your strategy will return a position code for the next stone, e.g. (8,7)
    """
    board, last_move, playing, board_size = state
    if last_move == None:
        return (board_size / 2 + 1, board_size / 2 + 1)

    root = construct_tree(state, 0, 2)
    max_value = float("-inf")
    best_move = []
    for successor in root.successor:
        successor_value = maxValue(successor, float("-inf"), float("inf"))
        if successor_value > max_value:
            max_value = successor_value
            best_move = list(successor.state[0][playing] - board[playing])
        elif successor_value == max_value:
            best_move.extend(list(successor.state[0][playing] - board[playing]))
    if best_move == []:
        best_move = random.choice(find_avai_position(state))
    return random.choice(best_move)


def maxValue(node, alpha, beta):
    if node.isLeaf:
        return node.value
    v = float("-inf")
    for successor in node.successor:
        v = max(v, minValue(successor, alpha, beta))
        if v >= beta:
            return v
        alpha = max(alpha, v)
    return v


def minValue(node, alpha, beta):
    if node.isLeaf:
        return node.value
    v = float("inf")
    for successor in node.successor:
        v = min(v, maxValue(successor, alpha, beta))
        if v <= alpha:
            return v
        beta = min(beta, v)
    return v


def find_avai_position(state):
    board, last_move, playing, board_size = state
    my_stones = board[playing]
    oppo_stones = board[not playing]

    avai_position = []
    for stone in my_stones:
        avai_position.extend(find_around_position(stone))
    for stone in oppo_stones:
        avai_position.extend(find_around_position(stone))

    avai_position = set(avai_position)
    for stone in my_stones:
        avai_position.remove(stone)
    for stone in oppo_stones:
        avai_position.remove(stone)
    avai_position = {pos for pos in avai_position
                     if pos[0] in range(1, board_size + 1)
                     and pos[1] in range(1, board_size + 1)}
    return avai_position


def find_around_position(position):
    x, y = position
    return [(x_, y_) for x_ in [x - 1, x, x + 1] for y_ in [y - 1, y, y + 1]]


def score(fiveTuple):
    if len(fiveTuple) != 5:
        print("ERROR")
        return None
    if 1 in fiveTuple and -1 in fiveTuple:
        return 0
    elif sum(fiveTuple) == 0:
        return 7
    elif sum(fiveTuple) == -1:
        return -35
    elif sum(fiveTuple) == -2:
        return -800
    elif sum(fiveTuple) == -3:
        return -15000
    elif sum(fiveTuple) == -4:
        return -800000
    elif sum(fiveTuple) == -5:
        return -10000000
    elif sum(fiveTuple) == 1:
        return 15
    elif sum(fiveTuple) == 2:
        return 400
    elif sum(fiveTuple) == 3:
        return 1800
    elif sum(fiveTuple) == 4:
        return 100000
    elif sum(fiveTuple) == 5:
        return 10000000


def get_value(state):
    board, last_move, playing, board_size = state
    row = board_size
    col = board_size
    # create a table to record the board state
    # 1: occupied by self
    # -1: occupied by opponent
    # 0: available
    table = [[0 for i in range(col)] for j in range(row)]
    for i in range(row):
        for j in range(col):
            if playing == 1:
                if (i + 1, j + 1) in board[0]:
                    table[i][j] = -1
                elif (i + 1, j + 1) in board[1]:
                    table[i][j] = 1
            else:
                if (i + 1, j + 1) in board[0]:
                    table[i][j] = 1
                elif (i + 1, j + 1) in board[1]:
                    table[i][j] = -1
    sumScore = 0
    for i in range(row):
        for j in range(col):
            if j + 4 < col:
                sumScore += score(tuple(table[i][j:j + 5]))
            if i + 4 < row:
                sumScore += score(
                    tuple([table[i][j], table[i + 1][j], table[i + 2][j], table[i + 3][j], table[i + 4][j]]))
            if i + 4 < row and j + 4 < col:
                fivetuple = []
                for k in range(5):
                    fivetuple.append(table[i + k][j + k])
                sumScore += score(tuple(fivetuple))
            if i + 4 < row and j - 4 >= 0:
                fivetuple = []
                for k in range(5):
                    fivetuple.append(table[i + k][j - k])
                sumScore += score(tuple(fivetuple))
    return sumScore


class Node:
    def __init__(self, state, depth, limitedDepth, successor=[], isLeaf=False, value=None):
        self.state = state
        self.depth = depth
        self.limitedDepth = limitedDepth
        self.successor = successor
        self.isLeaf = isLeaf
        self.value = value

    def __repr__(self):
        info = '========= Node Info ========'
        depth = 'depth:' + str(self.depth)
        limitedDepth = 'limitedDepth:' + str(self.limitedDepth)
        isLeaf = 'isLeaf:' + str(self.isLeaf)
        value = 'value:' + str(self.value)
        state = 'state:' + str(self.state)
        successor = 'successors:' + str(len(self.successor))
        return '\n'.join([info, depth, limitedDepth, isLeaf, value, state, successor, '\n'])


def construct_tree(state, depth, limitedDepth):
    board, last_move, playing, board_size = state
    oppo_stones = board[not playing].copy()

    tree_root = Node(state, depth, limitedDepth, successor=[])

    if depth == limitedDepth:
        tree_root.isLeaf = True
        tree_root.value = get_value(state)
        return tree_root

    avai_position = find_avai_position(state)
    for position in avai_position:
        my_stones = board[playing].copy()
        my_stones.add(position)
        if playing == 0:
            new_board = (my_stones, oppo_stones)
            next_playing = 1
        else:
            new_board = (oppo_stones, my_stones)
            next_playing = 0
        new_state = (new_board, position, next_playing, board_size)
        tree_root.successor.append(construct_tree(new_state, depth + 1, limitedDepth))
    return tree_root


def finish():
    pass


STATE = [(set(), set()), None, 1, 20]


# import time
# start = time.clock()
# print strategy(test_state)
# end = time.clock()
# print start
# print end
# print end-start


########################### changed function ####################################################################
def brain_my(x, y):
    if isFree(x, y):
        STATE[0][0].add((int(x), int(y)))
        STATE[1] = (x, y)
        board[x][y] = 1
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
    if isFree(x, y):
        STATE[0][1].add((int(x), int(y)))
        STATE[1] = (x, y)
        board[x][y] = 2
    else:
        pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))


def brain_turn():
    if pp.terminateAI:
        return
    i = 0
    while True:
        x, y = strategy(STATE)
        i += 1
        if pp.terminateAI:
            return
        if isFree(x, y):
            break
    if i > 1:
        pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
    pp.do_mymove(x, y)


def brain_restart():
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0
    STATE[0][0] = set()
    STATE[0][1] = set()
    STATE[1] = None
    pp.pipeOut("OK")


########################### unchanged function ##################################################################

def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipeOut("OK")


def isFree(x, y):
    return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0


def brain_block(x, y):
    if isFree(x, y):
        board[x][y] = 3
    else:
        pp.pipeOut("ERROR winning move [{},{}]".format(x, y))


def brain_takeback(x, y):
    if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
        board[x][y] = 0
        return 0
    return 2


def brain_end():
    pass


def brain_about():
    pp.pipeOut(pp.infotext)


if DEBUG_EVAL:
    import win32gui


    def brain_eval(x, y):
        # TODO check if it works as expected
        wnd = win32gui.GetForegroundWindow()
        dc = win32gui.GetDC(wnd)
        rc = win32gui.GetClientRect(wnd)
        c = str(board[x][y])
        win32gui.ExtTextOut(dc, rc[2] - 15, 3, 0, None, c, ())
        win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################
"""
# define a file for logging ...
DEBUG_LOGFILE = "/tmp/pbrain-pyrandom.log"
# ...and clear it initially
with open(DEBUG_LOGFILE,"w") as f:
	pass

# define a function for writing messages to the file
def logDebug(msg):
	with open(DEBUG_LOGFILE,"a") as f:
		f.write(msg+"\n")
		f.flush()

# define a function to get exception traceback
def logTraceBack():
	import traceback
	with open(DEBUG_LOGFILE,"a") as f:
		traceback.print_exc(file=f)
		f.flush()
	raise

# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function
def brain_turn():
	logDebug("some message 1")
	try:
		logDebug("some message 2")
		1. / 0. # some code raising an exception
		logDebug("some message 3") # not logged, as it is after error
	except:
		logTraceBack()
"""
######################################################################

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
    pp.brain_eval = brain_eval


def main():
    pp.main()


if __name__ == "__main__":
    main()
