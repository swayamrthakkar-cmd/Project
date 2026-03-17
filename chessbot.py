import chess
import chess.engine

# Standard Algebric Notation (SAN)
# Universal Chess Interface (UCI)

# Download Stockfish

with chess.engine.SimpleEngine.popen_uci("STOCKFISH") as engine:
    board = chess.Board()
    result = engine.analyse(board, chess.engine.Limit(depth=15))

    result = str(result["score"]).replace('PovScore(', '').replace('(', ',').replace('', '').replace(')', '').replace(' ', '')

    unit, eval, color = result.split(',')

    print(result)