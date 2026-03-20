import sys
import math

ROWS = 6
COLS = 7

board = [
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '']
]   

heights = [0] * COLS


# ---------------- WIN CHECK ----------------
def check_winner(board):
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] != '' and board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3]:
                return board[r][c]

    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] != '' and board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c]:
                return board[r][c]

    return None


# ---------------- VALID MOVES ----------------
def get_valid_moves(heights):
    moves = []
    for c in range(COLS):
        if heights[c] < ROWS:
            moves.append(c)
    return moves


# ---------------- MAKE MOVE ----------------
def make_move(board, heights, col, piece):
    new_board = []
    for row in board:
        new_board.append(row[:])

    new_heights = heights[:]

    row = ROWS - 1 - new_heights[col]
    new_board[row][col] = piece
    new_heights[col] += 1

    return new_board, new_heights


# ---------------- EVALUATE ----------------
def evaluate(board):
    winner = check_winner(board)

    if winner == 'o':
        return 1000
    if winner == 'x':
        return -1000

    return 0


# ---------------- MINIMAX ----------------
def minimax(board, heights, depth, maximizing):

    moves = get_valid_moves(heights)

    if moves == []:
        return None, evaluate(board)

    if depth == 0 or check_winner(board):
        return None, evaluate(board)

    if depth == 0 or check_winner(board):
        return None, evaluate(board)

    moves = get_valid_moves(heights)

    if maximizing:
        best_score = -math.inf
        best_col = moves[0]

        for col in moves:
            new_board, new_heights = make_move(board, heights, col, 'o')
            _, score = minimax(new_board, new_heights, depth - 1, False)

            if score > best_score:
                best_score = score
                best_col = col

        return best_col, best_score

    else:
        best_score = math.inf
        best_col = moves[0]

        for col in moves:
            new_board, new_heights = make_move(board, heights, col, 'x')
            _, score = minimax(new_board, new_heights, depth - 1, True)

            if score < best_score:
                best_score = score
                best_col = col

        return best_col, best_score


# ---------------- GAME LOOP ----------------
while True:

    col = int(input("Move (1-7): ")) - 1

    if col not in range(7) or heights[col] >= 6:
        sys.exit("Invalid move")

    # player move
    board[ROWS - 1 - heights[col]][col] = 'x'
    heights[col] += 1

    if check_winner(board):
        print("x wins!")
        break

    # AI move
    col, _ = minimax(board, heights, 3, True)

    board, heights = make_move(board, heights, col, 'o')

    print("AI plays:", col + 1)

    for row in board:
        print(row)

    if check_winner(board):
        print("o wins!")
        break