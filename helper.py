import copy

MAX_BOARD = 100
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
shape = {0: ".", 1: "o", 2: "*", 3: "#"}


class nothing:
    width = 20
    height = 20
pp = nothing()


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
                        valuesUpdate[x + num * dx][y + num * dy] = updateOne(board=board, x=x + num * dx, y=y + num * dy, col=col)
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
        return 100000
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


def maxValueIndex():
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




######################## other function ###################################
def printboard():
    print("################################################")
    print("  ", end="")
    for x in range(pp.width):
        print(x % 10, end=" ")
    print()
    for y in range(pp.height):
        print(y % 10, end=" ")
        for x in range(pp.height):
            print(shape[board[x][y]], end=" ")
        print()
    print()


play_col = 2
while True:
    printboard()
    if play_col == 2:
        y, x = str.split(input("输入行，列，空格分开"), " ")
        x = int(x)
        y = int(y)
        board[x][y] = play_col
        updateAll(values_my, x, y, 1)
        updateAll(values_oppo, x, y, 2)
        printboard()
        play_col = 3 - play_col
    else:
        x, y = maxValueIndex()
        board[x][y] = play_col
        updateAll(values_my, x, y, 1)
        updateAll(values_oppo, x, y, 2)
        printboard()
        play_col = 3 - play_col
