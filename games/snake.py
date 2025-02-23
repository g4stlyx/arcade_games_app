import pygame
import random

class Snake:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.snake_pos = [[100, 50], [90, 50], [80, 50]]  # Initial snake position
        self.snake_direction = 'RIGHT'  # Initial direction
        self.food_pos = [random.randrange(1, (self.screen.get_width() // 10)) * 10,
                         random.randrange(1, (self.screen.get_height() // 10)) * 10]  # Random food position
        self.score = 0
        self.high_score = 0
        self.start_time = pygame.time.get_ticks()  # Timer start
        self.paused = False
        self.elapsed_time = 0  # Track elapsed time
        self.pause_start_time = 0  # Track when the game was paused

    def run(self):
        while self.running:
            self.handle_events()
            if not self.paused:
                self.update()
                self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000  # Update elapsed time
            self.draw()
            pygame.time.delay(100)  # Control the speed of the game

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
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
        for pos in self.snake_pos:
            pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(pos[0], pos[1], 10, 10))  # Draw snake
        pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(self.food_pos[0], self.food_pos[1], 10, 10))  # Draw food
        
        # Display score and timer
        self.display_score_and_timer()

        # Show paused message if paused
        if self.paused:
            self.show_paused_message()

        pygame.display.flip()  # Update the display

    def display_score_and_timer(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        timer_text = font.render(f'Time: {self.elapsed_time}', True, (255, 255, 255))  # Use elapsed_time
        self.screen.blit(score_text, (10, 10))  # Score at top left
        self.screen.blit(timer_text, (10, 40))  # Timer below score

    def show_paused_message(self):
        font = pygame.font.Font(None, 48)
        paused_text = font.render('PAUSED, press P to continue', True, (255, 255, 255))
        self.screen.blit(paused_text, (self.screen.get_width() // 2 - paused_text.get_width() // 2,
                                        self.screen.get_height() // 2 - paused_text.get_height() // 2))

    def game_over(self):
        self.running = False  # End the game
        self.game_over_menu()  # Show the game over menu

    def game_over_menu(self):
        # Game Over Menu
        while True:
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 48)
            game_over_text = font.render('Game Over', True, (255, 0, 0))
            self.screen.blit(game_over_text, (self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 100))
            score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
            high_score_text = font.render(f'High Score: {self.high_score}', True, (255, 255, 255))
            self.screen.blit(score_text, (self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 50))
            self.screen.blit(high_score_text, (self.screen.get_width() // 2 - 100, self.screen.get_height() // 2))

            # Menu options
            options = ['Restart (R)', 'Quit to Menu (M)', 'Quit Game (Q)']
            for i, option in enumerate(options):
                option_text = font.render(option, True, (255, 255, 255))
                self.screen.blit(option_text, (self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 + 50 + i * 40))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart
                        self.restart_game()
                        return
                    elif event.key == pygame.K_m:  # Quit to menu
                        self.running = False
                        return
                    elif event.key == pygame.K_q:  # Quit game
                        pygame.quit()
                        return

    def restart_game(self):
        self.snake_pos = [[100, 50], [90, 50], [80, 50]]  # Reset snake position
        self.snake_direction = 'RIGHT'  # Reset direction
        self.food_pos = [random.randrange(1, (self.screen.get_width() // 10)) * 10,
                         random.randrange(1, (self.screen.get_height() // 10)) * 10]  # Reset food position
        self.score = 0
        self.start_time = pygame.time.get_ticks()  # Reset timer
        self.running = True

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            # Reset the start time to account for the time spent paused
            self.start_time += (pygame.time.get_ticks() - self.pause_start_time)
        else:
            self.paused = True
            self.pause_start_time = pygame.time.get_ticks()  # Record the time when paused