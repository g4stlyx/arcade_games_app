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
        self.block_size = self.screen.get_height() // GRID_HEIGHT
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
        # Optionally load a background image from assets if exists
        try:
            self.background_image = pygame.image.load('assets/tetris/tetris.png')
            self.background_image = pygame.transform.scale(self.background_image, (GRID_WIDTH * self.block_size, GRID_HEIGHT * self.block_size))
        except:
            self.background_image = None

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
        self.grid = self.create_grid()
        self.score = 0
        self.level = 1
        self.fall_speed = 0.3
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.last_update_time = time.time()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
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
                        self.current_piece['rotation'] = (self.current_piece['rotation'] + 1) % len(SHAPES[self.current_piece['shape']])
                        if not self.valid_space(self.current_piece):
                            self.current_piece['rotation'] = (self.current_piece['rotation'] - 1) % len(SHAPES[self.current_piece['shape']])
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while self.valid_space(self.current_piece):
                            self.current_piece['y'] += 1
                        self.current_piece['y'] -= 1
                        self.lock_piece(self.current_piece)

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
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, self.grid[i][j],
                                 (j * self.block_size, i * self.block_size, self.block_size, self.block_size), 0)
                pygame.draw.rect(self.screen, GRAY,
                                 (j * self.block_size, i * self.block_size, self.block_size, self.block_size), 1)

    def draw_piece(self, piece):
        formatted = self.convert_shape_format(piece)
        color = COLORS[piece['shape']]
        for pos in formatted:
            x, y = pos
            if y >= 0:
                pygame.draw.rect(self.screen, color,
                                 (x * self.block_size, y * self.block_size, self.block_size, self.block_size), 0)
                pygame.draw.rect(self.screen, GRAY,
                                 (x * self.block_size, y * self.block_size, self.block_size, self.block_size), 1)

    def draw(self):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_piece(self.current_piece)
        # Draw next piece preview
        font = pygame.font.Font(None, 24)
        label = font.render("Next:", True, WHITE)
        self.screen.blit(label, (GRID_WIDTH * self.block_size + 20, 30))
        formatted = self.convert_shape_format(self.next_piece)
        for pos in formatted:
            x, y = pos
            preview_block = self.block_size // 2
            pygame.draw.rect(self.screen, COLORS[self.next_piece['shape']],
                             ((GRID_WIDTH * self.block_size + 20) + (x - self.next_piece['x']) * preview_block,
                              50 + (y - self.next_piece['y']) * preview_block, preview_block, preview_block), 0)
            pygame.draw.rect(self.screen, GRAY,
                             ((GRID_WIDTH * self.block_size + 20) + (x - self.next_piece['x']) * preview_block,
                              50 + (y - self.next_piece['y']) * preview_block, preview_block, preview_block), 1)
        # Display score and level
        score_label = font.render(f"Score: {self.score}", True, WHITE)
        level_label = font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(score_label, (GRID_WIDTH * self.block_size + 20, 150))
        self.screen.blit(level_label, (GRID_WIDTH * self.block_size + 20, 180))
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
