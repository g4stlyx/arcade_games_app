import pygame
from menu import MainMenu

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Arcade Super App")
    
    menu = MainMenu(screen)
    menu.run()

    pygame.quit()

if __name__ == "__main__":
    main()