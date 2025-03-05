import pygame
import random
import time
import math
from util.high_score_manager import load_high_scores, update_high_score
from util.pause_screen_manager import show_pause_screen
from util.game_over_screen_manager import show_game_over_screen

class FlappyBird:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Adaptive sizes based on screen dimensions
        self.scale_factor = min(self.screen_width, self.screen_height) / 800
        self.bird_size = int(40 * self.scale_factor)
        self.pipe_width = int(80 * self.scale_factor)
        self.gap_height = int(200 * self.scale_factor)
        
        # Load assets and scale them
        self.bird_image = pygame.transform.scale(
            pygame.image.load('assets/space_invaders/ship2.png'), 
            (self.bird_size, self.bird_size)
        )
        self.pipe_image = pygame.image.load('assets/space_invaders/alien4.png')
        self.background_image = pygame.transform.scale(
            pygame.image.load('assets/space_invaders/space1.jpg'),
            (self.screen_width, self.screen_height)
        )
        
        # Sound effects
        self.flap_sound = pygame.mixer.Sound('assets/space_invaders/level_up_space.wav')
        self.hit_sound = pygame.mixer.Sound('assets/space_invaders/explosion.wav')
        self.score_sound = pygame.mixer.Sound('assets/space_invaders/level_up_space.wav')
        
        # Game state variables
        self.reset_game()
        
        # Score tracking
        self.high_scores = load_high_scores()
        self.high_score = self.high_scores.get('flappy_bird', 0)
        
        # Sound and music settings
        self.volume = 0.5
        self.music_playing = True
        self.sound_effects_playing = True
        
        # Load and scale icons based on screen size
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
        
        # Calculate icon positions based on screen dimensions
        self.music_icon_pos = (self.screen_width - icon_size - 10, 10)
        self.sfx_icon_pos = (self.screen_width - icon_size - 10, icon_size + 20)
        
        # Load and play background music
        pygame.mixer.music.load('assets/space_invaders/explosion.wav')
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)  # Play music in a loop

    def reset_game(self):
        # Bird position and physics (responsive to screen size)
        self.bird_x = self.screen_width // 4
        self.bird_y = self.screen_height // 2
        self.bird_velocity = 0
        self.gravity = 0.5 * self.scale_factor
        self.flap_strength = -10 * self.scale_factor
        
        # Pipe generation
        self.pipe_speed = 3 * self.scale_factor
        self.pipes = []
        self.add_new_pipe()
        
        # Game state
        self.score = 0
        self.game_started = False
        self.paused = False
        self.start_time = time.time()
        self.elapsed_time = 0
        self.last_pipe_time = time.time()
        self.pipe_interval = 2.5  # Seconds between pipe spawns

    def add_new_pipe(self):
        # Create a new pipe with random gap position
        gap_y = random.randint(
            int(self.gap_height/2), 
            int(self.screen_height - self.gap_height/2)
        )
        
        self.pipes.append({
            'x': self.screen_width,
            'gap_y': gap_y,
            'scored': False
        })

    def run(self):
        while self.running:
            delta_time = self.clock.get_time() / 1000  # Delta time in seconds
            self.handle_events()
            
            if not self.paused:
                if self.game_started:
                    self.update(delta_time)
                self.elapsed_time = time.time() - self.start_time
                self.draw()
            else:
                show_pause_screen(self.screen)
                
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Update screen dimensions
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.screen_width = self.screen.get_width()
                self.screen_height = self.screen.get_height()
                
                # Recalculate scale factor and sizes
                self.scale_factor = min(self.screen_width, self.screen_height) / 800
                self.bird_size = int(40 * self.scale_factor)
                self.pipe_width = int(80 * self.scale_factor)
                self.gap_height = int(200 * self.scale_factor)
                
                # Rescale images
                self.bird_image = pygame.transform.scale(
                    # pygame.image.load('assets/flappy_bird/bird.png'),
                    pygame.image.load('assets/space_invaders/ship2.png'),
                    (self.bird_size, self.bird_size)
                )
                self.background_image = pygame.transform.scale(
                    # pygame.image.load('assets/flappy_bird/background.png'),
                    pygame.image.load('assets/space_invaders/space1.jpg'),
                    (self.screen_width, self.screen_height)
                )
                
                # Update physics parameters
                self.gravity = 0.5 * self.scale_factor
                self.flap_strength = -10 * self.scale_factor
                self.pipe_speed = 3 * self.scale_factor
                
                # Update icon positions
                icon_size = min(50, self.screen_width // 16)
                self.music_icon_pos = (self.screen_width - icon_size - 10, 10)
                self.sfx_icon_pos = (self.screen_width - icon_size - 10, icon_size + 20)
                
                # Rescale icons
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_started:
                        self.game_started = True
                        self.start_time = time.time()
                    self.flap()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                    if not self.paused:
                        # Adjust start time when unpausing
                        self.start_time = time.time() - self.elapsed_time
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if music icon is clicked
                    mouse_pos = pygame.mouse.get_pos()
                    if (self.music_icon_pos[0] <= mouse_pos[0] <= self.music_icon_pos[0] + self.music_icon_on.get_width() and
                        self.music_icon_pos[1] <= mouse_pos[1] <= self.music_icon_pos[1] + self.music_icon_on.get_height()):
                        self.toggle_music()
                    # Check if sound effects icon is clicked
                    elif (self.sfx_icon_pos[0] <= mouse_pos[0] <= self.sfx_icon_pos[0] + self.sfx_icon_on.get_width() and
                          self.sfx_icon_pos[1] <= mouse_pos[1] <= self.sfx_icon_pos[1] + self.sfx_icon_on.get_height()):
                        self.toggle_sound_effects()
                    # Otherwise flap
                    elif not self.paused:
                        if not self.game_started:
                            self.game_started = True
                            self.start_time = time.time()
                        self.flap()

    def flap(self):
        self.bird_velocity = self.flap_strength
        if self.sound_effects_playing:
            self.flap_sound.play()

    def toggle_music(self):
        if self.music_playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.music_playing = not self.music_playing

    def toggle_sound_effects(self):
        self.sound_effects_playing = not self.sound_effects_playing

    def update(self, delta_time):
        # Apply gravity and update bird position
        self.bird_velocity += self.gravity
        self.bird_y += self.bird_velocity
        
        # Rotate bird based on velocity (dive angle)
        rotation_angle = math.degrees(math.atan(self.bird_velocity / 10))
        rotated_bird = pygame.transform.rotate(self.bird_image, -rotation_angle)
        
        # Check for collisions with ceiling and floor
        if self.bird_y <= 0 or self.bird_y >= self.screen_height - self.bird_size:
            if self.sound_effects_playing:
                self.hit_sound.play()
            self.game_over()
            return
            
        # Spawn new pipes on interval
        current_time = time.time()
        if current_time - self.last_pipe_time > self.pipe_interval:
            self.add_new_pipe()
            self.last_pipe_time = current_time
            
        # Update pipe positions
        for pipe in self.pipes[:]:
            pipe['x'] -= self.pipe_speed
            
            # Check for score
            if not pipe['scored'] and pipe['x'] < self.bird_x - self.bird_size:
                pipe['scored'] = True
                self.score += 1
                if self.sound_effects_playing:
                    self.score_sound.play()
                
            # Check for collisions
            if self.check_collision(pipe):
                if self.sound_effects_playing:
                    self.hit_sound.play()
                self.game_over()
                return
                
            # Remove pipes that are off-screen
            if pipe['x'] < -self.pipe_width:
                self.pipes.remove(pipe)
    
    def check_collision(self, pipe):
        # Create a simplified hitbox for the bird
        bird_rect = pygame.Rect(
            self.bird_x, 
            self.bird_y, 
            self.bird_size * 0.8,  # Make hitbox slightly smaller than image
            self.bird_size * 0.8
        )
        
        # Create hitboxes for top and bottom pipes
        top_pipe_rect = pygame.Rect(
            pipe['x'],
            0,
            self.pipe_width,
            pipe['gap_y'] - self.gap_height/2
        )
        
        bottom_pipe_rect = pygame.Rect(
            pipe['x'],
            pipe['gap_y'] + self.gap_height/2,
            self.pipe_width,
            self.screen_height - (pipe['gap_y'] + self.gap_height/2)
        )
        
        # Check for collisions
        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)
    
    def draw(self):
        # Draw background
        self.screen.blit(self.background_image, (0, 0))
        
        # Draw pipes
        for pipe in self.pipes:
            # Draw top pipe (flipped)
            top_pipe = pygame.transform.scale(
                self.pipe_image,
                (self.pipe_width, pipe['gap_y'] - self.gap_height/2)
            )
            top_pipe = pygame.transform.flip(top_pipe, False, True)
            self.screen.blit(top_pipe, (pipe['x'], 0))
            
            # Draw bottom pipe
            bottom_pipe = pygame.transform.scale(
                self.pipe_image,
                (self.pipe_width, self.screen_height - (pipe['gap_y'] + self.gap_height/2))
            )
            self.screen.blit(bottom_pipe, (pipe['x'], pipe['gap_y'] + self.gap_height/2))
        
        # Draw bird with rotation based on velocity
        rotation_angle = math.degrees(math.atan(self.bird_velocity / 10))
        rotated_bird = pygame.transform.rotate(self.bird_image, -rotation_angle)
        rotated_rect = rotated_bird.get_rect(center=(self.bird_x + self.bird_size/2, self.bird_y + self.bird_size/2))
        self.screen.blit(rotated_bird, rotated_rect.topleft)
        
        # Draw score - with responsive font size
        font_size = max(24, self.screen_width // 20)
        font = pygame.font.Font(None, font_size)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw high score
        high_score_text = font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
        self.screen.blit(high_score_text, (10, 10 + font_size))
        
        # Draw "Press Space to Start" if game hasn't started
        if not self.game_started:
            start_font_size = max(36, self.screen_width // 15)
            start_font = pygame.font.Font(None, start_font_size)
            start_text = start_font.render("Press Space to Start", True, (255, 255, 255))
            start_text_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            
            # Draw text with shadow for better visibility
            shadow_text = start_font.render("Press Space to Start", True, (0, 0, 0))
            shadow_rect = shadow_text.get_rect(center=(self.screen_width // 2 + 2, self.screen_height // 2 + 2))
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(start_text, start_text_rect)
        
        # Draw sound icons
        music_icon = self.music_icon_on if self.music_playing else self.music_icon_off
        self.screen.blit(music_icon, self.music_icon_pos)
        
        sfx_icon = self.sfx_icon_on if self.sound_effects_playing else self.sfx_icon_off
        self.screen.blit(sfx_icon, self.sfx_icon_pos)

    def game_over(self):
        # Update high score if needed
        self.high_score = update_high_score('flappy_bird', self.score)
        
        # Show game over screen
        action = show_game_over_screen(self.screen, self.score, self.high_score, 1)  # Level is always 1
        
        if action == 'restart':
            self.reset_game()
        elif action == 'menu':
            self.running = False