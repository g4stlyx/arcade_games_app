import pygame
from games.space_invaders import SpaceInvaders
from games.snake import Snake
from games.tetris import Tetris
from games.tank import Tank
from games.contra import Contra
from games.pokemon import Pokemon

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.image_size = (200, 200)  # images (works like buttons) sizes

    def run(self):
        while self.running:
            self.screen.fill((60, 70, 80))
            self.draw_menu()
            self.handle_events()

    def draw_menu(self):
        # Draw game images and exit button
        space_invaders_image = pygame.image.load('assets/space_invaders/space_invaders.png')
        snake_image = pygame.image.load('assets/snake/snake.jpg')
        tetris_image = pygame.image.load('assets/tetris/tetris.jpg')
        tank_image = pygame.image.load('assets/tank/tank.jpg')
        contra_image = pygame.image.load('assets/contra/contra.jpg')
        pokemon_image = pygame.image.load('assets/pokemon/gastly_evolution.jpeg')

        # Resize images
        space_invaders_image = pygame.transform.scale(space_invaders_image, self.image_size)
        snake_image = pygame.transform.scale(snake_image, self.image_size)
        tetris_image = pygame.transform.scale(tetris_image, self.image_size)
        tank_image = pygame.transform.scale(tank_image, self.image_size)
        contra_image = pygame.transform.scale(contra_image, self.image_size)
        pokemon_image = pygame.transform.scale(pokemon_image, self.image_size)

        # Blit images onto the screen
        self.screen.blit(space_invaders_image, (100, 50))
        self.screen.blit(snake_image, (100, 270))
        self.screen.blit(tetris_image, (100, 490))
        self.screen.blit(contra_image, (500, 50))
        self.screen.blit(pokemon_image, (500, 270))
        self.screen.blit(tank_image, (500, 490))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if 100 <= pos[0] <= 300:
                    if 50 <= pos[1] <= 250:
                        self.start_game(SpaceInvaders)
                    elif 270 <= pos[1] <= 470:
                        self.start_game(Snake)
                    elif 490 <= pos[1] <= 690:
                        self.start_game(Tetris)
                elif 500 <= pos[0] <= 700:
                    if 50 <= pos[1] <= 250:
                        self.start_game(Contra)
                    elif 270 <= pos[1] <= 470:
                        self.start_game(Pokemon)
                    elif 490 <= pos[1] <= 690:
                        self.start_game(Tank)

    def start_game(self, game_class):
        game_instance = game_class(self.screen)
        game_instance.run()
