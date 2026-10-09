from copy import deepcopy

import pytest

from sudoku import (
    count_solutions,
    generate_puzzle,
    is_complete_and_correct,
    is_valid_board,
    solve,
)


def sample_puzzle():
    return [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]


def test_solver_solves_valid_puzzle():
    board = sample_puzzle()
    assert solve(board)
    assert is_valid_board(board)
    assert all(0 not in row for row in board)


def test_generated_easy_puzzle_has_unique_solution():
    puzzle, solution = generate_puzzle("easy")
    assert count_solutions(deepcopy(puzzle), limit=2) == 1
    assert is_valid_board(solution)
    assert all(0 not in row for row in solution)


def test_original_clues_match_solution():
    puzzle, solution = generate_puzzle("easy")
    for r in range(9):
        for c in range(9):
            if puzzle[r][c] != 0:
                assert puzzle[r][c] == solution[r][c]


def test_invalid_difficulty_is_rejected():
    with pytest.raises(ValueError):
        generate_puzzle("expert")


def test_duplicate_number_is_invalid():
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 5
    board[0][1] = 5
    assert not is_valid_board(board)


def test_incomplete_board_is_not_solved():
    board = [[0] * 9 for _ in range(9)]
    solution = [[1, 2, 3, 4, 5, 6, 7, 8, 9] for _ in range(9)]
    assert not is_complete_and_correct(board, solution)
