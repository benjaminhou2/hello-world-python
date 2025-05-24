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

class Snake:
    def __init__(self, snake_id, initial_pos, initial_direction='RIGHT', color='GREEN'):
        self.id = snake_id
        self.body = [initial_pos]
        self.direction = initial_direction
        self.grow_pending = False
        self.color = color 
        self.score = 0 

        self.active_powerup_type = None 
        self.powerup_effect_timer = 0   
        self.is_wall_ghost = False      
        self.steps_per_update = 1       
        self.is_slowed_timer = 0        
        self.slow_effect_counter = 0    
        self.is_started = False # MODIFIED: For static start

    def move(self):
        head_x, head_y = self.body[0]
        if self.direction == 'UP': new_head = (head_x, head_y - 1)
        elif self.direction == 'DOWN': new_head = (head_x, head_y + 1)
        elif self.direction == 'LEFT': new_head = (head_x - 1, head_y)
        elif self.direction == 'RIGHT': new_head = (head_x + 1, head_y)
        else: new_head = (head_x, head_y)
        self.body.insert(0, new_head)
        if self.grow_pending: self.grow_pending = False
        else: self.body.pop()

    def turn(self, new_direction): # MODIFIED: For static start
        valid_directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        if new_direction not in valid_directions: return

        if not self.is_started:
            # Allow any valid direction as the first move, except if it's directly opposite to initial_direction
            # This check is a bit nuanced: if initial_direction is RIGHT, first key press can't be LEFT.
            # However, the problem implies any first key press *sets* the direction and starts.
            # Let's assume any of the 4 arrow keys will start the snake in that direction.
            self.direction = new_direction
            self.is_started = True
        else:
            # Existing anti-reverse logic
            if (new_direction == 'UP' and self.direction != 'DOWN') or \
               (new_direction == 'DOWN' and self.direction != 'UP') or \
               (new_direction == 'LEFT' and self.direction != 'RIGHT') or \
               (new_direction == 'RIGHT' and self.direction != 'LEFT'):
                self.direction = new_direction

    def grow(self):
        self.grow_pending = True; self.score +=1
    def get_head_position(self): return self.body[0]
    def get_body(self): return self.body

