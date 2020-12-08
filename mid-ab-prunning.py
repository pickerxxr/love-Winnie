# -------------命令测试
# piskvork.exe -p xxx.exe FIVEROW.zip -opening 1 -rule 0 -memory 512 -timeturn 15000 -timematch 90
# -------------编译指令
# pyinstaller mid-ab-prunning.py pisqpipe.py --name pbrain-xiaocilao.exe --onefile
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL

pp.infotext = 'name="pbrain-pyrandom", author="Jan Stransky", version="1.0", country="Czech Republic", www="https://github.com/stranskyjan/pbrain-pyrandom"'


########################## self defined function ##############################################################
class State:
    def __init__(self, board_, space_, values_my_, values_oppo_, depth, col=1):
        self.board = [i[::] for i in board_]
        self.space = space_[::]
        self.values_my = [i[::] for i in values_my_]
        self.values_oppo = [i[::] for i in values_oppo_]
        self.depth = depth
        self.col = col

    def Update(self, x, y, col):
        self.board[x][y] = col
        UpdateSpace(self.space, self.board, x, y)
        UpdateAllLocation(self.values_my, self.board, x, y, 1)
        UpdateAllLocation(self.values_oppo, self.board, x, y, 2)

    def NextStates(self, col):
        states = []
        for x, y in self.space:
            newstate = State(self.board, self.space, self.values_my, self.values_oppo, depth=self.depth + 1,
                             col=3 - col)
            newstate.Update(x, y, col)
            newstate.lastmove = (x, y)
            states.append(newstate)
        return states

    def StateValue(self):
        myvalue = -float("Inf")
        myx = -1
        myy = -1
        oppovalue = -float("Inf")
        oppox = -1
        oppoy = -1
        for x, y in self.space:
            if self.values_my[x][y] > myvalue:
                myvalue = self.values_my[x][y]
                myx = x
                myy = y
            if self.values_oppo[x][y] > oppovalue:
                oppovalue = self.values_oppo[x][y]
                oppox = x
                oppoy = y
        if myvalue <= oppovalue:
            return (-oppovalue, oppox, oppoy)
        else:
            return (myvalue, myx, myy)

    def Value(self, alpha=-float("Inf"), beta=float("Inf")):
        if self.depth >= MAX_DEPTH:
            return self.StateValue()
        elif self.col == 2:
            return self.Min_Value(alpha, beta)
        else:
            return self.Max_Value(alpha, beta)

    def Max_Value(self, alpha, beta):
        lastmove = None
        v = -float("Inf")
        for x, y in self.space:
            newstate = State(self.board, self.space, self.values_my, self.values_oppo, self.depth + 1, 3 - self.col)
            newstate.Update(x, y, self.col)
            newstate.lastmove = (x, y)
            newvalue = newstate.Value(alpha, beta)[0]
            if v < newvalue:
                v = newvalue
                lastmove = newstate.lastmove
            alpha = max(alpha, v)
            if v >= beta:
                return v, lastmove[0], lastmove[1]
        return v, lastmove[0], lastmove[1]

    def Min_Value(self, alpha, beta):
        v = float("Inf")
        for x, y in self.space:
            newstate = State(self.board, self.space, self.values_my, self.values_oppo, self.depth + 1, 3 - self.col)
            newstate.Update(x, y, self.col)
            newstate.lastmove = (x, y)
            newvalue = newstate.Value(alpha, beta)[0]
            if v > newvalue:
                v = newvalue
                lastmove = newstate.lastmove
            beta = min(beta, v)
            if v <= alpha:
                return v, lastmove[0], lastmove[1]
        return v, lastmove[0], lastmove[1]


