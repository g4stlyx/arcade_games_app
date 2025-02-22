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
        self.image_size = (200, 200)  # Set desired image size (width, height)
        self.hovered_image = None  # Track which image is hovered
        self.volume = 0.5  # Default volume level
        self.music_playing = True  # Track if music is playing
        self.load_assets()
        self.load_music()
        self.music_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_on.png'), (50, 50))  # Load and scale music on icon
        self.music_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_off.png'), (50, 50))  # Load and scale music off icon

    def load_assets(self):
        # Load images
        self.images = {
            "space_invaders": pygame.image.load('assets/space_invaders/space_invaders.png'),
            "snake": pygame.image.load('assets/snake/snake.jpg'),
            "tetris": pygame.image.load('assets/tetris/tetris.jpg'),
            "tank": pygame.image.load('assets/tank/tank.jpg'),
            "contra": pygame.image.load('assets/contra/contra.jpg'),
            "pokemon": pygame.image.load('assets/pokemon/gastly_evolution.jpeg'),
            "music_on": pygame.image.load('assets/sound_effects/music_on.png'),
            "music_off": pygame.image.load('assets/sound_effects/music_off.png'),
        }
        # Resize images
        for key in self.images:
            self.images[key] = pygame.transform.scale(self.images[key], self.image_size)

    def load_music(self):
        pygame.mixer.music.load('assets\sound_effects\menu\9. Space Debris.wav')  # Load background music
        pygame.mixer.music.set_volume(self.volume)  # Set initial volume
        pygame.mixer.music.play(-1)  # Play music in a loop

    def run(self):
        while self.running:
            self.screen.fill((255, 255, 255))
            self.draw_menu()
            self.handle_events()

    def draw_menu(self):
        # Draw images with hover effect
        positions = {
            "space_invaders": (100, 50),
            "snake": (100, 270),
            "tetris": (100, 490),
            "contra": (500, 50),
            "pokemon": (500, 270),
            "tank": (500, 490)
        }

        for key, pos in positions.items():
            if self.hovered_image == key:
                # Draw a highlighted version of the image (e.g., slightly larger or with a border)
                highlighted_image = pygame.transform.scale(self.images[key], (self.image_size[0] + 10, self.image_size[1] + 10))
                self.screen.blit(highlighted_image, (pos[0] - 5, pos[1] - 5))  # Draw with offset
            else:
                self.screen.blit(self.images[key], pos)

        # Draw volume slider label
        font = pygame.font.Font(None, 36)  # Create a font object
        text_surface = font.render("Volume Slider", True, (0, 0, 0))  # Render the text
        self.screen.blit(text_surface, (50, 720))  # Position the text above the slider

        # Draw volume slider
        pygame.draw.rect(self.screen, (200, 200, 200), (50, 750, 700, 20))  # Slider background
        pygame.draw.rect(self.screen, (0, 255, 0), (50, 750, 700 * self.volume, 20))  # Slider fill
        pygame.draw.rect(self.screen, (0, 0, 0), (50 + 700 * self.volume - 5, 745, 10, 30))  # Slider knob

        # Draw mute/unmute music button
        music_icon = self.music_icon_on if self.music_playing else self.music_icon_off
        self.screen.blit(music_icon, (750, 15))  # Draw music icon

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.check_hover(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.check_click(event.pos)
                    self.check_volume_slider(event.pos)

    def check_hover(self, mouse_pos):
        # Check if mouse is hovering over any image
        positions = {
            "space_invaders": (100, 50),
            "snake": (100, 270),
            "tetris": (100, 490),
            "contra": (500, 50),
            "pokemon": (500, 270),
            "tank": (500, 490)
        }
        self.hovered_image = None  # Reset hovered image
        for key, pos in positions.items():
            if pos[0] <= mouse_pos[0] <= pos[0] + self.image_size[0] and pos[1] <= mouse_pos[1] <= pos[1] + self.image_size[1]:
                self.hovered_image = key
                break

        # Check if hovering over sound effects button
        if 750 <= mouse_pos[0] <= 800 and 60 <= mouse_pos[1] <= 110:
            self.hovered_image = "sound_effects"

    def check_click(self, mouse_pos):
        positions = {
            "space_invaders": (100, 50),
            "snake": (100, 270),
            "tetris": (100, 490),
            "contra": (500, 50),
            "pokemon": (500, 270),
            "tank": (500, 490)
        }
        for key, pos in positions.items():
            if pos[0] <= mouse_pos[0] <= pos[0] + self.image_size[0] and pos[1] <= mouse_pos[1] <= pos[1] + self.image_size[1]:
                self.start_game({
                    "space_invaders": SpaceInvaders,
                    "snake": Snake,
                    "tetris": Tetris,
                    "contra": Contra,
                    "pokemon": Pokemon,
                    "tank": Tank
                }[key])
                break

        # Check if stop music button is clicked
        if 750 <= mouse_pos[0] <= 800 and 10 <= mouse_pos[1] <= 60:
            self.toggle_music()

    def check_volume_slider(self, mouse_pos):
        if 50 <= mouse_pos[0] <= 750 and 750 <= mouse_pos[1] <= 770:
            # Calculate volume based on slider position
            self.volume = (mouse_pos[0] - 50) / 700
            pygame.mixer.music.set_volume(self.volume)  # Set the new volume

    def toggle_music(self):
        if self.music_playing:
            pygame.mixer.music.pause()  # Pause music
            self.music_playing = False
        else:
            pygame.mixer.music.unpause()  # Unpause music
            self.music_playing = True

    def start_game(self, game_class):
        pygame.mixer.music.stop()
        game_instance = game_class(self.screen)
        game_instance.run()
        pygame.mixer.music.play(-1)  # Restart music after returning to menu
