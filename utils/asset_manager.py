# utils/asset_manager.py - Centralized asset management

import os
import pygame
import sys


class AssetManager:
    """Handles loading and management of all game assets."""

    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of AssetManager exists."""
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the asset manager if not already initialized."""
        if self._initialized:
            return

        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()

        # Cache for loaded images
        self.images = {
            'board': {},
            'pieces': {},
            'dice': {},
            'ui': {},
        }

        # Set up the assets path
        self.assets_path = self._find_assets_path()
        print(f"Using assets path: {self.assets_path}")

        # Load fonts
        pygame.font.init()
        self.fonts = {
            'regular': pygame.font.SysFont('Arial', 20),
            'small': pygame.font.SysFont('Arial', 14),
            'large': pygame.font.SysFont('Arial', 30)
        }

        self._initialized = True

    def _find_assets_path(self):
        """Find the correct assets directory path."""
        # Check possible locations for the assets directory
        possible_paths = [
            'assets',  # Project root
            os.path.join(os.path.dirname(__file__), '..', 'assets'),  # Relative to utils
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets'),  # Absolute path
            'generators/assets',  # Legacy path
        ]

        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                return path

        # If no path found, create the assets directory in the standard location
        default_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
        os.makedirs(os.path.join(default_path, 'images'), exist_ok=True)
        print(f"Created new assets directory at: {default_path}")
        return default_path

    def load_image(self, category, name, transparent=False):
        """Load an image from assets or retrieve from cache.

        Args:
            category: Category of the image (board, pieces, dice, ui)
            name: Filename of the image
            transparent: Whether the image should have transparency

        Returns:
            pygame.Surface: The loaded image
        """
        # Check if already in cache
        if name in self.images[category]:
            return self.images[category][name]

        # Build the filepath
        filepath = os.path.join(self.assets_path, 'images', category, name)

        try:
            # Try to load the image
            image = pygame.image.load(filepath)

            if transparent:
                image = image.convert_alpha()
                if not image.get_alpha():
                    # If no alpha channel, use colorkey
                    colorkey = image.get_at((0, 0))
                    image.set_colorkey(colorkey, pygame.RLEACCEL)
            else:
                image = image.convert()

            # Store in cache
            self.images[category][name] = image
            return image
        except pygame.error as e:
            print(f"Error loading image: {filepath} - {e}")
            # Return a placeholder surface
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 255))  # Magenta for missing texture
            return placeholder

    def get_font(self, size='regular'):
        """Get a font by its size/name."""
        return self.fonts.get(size, self.fonts['regular'])

    def create_text_surface(self, text, font_size='regular', color=(255, 255, 255)):
        """Create a text surface with the given parameters."""
        font = self.get_font(font_size)
        return font.render(text, True, color)


# Convenience function to get the AssetManager instance
def get_asset_manager():
    """Get the global AssetManager instance."""
    return AssetManager()