# renderer.py - Fixed version with correct method names

import pygame
import os
import sys


class Renderer:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

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

        # Determine the correct assets path
        self.assets_path = self._find_assets_path()
        print(f"Using assets path: {self.assets_path}")

        # Load fonts for backup text rendering
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 14)

        # Load all images - if any are missing, you should run asset_creator.py first
        self.images = self._load_images()

        # Calculate positions of all points (for piece placement only)
        self.point_positions = self._calculate_point_positions()

    def _find_assets_path(self):
        """Find the correct assets directory path by checking several possibilities."""
        # Check common possible paths
        possible_paths = [
            'generators/assets',  # Specific directory mentioned
            'assets',  # Current directory
            '../assets',  # Parent directory
            os.path.join(os.path.dirname(__file__), 'assets'),  # Same directory as this script
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')  # Absolute path to script dir
        ]

        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                # Check if this directory contains images subdirectory
                images_path = os.path.join(path, 'images')
                if os.path.exists(images_path) and os.path.isdir(images_path):
                    return path

        # If no existing assets directory found, default to the first option and warn
        print("WARNING: Could not find assets directory. Using 'generators/assets' as default.")
        return 'generators/assets'

    def _load_images(self):
        """Load all pre-generated images."""
        images = {
            # Main components
            'board': self._load_image('board/board.png'),
            'info_bg': self._load_image('ui/info_bg.png'),

            # Pieces
            'pieces': {
                'white': None,
                'black': None
            },

            # Dice
            'dice': {},

            # Highlights
            'highlights': {
                'top': self._load_image('ui/top_highlight.png'),
                'bottom': self._load_image('ui/bottom_highlight.png'),
                'bar': self._load_image('ui/bar_highlight.png'),
                'home': self._load_image('ui/home_highlight.png')
            },

            # Text elements
            'text': {}
        }

        # Load game state text images
        for name in ['roll_dice', 'select_point', 'select_dest', 'ai_thinking',
                     'white_turn', 'black_turn', 'white_wins', 'black_wins']:
            images['text'][name] = self._load_image(f'text/{name}.png')

        # Load count overlays
        for i in range(1, 16):
            images['text'][f'count_{i}'] = self._load_image(f'text/count_{i}.png')

        # Load pieces - try different sizes
        for size in [40, 32, 48]:
            # Try different possible naming conventions
            for filename_pattern in [f'pieces/white_{size}.png', f'pieces/white_piece_{size}.png']:
                white = self._load_image(filename_pattern)
                if white:
                    break

            for filename_pattern in [f'pieces/black_{size}.png', f'pieces/black_piece_{size}.png']:
                black = self._load_image(filename_pattern)
                if black:
                    break

            if white and black:
                images['pieces']['white'] = white
                images['pieces']['black'] = black
                self.piece_size = size
                break

        # Load dice - try different sizes
        for size in [40, 48]:
            all_found = True
            temp_dice = {}

            for value in range(1, 7):
                # Try different naming conventions
                for die_pattern in [f'dice/die_{value}_{size}.png', f'dice/die{value}_{size}.png']:
                    die = self._load_image(die_pattern)
                    if die:
                        temp_dice[value] = die
                        break

                if value not in temp_dice:
                    all_found = False
                    break

                # Used die versions
                for used_pattern in [f'dice/die_{value}_used_{size}.png', f'dice/die{value}_used_{size}.png']:
                    used_die = self._load_image(used_pattern)
                    if used_die:
                        temp_dice[f'{value}_used'] = used_die
                        break

                if f'{value}_used' not in temp_dice:
                    all_found = False
                    break

            if all_found:
                images['dice'] = temp_dice
                self.dice_size = size
                break

        return images

    def _load_image(self, path):
        """Load an image from the assets directory."""
        full_path = os.path.join(self.assets_path, 'images', path)

        # Print detailed info for debugging
        if not os.path.exists(full_path):
            print(f"Cannot find image: {full_path}")
            # List files in the parent directory to see what's available
            parent_dir = os.path.dirname(full_path)
            if os.path.exists(parent_dir):
                print(f"Files in {parent_dir}:")
                for file in os.listdir(parent_dir):
                    print(f"  - {file}")
            return None

        try:
            image = pygame.image.load(full_path)
            # Check if it's the board and needs scaling
            if 'board/board.png' in full_path:
                if image.get_width() != self.width or image.get_height() != self.height:
                    return pygame.transform.scale(image, (self.width, self.height))
            return image
        except pygame.error as e:
            print(f"Error loading image: {full_path} - {e}")
            return None

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
        """Render the game by blitting pre-generated images."""
        # Draw the board (or fallback to filling with color)
        if self.images['board']:
            self.screen.blit(self.images['board'], (0, 0))
        else:
            self.screen.fill((34, 139, 34))  # Dark green background fallback
            print("WARNING: Board image missing. Run asset_creator.py first.")
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
        last_move_highlight = self.images['highlights'].get('last_move')

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
            highlight = self.images['highlights'].get('bottom')
            if highlight:
                self.screen.blit(highlight, (int(x), int(y - self.board_height / 4)))

        elif 13 <= point <= 24:  # Top row
            highlight = self.images['highlights'].get('top')
            if highlight:
                self.screen.blit(highlight, (int(x), int(y)))

        elif point in (0, 25):  # Bar
            highlight = self.images['highlights'].get('bar')
            if highlight:
                bar_y = self.board_margin_y if point == 0 else self.board_margin_y + self.board_height / 2
                bar_x = self.board_margin_x + self.board_width / 2 - self.bar_width / 2
                self.screen.blit(highlight, (int(bar_x), int(bar_y)))

        elif point in (26, 27):  # Home
            highlight = self.images['highlights'].get('home')
            if highlight:
                home_x = self.board_margin_x - 20 if point == 26 else self.board_margin_x + self.board_width
                home_y = self.board_margin_y if point == 26 else self.board_margin_y + self.board_height / 2
                self.screen.blit(highlight, (int(home_x), int(home_y)))

    def _blit_pieces(self, board):
        """Blit pieces onto the board."""
        # Check if piece images are available
        white_piece = self.images['pieces']['white']
        black_piece = self.images['pieces']['black']

        if not white_piece or not black_piece:
            print("WARNING: Piece images missing. Run asset_creator.py first.")
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
                piece_img = white_piece if color == "White" else black_piece

                # Calculate exact position for blitting (centered on the calculated position)
                x_pos = int(x - piece_img.get_width() / 2)
                y_pos = int(y - piece_img.get_height() / 2)

                # Blit the piece
                self.screen.blit(piece_img, (x_pos, y_pos))

            # Show count if more pieces than visible
            if len(pieces) > max_pieces_visible:
                count_img = self.images['text'].get(f'count_{len(pieces)}')
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
                    # Just log the missing image
                    print(f"Missing count image for {len(pieces)} pieces")

    def _blit_dice(self, dice_values, dice_used):
        """Blit dice images."""
        if not dice_values:
            return

        # Check if we have at least some dice images
        if not self.images['dice']:
            print("WARNING: Dice images missing. Run asset_creator.py first.")
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

            die_img = self.images['dice'].get(die_key)
            if die_img:
                x_pos = int(start_x + i * (self.dice_size + dice_margin))
                y_pos = int(y_position - die_img.get_height() / 2)
                self.screen.blit(die_img, (x_pos, y_pos))
            else:
                print(f"Missing dice image for value {value}, key {die_key}")

    def _blit_game_info(self, game_state):
        """Blit game state information."""
        # Blit info background
        if self.images['info_bg']:
            self.screen.blit(self.images['info_bg'], (0, 0))

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
            text_img = self.images['text'].get(text_key)
            if text_img:  # Check if image was loaded
                self.screen.blit(text_img, (self.width - text_img.get_width() - 20, 20))
            else:
                # Missing text image - handle it with a non-drawing approach
                # Render text to console only
                print(f"Missing text image for: {text_key}")

        # Blit player turn text if available
        player_key = "white_turn" if game_state["current_player"] == "White" else "black_turn"
        if player_key in self.images['text']:
            player_img = self.images['text'].get(player_key)
            if player_img:  # Check if image was loaded
                self.screen.blit(player_img, (20, 20))
            else:
                # Missing text image - handle it with a non-drawing approach
                # Render text to console only
                print(f"Missing text image for: {player_key}")

    def _blit_last_move_info(self, last_moves):
        """Display AI's last move information on screen."""
        if not last_moves:
            return

        # Display last move information in text format at the top of the screen
        move_text = "AI's last move: "
        for i, (from_point, to_point) in enumerate(last_moves):
            if i > 0:
                move_text += ", "
            move_text += f"{from_point} → {to_point}"

        # Render using built-in font
        move_surface = self.font.render(move_text, True, (255, 255, 255))
        self.screen.blit(move_surface, (self.width // 2 - move_surface.get_width() // 2, 45))

    def get_point_at_position(self, pos):
        """Convert screen position to board point."""
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