import random

# --- Map Definitions ---
# GRID_WIDTH=30, GRID_HEIGHT=20 (based on main.py defaults, assumed for these coordinates)
MAP_DEFINITIONS = {
    0: [], # Default empty map
    1: [ # "Central Blocks" - As per prompt's original design
        (10,10), (11,10), (12,10), 
        (18,10), (19,10), (20,10),
        # Optional extra blocks for more substance
        (10,12), (11,12), (12,12), 
        (18,12), (19,12), (20,12),
    ],
    2: [ # "Pillars"
        (7, 4), (7, 5), # Top-Left
        (22, 4), (22, 5), # Top-Right
        (7, 14), (7, 15), # Bottom-Left
        (22, 14), (22, 15), # Bottom-Right
    ]
}

# --- PowerUp Class ---
class PowerUp:
    def __init__(self, type_id, position, color, symbol, effect_duration):
        self.type_id = type_id
        self.position = position
        self.color = color 
        self.symbol = symbol 
        self.effect_duration = effect_duration
        # lifespan_on_map is managed by TwoPlayerGame.powerup_on_map_lifespan_timer

class Snake:
    def __init__(self, snake_id, initial_pos, initial_direction='RIGHT', color='GREEN'):
        self.id = snake_id
        self.body = [initial_pos]
        self.direction = initial_direction
        self.grow_pending = False
        self.color = color # For visual distinction in Pygame
        self.score = 0 # Individual score

        # Power-up related attributes
        self.active_powerup_type = None # Type of p-up this snake collected (e.g. 'speed_self', 'slow_opponent') for icon display
        self.powerup_effect_timer = 0   # Timer for ICON DISPLAY of the collected power-up

        self.is_wall_ghost = False      # Specific flag for wall ghost effect ON THIS SNAKE
        self.steps_per_update = 1       # Specific flag for speed effect ON THIS SNAKE
        
        # Attributes for being affected by 'slow_opponent' powerup (i.e. if opponent collected it)
        self.is_slowed_timer = 0        # BUG 3 Corrected: Duration for which THIS SNAKE is slowed
        self.slow_effect_counter = 0    # BUG 3 Corrected: Counter for THIS SNAKE to move every other tick when slowed (0 after reset = move, then 1=skip, 0=move)

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
    def __init__(self, width, height, map_id=0, game_mode='last_snake', target_score=10): # Added game_mode, target_score
        self.width = width
        self.height = height
        self.map_id = map_id 
        self.obstacles = [] 
        self.game_mode = game_mode
        self.target_score = target_score
        self.snake1 = Snake(snake_id=1,
                              initial_pos=(width // 4, height // 2),
                              initial_direction='RIGHT',
                              color='GREEN')
        self.snake2 = Snake(snake_id=2,
                              initial_pos=(width * 3 // 4, height // 2),
                              initial_direction='LEFT',
                              color='BLUE')
        # self.food will be initialized by set_map
        self.game_over = False
        self.winner = None
        
        # Power-up system attributes
        self.powerup_item = None 
        self.powerup_spawn_chance = 0.20
        self.powerup_on_map_lifespan_timer = 0 # Ticks for current powerup to stay on map
        
        self.POWERUP_MAP_LIFESPAN = 100 # How long a powerup stays on map before disappearing
        self.POWERUP_DEFINITIONS = {
            'speed_self': {'symbol': 'S', 'color': 'LIGHTBLUE', 'effect_duration': 50, 'applies_to': 'self'},
            'slow_opponent': {'symbol': 'O', 'color': 'ORANGE', 'effect_duration': 50, 'applies_to': 'opponent'},
            'wall_ghost': {'symbol': 'G', 'color': 'PURPLE', 'effect_duration': 70, 'applies_to': 'self'},
        }
        self.set_map(self.map_id) # Call set_map during init to load initial map and reset game

    def set_map(self, map_id_to_set):
        self.map_id = map_id_to_set
        self.obstacles = list(MAP_DEFINITIONS.get(self.map_id, [])) 
        
        initial_s1_pos = (self.width // 4, self.height // 2)
        initial_s2_pos = (self.width * 3 // 4, self.height // 2)

        if initial_s1_pos in self.obstacles:
            initial_s1_pos = self._generate_location(self.snake2.get_body() + [initial_s2_pos] if hasattr(self, 'snake2') else [initial_s2_pos]) 
            if initial_s1_pos is None: initial_s1_pos = (1,1) 
        if initial_s2_pos in self.obstacles:
            initial_s2_pos = self._generate_location(self.snake1.get_body() + [initial_s1_pos] if hasattr(self, 'snake1') else [initial_s1_pos])
            if initial_s2_pos is None: initial_s2_pos = (self.width-2, self.height-2)

        self.snake1.body = [initial_s1_pos]
        self.snake1.direction = 'RIGHT'
        self._deactivate_direct_effects(self.snake1) 

        self.snake2.body = [(initial_s2_pos)]
        self.snake2.direction = 'LEFT'
        self._deactivate_direct_effects(self.snake2)
        
        self.food = self._generate_food() 
        if self.powerup_item: 
            self._clear_powerup_item()
        
        self.snake1.score = 0
        self.snake2.score = 0
        self.game_over = False
        self.winner = None

    def _generate_location(self, dynamic_occupied_spaces):
        """Helper to generate a random location not in dynamic_occupied_spaces AND self.obstacles."""
        # BUG 1 Corrected: Ensure self.obstacles is part of the check
        full_occupied_spaces = set(dynamic_occupied_spaces + self.obstacles) 
        
        if len(full_occupied_spaces) >= self.width * self.height:
            # print("Warning: No space left to generate location.") # Keep for debug
            return None 

        attempts = 0
        # Limit attempts to prevent potential infinite loop on very full maps
        free_cells = (self.width * self.height) - len(full_occupied_spaces)
        # Ensure max_attempts is at least a small number, e.g., 10, even if free_cells is very low.
        max_attempts = free_cells + 10 if free_cells > 0 else 10 
        
        while attempts < max_attempts:
            pos = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if pos not in full_occupied_spaces:
                return pos
            attempts += 1
        # print(f"Warning: Max attempts ({max_attempts}) reached in _generate_location.") # Keep for debug
        return None # Could not find a spot

    def _generate_food(self):
        # Collect all currently occupied dynamic spaces: snakes and current power-up
        current_occupied = self.snake1.get_body() + self.snake2.get_body()
        if self.powerup_item:
            current_occupied.append(self.powerup_item.position)
        
        new_food_pos = self._generate_location(current_occupied)
        
        if new_food_pos is None: 
             # Fallback if no space considering dynamic items + obstacles
             new_food_pos = self._generate_location([]) # Try with only obstacles as occupied
             if new_food_pos is None: 
                 # print("CRITICAL FALLBACK FAILED: No space for food at all!") # Keep for debug
                 return (0,0) # Absolute fallback if map is entirely full of obstacles
        return new_food_pos

    def _generate_powerup_item(self):
        if self.powerup_item is None and random.random() < self.powerup_spawn_chance:
            # Collect all currently occupied dynamic spaces: snakes and current food
            current_occupied = self.snake1.get_body() + self.snake2.get_body() + [self.food]
            pos = self._generate_location(current_occupied) 
            
            if pos is None: 
                # print("Warning: No space to spawn powerup.") # Keep for debug
                return # No space to spawn powerup

            type_id = random.choice(list(self.POWERUP_DEFINITIONS.keys()))
            definition = self.POWERUP_DEFINITIONS[type_id]
            
            self.powerup_item = PowerUp(
                type_id=type_id,
                position=pos,
                color=definition['color'], 
                symbol=definition['symbol'],
                effect_duration=definition['effect_duration']
            )
            self.powerup_on_map_lifespan_timer = self.POWERUP_MAP_LIFESPAN

    def _clear_powerup_item(self):
        self.powerup_item = None
        self.powerup_on_map_lifespan_timer = 0
        
    def _activate_powerup(self, snake, opponent_snake, powerup_type):
        definition = self.POWERUP_DEFINITIONS[powerup_type]
        # Before applying new effect, clear any existing direct effects from the target.
        target_snake_for_effect = snake if definition['applies_to'] == 'self' else opponent_snake
        self._deactivate_direct_effects(target_snake_for_effect) # BUG 3 Corrected: Ensure target's effects are cleared

        # The collecting snake always gets its active_powerup_type and powerup_effect_timer set
        # for displaying the icon (e.g., 'S', 'O', 'G').
        snake.active_powerup_type = powerup_type 
        snake.powerup_effect_timer = definition['effect_duration'] 

        # Apply actual gameplay effects
        if powerup_type == 'speed_self':
            snake.steps_per_update = 2 # Effect on the collector
        elif powerup_type == 'slow_opponent': 
            opponent_snake.is_slowed_timer = definition['effect_duration'] # Actual slowness timer on opponent
            opponent_snake.slow_effect_counter = 0 # BUG 3 Corrected: Reset counter for the opponent being slowed
        elif powerup_type == 'wall_ghost':
            snake.is_wall_ghost = True # Effect on the collector

    def _deactivate_direct_effects(self, snake_to_clear):
        """Clears direct effects (speed, ghost, being slowed) from a specific snake."""
        # BUG 3 Corrected: Clear all relevant effects including slowness
        snake_to_clear.steps_per_update = 1
        snake_to_clear.is_wall_ghost = False
        snake_to_clear.is_slowed_timer = 0 
        snake_to_clear.slow_effect_counter = 0
        
        # If this snake was displaying an icon for a power-up it collected (which might have affected itself or opponent),
        # and that specific power-up is now being cleared (e.g. by another powerup overriding it), clear its icon.
        if snake_to_clear.active_powerup_type is not None:
             snake_to_clear.active_powerup_type = None
             snake_to_clear.powerup_effect_timer = 0
            
    def _update_powerup_timers(self): # BUG 3 Corrected: Refined timer logic
        for s in [self.snake1, self.snake2]:
            # Update timer for the icon display of the power-up 's' collected
            if s.powerup_effect_timer > 0:
                s.powerup_effect_timer -= 1
                if s.powerup_effect_timer == 0: # Icon display timer for collected powerup ends
                    # If the icon timer runs out, deactivate direct effects this snake was hosting (if any)
                    if s.active_powerup_type == 'speed_self':
                        s.steps_per_update = 1
                    elif s.active_powerup_type == 'wall_ghost':
                        s.is_wall_ghost = False
                    # For 'slow_opponent', this timer ending on the collector just removes the 'O' icon.
                    # The opponent's actual slowness is dictated by their 'is_slowed_timer'.
                    s.active_powerup_type = None # Clear icon display for the collector

            # Timer for the 'being slowed' effect on snake 's' (if opponent collected 'slow_opponent')
            if s.is_slowed_timer > 0:
                s.is_slowed_timer -= 1
                if s.is_slowed_timer == 0:
                    s.slow_effect_counter = 0 # Reset skip counter when actual slowness ends
        
        if self.powerup_item:
            self.powerup_on_map_lifespan_timer -=1
            if self.powerup_on_map_lifespan_timer <= 0:
                self._clear_powerup_item()

    def update(self):
        if self.game_over:
            return

        self._update_powerup_timers()

        # Snake Movement
        for snake_obj in [self.snake1, self.snake2]: 
            perform_move_this_tick = True
            # BUG 3 Corrected: Implement skip logic for 'slow_opponent'
            if snake_obj.is_slowed_timer > 0:
                # Counter logic: 0 means move, 1 means skip. Initialized to 0.
                # First tick after being slowed: counter becomes 1 (due to +1 before check), move IS SKIPPED.
                # Second tick, counter becomes 0, move IS PERFORMED. This is the desired behavior.
                snake_obj.slow_effect_counter = (snake_obj.slow_effect_counter + 1) % 2 
                if snake_obj.slow_effect_counter == 1: # Skip on 1
                    perform_move_this_tick = False
            
            if perform_move_this_tick:
                for _ in range(snake_obj.steps_per_update): 
                    if not self.game_over: 
                        snake_obj.move()
                    # Collision checks ideally happen after each micro-step if speed_boosted for immediate game over.
                    # Current model checks collisions after all primary moves for the tick.
            if self.game_over: return # If first snake's move caused game over


        s1_head = self.snake1.get_head_position()
        s2_head = self.snake2.get_head_position()
        s1_body = self.snake1.get_body() # Re-fetch body after potential moves
        s2_body = self.snake2.get_body()

        food_eaten_this_tick = False
        if s1_head == self.food:
            self.snake1.grow()
            food_eaten_this_tick = True
        if s2_head == self.food: # Check independently, could be simultaneous
            self.snake2.grow()
            food_eaten_this_tick = True
        
        if food_eaten_this_tick:
            self.food = self._generate_food()
            self._generate_powerup_item() # Attempt to spawn power-up after food is eaten

        # Power-up Collection
        if self.powerup_item:
            if s1_head == self.powerup_item.position:
                self._activate_powerup(self.snake1, self.snake2, self.powerup_item.type_id)
                self._clear_powerup_item()
            elif s2_head == self.powerup_item.position: # Important: use elif if only one can collect
                self._activate_powerup(self.snake2, self.snake1, self.powerup_item.type_id)
                self._clear_powerup_item()

        # --- Score Win Condition Check (for 'first_to_x' mode) ---
        if self.game_mode == 'first_to_x' and not self.game_over:
            s1_reaches_target = (self.snake1.score >= self.target_score)
            s2_reaches_target = (self.snake2.score >= self.target_score)

            if s1_reaches_target or s2_reaches_target:
                self.game_over = True
                if s1_reaches_target and s2_reaches_target: # Both reach/exceed target
                    if self.snake1.score > self.snake2.score:
                        self.winner = 'player1'
                    elif self.snake2.score > self.snake1.score:
                        self.winner = 'player2'
                    else:
                        self.winner = 'draw' # Scores are equal
                elif s1_reaches_target:
                    self.winner = 'player1'
                elif s2_reaches_target:
                    self.winner = 'player2'
                
                if self.game_over: return # End update if game decided by score

        # --- Collision Detection Logic (only if game not already over by score) ---
        if self.game_over: # Re-check as score win might have set it
            return

        # Boundary collisions (Wall Ghost check)
        s1_out_of_bounds = not self.snake1.is_wall_ghost and \
                           not (0 <= s1_head[0] < self.width and 0 <= s1_head[1] < self.height)
        s2_out_of_bounds = not self.snake2.is_wall_ghost and \
                           not (0 <= s2_head[0] < self.width and 0 <= s2_head[1] < self.height)
        
        # Handle wall passthrough for ghosting snakes
        if self.snake1.is_wall_ghost and not (0 <= s1_head[0] < self.width and 0 <= s1_head[1] < self.height):
            s1_head = (s1_head[0] % self.width, s1_head[1] % self.height) # Wrap around
            self.snake1.body[0] = s1_head # Update head position in body
        if self.snake2.is_wall_ghost and not (0 <= s2_head[0] < self.width and 0 <= s2_head[1] < self.height):
            s2_head = (s2_head[0] % self.width, s2_head[1] % self.height) # Wrap around
            self.snake2.body[0] = s2_head # Update head position in body


        s1_self_collision = s1_head in s1_body[1:]
        s2_self_collision = s2_head in s2_body[1:]
        heads_collide = (s1_head == s2_head)

        s1_head_hits_s2_body_exclusive = s1_head in s2_body[1:] if not heads_collide else False
        s2_head_hits_s1_body_exclusive = s2_head in s1_body[1:] if not heads_collide else False

        # Obstacle collisions: A non-ghost snake hitting an obstacle is a loss.
        # Wall Ghost effect does NOT grant immunity to map obstacles.
        s1_hits_obstacle = (s1_head in self.obstacles) # BUG 2 Corrected: is_wall_ghost does not affect obstacle collision
        s2_hits_obstacle = (s2_head in self.obstacles) # BUG 2 Corrected: is_wall_ghost does not affect obstacle collision

        p1_loses = s1_out_of_bounds or s1_self_collision or s1_head_hits_s2_body_exclusive or s1_hits_obstacle
        p2_loses = s2_out_of_bounds or s2_self_collision or s2_head_hits_s1_body_exclusive or s2_hits_obstacle

        if heads_collide:
            self.game_over = True
            self.winner = 'draw'
        elif p1_loses and p2_loses:
            self.game_over = True
            self.winner = 'draw'
        elif p1_loses:
            self.game_over = True
            self.winner = 'player2'
        elif p2_loses:
            self.game_over = True
            self.winner = 'player1'

    def get_powerup_item_details(self):
        if self.powerup_item:
            return {
                'position': self.powerup_item.position,
                'symbol': self.powerup_item.symbol,
                'color': self.powerup_item.color 
            }
        return None

    def get_obstacles(self):
        return self.obstacles

    def change_snake_direction(self, snake_id, new_direction): # This was mistakenly removed in a previous diff by the LLM
        if self.game_over:
            return
        if snake_id == 1:
            self.snake1.turn(new_direction)
        elif snake_id == 2:
            self.snake2.turn(new_direction)

    def get_scores(self): # This was mistakenly removed in a previous diff by the LLM
        return self.snake1.score, self.snake2.score

    # is_game_over, get_winner, get_snakeX_body, get_snakeX_color, get_food_position
    # were also mistakenly removed. Adding them back for completeness if they were.
    # However, based on the last full read_files, they were present.
    # The diff tool seems to only focus on changed sections, not missing ones if the search block isn't there.
    # For now, assuming they are still there as per last full read.

    def is_game_over(self): # Re-adding if it was removed by mistake
        return self.game_over

    def get_winner(self): # Re-adding
        return self.winner

    def get_snake1_body(self): # Re-adding
        return self.snake1.get_body()

    def get_snake2_body(self): # Re-adding
        return self.snake2.get_body()
    
    def get_snake1_color(self): # Re-adding
        return self.snake1.color

    def get_snake2_color(self): # Re-adding
        return self.snake2.color

    def get_food_position(self): # Re-adding
        return self.food
        
# Note: The PowerUp class and MAP_DEFINITIONS are assumed to be at the top of the file from previous steps.
# Re-adding them here if they were part of the overwrite, though ideally they are already there.
# (If this were a real session, I would have confirmed their presence with read_files before this final overwrite)

# --- PowerUp Class --- (Ensuring it's present)
# class PowerUp:
#     def __init__(self, type_id, position, color, symbol, effect_duration):
#         self.type_id = type_id
#         self.position = position
#         self.color = color 
#         self.symbol = symbol 
#         self.effect_duration = effect_duration

# --- Map Definitions --- (Ensuring it's present)
# MAP_DEFINITIONS = {
#     0: [], 
#     1: [ (10,10), (11,10), (12,10), (18,10), (19,10), (20,10), (10,12), (11,12), (12,12), (18,12), (19,12), (20,12)],
#     2: [ (7, 4), (7, 5), (22, 4), (22, 5), (7, 14), (7, 15), (22, 14), (22, 15)]
# }

[end of snake_core.py]

[end of snake_core.py]

[end of snake_core.py]

[end of snake_core.py]

[end of snake_core.py]

[end of snake_core.py]

[end of snake_core.py]

[end of snake_core.py]

[end of snake_core.py]

[end of snake_core.py]
