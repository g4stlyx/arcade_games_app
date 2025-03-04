import pygame
import random
import time
from util.high_score_manager import load_high_scores, update_high_score
from util.pause_screen_manager import show_pause_screen
from util.game_over_screen_manager import show_game_over_screen

class PacmanGame:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Calculate adaptive element sizes
        self.element_size = min(16, max(int(min(self.screen_width, self.screen_height) / 40), 8))
        
        # Scale images based on screen size
        self.pacman_image = pygame.transform.scale(pygame.image.load('assets/pacman/pacman.png'), 
                                                  (self.element_size, self.element_size))
        self.ghost_image = pygame.transform.scale(pygame.image.load('assets/snake/mouse.png'),
                                                 (self.element_size, self.element_size))
        self.dot_image = pygame.transform.scale(pygame.image.load('assets/snake/apple.png'),
                                               (self.element_size, self.element_size))
        self.powerup_image = pygame.transform.scale(pygame.image.load('assets/space_invaders/ufo.png'),
                                                  (self.element_size, self.element_size))
        self.wall_image = pygame.transform.scale(pygame.image.load('assets/pacman/grass16.png'),
                                               (self.element_size, self.element_size))
        
        # Load and scale background image
        self.background_image = pygame.image.load('assets/space_invaders/space2.jpg')
        self.background_image = pygame.transform.scale(self.background_image, 
                                                     (self.screen_width, self.screen_height))
        
        self.eat_sound = pygame.mixer.Sound('assets/space_invaders/level_up_space.wav')
        self.game_over_sound = pygame.mixer.Sound('assets/space_invaders/game_over_space.wav')

        # Responsive positioning
        self.pacman_pos = [self.screen_width // 2, self.screen_height - self.element_size * 3]
        self.pacman_speed = self.screen_width // 6  # Adaptive speed
        self.ghost_speed = self.screen_width // 8  # Adaptive speed
        self.levels = self.define_levels()
        self.level = 1
        self.walls = self.create_walls()
        self.dots = self.create_dots()
        self.ghosts = self.create_ghosts()
        self.powerups = self.create_powerups()
        self.max_level = 5
        self.super_mode = False
        self.super_mode_timer = 0
        self.score = 0
        self.high_scores = load_high_scores()  # Load all high scores
        self.high_score = self.high_scores.get('pacman', 0)  # Get high score for this game
        self.paused = False  # Track if the game is paused
        self.elapsed_time = 0 
        self.start_time = time.time()
        self.volume = 0.5  # Default volume level
        self.music_playing = True  # Track if music is playing
        self.sound_effects_playing = True  # Track if sound effects are playing
        
        # Load and scale icons based on screen size
        icon_size = min(50, self.screen_width // 16)
        self.music_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_on_white.png'), 
                                                  (icon_size, icon_size))
        self.music_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_off_white.png'), 
                                                   (icon_size, icon_size))
        self.sfx_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_on_white.png'), 
                                                 (icon_size, icon_size))
        self.sfx_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_off_white.png'), 
                                                  (icon_size, icon_size))
        
        # Calculate icon positions based on screen size
        self.music_icon_pos = (self.screen_width - icon_size - 10, 10)
        self.sfx_icon_pos = (self.screen_width - icon_size - 10, icon_size + 20)
        
        self.max_powerups = 2  # Maximum number of power-ups on screen
        
        # Load and play background music
        pygame.mixer.music.load('assets/sound_effects/menu/9. Space Debris.wav')
        pygame.mixer.music.set_volume(self.volume)  # Set initial volume
        pygame.mixer.music.play(-1)  # Play music in a loop

        self.clock.tick(60)  # Keep the game running at 60 FPS

    def define_levels(self):
        """Define the wall layouts for each level with denser clusters."""
        # Scale factor to adjust overall cluster density
        density_scale = 1.2
        margin = self.element_size * 3  # Margin from edges
        
        # Calculate playable area
        max_x = self.screen_width - margin
        max_y = self.screen_height - margin
        
        level1 = []
        for i in range(int(5 * density_scale)):
            level1.append((random.randint(margin, max_x), random.randint(margin, max_y)))

        level2 = []
        for i in range(int(10 * density_scale)):
            x = random.randint(margin, max_x)
            y = random.randint(margin, max_y)
            level2.append((x, y))
            level2.append((x + self.element_size, y))
            level2.append((x, y + self.element_size))

        level3 = []
        for i in range(int(15 * density_scale)):
            x = random.randint(margin, max_x)
            y = random.randint(margin, max_y)
            level3.append((x, y))
            level3.append((x + self.element_size, y))
            level3.append((x, y + self.element_size))
            level3.append((x + self.element_size, y + self.element_size))

        level4 = []
        for i in range(int(20 * density_scale)):
            x = random.randint(margin, max_x)
            y = random.randint(margin, max_y)
            level4.append((x, y))
            level4.append((x + self.element_size, y))
            level4.append((x, y + self.element_size))
            level4.append((x - self.element_size, y))
            level4.append((x, y - self.element_size))

        level5 = []
        for i in range(int(25 * density_scale)):
            x = random.randint(margin, max_x)
            y = random.randint(margin, max_y)
            level5.append((x, y))
            level5.append((x + self.element_size, y))
            level5.append((x, y + self.element_size))
            level5.append((x - self.element_size, y))
            level5.append((x, y - self.element_size))
            level5.append((x + self.element_size * 2, y))
            level5.append((x, y + self.element_size * 2))

        return [level1, level2, level3, level4, level5]
    
    def handle_window_resize(self):
        """Update all size-dependent variables when window is resized"""
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        # Recalculate sizes
        self.element_size = min(16, max(int(min(self.screen_width, self.screen_height) / 40), 8))
        
        # Rescale all images
        self.pacman_image = pygame.transform.scale(pygame.image.load('assets/pacman/pacman.png'), 
                                                  (self.element_size, self.element_size))
        self.ghost_image = pygame.transform.scale(pygame.image.load('assets/snake/mouse.png'),
                                                 (self.element_size, self.element_size))
        self.dot_image = pygame.transform.scale(pygame.image.load('assets/snake/apple.png'),
                                               (self.element_size, self.element_size))
        self.powerup_image = pygame.transform.scale(pygame.image.load('assets/space_invaders/ufo.png'),
                                                  (self.element_size, self.element_size))
        self.wall_image = pygame.transform.scale(pygame.image.load('assets/pacman/grass16.png'),
                                               (self.element_size, self.element_size))
        
        # Rescale background
        self.background_image = pygame.transform.scale(
            pygame.image.load('assets/space_invaders/space2.jpg'),
            (self.screen_width, self.screen_height)
        )
        
        # Recalculate speeds
        self.pacman_speed = self.screen_width // 6
        self.ghost_speed = self.screen_width // 8
        
        # Recalculate icon sizes and positions
        icon_size = min(50, self.screen_width // 16)
        self.music_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_on_white.png'), 
                                                  (icon_size, icon_size))
        self.music_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_off_white.png'), 
                                                   (icon_size, icon_size))
        self.sfx_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_on_white.png'), 
                                                 (icon_size, icon_size))
        self.sfx_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_off_white.png'), 
                                                  (icon_size, icon_size))
        
        # Recalculate icon positions
        self.music_icon_pos = (self.screen_width - icon_size - 10, 10)
        self.sfx_icon_pos = (self.screen_width - icon_size - 10, icon_size + 20)
        
        # Update game elements
        self.levels = self.define_levels()
        self.walls = self.create_walls()
    
    def run(self):
        while self.running:
            delta_time = self.clock.get_time() / 1000  # Get delta time in seconds
            self.handle_events(delta_time)
            if not self.paused:  # Only update if not paused
                self.update(delta_time)  # Update game state, passing delta_time
                self.elapsed_time = time.time() - self.start_time  # Update elapsed time only when not paused
                self.draw()  # Draw the game only if not paused
            else:
                show_pause_screen(self.screen)  # Show pause screen
            pygame.display.flip() 
            self.clock.tick(60)  # Limit to 60 frames per second

    def create_dots(self):
        """Create a list of dots at random positions."""
        margin = self.element_size  # Safety margin from edge
        num_dots = int((self.screen_width * self.screen_height) / 6400)  # Scale dots with screen size
        return [[random.randint(margin, self.screen_width - margin), 
                 random.randint(margin, self.screen_height - margin)] 
                for _ in range(num_dots)]

    def create_ghosts(self):
        """Create a list of ghosts at random positions, away from Pac-Man."""
        ghosts = []
        num_ghosts = min(4 + self.level, 8)  # Scale number of ghosts with level, max 8
        min_distance = min(self.screen_width, self.screen_height) / 4  # Minimum distance from Pacman
        
        while len(ghosts) < num_ghosts:
            x = random.randint(self.element_size, self.screen_width - self.element_size * 2)
            y = random.randint(self.element_size, self.screen_height - self.element_size * 2)
            
            # Ensure ghosts are reasonably far from Pac-Man on creation
            if ((x - self.pacman_pos[0])**2 + (y - self.pacman_pos[1])**2) > min_distance**2:
                valid_position = True
                for wall in self.walls:
                    if (x < wall[0] + self.element_size and 
                        x + self.element_size > wall[0] and 
                        y < wall[1] + self.element_size and 
                        y + self.element_size > wall[1]):
                        valid_position = False
                        break  # Skip this position if it's inside a wall

                if valid_position:
                    ghosts.append([x, y])
        return ghosts

    def create_powerups(self):
        """Create a list of power-ups at random positions, ensuring they don't overlap with walls."""
        powerups = []
        max_powerups = min(2, self.level)  # Scale with level, max 2
        attempts = 0
        
        while len(powerups) < max_powerups and attempts < 20:
            attempts += 1
            x = random.randint(self.element_size, self.screen_width - self.element_size * 2)
            y = random.randint(self.element_size, self.screen_height - self.element_size * 2)
            new_powerup = [x, y]

            # Check if the power-up overlaps with a wall
            valid_position = True
            for wall in self.walls:
                if (x < wall[0] + self.element_size and 
                    x + self.element_size > wall[0] and 
                    y < wall[1] + self.element_size and 
                    y + self.element_size > wall[1]):
                    valid_position = False
                    break

            if valid_position and new_powerup not in powerups:
                powerups.append(new_powerup)
                
        return powerups

    def create_walls(self):
        """Create walls based on the current level."""
        if 1 <= self.level <= len(self.levels):
            return self.levels[self.level - 1]  # Get walls for the current level
        else:
            return []  # No walls if level is out of range

    def handle_events(self, delta_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.handle_window_resize()  # Update all size-dependent variables
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Toggle pause with 'P' key
                    self.paused = not self.paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if music icon is clicked
                    if (self.music_icon_pos[0] <= mouse_pos[0] <= self.music_icon_pos[0] + self.music_icon_on.get_width() and 
                        self.music_icon_pos[1] <= mouse_pos[1] <= self.music_icon_pos[1] + self.music_icon_on.get_height()):
                        self.toggle_music()
                    # Check if sound effects icon is clicked
                    elif (self.sfx_icon_pos[0] <= mouse_pos[0] <= self.sfx_icon_pos[0] + self.sfx_icon_on.get_width() and 
                          self.sfx_icon_pos[1] <= mouse_pos[1] <= self.sfx_icon_pos[1] + self.sfx_icon_on.get_height()):
                        self.toggle_sound_effects()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            new_x = self.pacman_pos[0] - self.pacman_speed * delta_time
            if new_x >= 0 and not self.is_blocked(self.pacman_pos, [new_x, self.pacman_pos[1]]):
                self.pacman_pos[0] = new_x
        if keys[pygame.K_RIGHT]:
            new_x = self.pacman_pos[0] + self.pacman_speed * delta_time
            if new_x <= self.screen_width - self.element_size and not self.is_blocked(self.pacman_pos, [new_x, self.pacman_pos[1]]):
                self.pacman_pos[0] = new_x
        if keys[pygame.K_UP]:
            new_y = self.pacman_pos[1] - self.pacman_speed * delta_time
            if new_y >= 0 and not self.is_blocked(self.pacman_pos, [self.pacman_pos[0], new_y]):
                self.pacman_pos[1] = new_y
        if keys[pygame.K_DOWN]:
            new_y = self.pacman_pos[1] + self.pacman_speed * delta_time
            if new_y <= self.screen_height - self.element_size and not self.is_blocked(self.pacman_pos, [self.pacman_pos[0], new_y]):
                self.pacman_pos[1] = new_y

    def update(self, delta_time):
        # Dots fetching
        for dot in list(self.dots):
            if (dot[0] < self.pacman_pos[0] + 16 < dot[0] + 20) and \
               (dot[1] < self.pacman_pos[1] + 16 < dot[1] + 20):
                self.dots.remove(dot)
                self.score += 1
                if self.sound_effects_playing:
                    self.eat_sound.play()

        for ghost in self.ghosts:
            # Super Mode: Ghosts Run Away
            if self.super_mode:
                dx = ghost[0] - self.pacman_pos[0]  # Flee direction
                dy = ghost[1] - self.pacman_pos[1]

                if abs(dx) > abs(dy):
                    if dx > 0:  # Move away (left)
                        new_x = ghost[0] + self.ghost_speed * delta_time
                        if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                            ghost[0] = new_x
                        else: # If blocked, try moving perpendicularly
                            if dy > 0:
                                new_y = ghost[1] + self.ghost_speed * delta_time
                                if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                                    ghost[1] = new_y
                            else:
                                new_y = ghost[1] - self.ghost_speed * delta_time
                                if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                                    ghost[1] = new_y
                    else:  # Move away (right)
                        new_x = ghost[0] - self.ghost_speed * delta_time
                        if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                            ghost[0] = new_x
                        else: # If blocked, try moving perpendicularly
                            if dy > 0:
                                new_y = ghost[1] + self.ghost_speed * delta_time
                                if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                                    ghost[1] = new_y
                            else:
                                new_y = ghost[1] - self.ghost_speed * delta_time
                                if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                                    ghost[1] = new_y
                else:
                    if dy > 0:  # Move away (up)
                        new_y = ghost[1] + self.ghost_speed * delta_time
                        if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                            ghost[1] = new_y
                        else: # If blocked, try moving perpendicularly
                            if dx > 0:
                                new_x = ghost[0] + self.ghost_speed * delta_time
                                if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                                    ghost[0] = new_x
                            else:
                                new_x = ghost[0] - self.ghost_speed * delta_time
                                if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                                    ghost[0] = new_x
                    else:  # Move away (down)
                        new_y = ghost[1] - self.ghost_speed * delta_time
                        if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                            ghost[1] = new_y
                        else: # If blocked, try moving perpendicularly
                            if dx > 0:
                                new_x = ghost[0] + self.ghost_speed * delta_time
                                if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                                    ghost[0] = new_x
                            else:
                                new_x = ghost[0] - self.ghost_speed * delta_time
                                if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                                    ghost[0] = new_x
            # Normal Mode: Ghosts Chase
            else:
                dx = self.pacman_pos[0] - ghost[0]
                dy = self.pacman_pos[1] - ghost[1]

                if abs(dx) > abs(dy):
                    if dx > 0:  # Move right
                        new_x = ghost[0] + self.ghost_speed * delta_time
                        if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                            ghost[0] = new_x
                        else:
                            if dy > 0:
                                new_y = ghost[1] + self.ghost_speed * delta_time
                                if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                                    ghost[1] = new_y
                            else:
                                new_y = ghost[1] - self.ghost_speed * delta_time
                                if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                                    ghost[1] = new_y
                    else:  # Move left
                        new_x = ghost[0] - self.ghost_speed * delta_time
                        if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                            ghost[0] = new_x
                        else:
                            if dy > 0:
                                new_y = ghost[1] + self.ghost_speed * delta_time
                                if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                                    ghost[1] = new_y
                            else:
                                new_y = ghost[1] - self.ghost_speed * delta_time
                                if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                                    ghost[1] = new_y
                else:
                    if dy > 0:  # Move down
                        new_y = ghost[1] + self.ghost_speed * delta_time
                        if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                            ghost[1] = new_y
                        else:
                            if dx > 0:
                                new_x = ghost[0] + self.ghost_speed * delta_time
                                if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                                    ghost[0] = new_x
                            else:
                                new_x = ghost[0] - self.ghost_speed * delta_time
                                if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                                    ghost[0] = new_x
                    else:  # Move up
                        new_y = ghost[1] - self.ghost_speed * delta_time
                        if new_y <= self.screen.get_height() - 16 and new_y >= 0 and not self.is_blocked(ghost, [ghost[0], new_y]):
                            ghost[1] = new_y
                        else:
                            if dx > 0:
                                new_x = ghost[0] + self.ghost_speed * delta_time
                                if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                                    ghost[0] = new_x
                            else:
                                new_x = ghost[0] - self.ghost_speed * delta_time
                                if new_x <= self.screen.get_width() - 16 and new_x >= 0 and not self.is_blocked(ghost, [new_x, ghost[1]]):
                                    ghost[0] = new_x


        for ghost in list(self.ghosts):
            if (ghost[0] < self.pacman_pos[0] + 16 < ghost[0] + 20) and \
               (ghost[1] < self.pacman_pos[1] + 16 < ghost[1] + 20):
                if self.super_mode:
                    self.ghosts.remove(ghost)
                    self.score += 10
                else:
                    self.game_over()

        # Check for collisions with power-ups
        for powerup in list(self.powerups):  # Iterate over a copy to allow removal
            if (powerup[0] < self.pacman_pos[0] < powerup[0] + 20) and (powerup[1] < self.pacman_pos[1] < powerup[1] + 20):
                self.powerups.remove(powerup)
                self.super_mode = True
                self.super_mode_timer = time.time()

        # After power-up is eaten, disable super mode after its time is up.
        if self.super_mode:
            if time.time() - self.super_mode_timer >= 10:  # 10 seconds of super mode
                self.super_mode = False

        # Check for level up condition (if no ghosts left)
        if not self.ghosts:
            self.level_up()

        if not self.dots:
            self.level_up()

        if not self.dots and self.level >= self.max_level:
            self.game_over()

        # Adjust the probability of spawning power-ups based on the current level
        powerup_spawn_probability = max(0.001, 0.01 - (self.level * 0.002))  # Decrease frequency with level
        if len(self.powerups) < self.max_powerups and random.random() < powerup_spawn_probability:
            self.powerups.extend(self.create_powerups())  # Add new power-ups to the existing list

    def game_over(self):
        if self.sound_effects_playing:
            self.game_over_sound.play()
        self.high_score = update_high_score('pacman', self.score)  # Update high score if current score is higher
        action = show_game_over_screen(self.screen, self.score, self.high_score, self.level)
        if action == 'restart':
            self.level = 1
            self.reset_game()
        elif action == 'menu':
            self.running = False

    def level_up(self):
        if self.level < self.max_level:  # Ensure we don't exceed max level
            self.level += 1
            self.walls = self.create_walls()  # Create walls for the new level
            self.ghosts = self.create_ghosts()
            self.dots = self.create_dots()
            self.powerups = self.create_powerups()
            self.show_level_up_message()
            self.ghost_speed = 50 + (self.level * 10)  # Reset and increment ghost speed
            #self.add_more_walls() # this will break the game

    def add_more_walls(self):
        """Add more walls to the game based on the current level."""
        additional_walls = self.level * 5  # Increase the number of walls based on the level
        for _ in range(additional_walls):
            new_wall = [random.randint(0, 750), random.randint(0, 650)]
            # Ensure new wall does not overlap with existing walls
            while new_wall in self.walls:
                new_wall = [random.randint(0, 750), random.randint(0, 650)]
            self.walls.append(new_wall)  # Add random walls

    def show_level_up_message(self):
        # Use responsive font size
        font_size = max(36, min(self.screen_width, self.screen_height) // 15)
        font = pygame.font.Font(None, font_size)
        
        text_surface = font.render(f"Level Up! Now at Level {self.level}", True, (255, 255, 0))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        
        # Draw the overlay and text
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
        pygame.time.delay(2000)  # Show the message for 2 seconds

    def reset_game(self):
        # Reset all game elements with responsive positions
        self.pacman_pos = [self.screen_width // 2, self.screen_height - self.element_size * 3]
        self.dots = self.create_dots()
        self.ghosts = self.create_ghosts()
        self.powerups = self.create_powerups()
        self.score = 0
        self.super_mode = False
        self.super_mode_timer = 0
        self.running = True
        self.walls = self.create_walls()
        
        # Reset speeds based on current screen size
        self.pacman_speed = self.screen_width // 6
        self.ghost_speed = self.screen_width // 8

    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear the screen *FIRST*
        self.screen.blit(self.background_image, (0, 0))  # Draw background

        # Draw walls
        for wall in self.walls:
            self.screen.blit(self.wall_image, (wall[0], wall[1]))  # Draw wall

        for powerup in self.powerups:
            self.screen.blit(self.powerup_image, (powerup[0], powerup[1]))  # Draw food

        self.screen.blit(self.pacman_image, tuple(self.pacman_pos))  # Draw Pacman

        # Draw ghosts
        for ghost in self.ghosts:
            self.screen.blit(self.ghost_image, (ghost[0], ghost[1]))  # Draw ghost

        # Draw dots
        for dot in self.dots:
            self.screen.blit(self.dot_image, (dot[0], dot[1]))  # Draw dot

        # Draw power-ups
        for powerup in self.powerups:
            self.screen.blit(self.powerup_image, (powerup[0], powerup[1]))  # Draw power-up

        # Draw score - responsive font size
        font_size = max(24, self.screen_width // 40)
        font = pygame.font.Font(None, font_size)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 0))
        self.screen.blit(score_text, (10, 10))

        # Draw mute/unmute music button
        music_icon = self.music_icon_on if self.music_playing else self.music_icon_off
        self.screen.blit(music_icon, self.music_icon_pos)  # Draw music icon

        # Draw mute/unmute sound effects button
        sfx_icon = self.sfx_icon_on if self.sound_effects_playing else self.sfx_icon_off
        self.screen.blit(sfx_icon, self.sfx_icon_pos)  # Draw sound effects icon

        # Draw level indicator
        level_text = font.render(f'Level: {self.level}', True, (255, 255, 0))
        self.screen.blit(level_text, (10, 10 + font_size))

        # Draw super mode timer
        if self.super_mode:
            elapsed_time = time.time() - self.super_mode_timer
            if elapsed_time > 10:  # Super mode lasts for 10 seconds
                self.super_mode = False
            else:
                super_mode_text = font.render(f'Super Mode: {10 - int(elapsed_time)}', True, (255, 0, 0))
                self.screen.blit(super_mode_text, (10, 10 + font_size * 2))

    def toggle_music(self):
        if self.music_playing:
            pygame.mixer.music.pause()  # Pause music
            self.music_playing = False
        else:
            pygame.mixer.music.unpause()  # Unpause music
            self.music_playing = True

    def toggle_sound_effects(self):
        self.sound_effects_playing = not self.sound_effects_playing  # Toggle sound effects state

    def is_blocked(self, entity_pos, new_position):
        """Check if the new position is blocked by a wall."""
        for wall in self.walls:
            if (new_position[0] < wall[0] + self.element_size and 
                new_position[0] + self.element_size > wall[0] and
                new_position[1] < wall[1] + self.element_size and 
                new_position[1] + self.element_size > wall[1]):
                return True
        return False