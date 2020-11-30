# -------------命令测试
# piskvork.exe -p xxx.exe FIVEROW.zip -opening 1 -rule 0 -memory 512 -timeturn 15000 -timematch 90
# -------------编译指令
# pyinstaller mid-ab-prunning.py pisqpipe.py --name pbrain-pyrandom.exe --onefile

import copy
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG

pp.infotext = 'name="pbrain-pyrandom", author="Jan Stransky", version="1.0", country="Czech Republic", www="https://github.com/stranskyjan/pbrain-pyrandom"'

MAX_BOARD = 100
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]


########################## self defined function ##############################################################
class State:
    def __init__(self, board, space, values_my, values_oppo):
        self.board = copy.deepcopy(board)
        self.space = space[::]


# 某些需要引用的全局变量
values_my = [[-1 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]  # rate for color 1
values_oppo = [[-1 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]  # rate for color 2
values_my[10][10] = 1
values_oppo[10][10] = 1


# 如果棋盘上一个位置被更新，那么周围的点的值都要被更新
def updateAll(valuesUpdate, board, x, y, col):
    valuesUpdate[x][y] = -1000
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx or dy:
                num = 1
                while num <= 4 and board[x + num * dx][y + num * dy] != 3 \
                        and board[x + num * dx][y + num * dy] != 3 - col \
                        and 0 <= x + num * dx < pp.width and 0 <= y + num * dy < pp.height:
                    if board[x + num * dx][y + num * dy] == 0:
                        valuesUpdate[x + num * dx][y + num * dy] = updateOne(board=board, x=x + num * dx,
                                                                             y=y + num * dy, col=col)
                    num += 1


# 想要更新某一个位置的值，要对四个方向进行考虑
def updateOne(board, x, y, col):
    value = []
    for dx, dy in [(1, 0), (0, 1), (-1, 1), (1, 1)]:
        valueOne = []
        for num in range(-4, 0):
            if 0 <= x + num * dx < pp.width and 0 <= y + num * dy < pp.height:
                valueOne.append(board[x + num * dx][y + num * dy])
        valueOne.append(col)
        for num in range(1, 5):
            if 0 <= x + num * dx < pp.width and 0 <= y + num * dy < pp.height:
                valueOne.append(board[x + num * dx][y + num * dy])
        value.append(updateHelper(valueOne, col))
    if 5 in value:
        return 100000
    elif 41 in value or value.count(42) == 2 or (42 in value and (311 in value or 312 in value)):
        return 10000
    elif value.count(31) == 2:
        return 5000
    elif (311 in value or 312 in value) and 32 in value:
        return 1000
    elif 41 in value:
        return 500
    elif 311 in value:
        return 200
    elif value.count(21) == 2:
        return 100
    elif 32 in value:
        return 50
    elif 21 in value and 22 in value:
        return 10
    elif 21 in value:
        return 5
    elif 22 in value:
        return 2
    else:
        return 0


# 判断某一行/列/斜列属于哪种情况
def updateHelper(value, col):
    # 连五行
    if match(value, [col, col, col, col, col]):
        return 5
    # 活四
    elif match(value, [0, col, col, col, col, 0]):
        return 41
    # 冲四
    elif match(value, [0, col, col, col, col]) or match(value, [col, col, col, col, 0]):
        return 42
    # 眠四/死四
    elif match(value, [col, col, col, col]):
        return 43
    # 连活三
    elif match(value, [0, 0, col, col, col, 0]) or match(value, [0, col, col, col, 0, 0]):
        return 311
    # 跳活三
    elif match(value, [0, col, 0, col, col, 0]) or match(value, [0, col, col, 0, col, 0]):
        return 312
    # 眠三
    elif match(value, [col, col, col, 0, 0]) or match(value, [0, 0, col, col, col]):
        return 32
    # 活二
    elif match(value, [0, 0, col, col, 0, 0]) or match(value, [0, col, col, 0, 0, 0]) or \
            match(value, [0, 0, 0, col, col, 0]):
        return 21
    # 眠二
    elif match(value, [col, col, 0, 0, 0]) or match(value, [0, 0, 0, col, col]):
        return 22
    # 其他乱七八糟的情况
    else:
        return 0


# 这是一个较为通用的匹配函数
def match(l1, l2):
    if len(l2) > len(l1):
        return False
    for i in range(len(l1) - len(l2) + 1):
        if l1[i:(i + len(l2))] == l2:
            return True
    return False


def maxValueIndex(values_my, values_oppo):
    maxX = -1
    maxY = -1
    maxV = -100
    for x in range(pp.width):
        for y in range(pp.height):
            if max(values_my[x][y], values_oppo[x][y] - 1) > maxV:
                maxX = x
                maxY = y
                maxV = max(values_my[x][y], values_oppo[x][y] - 1)
    return maxX, maxY


def restart():
    board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
    values_my = [[-1 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]  # rate for color 1
    values_oppo = [[-1 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]  # rate for color 2
    values_my[10][10] = 1
    values_oppo[10][10] = 1


########################### changed function ####################################################################
def brain_my(x, y):
    if isFree(x, y):
        board[x][y] = 1
        updateAll(valuesUpdate=values_oppo, board=board, x=x, y=y, col=2)
        updateAll(valuesUpdate=values_my, board=board, x=x, y=y, col=1)
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
    if isFree(x, y):
        board[x][y] = 2
        updateAll(valuesUpdate=values_oppo, board=board, x=x, y=y, col=2)
        updateAll(valuesUpdate=values_my, board=board, x=x, y=y, col=1)
    else:
        pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))


def brain_turn():
    if pp.terminateAI:
        return
    i = 0
    while True:
        x, y = maxValueIndex(values_my=values_my, values_oppo=values_oppo)
        i += 1
        if pp.terminateAI:
            return
        if isFree(x, y):
            break
    if i > 1:
        pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
    pp.do_mymove(x, y)


def brain_restart():
    restart()
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0
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