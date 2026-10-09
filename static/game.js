"use strict";

const $ = (selector) => document.querySelector(selector);
const boardElement = $("#board");
const statusElement = $("#status");
const timerElement = $("#timer");

let puzzle = [];
let board = [];
let selected = null;
let hinted = new Set();
let startedAt = 0;
let timerHandle = null;
let finished = false;
let difficulty = "medium";
let busy = false;

const STORAGE_KEY = "sudoku-studio-leaderboard-v1";
const THEME_KEY = "sudoku-studio-theme-v1";

function setStatus(message) { statusElement.textContent = message; }
function formatTime(seconds) {
  return `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
}
function elapsedSeconds() { return Math.floor((Date.now() - startedAt) / 1000); }
function startTimer() {
  clearInterval(timerHandle);
  startedAt = Date.now();
  timerElement.textContent = "00:00";
  timerHandle = setInterval(() => {
    if (!finished) timerElement.textContent = formatTime(elapsedSeconds());
  }, 1000);
}
function isFixed(row, col) { return puzzle[row][col] !== 0 || hinted.has(`${row},${col}`); }

function renderBoard(errors = []) {
  const errorSet = new Set(errors.map(([r, c]) => `${r},${c}`));
  boardElement.replaceChildren();
  for (let r = 0; r < 9; r++) {
    for (let c = 0; c < 9; c++) {
      const key = `${r},${c}`;
      const cell = document.createElement("button");
      cell.type = "button";
      cell.className = "cell";
      cell.setAttribute("aria-label", `Row ${r + 1}, column ${c + 1}, ${board[r][c] || "empty"}`);
      if ((Math.floor(r / 3) + Math.floor(c / 3)) % 2 === 1) cell.classList.add("box-shade");
      if (puzzle[r][c] !== 0) cell.classList.add("fixed");
      if (hinted.has(key)) cell.classList.add("fixed", "hinted");
      if (selected && selected[0] === r && selected[1] === c) cell.classList.add("selected");
      if (errorSet.has(key)) cell.classList.add("error");
      cell.textContent = board[r][c] || "";
      cell.disabled = finished || isFixed(r, c);
      cell.addEventListener("click", () => { selected = [r, c]; renderBoard(errors); });
      boardElement.appendChild(cell);
    }
  }
}

function renderNumberPad() {
  const pad = $("#numberPad");
  pad.replaceChildren();
  for (let n = 1; n <= 9; n++) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = n;
    button.setAttribute("aria-label", `Enter ${n}`);
    button.addEventListener("click", () => enterNumber(n));
    pad.appendChild(button);
  }
}

async function apiPost(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed.");
  return data;
}

async function enterNumber(number) {
  if (finished || busy || !selected) {
    if (!selected) setStatus("Select an empty cell first.");
    return;
  }
  const [r, c] = selected;
  if (isFixed(r, c)) return;
  board[r][c] = number;
  renderBoard();
  setStatus("Checking entry…");
  try {
    const data = await apiPost("/api/check", { board });
    renderBoard(data.incorrect);
    if (data.incorrect.some(([row, col]) => row === r && col === c)) {
      setStatus("Incorrect entry. Try another number.");
    } else {
      setStatus("Entry is correct so far.");
    }
  } catch (error) { setStatus(error.message); }
}

function eraseCell() {
  if (!selected || finished || busy) return;
  const [r, c] = selected;
  if (isFixed(r, c)) return;
  board[r][c] = 0;
  renderBoard();
  setStatus("Cell erased.");
}

async function newGame() {
  if (busy) return;
  busy = true;
  $("#newGame").disabled = true;
  setStatus("Generating a unique puzzle…");
  try {
    difficulty = $("#difficulty").value;
    const data = await apiPost("/api/new", { difficulty });
    puzzle = data.puzzle;
    board = puzzle.map((row) => row.slice());
    hinted = new Set();
    selected = null;
    finished = false;
    renderBoard();
    startTimer();
    setStatus(`${difficulty[0].toUpperCase() + difficulty.slice(1)} puzzle ready.`);
  } catch (error) { setStatus(error.message); }
  finally { busy = false; $("#newGame").disabled = false; }
}

async function checkGame() {
  if (finished || busy || !puzzle.length) return;
  busy = true;
  try {
    const data = await apiPost("/api/check", { board });
    renderBoard(data.incorrect);
    if (data.solved) {
      finished = true;
      clearInterval(timerHandle);
      const seconds = elapsedSeconds();
      setStatus(`Congratulations! Solved in ${formatTime(seconds)}.`);
      renderBoard();
      await saveScore(seconds);
    } else if (data.incorrect.length) {
      setStatus(`${data.incorrect.length} incorrect cell(s) highlighted.`);
    } else {
      setStatus("No incorrect entries found so far. Keep going!");
    }
  } catch (error) { setStatus(error.message); }
  finally { busy = false; }
}

async function giveHint() {
  if (finished || busy || !puzzle.length) return;
  busy = true;
  try {
    const data = await apiPost("/api/hint", { board });
    board[data.row][data.col] = data.value;
    hinted.add(`${data.row},${data.col}`);
    selected = [data.row, data.col];
    renderBoard();
    setStatus("Hint added. That cell is now locked.");
  } catch (error) { setStatus(error.message); }
  finally { busy = false; }
}

function loadScores() {
  try {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(data) ? data.filter(item =>
      item && typeof item.name === "string" &&
      Number.isFinite(item.seconds) &&
      ["easy", "medium", "hard"].includes(item.difficulty)
    ) : [];
  } catch { return []; }
}

function renderLeaderboard() {
  const list = $("#leaderboard");
  list.replaceChildren();
  const scores = loadScores().sort((a, b) => a.seconds - b.seconds).slice(0, 10);
  if (!scores.length) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "No completed games yet.";
    list.appendChild(empty);
    return;
  }
  scores.forEach(score => {
    const li = document.createElement("li");
    li.textContent = `${score.name} — ${formatTime(score.seconds)} (${score.difficulty})`;
    list.appendChild(li);
  });
}

async function saveScore(seconds) {
  const nameInput = prompt("Puzzle solved! Enter your name for the leaderboard:");
  if (nameInput === null) { renderLeaderboard(); return; }
  const name = nameInput.trim().slice(0, 30) || "Player";
  const scores = loadScores();
  scores.push({ name, seconds, difficulty, date: new Date().toISOString() });
  scores.sort((a, b) => a.seconds - b.seconds);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(scores.slice(0, 10)));
  } catch { setStatus("Solved, but the browser could not save the score."); }
  renderLeaderboard();
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  $("#themeToggle").textContent = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
}

$("#newGame").addEventListener("click", newGame);
$("#checkGame").addEventListener("click", checkGame);
$("#hintGame").addEventListener("click", giveHint);
$("#erase").addEventListener("click", eraseCell);
$("#themeToggle").addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(next);
  try { localStorage.setItem(THEME_KEY, next); } catch {}
});

document.addEventListener("keydown", event => {
  if (event.ctrlKey || event.metaKey || event.altKey) return;
  if (/^[1-9]$/.test(event.key)) enterNumber(Number(event.key));
  if (event.key === "Backspace" || event.key === "Delete") eraseCell();
  if (selected && ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
    event.preventDefault();
    const [r, c] = selected;
    const offsets = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
    const [dr, dc] = offsets[event.key];
    selected = [(r + dr + 9) % 9, (c + dc + 9) % 9];
    renderBoard();
  }
});

applyTheme(localStorage.getItem(THEME_KEY) || "light");
renderNumberPad();
renderLeaderboard();
newGame();
