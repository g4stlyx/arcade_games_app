import pygame
import random
import time
from util.high_score_manager import load_high_scores, update_high_score
from util.pause_screen_manager import show_pause_screen
from util.game_over_screen_manager import show_game_over_screen

class SpaceInvaders:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.running = True
        self.clock = pygame.time.Clock()
        self.player_image = pygame.image.load('assets/space_invaders/ship1.png')
        self.invader_images = [
            pygame.image.load('assets/space_invaders/invader.gif'),
            pygame.image.load('assets/space_invaders/alien2.png'),
            pygame.image.load('assets/space_invaders/alien3.png'),
            pygame.image.load('assets/space_invaders/alien4.png')
        ]
        self.bullet_image = pygame.image.load('assets/space_invaders/blasterbolt.png')
        self.background_image = pygame.image.load('assets/space_invaders/space2.jpg')
        # Scale background to fit screen
        self.background_image = pygame.transform.scale(self.background_image, (self.screen_width, self.screen_height))
        self.laser_sound = pygame.mixer.Sound('assets/space_invaders/laser.wav')
        self.explosion_sound = pygame.mixer.Sound('assets/space_invaders/explosion.wav')
        self.level_up_sound = pygame.mixer.Sound('assets/space_invaders/level_up_space.wav')

        # Calculate positions based on screen dimensions
        self.player_pos = [self.screen_width // 2 - self.player_image.get_width() // 2, 
                          self.screen_height - self.player_image.get_height() - 20]
        
        # Random invader positions with random images
        self.invaders = [
            [random.randint(0, self.screen_width - 50), 
             random.randint(100, 150), 
             random.choice(self.invader_images)] for _ in range(5)
        ]  
        
        self.lasers = []  # List to hold lasers
        self.score = 0
        self.high_scores = load_high_scores()  # Load all high scores
        self.high_score = self.high_scores.get('space_invaders', 0)  # Get high score for this game
        self.invader_direction = 1  # 1 for right, -1 for left
        self.invader_speed = 2  # Speed of invaders
        self.bullet_ready = True  # Bullet shooting logic
        self.game_over_threshold = self.screen_height // 12  # Threshold for game over condition
        self.level = 1  # Current level
        self.max_level = 5  # Maximum level
        self.elapsed_time = 0  # Total elapsed time
        self.start_time = time.time()  # Start time for the timer
        self.volume = 0.5  # Default volume level
        self.music_playing = True  # Track if music is playing
        self.sound_effects_playing = True  # Track if sound effects are playing
        
        # Load and scale icons based on screen size
        icon_size = min(50, self.screen_width // 16)
        self.music_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_on_white.png'), (icon_size, icon_size))
        self.music_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_off_white.png'), (icon_size, icon_size))
        self.sfx_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_on_white.png'), (icon_size, icon_size))
        self.sfx_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_off_white.png'), (icon_size, icon_size))
        
        # Calculate icon positions based on screen dimensions
        self.music_icon_pos = (self.screen_width - icon_size - 10, 10)
        self.sfx_icon_pos = (self.screen_width - icon_size - 10, icon_size + 20)
        
        self.paused = False  # Track if the game is paused

        # Load and play background music
        pygame.mixer.music.load('assets\sound_effects\menu\9. Space Debris.wav')
        pygame.mixer.music.set_volume(self.volume)  # Set initial volume
        pygame.mixer.music.play(-1) # Play music in a loop

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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.screen_width = self.screen.get_width()
                self.screen_height = self.screen.get_height()
                # Rescale background
                self.background_image = pygame.transform.scale(
                    pygame.image.load('assets/space_invaders/space2.jpg'),
                    (self.screen_width, self.screen_height)
                )
                # Recalculate player position
                self.player_pos[1] = self.screen_height - self.player_image.get_height() - 20
                
                # Recalculate icon positions and sizes
                icon_size = min(50, self.screen_width // 16)
                self.music_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_on_white.png'), (icon_size, icon_size))
                self.music_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_off_white.png'), (icon_size, icon_size))
                self.sfx_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_on_white.png'), (icon_size, icon_size))
                self.sfx_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_off_white.png'), (icon_size, icon_size))
                self.music_icon_pos = (self.screen_width - icon_size - 10, 10)
                self.sfx_icon_pos = (self.screen_width - icon_size - 10, icon_size + 20)
                
                # Update game over threshold
                self.game_over_threshold = self.screen_height // 12
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if mute/unmute music button is clicked
                    if (self.music_icon_pos[0] <= mouse_pos[0] <= self.music_icon_pos[0] + self.music_icon_on.get_width() and 
                        self.music_icon_pos[1] <= mouse_pos[1] <= self.music_icon_pos[1] + self.music_icon_on.get_height()):
                        self.toggle_music()
                    # Check if mute/unmute sound effects button is clicked
                    elif (self.sfx_icon_pos[0] <= mouse_pos[0] <= self.sfx_icon_pos[0] + self.sfx_icon_on.get_width() and 
                          self.sfx_icon_pos[1] <= mouse_pos[1] <= self.sfx_icon_pos[1] + self.sfx_icon_on.get_height()):
                        self.toggle_sound_effects()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Toggle pause with 'P' key
                    if self.paused:
                        # Resume: Adjust start time to account for pause duration
                        self.start_time = time.time() - self.elapsed_time
                    else:
                        # Pause: Just stop updating elapsed time
                        self.elapsed_time = time.time() - self.start_time
                    self.paused = not self.paused

        keys = pygame.key.get_pressed()
        move_speed = self.screen_width // 160  # Adaptive movement speed
        if keys[pygame.K_LEFT] and self.player_pos[0] > 0:
            self.player_pos[0] -= move_speed
        if keys[pygame.K_RIGHT] and self.player_pos[0] < self.screen_width - self.player_image.get_width():
            self.player_pos[0] += move_speed
        if keys[pygame.K_SPACE] and self.bullet_ready:
            self.shoot_bullet()

        # Volume control with keys (optional)
        if keys[pygame.K_UP]:
            self.volume = min(self.volume + 0.01, 1.0)  # Increase volume
            pygame.mixer.music.set_volume(self.volume)
        if keys[pygame.K_DOWN]:
            self.volume = max(self.volume - 0.01, 0.0)  # Decrease volume
            pygame.mixer.music.set_volume(self.volume)

    def toggle_music(self):
        if self.music_playing:
            pygame.mixer.music.pause()  # Pause music
            self.music_playing = False
        else:
            pygame.mixer.music.unpause()  # Unpause music
            self.music_playing = True

    def toggle_sound_effects(self):
        self.sound_effects_playing = not self.sound_effects_playing  # Toggle sound effects state

    def shoot_bullet(self):
        bullet_pos = [self.player_pos[0] + (self.player_image.get_width() // 2) - (self.bullet_image.get_width() // 2), 
                      self.player_pos[1] - 10]  # Center bullet above player
        self.lasers.append(bullet_pos)
        if self.sound_effects_playing:
            self.laser_sound.play()
        self.bullet_ready = False

    def update(self):
        if not self.paused:  # Only update the timer if not paused
            # Move bullets
            bullet_speed = self.screen_height // 60  # Adaptive bullet speed
            for bullet in self.lasers:
                bullet[1] -= bullet_speed
                if bullet[1] < 0:  # Bullet goes off screen
                    self.lasers.remove(bullet)
                    self.bullet_ready = True

            # Move invaders
            for invader in self.invaders:
                invader[0] += self.invader_direction * self.invader_speed

            # Check for invader boundaries
            if any(invader[0] <= 0 for invader in self.invaders) or any(invader[0] >= self.screen_width - 50 for invader in self.invaders):
                self.invader_direction *= -1  # Change direction
                for invader in self.invaders:
                    invader[1] += 10  # Move down

            # Check for collisions
            for bullet in self.lasers[:]:  # Use a copy for safe iteration
                for invader in self.invaders[:]:  # Use a copy for safe iteration
                    invader_width = invader[2].get_width()
                    invader_height = invader[2].get_height()
                    if (invader[0] < bullet[0] < invader[0] + invader_width and 
                        invader[1] < bullet[1] < invader[1] + invader_height):
                        if bullet in self.lasers:
                            self.lasers.remove(bullet)
                        if invader in self.invaders:
                            self.invaders.remove(invader)
                        self.score += 1
                        if self.sound_effects_playing:
                            self.explosion_sound.play()
                        self.bullet_ready = True
                        # Respawn the invader immediately
                        self.invaders.append([
                            random.randint(0, self.screen_width - 50), 
                            random.randint(100, 150), 
                            random.choice(self.invader_images)
                        ])
                        self.check_level_up()
                        break

            # Check for game over condition
            for invader in self.invaders:
                if invader[1] >= self.player_pos[1] - self.game_over_threshold:  # If any invader is close to player height
                    self.game_over()

    def check_level_up(self):
        # Level up based on score or time
        elapsed_time = time.time() - self.start_time
        if self.score >= self.level * 100 or elapsed_time >= self.level * 120:  # Level up every 100 points or every 2 minutes
            if self.level < self.max_level:
                self.level += 1
                self.invader_speed += 1
                self.invaders.append([
                    random.randint(0, self.screen_width - 50), 
                    random.randint(100, 150), 
                    random.choice(self.invader_images)
                ])  # Add an extra invader with random image
                if self.sound_effects_playing:
                    self.level_up_sound.play()
                self.show_level_up_message()
                print(f"Level Up! Current Level: {self.level}")

    def show_level_up_message(self):
        font = pygame.font.Font(None, max(24, self.screen_width // 20))  # Adaptive font size
        text_surface = font.render(f"Level Up! Now at Level {self.level}", True, (255, 255, 0))  # Render the text
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))  # Center the text
        self.screen.blit(text_surface, text_rect)  # Position the text on the screen
        pygame.display.flip()  # Update the display
        pygame.time.delay(2000)  # Show the message for 2 seconds

    def game_over(self):
        self.play_game_over_sound()
        self.show_game_over_reason()
        self.high_score = update_high_score('space_invaders', self.score)  # Update high score if current score is higher
        action = show_game_over_screen(self.screen, self.score, self.high_score, self.level)
        if action == 'restart':
            self.reset_game()
        elif action == 'menu':
            self.running = False

    def show_game_over_reason(self):
        font = pygame.font.Font(None, max(24, self.screen_width // 20))  # Adaptive font size
        text_surface = font.render("Game Over! Invaders reached your base!", True, (255, 0, 0))  # Render the text
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))  # Center the text
        self.screen.blit(text_surface, text_rect)  # Position the text on the screen
        pygame.display.flip()  # Update the display
        pygame.time.delay(2000)  # Show the message for 2 seconds

    def play_game_over_sound(self):
        game_over_sound = pygame.mixer.Sound('assets/space_invaders/game_over_space.wav')
        if self.sound_effects_playing:
            game_over_sound.play()

    def reset_game(self):
        # Reset player position based on screen size
        self.player_pos = [self.screen_width // 2 - self.player_image.get_width() // 2, 
                          self.screen_height - self.player_image.get_height() - 20]
        # Reset invaders based on screen size
        self.invaders = [
            [random.randint(0, self.screen_width - 50), 
             random.randint(100, 150), 
             random.choice(self.invader_images)] for _ in range(5)
        ]
        self.lasers = [] 
        self.score = 0
        self.bullet_ready = True
        self.invader_direction = 1
        self.invader_speed = 2
        self.level = 1
        self.start_time = time.time()
        self.running = True

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))  # background
        self.screen.blit(self.player_image, tuple(self.player_pos))  # player

        # invaders
        for invader in self.invaders:
            self.screen.blit(invader[2], (invader[0], invader[1]))  # Draw invader using the selected image

        # bullets
        for bullet in self.lasers:
            self.screen.blit(self.bullet_image, (bullet[0], bullet[1])) 

        # score and level
        font_size = max(18, self.screen_width // 40)  # Adaptive font size
        font = pygame.font.Font(None, font_size)
        score_text = font.render(f'Score: {self.score}', True, (28, 237, 28))
        level_text = font.render(f'Level: {self.level}', True, (28, 237, 28))
        elapsed_time = self.elapsed_time if self.paused else time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        timer_text = font.render(f'Time: {minutes:02}:{seconds:02}', True, (28, 237, 28))

        # score, level, timer info
        margin = self.screen_width // 50
        self.screen.blit(score_text, (margin, margin))
        self.screen.blit(level_text, (margin + score_text.get_width() + margin, margin))
        self.screen.blit(timer_text, (margin + score_text.get_width() + level_text.get_width() + 2 * margin, margin))

        # Draw mute/unmute music button
        music_icon = self.music_icon_on if self.music_playing else self.music_icon_off
        self.screen.blit(music_icon, self.music_icon_pos)  # Draw music icon

        # Draw mute/unmute sound effects button
        sfx_icon = self.sfx_icon_on if self.sound_effects_playing else self.sfx_icon_off
        self.screen.blit(sfx_icon, self.sfx_icon_pos)  # Draw sound effects icon

        pygame.display.flip()
