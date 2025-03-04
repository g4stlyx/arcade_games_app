import pygame

class Tank:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

    def update(self):
        # Update game state
        pass

    def draw(self):
        self.screen.fill((255, 255, 255))  # Clear screen
        # Draw game elements
        pygame.display.flip()
