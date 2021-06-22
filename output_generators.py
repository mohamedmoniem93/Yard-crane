def get_optimum_x(m):
    # Get all x that have a value
    optimum_x = []
    for x in m.getVars():
        if x.x > 0:
            x_y_var = (x.Varname, x.x)
            optimum_x.append(x_y_var)
    return optimum_x


def get_optimum_y(optimum_x):
    # Only get numbers out of var name
    # input
    # [
    #    (x[2, 1, 1], 1),
    #    (x[20, 1, 1], 1),
    # ]
    # Output
    # [
    #    [2, 1, 1, 1],
    #    [20, 1, 1, 1],
    # ]
    optimum_y = []
    for opt_x in optimum_x:
        cur_y = []
        for str in opt_x[0].split(","):
            cur_number = ""
            for char in str:
                if char.isdigit():
                    cur_number += char
            cur_y.append(int(cur_number))
        cur_y.append(opt_x[1])
        optimum_y.append(cur_y)
    return optimum_y


def get_total_y(optimum_y, y):
    # calculate total y
    total_y = 0
    for opt_y in optimum_y:
        i = opt_y[0]
        j = opt_y[1]
        quantity = opt_y[3]
        total_y += y[(i, j)] * quantity
    return total_y


def update_b_values(b, optimum_y, last_shift):
    """
    Takes in co-ordinates of x and values of cranes and update b array
    :param b: b dictionary
    :param optimum_y: [
    #     i , j , t (shift), quantity
    #    [2, 1, 1, 1],
    #    [20, 1, 1, 1],
    # ]
    :return: Nothing, it changes b internally
    """
    # Create entries for the next shift
    new_shift_dictionary = {}
    for key, value in b.items():
        src_block, solution_shift = key[0], key[1]
        if solution_shift == last_shift:
            new_shift_dictionary[(src_block, last_shift + 1)] = value

    # Get the optimum solution for the last shift and update the values
    for op_y in optimum_y:
        src_block, d_block, quantity = op_y[0], op_y[1], op_y[3]
        # Take from the src block and add it to the d_block
        new_shift_dictionary[(src_block, last_shift + 1)] -= quantity
        new_shift_dictionary[(d_block, last_shift + 1)] += quantity

    b.update(new_shift_dictionary)
