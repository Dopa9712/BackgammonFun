#!/usr/bin/env python3
# create_last_move_highlight.py - Create a highlight image for the last AI move in the correct generators/assets directory

import pygame
import os
import sys


def create_last_move_highlight():
    """Create a special highlight for displaying AI's last move."""
    # Find the correct assets directory
    assets_dir = find_assets_directory()
    ui_dir = os.path.join(assets_dir, 'images', 'ui')

    # Make sure UI directory exists
    if not os.path.exists(ui_dir):
        os.makedirs(ui_dir, exist_ok=True)

    # Initialize pygame
    pygame.init()

    # Create highlight for points - using a different color (blue) for last move
    point_width = 50  # Approximate width, adjust as needed
    triangle_height = 90  # Approximate height, adjust as needed

    # Create the highlight with transparency
    last_move_highlight = pygame.Surface((point_width, triangle_height), pygame.SRCALPHA)

    # Fill with a semi-transparent blue
    highlight_color = (0, 100, 255, 128)  # Blue with alpha

    # Create a triangle shape
    points = [
        (0, 0),
        (point_width, 0),
        (point_width // 2, -triangle_height + 10)
    ]
    pygame.draw.polygon(last_move_highlight, highlight_color, points)

    # Save the highlight
    output_path = os.path.join(ui_dir, 'last_move_highlight.png')
    pygame.image.save(last_move_highlight, output_path)
    print(f"Last move highlight saved to {output_path}")

    # Clean up
    pygame.quit()


def find_assets_directory():
    """Find the correct assets directory path."""
    # First, try the specific path mentioned by the user
    specific_path = 'generators/assets'
    if os.path.exists(specific_path):
        return specific_path

    # Check other possible paths
    possible_paths = [
        'assets',
        '../generators/assets',
        os.path.join(os.path.dirname(__file__), 'generators', 'assets'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generators', 'assets')
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # If no existing assets directory found, create the user-specified path
    print(f"Creating new assets directory at: {specific_path}")
    os.makedirs(os.path.join(specific_path, 'images', 'ui'), exist_ok=True)
    return specific_path


if __name__ == "__main__":
    create_last_move_highlight()