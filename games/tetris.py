import pygame
import random
import time
import os
from util.high_score_manager import load_high_scores, update_high_score
from util.pause_screen_manager import show_pause_screen
from util.game_over_screen_manager import show_game_over_screen

# Grid settings
GRID_WIDTH = 15
GRID_HEIGHT = 20
# BLOCK_SIZE will be computed dynamically based on window height in Tetris class

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = {
    'I': (0, 240, 240),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
    'O': (240, 240, 0),
    'S': (0, 240, 0),
    'T': (160, 0, 240),
    'Z': (240, 0, 0)
}

# Tetromino shapes in 4 rotations (each shape is a list of 4x4 grid strings)
SHAPES = {
    'I': [
        ["....",
         "####",
         "....",
         "...."],
        ["..#.",
         "..#.",
         "..#.",
         "..#."]
    ],
    'J': [
        [".#..",
         ".#..",
         "##..",
         "...."],
        ["....",
         "#...",
         "###.",
         "...."],
        ["..##",
         "..#.",
         "..#.",
         "...."],
        ["....",
         "###.",
         "..#.",
         "...."]
    ],
    'L': [
        ["..#.",
         "..#.",
         "..##",
         "...."],
        ["....",
         "###.",
         "#...",
         "...."],
        ["##..",
         ".#..",
         ".#..",
         "...."],
        ["....",
         "..#.",
         "###.",
         "...."]
    ],
    'O': [
        ["....",
         ".##.",
         ".##.",
         "...."]
    ],
    'S': [
        ["....",
         ".##.",
         "##..",
         "...."],
        ["#...",
         "##..",
         ".#..",
         "...."]
    ],
    'T': [
        ["....",
         "###.",
         ".#..",
         "...."],
        [".#..",
         "##..",
         ".#..",
         "...."],
        [".#..",
         "###.",
         "....",
         "...."],
        [".#..",
         ".##.",
         ".#..",
         "...."]
    ],
    'Z': [
        ["....",
         "##..",
         ".##.",
         "...."],
        [".#..",
         "##..",
         "#...",
         "...."]
    ]
}

