import random

SIZE = 9
BOX = 3
Grid = list[list[int]]


def candidates(board: Grid, row: int, col: int) -> list[int]:
    used = set(board[row])
    used.update(board[r][col] for r in range(SIZE))
    box_row, box_col = (row // BOX) * BOX, (col // BOX) * BOX

    for r in range(box_row, box_row + BOX):
        for c in range(box_col, box_col + BOX):
            used.add(board[r][c])

    return [number for number in range(1, 10) if number not in used]


def find_empty(board: Grid):
    best_cell = None
    best_options = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == 0:
                options = candidates(board, row, col)
                if best_options is None or len(options) < len(best_options):
                    best_cell = (row, col)
                    best_options = options
                if not options:
                    return row, col, []
                if len(options) == 1:
                    return row, col, options

    if best_cell is None:
        return None
    return best_cell[0], best_cell[1], best_options


def solve(board: Grid, randomize: bool = False) -> bool:
    empty = find_empty(board)
    if empty is None:
        return True

    row, col, options = empty
    if randomize:
        random.shuffle(options)

    for number in options:
        board[row][col] = number
        if solve(board, randomize):
            return True
        board[row][col] = 0

    return False


def count_solutions(board: Grid, limit: int = 2) -> int:
    """Count solutions, stopping when `limit` solutions have been found."""
    if limit <= 0:
        return 0

    empty = find_empty(board)
    if empty is None:
        return 1

    row, col, options = empty
    total = 0
    for number in options:
        board[row][col] = number
        total += count_solutions(board, limit - total)
        board[row][col] = 0
        if total >= limit:
            return total
    return total


def generate_solution() -> Grid:
    board = [[0] * SIZE for _ in range(SIZE)]
    if not solve(board, randomize=True):
        raise RuntimeError("Could not generate a Sudoku solution.")
    return board


def generate_puzzle(difficulty: str = "medium") -> tuple[Grid, Grid]:
    """Return a puzzle and its solution. Empty cells are represented by 0."""
    blanks_by_level = {"easy": 32, "medium": 42, "hard": 50}
    if difficulty not in blanks_by_level:
        raise ValueError("Difficulty must be easy, medium, or hard.")

    solution = generate_solution()
    puzzle = [row[:] for row in solution]
    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)

    blanks_target = blanks_by_level[difficulty]
    removed = 0
    for row, col in cells:
        if removed >= blanks_target:
            break
        previous = puzzle[row][col]
        puzzle[row][col] = 0
        if count_solutions([line[:] for line in puzzle], limit=2) == 1:
            removed += 1
        else:
            puzzle[row][col] = previous

    return puzzle, solution


def is_valid_board(board: Grid) -> bool:
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        return False

    for row in range(SIZE):
        for col in range(SIZE):
            number = board[row][col]
            if not isinstance(number, int) or isinstance(number, bool):
                return False
            if not 0 <= number <= 9:
                return False
            if number == 0:
                continue

            board[row][col] = 0
            valid = number in candidates(board, row, col)
            board[row][col] = number
            if not valid:
                return False
    return True


def is_complete_and_correct(board: Grid, solution: Grid) -> bool:
    return (
        len(board) == SIZE
        and all(len(row) == SIZE for row in board)
        and all(cell != 0 for row in board for cell in row)
        and board == solution
    )
