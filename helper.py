import copy

shape = {0: ".", 1: "o", 2: "*", 3: "#"}


class nothing:
    width = 20
    height = 20


pp = nothing()


########################## self defined function ##############################################################
class State:
    def __init__(self, board_, space_, values_my_, values_oppo_, depth, col=1):
        self.board = copy.deepcopy(board_)
        self.space = space_[::]
        self.values_my = copy.deepcopy(values_my_)
        self.values_oppo = copy.deepcopy(values_oppo_)
        self.depth = depth
        self.col = col

    def Update(self, x, y, col):
        self.board[x][y] = col
        UpdateSpace(self.space, x, y)
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

    def MaxValueIndex(self):
        maxvalue = -1000
        maxx = -1
        maxy = -1
        for x, y in self.space:
            if max(self.values_my[x][y] + 1, self.values_oppo[x][y]) > maxvalue:
                maxx = x
                maxy = y
                maxvalue = max(self.values_my[x][y] + 1, self.values_oppo[x][y])
        return maxvalue, maxx, maxy

    def Value(self, alpha=-float("Inf"), beta=float("Inf")):
        if self.depth >= MAX_DEPTH:
            return self.MaxValueIndex()
        elif self.col == 1:
            return self.Max_Value(alpha, beta)
        else:
            return self.Min_Value(alpha, beta)

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
MAX_DEPTH = 2
MAX_WIDTH = 2
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
        for num in range(-4, 0):
            if 0 <= x + num * dx < pp.width and 0 <= y + num * dy < pp.height:
                valueOne.append(board_[x + num * dx][y + num * dy])
        valueOne.append(col)
        for num in range(1, 5):
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


def UpdateSpace(space_, x, y):
    for new_x in range(max(0, x - MAX_WIDTH), min(x + MAX_DEPTH + 1, pp.height)):
        for new_y in range(max(0, y - MAX_WIDTH), min(y + MAX_WIDTH + 1, pp.width)):
            if (new_x, new_y) not in space_:
                space_.append((new_x, new_y))
    space_.remove((x, y))


######################## other function ###################################
def printboard(state):
    if printBoard:
        print("################################################")
        print("  ", end="")
        for x in range(pp.width):
            print(x % 10, end=" ")
        print()
        for y in range(pp.height):
            print(y % 10, end=" ")
            for x in range(pp.height):
                print(shape[state.board[x][y]], end=" ")
            print()
        print()


def printboardvalue(state):
    if printMyValue or printOppoValue:
        print(
            "##########################################################################################################")
        print("         ", end="")
        for x in range(pp.width):
            print(x % 10, end="       ")
        print()
        for y in range(pp.height):
            print(y % 10, end="       ")
            for x in range(pp.height):
                print(shape[state.board[x][y]], end="")
                if printMyValue:
                    print(max(state.values_my[x][y], state.values_oppo[x][y] - 1),
                          end=" " * (7 - len(str(max(state.values_my[x][y], state.values_oppo[x][y] - 1)))))
                if printOppoValue:
                    print(max(state.VALUES_MY[x][y] - 1, state.VALUES_OPPO[x][y]),
                          end=" " * (7 - len(str(max(state.values_my[x][y], state.values_oppo[x][y] - 1)))))
            print()
        print()


def main_(state):
    global play_col
    while run:
        printboard(state)
        printboardvalue(state)
        if play_col == 2:
            y, x = str.split(input("输入行，列，空格分开"), " ")
            x = int(x)
            y = int(y)
            state.Update(x, y, play_col)
            printboard(state)
            play_col = 3 - play_col
        else:
            v, x, y = state.Value()
            board[x][y] = play_col
            state.Update(x, y, play_col)
            printboard(state)
            play_col = 3 - play_col


###################################################################################################
run = 1
play_col = 2  # 1为后下，否则先下
printBoard = 0
printMyValue = 1
printOppoValue = 0
main_(STATE)
