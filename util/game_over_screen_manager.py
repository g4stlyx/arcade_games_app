import pygame

def show_game_over_screen(screen, score, high_score, level):
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Calculate responsive sizes
    main_font_size = max(36, min(screen_width, screen_height) // 11)
    sub_font_size = max(24, min(screen_width, screen_height) // 20)
    
    # Calculate vertical spacing
    vertical_spacing = screen_height // 12
    start_y = screen_height // 5
    
    # Create semi-transparent background
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))  # Black with high transparency
    screen.blit(overlay, (0, 0))
    
    # Main "Game Over" text
    main_font = pygame.font.Font(None, main_font_size)
    game_over_text = main_font.render("Game Over", True, (255, 0, 0))
    text_rect = game_over_text.get_rect(center=(screen_width // 2, start_y))
    screen.blit(game_over_text, text_rect)

    # Display scores and level with smaller font
    sub_font = pygame.font.Font(None, sub_font_size)
    
    # Score text
    score_text = sub_font.render(f'Your Score: {score}', True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(screen_width // 2, start_y + vertical_spacing))
    screen.blit(score_text, score_rect)
    
    # High score text
    high_score_text = sub_font.render(f'High Score: {high_score}', True, (255, 255, 255))
    high_score_rect = high_score_text.get_rect(center=(screen_width // 2, start_y + vertical_spacing * 2))
    screen.blit(high_score_text, high_score_rect)
    
    # Level text
    level_text = sub_font.render(f'Level: {level}', True, (255, 255, 255))
    level_rect = level_text.get_rect(center=(screen_width // 2, start_y + vertical_spacing * 3))
    screen.blit(level_text, level_rect)

    # Display options
    option_y_start = start_y + vertical_spacing * 4.5
    
    restart_text = sub_font.render("Press R to Restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(screen_width // 2, option_y_start))
    screen.blit(restart_text, restart_rect)
    
    menu_text = sub_font.render("Press M to Return to Menu", True, (255, 255, 255))
    menu_rect = menu_text.get_rect(center=(screen_width // 2, option_y_start + vertical_spacing))
    screen.blit(menu_text, menu_rect)
    
    exit_text = sub_font.render("Press Q to Quit", True, (255, 255, 255))
    exit_rect = exit_text.get_rect(center=(screen_width // 2, option_y_start + vertical_spacing * 2))
    screen.blit(exit_text, exit_rect)

    pygame.display.flip()
    
    # Handle events for game over screen
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game
                    return 'restart'
                elif event.key == pygame.K_m:  # Return to menu
                    return 'menu'
                elif event.key == pygame.K_q:  # Quit the game
                    pygame.quit()
                    return