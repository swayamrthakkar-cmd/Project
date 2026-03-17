import sys

board = [
    [' ', ' ', ' '],
    [' ', ' ', ' '],
    [' ', ' ', ' ']
]

def print_board(board):
    for i in range(3):
        print(f'{board[i][0]}|{board[i][1]}|{board[i][2]}')
        if i != 2:
            print('-----')

def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] != ' ':
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != ' ':
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]
    return None

def minimax(board, is_ai_turn):
    winner = check_winner(board)
    if winner == 'O':
        return 1
    elif winner == 'X':
        return -1
    elif all(cell != ' ' for row in board for cell in row):
        return 0

    if is_ai_turn:
        best_score = -float('inf')
        for r in range(3):
            for c in range(3):
                if board[r][c] == ' ':
                    board[r][c] = 'O'
                    score = minimax(board, False)
                    board[r][c] = ' '
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for r in range(3):
            for c in range(3):
                if board[r][c] == ' ':
                    board[r][c] = 'X'
                    score = minimax(board, True)
                    board[r][c] = ' '
                    best_score = min(score, best_score)
        return best_score

def best_move(board):
    move = None
    best_score = -float('inf')
    for r in range(3):
        for c in range(3):
            if board[r][c] == ' ':
                board[r][c] = 'O'
                score = minimax(board, False)
                board[r][c] = ' '
                if score > best_score:
                    best_score = score
                    move = (r, c)
    return move

move_map = {
    '1': (0,0), '2': (0,1), '3': (0,2),
    '4': (1,0), '5': (1,1), '6': (1,2),
    '7': (2,0), '8': (2,1), '9': (2,2)
}

while True:
    print_board(board)
    inp = input('Choose square (1-9) or "exit": ').strip()
    if inp in ['exit','stop','quit']:
        sys.exit(0)
    if inp not in move_map:
        print("Invalid input!")
        continue
    row, col = move_map[inp]
    if board[row][col] != ' ':
        print("Square taken!")
        continue
    board[row][col] = 'X'

    # Check for player win or draw
    winner = check_winner(board)
    if winner:
        print_board(board)
        print(f"{winner} wins!")
        break
    if all(cell != ' ' for row in board for cell in row):
        print_board(board)
        print("It's a draw!")
        break

    # AI move
    ai_row, ai_col = best_move(board)
    board[ai_row][ai_col] = 'O'

    # Check for AI win
    winner = check_winner(board)
    if winner:
        print_board(board)
        print(f"{winner} wins!")
        break
    if all(cell != ' ' for row in board for cell in row):
        print_board(board)
        print("It's a draw!")
        break
