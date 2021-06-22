import random
import math

def place_blocks(ROWS, COLS, NUMBER_OF_BLOCKS):
    """
    :param: ROWS: Rows of the grid
    :param COLS: columns of the grid
    :param NUMBER_OF_BLOCKS: total number of blocks
    Places blocks on the given rows and columns
    :return: grid as a map of
    """
    if ROWS * COLS != NUMBER_OF_BLOCKS:
        raise Exception("Blocks more or less than grid")

    # Maps between block number and position block: (x, y)
    grid = {}
    positions = [(row, col) for row in range(1, ROWS + 1) for col in range(1, COLS + 1)]
    index = 1
    for position in positions:
        grid[index] = position
        index += 1

    return grid

def create_h_given_workload(shifts, NUMBER_OF_BLOCKS):
    tc= 240
    Rc=[(0.79,"F"),(1.58,"E"),(2.40,"R")]
    f = open("workload.txt", "r")
    workloads=[]
    for i in range (1, NUMBER_OF_BLOCKS+1):
        workloads.append(float(f.readline()))
    
    h = {}
    for t in shifts:
        for block in range(1, NUMBER_OF_BLOCKS + 1):
            random_Rc= random.choice(Rc)
            h[(block, t)]= (math.ceil(workloads[block-1]/(random_Rc[0]*tc)), random_Rc[1])
    return h
    
def create_h(shifts, NUMBER_OF_BLOCKS):
    """
    Create a dictionary keys= (block#, shift#): random between ((0-2), empty string)
    :returns H (# H= {(1, 1): (2,""), (2, 1): (0,""), (3, 1): (0,""), (4, 1): (0,""), (5, 1): (0,""), (6, 1): (0,"")})
    """
    tc= 240
    Rc=[(0.79,"F"),(1.58,"E"),(2.40,"R")]
    h = {}
    for t in shifts:
        for block in range(1, NUMBER_OF_BLOCKS + 1):
            random_Rc= random.choice(Rc)
            h[(block, t)] = (random.randint(0, 2), random_Rc[1])
    return h


def create_b(NUMBER_OF_BLOCKS):
    """
    Create a dictionary keys= (block#, shift#): random between (0-2)
    This is done for the first shift only, after that B is updated from the solution
    :returns B (# b= {(1, 1): 1, (2, 1): 2, (3, 1): 2, (4, 1): 0, (5, 1): 1, (6, 1): 1})
    """
    b = {}
    t = 1
    for block in range(1, NUMBER_OF_BLOCKS + 1):
        b[(block, t)] = random.randint(0, 2)
    return b


def calculate_distance_matrix(I, J, y):
    """
    Takes in I, J arrays and calculate the distance matrix out of it
    :param I: Source blocks
    :param J: Destination blocks
    :param y: Distance matrix as dictionary
    :return: Nothing, it changes y value
    """
    yr = 50
    yt = 150
    # same rows and adj columns
    for k1, v1 in I.items():
        for k2, v2 in J.items():
            if v1[0] == v2[0] and abs(v1[1] - v2[1]) == 1:
                y1 = abs(v1[1] - v2[1]) * 210
                y[(k1, k2)] = y1
            # same columns and diff rows
            elif v1[1] == v2[1] and v1[0] != v2[0]:
                y5 = abs(v1[0] - v2[0]) * 46 + (2 * yt)
                y[(k1, k2)] = y5
            # diff rows and adj columns
            elif v1[0] != v2[0] and abs(v1[1] - v2[1]) == 1:
                y2 = abs(v1[1] - v2[1]) * 210 + abs(v1[0] - v2[0]) * 46 + (2 * yt)
                y[(k1, k2)] = y2
            elif k1 == k2:
                y[(k1, k2)] = 10000000
            else:
                y3 = (
                    abs(v1[1] - v2[1]) * 210
                    + abs(v1[0] - 1) * 210
                    + abs(v2[0] - 1) * 46
                    + (2 * yr)
                    + (4 * yt)
                )
                y[(k1, k2)] = y3


def input_ready(number_of_blocks, b, h, cur_shift):
    """
    Returns True and {} penalty if b total is more than or equal h total in each shift
    Returns False and the penalty dictionary (block: penalty value) otherwise
    :param b: available cranes, b = { (block, shift): value}
    :param h: needed cranes, h =  { (block, shift): value}
    :param cur_shift: Number of shf
    :return: Returns True if b total is more than or equal h total
    Returns False otherwise and a dictionary with blocks and values
    penalty_dict = {3: 1, 2: 5}
    """
    penalty_dict = {}
    b_sum = 0
    h_sum = 0
    for block in range(1, number_of_blocks + 1):
        b_sum += b[(block, cur_shift)]
        h_sum += h[(block, cur_shift)][0]

    if b_sum >= h_sum:
        return True, {}

    penalty = int(h_sum - b_sum)

    # Insert penalty at each block where H is more than b
    for block in range(1, number_of_blocks + 1):
        if b[(block, cur_shift)] < h[(block, cur_shift)][0]:
            diff = h[(block, cur_shift)][0] - b[(block, cur_shift)]
            penalty_dict[block] = min(diff, penalty)
            penalty -= min(diff, penalty)
            if penalty <= 0:
                break
    return False, penalty_dict

def sub_penalty_cranes_from_h(h, penalty, cur_shift):
    """
    Substract penalty blocks from h(Needed cranes)
    :param h: Needed cranes dictionary
    :param penalty: Dictionary containing blocks to the penalty cranes
    penalty = {1: 2, 2: 4}, this means that we will sub 2 cranes from the first block and 4 cranes from second block
    :return: Nothing, just updates h
    """
    for block, value in penalty.items():
        h[(block, cur_shift)] = (h[(block, cur_shift)][0]- value , h[(block, cur_shift)][1])


def calculate_penalty_distance(penalty):
    """
    Calculates penalty distance added by getting the penalty cranes
    :param penalty: Dictionary of cranes needed per block id
    :return: A integer representing the penalty distance
    """
    GET_FROM_SPARE_BLOCK_PENALTY = 2000
    added_distance = 0
    for block, value in penalty.items():
        added_distance += value * GET_FROM_SPARE_BLOCK_PENALTY
    return added_distance

if __name__ == "__main__":
    # Row, cols, shifts
    create_h_given_workload([1,2],6)