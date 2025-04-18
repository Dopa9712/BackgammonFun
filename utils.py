# utils.py - Utility functions for the backgammon game

import pygame


def load_image(filename, transparent=False):
    """Load an image from the assets folder.

    Args:
        filename: The filename of the image
        transparent: If True, set the colorkey to the top-left pixel

    Returns:
        pygame.Surface: The loaded image
    """
    try:
        image = pygame.image.load(f"generators/assets/images/{filename}")
    except pygame.error:
        print(f"Unable to load image: {filename}")
        return pygame.Surface((100, 100))

    if transparent:
        image = image.convert_alpha()
        if not image.get_alpha():
            # If image doesn't have alpha channel already
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
    else:
        image = image.convert()

    return image


def draw_text(surface, text, font, color, x, y, align="left"):
    """Draw text on a surface with alignment options.

    Args:
        surface: The surface to draw on
        text: The text to draw
        font: The pygame font object
        color: The color of the text
        x, y: The position to draw
        align: Alignment ("left", "center", "right")
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

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