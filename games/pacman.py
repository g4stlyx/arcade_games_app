import pygame
import random
import time
from util.high_score_manager import load_high_scores, update_high_score
from util.pause_screen_manager import show_pause_screen
from util.game_over_screen_manager import show_game_over_screen

class PacmanGame:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.pacman_image = pygame.transform.scale(pygame.image.load('assets/pacman/pacman.png'), (16, 16))
        self.ghost_image = pygame.image.load('assets/snake/mouse.png')
        self.dot_image = pygame.image.load('assets/snake/apple.png')
        self.powerup_image = pygame.image.load('assets/space_invaders/ufo.png')
        self.background_image = pygame.image.load('assets/space_invaders/space2.jpg')
        self.wall_image = pygame.image.load('assets/pacman/grass16.png')
        self.eat_sound = pygame.mixer.Sound('assets/space_invaders/level_up_space.wav')
        self.game_over_sound = pygame.mixer.Sound('assets/space_invaders/game_over_space.wav')

        self.pacman_pos = [375, 650]
        self.pacman_speed = 150  # Adjusted for pixel/second
        self.ghost_speed = 100  # Adjusted for pixel/second
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
        self.music_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_on_white.png'), (50, 50))  # Load and scale music on icon
        self.music_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_off_white.png'), (50, 50))  # Load and scale music off icon
        self.sfx_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_on_white.png'), (50, 50))  # Load and scale sound effects on icon
        self.sfx_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_off_white.png'), (50, 50))  # Load and scale sound effects off icon
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

        level1 = []
        for i in range(int(5 * density_scale)):
            level1.append((random.randint(50, 700), random.randint(50, 600)))

        level2 = []
        for i in range(int(10 * density_scale)):
            x = random.randint(50, 700)
            y = random.randint(50, 600)
            level2.append((x, y))
            level2.append((x + 16, y))
            level2.append((x, y + 16))

        level3 = []
        for i in range(int(15 * density_scale)):
            x = random.randint(50, 700)
            y = random.randint(50, 600)
            level3.append((x, y))
            level3.append((x + 16, y))
            level3.append((x, y + 16))
            level3.append((x + 16, y + 16))

        level4 = []
        for i in range(int(20 * density_scale)):
            x = random.randint(50, 700)
            y = random.randint(50, 600)
            level4.append((x, y))
            level4.append((x + 16, y))
            level4.append((x, y + 16))
            level4.append((x - 16, y))
            level4.append((x, y - 16))

        level5 = []
        for i in range(int(25 * density_scale)):
            x = random.randint(50, 700)
            y = random.randint(50, 600)
            level5.append((x, y))
            level5.append((x + 16, y))
            level5.append((x, y + 16))
            level5.append((x - 16, y))
            level5.append((x, y - 16))
            level5.append((x + 32, y))
            level5.append((x, y + 32))

        return [level1, level2, level3, level4, level5]
    
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
        return [[random.randint(0, 750), random.randint(0, 650)] for _ in range(100)]

    def create_ghosts(self):
        """Create a list of ghosts at random positions, away from Pac-Man."""
        ghosts = []
        while len(ghosts) < 4:
            x = random.randint(0, 750)
            y = random.randint(0, 650)
            # Ensure ghosts are reasonably far from Pac-Man on creation
            if ((x - self.pacman_pos[0])**2 + (y - self.pacman_pos[1])**2) > 200**2:
                valid_position = True
                for wall in self.walls:
                    if (x < wall[0] + 25 and x + 20 > wall[0] and y < wall[1] + 25 and y + 20 > wall[1]):
                        valid_position = False
                        break  # Skip this position if it's inside a wall

                if valid_position:
                    ghosts.append([x, y])
        return ghosts

    def create_powerups(self):
        """Create a list of power-ups at random positions, ensuring they don't overlap with walls."""
        powerups = []
        while len(powerups) < 2:  # Create up to 2 power-ups
            x = random.randint(0, 750)
            y = random.randint(0, 650)
            new_powerup = [x, y]

            # Check if the power-up overlaps with a wall
            valid_position = True
            for wall in self.walls:
                if (x < wall[0] + 25 and x + 20 > wall[0] and y < wall[1] + 25 and y + 20 > wall[1]):
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Toggle pause with 'P' key
                    self.paused = not self.paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    if 750 <= mouse_pos[0] <= 790 and 10 <= mouse_pos[1] <= 50:  # Check if mute/unmute music button is clicked
                        self.toggle_music()
                    elif 750 <= mouse_pos[0] <= 790 and 60 <= mouse_pos[1] <= 100:  # Check if mute/unmute sound effects button is clicked
                        self.toggle_sound_effects()


        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            new_x = self.pacman_pos[0] - self.pacman_speed * delta_time
            if new_x >= 0 and not self.is_blocked(self.pacman_pos, [new_x, self.pacman_pos[1]]):
                self.pacman_pos[0] = new_x
        if keys[pygame.K_RIGHT]:
            new_x = self.pacman_pos[0] + self.pacman_speed * delta_time
            if new_x <= self.screen.get_width() - 16 and not self.is_blocked(self.pacman_pos, [new_x, self.pacman_pos[1]]):
                self.pacman_pos[0] = new_x
        if keys[pygame.K_UP]:
            new_y = self.pacman_pos[1] - self.pacman_speed * delta_time
            if new_y >= 0 and not self.is_blocked(self.pacman_pos, [self.pacman_pos[0], new_y]):
                self.pacman_pos[1] = new_y
        if keys[pygame.K_DOWN]:
            new_y = self.pacman_pos[1] + self.pacman_speed * delta_time
            if  new_y <= self.screen.get_height() - 16 and not self.is_blocked(self.pacman_pos, [self.pacman_pos[0], new_y]):
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
        font = pygame.font.Font(None, 48)  # Create a font object
        text_surface = font.render(f"Level Up! Now at Level {self.level}", True, (255, 255, 0))  # Render the text
        text_rect = text_surface.get_rect(center=(400, 300))  # Center the text horizontally
        self.screen.blit(text_surface, text_rect)  # Position the text on the screen
        pygame.display.flip()  # Update the display
        pygame.time.delay(2000)  # Show the message for 2 seconds

        self.reset_game()

    def reset_game(self):
        self.pacman_pos = [375, 650]
        self.dots = self.create_dots()
        self.ghosts = self.create_ghosts()
        self.powerups = self.create_powerups()
        self.score = 0
        self.super_mode = False
        self.super_mode_timer = 0
        self.running = True
        self.walls = self.create_walls()

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

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 0))
        self.screen.blit(score_text, (10, 10))

        # Draw mute/unmute music button
        self.music_icon = self.music_icon_on if self.music_playing else self.music_icon_off
        self.screen.blit(self.music_icon, (750, 10))  # Draw music icon

        # Draw mute/unmute sound effects button
        self.sfx_icon = self.sfx_icon_on if self.sound_effects_playing else self.sfx_icon_off
        self.screen.blit(self.sfx_icon, (750, 60))  # Draw sound effects icon

        # Draw super mode timer
        if self.super_mode:
            elapsed_time = time.time() - self.super_mode_timer
            if elapsed_time > 10:  # Super mode lasts for 10 seconds
                self.super_mode = False
            else:
                font = pygame.font.Font(None, 36)
                super_mode_text = font.render(f'Super Mode: {10 - int(elapsed_time)}', True, (255, 0, 0))
                self.screen.blit(super_mode_text, (10, 50))

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
        # Slightly increased bounding box size for more reliable collision detection
        entity_size = 16  # Size of Pacman and Ghost images
        for wall in self.walls:
            if (new_position[0] < wall[0] + 25 and new_position[0] + entity_size > wall[0] and
                new_position[1] < wall[1] + 25 and new_position[1] + entity_size > wall[1]):
                return True
        return False