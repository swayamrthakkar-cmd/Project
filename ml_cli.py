import random

# memory of learned states
memory = {}

def new_board():
    return [[' ' for _ in range(3)] for _ in range(3)]

def board_to_string(board):
    return ''.join(cell for row in board for cell in row)

def empty_squares(board):
    moves = []
    for i in range(9):
        r = i // 3
        c = i % 3
        if board[r][c] == ' ':
            moves.append(i)
    return moves

def check_winner(board):

    # rows
    for row in board:
        if row[0] == row[1] == row[2] != ' ':
            return row[0]

    # columns
    for c in range(3):
        if board[0][c] == board[1][c] == board[2][c] != ' ':
            return board[0][c]

    # diagonals
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]

    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]

    # draw
    if all(cell != ' ' for row in board for cell in row):
        return 'draw'

    return None


def ai_choose_move(board):

    state = board_to_string(board)

    if state not in memory:
        memory[state] = [0]*9

    scores = memory[state]
    moves = empty_squares(board)

    # choose move with best score
    move = max(moves, key=lambda x: scores[x])

    return move, state


def play_game():

    board = new_board()
    history = []

    turn = 'O'   # AI starts

    while True:

        if turn == 'O':

            move, state = ai_choose_move(board)
            r = move // 3
            c = move % 3
            board[r][c] = 'O'

            history.append((state, move))

        else:
            move = random.choice(empty_squares(board))
            r = move // 3
            c = move % 3
            board[r][c] = 'X'

        winner = check_winner(board)

        if winner:
            return winner, history

        turn = 'X' if turn == 'O' else 'O'


def train(games):

    for i in range(games):

        winner, history = play_game()

        if winner == 'O':
            reward = 1
        elif winner == 'X':
            reward = -1
        else:
            reward = 0.3

        for state, move in history:
            memory[state][move] += reward


def print_board(board):

    print(f"{board[0][0]}|{board[0][1]}|{board[0][2]}")
    print("-----")
    print(f"{board[1][0]}|{board[1][1]}|{board[1][2]}")
    print("-----")
    print(f"{board[2][0]}|{board[2][1]}|{board[2][2]}")


def play_human():

    board = new_board()
    turn = 'X'

    while True:

        print_board(board)

        if turn == 'X':

            move = int(input("Your move (0-8): "))
            r = move // 3
            c = move % 3

            if board[r][c] != ' ':
                print("Invalid move")
                continue

            board[r][c] = 'X'

        else:

            move, _ = ai_choose_move(board)
            r = move // 3
            c = move % 3
            board[r][c] = 'O'

        winner = check_winner(board)

        if winner:
            print_board(board)
            print("Winner:", winner)
            break

        turn = 'O' if turn == 'X' else 'X'


# train the AI
print("Training AI...")
train(10000)

print("Training complete.")

# play against it
play_human()
