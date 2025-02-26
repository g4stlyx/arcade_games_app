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
        self.eat_sound = pygame.mixer.Sound('assets/space_invaders/level_up_space.wav')
        self.game_over_sound = pygame.mixer.Sound('assets/space_invaders/game_over_space.wav')

        self.pacman_pos = [375, 650]
        self.pacman_speed = 5  # Add a speed attribute for Pac-Man's movement
        self.dots = self.create_dots()
        self.ghosts = self.create_ghosts()
        self.powerups = self.create_powerups()
        self.wall_image = pygame.image.load('assets/pacman/grass16.png')
        self.walls = self.create_walls()
        self.level = 1
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
        
        # Load and play background music
        pygame.mixer.music.load('assets/sound_effects/menu/9. Space Debris.wav')
        pygame.mixer.music.set_volume(self.volume)  # Set initial volume
        pygame.mixer.music.play(-1)  # Play music in a loop

    def run(self):
        while self.running:
            self.handle_events()
            if not self.paused:  # Only update if not paused
                self.update()  # Update game state
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
        """Create a list of ghosts at random positions."""
        return [[random.randint(0, 750), random.randint(0, 650)] for _ in range(4)]

    def create_powerups(self):
        """Create a list of power-ups at random positions."""
        return [[random.randint(0, 750), random.randint(0, 650)] for _ in range(5)]

    def create_walls(self):
        """Create a list of wall positions."""
        walls = []
        clusters = [
            [(100, 100), (132, 100), (100, 132)],
            [(300, 300), (332, 300), (300, 332)],
            [(500, 500), (532, 500), (500, 532)],
            [(700, 700), (732, 700), (700, 732)],
            [(200, 200), (232, 200), (200, 232)],
            [(400, 400), (432, 400), (400, 432)],
            [(600, 600), (632, 600), (600, 632)]
        ]
        for cluster in clusters:
            walls.extend(cluster)
        for _ in range(50):  # Add 50 random walls
            walls.append([random.randint(0, 768), random.randint(0, 768)])
        return walls

    def handle_events(self):
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
        if keys[pygame.K_LEFT] and self.pacman_pos[0] > 0:
            self.pacman_pos[0] -= self.pacman_speed
        elif keys[pygame.K_RIGHT] and self.pacman_pos[0] < 750:
            self.pacman_pos[0] += self.pacman_speed
        elif keys[pygame.K_UP] and self.pacman_pos[1] > 0:
            self.pacman_pos[1] -= self.pacman_speed
        elif keys[pygame.K_DOWN] and self.pacman_pos[1] < 650:
            self.pacman_pos[1] += self.pacman_speed

    def update(self):
        # Check for collisions with walls
        for wall in self.walls:
            if self.pacman_pos[0] < wall[0] + 32 and self.pacman_pos[0] + 32 > wall[0] and self.pacman_pos[1] < wall[1] + 32 and self.pacman_pos[1] + 32 > wall[1]:
                if self.pacman_pos[0] < wall[0]:
                    self.pacman_pos[0] -= self.pacman_speed
                elif self.pacman_pos[0] > wall[0]:
                    self.pacman_pos[0] += self.pacman_speed
                if self.pacman_pos[1] < wall[1]:
                    self.pacman_pos[1] -= self.pacman_speed
                elif self.pacman_pos[1] > wall[1]:
                    self.pacman_pos[1] += self.pacman_speed

        for ghost in self.ghosts:
            for wall in self.walls:
                if ghost[0] < wall[0] + 32 and ghost[0] + 32 > wall[0] and ghost[1] < wall[1] + 32 and ghost[1] + 32 > wall[1]:
                    if ghost[0] < wall[0]:
                        ghost[0] -= 2
                    elif ghost[0] > wall[0]:
                        ghost[0] += 2
                    if ghost[1] < wall[1]:
                        ghost[1] -= 2
                    elif ghost[1] > wall[1]:
                        ghost[1] += 2

                if ghost[0] < 0:
                    ghost[0] = 0
                elif ghost[0] > 768:
                    ghost[0] = 768
                if ghost[1] < 0:
                    ghost[1] = 0
                elif ghost[1] > 768:
                    ghost[1] = 768

        for dot in list(self.dots):  # Iterate over a copy to allow removal
            if (dot[0] < self.pacman_pos[0] < dot[0] + 20) and (dot[1] < self.pacman_pos[1] < dot[1] + 20):
                self.dots.remove(dot)
                self.score += 1
                if self.sound_effects_playing:
                    self.eat_sound.play()

        # Move ghosts
        for ghost in self.ghosts:
            if self.super_mode:
                if ghost[0] < self.pacman_pos[0]:
                    ghost[0] -= 2
                elif ghost[0] > self.pacman_pos[0]:
                    ghost[0] += 2
                elif ghost[1] < self.pacman_pos[1]:
                    ghost[1] -= 2
                elif ghost[1] > self.pacman_pos[1]:
                    ghost[1] += 2
            else:
                if ghost[0] < self.pacman_pos[0]:
                    ghost[0] += 2
                elif ghost[0] > self.pacman_pos[0]:
                    ghost[0] -= 2
                elif ghost[1] < self.pacman_pos[1]:
                    ghost[1] += 2
                elif ghost[1] > self.pacman_pos[1]:
                    ghost[1] -= 2

        for ghost in self.ghosts:
            if (ghost[0] < self.pacman_pos[0] < ghost[0] + 20) and (ghost[1] < self.pacman_pos[1] < ghost[1] + 20):
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

        # Check for level up condition (if no ghosts left)
        if not self.ghosts:
            self.level_up()

        if not self.dots:
            self.game_over()

    def game_over(self):
        self.game_over_sound.play()
        self.high_score = update_high_score('pacman', self.score)  # Update high score if current score is higher
        action = show_game_over_screen(self.screen, self.score, self.high_score, 1)  # Assuming level is 1 for simplicity
        if action == 'restart':
            self.reset_game()
        elif action == 'menu':
            self.running = False

    def level_up(self):
        self.level += 1
        self.ghosts = self.create_ghosts()
        self.dots = self.create_dots()
        self.powerups = self.create_powerups()
        self.show_level_up_message()

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
        self.level = 1
        self.running = True

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