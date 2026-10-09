import pytest

from app import app, GAMES


@pytest.fixture
def client():
    app.config.update(TESTING=True, SECRET_KEY="test-secret-key")
    GAMES.clear()
    with app.test_client() as test_client:
        yield test_client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sudoku Studio" in response.data


def test_new_game_returns_nine_by_nine_board(client):
    response = client.post("/api/new", json={"difficulty": "easy"})
    assert response.status_code == 200
    board = response.get_json()["puzzle"]
    assert len(board) == 9
    assert all(len(row) == 9 for row in board)


def test_invalid_difficulty_is_rejected(client):
    response = client.post("/api/new", json={"difficulty": "expert"})
    assert response.status_code == 400


def test_check_requires_game(client):
    board = [[0] * 9 for _ in range(9)]
    response = client.post("/api/check", json={"board": board})
    assert response.status_code == 400


def test_malformed_board_is_rejected(client):
    client.post("/api/new", json={"difficulty": "easy"})
    response = client.post("/api/check", json={"board": [[0, 0]]})
    assert response.status_code == 400


def test_hint_returns_a_valid_cell(client):
    response = client.post("/api/new", json={"difficulty": "easy"})
    board = response.get_json()["puzzle"]
    hint_response = client.post("/api/hint", json={"board": board})
    assert hint_response.status_code == 200
    hint = hint_response.get_json()
    assert 0 <= hint["row"] < 9
    assert 0 <= hint["col"] < 9
    assert 1 <= hint["value"] <= 9
