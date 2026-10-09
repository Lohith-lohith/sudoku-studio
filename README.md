# Sudoku Studio

A responsive Sudoku game built with Python, Flask, HTML, CSS, and JavaScript.

## Features

- Easy, Medium, and Hard difficulty settings
- Backtracking Sudoku solver and unique-solution puzzle generation
- Check button for identifying incorrect entries
- Locked hints
- Game timer and completion message
- Top 10 fastest-times leaderboard using browser `localStorage`
- Light and dark themes
- Responsive interface and keyboard controls
- Automated tests using pytest

## Requirements

- Python 3.10 or newer
- pip

## Install

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Tests

```bash
python -m pytest -v
```

## Structure

- `app.py`: Flask routes and JSON API
- `sudoku.py`: Puzzle generation, solver, and validation
- `templates/index.html`: Game interface
- `static/style.css`: Responsive styles and themes
- `static/game.js`: Game interactions and browser leaderboard
- `tests/`: Automated tests
- `Screenshots/`: Baseline test and Copilot milestone screenshots

## Leaderboard storage

Scores are stored in the current browser's `localStorage`. They persist in the same browser profile but are not synchronized across devices.

## Security note

The default Flask secret key is for local development only. Set a strong `FLASK_SECRET_KEY` environment variable before deploying. The demo game store is in-memory and resets when the server restarts.
