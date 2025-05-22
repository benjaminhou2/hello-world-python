import pygame
import sys
from snake_core import Game, TwoPlayerGame # Import TwoPlayerGame

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20  # Size of each grid cell
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0) # Default for P1
BLUE = (0, 0, 255) # For P2
RED = (255, 0, 0)
GRAY = (200, 200, 200) # For grid lines

FPS = 10  # Frames per second, controls game speed

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 35)
game_over_font = pygame.font.SysFont(None, 75)

# --- Helper Functions ---
def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_snake(snake_body, color=GREEN): # Added color parameter
    for segment in snake_body:
        pygame.draw.rect(screen, color, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_food(food_position):
    pygame.draw.rect(screen, RED, (food_position[0] * GRID_SIZE, food_position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def display_score_single(score):
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

def display_scores_two_player(score1, score2):
    score1_text = font.render(f"P1 Score: {score1}", True, GREEN)
    score2_text = font.render(f"P2 Score: {score2}", True, BLUE)
    screen.blit(score1_text, (10, 10))
    screen.blit(score2_text, (SCREEN_WIDTH - score2_text.get_width() - 10, 10))


def display_game_over_single(score):
    game_over_text = game_over_font.render("GAME OVER", True, RED)
    score_text = font.render(f"Final Score: {score}", True, BLACK)
    instructions_text = font.render("R: Restart | M: Menu | Q: Quit", True, BLACK)

    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3 - game_over_text.get_height() // 2))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - score_text.get_height() // 2))
    screen.blit(instructions_text, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, SCREEN_HEIGHT * 2 // 3 - instructions_text.get_height() // 2))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    return 'restart'
                if event.key == pygame.K_m:
                    return 'menu'
        clock.tick(5)

def display_game_over_two_player(winner, score1, score2):
    if winner == 'draw':
        message = "IT'S A DRAW!"
        color = BLACK
    elif winner == 'player1':
        message = "PLAYER 1 WINS!"
        color = GREEN
    else: # player2
        message = "PLAYER 2 WINS!"
        color = BLUE

    game_over_text = game_over_font.render(message, True, color)
    score1_text = font.render(f"P1 Final Score: {score1}", True, BLACK)
    score2_text = font.render(f"P2 Final Score: {score2}", True, BLACK)
    instructions_text = font.render("R: Restart | M: Menu | Q: Quit", True, BLACK)

    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3 - game_over_text.get_height() // 2))
    screen.blit(score1_text, (SCREEN_WIDTH // 2 - score1_text.get_width() // 2, SCREEN_HEIGHT // 2 - score1_text.get_height() // 2 - 20))
    screen.blit(score2_text, (SCREEN_WIDTH // 2 - score2_text.get_width() // 2, SCREEN_HEIGHT // 2 - score2_text.get_height() // 2 + 20))
    screen.blit(instructions_text, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, SCREEN_HEIGHT * 2 // 3 - instructions_text.get_height() // 2))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    return 'restart'
                if event.key == pygame.K_m:
                    return 'menu'
        clock.tick(5)

def display_mode_selection():
    screen.fill(WHITE)
    title_text = game_over_font.render("Snake Game", True, BLACK)
    single_player_text = font.render("Press 1 for Single Player", True, BLACK)
    two_player_text = font.render("Press 2 for Two Players (VS)", True, BLACK)
    quit_text = font.render("Press Q to Quit", True, BLACK)

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4 - title_text.get_height() // 2))
    screen.blit(single_player_text, (SCREEN_WIDTH // 2 - single_player_text.get_width() // 2, SCREEN_HEIGHT // 2 - single_player_text.get_height() // 2 - 20))
    screen.blit(two_player_text, (SCREEN_WIDTH // 2 - two_player_text.get_width() // 2, SCREEN_HEIGHT // 2 - two_player_text.get_height() // 2 + 20))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT * 3 // 4 - quit_text.get_height() // 2))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 'single'
                if event.key == pygame.K_2:
                    return 'two_player'
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(5)


# --- Game Loops ---
def single_player_game_loop():
    game = Game(GRID_WIDTH, GRID_HEIGHT)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not game.is_game_over():
                    if event.key == pygame.K_UP:
                        game.change_snake_direction('UP')
                    elif event.key == pygame.K_DOWN:
                        game.change_snake_direction('DOWN')
                    elif event.key == pygame.K_LEFT:
                        game.change_snake_direction('LEFT')
                    elif event.key == pygame.K_RIGHT:
                        game.change_snake_direction('RIGHT')

        if not game.is_game_over():
            game.update()

        screen.fill(WHITE)
        draw_grid()
        draw_snake(game.get_snake_body()) # Default color (GREEN)
        draw_food(game.get_food_position())
        display_score_single(game.get_score())

        if game.is_game_over():
            action = display_game_over_single(game.get_score())
            if action == 'restart':
                single_player_game_loop() # Restart this mode
            elif action == 'menu':
                return # Go back to main_menu
            return # Exit current loop instance

        pygame.display.flip()
        clock.tick(FPS)

def two_player_game_loop():
    game = TwoPlayerGame(GRID_WIDTH, GRID_HEIGHT)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not game.is_game_over():
                    # Player 1 Controls (Arrows)
                    if event.key == pygame.K_UP:
                        game.change_snake_direction(1, 'UP')
                    elif event.key == pygame.K_DOWN:
                        game.change_snake_direction(1, 'DOWN')
                    elif event.key == pygame.K_LEFT:
                        game.change_snake_direction(1, 'LEFT')
                    elif event.key == pygame.K_RIGHT:
                        game.change_snake_direction(1, 'RIGHT')
                    # Player 2 Controls (WASD)
                    elif event.key == pygame.K_w:
                        game.change_snake_direction(2, 'UP')
                    elif event.key == pygame.K_s:
                        game.change_snake_direction(2, 'DOWN')
                    elif event.key == pygame.K_a:
                        game.change_snake_direction(2, 'LEFT')
                    elif event.key == pygame.K_d:
                        game.change_snake_direction(2, 'RIGHT')

        if not game.is_game_over():
            game.update()

        screen.fill(WHITE)
        draw_grid()
        draw_snake(game.get_snake1_body(), game.get_snake1_color()) # P1
        draw_snake(game.get_snake2_body(), game.get_snake2_color()) # P2
        draw_food(game.get_food_position())
        s1_score, s2_score = game.get_scores()
        display_scores_two_player(s1_score, s2_score)

        if game.is_game_over():
            action = display_game_over_two_player(game.get_winner(), s1_score, s2_score)
            if action == 'restart':
                two_player_game_loop() # Restart this mode
            elif action == 'menu':
                return # Go back to main_menu
            return # Exit current loop instance

        pygame.display.flip()
        clock.tick(FPS)

def main_menu():
    while True:
        mode = display_mode_selection()
        if mode == 'single':
            single_player_game_loop()
        elif mode == 'two_player':
            two_player_game_loop()
        # If a game loop returns, it means 'menu' was selected, so display_mode_selection() will run again.

if __name__ == "__main__":
    main_menu()
