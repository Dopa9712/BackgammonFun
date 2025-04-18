#!/usr/bin/env python3
# asset_creator.py - Creates ALL visual assets for the backgammon game

import pygame
import os
import sys


def create_all_assets(width=1024, height=768):
    """Create all visual assets for the game."""
    # Initialize pygame
    pygame.init()

    # Create asset directory structure
    create_directories()

    # Board dimensions parameters
    board_margin_x = 50
    board_margin_y = 70
    board_width = width - 2 * board_margin_x
    board_height = height - 2 * board_margin_y
    point_width = (board_width / 2 - 15) / 6
    bar_width = 30

    # Create the main board
    create_board(width, height, board_margin_x, board_margin_y, board_width, board_height, point_width, bar_width)

    # Create UI elements
    create_ui_elements(width, height, board_margin_y)

    # Create pieces
    create_pieces()

    # Create dice
    create_dice()

    # Create highlighted points
    create_highlight_overlays(point_width, board_height)

    # Create state text images
    create_text_elements()

    # Clean up
    pygame.quit()

    print("All assets have been created successfully!")


def create_directories():
    """Create directory structure for assets."""
    directories = [
        'assets',
        'assets/images',
        'assets/images/board',
        'assets/images/pieces',
        'assets/images/dice',
        'assets/images/ui',
        'assets/images/text'
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")


def create_board(width, height, margin_x, margin_y, board_width, board_height, point_width, bar_width):
    """Create board image."""
    # Colors
    BACKGROUND_COLOR = (34, 139, 34)  # Dark green
    BOARD_COLOR = (210, 180, 140)  # Tan
    BROWN_POINT_COLOR = (139, 69, 19)  # Brown points
    GREEN_POINT_COLOR = (0, 100, 0)  # Green points
    BAR_COLOR = (180, 140, 100)  # Light brown bar
    TEXT_COLOR = (255, 255, 255)  # White text
    BORDER_COLOR = (0, 0, 0)  # Black border

    # Create board surface
    board = pygame.Surface((width, height))
    board.fill(BACKGROUND_COLOR)

    # Draw main board
    board_rect = pygame.Rect(margin_x, margin_y, board_width, board_height)
    pygame.draw.rect(board, BOARD_COLOR, board_rect)
    pygame.draw.rect(board, BORDER_COLOR, board_rect, 2)

    # Draw horizontal divider
    pygame.draw.line(board, BORDER_COLOR,
                     (margin_x, margin_y + board_height / 2),
                     (margin_x + board_width, margin_y + board_height / 2), 2)

    # Draw bar
    bar_rect = pygame.Rect(
        margin_x + board_width / 2 - bar_width / 2,
        margin_y,
        bar_width,
        board_height
    )
    pygame.draw.rect(board, BAR_COLOR, bar_rect)
    pygame.draw.rect(board, BORDER_COLOR, bar_rect, 2)

    # Load font
    font = pygame.font.SysFont('Arial', 14)

    # Draw home areas
    home_width = 20

    # White home (bottom left)
    white_home_rect = pygame.Rect(
        margin_x - home_width,
        margin_y + board_height / 2,
        home_width,
        board_height / 2
    )
    pygame.draw.rect(board, BOARD_COLOR, white_home_rect)
    pygame.draw.rect(board, BORDER_COLOR, white_home_rect, 2)

    # Black home (top right)
    black_home_rect = pygame.Rect(
        margin_x + board_width,
        margin_y,
        home_width,
        board_height / 2
    )
    pygame.draw.rect(board, BOARD_COLOR, black_home_rect)
    pygame.draw.rect(board, BORDER_COLOR, black_home_rect, 2)

    # Add home labels
    white_text = font.render("White Home", True, TEXT_COLOR)
    black_text = font.render("Black Home", True, TEXT_COLOR)

    white_rotated = pygame.transform.rotate(white_text, 90)
    black_rotated = pygame.transform.rotate(black_text, 90)

    board.blit(white_rotated,
               (white_home_rect.x + (white_home_rect.width - white_rotated.get_width()) // 2,
                white_home_rect.y + 10))

    board.blit(black_rotated,
               (black_home_rect.x + (black_home_rect.width - black_rotated.get_width()) // 2,
                black_home_rect.y + 10))

    # Draw points
    quadrant_height = board_height / 2
    bar_mid_x = margin_x + board_width / 2

    # Bottom right quadrant (points 1-6)
    for i in range(1, 7):
        x = bar_mid_x + (6 - i) * point_width + bar_width / 2
        y = margin_y + board_height

        color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

        # Triangle pointing up
        triangle_height = quadrant_height - 10
        points = [
            (x, y),
            (x + point_width, y),
            (x + point_width / 2, y - triangle_height)
        ]
        pygame.draw.polygon(board, color, points)
        pygame.draw.polygon(board, BORDER_COLOR, points, 1)

        # Point number
        num = font.render(str(i), True, TEXT_COLOR)
        board.blit(num, (x + point_width / 2 - num.get_width() / 2, y - 20))

    # Bottom left quadrant (points 7-12)
    for i in range(7, 13):
        x = margin_x + (12 - i) * point_width
        y = margin_y + board_height

        color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

        # Triangle pointing up
        triangle_height = quadrant_height - 10
        points = [
            (x, y),
            (x + point_width, y),
            (x + point_width / 2, y - triangle_height)
        ]
        pygame.draw.polygon(board, color, points)
        pygame.draw.polygon(board, BORDER_COLOR, points, 1)

        # Point number
        num = font.render(str(i), True, TEXT_COLOR)
        board.blit(num, (x + point_width / 2 - num.get_width() / 2, y - 20))

    # Top left quadrant (points 13-18)
    for i in range(13, 19):
        x = margin_x + (i - 13) * point_width
        y = margin_y

        color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

        # Triangle pointing down
        triangle_height = quadrant_height - 10
        points = [
            (x, y),
            (x + point_width, y),
            (x + point_width / 2, y + triangle_height)
        ]
        pygame.draw.polygon(board, color, points)
        pygame.draw.polygon(board, BORDER_COLOR, points, 1)

        # Point number
        num = font.render(str(i), True, TEXT_COLOR)
        board.blit(num, (x + point_width / 2 - num.get_width() / 2, y + 5))

    # Top right quadrant (points 19-24)
    for i in range(19, 25):
        x = bar_mid_x + (i - 19) * point_width + bar_width / 2
        y = margin_y

        color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

        # Triangle pointing down
        triangle_height = quadrant_height - 10
        points = [
            (x, y),
            (x + point_width, y),
            (x + point_width / 2, y + triangle_height)
        ]
        pygame.draw.polygon(board, color, points)
        pygame.draw.polygon(board, BORDER_COLOR, points, 1)

        # Point number
        num = font.render(str(i), True, TEXT_COLOR)
        board.blit(num, (x + point_width / 2 - num.get_width() / 2, y + 5))

    # Save the board
    pygame.image.save(board, 'assets/images/board/board.png')
    print(f"Board image saved ({width}x{height})")


def create_ui_elements(width, height, margin_y):
    """Create UI elements like info panel and button backgrounds."""
    # Info panel background
    info_bg = pygame.Surface((width, margin_y - 10))
    info_bg.fill((50, 100, 50))  # Dark green
    pygame.image.save(info_bg, 'assets/images/ui/info_bg.png')

    # Button background (normal)
    button_bg = pygame.Surface((120, 40))
    button_bg.fill((80, 120, 80))  # Medium green
    pygame.draw.rect(button_bg, (255, 255, 255), button_bg.get_rect(), 2)
    pygame.image.save(button_bg, 'assets/images/ui/button_normal.png')

    # Button background (highlighted)
    button_highlight = pygame.Surface((120, 40))
    button_highlight.fill((100, 150, 100))  # Lighter green
    pygame.draw.rect(button_highlight, (255, 255, 0), button_highlight.get_rect(), 2)
    pygame.image.save(button_highlight, 'assets/images/ui/button_highlight.png')

    print("UI elements saved")


def create_pieces():
    """Create checker pieces in different sizes."""
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

        pygame.image.save(white, f'assets/images/pieces/white_{size}.png')

        # Black piece
        black = pygame.Surface((size, size), pygame.SRCALPHA)

        # Main circle
        pygame.draw.circle(black, (0, 0, 0), (center, center), radius)
        # Border
        pygame.draw.circle(black, (50, 50, 50), (center, center), radius, 2)
        # Inner highlight for 3D effect
        pygame.draw.circle(black, (40, 40, 40), (center - 2, center - 2), radius - 4)

        pygame.image.save(black, f'assets/images/pieces/black_{size}.png')

    print("Piece images saved in multiple sizes")


def create_dice():
    """Create dice images for all values and states."""
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
            pygame.image.save(die, f'assets/images/dice/die_{value}_{size}.png')

            # Create used (grayed out) version
            used_die = die.copy()
            overlay = pygame.Surface((size, size), pygame.SRCALPHA)
            overlay.fill((128, 128, 128, 128))  # Semi-transparent gray
            used_die.blit(overlay, (0, 0))
            pygame.image.save(used_die, f'assets/images/dice/die_{value}_used_{size}.png')

    print("Dice images saved in multiple sizes")


def create_highlight_overlays(point_width, board_height):
    """Create highlight overlays for points and bar."""
    # Convert parameters to integers for surface creation
    point_width = int(point_width)
    quad_height = int(board_height / 4)

    # Bottom points highlight (pointing up)
    bottom = pygame.Surface((point_width, quad_height), pygame.SRCALPHA)
    points = [
        (0, 0),
        (point_width, 0),
        (point_width / 2, -quad_height + 10)
    ]
    pygame.draw.polygon(bottom, (255, 255, 0, 128), points)
    pygame.image.save(bottom, 'assets/images/ui/bottom_highlight.png')

    # Top points highlight (pointing down)
    top = pygame.Surface((point_width, quad_height), pygame.SRCALPHA)
    points = [
        (0, 0),
        (point_width, 0),
        (point_width / 2, quad_height - 10)
    ]
    pygame.draw.polygon(top, (255, 255, 0, 128), points)
    pygame.image.save(top, 'assets/images/ui/top_highlight.png')

    # Bar highlight
    bar_width = 30
    bar_highlight = pygame.Surface((bar_width, quad_height), pygame.SRCALPHA)
    bar_highlight.fill((255, 255, 0, 128))
    pygame.image.save(bar_highlight, 'assets/images/ui/bar_highlight.png')

    # Home highlight
    home_width = 20
    home_highlight = pygame.Surface((home_width, quad_height * 2), pygame.SRCALPHA)
    home_highlight.fill((255, 255, 0, 128))
    pygame.image.save(home_highlight, 'assets/images/ui/home_highlight.png')

    print("Highlight overlays saved")


def create_text_elements():
    """Create text elements for common game states."""
    font = pygame.font.SysFont('Arial', 20)
    small_font = pygame.font.SysFont('Arial', 16)

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
        text_surface = font.render(text, True, (255, 255, 255))
        pygame.image.save(text_surface, f'assets/images/text/{name}.png')

    # Create number overlays for piece counts (1-15)
    for i in range(1, 16):
        count = small_font.render(str(i), True, (255, 255, 255))
        # Add background
        bg_surface = pygame.Surface((count.get_width() + 4, count.get_height() + 4), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        bg_surface.blit(count, (2, 2))
        pygame.image.save(bg_surface, f'assets/images/text/count_{i}.png')

    print("Text elements saved")


if __name__ == "__main__":
    # Use command-line arguments for dimensions if provided
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 768

    create_all_assets(width, height)