import pygame
import random
import time
from util.high_score_manager import load_high_scores, update_high_score
from util.pause_screen_manager import show_pause_screen
from util.game_over_screen_manager import show_game_over_screen

class Bomberman:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Calculate responsive tile size
        self.grid_width = 15
        self.grid_height = 13
        tile_width = self.screen_width // self.grid_width
        tile_height = self.screen_height // self.grid_height
        self.tile_size = min(tile_width, tile_height)
        
        # Calculate board position (centered)
        self.board_width = self.grid_width * self.tile_size
        self.board_height = self.grid_height * self.tile_size
        self.board_x = (self.screen_width - self.board_width) // 2
        self.board_y = (self.screen_height - self.board_height) // 2
        
        # Load assets and scale them
        try:
            self.player_image = pygame.transform.scale(
                pygame.image.load('assets/bomberman/player.png'), 
                (self.tile_size, self.tile_size)
            )
        except:
            # Create a default player image if asset is missing
            self.player_image = self.create_colored_tile((0, 0, 255))  # Blue player
            
        try:
            self.wall_image = pygame.transform.scale(
                pygame.image.load('assets/bomberman/wall.png'), 
                (self.tile_size, self.tile_size)
            )
        except:
            # Create a default wall image if asset is missing
            self.wall_image = self.create_colored_tile((100, 100, 100))  # Gray wall
            
        try:
            self.brick_image = pygame.transform.scale(
                pygame.image.load('assets/bomberman/brick.png'), 
                (self.tile_size, self.tile_size)
            )
        except:
            # Create a default brick image if asset is missing
            self.brick_image = self.create_colored_tile((165, 42, 42))  # Brown brick

        try:
            self.bomb_image = pygame.transform.scale(
                pygame.image.load('assets/bomberman/bomb.png'), 
                (self.tile_size, self.tile_size)
            )
        except:
            # Create a default bomb image if asset is missing
            self.bomb_image = self.create_colored_tile((0, 0, 0))  # Black bomb

        try:
            self.explosion_image = pygame.transform.scale(
                pygame.image.load('assets/bomberman/explosion.png'), 
                (self.tile_size, self.tile_size)
            )
        except:
            # Create a default explosion image if asset is missing
            self.explosion_image = self.create_colored_tile((255, 0, 0))  # Red explosion

        try:
            self.enemy_image = pygame.transform.scale(
                pygame.image.load('assets/bomberman/enemy.png'), 
                (self.tile_size, self.tile_size)
            )
        except:
            # Create a default enemy image if asset is missing
            self.enemy_image = self.create_colored_tile((255, 165, 0))  # Orange enemy

        try:
            self.power_up_images = {
                'bomb': pygame.transform.scale(
                    pygame.image.load('assets/bomberman/power_bomb.png'), 
                    (self.tile_size, self.tile_size)
                ),
                'flame': pygame.transform.scale(
                    pygame.image.load('assets/bomberman/power_flame.png'), 
                    (self.tile_size, self.tile_size)
                ),
                'speed': pygame.transform.scale(
                    pygame.image.load('assets/bomberman/power_speed.png'), 
                    (self.tile_size, self.tile_size)
                )
            }
        except:
            # Create default power-up images if assets are missing
            self.power_up_images = {
                'bomb': self.create_colored_tile((0, 255, 0)),    # Green for bomb power-up
                'flame': self.create_colored_tile((255, 0, 0)),   # Red for flame power-up
                'speed': self.create_colored_tile((0, 0, 255))    # Blue for speed power-up
            }
        
        # Load and scale background image
        try:
            self.background_image = pygame.image.load('assets/bomberman/background.png')
            self.background_image = pygame.transform.scale(
                self.background_image, 
                (self.screen_width, self.screen_height)
            )
        except:
            self.background_image = None

        # Load sound effects
        try:
            self.place_bomb_sound = pygame.mixer.Sound('assets/bomberman/place_bomb.wav')
        except:
            self.place_bomb_sound = pygame.mixer.Sound('assets/space_invaders/laser.wav')
            
        try:
            self.explosion_sound = pygame.mixer.Sound('assets/bomberman/explosion.wav')
        except:
            self.explosion_sound = pygame.mixer.Sound('assets/space_invaders/explosion.wav')
            
        try:
            self.power_up_sound = pygame.mixer.Sound('assets/bomberman/power_up.wav')
        except:
            self.power_up_sound = pygame.mixer.Sound('assets/space_invaders/level_up_space.wav')
            
        try:
            self.death_sound = pygame.mixer.Sound('assets/bomberman/death.wav')
        except:
            self.death_sound = pygame.mixer.Sound('assets/space_invaders/game_over_space.wav')
        
        # Game state
        self.level = 1
        self.max_level = 5
        self.score = 0
        self.lives = 3
        
        # Player attributes
        self.player_pos = [1, 1]  # Starting position [x, y] in grid coordinates
        self.player_speed = 5  # Tiles per second
        self.bomb_count = 1  # Initial number of bombs player can place
        self.bomb_range = 2  # Initial explosion range
        
        # Game objects
        self.grid = []  # Will hold tile types
        self.bombs = []  # Will hold bomb positions, planting time, and range
        self.explosions = []  # Will hold explosion positions and time
        self.enemies = []  # Will hold enemy positions and direction
        self.power_ups = []  # Will hold power-up positions and type
        
        # Game timing
        self.start_time = time.time()
        self.elapsed_time = 0
        self.paused = False
        
        # Sound settings
        self.volume = 0.5
        self.music_playing = True
        self.sound_effects_playing = True
        
        # Load and scale icons for sound control
        icon_size = min(50, self.screen_width // 16)
        self.music_icon_on = pygame.transform.scale(
            pygame.image.load('assets/sound_effects/music_on_white.png'), 
            (icon_size, icon_size)
        )
        self.music_icon_off = pygame.transform.scale(
            pygame.image.load('assets/sound_effects/music_off_white.png'), 
            (icon_size, icon_size)
        )
        self.sfx_icon_on = pygame.transform.scale(
            pygame.image.load('assets/sound_effects/sound_on_white.png'), 
            (icon_size, icon_size)
        )
        self.sfx_icon_off = pygame.transform.scale(
            pygame.image.load('assets/sound_effects/sound_off_white.png'), 
            (icon_size, icon_size)
        )
        
        # Calculate icon positions
        self.music_icon_pos = (self.screen_width - icon_size - 10, 10)
        self.sfx_icon_pos = (self.screen_width - icon_size - 10, icon_size + 20)
        
        # Load high scores
        self.high_scores = load_high_scores()
        self.high_score = self.high_scores.get('bomberman', 0)
        
        # Load and play background music
        try:
            pygame.mixer.music.load('assets/bomberman/music.wav')
        except:
            pygame.mixer.music.load('assets/sound_effects/menu/9. Space Debris.wav')
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)  # Loop music
        
        # Initialize the game
        self.init_level(self.level)

    def create_colored_tile(self, color):
        """Create a simple colored square as a placeholder for missing images"""
        tile = pygame.Surface((self.tile_size, self.tile_size))
        tile.fill(color)
        return tile

    def init_level(self, level):
        """Initialize the game grid and entities for the specified level"""
        # Create empty grid
        self.grid = [['empty' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Place fixed walls in alternating pattern
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if x == 0 or x == self.grid_width - 1 or y == 0 or y == self.grid_height - 1:
                    # Border walls
                    self.grid[y][x] = 'wall'
                elif x % 2 == 0 and y % 2 == 0:
                    # Interior walls
                    self.grid[y][x] = 'wall'
        
        # Clear starting area for player (3x3 area)
        self.grid[1][1] = 'empty'
        self.grid[1][2] = 'empty'
        self.grid[2][1] = 'empty'
        
        # Add destructible bricks (more bricks with higher levels)
        brick_count = 10 + level * 5
        for _ in range(brick_count):
            x, y = random.randint(1, self.grid_width - 2), random.randint(1, self.grid_height - 2)
            if self.grid[y][x] == 'empty' and (x > 2 or y > 2):  # Avoid starting area
                self.grid[y][x] = 'brick'
        
        # Reset player
        self.player_pos = [1, 1]
        
        # Clear bombs and explosions
        self.bombs = []
        self.explosions = []
        
        # Add enemies (more enemies with higher levels)
        self.enemies = []
        enemy_count = level + 2
        for _ in range(enemy_count):
            # Find a valid position away from the player
            while True:
                x, y = random.randint(1, self.grid_width - 2), random.randint(1, self.grid_height - 2)
                if self.grid[y][x] == 'empty' and (abs(x - self.player_pos[0]) > 2 or abs(y - self.player_pos[1]) > 2):
                    # Enemy data: [x, y, direction_x, direction_y, speed]
                    speed = 2 + level * 0.5  # Increase speed with level
                    direction = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
                    self.enemies.append([x, y, direction[0], direction[1], speed])
                    break
        
        # Reset power-ups
        self.power_ups = []
        
        # Reset timing
        self.start_time = time.time()
        self.elapsed_time = 0

    def run(self):
        """Main game loop"""
        while self.running:
            delta_time = self.clock.get_time() / 1000  # Convert to seconds
            
            self.handle_events()
            
            if not self.paused:
                self.update(delta_time)
                self.elapsed_time = time.time() - self.start_time
                self.draw()
            else:
                show_pause_screen(self.screen)
                
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS

    def handle_events(self):
        """Process user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Update screen dimensions
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.screen_width = self.screen.get_width()
                self.screen_height = self.screen.get_height()
                
                # Recalculate tile size and board position
                tile_width = self.screen_width // self.grid_width
                tile_height = self.screen_height // self.grid_height
                self.tile_size = min(tile_width, tile_height)
                self.board_width = self.grid_width * self.tile_size
                self.board_height = self.grid_height * self.tile_size
                self.board_x = (self.screen_width - self.board_width) // 2
                self.board_y = (self.screen_height - self.board_height) // 2
                
                # Rescale all images
                # (Assuming assets are available, if not would need to recreate colored tiles)
                self.player_image = pygame.transform.scale(self.player_image, (self.tile_size, self.tile_size))
                self.wall_image = pygame.transform.scale(self.wall_image, (self.tile_size, self.tile_size))
                self.brick_image = pygame.transform.scale(self.brick_image, (self.tile_size, self.tile_size))
                self.bomb_image = pygame.transform.scale(self.bomb_image, (self.tile_size, self.tile_size))
                self.explosion_image = pygame.transform.scale(self.explosion_image, (self.tile_size, self.tile_size))
                self.enemy_image = pygame.transform.scale(self.enemy_image, (self.tile_size, self.tile_size))
                
                for key in self.power_up_images:
                    self.power_up_images[key] = pygame.transform.scale(
                        self.power_up_images[key], 
                        (self.tile_size, self.tile_size)
                    )
                
                if self.background_image:
                    self.background_image = pygame.transform.scale(
                        self.background_image, 
                        (self.screen_width, self.screen_height)
                    )
                
                # Update icon positions
                icon_size = min(50, self.screen_width // 16)
                self.music_icon_on = pygame.transform.scale(
                    pygame.image.load('assets/sound_effects/music_on_white.png'), 
                    (icon_size, icon_size)
                )
                self.music_icon_off = pygame.transform.scale(
                    pygame.image.load('assets/sound_effects/music_off_white.png'), 
                    (icon_size, icon_size)
                )
                self.sfx_icon_on = pygame.transform.scale(
                    pygame.image.load('assets/sound_effects/sound_on_white.png'), 
                    (icon_size, icon_size)
                )
                self.sfx_icon_off = pygame.transform.scale(
                    pygame.image.load('assets/sound_effects/sound_off_white.png'), 
                    (icon_size, icon_size)
                )
                self.music_icon_pos = (self.screen_width - icon_size - 10, 10)
                self.sfx_icon_pos = (self.screen_width - icon_size - 10, icon_size + 20)
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                    if not self.paused:
                        self.start_time = time.time() - self.elapsed_time
                elif event.key == pygame.K_SPACE:
                    self.place_bomb()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if music icon is clicked
                    if (self.music_icon_pos[0] <= mouse_pos[0] <= self.music_icon_pos[0] + self.music_icon_on.get_width() and
                        self.music_icon_pos[1] <= mouse_pos[1] <= self.music_icon_pos[1] + self.music_icon_on.get_height()):
                        self.toggle_music()
                    # Check if sound effects icon is clicked
                    elif (self.sfx_icon_pos[0] <= mouse_pos[0] <= self.sfx_icon_pos[0] + self.sfx_icon_on.get_width() and
                          self.sfx_icon_pos[1] <= mouse_pos[1] <= self.sfx_icon_pos[1] + self.sfx_icon_on.get_height()):
                        self.toggle_sound_effects()

    def toggle_music(self):
        """Toggle background music on/off"""
        if self.music_playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.music_playing = not self.music_playing

    def toggle_sound_effects(self):
        """Toggle sound effects on/off"""
        self.sound_effects_playing = not self.sound_effects_playing

    def update(self, delta_time):
        """Update game state"""
        # Process player movement
        keys = pygame.key.get_pressed()
        new_pos = list(self.player_pos)
        move_distance = self.player_speed * delta_time
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_pos[0] -= move_distance
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_pos[0] += move_distance
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_pos[1] -= move_distance
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_pos[1] += move_distance
            
        # Check for valid movement (no collisions)
        if self.is_valid_position(new_pos):
            self.player_pos = new_pos
            
        # Check for power-up collection
        self.check_power_up_collection()
            
        # Update bombs
        self.update_bombs()
        
        # Update explosions
        self.update_explosions()
        
        # Update enemies
        self.update_enemies(delta_time)
        
        # Check for player death
        if self.check_player_death():
            self.lives -= 1
            if self.lives <= 0:
                self.game_over()
            else:
                self.reset_player()
                
        # Check if level is completed (all enemies killed)
        if not self.enemies:
            self.complete_level()

    def is_valid_position(self, pos):
        """Check if a position is valid for movement (no walls, bombs, etc.)"""
        # Convert to integer grid coordinates for checking
        grid_x = int(pos[0] + 0.5)
        grid_y = int(pos[1] + 0.5)
        
        # Check grid bounds
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return False
            
        # Check for walls and bricks
        if self.grid[grid_y][grid_x] in ['wall', 'brick']:
            return False
            
        # Check for bombs (can't walk through bombs)
        for bomb in self.bombs:
            bomb_x, bomb_y = int(bomb[0]), int(bomb[1])
            if grid_x == bomb_x and grid_y == bomb_y:
                return False
                
        return True

    def place_bomb(self):
        """Place a bomb at the player's position if bomb count allows"""
        if len([b for b in self.bombs if b[3] == False]) < self.bomb_count:  # Check available bombs
            grid_x, grid_y = int(self.player_pos[0]), int(self.player_pos[1])
            
            # Check if there's already a bomb at this position
            for bomb in self.bombs:
                if int(bomb[0]) == grid_x and int(bomb[1]) == grid_y:
                    return
                    
            # Add new bomb: [x, y, timer, exploded, range]
            self.bombs.append([grid_x, grid_y, time.time(), False, self.bomb_range])
            
            if self.sound_effects_playing:
                self.place_bomb_sound.play()

    def update_bombs(self):
        """Update bomb timers and handle explosions"""
        current_time = time.time()
        
        for bomb in self.bombs[:]:  # Use a copy for safe modification
            if not bomb[3] and current_time - bomb[2] >= 3:  # Bomb timer (3 seconds)
                bomb[3] = True  # Mark as exploded
                self.create_explosion(bomb[0], bomb[1], bomb[4])  # Create explosion with bomb's range
                
                if self.sound_effects_playing:
                    self.explosion_sound.play()

    def create_explosion(self, x, y, explosion_range):
        """Create explosion at position with specified range"""
        # Add center of explosion
        self.explosions.append([x, y, time.time()])
        
        # Create explosion in four directions
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, explosion_range):
                nx, ny = x + dx * i, y + dy * i
                
                # Stop if out of bounds
                if nx < 0 or nx >= self.grid_width or ny < 0 or ny >= self.grid_height:
                    break
                    
                # Stop at walls
                if self.grid[int(ny)][int(nx)] == 'wall':
                    break
                    
                # Handle bricks (destroy and stop explosion in this direction)
                if self.grid[int(ny)][int(nx)] == 'brick':
                    self.grid[int(ny)][int(nx)] = 'empty'
                    self.score += 10
                    
                    # Chance to spawn power-up
                    if random.random() < 0.3:  # 30% chance
                        power_type = random.choice(['bomb', 'flame', 'speed'])
                        self.power_ups.append([nx, ny, power_type])
                        
                    self.explosions.append([nx, ny, time.time()])
                    break
                    
                # Add explosion segment
                self.explosions.append([nx, ny, time.time()])

    def update_explosions(self):
        """Update explosion timers and remove expired explosions"""
        current_time = time.time()
        self.explosions = [exp for exp in self.explosions if current_time - exp[2] < 1]  # Explosions last 1 second

    def update_enemies(self, delta_time):
        """Update enemy positions and check for direction changes"""
        for enemy in self.enemies[:]:  # Use a copy for safe removal
            # Calculate new position
            new_x = enemy[0] + enemy[2] * enemy[4] * delta_time
            new_y = enemy[1] + enemy[3] * enemy[4] * delta_time
            
            # Check if new position is valid
            if self.is_valid_position([new_x, new_y]):
                enemy[0], enemy[1] = new_x, new_y
            else:
                # Choose a new random direction
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                directions.remove((enemy[2], enemy[3]))  # Remove current direction
                new_dir = random.choice(directions)
                enemy[2], enemy[3] = new_dir
            
            # Check if enemy is in explosion
            if self.is_in_explosion(enemy[0], enemy[1]):
                self.enemies.remove(enemy)
                self.score += 100

    def is_in_explosion(self, x, y):
        """Check if a position is inside an explosion"""
        grid_x, grid_y = int(x), int(y)
        
        for exp_x, exp_y, _ in self.explosions:
            if grid_x == int(exp_x) and grid_y == int(exp_y):
                return True
                
        return False

    def check_player_death(self):
        """Check if player is hit by explosion or enemy"""
        grid_x, grid_y = int(self.player_pos[0]), int(self.player_pos[1])
        
        # Check if player is in explosion
        if self.is_in_explosion(self.player_pos[0], self.player_pos[1]):
            if self.sound_effects_playing:
                self.death_sound.play()
            return True
            
        # Check if player collides with enemy
        for enemy in self.enemies:
            enemy_grid_x, enemy_grid_y = int(enemy[0]), int(enemy[1])
            if grid_x == enemy_grid_x and grid_y == enemy_grid_y:
                if self.sound_effects_playing:
                    self.death_sound.play()
                return True
                
        return False

    def check_power_up_collection(self):
        """Check if player collects power-ups"""
        grid_x, grid_y = int(self.player_pos[0]), int(self.player_pos[1])
        
        for power_up in self.power_ups[:]:  # Use a copy for safe removal
            if grid_x == int(power_up[0]) and grid_y == int(power_up[1]):
                power_type = power_up[2]
                self.power_ups.remove(power_up)
                
                # Apply power-up effect
                if power_type == 'bomb':
                    self.bomb_count += 1
                elif power_type == 'flame':
                    self.bomb_range += 1
                elif power_type == 'speed':
                    self.player_speed += 1
                    
                self.score += 50
                
                if self.sound_effects_playing:
                    self.power_up_sound.play()
                    
                break

    def reset_player(self):
        """Reset player after death"""
        self.player_pos = [1, 1]  # Starting position
        
        # Ensure there are no enemies nearby
        for enemy in self.enemies[:]:
            if abs(enemy[0] - self.player_pos[0]) < 3 and abs(enemy[1] - self.player_pos[1]) < 3:
                # Move enemy to a random position away from player
                while True:
                    x = random.randint(1, self.grid_width - 2)
                    y = random.randint(1, self.grid_height - 2)
                    if self.grid[y][x] == 'empty' and (abs(x - self.player_pos[0]) > 3 or abs(y - self.player_pos[1]) > 3):
                        enemy[0], enemy[1] = x, y
                        break

    def complete_level(self):
        """Handle level completion"""
        if self.level < self.max_level:
            self.level += 1
            self.score += 500  # Level completion bonus
            self.show_level_up_message()
            self.init_level(self.level)
        else:
            # Game completed
            self.score += 1000  # Game completion bonus
            self.game_over(completed=True)

    def show_game_completed_message(self):
        """Show game completed message"""
        font_size = max(36, min(self.screen_width, self.screen_height) // 15)
        font = pygame.font.Font(None, font_size)
        
        text_surface = font.render("GAME COMPLETED!", True, (255, 215, 0))  # Gold color
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - font_size))
        
        bonus_text = font.render(f"Bonus: 1000 Points!", True, (255, 215, 0))
        bonus_rect = bonus_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + font_size))
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text_surface, text_rect)
        self.screen.blit(bonus_text, bonus_rect)
        
        pygame.display.flip()
        pygame.time.delay(3000)  # Show for 3 seconds

    def game_over(self, completed=False):
        """Handle game over"""
        self.high_score = update_high_score('bomberman', self.score)
        
        # Show different message if game was completed
        if completed:
            self.show_game_completed_message()
            
        action = show_game_over_screen(self.screen, self.score, self.high_score, self.lives)
        
        if action == "retry":
            # Reset game state
            self.score = 0
            self.lives = 3
            self.level = 1
            self.bomb_count = 1
            self.bomb_range = 2
            self.player_speed = 5
            self.init_level(self.level)
        else:
            self.running = False  # Exit to menu

    def draw(self):
        """Draw the game state to the screen"""
        # Clear screen or draw background
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((0, 0, 0))  # Black background
        
        # Draw the board background
        board_background = pygame.Rect(self.board_x, self.board_y, self.board_width, self.board_height)
        pygame.draw.rect(self.screen, (50, 50, 50), board_background)
        
        # Draw grid tiles
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                screen_x = self.board_x + x * self.tile_size
                screen_y = self.board_y + y * self.tile_size
                
                if self.grid[y][x] == 'wall':
                    self.screen.blit(self.wall_image, (screen_x, screen_y))
                elif self.grid[y][x] == 'brick':
                    self.screen.blit(self.brick_image, (screen_x, screen_y))
        
        # Draw power-ups
        for power_up in self.power_ups:
            power_x, power_y, power_type = power_up
            screen_x = self.board_x + int(power_x) * self.tile_size
            screen_y = self.board_y + int(power_y) * self.tile_size
            self.screen.blit(self.power_up_images[power_type], (screen_x, screen_y))
        
        # Draw bombs
        for bomb in self.bombs:
            if not bomb[3]:  # If not exploded
                screen_x = self.board_x + int(bomb[0]) * self.tile_size
                screen_y = self.board_y + int(bomb[1]) * self.tile_size
                self.screen.blit(self.bomb_image, (screen_x, screen_y))
        
        # Draw explosions
        for exp in self.explosions:
            screen_x = self.board_x + int(exp[0]) * self.tile_size
            screen_y = self.board_y + int(exp[1]) * self.tile_size
            self.screen.blit(self.explosion_image, (screen_x, screen_y))
        
        # Draw enemies
        for enemy in self.enemies:
            enemy_x, enemy_y = enemy[0], enemy[1]
            screen_x = self.board_x + int(enemy_x) * self.tile_size
            screen_y = self.board_y + int(enemy_y) * self.tile_size
            self.screen.blit(self.enemy_image, (screen_x, screen_y))
        
        # Draw player
        player_screen_x = self.board_x + int(self.player_pos[0]) * self.tile_size
        player_screen_y = self.board_y + int(self.player_pos[1]) * self.tile_size
        self.screen.blit(self.player_image, (player_screen_x, player_screen_y))
        
        # Draw HUD (score, lives, level)
        self.draw_hud()
        
        # Draw sound control icons
        if self.music_playing:
            self.screen.blit(self.music_icon_on, self.music_icon_pos)
        else:
            self.screen.blit(self.music_icon_off, self.music_icon_pos)
            
        if self.sound_effects_playing:
            self.screen.blit(self.sfx_icon_on, self.sfx_icon_pos)
        else:
            self.screen.blit(self.sfx_icon_off, self.sfx_icon_pos)

    def draw_hud(self):
        """Draw the Heads-Up Display (score, lives, level, etc.)"""
        font_size = max(20, min(self.screen_width, self.screen_height) // 30)
        font = pygame.font.Font(None, font_size)
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # High score
        high_score_text = font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
        high_score_rect = high_score_text.get_rect()
        self.screen.blit(high_score_text, (10, 10 + high_score_rect.height + 5))
        
        # Level
        level_text = font.render(f"Level: {self.level}", True, (255, 255, 255))
        level_rect = level_text.get_rect()
        self.screen.blit(level_text, (10, 10 + 2 * (high_score_rect.height + 5)))
        
        # Lives
        lives_text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        lives_rect = lives_text.get_rect()
        self.screen.blit(lives_text, (10, 10 + 3 * (high_score_rect.height + 5)))
        
        # Bomb count
        bomb_text = font.render(f"Bombs: {self.bomb_count}", True, (255, 255, 255))
        bomb_rect = bomb_text.get_rect()
        self.screen.blit(bomb_text, (10, 10 + 4 * (high_score_rect.height + 5)))
        
        # Bomb range
        range_text = font.render(f"Range: {self.bomb_range}", True, (255, 255, 255))
        self.screen.blit(range_text, (10, 10 + 5 * (high_score_rect.height + 5)))