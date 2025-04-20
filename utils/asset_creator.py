# utils/asset_creator.py - Unified asset creation system

import pygame
import os
import sys


class AssetCreator:
    """Handles creation of all game assets."""

    def __init__(self, width=1024, height=768):
        """Initialize the asset creator.

        Args:
            width: Width of the board
            height: Height of the board
        """
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
        self.point_width = (self.board_width / 2 - 15) / 6
        self.bar_width = 30

        # Set up fonts
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 14)

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

        print("All assets have been created successfully!")

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
        """Create the board image."""
        # Colors
        BACKGROUND_COLOR = (34, 139, 34)  # Dark green
        BOARD_COLOR = (210, 180, 140)  # Tan
        BROWN_POINT_COLOR = (139, 69, 19)  # Brown points
        GREEN_POINT_COLOR = (0, 100, 0)  # Green points
        BAR_COLOR = (180, 140, 100)  # Light brown bar
        TEXT_COLOR = (255, 255, 255)  # White text
        BORDER_COLOR = (0, 0, 0)  # Black border

        # Create board surface
        board = pygame.Surface((self.width, self.height))
        board.fill(BACKGROUND_COLOR)

        # Draw main board
        board_rect = pygame.Rect(self.board_margin_x, self.board_margin_y,
                                 self.board_width, self.board_height)
        pygame.draw.rect(board, BOARD_COLOR, board_rect)
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
        pygame.draw.rect(board, BAR_COLOR, bar_rect)
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
        pygame.draw.rect(board, BOARD_COLOR, white_home_rect)
        pygame.draw.rect(board, BORDER_COLOR, white_home_rect, 2)

        # Black home (top right)
        black_home_rect = pygame.Rect(
            self.board_margin_x + self.board_width,
            self.board_margin_y,
            home_width,
            self.board_height / 2
        )
        pygame.draw.rect(board, BOARD_COLOR, black_home_rect)
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

            color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

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

            color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

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

            color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

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

            color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

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

    def _create_ui_elements(self):
        """Create UI elements like info panel and button backgrounds."""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')

        # Info panel background
        info_bg = pygame.Surface((self.width, self.board_margin_y - 10))
        info_bg.fill((50, 100, 50))  # Dark green
        pygame.image.save(info_bg, os.path.join(base_dir, 'images', 'ui', 'info_bg.png'))

        # Button background (normal)
        button_bg = pygame.Surface((120, 40))
        button_bg.fill((80, 120, 80))  # Medium green
        pygame.draw.rect(button_bg, (255, 255, 255), button_bg.get_rect(), 2)
        pygame.image.save(button_bg, os.path.join(base_dir, 'images', 'ui', 'button_normal.png'))

        # Button background (highlighted)
        button_highlight = pygame.Surface((120, 40))
        button_highlight.fill((100, 150, 100))  # Lighter green
        pygame.draw.rect(button_highlight, (255, 255, 0), button_highlight.get_rect(), 2)
        pygame.image.save(button_highlight, os.path.join(base_dir, 'images', 'ui', 'button_highlight.png'))

        print("UI elements saved")

    def _create_pieces(self):
        """Create checker pieces in different sizes."""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
        sizes = [32, 40, 48]

        for size in sizes:
            # White piece
            white = pygame.Surface((size, size), pygame.SRCALPHA)
            center = size // 2
            radius = size // 2 - 1

            # Main circle
            pygame.draw.circle(white, (255, 255, 255), (center, center), radius)
            # Border
            pygame.draw.circle(white, (0, 0, 0), (center, center), radius, 2)
            # Inner shadow for 3D effect
            pygame.draw.circle(white, (220, 220, 220), (center - 2, center - 2), radius - 4)

            pygame.image.save(white, os.path.join(base_dir, 'images', 'pieces', f'white_piece_{size}.png'))

            # Black piece
            black = pygame.Surface((size, size), pygame.SRCALPHA)

            # Main circle
            pygame.draw.circle(black, (0, 0, 0), (center, center), radius)
            # Border
            pygame.draw.circle(black, (50, 50, 50), (center, center), radius, 2)
            # Inner highlight for 3D effect
            pygame.draw.circle(black, (40, 40, 40), (center - 2, center - 2), radius - 4)

            pygame.image.save(black, os.path.join(base_dir, 'images', 'pieces', f'black_piece_{size}.png'))

        print("Piece images saved in multiple sizes")

    def _create_dice(self):
        """Create dice images for all values and states."""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
        sizes = [40, 48]

        for size in sizes:
            for value in range(1, 7):
                # Regular dice
                die = pygame.Surface((size, size), pygame.SRCALPHA)

                # Die body
                die_rect = pygame.Rect(0, 0, size, size)
                pygame.draw.rect(die, (255, 255, 255), die_rect, 0, size // 8)  # Rounded corners
                pygame.draw.rect(die, (0, 0, 0), die_rect, 2, size // 8)  # Border

                # Draw pips
                dot_radius = size // 10
                center = size // 2
                offset = size // 3

                if value == 1:
                    pygame.draw.circle(die, (0, 0, 0), (center, center), dot_radius)
                elif value == 2:
                    pygame.draw.circle(die, (0, 0, 0), (center - offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center + offset // 2, center + offset // 2), dot_radius)
                elif value == 3:
                    pygame.draw.circle(die, (0, 0, 0), (center, center), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center - offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center + offset // 2, center + offset // 2), dot_radius)
                elif value == 4:
                    pygame.draw.circle(die, (0, 0, 0), (center - offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center + offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center - offset // 2, center + offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center + offset // 2, center + offset // 2), dot_radius)
                elif value == 5:
                    pygame.draw.circle(die, (0, 0, 0), (center, center), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center - offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center + offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center - offset // 2, center + offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center + offset // 2, center + offset // 2), dot_radius)
                elif value == 6:
                    pygame.draw.circle(die, (0, 0, 0), (center - offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center - offset // 2, center), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center - offset // 2, center + offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center + offset // 2, center - offset // 2), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center + offset // 2, center), dot_radius)
                    pygame.draw.circle(die, (0, 0, 0), (center + offset // 2, center + offset // 2), dot_radius)

                # Save regular die
                pygame.image.save(die, os.path.join(base_dir, 'images', 'dice', f'die_{value}_{size}.png'))

                # Create used (grayed out) version
                used_die = die.copy()
                overlay = pygame.Surface((size, size), pygame.SRCALPHA)
                overlay.fill((128, 128, 128, 128))  # Semi-transparent gray
                used_die.blit(overlay, (0, 0))
                pygame.image.save(used_die, os.path.join(base_dir, 'images', 'dice', f'die_{value}_used_{size}.png'))

        print("Dice images saved in multiple sizes")

    def _create_highlight_overlays(self):
        """Create highlight overlays for points and bar."""
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
        pygame.draw.polygon(bottom, (255, 255, 0, 128), points)
        pygame.image.save(bottom, os.path.join(base_dir, 'images', 'ui', 'bottom_highlight.png'))

        # Top points highlight (pointing down)
        top = pygame.Surface((point_width, quad_height), pygame.SRCALPHA)
        points = [
            (0, 0),
            (point_width, 0),
            (point_width / 2, quad_height - 10)
        ]
        pygame.draw.polygon(top, (255, 255, 0, 128), points)
        pygame.image.save(top, os.path.join(base_dir, 'images', 'ui', 'top_highlight.png'))

        # Bar highlight
        bar_width = 30
        bar_highlight = pygame.Surface((bar_width, quad_height), pygame.SRCALPHA)
        bar_highlight.fill((255, 255, 0, 128))
        pygame.image.save(bar_highlight, os.path.join(base_dir, 'images', 'ui', 'bar_highlight.png'))

        # Home highlight
        home_width = 20
        home_highlight = pygame.Surface((home_width, quad_height * 2), pygame.SRCALPHA)
        home_highlight.fill((255, 255, 0, 128))
        pygame.image.save(home_highlight, os.path.join(base_dir, 'images', 'ui', 'home_highlight.png'))

        # Special last move highlight (blue)
        last_move = pygame.Surface((point_width, quad_height), pygame.SRCALPHA)
        pygame.draw.polygon(last_move, (0, 100, 255, 128), points)  # Blue highlight
        pygame.image.save(last_move, os.path.join(base_dir, 'images', 'ui', 'last_move_highlight.png'))

        print("Highlight overlays saved")

    def _create_text_elements(self):
        """Create text elements for common game states."""
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
            text_surface = self.font.render(text, True, (255, 255, 255))
            pygame.image.save(text_surface, os.path.join(base_dir, 'images', 'text', f'{name}.png'))

        # Create number overlays for piece counts (1-15)
        for i in range(1, 16):
            count = self.small_font.render(str(i), True, (255, 255, 255))
            # Add background
            bg_surface = pygame.Surface((count.get_width() + 4, count.get_height() + 4), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            bg_surface.blit(count, (2, 2))
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