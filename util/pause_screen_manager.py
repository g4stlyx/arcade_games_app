import pygame

def show_pause_screen(screen):
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Adaptive font size based on screen dimensions
    font_size = max(36, min(screen_width, screen_height) // 10)
    font = pygame.font.Font(None, font_size)
    
    # Create text with responsive font size
    pause_text = font.render("PAUSED", True, (255, 255, 0))
    
    # Create instruction text with smaller font
    instruction_font = pygame.font.Font(None, font_size // 2)
    instruction_text = instruction_font.render("Press P to continue", True, (255, 255, 255))
    
    # Position text in center of screen
    pause_text_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2 - font_size // 2))
    instruction_text_rect = instruction_text.get_rect(center=(screen_width // 2, screen_height // 2 + font_size // 2))
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
    
    # Apply overlay and draw text
    screen.blit(overlay, (0, 0))
    screen.blit(pause_text, pause_text_rect)
    screen.blit(instruction_text, instruction_text_rect)
    
    pygame.display.flip()