import pygame

def show_pause_screen(screen):
    font = pygame.font.Font(None, 74)
    pause_text = font.render("PAUSED, press P to continue", True, (255, 255, 0))
    text_rect = pause_text.get_rect(center=(400, 300))  # Center the text
    screen.blit(pause_text, text_rect)  # Position the text on the screen
    pygame.display.flip()  # Update the display