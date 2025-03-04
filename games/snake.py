import pygame
import random
from util.high_score_manager import load_high_scores, update_high_score
from util.pause_screen_manager import show_pause_screen
from util.game_over_screen_manager import show_game_over_screen

class Snake:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.snake_pos = [[100, 50], [90, 50], [80, 50]]  # Initial snake position
        self.snake_direction = 'RIGHT'  # Initial direction
        self.food_pos = [random.randrange(1, (self.screen.get_width() // 10)) * 10,
                         random.randrange(1, (self.screen.get_height() // 10)) * 10]  # Random food position
        self.score = 0
        self.high_scores = load_high_scores()  # Load all high scores
        self.high_score = self.high_scores.get('snake', 0)  # Get high score for this game
        self.start_time = pygame.time.get_ticks()  # Timer start
        self.paused = False
        self.elapsed_time = 0  # Track elapsed time
        self.pause_start_time = 0  # Track when the game was paused
        self.game_over_sound = pygame.mixer.Sound('assets/space_invaders/game_over_space.wav')  # Load game over sound
        self.apple_image = pygame.image.load('assets/snake/apple.png')  # Load apple image
        self.snake_head_image = pygame.image.load('assets/snake/snake_head16.png')  # Load snake head image
        self.snake_body_image = pygame.image.load('assets/snake/snake_body16.png')  # Load snake body image
        self.snake_tail_image = pygame.image.load('assets/snake/snake_body16.png')
        #self.snake_tail_image = pygame.image.load('assets/snake/snake_tail.png')  # Load snake tail image

    def run(self):
        while self.running:
            self.handle_events()
            if not self.paused:  # Only update if not paused
                self.update()  # Update game state
                self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000  # Update elapsed time
                self.draw()  # Draw the game only if not paused
            else:
                show_pause_screen(self.screen)  # Show pause screen
            pygame.display.flip() 
            pygame.time.delay(100)  # Control the speed of the game

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake_direction != 'DOWN':
                    self.snake_direction = 'UP'
                elif event.key == pygame.K_DOWN and self.snake_direction != 'UP':
                    self.snake_direction = 'DOWN'
                elif event.key == pygame.K_LEFT and self.snake_direction != 'RIGHT':
                    self.snake_direction = 'LEFT'
                elif event.key == pygame.K_RIGHT and self.snake_direction != 'LEFT':
                    self.snake_direction = 'RIGHT'
                elif event.key == pygame.K_p:  # Pause the game
                    self.toggle_pause()

    def toggle_pause(self):
        self.paused = not self.paused  # Toggle pause state

    def update(self):
        if not self.paused:  # Only update if not paused
            # Move the snake
            head_x, head_y = self.snake_pos[0]
            if self.snake_direction == 'UP':
                head_y -= 10
            elif self.snake_direction == 'DOWN':
                head_y += 10
            elif self.snake_direction == 'LEFT':
                head_x -= 10
            elif self.snake_direction == 'RIGHT':
                head_x += 10

            # Insert new head
            self.snake_pos.insert(0, [head_x, head_y])

            # Check for food collision
            if self.snake_pos[0] == self.food_pos:
                self.score += 1
                self.food_pos = [random.randrange(1, (self.screen.get_width() // 10)) * 10,
                                 random.randrange(1, (self.screen.get_height() // 10)) * 10]  # Respawn food
            else:
                self.snake_pos.pop()  # Remove the last segment if no food eaten

            # Check for collisions with boundaries or self
            if (head_x < 0 or head_x >= self.screen.get_width() or
                    head_y < 0 or head_y >= self.screen.get_height() or
                    self.snake_pos[0] in self.snake_pos[1:]):
                self.game_over()  # Trigger game over

    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        #! background
        #background = pygame.image.load('background.png')  # Load background image
        #self.screen.blit(background, (0, 0))  # Draw background
        #! snake created using head, tail, and body parts
        if self.snake_pos:
            #* head
            self.screen.blit(self.snake_head_image, (self.snake_pos[0][0], self.snake_pos[0][1]))  # Draw head
            #* body segments using images
            for pos in self.snake_pos[1:-1]:
                self.screen.blit(self.snake_body_image, (pos[0], pos[1]))
            #*tail
            if len(self.snake_pos) > 1:
                self.screen.blit(self.snake_tail_image, (self.snake_pos[-1][0], self.snake_pos[-1][1]))  # Draw tail
        #! fruits
        self.screen.blit(self.apple_image, (self.food_pos[0], self.food_pos[1]))  # Draw apple using image
        
        # Display score and timer
        self.display_score_and_timer()

    def display_score_and_timer(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        timer_text = font.render(f'Time: {self.elapsed_time}', True, (255, 255, 255))  # Use elapsed_time
        self.screen.blit(score_text, (10, 10))  # Score at top left
        self.screen.blit(timer_text, (10, 40))  # Timer below score

    def game_over(self):
        self.game_over_sound.play()  # Play game over sound
        self.high_score = update_high_score('snake', self.score)  # Update high score if current score is higher
        action = show_game_over_screen(self.screen, self.score, self.high_score, 1)  # Assuming level is 1 for simplicity
        if action == 'restart':
            self.restart_game()
        elif action == 'menu':
            self.running = False

    def restart_game(self):
        self.snake_pos = [[100, 50], [90, 50], [80, 50]]  # Reset snake position
        self.snake_direction = 'RIGHT'  # Reset direction
        self.food_pos = [random.randrange(1, (self.screen.get_width() // 10)) * 10,
                         random.randrange(1, (self.screen.get_height() // 10)) * 10]  # Reset food position
        self.score = 0
        self.start_time = pygame.time.get_ticks()  # Reset timer
        self.running = True