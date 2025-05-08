import pygame
from games.pacman import PacmanGame
from games.space_invaders import SpaceInvaders
from games.snake import Snake
from games.tetris import Tetris
from games.flappy_bird import FlappyBird

class MainMenu:
    def __init__(self, screen, screen_size=(800, 800)):
        self.screen = screen
        self.set_screen_size(screen_size)  # Set the screen size
        self.running = True
        self.hovered_image = None  # Track which image is hovered
        self.volume = 0.5  # Default volume level
        self.music_playing = True  # Track if music is playing
        self.load_assets()
        self.load_music()
        self.music_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_on.png'), (50, 50))  # Load and scale music on icon
        self.music_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_off.png'), (50, 50))  # Load and scale music off icon
        self.background_image = pygame.image.load('assets/pokemon/gastly2.png')
        self.background_rect = self.background_image.get_rect(center=(self.screen_size[0] // 2, self.screen_size[1] // 2))
        
        # Adjusted positions based on screen size
        self.update_positions()

    def set_screen_size(self, screen_size):
        self.screen_size = screen_size  # Set the screen size
        self.image_size = (self.screen_size[0] // 6, self.screen_size[1] // 6)  # Responsive image size
        self.update_positions()  # Update button positions based on new screen size

    def update_positions(self):
        # Adjusted positions based on screen size for better alignment
        button_spacing = self.screen_size[1] // 8  # Adjusted spacing for fewer items
        button_x_left = self.screen_size[0] // 5 
        button_x_right = self.screen_size[0] // 1.5 
        
        self.positions = {
            "space_invaders": (button_x_left, button_spacing * 2),
            "snake": (button_x_left, button_spacing * 4),
            "tetris": (button_x_left, button_spacing * 6),
            "pacman": (button_x_right, button_spacing * 2),
            "flappy_bird": (button_x_right, button_spacing * 4),
        }

    def load_assets(self):
        self.images = {
            "space_invaders": pygame.image.load('assets/space_invaders/space_invaders2.png'),
            "snake": pygame.image.load('assets/snake/slytherin.gif'),
            "tetris": pygame.image.load('assets/tetris/tetris.png'),
            "pacman": pygame.image.load('assets/pacman/pacman.png'),
            "flappy_bird": pygame.image.load('assets/flappy_bird/bird.png'),
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
            # Handle events first to catch resize events
            self.handle_events()
            
            # Clear and redraw the screen
            self.screen.fill((0, 0, 0))  # Fill the screen with black
            
            # Scale background image to match current screen size
            scaled_background = pygame.transform.scale(self.background_image, self.screen_size)
            self.background_rect = scaled_background.get_rect(center=(self.screen_size[0] // 2, self.screen_size[1] // 2))
            self.screen.blit(scaled_background, self.background_rect)
            
            # Create a transparent overlay scaled to the current screen size
            transparent_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            transparent_surface.fill((255, 255, 255, 128))  # Fill with white and 50% transparency
            self.screen.blit(transparent_surface, (0, 0))
            
            self.draw_menu()

    def draw_menu(self):
        # Draw images with hover effect
        for key, pos in self.positions.items():
            if self.hovered_image == key:
                highlighted_image = pygame.transform.scale(self.images[key], (self.image_size[0] + 20, self.image_size[1] + 20))
                self.screen.blit(highlighted_image, (pos[0] - 10, pos[1] - 10))
            else:
                # Scale images to current screen size
                scaled_image = pygame.transform.scale(self.images[key], self.image_size)
                self.screen.blit(scaled_image, pos)

        # Draw game titles under icons
        font_size = max(24, self.screen_size[0] // 22)
        font = pygame.font.Font(None, font_size)
        
        # Draw mute/unmute music button in a responsive position
        music_icon = self.music_icon_on if self.music_playing else self.music_icon_off
        icon_size = music_icon.get_width()
        self.screen.blit(music_icon, (self.screen_size[0] - icon_size - 10, 10))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Update screen and recalculate all size-dependent variables
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.set_screen_size((event.w, event.h))
                # Re-scale music icons to fit new screen size
                icon_size = min(50, self.screen_size[0] // 16)
                self.music_icon_on = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_on.png'), (icon_size, icon_size))
                self.music_icon_off = pygame.transform.scale(pygame.image.load('assets/sound_effects/music_off.png'), (icon_size, icon_size))
            elif event.type == pygame.MOUSEMOTION:
                self.check_hover(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.check_click(event.pos)

    def check_hover(self, mouse_pos):
        # Reset hovered image
        self.hovered_image = None
        
        # Check if mouse is hovering over any game icon
        for key, pos in self.positions.items():
            if pos[0] <= mouse_pos[0] <= pos[0] + self.image_size[0] and pos[1] <= mouse_pos[1] <= pos[1] + self.image_size[1]:
                self.hovered_image = key
                break

        # Check if hovering over music icon (responsive position)
        icon_size = self.music_icon_on.get_width()
        if (self.screen_size[0] - icon_size - 10 <= mouse_pos[0] <= self.screen_size[0] - 10 and 
            10 <= mouse_pos[1] <= 10 + icon_size):
            self.hovered_image = "music"

    def check_click(self, mouse_pos):
        # Check for game icon clicks
        for key, pos in self.positions.items():
            if pos[0] <= mouse_pos[0] <= pos[0] + self.image_size[0] and pos[1] <= mouse_pos[1] <= pos[1] + self.image_size[1]:
                game_map = {
                    "space_invaders": SpaceInvaders,
                    "snake": Snake,
                    "tetris": Tetris,
                    "pacman": PacmanGame,
                    "flappy_bird": FlappyBird,
                }
                if key in game_map: # Check if the key is still in our active games
                    self.start_game(game_map[key])
                break

        # Check music icon click (responsive position)
        icon_size = self.music_icon_on.get_width()
        if (self.screen_size[0] - icon_size - 10 <= mouse_pos[0] <= self.screen_size[0] - 10 and 
            10 <= mouse_pos[1] <= 10 + icon_size):
            self.toggle_music()

    def check_volume_slider(self, mouse_pos):
        # Responsive slider position and dimensions
        slider_y = self.screen_size[1] - 50
        slider_width = self.screen_size[0] - 100
        
        if 50 <= mouse_pos[0] <= 50 + slider_width and slider_y <= mouse_pos[1] <= slider_y + 20:
            self.volume = (mouse_pos[0] - 50) / slider_width
            pygame.mixer.music.set_volume(self.volume)

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