# Snake Game - Player Manual

## 1. Game Overview

Welcome to Snake! This classic arcade game has been reimagined with both single-player and exciting two-player versus modes. Control a growing snake, eat food to score points, and try to survive as long as possible. In two-player mode, compete against a friend to be the last snake slithering!

## 2. Getting Started

*   **Launching the Game:**
    *   To start the game, ensure you have Python and Pygame installed.
    *   Navigate to the game's directory in your terminal.
    *   Run the command: `python main.py` or `python3 main.py`
*   **Initial Mode Selection:**
    *   Upon launching, you will see a menu screen.
    *   Press '1' for Single Player mode.
    *   Press '2' for Two-Player VS mode.
    *   Press 'Q' to Quit the game from this screen.

## 3. Single-Player Mode

*   **Objective:**
    *   Survive for as long as you can by maneuvering your snake around the play area.
    *   Achieve the highest possible score by eating food.

*   **Controls:**
    *   **Arrow Keys (Up, Down, Left, Right):** Use these keys to change the direction of your snake.

*   **Gameplay:**
    *   Your snake moves automatically in the direction you've set.
    *   Red blocks will appear on the screen; these are food. Guide your snake to eat them.
    *   Each piece of food eaten will make your snake grow longer and increase your score.
    *   The game ends if your snake's head collides with any of the four walls of the play area or if it collides with any part of its own body.

*   **Scoring:**
    *   Each piece of food consumed adds 1 point to your score.

*   **Game Over:**
    *   When the game ends, a "GAME OVER" message will be displayed along with your final score.
    *   You will have the following options:
        *   Press 'R' to Restart the single-player game.
        *   Press 'M' to return to the Main Menu (mode selection).
        *   Press 'Q' to Quit the game.

## 4. Two-Player Versus (VS) Mode

*   **Objective:**
    *   Compete against another player to be the last snake remaining.
    *   Outmaneuver and outlast your opponent!

*   **Controls:**
    *   **Player 1 (Green Snake):**
        *   Arrow Keys (Up, Down, Left, Right)
    *   **Player 2 (Blue Snake):**
        *   W Key: Up
        *   A Key: Left
        *   S Key: Down
        *   D Key: Right

*   **Gameplay:**
    *   Both players control their snakes on the same screen simultaneously.
    *   Both snakes compete for the same red food blocks.
    *   When a snake eats food, it grows longer, and that player's score increases by 1 point.
    *   **Winning and Losing:**
        *   **Wall Collision:** If a snake hits one of the outer walls, that snake loses, and the other player wins.
        *   **Self-Collision:** If a snake hits its own body, that snake loses, and the other player wins.
        *   **Opponent Collision:** If Snake 1's head hits any part of Snake 2's body, Snake 1 loses, and Snake 2 wins (and vice-versa).
        *   **Head-on-Head Collision:** If both snakes' heads collide at the exact same spot, the game results in a draw.
        *   **Simultaneous Loss:** If both players cause a losing condition for their snake on the same turn (e.g., both hit a wall, or both self-collide, or one hits a wall and the other self-collides), the game is a draw.

*   **Scoring:**
    *   Each piece of food eaten increases the respective player's score by 1 point. Scores are displayed for both players during the game and on the game over screen.

*   **Game Over:**
    *   The game over screen will announce the outcome:
        *   "PLAYER 1 WINS!"
        *   "PLAYER 2 WINS!"
        *   "IT'S A DRAW!"
    *   The final scores for both players will be displayed.
    *   You will have the following options:
        *   Press 'R' to Restart the two-player match.
        *   Press 'M' to return to the Main Menu (mode selection).
        *   Press 'Q' to Quit the game.

## 5. Tips for Playing

*   **Anticipate Your Moves:** Always think a few steps ahead, especially as your snake gets longer.
*   **Use the Walls (Carefully):** Sometimes, running along a wall can be helpful, but be careful not to trap yourself.
*   **Don't Trap Yourself:** Avoid making turns that lead your snake into a closed area with no escape.
*   **Two-Player Tactics:**
    *   **Cut Off Opponent:** Try to maneuver your snake to block your opponent's path, forcing them into a collision.
    *   **Food Control:** Strategically go for food, sometimes even if it means putting yourself in a slightly riskier position to prevent your opponent from getting it.
    *   **Patience:** Sometimes, letting your opponent make a mistake is the best strategy.

Good luck, and have fun playing Snake!
