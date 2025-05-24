import pygame
import sys
from snake_core import Game, TwoPlayerGame # Import TwoPlayerGame

# --- Constants ---
SCREEN_WIDTH = 800  # Increased from 600
SCREEN_HEIGHT = 600 # Increased from 400
GRID_SIZE = 20  # Size of each grid cell (kept same)
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE   # Now 40
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE # Now 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0) # Default for P1
BLUE = (0, 0, 255) # For P2
RED = (255, 0, 0) # Food
GRAY = (200, 200, 200) # For grid lines
OBSTACLE_COLOR = (100, 100, 100) # Dark Gray for obstacles

# Power-up Colors (mapping string names from snake_core to Pygame colors)
POWERUP_PYGAME_COLORS = {
    'LIGHTBLUE': (173, 216, 230),
    'ORANGE': (255, 165, 0),
    'PURPLE': (128, 0, 128),
}

FPS = 7  # Frames per second, controls game speed (decreased from 10)

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48) # Increased font size
game_over_font = pygame.font.SysFont(None, 100) # Increased game over font size

# --- Helper Functions ---
def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_snake(snake_body, color=GREEN): # Added color parameter
    for segment in snake_body:
        pygame.draw.rect(screen, color, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_foods(foods_list): # MODIFIED: Renamed and takes a list
    for food_position in foods_list: # MODIFIED: Loop through the list
        pygame.draw.rect(screen, RED, (food_position[0] * GRID_SIZE, food_position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def display_score_single(game_obj): # Modified signature to take game object
    score = game_obj.get_score()
    score_text_str = f"Score: {score}"

    snake = game_obj.snake # Access the snake instance
    if snake.active_powerup_type and snake.powerup_effect_timer > 0:
        powerup_def = game_obj.POWERUP_DEFINITIONS.get(snake.active_powerup_type)
        if powerup_def:
            symbol = powerup_def['symbol']
            timer_secs = round(snake.powerup_effect_timer / FPS)
            score_text_str += f" [{symbol}: {timer_secs}s]"

    score_text_render = font.render(score_text_str, True, BLACK)
    screen.blit(score_text_render, (10, 10))

def draw_obstacles(obstacle_coords):
    for x, y in obstacle_coords:
        rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, OBSTACLE_COLOR, rect)

def draw_powerup_item(details):
    if not details:
        return
    
    pup_color_str = details['color']
    pup_pygame_color = POWERUP_PYGAME_COLORS.get(pup_color_str, BLACK) # Default to BLACK if color str not found
    pup_rect = pygame.Rect(details['position'][0] * GRID_SIZE, details['position'][1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, pup_pygame_color, pup_rect)
    
    symbol_text = font.render(details['symbol'], True, BLACK) # Black symbol text
    text_rect = symbol_text.get_rect(center=pup_rect.center)
    screen.blit(symbol_text, text_rect)

def display_scores_two_player(game_obj): # Pass the whole game object
    s1_score = game_obj.snake1.score
    s2_score = game_obj.snake2.score
    
    # Display Target Score if applicable
    if game_obj.game_mode == 'first_to_x':
        target_text = font.render(f"Target: {game_obj.target_score}", True, BLACK)
        screen.blit(target_text, (SCREEN_WIDTH // 2 - target_text.get_width() // 2, 10))

    p1_text_str = f"P1 Score: {s1_score}"
    if game_obj.snake1.active_powerup_type:
        symbol = game_obj.POWERUP_DEFINITIONS[game_obj.snake1.active_powerup_type]['symbol']
        timer_secs = round(game_obj.snake1.powerup_effect_timer / FPS)
        p1_text_str += f" [{symbol}: {timer_secs}s]"
        
    p2_text_str = f"P2 Score: {s2_score}"
    if game_obj.snake2.active_powerup_type:
        symbol = game_obj.POWERUP_DEFINITIONS[game_obj.snake2.active_powerup_type]['symbol']
        timer_secs = round(game_obj.snake2.powerup_effect_timer / FPS)
        p2_text_str += f" [{symbol}: {timer_secs}s]"

    score1_text_render = font.render(p1_text_str, True, game_obj.get_snake1_color()) # Use snake's actual color
    score2_text_render = font.render(p2_text_str, True, game_obj.get_snake2_color()) # Use snake's actual color
    
    screen.blit(score1_text_render, (10, 10))
    screen.blit(score2_text_render, (SCREEN_WIDTH - score2_text_render.get_width() - 10, 10))


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

def display_map_selection_menu(): # Keep this function as is
    screen.fill(WHITE)
    title_text = game_over_font.render("Select Map", True, BLACK)
    map0_text = font.render("0: Classic (No Obstacles)", True, BLACK)
    map1_text = font.render("1: Central Blocks", True, BLACK)
    map2_text = font.render("2: Pillars", True, BLACK)
    back_text = font.render("Press B to Go Back to Main Menu", True, BLACK)

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 5 - title_text.get_height() // 2))
    screen.blit(map0_text, (SCREEN_WIDTH // 2 - map0_text.get_width() // 2, SCREEN_HEIGHT * 2 // 5 - map0_text.get_height() // 2))
    screen.blit(map1_text, (SCREEN_WIDTH // 2 - map1_text.get_width() // 2, SCREEN_HEIGHT * 3 // 5 - map1_text.get_height() // 2))
    screen.blit(map2_text, (SCREEN_WIDTH // 2 - map2_text.get_width() // 2, SCREEN_HEIGHT * 4 // 5 - map2_text.get_height() // 2 - 20))
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT * 4 // 5 + 30 ))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    return 0
                if event.key == pygame.K_1:
                    return 1
                if event.key == pygame.K_2:
                    return 2
                if event.key == pygame.K_b: 
                    return None 
        clock.tick(5)

def display_game_mode_selection_menu():
    screen.fill(WHITE)
    title_text = game_over_font.render("Select Game Mode", True, BLACK)
    mode1_text = font.render("1: Last Snake Standing", True, BLACK)
    mode2_text = font.render("2: First to 10 Points", True, BLACK)
    back_text = font.render("Press B to Go Back to Map Selection", True, BLACK)

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 5 - title_text.get_height() // 2))
    screen.blit(mode1_text, (SCREEN_WIDTH // 2 - mode1_text.get_width() // 2, SCREEN_HEIGHT * 2 // 5 - mode1_text.get_height() // 2))
    screen.blit(mode2_text, (SCREEN_WIDTH // 2 - mode2_text.get_width() // 2, SCREEN_HEIGHT * 3 // 5 - mode2_text.get_height() // 2))
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT * 4 // 5 + 30 ))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return {'game_mode': 'last_snake'}
                if event.key == pygame.K_2:
                    return {'game_mode': 'first_to_x', 'target_score': 10}
                if event.key == pygame.K_b: # Go back
                    return None # Indicates going back to map selection
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
        draw_foods(game.get_foods()) # MODIFIED: Call draw_foods with game.get_foods()
        
        # Display powerup if active on map (for single player)
        powerup_details_sp = game.get_powerup_item_details()
        if powerup_details_sp:
            draw_powerup_item(powerup_details_sp)
            
        display_score_single(game) # Pass the whole game object

        if game.is_game_over():
            action = display_game_over_single(game.get_score())
            if action == 'restart':
                single_player_game_loop() # Restart this mode
            elif action == 'menu':
                return # Go back to main_menu
            return # Exit current loop instance

        pygame.display.flip()
        clock.tick(FPS)

def two_player_game_loop(selected_map_id, game_mode_details): # Added game_mode_details
    game = TwoPlayerGame(GRID_WIDTH, GRID_HEIGHT, 
                         map_id=selected_map_id, 
                         game_mode=game_mode_details['game_mode'], 
                         target_score=game_mode_details.get('target_score', 10)) # Default target_score if not in dict
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
        draw_obstacles(game.get_obstacles()) # Draw obstacles first
        draw_snake(game.get_snake1_body(), game.get_snake1_color()) # P1
        draw_snake(game.get_snake2_body(), game.get_snake2_color()) # P2
        draw_foods(game.get_foods()) # MODIFIED: Call draw_foods with game.get_foods()
        
        powerup_details = game.get_powerup_item_details()
        if powerup_details:
            draw_powerup_item(powerup_details)
            
        display_scores_two_player(game) # Pass the game object

        if game.is_game_over():
            s1_final_score, s2_final_score = game.get_scores()
            action = display_game_over_two_player(game.get_winner(), s1_final_score, s2_final_score)
            if action == 'restart':
                two_player_game_loop(selected_map_id, game_mode_details) # Restart with same map and mode
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
            selected_map_id = display_map_selection_menu()
            if selected_map_id is not None: 
                game_mode_details = display_game_mode_selection_menu()
                if game_mode_details is not None: # If a game mode was selected
                    two_player_game_loop(selected_map_id, game_mode_details)
            # If selected_map_id or game_mode_details is None, loop back to main_menu

if __name__ == "__main__":
    main_menu()
