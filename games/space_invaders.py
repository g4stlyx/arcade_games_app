import pygame
import random
import time

class SpaceInvaders:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.player_image = pygame.image.load('assets/space_invaders/player.gif')
        self.invader_images = [
            pygame.image.load('assets/space_invaders/invader.gif'),
            pygame.image.load('assets/space_invaders/alien2.png'),
            pygame.image.load('assets/space_invaders/alien3.png'),
            pygame.image.load('assets/space_invaders/alien4.png')
        ]
        self.bullet_image = pygame.image.load('assets/space_invaders/blasterbolt.png')
        self.background_image = pygame.image.load('assets/space_invaders/space2.jpg')
        self.laser_sound = pygame.mixer.Sound('assets/space_invaders/laser.wav')
        self.explosion_sound = pygame.mixer.Sound('assets/space_invaders/explosion.wav')

        self.player_pos = [375, 650]
        self.invaders = [[random.randint(0, 750), random.randint(100, 150), random.choice(self.invader_images)] for _ in range(5)]  # Random invader positions with random images
        self.lasers = []  # List to hold lasers
        self.score = 0
        self.high_score = 0  # Track highest score
        self.invader_direction = 1  # 1 for right, -1 for left
        self.invader_speed = 2  # Speed of invaders
        self.bullet_ready = True  # Bullet shooting logic
        self.game_over_threshold = 50  # Threshold for game over condition
        self.level = 1  # Current level
        self.max_level = 5  # Maximum level
        self.start_time = time.time()  # Start time for the timer

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # Limit to 60 frames per second

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player_pos[0] > 0:
            self.player_pos[0] -= 5
        if keys[pygame.K_RIGHT] and self.player_pos[0] < 750:
            self.player_pos[0] += 5
        if keys[pygame.K_SPACE] and self.bullet_ready:
            self.shoot_bullet()

    def shoot_bullet(self):
        bullet_pos = [self.player_pos[0] + (self.player_image.get_width() // 2) - (self.bullet_image.get_width() // 2), self.player_pos[1] - 10]  # Center bullet above player
        self.lasers.append(bullet_pos)
        self.laser_sound.play()
        self.bullet_ready = False  # Set bullet to not ready until it is fired

    def update(self):
        # Move bullets
        for bullet in self.lasers:
            bullet[1] -= 10
            if bullet[1] < 0:  # Bullet goes off screen
                self.lasers.remove(bullet)
                self.bullet_ready = True

        # Move invaders
        for invader in self.invaders:
            invader[0] += self.invader_direction * self.invader_speed

        # Check for invader boundaries
        if any(invader[0] <= 0 for invader in self.invaders) or any(invader[0] >= 750 for invader in self.invaders):
            self.invader_direction *= -1  # Change direction
            for invader in self.invaders:
                invader[1] += 10  # Move down

        # Check for collisions
        for bullet in self.lasers:
            for invader in self.invaders:
                if (invader[0] < bullet[0] < invader[0] + 50) and (invader[1] < bullet[1] < invader[1] + 50):
                    self.invaders.remove(invader)
                    self.lasers.remove(bullet)
                    self.score += 1
                    self.explosion_sound.play()
                    self.bullet_ready = True
                    # Respawn the invader immediately
                    self.invaders.append([random.randint(0, 750), random.randint(100, 150), random.choice(self.invader_images)])
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
                self.invader_speed += 1  # Increase invader speed
                self.invaders.append([random.randint(0, 750), random.randint(100, 150), random.choice(self.invader_images)])  # Add an extra invader with random image
                print(f"Level Up! Current Level: {self.level}")

    def game_over(self):
        if self.score > self.high_score:
            self.high_score = self.score  # Update high score if current score is higher
        self.show_game_over_screen()

    def show_game_over_screen(self):
        while True:
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 74)
            game_over_text = font.render("Game Over", True, (255, 0, 0))
            self.screen.blit(game_over_text, (250, 100))

            # Display scores and level
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Your Score: {self.score}', True, (255, 255, 255))
            high_score_text = font.render(f'High Score: {self.high_score}', True, (255, 255, 255))
            level_text = font.render(f'Level: {self.level}', True, (255, 255, 255))
            self.screen.blit(score_text, (300, 200))
            self.screen.blit(high_score_text, (300, 250))
            self.screen.blit(level_text, (300, 300))

            # Display options
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            menu_text = font.render("Press M to Return to Menu", True, (255, 255, 255))
            exit_text = font.render("Press Q to Quit", True, (255, 255, 255))
            self.screen.blit(restart_text, (300, 350))
            self.screen.blit(menu_text, (300, 400))
            self.screen.blit(exit_text, (300, 450))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart the game
                        self.reset_game()
                        return
                    elif event.key == pygame.K_m:  # Return to menu
                        self.running = False
                        return
                    elif event.key == pygame.K_q:  # Quit the game
                        pygame.quit()
                        return

    def reset_game(self):
        self.player_pos = [375, 650]
        self.invaders = [[random.randint(0, 750), random.randint(100, 150), random.choice(self.invader_images)] for _ in range(5)] 
        self.lasers = [] 
        self.score = 0
        self.bullet_ready = True
        self.invader_direction = 1
        self.invader_speed = 2
        self.level = 1
        self.start_time = time.time()
        self.running = True  #* reset everything and restart the game loop

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
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (28, 237, 28))
        level_text = font.render(f'Level: {self.level}', True, (28, 237, 28))
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        timer_text = font.render(f'Time: {minutes:02}:{seconds:02}', True, (28, 237, 28))

        # score, level, timer info
        margin = 20
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10 + score_text.get_width() + margin, 10))
        self.screen.blit(timer_text, (10 + score_text.get_width() + level_text.get_width() + 2 * margin, 10))

        pygame.display.flip()