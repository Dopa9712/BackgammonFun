# utils/game_utils.py - Utility functions for the backgammon game

import pygame
from utils.asset_manager import get_asset_manager


def create_button(text, font, position, size, bg_color, text_color, highlight_color=None):
    """Create a button.

    Args:
        text: The text for the button
        font: The pygame font object
        position: (x, y) tuple for position
        size: (width, height) tuple for size
        bg_color: Background color
        text_color: Text color
        highlight_color: Color when highlighted (None for no highlight)

    Returns:
        dict: A button object
    """
    x, y = position
    width, height = size

    button = {
        "rect": pygame.Rect(x, y, width, height),
        "text": text,
        "font": font,
        "bg_color": bg_color,
        "text_color": text_color,
        "highlight_color": highlight_color,
        "highlighted": False
    }

    return button


def draw_button(surface, button):
    """Draw a button on a surface.

    Args:
        surface: The surface to draw on
        button: The button object to draw
    """
    bg_color = button["highlight_color"] if button["highlighted"] and button["highlight_color"] else button["bg_color"]

    pygame.draw.rect(surface, bg_color, button["rect"])
    pygame.draw.rect(surface, (0, 0, 0), button["rect"], 2)  # Border

    # Center text on button
    text_surface = button["font"].render(button["text"], True, button["text_color"])
    text_rect = text_surface.get_rect()
    text_rect.center = button["rect"].center

    surface.blit(text_surface, text_rect)


def update_button_highlight(button, mouse_pos):
    """Update button highlighted state based on mouse position.

    Args:
        button: The button object
        mouse_pos: (x, y) tuple of mouse position

    Returns:
        bool: True if button is highlighted, False otherwise
    """
    button["highlighted"] = button["rect"].collidepoint(mouse_pos)
    return button["highlighted"]


def check_button_click(button, mouse_pos, mouse_click):
    """Check if a button was clicked.

    Args:
        button: The button object
        mouse_pos: (x, y) tuple of mouse position
        mouse_click: True if mouse was clicked

    Returns:
        bool: True if button was clicked, False otherwise
    """
    return button["rect"].collidepoint(mouse_pos) and mouse_click


def draw_text(surface, text, position, size="regular", color=(255, 255, 255), align="left"):
    """Draw text on a surface.

    Args:
        surface: The surface to draw on
        text: The text to display
        position: (x, y) tuple for position
        size: Font size ("small", "regular", "large")
        color: Text color
        align: Alignment ("left", "center", "right")
    """
    asset_manager = get_asset_manager()
    font = asset_manager.get_font(size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    x, y = position

    if align == "center":
        text_rect.centerx = x
        text_rect.y = y
    elif align == "right":
        text_rect.right = x
        text_rect.y = y
    else:  # left
        text_rect.x = x
        text_rect.y = y

    surface.blit(text_surface, text_rect)


def draw_centered_text(surface, text, y_position, size="regular", color=(255, 255, 255)):
    """Draw text centered horizontally on the surface.

    Args:
        surface: The surface to draw on
        text: The text to display
        y_position: Vertical position
        size: Font size ("small", "regular", "large")
        color: Text color
    """
    draw_text(surface, text, (surface.get_width() // 2, y_position), size, color, "center")


def draw_text_with_shadow(surface, text, position, size="regular", color=(255, 255, 255),
                          shadow_color=(0, 0, 0), offset=(2, 2), align="left"):
    """Draw text with a shadow effect.

    Args:
        surface: The surface to draw on
        text: The text to display
        position: (x, y) tuple for position
        size: Font size ("small", "regular", "large")
        color: Text color
        shadow_color: Shadow color
        offset: Shadow offset
        align: Alignment ("left", "center", "right")
    """
    asset_manager = get_asset_manager()
    font = asset_manager.get_font(size)

    # Create shadow and text surfaces
    shadow_surface = font.render(text, True, shadow_color)
    text_surface = font.render(text, True, color)

    # Set up rectangles for positioning
    shadow_rect = shadow_surface.get_rect()
    text_rect = text_surface.get_rect()

    x, y = position

    if align == "center":
        shadow_rect.centerx = x + offset[0]
        shadow_rect.y = y + offset[1]
        text_rect.centerx = x
        text_rect.y = y
    elif align == "right":
        shadow_rect.right = x + offset[0]
        shadow_rect.y = y + offset[1]
        text_rect.right = x
        text_rect.y = y
    else:  # left
        shadow_rect.x = x + offset[0]
        shadow_rect.y = y + offset[1]
        text_rect.x = x
        text_rect.y = y

    # Draw shadow first, then text
    surface.blit(shadow_surface, shadow_rect)
    surface.blit(text_surface, text_rect)


def draw_semi_transparent_overlay(surface, color, alpha, rect=None):
    """Draw a semi-transparent overlay on the surface.

    Args:
        surface: The surface to draw on
        color: Base color (r, g, b)
        alpha: Alpha value (0-255)
        rect: Rectangle to fill, or None for full surface
    """
    if rect is None:
        rect = surface.get_rect()

    overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    overlay.fill((*color, alpha))
    surface.blit(overlay, rect.topleft)


def create_navigation_controls(renderer, font, center_y, button_gap=20):
    """Create a set of navigation controls for review mode.

    Args:
        renderer: The renderer object
        font: Font to use for buttons
        center_y: Vertical center position for buttons
        button_gap: Gap between buttons

    Returns:
        dict: Dictionary of button objects
    """
    buttons = {}

    # Button styling
    button_width = 100
    button_height = 40
    bg_color = (120, 81, 45)  # Medium wood
    highlight_color = (160, 120, 70)  # Lighter wood when highlighted
    text_color = (230, 210, 180)  # Cream text

    # Calculate horizontal positions
    width = renderer.width
    center_x = width // 2
    button_x_positions = [
        center_x - (button_width * 2) - (button_gap * 2),  # First
        center_x - button_width - button_gap,  # Previous
        center_x + button_gap,  # Next
        center_x + button_width + (button_gap * 2)  # Last
    ]

    # Create buttons
    buttons["first"] = create_button("⏮ First", font,
                                     (button_x_positions[0], center_y - button_height // 2),
                                     (button_width, button_height),
                                     bg_color, text_color, highlight_color)

    buttons["prev"] = create_button("◀ Previous", font,
                                    (button_x_positions[1], center_y - button_height // 2),
                                    (button_width, button_height),
                                    bg_color, text_color, highlight_color)

    buttons["next"] = create_button("Next ▶", font,
                                    (button_x_positions[2], center_y - button_height // 2),
                                    (button_width, button_height),
                                    bg_color, text_color, highlight_color)

    buttons["last"] = create_button("Last ⏭", font,
                                    (button_x_positions[3], center_y - button_height // 2),
                                    (button_width, button_height),
                                    bg_color, text_color, highlight_color)

    # Add exit button
    buttons["exit"] = create_button("Exit Review", font,
                                    (center_x - 60, center_y + button_height),
                                    (120, 35),
                                    bg_color, text_color, highlight_color)

    return buttons