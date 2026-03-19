import sys

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

a_file = []
b_file = []
c_file = []
d_file = []
e_file = []
f_file = []
g_file = []

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
    user_input = input('Move: ')

    if len(user_input) != 1:
        sys.exit('Invalid Input')

    if user_input not in ['a', 'b', 'c', 'd', 'e', 'f', 'g']:
        sys.exit('Invalid Input')

    if user_input == 'a' and len(a_file) < 6:
        a_file.append('x')
        board[5 - (len(a_file)-1)][0] = 'x'
    elif user_input == 'b' and len(b_file) < 6:
        b_file.append('x')
        board[5 - (len(b_file)-1)][1] = 'x'
    elif user_input == 'c' and len(c_file) < 6:
        c_file.append('x')
        board[5 - (len(c_file)-1)][2] = 'x'
    elif user_input == 'd' and len(d_file) < 6:
        d_file.append('x')
        board[5 - (len(d_file)-1)][3] = 'x'
    elif user_input == 'e' and len(e_file) < 6:
        e_file.append('x')
        board[5 - (len(e_file)-1)][4] = 'x'
    elif user_input == 'f' and len(f_file) < 6:
        f_file.append('x')
        board[5 - (len(f_file)-1)][5] = 'x'
    elif user_input == 'g' and len(g_file) < 6:
        g_file.append('x')
        board[5 - (len(g_file)-1)][6] = 'x'
    else:
        sys.exit('Invalid Input')

    winner = check_winner(board)

    if winner:
        sys.exit(f'{winner} wins!')