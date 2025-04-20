#!/usr/bin/env python3
# main.py - Entry point for the backgammon game

import os
import pygame
import sys
import time

# Import game components
from model.board import Board
from model.player import HumanPlayer  # This import should now work correctly
from controller.ai_player import AIPlayer
from controller.game_controller import GameController
from view.renderer import Renderer
from utils.asset_manager import get_asset_manager
from utils.asset_creator import create_assets


def check_assets():
    """Check if required assets exist and generate missing ones."""
    assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

    # Check if assets directory exists
    if not os.path.exists(assets_path):
        print("Assets directory not found. Creating assets...")
        create_assets()
        return

    # Check for board image
    board_path = os.path.join(assets_path, 'images', 'board', 'board.png')
    if not os.path.exists(board_path):
        print("Board image missing. Creating assets...")
        create_assets()
        return

    # Check for dice images
    dice_path = os.path.join(assets_path, 'images', 'dice')
    if not os.path.exists(dice_path) or not os.listdir(dice_path):
        print("Dice images missing. Creating assets...")
        create_assets()
        return

    print("All required assets found.")


def main():
    """Main function to run the backgammon game."""
    # Check assets
    check_assets()

    # Initialize Pygame
    pygame.init()

    # Set up display
    width, height = 1024, 768
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Backgammon Game")

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

    # Allow the renderer to fully load before continuing
    time.sleep(0.5)

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