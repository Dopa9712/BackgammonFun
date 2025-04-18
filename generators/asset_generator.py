#!/usr/bin/env python3
# asset_generator.py - Generates all visual assets for the backgammon game

import pygame
import os
import sys


def generate_all_assets(width=1024, height=768):
    """Generate all assets for the backgammon game."""
    # Initialize pygame
    pygame.init()

    # Create asset directory structure
    create_directories()

    # Generate board
    generate_board(width, height)

    # Generate pieces
    generate_pieces()

    # Generate dice
    generate_dice()

    # Generate highlight overlays
    generate_highlights(width, height)

    # Clean up
    pygame.quit()

    print("All assets have been generated successfully!")


def create_directories():
    """Create the necessary directory structure for assets."""
    directories = [
        'assets',
        'assets/images',
        'assets/images/board',
        'assets/images/pieces',
        'assets/images/dice',
        'assets/images/ui'
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")


def generate_board(width, height):
    """Generate the backgammon board image."""
    # Create a surface for the board
    board_surface = pygame.Surface((width, height))

    # Define colors
    BACKGROUND_COLOR = (34, 139, 34)  # Dark green background
    BOARD_COLOR = (210, 180, 140)  # Tan for the board
    BROWN_POINT_COLOR = (139, 69, 19)  # Brown for points
    GREEN_POINT_COLOR = (0, 100, 0)  # Green for points
    BAR_COLOR = (180, 140, 100)  # Light brown for the bar
    TEXT_COLOR = (255, 255, 255)  # White text
    BORDER_COLOR = (0, 0, 0)  # Black for borders

    # Define board dimensions
    board_margin_x = 50
    board_margin_y = 70  # Top margin for game info
    board_width = width - 2 * board_margin_x
    board_height = height - 2 * board_margin_y

    # Define quadrant dimensions
    quadrant_width = board_width / 2 - 15  # Half board width minus half bar width
    quadrant_height = board_height / 2
    point_width = quadrant_width / 6  # 6 points per quadrant
    bar_width = 30

    # Fill the background
    board_surface.fill(BACKGROUND_COLOR)

    # Draw the main board
    board_rect = pygame.Rect(
        board_margin_x, board_margin_y, board_width, board_height
    )
    pygame.draw.rect(board_surface, BOARD_COLOR, board_rect)
    pygame.draw.rect(board_surface, BORDER_COLOR, board_rect, 2)

    # Draw the horizontal divider
    pygame.draw.line(
        board_surface,
        BORDER_COLOR,
        (board_margin_x, board_margin_y + board_height / 2),
        (board_margin_x + board_width, board_margin_y + board_height / 2),
        2
    )

    # Draw the bar (center divider)
    bar_rect = pygame.Rect(
        board_margin_x + board_width / 2 - bar_width / 2,
        board_margin_y,
        bar_width,
        board_height
    )
    pygame.draw.rect(board_surface, BAR_COLOR, bar_rect)
    pygame.draw.rect(board_surface, BORDER_COLOR, bar_rect, 2)

    # Load fonts
    font = pygame.font.SysFont('Arial', 20)
    small_font = pygame.font.SysFont('Arial', 14)

    # Draw small home indicators
    home_width = 20

    # White home (bottom left)
    white_home_rect = pygame.Rect(
        board_margin_x - home_width,
        board_margin_y + board_height / 2,
        home_width,
        board_height / 2
    )
    pygame.draw.rect(board_surface, BOARD_COLOR, white_home_rect)
    pygame.draw.rect(board_surface, BORDER_COLOR, white_home_rect, 2)

    # Black home (top right)
    black_home_rect = pygame.Rect(
        board_margin_x + board_width,
        board_margin_y,
        home_width,
        board_height / 2
    )
    pygame.draw.rect(board_surface, BOARD_COLOR, black_home_rect)
    pygame.draw.rect(board_surface, BORDER_COLOR, black_home_rect, 2)

    # Add home labels
    white_home_text = small_font.render("White Home", True, TEXT_COLOR)
    black_home_text = small_font.render("Black Home", True, TEXT_COLOR)

    # Rotate and position text
    white_text_rotated = pygame.transform.rotate(white_home_text, 90)
    board_surface.blit(
        white_text_rotated,
        (white_home_rect.x + (white_home_rect.width - white_text_rotated.get_width()) // 2,
         white_home_rect.y + 10)
    )

    black_text_rotated = pygame.transform.rotate(black_home_text, 90)
    board_surface.blit(
        black_text_rotated,
        (black_home_rect.x + (black_home_rect.width - black_text_rotated.get_width()) // 2,
         black_home_rect.y + 10)
    )

    # Draw the points
    # Bar midpoint (for reference)
    bar_mid_x = board_margin_x + board_width / 2

    # Bottom right quadrant (points 1-6) - 1 is rightmost
    for i in range(1, 7):
        x = bar_mid_x + (6 - i) * point_width + bar_width / 2
        y = board_margin_y + board_height

        # Alternate colors
        color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

        # Draw triangle pointing up
        triangle_height = quadrant_height - 10
        points = [
            (x, y),
            (x + point_width, y),
            (x + point_width / 2, y - triangle_height)
        ]
        pygame.draw.polygon(board_surface, color, points)
        pygame.draw.polygon(board_surface, BORDER_COLOR, points, 1)

        # Draw point number
        text = small_font.render(str(i), True, TEXT_COLOR)
        board_surface.blit(text, (x + point_width / 2 - text.get_width() / 2, y - 20))

    # Bottom left quadrant (points 7-12) - 7 is rightmost
    for i in range(7, 13):
        x = board_margin_x + (12 - i) * point_width
        y = board_margin_y + board_height

        # Alternate colors
        color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

        # Draw triangle pointing up
        triangle_height = quadrant_height - 10
        points = [
            (x, y),
            (x + point_width, y),
            (x + point_width / 2, y - triangle_height)
        ]
        pygame.draw.polygon(board_surface, color, points)
        pygame.draw.polygon(board_surface, BORDER_COLOR, points, 1)

        # Draw point number
        text = small_font.render(str(i), True, TEXT_COLOR)
        board_surface.blit(text, (x + point_width / 2 - text.get_width() / 2, y - 20))

    # Top left quadrant (points 13-18) - 13 is leftmost
    for i in range(13, 19):
        x = board_margin_x + (i - 13) * point_width
        y = board_margin_y

        # Alternate colors
        color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

        # Draw triangle pointing down
        triangle_height = quadrant_height - 10
        points = [
            (x, y),
            (x + point_width, y),
            (x + point_width / 2, y + triangle_height)
        ]
        pygame.draw.polygon(board_surface, color, points)
        pygame.draw.polygon(board_surface, BORDER_COLOR, points, 1)

        # Draw point number
        text = small_font.render(str(i), True, TEXT_COLOR)
        board_surface.blit(text, (x + point_width / 2 - text.get_width() / 2, y + 5))

    # Top right quadrant (points 19-24) - 24 is rightmost
    for i in range(19, 25):
        x = bar_mid_x + (i - 19) * point_width + bar_width / 2
        y = board_margin_y

        # Alternate colors
        color = GREEN_POINT_COLOR if i % 2 == 0 else BROWN_POINT_COLOR

        # Draw triangle pointing down
        triangle_height = quadrant_height - 10
        points = [
            (x, y),
            (x + point_width, y),
            (x + point_width / 2, y + triangle_height)
        ]
        pygame.draw.polygon(board_surface, color, points)
        pygame.draw.polygon(board_surface, BORDER_COLOR, points, 1)

        # Draw point number
        text = small_font.render(str(i), True, TEXT_COLOR)
        board_surface.blit(text, (x + point_width / 2 - text.get_width() / 2, y + 5))

    # Save the board image
    pygame.image.save(board_surface, 'assets/images/board/backgammon_board.png')

    # Also save the info area background
    info_bg = pygame.Surface((width, board_margin_y - 10))
    info_bg.fill((50, 100, 50))  # Dark green for info area
    pygame.image.save(info_bg, 'assets/images/ui/info_bg.png')

    print(f"Board images saved to assets/images/board/ ({width}x{height})")


def generate_pieces():
    """Generate piece images in different sizes."""
    sizes = [32, 40, 48]

    for size in sizes:
        # White piece
        white_piece = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        radius = (size // 2) - 1

        # Main circle
        pygame.draw.circle(white_piece, (255, 255, 255), (center, center), radius)
        # Border
        pygame.draw.circle(white_piece, (0, 0, 0), (center, center), radius, 2)
        # Inner shadow for 3D effect
        pygame.draw.circle(white_piece, (220, 220, 220), (center - 2, center - 2), radius - 4)

        # Save white piece
        pygame.image.save(white_piece, f'assets/images/pieces/white_piece_{size}.png')

        # Black piece
        black_piece = pygame.Surface((size, size), pygame.SRCALPHA)

        # Main circle
        pygame.draw.circle(black_piece, (0, 0, 0), (center, center), radius)
        # Border
        pygame.draw.circle(black_piece, (50, 50, 50), (center, center), radius, 2)
        # Inner highlight for 3D effect
        pygame.draw.circle(black_piece, (40, 40, 40), (center - 2, center - 2), radius - 4)

        # Save black piece
        pygame.image.save(black_piece, f'assets/images/pieces/black_piece_{size}.png')

    print(f"Piece images saved in multiple sizes to assets/images/pieces/")


def generate_dice():
    """Generate dice images for all values."""
    sizes = [40, 48]

    for size in sizes:
        for value in range(1, 7):
            # Create a die surface
            die = pygame.Surface((size, size), pygame.SRCALPHA)

            # Draw die body
            die_rect = pygame.Rect(0, 0, size, size)
            pygame.draw.rect(die, (255, 255, 255), die_rect, 0, size // 8)  # Rounded corners
            pygame.draw.rect(die, (0, 0, 0), die_rect, 2, size // 8)  # Border

            # Draw pips based on value
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

            # Save die image
            pygame.image.save(die, f'assets/images/dice/die_{value}_{size}.png')

            # Also generate a "used" (grayed out) version
            used_die = die.copy()
            gray_overlay = pygame.Surface((size, size), pygame.SRCALPHA)
            gray_overlay.fill((128, 128, 128, 128))  # Semi-transparent gray
            used_die.blit(gray_overlay, (0, 0))
            pygame.image.save(used_die, f'assets/images/dice/die_{value}_used_{size}.png')

    print(f"Dice images saved in multiple sizes to assets/images/dice/")


def generate_highlights(width, height):
    """Generate highlight overlays for points and bar."""
    # Board dimensions (same as in generate_board)
    board_margin_x = 50
    board_margin_y = 70
    board_width = width - 2 * board_margin_x
    board_height = height - 2 * board_margin_y
    quadrant_width = board_width / 2 - 15
    point_width = quadrant_width / 6
    bar_width = 30

    # Generate triangle highlight for bottom points (pointing up)
    bottom_highlight = pygame.Surface((int(point_width), int(board_height / 4)), pygame.SRCALPHA)
    triangle_height = int(board_height / 4 - 10)
    points = [
        (0, 0),
        (int(point_width), 0),
        (int(point_width / 2), -triangle_height)
    ]
    pygame.draw.polygon(bottom_highlight, (255, 255, 0, 128), points)
    pygame.image.save(bottom_highlight, 'assets/images/ui/bottom_highlight.png')

    # Generate triangle highlight for top points (pointing down)
    top_highlight = pygame.Surface((int(point_width), int(board_height / 4)), pygame.SRCALPHA)
    points = [
        (0, 0),
        (int(point_width), 0),
        (int(point_width / 2), triangle_height)
    ]
    pygame.draw.polygon(top_highlight, (255, 255, 0, 128), points)
    pygame.image.save(top_highlight, 'assets/images/ui/top_highlight.png')

    # Generate bar highlight
    bar_highlight = pygame.Surface((bar_width, int(board_height / 4)), pygame.SRCALPHA)
    bar_highlight.fill((255, 255, 0, 128))
    pygame.image.save(bar_highlight, 'assets/images/ui/bar_highlight.png')

    print("Highlight overlays saved to assets/images/ui/")


if __name__ == "__main__":
    # Use command-line arguments for dimensions if provided
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 768

    generate_all_assets(width, height)