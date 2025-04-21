#!/usr/bin/env python3
# main.py - Entry point for the enhanced backgammon game with extensive error handling

import os
import pygame
import sys
import time
import traceback
from datetime import datetime

# Try importing the game components and log any errors
try:
    from model.board import Board
    from model.player import HumanPlayer
    from controller.ai_player import AIPlayer
    from controller.game_controller import GameController
    from view.renderer import Renderer
    from utils.asset_manager import get_asset_manager
    from utils.asset_creator import create_assets

    print("All modules imported successfully")
except ImportError as e:
    print(f"Error importing game modules: {e}")
    traceback.print_exc()
    print("Make sure all Python files are in the correct directories.")
    sys.exit(1)


class BackgammonGame:
    """Main game class that coordinates all components."""

    def __init__(self, width=1024, height=768, ai_difficulty="medium"):
        """Initialize the backgammon game.

        Args:
            width: Screen width
            height: Screen height
            ai_difficulty: AI difficulty level ("easy", "medium", "hard")
        """
        print(f"Initializing BackgammonGame ({width}x{height}, AI: {ai_difficulty})")
        self.width = width
        self.height = height
        self.ai_difficulty = ai_difficulty

        # Flag to track if the game is running
        self.running = True

        # Initialize pygame
        try:
            pygame.init()
            driver_name = pygame.display.get_driver()
            print(f"Pygame initialized successfully (using driver: {driver_name})")
        except Exception as e:
            print(f"Error initializing pygame: {e}")
            traceback.print_exc()
            sys.exit(1)

        pygame.display.set_caption("Elegant Backgammon")

        # Always create assets first to ensure they exist for the renderer
        print("Creating game assets...")
        try:
            create_assets(width, height)
            print("Assets created successfully")
        except Exception as e:
            print(f"Warning: Error creating assets: {e}")
            traceback.print_exc()
            print("Will attempt to continue anyway, but game might not display correctly.")

        # Set up display with icon
        try:
            self.screen = pygame.display.set_mode((width, height))
            print(f"Display window created ({width}x{height})")
        except Exception as e:
            print(f"Error creating display: {e}")
            traceback.print_exc()
            sys.exit(1)

        self._set_window_icon()

        # Display loading screen
        try:
            self._show_loading_screen()
            print("Loading screen displayed")
        except Exception as e:
            print(f"Error showing loading screen: {e}")
            traceback.print_exc()
            # Not critical, continue

        # Print game instructions
        self._print_instructions()

        # Create game components
        try:
            self._create_game_components()
            print("Game components created successfully")
        except Exception as e:
            print(f"Error creating game components: {e}")
            traceback.print_exc()
            sys.exit(1)

        # Main game loop
        self.clock = pygame.time.Clock()

    def _set_window_icon(self):
        """Set the window icon."""
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'assets', 'images', 'ui', 'icon.png')
        if os.path.exists(icon_path):
            try:
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
                print(f"Window icon set from {icon_path}")
            except pygame.error as e:
                print(f"Could not load window icon: {e}")
        else:
            print(f"Window icon not found at {icon_path}")

    def _show_loading_screen(self):
        """Display a loading screen while initializing."""
        # Fill with dark wood color
        self.screen.fill((40, 26, 13))

        try:
            # Use asset manager to access fonts if available
            asset_manager = get_asset_manager()
            font = asset_manager.get_font('large')
            print("Using asset manager font for loading screen")
        except Exception as e:
            print(f"Cannot use asset manager font, falling back to default: {e}")
            font = pygame.font.SysFont('Arial', 30)

        # Fancy loading text with shadow
        loading_text = font.render("Loading Elegant Backgammon...", True, (230, 210, 180))
        shadow_text = font.render("Loading Elegant Backgammon...", True, (0, 0, 0))

        # Draw text with shadow effect
        self.screen.blit(shadow_text,
                         (self.width // 2 - loading_text.get_width() // 2 + 2,
                          self.height // 2 + 2))
        self.screen.blit(loading_text,
                         (self.width // 2 - loading_text.get_width() // 2,
                          self.height // 2))

        # Add version info
        version_text = pygame.font.SysFont('Arial', 16).render("Version 2.0", True, (180, 160, 140))
        self.screen.blit(version_text, (self.width - version_text.get_width() - 10,
                                        self.height - version_text.get_height() - 10))

        pygame.display.flip()

    def _print_instructions(self):
        """Print game instructions to the console."""
        print("\n" + "=" * 50)
        print("ELEGANT BACKGAMMON - GAME INSTRUCTIONS")
        print("=" * 50)
        print("1. White pieces move from 1 → 24 (increasing)")
        print("2. Black pieces move from 24 → 1 (decreasing)")
        print("3. Click to roll dice")
        print("4. Click on a piece to select it, then click a destination")
        print("5. You cannot land on points with 2+ opponent pieces")
        print("6. When all your pieces are in your home board, you can bear them off")
        print("7. The first player to bear off all pieces wins")
        print("\nKEYBOARD SHORTCUTS:")
        print("- F1: Toggle debug mode")
        print("- F2: Toggle move hints")
        print("- P or ESC: Pause game")
        print("- R: Reset game")
        print("=" * 50 + "\n")

    def _create_game_components(self):
        """Create all game components."""
        print("Creating game board...")
        self.board = Board()

        print("Creating human player...")
        self.human_player = HumanPlayer('White')

        print("Creating AI player...")
        self.ai_player = AIPlayer('Black', self.ai_difficulty)

        print("Creating renderer...")
        # Create renderer - assumes all assets exist
        self.renderer = Renderer(self.screen, self.width, self.height)

        # Allow components to fully initialize
        time.sleep(0.5)

        print("Creating game controller...")
        # Create game controller
        self.game_controller = GameController(self.board, self.human_player,
                                              self.ai_player, self.renderer)

    def run(self):
        """Run the main game loop."""
        print("Starting main game loop")
        frame_count = 0
        start_time = time.time()

        try:
            while self.running:
                # Process events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print("Quit event received")
                        self.running = False
                    else:
                        try:
                            self.game_controller.handle_event(event)
                        except Exception as e:
                            print(f"Error handling event: {e}")
                            traceback.print_exc()

                # Update game state
                try:
                    self.game_controller.update()
                except Exception as e:
                    print(f"Error updating game state: {e}")
                    traceback.print_exc()

                # Render the game - assumes all assets exist
                try:
                    self.renderer.render(self.board, self.game_controller.get_game_state())
                    frame_count += 1
                except Exception as e:
                    print(f"Error rendering game: {e}")
                    traceback.print_exc()

                # Cap the frame rate
                self.clock.tick(60)

                # Log performance every 5 seconds
                if frame_count % 300 == 0:  # Every ~5 seconds at 60 FPS
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    print(f"Performance: {fps:.1f} FPS, {frame_count} frames in {elapsed:.1f}s")
        except KeyboardInterrupt:
            print("Game interrupted by user")
        except Exception as e:
            print(f"Unexpected error in game loop: {e}")
            traceback.print_exc()
        finally:
            # Clean up
            pygame.quit()
            print("\nThanks for playing Elegant Backgammon!")
            print(f"Game session ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main function with command line argument handling."""
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Elegant Backgammon Game')
    parser.add_argument('--width', type=int, default=1024, help='Screen width')
    parser.add_argument('--height', type=int, default=768, help='Screen height')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard'],
                        default='medium', help='AI difficulty level')
    parser.add_argument('--recreate-assets', action='store_true',
                        help='Force recreation of game assets')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')

    args = parser.parse_args()

    # Report Python and Pygame versions
    print(f"Python version: {sys.version}")
    print(f"Pygame version: {pygame.version.ver}")
    print(f"Running on: {sys.platform}")

    # Force asset recreation if requested
    if args.recreate_assets:
        print(f"Forcing recreation of game assets ({args.width}x{args.height})...")
        try:
            create_assets(args.width, args.height)
            print("Assets recreated successfully")
        except Exception as e:
            print(f"Error recreating assets: {e}")
            traceback.print_exc()

    # Create and run the game (game init will automatically create assets if needed)
    try:
        print(f"Creating game instance: {args.width}x{args.height}, {args.difficulty} AI")
        game = BackgammonGame(args.width, args.height, args.difficulty)
        game.run()
    except Exception as e:
        print(f"Error in main game: {e}")
        traceback.print_exc()

        # Keep the console window open if there was an error
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Critical error: {e}")
        traceback.print_exc()
        input("\nPress Enter to exit...")