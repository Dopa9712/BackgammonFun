#!/usr/bin/env python3
# simple_piece_generator.py - Generates basic backgammon board and pieces

import pygame
import os
import sys


def generate_assets(width=1024, height=768, piece_size=40):
    """Generate basic backgammon board and piece images."""
    # Initialize pygame
    pygame.init()

    # Create asset directory if it doesn't exist
    if not os.path.exists('assets'):
        os.makedirs('assets')
    if not os.path.exists('assets/images'):
        os.makedirs('assets/images')

    # Generate the board
    generate_board(width, height)

    # Generate simple pieces
    generate_simple_pieces(piece_size)

    # Clean up
    pygame.quit()

    print("All assets have been generated successfully!")


def generate_board(width, height):
    """Generate a backgammon board image."""
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
    pygame.image.save(board_surface, 'assets/images/backgammon_board.png')
    print(f"Board image saved to assets/images/backgammon_board.png ({width}x{height})")


def generate_simple_pieces(size=40):
    """Generate a single white and black checker piece."""
    # Create surfaces for the pieces
    white_piece = pygame.Surface((size, size), pygame.SRCALPHA)
    black_piece = pygame.Surface((size, size), pygame.SRCALPHA)

    # Draw pieces with anti-aliasing if possible
    center = size // 2
    radius = (size // 2) - 1

    # White piece
    pygame.draw.circle(white_piece, (255, 255, 255), (center, center), radius)
    pygame.draw.circle(white_piece, (0, 0, 0), (center, center), radius, 2)
    # Inner shadow for 3D effect
    pygame.draw.circle(white_piece, (220, 220, 220), (center - 2, center - 2), radius - 4)

    # Black piece
    pygame.draw.circle(black_piece, (0, 0, 0), (center, center), radius)
    pygame.draw.circle(black_piece, (50, 50, 50), (center, center), radius, 2)
    # Inner highlight for 3D effect
    pygame.draw.circle(black_piece, (40, 40, 40), (center - 2, center - 2), radius - 4)

    # Save pieces
    pygame.image.save(white_piece, 'assets/images/white_piece.png')
    pygame.image.save(black_piece, 'assets/images/black_piece.png')

    print(f"Piece images saved to assets/images/ (size: {size}x{size})")


if __name__ == "__main__":
    # Use command-line arguments for dimensions if provided
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 768
    piece_size = int(sys.argv[3]) if len(sys.argv) > 3 else 40

    generate_assets(width, height, piece_size)