# Project Instructions: Sudoku Studio

## Technology
- Python 3 and Flask for the backend.
- HTML, CSS, and vanilla JavaScript for the frontend.
- pytest for automated tests.

## Code quality
- Prefer small, readable functions and meaningful names.
- Use Flask JSON APIs with appropriate HTTP status codes.
- Never expose the answer key in the initial puzzle response.
- Keep original clues immutable and validate submitted data.
- Use a backtracking solver and verify puzzle uniqueness.
- Avoid unnecessary dependencies.

## Required functionality
- Easy, Medium, and Hard difficulty levels.
- Unique-solution Sudoku generation.
- Immediate feedback and a Check button.
- One-cell hints that lock the revealed value.
- Completion message and elapsed-time tracking.
- Persistent top-10 leaderboard using localStorage.
- Light and dark themes.
- Responsive 9x9 grid with contrasting 3x3 regions.

## Testing
- Run pytest after meaningful changes.
- Test successful and invalid requests.
- Never claim tests passed unless they were executed.
- Add tests for new behavior and edge cases.

## Accessibility
- Use semantic HTML, keyboard input, visible focus,
  readable contrast, and live status announcements.
