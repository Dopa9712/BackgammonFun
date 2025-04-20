# view/renderer.py - Handles rendering the game to the screen

import pygame
import os
import sys

# Add parent directory to path to allow imports from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.asset_manager import get_asset_manager


class Renderer:
    """Handles rendering the backgammon game to the screen."""

    def __init__(self, screen, width, height):
        """Initialize the renderer.

        Args:
            screen: Pygame screen object
            width: Screen width
            height: Screen height
        """
        self.screen = screen
        self.width = width
        self.height = height

        # Get the asset manager
        self.asset_manager = get_asset_manager()

        # Board dimensions (needed for positioning only)
        self.board_margin_x = 50
        self.board_margin_y = 70
        self.board_width = width - 2 * self.board_margin_x
        self.board_height = height - 2 * self.board_margin_y
        self.point_width = (self.board_width / 2 - 15) / 6  # (half_board - bar) / 6 points
        self.bar_width = 30

        # Default piece and dice size
        self.piece_size = 40
        self.dice_size = 40

        # Calculate positions of all points (for piece placement only)
        self.point_positions = self._calculate_point_positions()

        # Load required images
        self._load_images()

    def _load_images(self):
        """Load all required images using the asset manager."""
        # Main board image
        self.board_image = self.asset_manager.load_image('board', 'board.png')
        if self.board_image:
            # Scale to match screen size if needed
            if self.board_image.get_width() != self.width or self.board_image.get_height() != self.height:
                self.board_image = pygame.transform.scale(self.board_image, (self.width, self.height))

        # Load info background
        self.info_bg = self.asset_manager.load_image('ui', 'info_bg.png')

        # Load game state text images
        self.text_images = {}
        for name in ['roll_dice', 'select_point', 'select_dest', 'ai_thinking',
                     'white_turn', 'black_turn', 'white_wins', 'black_wins']:
            self.text_images[name] = self.asset_manager.load_image('text', f'{name}.png')

        # Load count overlays
        for i in range(1, 16):
            self.text_images[f'count_{i}'] = self.asset_manager.load_image('text', f'count_{i}.png')

        # Load highlight images
        self.highlight_images = {
            'top': self.asset_manager.load_image('ui', 'top_highlight.png'),
            'bottom': self.asset_manager.load_image('ui', 'bottom_highlight.png'),
            'bar': self.asset_manager.load_image('ui', 'bar_highlight.png'),
            'home': self.asset_manager.load_image('ui', 'home_highlight.png'),
            'last_move': self.asset_manager.load_image('ui', 'last_move_highlight.png')
        }

        # Load pieces - try different sizes
        self.piece_images = {'white': None, 'black': None}

        for size in [40, 32, 48]:
            # Try different possible naming conventions
            white = self.asset_manager.load_image('pieces', f'white_piece_{size}.png') or \
                    self.asset_manager.load_image('pieces', f'white_{size}.png')

            black = self.asset_manager.load_image('pieces', f'black_piece_{size}.png') or \
                    self.asset_manager.load_image('pieces', f'black_{size}.png')

            if white and black:
                self.piece_images['white'] = white
                self.piece_images['black'] = black
                self.piece_size = size
                break

        # Load dice - try different sizes
        self.dice_images = {}

        for size in [40, 48]:
            all_found = True
            temp_dice = {}

            for value in range(1, 7):
                # Try different naming conventions
                die = self.asset_manager.load_image('dice', f'die_{value}_{size}.png') or \
                      self.asset_manager.load_image('dice', f'die{value}_{size}.png')

                if die:
                    temp_dice[value] = die
                else:
                    all_found = False
                    break

                # Used die versions
                used_die = self.asset_manager.load_image('dice', f'die_{value}_used_{size}.png') or \
                           self.asset_manager.load_image('dice', f'die{value}_used_{size}.png')

                if used_die:
                    temp_dice[f'{value}_used'] = used_die
                else:
                    all_found = False
                    break

            if all_found:
                self.dice_images = temp_dice
                self.dice_size = size
                break

    def _calculate_point_positions(self):
        """Calculate positions of all points (for piece placement only)."""
        positions = {}

        # Bar midpoint (for reference)
        bar_mid_x = self.board_margin_x + self.board_width / 2
        bar_mid_y = self.board_margin_y + self.board_height / 2

        # Bottom right quadrant (points 1-6) - 1 is rightmost
        for i in range(1, 7):
            x = bar_mid_x + (6 - i) * self.point_width + self.bar_width / 2
            positions[i] = (x, self.board_margin_y + self.board_height)

        # Bottom left quadrant (points 7-12) - 7 is rightmost
        for i in range(7, 13):
            x = self.board_margin_x + (12 - i) * self.point_width
            positions[i] = (x, self.board_margin_y + self.board_height)

        # Top left quadrant (points 13-18) - 13 is leftmost
        for i in range(13, 19):
            x = self.board_margin_x + (i - 13) * self.point_width
            positions[i] = (x, self.board_margin_y)

        # Top right quadrant (points 19-24) - 24 is rightmost
        for i in range(19, 25):
            x = bar_mid_x + (i - 19) * self.point_width + self.bar_width / 2
            positions[i] = (x, self.board_margin_y)

        # Bar positions (0 for black, 25 for white)
        positions[0] = (bar_mid_x - self.bar_width / 4, bar_mid_y - self.board_height / 4)  # Black bar
        positions[25] = (bar_mid_x - self.bar_width / 4, bar_mid_y + self.board_height / 4)  # White bar

        # Home positions (26 for black, 27 for white)
        positions[26] = (self.board_margin_x - 10, self.board_margin_y + self.board_height / 4)  # Black home
        positions[27] = (
        self.board_margin_x + self.board_width + 10, self.board_margin_y + self.board_height * 3 / 4)  # White home

        return positions

    def render(self, board, game_state):
        """Render the game by blitting pre-generated images.

        Args:
            board: The game board
            game_state: Dictionary containing the current game state
        """
        # Draw the board (or fallback to filling with color)
        if self.board_image:
            self.screen.blit(self.board_image, (0, 0))
        else:
            self.screen.fill((34, 139, 34))  # Dark green background fallback
            print("WARNING: Board image missing. Using fallback.")
            # Draw a simple board outline if image is missing
            pygame.draw.rect(self.screen, (210, 180, 140),
                             (self.board_margin_x, self.board_margin_y,
                              self.board_width, self.board_height))

        # Highlight last AI moves
        if game_state["current_player"] == "White" and game_state["last_ai_moves"]:
            self._blit_last_moves(game_state["last_ai_moves"])

        # Highlight selected point and possible moves if any
        if game_state["selected_point"] is not None:
            self._blit_highlight(game_state["selected_point"])

            if game_state["possible_moves"]:
                for from_point, to_point in game_state["possible_moves"]:
                    if from_point == game_state["selected_point"]:
                        self._blit_highlight(to_point)

        # Blit pieces
        self._blit_pieces(board)

        # Blit dice
        self._blit_dice(game_state["dice_values"], game_state["dice_used"])

        # Blit game state info
        self._blit_game_info(game_state)

        # Blit AI's last move info
        self._blit_last_move_info(game_state["last_ai_moves"])

        # Update the display
        pygame.display.flip()

    def _blit_last_moves(self, last_moves):
        """Blit highlights for AI's last moves."""
        if not last_moves:
            return

        # Get the highlight image for last move (different color than selection)
        last_move_highlight = self.highlight_images.get('last_move')

        # If no special highlight for last move, use regular highlight
        if not last_move_highlight:
            for from_point, to_point in last_moves:
                self._blit_highlight(to_point)
            return

        # Use special highlight for last moves
        for from_point, to_point in last_moves:
            x, y = self.point_positions.get(to_point, (0, 0))
            if to_point in range(1, 13):  # Bottom row
                self.screen.blit(last_move_highlight, (int(x), int(y - self.board_height / 4)))
            elif to_point in range(13, 25):  # Top row
                self.screen.blit(last_move_highlight, (int(x), int(y)))
            elif to_point in (0, 25):  # Bar
                bar_y = self.board_margin_y if to_point == 0 else self.board_margin_y + self.board_height / 2
                bar_x = self.board_margin_x + self.board_width / 2 - self.bar_width / 2
                self.screen.blit(last_move_highlight, (int(bar_x), int(bar_y)))
            elif to_point in (26, 27):  # Home
                home_x = self.board_margin_x - 20 if to_point == 26 else self.board_margin_x + self.board_width
                home_y = self.board_margin_y if to_point == 26 else self.board_margin_y + self.board_height / 2
                self.screen.blit(last_move_highlight, (int(home_x), int(home_y)))

    def _blit_highlight(self, point):
        """Blit the appropriate highlight overlay for a point."""
        if point not in self.point_positions:
            return

        x, y = self.point_positions[point]

        # Select the correct highlight image
        highlight = None

        if 1 <= point <= 12:  # Bottom row
            highlight = self.highlight_images.get('bottom')
            if highlight:
                self.screen.blit(highlight, (int(x), int(y - self.board_height / 4)))

        elif 13 <= point <= 24:  # Top row
            highlight = self.highlight_images.get('top')
            if highlight:
                self.screen.blit(highlight, (int(x), int(y)))

        elif point in (0, 25):  # Bar
            highlight = self.highlight_images.get('bar')
            if highlight:
                bar_y = self.board_margin_y if point == 0 else self.board_margin_y + self.board_height / 2
                bar_x = self.board_margin_x + self.board_width / 2 - self.bar_width / 2
                self.screen.blit(highlight, (int(bar_x), int(bar_y)))

        elif point in (26, 27):  # Home
            highlight = self.highlight_images.get('home')
            if highlight:
                home_x = self.board_margin_x - 20 if point == 26 else self.board_margin_x + self.board_width
                home_y = self.board_margin_y if point == 26 else self.board_margin_y + self.board_height / 2
                self.screen.blit(highlight, (int(home_x), int(home_y)))

    def _blit_pieces(self, board):
        """Blit pieces onto the board."""
        # Check if piece images are available
        white_piece = self.piece_images.get('white')
        black_piece = self.piece_images.get('black')

        if not white_piece or not black_piece:
            print("WARNING: Piece images missing.")
            return

        for point in range(28):  # 0-27 for all points including bar and home
            pieces = board.get_pieces_at(point)
            if not pieces:
                continue

            # Skip points without defined positions
            if point not in self.point_positions:
                continue

            base_x, base_y = self.point_positions[point]
            max_pieces_visible = 5  # Max pieces to show before stacking

            # Calculate the center x-coordinate of the point
            x_center = base_x + self.point_width / 2

            # Determine stacking direction and start position
            if point <= 12:  # Bottom row points
                direction = -1  # Up
                start_y = base_y - self.piece_size / 2
            elif 13 <= point <= 24:  # Top row points
                direction = 1  # Down
                start_y = base_y + self.piece_size / 2
            elif point == 0:  # Black bar
                direction = -1  # Up
                start_y = self.board_margin_y + self.board_height / 2 - self.piece_size / 2
                x_center = self.board_margin_x + self.board_width / 2
            elif point == 25:  # White bar
                direction = 1  # Down
                start_y = self.board_margin_y + self.board_height / 2 + self.piece_size / 2
                x_center = self.board_margin_x + self.board_width / 2
            else:  # Home areas (26, 27)
                direction = 0  # Vertical stacking in home areas
                if point == 26:  # Black home
                    x_center = self.board_margin_x - 10
                    start_y = self.board_margin_y + self.board_height / 4
                else:  # White home
                    x_center = self.board_margin_x + self.board_width + 10
                    start_y = self.board_margin_y + self.board_height * 3 / 4

            # Draw each piece (up to max_pieces_visible)
            visible_count = min(len(pieces), max_pieces_visible)
            for i in range(visible_count):
                color = pieces[i]

                # Calculate position
                if direction == 0:  # Home areas - stack vertically
                    x = x_center
                    y = start_y + i * (self.piece_size * 0.6)
                else:  # Normal stacking
                    x = x_center
                    y = start_y + direction * i * (self.piece_size * 0.6)

                # Get correct piece image
                piece_img = self.piece_images['white'] if color == "White" else self.piece_images['black']

                # Calculate exact position for blitting (centered on the calculated position)
                x_pos = int(x - piece_img.get_width() / 2)
                y_pos = int(y - piece_img.get_height() / 2)

                # Blit the piece
                self.screen.blit(piece_img, (x_pos, y_pos))

            # Show count if more pieces than visible
            if len(pieces) > max_pieces_visible:
                count_img = self.text_images.get(f'count_{len(pieces)}')
                if count_img:
                    # Position for count
                    if direction == 0:  # Home areas
                        count_x = int(x_center - count_img.get_width() / 2)
                        count_y = int(start_y + visible_count * (self.piece_size * 0.6))
                    else:
                        count_x = int(x_center - count_img.get_width() / 2)
                        count_y = int(start_y + direction * (visible_count) * (self.piece_size * 0.6))

                    self.screen.blit(count_img, (count_x, count_y))
                else:
                    # If count image is missing, render text directly
                    text = self.asset_manager.create_text_surface(str(len(pieces)), 'small')
                    if direction == 0:  # Home areas
                        count_x = int(x_center - text.get_width() / 2)
                        count_y = int(start_y + visible_count * (self.piece_size * 0.6))
                    else:
                        count_x = int(x_center - text.get_width() / 2)
                        count_y = int(start_y + direction * (visible_count) * (self.piece_size * 0.6))

                    # Add background for better visibility
                    bg_rect = pygame.Rect(count_x - 2, count_y - 2, text.get_width() + 4, text.get_height() + 4)
                    pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
                    self.screen.blit(text, (count_x, count_y))

    def _blit_dice(self, dice_values, dice_used):
        """Blit dice images.

        Args:
            dice_values: List of dice values
            dice_used: List of boolean flags indicating if each die has been used
        """
        if not dice_values:
            return

        # Check if we have at least some dice images
        if not self.dice_images:
            print("WARNING: Dice images missing.")
            return

        # Position dice at the bottom center of the screen
        dice_margin = 10
        start_x = self.width / 2 - (len(dice_values) * (self.dice_size + dice_margin)) / 2
        y_position = self.height - self.board_margin_y / 2

        for i, value in enumerate(dice_values):
            # Skip invalid dice values
            if value < 1 or value > 6:
                continue

            # Determine which image to use (used or regular)
            die_key = f"{value}_used" if (dice_used and i < len(dice_used) and dice_used[i]) else value

            die_img = self.dice_images.get(die_key)
            if die_img:
                x_pos = int(start_x + i * (self.dice_size + dice_margin))
                y_pos = int(y_position - die_img.get_height() / 2)
                self.screen.blit(die_img, (x_pos, y_pos))
            else:
                # If image is missing, create a simple representation
                die_surface = pygame.Surface((self.dice_size, self.dice_size))
                die_surface.fill((255, 255, 255))
                pygame.draw.rect(die_surface, (0, 0, 0), die_surface.get_rect(), 2)

                # Render the value
                value_text = self.asset_manager.create_text_surface(str(value), 'regular')
                text_pos = ((self.dice_size - value_text.get_width()) // 2,
                            (self.dice_size - value_text.get_height()) // 2)

                # Gray out if used
                if die_key.endswith('_used'):
                    overlay = pygame.Surface((self.dice_size, self.dice_size), pygame.SRCALPHA)
                    overlay.fill((128, 128, 128, 128))
                    die_surface.blit(overlay, (0, 0))

                die_surface.blit(value_text, text_pos)

                x_pos = int(start_x + i * (self.dice_size + dice_margin))
                y_pos = int(y_position - self.dice_size / 2)
                self.screen.blit(die_surface, (x_pos, y_pos))

    def _blit_game_info(self, game_state):
        """Blit game state information.

        Args:
            game_state: Dictionary containing current game state
        """
        # Blit info background
        if self.info_bg:
            self.screen.blit(self.info_bg, (0, 0))

        # Determine which instruction text to show
        text_key = None
        if game_state["state"] == "ROLL_DICE":
            text_key = "roll_dice"
        elif game_state["state"] == "HUMAN_TURN":
            if game_state["selected_point"] is None:
                text_key = "select_point"
            else:
                text_key = "select_dest"
        elif game_state["state"] == "AI_TURN":
            text_key = "ai_thinking"
        elif game_state["state"] == "GAME_OVER":
            text_key = "white_wins" if game_state["current_player"] == "White" else "black_wins"

        # Blit instruction text if available
        if text_key:
            text_img = self.text_images.get(text_key)
            if text_img:  # Check if image was loaded
                self.screen.blit(text_img, (self.width - text_img.get_width() - 20, 20))
            else:
                # If image is missing, draw text directly
                instruction_text = {
                    "roll_dice": "Click to roll dice",
                    "select_point": "Select a point with your pieces",
                    "select_dest": "Select destination point",
                    "ai_thinking": "AI is thinking...",
                    "white_wins": "White wins! Click to play again.",
                    "black_wins": "Black wins! Click to play again."
                }.get(text_key, "")

                text_surface = self.asset_manager.create_text_surface(instruction_text, 'regular')
                self.screen.blit(text_surface, (self.width - text_surface.get_width() - 20, 20))

        # Blit player turn text if available
        player_key = "white_turn" if game_state["current_player"] == "White" else "black_turn"
        player_img = self.text_images.get(player_key)
        if player_img:  # Check if image was loaded
            self.screen.blit(player_img, (20, 20))
        else:
            # If image is missing, draw text directly
            turn_text = "White's turn" if game_state["current_player"] == "White" else "Black's turn"
            text_surface = self.asset_manager.create_text_surface(turn_text, 'regular')
            self.screen.blit(text_surface, (20, 20))

    def _blit_last_move_info(self, last_moves):
        """Display AI's last move information on screen.

        Args:
            last_moves: List of (from_point, to_point) tuples representing the AI's last moves
        """
        if not last_moves:
            return

        # Display last move information in text format at the top of the screen
        move_text = "AI's last move: "
        for i, (from_point, to_point) in enumerate(last_moves):
            if i > 0:
                move_text += ", "
            move_text += f"{from_point} → {to_point}"

        # Render using built-in font
        move_surface = self.asset_manager.create_text_surface(move_text, 'regular')
        self.screen.blit(move_surface, (self.width // 2 - move_surface.get_width() // 2, 45))

    def get_point_at_position(self, pos):
        """Convert screen position to board point.

        Args:
            pos: (x, y) tuple of screen coordinates

        Returns:
            int or None: The point number (0-27) at the given position, or None if no point
        """
        x, y = pos

        # Check each point to see if the position is within it
        for point, (point_x, point_y) in self.point_positions.items():
            if 1 <= point <= 12:  # Bottom row points
                triangle_height = int(self.board_height / 4 - 10)
                if (point_x <= x <= point_x + self.point_width and
                        point_y - triangle_height <= y <= point_y):
                    return point

            elif 13 <= point <= 24:  # Top row points
                triangle_height = int(self.board_height / 4 - 10)
                if (point_x <= x <= point_x + self.point_width and
                        point_y <= y <= point_y + triangle_height):
                    return point

            elif point == 0 or point == 25:  # Bar
                bar_x = int(self.board_margin_x + self.board_width / 2 - self.bar_width / 2)
                if point == 0:  # Black bar (top half)
                    bar_y = int(self.board_margin_y)
                    bar_height = int(self.board_height / 2)
                else:  # White bar (bottom half)
                    bar_y = int(self.board_margin_y + self.board_height / 2)
                    bar_height = int(self.board_height / 2)

                if (bar_x <= x <= bar_x + self.bar_width and
                        bar_y <= y <= bar_y + bar_height):
                    return point

            elif point == 26:  # Black home
                home_rect = pygame.Rect(
                    int(self.board_margin_x - 20),
                    int(self.board_margin_y),
                    20,
                    int(self.board_height / 2)
                )
                if home_rect.collidepoint(x, y):
                    return point

            elif point == 27:  # White home
                home_rect = pygame.Rect(
                    int(self.board_margin_x + self.board_width),
                    int(self.board_margin_y + self.board_height / 2),
                    20,
                    int(self.board_height / 2)
                )
                if home_rect.collidepoint(x, y):
                    return point

        return None