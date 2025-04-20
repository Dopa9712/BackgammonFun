# model/player.py - Player classes for backgammon

__all__ = ['Player', 'HumanPlayer']


class Player:
    """Base class for backgammon players (human or AI)."""

    def __init__(self, color):
        """Initialize a player.

        Args:
            color: "White" or "Black" - the player's color
        """
        self.color = color

    def get_name(self):
        """Get the player's name.

        Returns:
            str: The player's name
        """
        return f"Player ({self.color})"

    def get_color(self):
        """Get the player's color.

        Returns:
            str: The player's color ("White" or "Black")
        """
        return self.color

    def choose_moves(self, board, dice_values):
        """Choose moves for the current dice roll.

        This method should be overridden by subclasses.

        Args:
            board: The game board
            dice_values: List of available dice values

        Returns:
            list: List of (from_point, to_point) tuples representing moves
        """
        raise NotImplementedError("Subclasses must implement choose_moves method")


class HumanPlayer(Player):
    """Human player for backgammon."""

    def __init__(self, color):
        """Initialize a human player.

        Args:
            color: "White" or "Black" - the player's color
        """
        super().__init__(color)

    def get_name(self):
        """Get the human player's name."""
        return f"Human ({self.color})"

    def choose_moves(self, board, dice_values):
        """Human moves are handled through the UI, not this method.

        This method is here for compatibility with the Player interface.

        Args:
            board: The game board
            dice_values: List of available dice values

        Returns:
            list: Always returns an empty list
        """
        # Human player moves are handled through the GameController's
        # event handling, not through this method
        return []

    def can_move(self, board, dice_values):
        """Check if the player has any valid moves.

        Args:
            board: The game board
            dice_values: List of available dice values

        Returns:
            bool: True if there are valid moves, False otherwise
        """
        # This should use MoveValidator but for simplicity,
        # we're delegating this to the GameController
        return True  # Placeholder - actual logic in GameController