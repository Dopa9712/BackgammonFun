#!/usr/bin/env python3
# run_game.py - Run backgammon game with corrected movement and assets path

import os
import pygame
import sys
from board import Board
from game_controller import GameController
from renderer import Renderer
from player import HumanPlayer
from ai_player import AIPlayer


def check_assets():
    """Check if required assets exist and generate missing ones."""
    # Check for generators/assets directory
    assets_path = 'generators/assets'
    if not os.path.exists(assets_path):
        print(f"Assets directory not found at {assets_path}.")
        # Try to find it in other locations
        if os.path.exists('assets'):
            print("Found assets in the current directory.")
            return

    # Check for last move highlight
    last_move_path = os.path.join(assets_path, 'images', 'ui', 'last_move_highlight.png')
    if not os.path.exists(last_move_path):
        print("Last move highlight missing. Generating...")
        try:
            from create_last_move_highlight import create_last_move_highlight
            create_last_move_highlight()
        except ImportError:
            print("WARNING: Could not generate last move highlight.")


def main():
    """Run the backgammon game with the corrected movement directions."""
    # Check assets
    check_assets()

    # Initialize Pygame
    pygame.init()

    # Set up display
    width, height = 1024, 768
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Backgammon vs AI - Fixed Direction")

    # Display loading screen
    font = pygame.font.SysFont('Arial', 30)
    loading_text = font.render("Loading backgammon game...", True, (255, 255, 255))
    screen.fill((34, 139, 34))  # Dark green background
    screen.blit(loading_text, (width // 2 - loading_text.get_width() // 2, height // 2))
    pygame.display.flip()

    # Print instructions
    print("\nBackgammon Game Instructions:")
    print("1. White pieces move from 1 to 24 (increasing)")
    print("2. Black pieces move from 24 to 1 (decreasing)")
    print("3. Click to roll dice")
    print("4. Click on a piece to select it, then click on a destination to move")
    print("5. You cannot land on points with 2+ opponent pieces")
    print("6. When all your pieces are in your home board, you can bear them off")
    print("7. You can use larger dice values to bear off if no pieces on higher points")
    print("8. The AI's last move will be displayed at the top of the screen\n")

    # Create game components
    board = Board()
    human_player = HumanPlayer('White')
    ai_player = AIPlayer('Black')
    renderer = Renderer(screen, width, height)

    # Create game controller
    game_controller = GameController(board, human_player, ai_player, renderer)

    # Main game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Allow escape key to exit
                if event.key == pygame.K_ESCAPE:
                    running = False
            else:
                game_controller.handle_event(event)

        # Update game state
        game_controller.update()

        # Render the game
        renderer.render(board, game_controller.get_game_state())

        # Cap the frame rate
        clock.tick(60)

    # Clean up
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()