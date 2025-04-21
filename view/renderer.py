# view/renderer.py - Simplified renderer that assumes assets exist

import pygame
import os
import sys

# Add parent directory to path to allow imports from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.asset_manager import get_asset_manager


class Renderer:
    """Handles rendering the backgammon game - assumes all assets exist."""

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
        self.point_width = (self.board_width / 2 - 20) / 6  # Matching asset creator
        self.bar_width = 40  # Matching asset creator

        # Default piece and dice size
        self.piece_size = 40
        self.dice_size = 40

        # Calculate positions of all points (for piece placement)
        self.point_positions = self._calculate_point_positions()

        # Debug mode for development
        self.debug_mode = False

        # Load all required assets
        self._load_assets()

    def _load_assets(self):
        """Load all required assets - assumes they exist."""
        # Board image
        self.board_image = self.asset_manager.load_image('board', 'board.png')

        # Info background
        self.info_bg = self.asset_manager.load_image('ui', 'info_bg.png')

        # Load game state text images
        self.text_images = {}
        text_image_names = ['roll_dice', 'select_point', 'select_dest', 'ai_thinking',
                            'white_turn', 'black_turn', 'white_wins', 'black_wins']

        for name in text_image_names:
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

        # Load piece images at standard size
        self.piece_images = {
            'white': self.asset_manager.load_image('pieces', f'white_piece_{self.piece_size}.png'),
            'black': self.asset_manager.load_image('pieces', f'black_piece_{self.piece_size}.png')
        }

        # Load dice images
        self.dice_images = {}
        for value in range(1, 7):
            self.dice_images[value] = self.asset_manager.load_image('dice', f'die_{value}_{self.dice_size}.png')
            self.dice_images[f'{value}_used'] = self.asset_manager.load_image('dice',
                                                                              f'die_{value}_used_{self.dice_size}.png')

    def _calculate_point_positions(self):
        """Calculate positions of all points (for piece placement)."""
        positions = {}

        # Bar midpoint (for reference)
        bar_mid_x = self.board_margin_x + self.board_width / 2
        bar_mid_y = self.board_margin_y + self.board_height / 2

        # Bottom right quadrant (points 1-6) - 1 is rightmost
        for i in range(1, 7):
            x = bar_mid_x + (6 - i) * self.point_width + self.bar_width / 2
            positions[i] = (x + self.point_width / 2, self.board_margin_y + self.board_height)

        # Bottom left quadrant (points 7-12) - 7 is rightmost
        for i in range(7, 13):
            x = self.board_margin_x + (12 - i) * self.point_width
            positions[i] = (x + self.point_width / 2, self.board_margin_y + self.board_height)

        # Top left quadrant (points 13-18) - 13 is leftmost
        for i in range(13, 19):
            x = self.board_margin_x + (i - 13) * self.point_width
            positions[i] = (x + self.point_width / 2, self.board_margin_y)

        # Top right quadrant (points 19-24) - 24 is rightmost
        for i in range(19, 25):
            x = bar_mid_x + (i - 19) * self.point_width + self.bar_width / 2
            positions[i] = (x + self.point_width / 2, self.board_margin_y)

        # Bar positions (0 for black, 25 for white)
        positions[0] = (bar_mid_x, bar_mid_y - self.board_height / 4)  # Black bar
        positions[25] = (bar_mid_x, bar_mid_y + self.board_height / 4)  # White bar

        # Home positions (26 for black, 27 for white)
        positions[26] = (self.board_margin_x - 10, self.board_margin_y + self.board_height / 4)  # Black home
        positions[27] = (self.board_margin_x + self.board_width + 10,
                         self.board_margin_y + self.board_height * 3 / 4)  # White home

        return positions

    def render(self, board, game_state):
        """Render the game (assumes all assets exist).

        Args:
            board: The game board
            game_state: Dictionary containing the current game state
        """
        # Draw the board
        self.screen.blit(self.board_image, (0, 0))

        # Highlight last AI moves
        if game_state.get("last_ai_moves"):
            self._blit_last_moves(game_state["last_ai_moves"])

        # Highlight selected point and possible moves if any
        if game_state.get("selected_point") is not None:
            self._blit_highlight(game_state["selected_point"])

            # Highlight possible moves for better user experience
            if game_state.get("possible_moves"):
                for from_point, to_point in game_state["possible_moves"]:
                    if from_point == game_state["selected_point"]:
                        self._blit_highlight(to_point)

        # Blit pieces
        self._blit_pieces(board)

        # Blit dice
        self._blit_dice(game_state.get("dice_values", []), game_state.get("dice_used", []))

        # Blit game state info
        self._blit_game_info(game_state)

        # Blit AI's last move info
        self._blit_last_move_info(game_state.get("last_ai_moves", []))

        # Display debug info if enabled
        if self.debug_mode:
            self._display_debug_info(board, game_state)

        # Update the display
        pygame.display.flip()

    def _blit_last_moves(self, last_moves):
        """Blit highlights for AI's last moves."""
        if not last_moves:
            return

        # Highlight each destination point of the AI's last moves
        for from_point, to_point in last_moves:
            x, y = self.point_positions.get(to_point, (0, 0))

            # Different positioning based on the point location
            if to_point in range(1, 13):  # Bottom row
                x_pos = int(x - self.point_width / 2)
                y_pos = int(y - self.board_height / 4)
                self.screen.blit(self.highlight_images['last_move'], (x_pos, y_pos))

            elif to_point in range(13, 25):  # Top row
                x_pos = int(x - self.point_width / 2)
                y_pos = int(y)
                self.screen.blit(self.highlight_images['last_move'], (x_pos, y_pos))

            elif to_point in (0, 25):  # Bar
                bar_x = self.board_margin_x + self.board_width / 2 - self.bar_width / 2
                bar_y = self.board_margin_y if to_point == 0 else self.board_margin_y + self.board_height / 2
                self.screen.blit(self.highlight_images['bar'], (int(bar_x), int(bar_y)))

            elif to_point in (26, 27):  # Home
                home_x = self.board_margin_x - 20 if to_point == 26 else self.board_margin_x + self.board_width
                home_y = self.board_margin_y if to_point == 26 else self.board_margin_y + self.board_height / 2
                self.screen.blit(self.highlight_images['home'], (int(home_x), int(home_y)))

    # Add this method to your renderer.py file inside the Renderer class

    def add_move_animation(self, from_point, to_point, color, duration=30):
        """Add an animation for a piece moving between points.

        This is a placeholder for future animation support.

        Args:
            from_point: Starting point
            to_point: Destination point
            color: Piece color
            duration: Animation duration in frames
        """
        # This is a stub for future animation implementation
        # Currently, we don't do any animations, but the method needs to exist
        # to prevent the 'object has no attribute' error
        pass

    def _blit_highlight(self, point):
        """Blit the appropriate highlight overlay for a point."""
        if point not in self.point_positions:
            return

        x, y = self.point_positions[point]

        # Select the correct highlight image based on point location
        if 1 <= point <= 12:  # Bottom row
            x_pos = int(x - self.point_width / 2)
            y_pos = int(y - self.board_height / 4)
            self.screen.blit(self.highlight_images['bottom'], (x_pos, y_pos))

        elif 13 <= point <= 24:  # Top row
            x_pos = int(x - self.point_width / 2)
            y_pos = int(y)
            self.screen.blit(self.highlight_images['top'], (x_pos, y_pos))

        elif point in (0, 25):  # Bar
            highlight = self.highlight_images['bar']
            bar_y = self.board_margin_y if point == 0 else self.board_margin_y + self.board_height / 2
            bar_x = self.board_margin_x + self.board_width / 2 - self.bar_width / 2
            self.screen.blit(highlight, (int(bar_x), int(bar_y)))

        elif point in (26, 27):  # Home
            highlight = self.highlight_images['home']
            home_x = self.board_margin_x - 20 if point == 26 else self.board_margin_x + self.board_width
            home_y = self.board_margin_y if point == 26 else self.board_margin_y + self.board_height / 2
            self.screen.blit(highlight, (int(home_x), int(home_y)))

    def _blit_pieces(self, board):
        """Blit pieces onto the board."""
        white_piece = self.piece_images['white']
        black_piece = self.piece_images['black']

        max_pieces_visible = 5  # Max pieces to show before adding count

        for point in range(28):  # 0-27 for all points including bar and home
            pieces = board.get_pieces_at(point)
            if not pieces:
                continue

            # Skip points without defined positions
            if point not in self.point_positions:
                continue

            base_x, base_y = self.point_positions[point]

            # Determine stacking direction and start position based on point location
            if point <= 12:  # Bottom row points
                direction = -1  # Up
                start_y = base_y - self.piece_size / 2
            elif 13 <= point <= 24:  # Top row points
                direction = 1  # Down
                start_y = base_y + self.piece_size / 2
            elif point == 0:  # Black bar
                direction = 1  # Down from center
                start_y = self.board_margin_y + self.board_height / 4
                base_x = self.board_margin_x + self.board_width / 2
            elif point == 25:  # White bar
                direction = -1  # Up from center
                start_y = self.board_margin_y + self.board_height * 3 / 4
                base_x = self.board_margin_x + self.board_width / 2
            else:  # Home areas (26, 27)
                direction = 0  # Vertical stacking in home areas
                if point == 26:  # Black home
                    base_x = self.board_margin_x - 10
                    start_y = self.board_margin_y + self.board_height / 4
                else:  # White home
                    base_x = self.board_margin_x + self.board_width + 10
                    start_y = self.board_margin_y + self.board_height * 3 / 4

            # Draw each piece (up to max_pieces_visible)
            visible_count = min(len(pieces), max_pieces_visible)
            for i in range(visible_count):
                color = pieces[i]

                # Calculate position with tight stacking
                if direction == 0:  # Home areas
                    x = base_x
                    y = start_y + i * (self.piece_size * 0.4)
                else:  # Normal stacking
                    x = base_x
                    y = start_y + direction * i * (self.piece_size * 0.4)

                # Get correct piece image
                piece_img = white_piece if color == "White" else black_piece

                # Calculate exact position for blitting (centered)
                x_pos = int(x - piece_img.get_width() / 2)
                y_pos = int(y - piece_img.get_height() / 2)

                # Blit the piece
                self.screen.blit(piece_img, (x_pos, y_pos))

            # Show count if more pieces than visible
            if len(pieces) > max_pieces_visible:
                count_img = self.text_images.get(f'count_{len(pieces)}')

                # Position for count
                if direction == 0:  # Home areas
                    count_x = int(base_x - count_img.get_width() / 2)
                    count_y = int(start_y + visible_count * (self.piece_size * 0.4))
                else:
                    count_x = int(base_x - count_img.get_width() / 2)
                    count_y = int(start_y + direction * (visible_count) * (self.piece_size * 0.4))

                self.screen.blit(count_img, (count_x, count_y))

    def _blit_dice(self, dice_values, dice_used):
        """Blit dice images."""
        if not dice_values:
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
            is_used = (i < len(dice_used) and dice_used[i])
            die_key = f"{value}_used" if is_used else value

            die_img = self.dice_images[die_key]
            x_pos = int(start_x + i * (self.dice_size + dice_margin))
            y_pos = int(y_position - die_img.get_height() / 2)

            # Draw shadow for 3D effect
            shadow_pos = (x_pos + 2, y_pos + 2)
            shadow = pygame.Surface(die_img.get_size(), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 40))
            self.screen.blit(shadow, shadow_pos)

            # Draw the die
            self.screen.blit(die_img, (x_pos, y_pos))

    def _blit_game_info(self, game_state):
        """Blit game state information."""
        # Blit info background
        self.screen.blit(self.info_bg, (0, 0))

        # Determine which instruction text to show based on game state
        text_key = None
        if game_state.get("state") == "ROLL_DICE":
            text_key = "roll_dice"
        elif game_state.get("state") == "HUMAN_TURN":
            if game_state.get("selected_point") is None:
                text_key = "select_point"
            else:
                text_key = "select_dest"
        elif game_state.get("state") == "AI_TURN":
            text_key = "ai_thinking"
        elif game_state.get("state") == "GAME_OVER":
            text_key = "white_wins" if game_state.get("current_player") == "White" else "black_wins"

        # Blit instruction text
        if text_key:
            text_img = self.text_images[text_key]
            self.screen.blit(text_img, (self.width - text_img.get_width() - 20, 20))

        # Blit player turn text
        player_key = "white_turn" if game_state.get("current_player") == "White" else "black_turn"
        player_img = self.text_images[player_key]
        self.screen.blit(player_img, (20, 20))

    def _blit_last_move_info(self, last_moves):
        """Display AI's last move information on screen."""
        if not last_moves:
            return

        # Display last move information in text format at the top of the screen
        move_text = "Last move: "
        for i, (from_point, to_point) in enumerate(last_moves):
            if i > 0:
                move_text += ", "
            move_text += f"{from_point} → {to_point}"

        # Use asset manager to render text
        text_surface = self.asset_manager.create_text_surface(move_text, 'regular', (230, 210, 180))
        shadow_surface = self.asset_manager.create_text_surface(move_text, 'regular', (0, 0, 0))

        # Draw with shadow effect
        x = self.width // 2 - text_surface.get_width() // 2
        self.screen.blit(shadow_surface, (x + 2, 47))
        self.screen.blit(text_surface, (x, 45))

    def _display_debug_info(self, board, game_state):
        """Display debug information when debug mode is enabled."""
        y_pos = 100
        line_height = 20

        debug_texts = [
            f"Game State: {game_state.get('state', 'UNKNOWN')}",
            f"Current Player: {game_state.get('current_player', 'UNKNOWN')}",
            f"Dice: {game_state.get('dice_values', [])} Used: {game_state.get('dice_used', [])}",
            f"Selected: {game_state.get('selected_point', 'None')}",
            f"FPS: {int(pygame.time.Clock().get_fps())}"
        ]

        for text in debug_texts:
            self._draw_text(text, (20, y_pos), 'small')
            y_pos += line_height

    def _draw_text(self, text, position, size='regular', color=(230, 210, 180), align="left"):
        """Draw text with a shadow effect.

        Args:
            text: The text to render
            position: (x, y) position tuple
            size: Font size ('small', 'regular', 'large')
            color: Text color as RGB tuple
            align: Text alignment ('left', 'center', 'right')
        """
        text_surface = self.asset_manager.create_text_surface(text, size, color)
        shadow_surface = self.asset_manager.create_text_surface(text, size, (0, 0, 0))

        x, y = position
        if align == "center":
            x -= text_surface.get_width() // 2
        elif align == "right":
            x -= text_surface.get_width()

        # Draw shadow first, then text
        self.screen.blit(shadow_surface, (x + 2, y + 2))
        self.screen.blit(text_surface, (x, y))

    def get_point_at_position(self, pos):
        """Convert screen position to board point.

        Args:
            pos: (x, y) tuple of screen coordinates

        Returns:
            int or None: The point number (0-27) at the given position, or None if no point
        """
        x, y = pos

        # Check bottom row (1-12)
        for point in range(1, 13):
            point_x, point_y = self.point_positions[point]
            base_x = point_x - self.point_width / 2

            # Check if in point bounds
            if (base_x <= x <= base_x + self.point_width and
                    point_y - self.board_height / 4 <= y <= point_y):
                return point

        # Check top row (13-24)
        for point in range(13, 25):
            point_x, point_y = self.point_positions[point]
            base_x = point_x - self.point_width / 2

            # Check if in point bounds
            if (base_x <= x <= base_x + self.point_width and
                    point_y <= y <= point_y + self.board_height / 4):
                return point

        # Check bar (0, 25)
        bar_x = self.board_margin_x + self.board_width / 2 - self.bar_width / 2

        # Black bar (top)
        bar_y = self.board_margin_y
        if (bar_x <= x <= bar_x + self.bar_width and
                bar_y <= y <= bar_y + self.board_height / 2):
            return 0

        # White bar (bottom)
        bar_y = self.board_margin_y + self.board_height / 2
        if (bar_x <= x <= bar_x + self.bar_width and
                bar_y <= y <= bar_y + self.board_height):
            return 25

        # Check home (26, 27)
        # Black home
        if (self.board_margin_x - 20 <= x <= self.board_margin_x and
                self.board_margin_y <= y <= self.board_margin_y + self.board_height / 2):
            return 26

        # White home
        if (self.board_margin_x + self.board_width <= x <= self.board_margin_x + self.board_width + 20 and
                self.board_margin_y + self.board_height / 2 <= y <= self.board_margin_y + self.board_height):
            return 27

        # No point found
        return None

    def toggle_debug_mode(self):
        """Toggle the debug display mode."""
        self.debug_mode = not self.debug_mode