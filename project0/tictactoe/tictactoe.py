"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    Initially X on empty board.
    Find the number of cells with an X or O,
    If odd then it is 0 turn otherwise X
    """
    count = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] != EMPTY:
                count += 1

    if board == initial_state():
        return X
    if count % 2 == 1:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    action = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                action.add((i, j))
    return action


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    board2 = copy.deepcopy(board)
    # on the board fill in the players symbol
    # print(f"{action[0]} and {action[1]}")
    board2[action[0]][action[1]] = player(board)
    return board2


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # horizontal
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2]:
            if board[i][0] != None:
                return board[i][0]
            else:
                return None
    # vertical
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i]:
            if board[0][i] != None:
                return board[0][i]
            else:
                return None

    # diagonal 1
    if board[0][0] == board[1][1] == board[2][2]:
        if board[0][0] != None:
            return board[0][0]
        else:
            return None

    # diagonal 2
    if board[0][2] == board[1][1] == board[2][0]:
        if board[0][0] != None:
            return board[1][1]
        else:
            return None
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # if there is winner the game is oover
    if (winner(board) == X):
        return True
    elif (winner(board) == O):
        return True
    # if the board is not full keep going otherwise stop
    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                return False
    # board is full so game over
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if (winner(board) == X):
        return 1
    elif (winner(board) == O):
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    The maximizing player picks action a in Actions(s) that 
        produces the highest value of Min-Value(Result(s, a)).
    The minimizing player picks action a in Actions(s) that 
        produces the lowest value of Max-Value(Result(s, a)).
    """
    if terminal(board):
        return None
    Max = float("-inf")
    Min = float("inf")

    if player(board) == X:
        # max_value returns the action that produces the highest min-value
        return Max_Value(board, Max, Min)[1]
    else:
        # min_value returns the actions that produces the lowest max-value
        return Min_Value(board, Max, Min)[1]


def Max_Value(board, Max, Min):
    """
    Returns the max value and associated action of the min_value function
    """
    move = None
    # if done return
    if terminal(board):
        return [utility(board), None]

    v = float('-inf')

    # go through each possible action and test it in Min_value.
    # return the max value of the test results
    for action in actions(board):
        # 0 returns the value
        test = Min_Value(result(board, action), Max, Min)[0]
        Max = max(Max, test)
        if test > v:
            v = test
            move = action
        if Max >= Min:
            break
    return [v, move]


def Min_Value(board, Max, Min):
    """
    Returns the min value and associated action of the max_value functio n
    """
    move = None
    # return if done
    if terminal(board):
        return [utility(board), None]
    v = float('inf')

    # go through each possible action and test it in Max_value.
    # return the min value of those results
    for action in actions(board):
        test = Max_Value(result(board, action), Max, Min)[0]
        Min = min(Min, test)
        if test < v:
            v = test
            move = action
        if Max >= Min:
            break
    return [v, move]
