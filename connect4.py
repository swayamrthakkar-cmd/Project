import sys
import math

board = [
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '']
]

for row in board:
    print(f'{row}\n')

heights = [0, 0, 0, 0, 0, 0, 0]

def check_winner(board):
    ROWS = 6
    COLS = 7

    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] != '' and board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3]:
                return board[r][c]

    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] != '' and board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c]:
                return board[r][c]

    # Diagonal (down-right)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] != '' and board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return board[r][c]

    # Diagonal (down-left)
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if board[r][c] != '' and board[r][c] == board[r+1][c-1] == board[r+2][c-2] == board[r+3][c-3]:
                return board[r][c]

    return None

while True:
    user_input = int(input('Move (1-7): '))

    if user_input not in [1,2,3,4,5,6,7]:
        sys.exit('Invalid Input')

    col = user_input - 1

    if heights[col] >= 6:
        sys.exit('Column full')

    board[5 - heights[col]][col] = 'x'
    heights[col] += 1

    winner = check_winner(board)

    if winner:
        sys.exit(f'{winner} wins!')
