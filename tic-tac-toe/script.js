// Game state
let board = ['', '', '', '', '', '', '', '', ''];
let currentPlayer = 'X';
let gameActive = true;
let scores = {
    X: 0,
    O: 0,
    draws: 0
};

// Win patterns
const winPatterns = [
    [0, 1, 2], // Top row
    [3, 4, 5], // Middle row
    [6, 7, 8], // Bottom row
    [0, 3, 6], // Left column
    [1, 4, 7], // Middle column
    [2, 5, 8], // Right column
    [0, 4, 8], // Diagonal \
    [2, 4, 6]  // Diagonal /
];

// DOM elements
const cells = document.querySelectorAll('.cell');
const gameStatus = document.getElementById('gameStatus');
const resetBtn = document.getElementById('resetBtn');
const currentPlayerDisplay = document.getElementById('currentPlayer');
const turnIndicator = document.getElementById('turnIndicator');
const scoreXDisplay = document.getElementById('scoreX');
const scoreODisplay = document.getElementById('scoreO');
const scoreDrawsDisplay = document.getElementById('scoreDraws');

// Initialize game
function initGame() {
    cells.forEach((cell, index) => {
        cell.addEventListener('click', () => handleCellClick(index));
    });
    resetBtn.addEventListener('click', resetGame);
    updateTurnIndicator();
    updateScoreDisplay();
}

// Handle cell click
function handleCellClick(index) {
    // Check if cell is already taken or game is not active
    if (board[index] !== '' || !gameActive) {
        if (board[index] !== '' && gameActive) {
            // Show invalid move animation
            cells[index].classList.add('invalid-move');
            setTimeout(() => {
                cells[index].classList.remove('invalid-move');
            }, 300);
        }
        return;
    }

    // Make the move
    board[index] = currentPlayer;
    cells[index].textContent = currentPlayer;
    cells[index].classList.add('taken', currentPlayer.toLowerCase());

    // Check for winner
    const winnerInfo = checkWinner();
    if (winnerInfo) {
        handleWin(winnerInfo);
        return;
    }

    // Check for draw
    if (checkDraw()) {
        handleDraw();
        return;
    }

    // Switch player
    currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
    updateTurnIndicator();
}

// Check for winner
function checkWinner() {
    for (let pattern of winPatterns) {
        const [a, b, c] = pattern;
        if (board[a] && board[a] === board[b] && board[a] === board[c]) {
            return {
                winner: board[a],
                pattern: pattern
            };
        }
    }
    return null;
}

// Check for draw
function checkDraw() {
    return board.every(cell => cell !== '');
}

// Handle win
function handleWin(winnerInfo) {
    gameActive = false;
    gameStatus.textContent = `Player ${winnerInfo.winner} Wins! 🎉`;
    gameStatus.classList.add('winner');
    
    // Highlight winning cells
    winnerInfo.pattern.forEach(index => {
        cells[index].classList.add('winning');
    });

    // Update score
    scores[winnerInfo.winner]++;
    updateScoreDisplay();

    // Hide turn indicator
    turnIndicator.style.opacity = '0.5';
}

// Handle draw
function handleDraw() {
    gameActive = false;
    gameStatus.textContent = "It's a Draw! 🤝";
    gameStatus.classList.add('draw');
    
    // Update score
    scores.draws++;
    updateScoreDisplay();

    // Hide turn indicator
    turnIndicator.style.opacity = '0.5';
}

// Reset game
function resetGame() {
    board = ['', '', '', '', '', '', '', '', ''];
    currentPlayer = 'X';
    gameActive = true;
    gameStatus.textContent = '';
    gameStatus.classList.remove('winner', 'draw');
    turnIndicator.style.opacity = '1';

    cells.forEach(cell => {
        cell.textContent = '';
        cell.classList.remove('taken', 'x', 'o', 'winning', 'invalid-move');
    });

    updateTurnIndicator();
}

// Update turn indicator
function updateTurnIndicator() {
    currentPlayerDisplay.textContent = currentPlayer;
    turnIndicator.classList.remove('player-x', 'player-o');
    turnIndicator.classList.add(`player-${currentPlayer.toLowerCase()}`);
}

// Update score display
function updateScoreDisplay() {
    scoreXDisplay.textContent = scores.X;
    scoreODisplay.textContent = scores.O;
    scoreDrawsDisplay.textContent = scores.draws;
}

// Start the game
initGame();

// Made with Bob