# 某些需要引用的全局变量
# 游戏自带变量（不可修改）
MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
# pp.width/pp.height
# 游戏添加变量
SPACE = [(10, 10)]
MAX_DEPTH = 1
MAX_WIDTH = 3
VALUES_MY = [[-1 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]  # rate for color 1
VALUES_OPPO = [[-1 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]  # rate for color 2
VALUES_MY[10][10] = 1
VALUES_OPPO[10][10] = 1
STATE = State(board_=board, space_=SPACE, values_my_=VALUES_MY, values_oppo_=VALUES_OPPO, depth=1, col=1)


# 如果棋盘上一个位置被更新，那么周围的点的值都要被更新
def UpdateAllLocation(values_update, board_, x, y, col):
    values_update[x][y] = -1000
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx or dy:
                num = 1
                while num <= 4 and 0 <= x + num * dx < pp.width and 0 <= y + num * dy < pp.height \
                        and board_[x + num * dx][y + num * dy] != 3 \
                        and board_[x + num * dx][y + num * dy] != 3 - col:
                    if board_[x + num * dx][y + num * dy] == 0:
                        values_update[x + num * dx][y + num * dy] = UpdateOneLocation(board_=board_, x=x + num * dx,
                                                                                      y=y + num * dy, col=col)
                    num += 1


# 想要更新某一个位置的值，要对四个方向进行考虑
def UpdateOneLocation(board_, x, y, col):
    value = []
    for dx, dy in [(1, 0), (0, 1), (-1, 1), (1, 1)]:
        valueOne = []
        for num in range(-5, 0):
            if 0 <= x + num * dx < pp.width and 0 <= y + num * dy < pp.height:
                valueOne.append(board_[x + num * dx][y + num * dy])
        valueOne.append(col)
        for num in range(1, 6):
            if 0 <= x + num * dx < pp.width and 0 <= y + num * dy < pp.height:
                valueOne.append(board_[x + num * dx][y + num * dy])
        value.append(TypeJudge(valueOne, col))
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
def TypeJudge(value, col):
    # 连五行
    if Match(value, [col, col, col, col, col]):
        return 5
    # 活四
    elif Match(value, [0, col, col, col, col, 0]):
        return 41
    # 冲四
    elif Match(value, [0, col, col, col, col]) or Match(value, [col, col, col, col, 0]):
        return 42
    # 眠四/死四
    elif Match(value, [col, col, col, col]):
        return 43
    # 连活三
    elif Match(value, [0, 0, col, col, col, 0]) or Match(value, [0, col, col, col, 0, 0]):
        return 311
    # 跳活三
    elif Match(value, [0, col, 0, col, col, 0]) or Match(value, [0, col, col, 0, col, 0]):
        return 312
    # 眠三
    elif Match(value, [col, col, col, 0, 0]) or Match(value, [0, 0, col, col, col]):
        return 32
    # 活二
    elif Match(value, [0, 0, col, col, 0, 0]) or Match(value, [0, col, col, 0, 0, 0]) or \
            Match(value, [0, 0, 0, col, col, 0]):
        return 21
    # 眠二
    elif Match(value, [col, col, 0, 0, 0]) or Match(value, [0, 0, 0, col, col]):
        return 22
    # 其他乱七八糟的情况
    else:
        return 0


# 这是一个较为通用的匹配函数
def Match(l1, l2):
    if len(l2) > len(l1):
        return False
    for i in range(len(l1) - len(l2) + 1):
        if l1[i:(i + len(l2))] == l2:
            return True
    return False


def UpdateSpace(space_, board_, x, y):
    for new_x in range(max(0, x - MAX_WIDTH), min(x + MAX_WIDTH + 1, pp.height)):
        for new_y in range(max(0, y - MAX_WIDTH), min(y + MAX_WIDTH + 1, pp.width)):
            if (new_x, new_y) not in space_ and board_[new_x][new_y] == 0:
                space_.append((new_x, new_y))
    if (x, y) in space_:
        space_.remove((x, y))


def direct(space_, value_):
    for x, y in space_:
        if value_[x][y] == 100000:
            return (1, x, y)
    return (0, 0, 0)


########################### changed function ####################################################################
def brain_my(x, y):
    if isFree(x, y):
        STATE.Update(x, y, 1)
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
    if isFree(x, y):
        STATE.Update(x, y, 2)
    else:
        pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))


def brain_turn():
    if pp.terminateAI:
        return
    i = 0
    while True:
        INS = direct(STATE.space, STATE.values_my)
        if INS[0]:
            x, y = INS[1], INS[2]
        else:
            x, y = STATE.Value()[1:3]
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
            STATE.board[x][y] = 0
            STATE.values_oppo[x][y] = -1
            STATE.values_my[x][y] = -1
    STATE.values_my[10][10] = 1
    STATE.values_oppo[10][10] = 1
    STATE.space = [(10, 10)]
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
