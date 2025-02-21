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
        self.image_size = (150, 150)  # Set desired image size (width, height)

    def run(self):
        while self.running:
            self.screen.fill((255, 255, 255))  # Clear screen
            self.draw_menu()
            self.handle_events()

    def draw_menu(self):
        # Draw game images and exit button
        space_invaders_image = pygame.image.load('assets/space_invaders/space_invaders_background.png')
        snake_image = pygame.image.load('assets/joker.jpeg')
        tetris_image = pygame.image.load('assets/homelander.jpeg')
        tank_image = pygame.image.load('assets/darth_vader.png')
        contra_image = pygame.image.load('assets/hetfield.jpg')
        pokemon_image = pygame.image.load('assets/gengar.jpg')

        # Resize images
        space_invaders_image = pygame.transform.scale(space_invaders_image, self.image_size)
        snake_image = pygame.transform.scale(snake_image, self.image_size)
        tetris_image = pygame.transform.scale(tetris_image, self.image_size)
        tank_image = pygame.transform.scale(tank_image, self.image_size)
        contra_image = pygame.transform.scale(contra_image, self.image_size)
        pokemon_image = pygame.transform.scale(pokemon_image, self.image_size)

        # Blit images onto the screen
        self.screen.blit(space_invaders_image, (100, 50))
        self.screen.blit(snake_image, (100, 220))
        self.screen.blit(tetris_image, (100, 390))
        self.screen.blit(tank_image, (400, 390))
        self.screen.blit(contra_image, (400, 50))
        self.screen.blit(pokemon_image, (400, 220))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if 100 <= pos[0] <= 250:
                    if 50 <= pos[1] <= 200:
                        self.start_game(SpaceInvaders)
                    elif 220 <= pos[1] <= 370:
                        self.start_game(Snake)
                    elif 390 <= pos[1] <= 540:
                        self.start_game(Tetris)
                elif 400 <= pos[0] <= 550:
                    if 50 <= pos[1] <= 200:
                        self.start_game(Contra)
                    elif 220 <= pos[1] <= 370:
                        self.start_game(Pokemon)
                    elif 390 <= pos[1] <= 540:
                        self.start_game(Tank)

                       
    def start_game(self, game_class):
        game_instance = game_class(self.screen)
        game_instance.run()
