import pygame
import random
import time
from util.high_score_manager import load_high_scores, update_high_score
from util.pause_screen_manager import show_pause_screen
from util.game_over_screen_manager import show_game_over_screen

class PacMan:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.pacman_image = pygame.image.load('assets/space_invaders/ship2.png')
        self.food_image = pygame.image.load('assets/space_invaders/ship2.png')
        self.background_image = pygame.image.load('assets/space_invaders/ship2.png')
        self.eat_sound = pygame.mixer.Sound('assets/space_invaders/game_over_space.wav')
        self.game_over_sound = pygame.mixer.Sound('assets/space_invaders/game_over_space.wav')

        self.pacman_pos = [375, 650]
        self.pacman_speed = 5  # Add a speed attribute for Pac-Man's movement
        self.food_count = 10  # Control the number of food items
        self.foods = self.create_food()
        self.score = 0
        self.high_scores = load_high_scores()  # Load all high scores
        self.high_score = self.high_scores.get('pacman', 0)  # Get high score for this game
        self.paused = False  # Track if the game is paused
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

    def create_food(self):
        """Create a list of food items at random positions."""
        return [[random.randint(0, 750), random.randint(0, 650)] for _ in range(self.food_count)]

    def run(self):
        while self.running:
            self.handle_events()
            if not self.paused:  # Only update if not paused
                self.update()  # Update game state
                self.draw()  # Draw the game only if not paused
            else:
                show_pause_screen(self.screen)  # Show pause screen
            pygame.display.flip()
            self.clock.tick(60)  # Limit to 60 frames per second

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
        if keys[pygame.K_RIGHT] and self.pacman_pos[0] < 750:
            self.pacman_pos[0] += self.pacman_speed
        if keys[pygame.K_UP] and self.pacman_pos[1] > 0:
            self.pacman_pos[1] -= self.pacman_speed
        if keys[pygame.K_DOWN] and self.pacman_pos[1] < 650:
            self.pacman_pos[1] += self.pacman_speed

    def update(self):
        # Check for collisions with food
        for food in list(self.foods): #Iterate over a copy to allow removal
            if (food[0] < self.pacman_pos[0] < food[0] + 20) and (food[1] < self.pacman_pos[1] < food[1] + 20):
                self.foods.remove(food)
                self.score += 1
                if self.sound_effects_playing:
                    self.eat_sound.play()

        # Check for game over condition (if no food left)
        if not self.foods:
            self.game_over()

    def game_over(self):
        self.game_over_sound.play()
        self.high_score = update_high_score('pacman', self.score)  # Update high score if current score is higher
        action = show_game_over_screen(self.screen, self.score, self.high_score, 1)  # Assuming level is 1 for simplicity
        if action == 'restart':
            self.reset_game()
        elif action == 'menu':
            self.running = False

    def reset_game(self):
        self.pacman_pos = [375, 650]
        self.foods = self.create_food()
        self.score = 0
        self.running = True  # Reset everything and restart the game loop

    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear the screen *FIRST*
        self.screen.blit(self.background_image, (0, 0))  # Draw background

        # Draw foods
        for food in self.foods:
            self.screen.blit(self.food_image, (food[0], food[1]))  # Draw food

        self.screen.blit(self.pacman_image, tuple(self.pacman_pos))  # Draw Pac-Man

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 0))
        self.screen.blit(score_text, (10, 10))

        # Draw mute/unmute music button
        music_icon = self.music_icon_on if self.music_playing else self.music_icon_off
        self.screen.blit(music_icon, (750, 10))  # Draw music icon

        # Draw mute/unmute sound effects button
        sfx_icon = self.sfx_icon_on if self.sound_effects_playing else self.sfx_icon_off
        self.screen.blit(sfx_icon, (750, 60))  # Draw sound effects icon

        pygame.display.flip()

    def toggle_music(self):
        if self.music_playing:
            pygame.mixer.music.pause()  # Pause music
            self.music_playing = False
        else:
            pygame.mixer.music.unpause()  # Unpause music
            self.music_playing = True

    def toggle_sound_effects(self):
        self.sound_effects_playing = not self.sound_effects_playing  # Toggle sound effects state