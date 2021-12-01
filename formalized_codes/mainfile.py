"""
AI name: xiaocilao
Version: 2020.1.18.3
Author: Zhenyu Xu, Alan Liu
Course: Introduction to artificial intelligence
Guider: Zhongyu Wei
Basic idea: Combine MCT with MinMaxSearch and return a valid move to guide the GOMOKU AI
Notes: Partial Comment information can be executed to attain our certain goal
"""

import pisqpipe as pp
# from pisqpipe import DEBUG_EVAL, DEBUG
import MCT_Agent as MCT_A
import random
from MCT_Values import result_oppo

# import openpyxl
Weight = result_oppo
IfWeight = 0  # 0 to void using value
MAX_BOARD = 20
begin = [(), ()]  # use this list to check whether we are the first to go

"""
We can uncomment theres lines to store every move and results in a xlsx file so as to apply off policy strategies. 
"""

# create file results.xlsx to store every move whiling playing
# f = openpyxl.load_workbook("E:\\my college\\GOMUKU\\pbrain-jellyfish-master\\results.xlsx")
# f1 = f["Sheet1"]
# RowNum = f1.cell(1, 2).value + 2
# f1.cell(1, 2).value = RowNum - 1
# StepNum = 1 + 3
# f1.cell(RowNum, 2).value = 1

"""
weighted random choice to get new value
"""


# import bisect
# import random
# from collections import Counter, Sequence
# def weighted_sample(population, weights, k):
#     return random.sample(WeightedPopulation(population, weights), k)
#
# class WeightedPopulation(Sequence):
#     def __init__(self, population, weights):
#         assert len(population) == len(weights) > 0
#         self.population = population
#         self.cumweights = []
#         cumsum = 0 # compute cumulative weight
#         for w in weights:
#             cumsum += w
#             self.cumweights.append(cumsum)
#     def __len__(self):
#         return self.cumweights[-1]
#     def __getitem__(self, i):
#         if not 0 <= i < len(self):
#             raise IndexError(i)
#         return self.population[bisect.bisect(self.cumweights, i)]
############################################## changed funcitons #######################################################
def brain_restart():
    global RowNum, StepNum
    for x in range(pp.width):
        for y in range(pp.height):
            MCT_A.board[x, y] = 0
    begin[0] = ()
    begin[1] = ()
    # RowNum = f1.cell(1, 2).value + 2
    # f1.cell(1, 2).value = RowNum - 1
    # StepNum = 1 + 3
    # f1.cell(RowNum, 2).value = 1
    pp.pipe_out("OK")


def brain_my(x, y):
    # global StepNum
    if is_free(x, y):
        MCT_A.board[x, y] = 1
        # f1.cell(RowNum, StepNum).value = str((x, y))
        # f1.cell(RowNum, 3).value = 1
        # StepNum += 1
        begin[0] = (x, y)
        # f.save("E:\\my college\\GOMUKU\\pbrain-jellyfish-master\\results.xlsx")
    else:
        pp.pipe_out("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
    # global StepNum
    if is_free(x, y):
        MCT_A.board[x, y] = 2
        # f1.cell(RowNum, StepNum).value = str((x, y))
        # f1.cell(RowNum, 3).value = 2
        # StepNum += 1
        begin[1] = (x, y)
        # f.save("E:\\my college\\GOMUKU\\pbrain-jellyfish-master\\results.xlsx")
    else:
        pp.pipe_out("ERROR opponents's move [{},{}]".format(x, y))


def brain_turn():
    if pp.terminateAI:
        return
    pos, v, top5_points, nodes_num = MCT_A.minimax()
    if begin[0] == () and begin[1] != ():
        # f1.cell(RowNum, 2).value = 2
        x, y = randomChoice()
    else:
        x, y = pos
    pp.do_mymove(x, y)
    pp.pipe_out("{},{}\tValue:{}\tNodes:{}\tTop5 Points:{}".format(x, y, v, nodes_num, top5_points))


def randomChoice():
    """
    We'd like to share a weight for our initial strategy, especially in the first step in the back hand.
    Monto carlo simulation will teach us which strategy is the best
    The step size is not suggested to be too large or you will be on the back foot
    """
    x, y = begin[1]
    if not IfWeight:
        while True:
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)
            if (dx == 0 and dy == 0) or x + dx < 0 or x + dx > 19 or y + dy < 0 or y + dy > 19:
                continue
            else:
                return x + dx, y + dy
    else:
        dx = 1
        dy = 1
        while True:
            # both MC and TD share a same result
            if (dx == 0 and dy == 0) or x + dx < 0 or x + dx > 19 or y + dy < 0 or y + dy > 19:
                dx = random.randint(-1, 1)
                dy = random.randint(-1, 1)
                continue
            else:
                return x + dx, y + dy


############################################## little changed functions ################################################
def is_free(x, y):
    return 0 <= x < pp.width and 0 <= y < pp.height and MCT_A.board[x, y] == 0


def brain_takeback(x, y):
    if 0 <= x < pp.width and 0 <= y < pp.height and MCT_A.board[x, y] != 0:
        MCT_A.board[x, y] = 0
        return 0
    return 2


############################################## unchanged functions #####################################################
def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipe_out("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipe_out("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipe_out("OK")


def brain_block(x, y):
    if is_free(x, y):
        MCT_A.board[x, y] = 3
    else:
        pp.pipe_out("ERROR winning move [{},{}]".format(x, y))


def brain_end():
    pass


def brain_about():
    pp.pipe_out(pp.infotext)


# if DEBUG_EVAL:
#     import win32gui
#
#
#     def brain_eval(x, y):
#         TODO check if it works as expected
# wnd = win32gui.GetForegroundWindow()
# dc = win32gui.GetDC(wnd)
# rc = win32gui.GetClientRect(wnd)
# c = str(MCT_A.board[x, y])
# win32gui.ExtTextOut(dc, rc[2] - 15, 3, 0, None, c, ())
# win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################
# # define a file for logging
# DEBUG_LOGFILE = "/tmp/pbrain-jellyfish.log"
# # clear it initially
# with open(DEBUG_LOGFILE,"w") as f:
#     pass
#
# # define a function for writing messages to the file
# def logDebug(msg):
#     with open(DEBUG_LOGFILE,"a") as f:
#         f.write(msg+"\n")
#         f.flush()
#
# # define a function to get exception traceback
# def logTraceBack():
#     import traceback
#     with open(DEBUG_LOGFILE,"a") as f:
#         traceback.print_exc(file=f)
#         f.flush()
#     raise
#
# # use logDebug wherever
# # use try-except (with logTraceBack in except branch) to get exception info
# # an example of problematic function
# def brain_turn():
#     logDebug("some message 1")
#     try:
#         logDebug("some message 2")
#         1. / 0. # some code raising an exception
#         logDebug("some message 3") # not logged, as it is after error
#     except:
#         logTraceBack()
######################################################################

# Overwrite functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about

# if DEBUG_EVAL:
#     pp.brain_eval = brain_eval

if __name__ == "__main__":
    pp.main()