class Tetris:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.calculate_dimensions()
        self.running = True
        self.clock = pygame.time.Clock()
        self.fall_time = 0
        self.fall_speed = 0.25
        self.score = 0
        self.level = 1
        self.high_scores = load_high_scores()
        self.high_score = self.high_scores.get('tetris', 0)
        self.grid = self.create_grid()
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.last_update_time = time.time()
        self.paused = False
        # Load background image and scale it
        try:
            self.background_image = pygame.image.load('assets/tetris/tetris.png')
            self.background_image = pygame.transform.scale(self.background_image, 
                                                         (self.play_width, self.play_height))
        except:
            self.background_image = None
            
        # Load sound effects
        try:
            self.clear_sound = pygame.mixer.Sound('assets/tetris/clear.wav')
            self.rotate_sound = pygame.mixer.Sound('assets/tetris/rotate.wav')
            self.drop_sound = pygame.mixer.Sound('assets/tetris/drop.wav')
        except:
            self.clear_sound = None
            self.rotate_sound = None
            self.drop_sound = None
            
        # Sound settings
        self.sound_effects_enabled = True
        # Load and scale icons
        icon_size = min(24, self.screen_width // 32)
        try:
            self.sound_on_icon = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_on_white.png'), 
                                                      (icon_size, icon_size))
            self.sound_off_icon = pygame.transform.scale(pygame.image.load('assets/sound_effects/sound_off_white.png'), 
                                                       (icon_size, icon_size))
        except:
            self.sound_on_icon = None
            self.sound_off_icon = None

    def calculate_dimensions(self):
        """Calculate responsive dimensions for the game area"""
        # Calculate the block size based on screen height and width
        # Use the smaller dimension to ensure it fits
        height_based = self.screen_height // GRID_HEIGHT
        width_based = (self.screen_width * 0.7) // GRID_WIDTH  # Use 70% of width for play area
        self.block_size = min(height_based, width_based)
        
        # Calculate play area dimensions
        self.play_width = GRID_WIDTH * self.block_size
        self.play_height = GRID_HEIGHT * self.block_size
        
        # Calculate the top-left position to center the play area
        self.top_left_x = (self.screen_width - self.play_width) // 2
        self.top_left_y = (self.screen_height - self.play_height) // 2
        
        # Calculate font sizes based on screen dimensions
        self.title_font_size = max(24, min(self.screen_width, self.screen_height) // 20)
        self.info_font_size = max(16, min(self.screen_width, self.screen_height) // 30)

    def create_grid(self):
        # Create a grid with empty cells represented as BLACK
        return [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def get_new_piece(self):
        shape = random.choice(list(SHAPES.keys()))
        rotations = SHAPES[shape]
        rotation = 0
        # Position starts near the top middle of grid
        x = GRID_WIDTH // 2 - 2
        y = 0
        return {'shape': shape, 'rotation': rotation, 'x': x, 'y': y}

    def convert_shape_format(self, piece):
        positions = []
        format = SHAPES[piece['shape']][piece['rotation'] % len(SHAPES[piece['shape']])]
        for i, line in enumerate(format):
            for j, char in enumerate(line):
                if char == "#":
                    positions.append((piece['x'] + j, piece['y'] + i))
        return positions

    def valid_space(self, piece):
        accepted_positions = [[(j, i) for j in range(GRID_WIDTH) if self.grid[i][j] == BLACK] for i in range(GRID_HEIGHT)]
        accepted_positions = [j for sub in accepted_positions for j in sub]
        formatted = self.convert_shape_format(piece)
        for pos in formatted:
            if pos not in accepted_positions:
                if pos[1] >= 0:
                    return False
        return True

    def lock_piece(self, piece):
        formatted = self.convert_shape_format(piece)
        color = COLORS[piece['shape']]
        for pos in formatted:
            x, y = pos
            if y >= 0:
                self.grid[y][x] = color
        self.clear_rows()
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        if not self.valid_space(self.current_piece):
            self.game_over()

    def clear_rows(self):
        # Check each row if it's filled
        rows_cleared = 0
        for i in range(len(self.grid)-1, -1, -1):
            if BLACK not in self.grid[i]:
                del self.grid[i]
                self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
                rows_cleared += 1
        if rows_cleared > 0:
            self.score += rows_cleared * 100
            if self.sound_effects_enabled and self.clear_sound:
                self.clear_sound.play()
            # Increase level every 500 points
            if self.score >= self.level * 500 and self.level < 10:
                self.level += 1
                self.fall_speed = max(0.1, self.fall_speed - 0.05)

    def game_over(self):
        self.high_score = update_high_score('tetris', self.score)
        action = show_game_over_screen(self.screen, self.score, self.high_score, self.level)
        if action == 'restart':
            self.reset_game()
        else:
            self.running = False

    def reset_game(self):
        # Recalculate dimensions in case window was resized
        self.calculate_dimensions()
        self.grid = self.create_grid()
        self.score = 0
        self.level = 1
        self.fall_speed = 0.25
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.last_update_time = time.time()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.screen_width = self.screen.get_width()
                self.screen_height = self.screen.get_height()
                self.calculate_dimensions()
                if self.background_image:
                    self.background_image = pygame.transform.scale(
                        pygame.image.load('assets/tetris/tetris.png'), 
                        (self.play_width, self.play_height)
                    )
                # Resize sound icons
                icon_size = min(24, self.screen_width // 32)
                if self.sound_on_icon and self.sound_off_icon:
                    self.sound_on_icon = pygame.transform.scale(
                        pygame.image.load('assets/sound_effects/sound_on_white.png'), 
                        (icon_size, icon_size)
                    )
                    self.sound_off_icon = pygame.transform.scale(
                        pygame.image.load('assets/sound_effects/sound_off_white.png'), 
                        (icon_size, icon_size)
                    )
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if self.paused:
                        self.last_update_time = time.time() - self.fall_time
                    self.paused = not self.paused
                if not self.paused:
                    if event.key == pygame.K_LEFT:
                        self.current_piece['x'] -= 1
                        if not self.valid_space(self.current_piece):
                            self.current_piece['x'] += 1
                    elif event.key == pygame.K_RIGHT:
                        self.current_piece['x'] += 1
                        if not self.valid_space(self.current_piece):
                            self.current_piece['x'] -= 1
                    elif event.key == pygame.K_DOWN:
                        self.current_piece['y'] += 1
                        if not self.valid_space(self.current_piece):
                            self.current_piece['y'] -= 1
                    elif event.key == pygame.K_UP:
                        old_rotation = self.current_piece['rotation']
                        self.current_piece['rotation'] = (self.current_piece['rotation'] + 1) % len(SHAPES[self.current_piece['shape']])
                        if not self.valid_space(self.current_piece):
                            self.current_piece['rotation'] = old_rotation
                        elif self.sound_effects_enabled and self.rotate_sound:
                            self.rotate_sound.play()
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while self.valid_space(self.current_piece):
                            self.current_piece['y'] += 1
                        self.current_piece['y'] -= 1
                        self.lock_piece(self.current_piece)
                        if self.sound_effects_enabled and self.drop_sound:
                            self.drop_sound.play()
                    elif event.key == pygame.K_s:
                        # Toggle sound effects
                        self.sound_effects_enabled = not self.sound_effects_enabled
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if sound toggle button was clicked
                    if self.sound_on_icon and self.sound_off_icon:
                        sound_icon_rect = pygame.Rect(
                            self.screen_width - self.sound_on_icon.get_width() - 10, 
                            10, 
                            self.sound_on_icon.get_width(), 
                            self.sound_on_icon.get_height()
                        )
                        if sound_icon_rect.collidepoint(event.pos):
                            self.sound_effects_enabled = not self.sound_effects_enabled

    def update(self):
        if self.paused:
            show_pause_screen(self.screen)
            return
        current_time = time.time()
        self.fall_time = current_time - self.last_update_time
        if self.fall_time > self.fall_speed:
            self.current_piece['y'] += 1
            if not self.valid_space(self.current_piece):
                self.current_piece['y'] -= 1
                self.lock_piece(self.current_piece)
            self.last_update_time = current_time

    def draw_grid(self):
        # Draw grid cells
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                pygame.draw.rect(
                    self.screen, 
                    self.grid[i][j],
                    (self.top_left_x + j * self.block_size, 
                     self.top_left_y + i * self.block_size, 
                     self.block_size, 
                     self.block_size), 
                    0
                )
                pygame.draw.rect(
                    self.screen, 
                    GRAY,
                    (self.top_left_x + j * self.block_size, 
                     self.top_left_y + i * self.block_size, 
                     self.block_size, 
                     self.block_size), 
                    1
                )

    def draw_piece(self, piece):
        formatted = self.convert_shape_format(piece)
        color = COLORS[piece['shape']]
        for pos in formatted:
            x, y = pos
            if y >= 0:
                pygame.draw.rect(
                    self.screen, 
                    color,
                    (self.top_left_x + x * self.block_size, 
                     self.top_left_y + y * self.block_size, 
                     self.block_size, 
                     self.block_size), 
                    0
                )
                pygame.draw.rect(
                    self.screen, 
                    GRAY,
                    (self.top_left_x + x * self.block_size, 
                     self.top_left_y + y * self.block_size, 
                     self.block_size, 
                     self.block_size), 
                    1
                )

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw game area background
        if self.background_image:
            self.screen.blit(self.background_image, (self.top_left_x, self.top_left_y))
        else:
            pygame.draw.rect(
                self.screen, 
                (40, 40, 40),
                (self.top_left_x, self.top_left_y, self.play_width, self.play_height)
            )
            
        # Draw game border
        pygame.draw.rect(
            self.screen, 
            WHITE,
            (self.top_left_x, self.top_left_y, self.play_width, self.play_height),
            2
        )
        
        # Draw the grid and pieces
        self.draw_grid()
        self.draw_piece(self.current_piece)
        
        # Calculate sidebar position - right side of play area
        sidebar_x = self.top_left_x + self.play_width + 10
        
        # Use responsive font sizes
        title_font = pygame.font.Font(None, self.title_font_size)
        info_font = pygame.font.Font(None, self.info_font_size)
        
        # Draw game title
        title = title_font.render("TETRIS", True, WHITE)
        self.screen.blit(title, (self.top_left_x + self.play_width // 2 - title.get_width() // 2, 
                                self.top_left_y - title.get_height() - 10))
        
        # Draw next piece preview
        next_label = info_font.render("Next:", True, WHITE)
        self.screen.blit(next_label, (sidebar_x, self.top_left_y + 20))
        
        # Draw next piece
        formatted = self.convert_shape_format(self.next_piece)
        preview_block = max(self.block_size // 2, 8)  # Ensure visible size with min of 8px
        preview_offset_x = sidebar_x + 10
        preview_offset_y = self.top_left_y + 50
        
        for pos in formatted:
            x, y = pos
            pygame.draw.rect(
                self.screen, 
                COLORS[self.next_piece['shape']],
                (preview_offset_x + (x - self.next_piece['x']) * preview_block,
                 preview_offset_y + (y - self.next_piece['y']) * preview_block, 
                 preview_block, 
                 preview_block), 
                0
            )
            pygame.draw.rect(
                self.screen, 
                GRAY,
                (preview_offset_x + (x - self.next_piece['x']) * preview_block,
                 preview_offset_y + (y - self.next_piece['y']) * preview_block, 
                 preview_block, 
                 preview_block), 
                1
            )
        
        # Display score and level
        score_label = info_font.render(f"Score: {self.score}", True, WHITE)
        level_label = info_font.render(f"Level: {self.level}", True, WHITE)
        high_score_label = info_font.render(f"High Score: {self.high_score}", True, WHITE)
        
        score_y = preview_offset_y + 100
        self.screen.blit(score_label, (sidebar_x, score_y))
        self.screen.blit(level_label, (sidebar_x, score_y + self.info_font_size + 5))
        self.screen.blit(high_score_label, (sidebar_x, score_y + (self.info_font_size + 5) * 2))
        
        # Draw controls help
        controls_y = score_y + (self.info_font_size + 5) * 4
        controls = [
            "Controls:",
            "← → : Move",
            "↑    : Rotate",
            "↓    : Soft Drop",
            "SPACE: Hard Drop",
            "P    : Pause",
            "S    : Sound"
        ]
        
        for i, text in enumerate(controls):
            control_label = info_font.render(text, True, WHITE)
            self.screen.blit(control_label, 
                            (sidebar_x, controls_y + i * (self.info_font_size + 2)))
        
        # Draw sound toggle icon
        if self.sound_on_icon and self.sound_off_icon:
            sound_icon = self.sound_on_icon if self.sound_effects_enabled else self.sound_off_icon
            self.screen.blit(sound_icon, 
                            (self.screen_width - sound_icon.get_width() - 10, 10))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    # Set fixed window size 800x800
    win_width = 800
    win_height = 800
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("Tetris")
    game = Tetris(screen)
    game.run()
    pygame.quit()

if __name__ == '__main__':
    main()