class Game: # Single Player Game
    def __init__(self, width, height):
        self.width = width; self.height = height
        self.snake = Snake(1, (width // 2, height // 2)) 
        self.foods = [] 
        self.MAX_FOOD_ITEMS = 5 
        self.game_over = False
        self.powerup_item = None; self.powerup_spawn_chance = 0.15 
        self.POWERUP_MAP_LIFESPAN = 100; self.powerup_on_map_lifespan_timer = 0
        self.POWERUP_DEFINITIONS = {
            'speed_self': {'symbol': 'S', 'color': 'LIGHTBLUE', 'effect_duration': 50, 'applies_to': 'self'},
            'wall_ghost': {'symbol': 'G', 'color': 'PURPLE', 'effect_duration': 70, 'applies_to': 'self'},
        }
        self._generate_food() 
        # self.snake.is_started is False by default

    def _generate_location(self, dynamic_occupied_spaces):
        full_occupied_spaces = set(dynamic_occupied_spaces) 
        if len(full_occupied_spaces) >= self.width * self.height: return None 
        attempts=0; max_attempts = (self.width*self.height)-len(full_occupied_spaces)+10
        if max_attempts <=0 : max_attempts = 1
        while attempts < max_attempts:
            pos = (random.randint(0,self.width-1), random.randint(0,self.height-1))
            if pos not in full_occupied_spaces: return pos
            attempts +=1
        return None 

    def _generate_food(self): 
        while len(self.foods) < self.MAX_FOOD_ITEMS:
            current_occupied = self.snake.get_body() + self.foods
            if self.powerup_item: current_occupied.append(self.powerup_item.position)
            new_food_pos = self._generate_location(current_occupied)
            if new_food_pos: self.foods.append(new_food_pos)
            else: break 

    def _generate_powerup_item(self):
        if self.powerup_item is None and random.random() < self.powerup_spawn_chance:
            current_occupied = self.snake.get_body() + self.foods
            if self.powerup_item: current_occupied.append(self.powerup_item.position)
            pos = self._generate_location(current_occupied) 
            if pos is None: return 
            type_id = random.choice(list(self.POWERUP_DEFINITIONS.keys()))
            definition = self.POWERUP_DEFINITIONS[type_id]
            self.powerup_item = PowerUp(type_id,pos,definition['color'],definition['symbol'],definition['effect_duration'])
            self.powerup_on_map_lifespan_timer = self.POWERUP_MAP_LIFESPAN

    def _clear_powerup_item(self): self.powerup_item=None; self.powerup_on_map_lifespan_timer=0
        
    def _activate_powerup(self, powerup_type): 
        definition = self.POWERUP_DEFINITIONS[powerup_type]
        self._deactivate_powerup_effects() 
        self.snake.active_powerup_type = powerup_type 
        self.snake.powerup_effect_timer = definition['effect_duration'] 
        if powerup_type == 'speed_self': self.snake.steps_per_update = 2
        elif powerup_type == 'wall_ghost': self.snake.is_wall_ghost = True

    def _deactivate_powerup_effects(self): 
        self.snake.steps_per_update = 1; self.snake.is_wall_ghost = False
        if self.snake.active_powerup_type is not None:
             self.snake.active_powerup_type = None; self.snake.powerup_effect_timer = 0
            
    def _update_powerup_timers(self): 
        if self.snake.powerup_effect_timer > 0:
            self.snake.powerup_effect_timer -= 1
            if self.snake.powerup_effect_timer == 0: 
                if self.snake.active_powerup_type=='speed_self': self.snake.steps_per_update=1
                elif self.snake.active_powerup_type=='wall_ghost': self.snake.is_wall_ghost=False
                self.snake.active_powerup_type = None 
        if self.powerup_item:
            self.powerup_on_map_lifespan_timer -=1
            if self.powerup_on_map_lifespan_timer <= 0: self._clear_powerup_item()

    def update(self):
        if self.game_over: return
        self._update_powerup_timers()

        if not self.snake.is_started: # MODIFIED: Gate game logic until snake starts
            return

        head_pos_before_move = self.snake.get_head_position() 

        for _ in range(self.snake.steps_per_update):
            if not self.game_over: 
                 self.snake.move()
                 head_pos = self.snake.get_head_position() 
                 is_out_of_bounds = not (0 <= head_pos[0] < self.width and 0 <= head_pos[1] < self.height)
                 if is_out_of_bounds:
                     if self.snake.is_wall_ghost:
                         new_head_pos = (head_pos[0] % self.width, head_pos[1] % self.height)
                         self.snake.body[0] = new_head_pos; head_pos = new_head_pos 
                     else: self.game_over = True; return
                 if head_pos in self.snake.get_body()[1:]: self.game_over = True; return
        
        head_pos = self.snake.get_head_position() 
        food_eaten_this_tick = False; eaten_food_index = -1
        for i, food_pos in enumerate(list(self.foods)): 
            if head_pos == food_pos:
                self.snake.grow(); eaten_food_index = i
                food_eaten_this_tick = True; break 
        
        if food_eaten_this_tick and eaten_food_index != -1:
            self.foods.pop(eaten_food_index)
            self._generate_food() 
            self._generate_powerup_item()

        current_head_pos_for_pickup = head_pos 
        if self.powerup_item and current_head_pos_for_pickup == self.powerup_item.position:
            self._activate_powerup(self.powerup_item.type_id); self._clear_powerup_item()
        
        if self.game_over: return

    def change_snake_direction(self, new_direction): 
        # is_started logic is now handled in Snake.turn()
        if not self.game_over: self.snake.turn(new_direction)

    def get_score(self): return self.snake.score
    def is_game_over(self): return self.game_over
    def get_snake_body(self): return self.snake.get_body()
    def get_foods(self): return self.foods 
    def get_powerup_item_details(self): 
        if self.powerup_item: return {'position':self.powerup_item.position,'symbol':self.powerup_item.symbol,'color':self.powerup_item.color}
        return None

class TwoPlayerGame:
    def __init__(self, width, height, map_id=0, game_mode='last_snake', target_score=10): 
        self.width=width; self.height=height; self.map_id=map_id; self.obstacles=[] 
        self.game_mode=game_mode; self.target_score=target_score
        self.snake1=Snake(1,(width//4,height//2),'RIGHT','GREEN')
        self.snake2=Snake(2,(width*3//4,height//2),'LEFT','BLUE')
        self.foods=[] ; self.MAX_FOOD_ITEMS=5
        self.game_over=False; self.winner=None
        self.powerup_item=None; self.powerup_spawn_chance=0.20
        self.powerup_on_map_lifespan_timer=0; self.POWERUP_MAP_LIFESPAN=100 
        self.POWERUP_DEFINITIONS={
            'speed_self':{'symbol':'S','color':'LIGHTBLUE','effect_duration':50,'applies_to':'self'},
            'slow_opponent':{'symbol':'O','color':'ORANGE','effect_duration':50,'applies_to':'opponent'},
            'wall_ghost':{'symbol':'G','color':'PURPLE','effect_duration':70,'applies_to':'self'},
        }
        self.set_map(self.map_id) 

    def set_map(self, map_id_to_set):
        self.map_id = map_id_to_set
        self.obstacles = list(MAP_DEFINITIONS.get(self.map_id, [])) 
        s1_initial = (self.width//4,self.height//2); s2_initial = (self.width*3//4,self.height//2)
        
        s2_body_for_s1_spawn = self.snake2.body if hasattr(self, 'snake2') and self.snake2.body else []
        s1_body_for_s2_spawn = self.snake1.body if hasattr(self, 'snake1') and self.snake1.body else []
        
        occupied_for_s1 = s2_body_for_s1_spawn + [s2_initial]
        occupied_for_s2 = s1_body_for_s2_spawn + [s1_initial]

        if s1_initial in self.obstacles: s1_initial = self._generate_location(occupied_for_s1) or (1,1)
        if s2_initial in self.obstacles: s2_initial = self._generate_location(occupied_for_s2) or (self.width-2,self.height-2)
        
        self.snake1.body=[s1_initial]; self.snake1.direction='RIGHT'; self._deactivate_direct_effects(self.snake1); self.snake1.is_started = False
        self.snake2.body=[s2_initial]; self.snake2.direction='LEFT'; self._deactivate_direct_effects(self.snake2); self.snake2.is_started = False
        self.foods=[]; self._generate_food()
        if self.powerup_item: self._clear_powerup_item()
        self.snake1.score=0; self.snake2.score=0
        self.game_over=False; self.winner=None

    def _generate_location(self, dynamic_occupied_spaces):
        full_occupied_spaces = set(dynamic_occupied_spaces + self.obstacles) 
        if len(full_occupied_spaces) >= self.width*self.height: return None 
        attempts=0; max_attempts = (self.width*self.height)-len(full_occupied_spaces)+10
        if max_attempts <=0 : max_attempts = 1
        while attempts < max_attempts:
            pos = (random.randint(0,self.width-1), random.randint(0,self.height-1))
            if pos not in full_occupied_spaces: return pos
            attempts +=1
        return None 

    def _generate_food(self): 
        while len(self.foods) < self.MAX_FOOD_ITEMS:
            occupied = self.snake1.get_body()+self.snake2.get_body()+self.foods
            if self.powerup_item: occupied.append(self.powerup_item.position)
            new_food_pos = self._generate_location(occupied)
            if new_food_pos: self.foods.append(new_food_pos)
            else: break

    def _generate_powerup_item(self):
        if self.powerup_item is None and random.random() < self.powerup_spawn_chance:
            current_occupied = self.snake1.get_body() + self.snake2.get_body() + self.foods
            if self.powerup_item: current_occupied.append(self.powerup_item.position)
            pos = self._generate_location(current_occupied) 
            if pos is None: return 
            type_id = random.choice(list(self.POWERUP_DEFINITIONS.keys()))
            definition = self.POWERUP_DEFINITIONS[type_id]
            self.powerup_item = PowerUp(type_id,pos,definition['color'],definition['symbol'],definition['effect_duration'])
            self.powerup_on_map_lifespan_timer = self.POWERUP_MAP_LIFESPAN

    def _clear_powerup_item(self): self.powerup_item=None; self.powerup_on_map_lifespan_timer=0
        
    def _activate_powerup(self, snake, opponent_snake, powerup_type):
        definition = self.POWERUP_DEFINITIONS[powerup_type]
        target_snake = snake if definition['applies_to']=='self' else opponent_snake
        self._deactivate_direct_effects(target_snake) 
        snake.active_powerup_type = powerup_type 
        snake.powerup_effect_timer = definition['effect_duration'] 
        if powerup_type == 'speed_self': snake.steps_per_update = 2
        elif powerup_type == 'slow_opponent': opponent_snake.is_slowed_timer = definition['effect_duration']; opponent_snake.slow_effect_counter = 0
        elif powerup_type == 'wall_ghost': snake.is_wall_ghost = True 

    def _deactivate_direct_effects(self, snake_to_clear):
        snake_to_clear.steps_per_update = 1; snake_to_clear.is_wall_ghost = False
        snake_to_clear.is_slowed_timer = 0; snake_to_clear.slow_effect_counter = 0
        if snake_to_clear.active_powerup_type is not None:
             snake_to_clear.active_powerup_type = None; snake_to_clear.powerup_effect_timer = 0
            
    def _update_powerup_timers(self): 
        for s in [self.snake1, self.snake2]:
            if s.powerup_effect_timer > 0:
                s.powerup_effect_timer -= 1
                if s.powerup_effect_timer == 0: 
                    if s.active_powerup_type=='speed_self': s.steps_per_update=1
                    elif s.active_powerup_type=='wall_ghost': s.is_wall_ghost=False
                    s.active_powerup_type = None 
            if s.is_slowed_timer > 0:
                s.is_slowed_timer -= 1
                if s.is_slowed_timer == 0: s.slow_effect_counter = 0 
        if self.powerup_item and self.powerup_on_map_lifespan_timer > 0: 
            self.powerup_on_map_lifespan_timer -=1
            if self.powerup_on_map_lifespan_timer <= 0: self._clear_powerup_item()

    def update(self):
        if self.game_over: return
        self._update_powerup_timers()

        # Snake Movement
        if self.snake1.is_started: # MODIFIED: Check if snake has started
            perform_move_s1 = True
            if self.snake1.is_slowed_timer > 0:
                self.snake1.slow_effect_counter=(self.snake1.slow_effect_counter+1)%2
                if self.snake1.slow_effect_counter == 1: perform_move_s1=False
            if perform_move_s1:
                for _ in range(self.snake1.steps_per_update): 
                    if not self.game_over: self.snake1.move()
            if self.game_over: return 
        
        if self.snake2.is_started: # MODIFIED: Check if snake has started
            perform_move_s2 = True
            if self.snake2.is_slowed_timer > 0:
                self.snake2.slow_effect_counter=(self.snake2.slow_effect_counter+1)%2
                if self.snake2.slow_effect_counter == 1: perform_move_s2=False
            if perform_move_s2:
                for _ in range(self.snake2.steps_per_update): 
                    if not self.game_over: self.snake2.move()
            if self.game_over: return 

        if not (self.snake1.is_started or self.snake2.is_started) and not self.game_over : # MODIFIED: Gate main game logic
            return

        s1_h=self.snake1.get_head_position(); s2_h=self.snake2.get_head_position()
        s1_b=self.snake1.get_body(); s2_b=self.snake2.get_body()

        food_eaten_s1=False; food_idx_s1=-1
        if self.snake1.is_started: # MODIFIED
            for i,fp in enumerate(list(self.foods)): 
                if s1_h==fp: self.snake1.grow(); food_idx_s1=i; food_eaten_s1=True; break
            if food_eaten_s1: 
                if food_idx_s1 != -1 : self.foods.pop(food_idx_s1) 
                self._generate_food(); self._generate_powerup_item()
        
        food_eaten_s2=False; food_idx_s2=-1
        if self.snake2.is_started: # MODIFIED
            for i,fp in enumerate(list(self.foods)): 
                if s2_h==fp: self.snake2.grow(); food_idx_s2=i; food_eaten_s2=True; break
            if food_eaten_s2: 
                if food_idx_s2 != -1 : self.foods.pop(food_idx_s2)
                self._generate_food()
                if not food_eaten_s1 : self._generate_powerup_item()


        if self.powerup_item:
            # Check collection only if snake has started and powerup_item exists
            if self.snake1.is_started and s1_h==self.powerup_item.position: # MODIFIED
                self._activate_powerup(self.snake1,self.snake2,self.powerup_item.type_id); self._clear_powerup_item()
            elif self.snake2.is_started and self.powerup_item and s2_h==self.powerup_item.position: # MODIFIED & Check powerup_item again
                 self._activate_powerup(self.snake2,self.snake1,self.powerup_item.type_id); self._clear_powerup_item()

        if self.game_mode=='first_to_x' and not self.game_over:
            s1r=(self.snake1.score>=self.target_score); s2r=(self.snake2.score>=self.target_score)
            if s1r or s2r: self.game_over=True
            if s1r and s2r: self.winner='draw' if self.snake1.score==self.snake2.score else ('player1' if self.snake1.score>self.snake2.score else 'player2')
            elif s1r: self.winner='player1'; elif s2r: self.winner='player2'
            if self.game_over: return

        if self.game_over: return
        s1_ob=not self.snake1.is_wall_ghost and not (0<=s1_h[0]<self.width and 0<=s1_h[1]<self.height)
        s2_ob=not self.snake2.is_wall_ghost and not (0<=s2_h[0]<self.width and 0<=s2_h[1]<self.height)
        if self.snake1.is_wall_ghost and s1_ob: s1_h=(s1_h[0]%self.width,s1_h[1]%self.height); self.snake1.body[0]=s1_h
        if self.snake2.is_wall_ghost and s2_ob: s2_h=(s2_h[0]%self.width,s2_h[1]%self.height); self.snake2.body[0]=s2_h
        s1_sc=s1_h in s1_b[1:]; s2_sc=s2_h in s2_b[1:]
        hc=(s1_h==s2_h)
        s1h2b=s1_h in s2_b[1:] if not hc else False; s2h1b=s2_h in s1_b[1:] if not hc else False
        s1ho=(s1_h in self.obstacles); s2ho=(s2_h in self.obstacles)
        p1l=s1_ob or s1_sc or s1h2b or s1ho; p2l=s2_ob or s2_sc or s2h1b or s2ho
        if hc: self.game_over=True;self.winner='draw'
        elif p1l and p2l: self.game_over=True;self.winner='draw'
        elif p1l: self.game_over=True;self.winner='player2'
        elif p2l: self.game_over=True;self.winner='player1'

    def get_powerup_item_details(self):
        if self.powerup_item: return {'position':self.powerup_item.position,'symbol':self.powerup_item.symbol,'color':self.powerup_item.color}
        return None
    def get_obstacles(self): return self.obstacles
    def change_snake_direction(self, snake_id, new_direction): 
        if self.game_over: return
        if snake_id==1:self.snake1.turn(new_direction)
        elif snake_id==2:self.snake2.turn(new_direction)
    def get_scores(self): return self.snake1.score, self.snake2.score
    def is_game_over(self): return self.game_over
    def get_winner(self): return self.winner
    def get_snake1_body(self): return self.snake1.get_body()
    def get_snake2_body(self): return self.snake2.get_body()
    def get_snake1_color(self): return self.snake1.color
    def get_snake2_color(self): return self.snake2.color
    def get_foods(self): return self.foods
