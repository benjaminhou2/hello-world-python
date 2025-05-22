import random

class Snake:
    def __init__(self, snake_id, initial_pos, initial_direction='RIGHT', color='GREEN'):
        self.id = snake_id
        self.body = [initial_pos]
        self.direction = initial_direction
        self.grow_pending = False
        self.color = color # For visual distinction in Pygame
        self.score = 0 # Individual score

    def move(self):
        head_x, head_y = self.body[0]
        if self.direction == 'UP':
            new_head = (head_x, head_y - 1)
        elif self.direction == 'DOWN':
            new_head = (head_x, head_y + 1)
        elif self.direction == 'LEFT':
            new_head = (head_x - 1, head_y)
        elif self.direction == 'RIGHT':
            new_head = (head_x + 1, head_y)
        else: # Should not happen
            new_head = (head_x, head_y)


        self.body.insert(0, new_head)

        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

    def turn(self, new_direction):
        # Prevent turning back on itself
        # Also ensure the new_direction is one of the valid ones, in case of erroneous input
        valid_directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        if new_direction not in valid_directions:
            return

        if (new_direction == 'UP' and self.direction != 'DOWN') or \
           (new_direction == 'DOWN' and self.direction != 'UP') or \
           (new_direction == 'LEFT' and self.direction != 'RIGHT') or \
           (new_direction == 'RIGHT' and self.direction != 'LEFT'):
            self.direction = new_direction

    def grow(self):
        self.grow_pending = True
        self.score +=1

    def get_head_position(self):
        return self.body[0]

    def get_body(self):
        return self.body


class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.snake = Snake(snake_id=1, initial_pos=(width // 2, height // 2)) # Default for single player
        self.food = self._generate_food()
        # self.score = 0 # Score is now per snake
        self.game_over = False

    def _generate_food(self):
        occupied_spaces = self.snake.get_body() # Default for single player
        # In TwoPlayerGame, this method will be overridden
        while True:
            food_pos = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if food_pos not in occupied_spaces:
                return food_pos

    def update(self):
        if self.game_over:
            return

        self.snake.move()
        head_pos = self.snake.get_head_position()

        # Collision with food
        if head_pos == self.food:
            self.snake.grow()
            # self.score += 1 # Score handled by snake
            self.food = self._generate_food()

        # Collision with boundaries
        if not (0 <= head_pos[0] < self.width and 0 <= head_pos[1] < self.height):
            self.game_over = True
            return

        # Collision with self
        if head_pos in self.snake.get_body()[1:]:
            self.game_over = True
            return

    def change_snake_direction(self, new_direction): # For single player
        if not self.game_over:
            self.snake.turn(new_direction)

    def get_score(self, snake_id=1): # For single player, default to snake 1
        return self.snake.score

    def is_game_over(self):
        return self.game_over

    def get_snake_body(self, snake_id=1): # For single player
        return self.snake.get_body()

    def get_food_position(self):
        return self.food


class TwoPlayerGame:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.snake1 = Snake(snake_id=1,
                              initial_pos=(width // 4, height // 2),
                              initial_direction='RIGHT',
                              color='GREEN')
        self.snake2 = Snake(snake_id=2,
                              initial_pos=(width * 3 // 4, height // 2),
                              initial_direction='LEFT',
                              color='BLUE') # Ensure a different color for snake2
        self.food = self._generate_food()
        self.game_over = False
        self.winner = None # None, 'player1', 'player2', 'draw'

    def _generate_food(self):
        occupied_spaces = self.snake1.get_body() + self.snake2.get_body()
        while True:
            food_pos = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if food_pos not in occupied_spaces:
                return food_pos

    def update(self):
        if self.game_over:
            return

        self.snake1.move()
        self.snake2.move()

        s1_head = self.snake1.get_head_position()
        s2_head = self.snake2.get_head_position()
        s1_body = self.snake1.get_body()
        s2_body = self.snake2.get_body()

        # 1. Food collision
        s1_ate = (s1_head == self.food)
        s2_ate = (s2_head == self.food)

        if s1_ate:
            self.snake1.grow()
        if s2_ate:
            self.snake2.grow()

        if s1_ate or s2_ate: # If either snake ate, generate new food
            self.food = self._generate_food()

        # --- Collision Detection Logic ---
        # Individual collision event flags
        s1_out_of_bounds = not (0 <= s1_head[0] < self.width and 0 <= s1_head[1] < self.height)
        s2_out_of_bounds = not (0 <= s2_head[0] < self.width and 0 <= s2_head[1] < self.height)

        s1_self_collision = s1_head in s1_body[1:]
        s2_self_collision = s2_head in s2_body[1:]

        heads_collide = (s1_head == s2_head)

        # Distinguish head-on-body from head-on-head
        # A snake hitting the other's head is covered by heads_collide.
        # So, for sX_hits_sY_body, we are interested if sX_head is in sY_body *excluding* sY_head.
        s1_head_hits_s2_body_exclusive = s1_head in s2_body[1:] if not heads_collide else False
        s2_head_hits_s1_body_exclusive = s2_head in s1_body[1:] if not heads_collide else False

        # Determine if each player has met a losing condition
        p1_loses = s1_out_of_bounds or s1_self_collision or s1_head_hits_s2_body_exclusive
        p2_loses = s2_out_of_bounds or s2_self_collision or s2_head_hits_s1_body_exclusive

        # Apply game outcome rules based on manual
        if heads_collide:
            self.game_over = True
            self.winner = 'draw'
        elif p1_loses and p2_loses:
            self.game_over = True
            self.winner = 'draw' # Simultaneous loss from different causes
        elif p1_loses:
            self.game_over = True
            self.winner = 'player2'
        elif p2_loses:
            self.game_over = True
            self.winner = 'player1'
        
        # No return statements needed here as game_over flag handles loop exit in main.py

    def change_snake_direction(self, snake_id, new_direction):
        if self.game_over:
            return
        if snake_id == 1:
            self.snake1.turn(new_direction)
        elif snake_id == 2:
            self.snake2.turn(new_direction)

    def get_scores(self):
        return self.snake1.score, self.snake2.score

    def is_game_over(self):
        return self.game_over

    def get_winner(self):
        return self.winner

    def get_snake1_body(self):
        return self.snake1.get_body()

    def get_snake2_body(self):
        return self.snake2.get_body()

    def get_snake1_color(self):
        return self.snake1.color

    def get_snake2_color(self):
        return self.snake2.color

    def get_food_position(self):
        return self.food
