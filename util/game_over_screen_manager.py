import pygame

def show_game_over_screen(screen, score, high_score, level):
    while True:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        screen.blit(game_over_text, (250, 100))

        # Display scores and level
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Your Score: {score}', True, (255, 255, 255))
        high_score_text = font.render(f'High Score: {high_score}', True, (255, 255, 255))
        level_text = font.render(f'Level: {level}', True, (255, 255, 255))
        screen.blit(score_text, (300, 200))
        screen.blit(high_score_text, (300, 250))
        screen.blit(level_text, (300, 300))

        # Display options
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        menu_text = font.render("Press M to Return to Menu", True, (255, 255, 255))
        exit_text = font.render("Press Q to Quit", True, (255, 255, 255))
        screen.blit(restart_text, (300, 350))
        screen.blit(menu_text, (300, 400))
        screen.blit(exit_text, (300, 450))

        pygame.display.flip()

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