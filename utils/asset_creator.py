# utils/asset_creator.py - Elegant asset creation system

import pygame
import os
import sys
from datetime import datetime


class AssetCreator:
    """Creates elegant assets for the backgammon game."""

    def __init__(self, width=1024, height=768):
        """Initialize the asset creator with configurable dimensions."""
        self.width = width
        self.height = height

        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()

        # Board dimensions parameters
        self.board_margin_x = 50
        self.board_margin_y = 70
        self.board_width = width - 2 * self.board_margin_x
        self.board_height = height - 2 * self.board_margin_y
        self.point_width = (self.board_width / 2 - 20) / 6  # Slightly narrower for better appearance
        self.bar_width = 40  # Slightly wider bar

        # Color scheme - elegant dark wood and cream theme
        self.colors = {
            'background': (40, 26, 13),  # Dark wood
            'board': (82, 46, 24),  # Medium wood
            'point_dark': (49, 29, 16),  # Dark brown points
            'point_light': (230, 210, 180),  # Cream points
            'bar': (120, 81, 45),  # Lighter wood bar
            'text': (230, 210, 180),  # Cream text
            'border': (20, 12, 6),  # Nearly black border
            'white_piece': (230, 220, 210),  # Off-white pieces
            'black_piece': (40, 26, 13),  # Dark wood pieces
            'highlight': (230, 180, 80, 160),  # Golden highlight
            'button': (120, 81, 45),  # Medium wood buttons
            'button_highlight': (160, 120, 70)  # Lighter wood when highlighted
        }

        # Set up fonts
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 14)
        self.large_font = pygame.font.SysFont('Arial', 28)

    def create_all_assets(self):
        """Create all assets for the backgammon game."""
        # Create directory structure
        self._create_directories()

        # Create the board
        self._create_board()

        # Create UI elements
        self._create_ui_elements()

        # Create pieces
        self._create_pieces()

        # Create dice
        self._create_dice()

        # Create highlighted points
        self._create_highlight_overlays()

        # Create state text images
        self._create_text_elements()

        print(f"All assets created successfully at {datetime.now().strftime('%H:%M:%S')}")

    def _create_directories(self):
        """Create directory structure for assets."""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')

        directories = [
            '',
            'images',
            'images/board',
            'images/pieces',
            'images/dice',
            'images/ui',
            'images/text'
        ]

        for directory in directories:
            dir_path = os.path.join(base_dir, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created directory: {dir_path}")

    def _create_board(self):
        """Create an elegant wooden board image."""
        # Get colors
        BACKGROUND_COLOR = self.colors['background']
        BOARD_COLOR = self.colors['board']
        DARK_POINT_COLOR = self.colors['point_dark']
        LIGHT_POINT_COLOR = self.colors['point_light']
        BAR_COLOR = self.colors['bar']
        TEXT_COLOR = self.colors['text']
        BORDER_COLOR = self.colors['border']

        # Create board surface
        board = pygame.Surface((self.width, self.height))
        board.fill(BACKGROUND_COLOR)

        # Draw wooden texture for the board (simple pattern for now)
        self._draw_wood_texture(board,
                                pygame.Rect(self.board_margin_x, self.board_margin_y,
                                            self.board_width, self.board_height),
                                BOARD_COLOR)

        # Draw main board outline
        board_rect = pygame.Rect(self.board_margin_x, self.board_margin_y,
                                 self.board_width, self.board_height)
        pygame.draw.rect(board, BORDER_COLOR, board_rect, 2)

        # Draw horizontal divider
        pygame.draw.line(board, BORDER_COLOR,
                         (self.board_margin_x, self.board_margin_y + self.board_height / 2),
                         (self.board_margin_x + self.board_width, self.board_margin_y + self.board_height / 2), 2)

        # Draw bar
        bar_rect = pygame.Rect(
            self.board_margin_x + self.board_width / 2 - self.bar_width / 2,
            self.board_margin_y,
            self.bar_width,
            self.board_height
        )
        self._draw_wood_texture(board, bar_rect, BAR_COLOR)
        pygame.draw.rect(board, BORDER_COLOR, bar_rect, 2)

        # Draw home areas
        home_width = 20

        # White home (bottom left)
        white_home_rect = pygame.Rect(
            self.board_margin_x - home_width,
            self.board_margin_y + self.board_height / 2,
            home_width,
            self.board_height / 2
        )
        self._draw_wood_texture(board, white_home_rect, BOARD_COLOR)
        pygame.draw.rect(board, BORDER_COLOR, white_home_rect, 2)

        # Black home (top right)
        black_home_rect = pygame.Rect(
            self.board_margin_x + self.board_width,
            self.board_margin_y,
            home_width,
            self.board_height / 2
        )
        self._draw_wood_texture(board, black_home_rect, BOARD_COLOR)
        pygame.draw.rect(board, BORDER_COLOR, black_home_rect, 2)

        # Add home labels
        white_text = self.small_font.render("White Home", True, TEXT_COLOR)
        black_text = self.small_font.render("Black Home", True, TEXT_COLOR)

        white_rotated = pygame.transform.rotate(white_text, 90)
        black_rotated = pygame.transform.rotate(black_text, 90)

        board.blit(white_rotated,
                   (white_home_rect.x + (white_home_rect.width - white_rotated.get_width()) // 2,
                    white_home_rect.y + 10))

        board.blit(black_rotated,
                   (black_home_rect.x + (black_home_rect.width - black_rotated.get_width()) // 2,
                    black_home_rect.y + 10))

        # Draw points
        quadrant_height = self.board_height / 2
        bar_mid_x = self.board_margin_x + self.board_width / 2

        # Bottom right quadrant (points 1-6)
        for i in range(1, 7):
            x = bar_mid_x + (6 - i) * self.point_width + self.bar_width / 2
            y = self.board_margin_y + self.board_height

            color = LIGHT_POINT_COLOR if i % 2 == 0 else DARK_POINT_COLOR

            # Triangle pointing up
            triangle_height = quadrant_height - 10
            points = [
                (x, y),
                (x + self.point_width, y),
                (x + self.point_width / 2, y - triangle_height)
            ]
            pygame.draw.polygon(board, color, points)
            pygame.draw.polygon(board, BORDER_COLOR, points, 1)

            # Point number
            num = self.small_font.render(str(i), True, TEXT_COLOR)
            board.blit(num, (x + self.point_width / 2 - num.get_width() / 2, y - 20))

        # Bottom left quadrant (points 7-12)
        for i in range(7, 13):
            x = self.board_margin_x + (12 - i) * self.point_width
            y = self.board_margin_y + self.board_height

            color = LIGHT_POINT_COLOR if i % 2 == 0 else DARK_POINT_COLOR

            # Triangle pointing up
            triangle_height = quadrant_height - 10
            points = [
                (x, y),
                (x + self.point_width, y),
                (x + self.point_width / 2, y - triangle_height)
            ]
            pygame.draw.polygon(board, color, points)
            pygame.draw.polygon(board, BORDER_COLOR, points, 1)

            # Point number
            num = self.small_font.render(str(i), True, TEXT_COLOR)
            board.blit(num, (x + self.point_width / 2 - num.get_width() / 2, y - 20))

        # Top left quadrant (points 13-18)
        for i in range(13, 19):
            x = self.board_margin_x + (i - 13) * self.point_width
            y = self.board_margin_y

            color = LIGHT_POINT_COLOR if i % 2 == 0 else DARK_POINT_COLOR

            # Triangle pointing down
            triangle_height = quadrant_height - 10
            points = [
                (x, y),
                (x + self.point_width, y),
                (x + self.point_width / 2, y + triangle_height)
            ]
            pygame.draw.polygon(board, color, points)
            pygame.draw.polygon(board, BORDER_COLOR, points, 1)

            # Point number
            num = self.small_font.render(str(i), True, TEXT_COLOR)
            board.blit(num, (x + self.point_width / 2 - num.get_width() / 2, y + 5))

        # Top right quadrant (points 19-24)
        for i in range(19, 25):
            x = bar_mid_x + (i - 19) * self.point_width + self.bar_width / 2
            y = self.board_margin_y

            color = LIGHT_POINT_COLOR if i % 2 == 0 else DARK_POINT_COLOR

            # Triangle pointing down
            triangle_height = quadrant_height - 10
            points = [
                (x, y),
                (x + self.point_width, y),
                (x + self.point_width / 2, y + triangle_height)
            ]
            pygame.draw.polygon(board, color, points)
            pygame.draw.polygon(board, BORDER_COLOR, points, 1)

            # Point number
            num = self.small_font.render(str(i), True, TEXT_COLOR)
            board.blit(num, (x + self.point_width / 2 - num.get_width() / 2, y + 5))

        # Save the board
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
        pygame.image.save(board, os.path.join(base_dir, 'images', 'board', 'board.png'))
        print(f"Board image saved ({self.width}x{self.height})")

    def _draw_wood_texture(self, surface, rect, base_color):
        """Draw a simple wood grain texture effect."""
        # Fill with base color first
        pygame.draw.rect(surface, base_color, rect)

        r, g, b = base_color
        lighter = (min(r + 20, 255), min(g + 20, 255), min(b + 20, 255))
        darker = (max(r - 20, 0), max(g - 20, 0), max(b - 20, 0))

        # Add some grain lines - subtle variations
        grain_count = rect.height // 8  # Number of grain lines

        for i in range(grain_count):
            y_pos = rect.y + (i * 8)
            variation = 3 if i % 3 == 0 else 1
            color = lighter if i % 2 == 0 else darker

            line_rect = pygame.Rect(rect.x, y_pos, rect.width, variation)
            # Make the line semi-transparent
            s = pygame.Surface((line_rect.width, line_rect.height), pygame.SRCALPHA)
            s.fill((color[0], color[1], color[2], 40))  # Semi-transparent
            surface.blit(s, (line_rect.x, line_rect.y))

    def _create_ui_elements(self):
        """Create elegant UI elements like info panel and button backgrounds."""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')

        # Info panel background - dark wood texture
        info_bg = pygame.Surface((self.width, self.board_margin_y - 10))
        self._draw_wood_texture(info_bg, info_bg.get_rect(), self.colors['background'])
        pygame.image.save(info_bg, os.path.join(base_dir, 'images', 'ui', 'info_bg.png'))

        # Button background (normal)
        button_bg = pygame.Surface((120, 40))
        self._draw_wood_texture(button_bg, button_bg.get_rect(), self.colors['button'])
        pygame.draw.rect(button_bg, self.colors['border'], button_bg.get_rect(), 2)
        pygame.image.save(button_bg, os.path.join(base_dir, 'images', 'ui', 'button_normal.png'))

        # Button background (highlighted)
        button_highlight = pygame.Surface((120, 40))
        self._draw_wood_texture(button_highlight, button_highlight.get_rect(), self.colors['button_highlight'])
        pygame.draw.rect(button_highlight, self.colors['text'], button_highlight.get_rect(), 2)
        pygame.image.save(button_highlight, os.path.join(base_dir, 'images', 'ui', 'button_highlight.png'))

        print("UI elements saved")

    def _create_pieces(self):
        """Create elegant checker pieces in different sizes."""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
        sizes = [32, 40, 48]

        for size in sizes:
            # White piece
            white = pygame.Surface((size, size), pygame.SRCALPHA)
            center = size // 2
            radius = size // 2 - 1

            # Main circle with gradient effect
            for r in range(radius, 0, -1):
                # Create a gradient from center to edge
                factor = r / radius
                # Mix between white_piece and a slightly darker shade
                white_piece_color = self.colors['white_piece']
                r_val = max(white_piece_color[0] - int(30 * (1 - factor)), 0)
                g_val = max(white_piece_color[1] - int(30 * (1 - factor)), 0)
                b_val = max(white_piece_color[2] - int(30 * (1 - factor)), 0)
                pygame.draw.circle(white, (r_val, g_val, b_val), (center, center), r)

            # Border
            pygame.draw.circle(white, self.colors['border'], (center, center), radius, 2)

            # Inner highlight for 3D effect
            highlight_radius = radius - 4
            pygame.draw.circle(white, (255, 255, 255, 180), (center - 2, center - 2), highlight_radius // 2)

            pygame.image.save(white, os.path.join(base_dir, 'images', 'pieces', f'white_piece_{size}.png'))

            # Black piece
            black = pygame.Surface((size, size), pygame.SRCALPHA)

            # Main circle with gradient effect
            for r in range(radius, 0, -1):
                # Create a gradient from center to edge
                factor = r / radius
                # Mix between black_piece and a slightly darker shade
                black_piece_color = self.colors['black_piece']
                r_val = max(black_piece_color[0] - int(20 * (1 - factor)), 0)
                g_val = max(black_piece_color[1] - int(20 * (1 - factor)), 0)
                b_val = max(black_piece_color[2] - int(20 * (1 - factor)), 0)
                pygame.draw.circle(black, (r_val, g_val, b_val), (center, center), r)

            # Border
            pygame.draw.circle(black, self.colors['border'], (center, center), radius, 2)

            # Inner highlight for 3D effect
            pygame.draw.circle(black, (90, 60, 30, 180), (center - 2, center - 2), highlight_radius // 2)

            pygame.image.save(black, os.path.join(base_dir, 'images', 'pieces', f'black_piece_{size}.png'))

        print("Piece images saved in multiple sizes")

    def _create_dice(self):
        """Create elegant wooden dice images for all values and states."""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
        sizes = [40, 48]

        for size in sizes:
            for value in range(1, 7):
                # Regular dice with wood effect
                die = pygame.Surface((size, size), pygame.SRCALPHA)

                # Die body - ivory color
                die_color = (230, 225, 200)  # Ivory
                die_rect = pygame.Rect(0, 0, size, size)
                pygame.draw.rect(die, die_color, die_rect, 0, size // 8)  # Rounded corners

                # Add subtle texture
                for y in range(0, size, 4):
                    color_var = (220, 215, 190) if y % 8 == 0 else (235, 230, 205)
                    line_rect = pygame.Rect(0, y, size, 2)
                    s = pygame.Surface((line_rect.width, line_rect.height), pygame.SRCALPHA)
                    s.fill((color_var[0], color_var[1], color_var[2], 40))
                    die.blit(s, (line_rect.x, line_rect.y))

                # Border
                pygame.draw.rect(die, self.colors['border'], die_rect, 2, size // 8)

                # Draw pips in dark brown
                dot_radius = size // 10
                center = size // 2
                offset = size // 3
                pip_color = (40, 26, 13)  # Dark brown pips

                if value == 1:
                    pygame.draw.circle(die, pip_color, (center, center), dot_radius)
                elif value == 2:
                    pygame.draw.circle(die, pip_color, (center - offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center + offset // 2, center + offset // 2), dot_radius)
                elif value == 3:
                    pygame.draw.circle(die, pip_color, (center, center), dot_radius)
                    pygame.draw.circle(die, pip_color, (center - offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center + offset // 2, center + offset // 2), dot_radius)
                elif value == 4:
                    pygame.draw.circle(die, pip_color, (center - offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center + offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center - offset // 2, center + offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center + offset // 2, center + offset // 2), dot_radius)
                elif value == 5:
                    pygame.draw.circle(die, pip_color, (center, center), dot_radius)
                    pygame.draw.circle(die, pip_color, (center - offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center + offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center - offset // 2, center + offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center + offset // 2, center + offset // 2), dot_radius)
                elif value == 6:
                    pygame.draw.circle(die, pip_color, (center - offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center - offset // 2, center), dot_radius)
                    pygame.draw.circle(die, pip_color, (center - offset // 2, center + offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center + offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, pip_color, (center + offset // 2, center), dot_radius)
                    pygame.draw.circle(die, pip_color, (center + offset // 2, center + offset // 2), dot_radius)

                # Add subtle 3D effect with highlights and shadows
                highlight = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.rect(highlight, (255, 255, 255, 40), (3, 3, size - 6, size // 4), 0, size // 10)
                die.blit(highlight, (0, 0))

                # Save regular die
                pygame.image.save(die, os.path.join(base_dir, 'images', 'dice', f'die_{value}_{size}.png'))

                # Create used (grayed out) version
                used_die = die.copy()
                overlay = pygame.Surface((size, size), pygame.SRCALPHA)
                overlay.fill((100, 100, 100, 128))  # Semi-transparent gray
                used_die.blit(overlay, (0, 0))
                pygame.image.save(used_die, os.path.join(base_dir, 'images', 'dice', f'die_{value}_used_{size}.png'))

        print("Dice images saved in multiple sizes")

    def _create_highlight_overlays(self):
        """Create elegant highlight overlays for points and bar."""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')

        # Convert parameters to integers for surface creation
        point_width = int(self.point_width)
        quad_height = int(self.board_height / 4)

        # Bottom points highlight (pointing up)
        bottom = pygame.Surface((point_width, quad_height), pygame.SRCALPHA)
        points = [
            (0, 0),
            (point_width, 0),
            (point_width / 2, -quad_height + 10)
        ]
        pygame.draw.polygon(bottom, self.colors['highlight'], points)
        pygame.image.save(bottom, os.path.join(base_dir, 'images', 'ui', 'bottom_highlight.png'))

        # Top points highlight (pointing down)
        top = pygame.Surface((point_width, quad_height), pygame.SRCALPHA)
        points = [
            (0, 0),
            (point_width, 0),
            (point_width / 2, quad_height - 10)
        ]
        pygame.draw.polygon(top, self.colors['highlight'], points)
        pygame.image.save(top, os.path.join(base_dir, 'images', 'ui', 'top_highlight.png'))

        # Bar highlight
        bar_width = self.bar_width
        bar_highlight = pygame.Surface((bar_width, quad_height), pygame.SRCALPHA)
        bar_highlight.fill(self.colors['highlight'])
        pygame.image.save(bar_highlight, os.path.join(base_dir, 'images', 'ui', 'bar_highlight.png'))

        # Home highlight
        home_width = 20
        home_highlight = pygame.Surface((home_width, quad_height * 2), pygame.SRCALPHA)
        home_highlight.fill(self.colors['highlight'])
        pygame.image.save(home_highlight, os.path.join(base_dir, 'images', 'ui', 'home_highlight.png'))

        # Special last move highlight (blue tint)
        last_move = pygame.Surface((point_width, quad_height), pygame.SRCALPHA)
        last_move_color = (100, 150, 230, 128)  # Blue highlight
        pygame.draw.polygon(last_move, last_move_color, points)
        pygame.image.save(last_move, os.path.join(base_dir, 'images', 'ui', 'last_move_highlight.png'))

        print("Highlight overlays saved")

    def _create_text_elements(self):
        """Create elegant text elements for common game states."""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')

        # Game state texts
        states = {
            "roll_dice": "Click to roll dice",
            "select_point": "Select a point with your pieces",
            "select_dest": "Select destination point",
            "ai_thinking": "AI is thinking...",
            "white_turn": "White's turn",
            "black_turn": "Black's turn",
            "white_wins": "White wins! Click to play again.",
            "black_wins": "Black wins! Click to play again."
        }

        for name, text in states.items():
            # Create a fancier text surface with a subtle shadow
            text_color = self.colors['text']
            shadow_color = (0, 0, 0)

            # Create shadow first
            shadow_surface = self.font.render(text, True, shadow_color)

            # Create main text
            text_surface = self.font.render(text, True, text_color)

            # Combine them with offset
            combined = pygame.Surface((text_surface.get_width() + 2, text_surface.get_height() + 2), pygame.SRCALPHA)
            combined.blit(shadow_surface, (2, 2))  # Shadow position
            combined.blit(text_surface, (0, 0))  # Main text position

            pygame.image.save(combined, os.path.join(base_dir, 'images', 'text', f'{name}.png'))

        # Create number overlays for piece counts (1-15)
        for i in range(1, 16):
            count_color = self.colors['text']
            count = self.small_font.render(str(i), True, count_color)

            # Add background
            bg_surface = pygame.Surface((count.get_width() + 6, count.get_height() + 6), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black

            # Add a subtle border
            pygame.draw.rect(bg_surface, (180, 150, 80, 200), bg_surface.get_rect(), 1)

            bg_surface.blit(count, (3, 3))
            pygame.image.save(bg_surface, os.path.join(base_dir, 'images', 'text', f'count_{i}.png'))

        print("Text elements saved")


def create_assets(width=1024, height=768):
    """Convenience function to create all assets."""
    creator = AssetCreator(width, height)
    creator.create_all_assets()


if __name__ == "__main__":
    # Use command-line arguments for dimensions if provided
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 768

    create_assets(width, height)