import os
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, session

from sudoku import generate_puzzle, is_complete_and_correct

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY", "local-development-only-change-me"
)

# Demo-only in-memory store. Games reset when the server restarts.
# For production, use a shared server-side store with expiration.
GAMES = {}


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/new")
def new_game():
    data = request.get_json(silent=True) or {}
    difficulty = data.get("difficulty", "medium")

    if difficulty not in {"easy", "medium", "hard"}:
        return jsonify(error="Invalid difficulty."), 400

    puzzle, solution = generate_puzzle(difficulty)
    game_id = uuid4().hex
    GAMES[game_id] = {
        "puzzle": puzzle,
        "solution": solution,
        "difficulty": difficulty,
    }
    session["game_id"] = game_id

    return jsonify(puzzle=puzzle, difficulty=difficulty)


def current_game():
    game = GAMES.get(session.get("game_id"))
    if game is None:
        return None, None
    return game["puzzle"], game["solution"]


def submitted_board():
    data = request.get_json(silent=True) or {}
    board = data.get("board")

    if not isinstance(board, list) or len(board) != 9:
        return None
    if any(not isinstance(row, list) or len(row) != 9 for row in board):
        return None
    for row in board:
        for value in row:
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
                or value > 9
            ):
                return None
    return board


def clues_unchanged(puzzle, board):
    return all(
        puzzle[r][c] == 0 or board[r][c] == puzzle[r][c]
        for r in range(9)
        for c in range(9)
    )


@app.post("/api/check")
def check_board():
    puzzle, solution = current_game()
    board = submitted_board()

    if puzzle is None:
        return jsonify(error="Start a new game first."), 400
    if board is None:
        return jsonify(error="Invalid board data."), 400
    if not clues_unchanged(puzzle, board):
        return jsonify(error="Original clues cannot be changed."), 400

    incorrect = [
        [r, c]
        for r in range(9)
        for c in range(9)
        if board[r][c] != 0
        and board[r][c] != solution[r][c]
        and puzzle[r][c] == 0
    ]
    solved = is_complete_and_correct(board, solution)
    return jsonify(incorrect=incorrect, solved=solved)


@app.post("/api/hint")
def hint():
    puzzle, solution = current_game()
    board = submitted_board()

    if puzzle is None:
        return jsonify(error="Start a new game first."), 400
    if board is None:
        return jsonify(error="Invalid board data."), 400
    if not clues_unchanged(puzzle, board):
        return jsonify(error="Original clues cannot be changed."), 400

    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return jsonify(row=r, col=c, value=solution[r][c])
    return jsonify(error="There are no empty cells."), 400


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
