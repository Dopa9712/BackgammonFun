# player.py - Contains the HumanPlayer class

class HumanPlayer:
    def __init__(self, color):
        """Initialize a human player.

        Args:
            color: "White" or "Black" - the player's color
        """
        self.color = color

    def get_name(self):
        """Get the player's name."""
        return f"Human ({self.color})"

    def get_color(self):
        """Get the player's color."""
        return self.color

    # Note: Human player moves are handled through the GameController's
    # event handling, not through this class. This is because human moves
    # are driven by user input events, which are processed by the controller.

    def can_move(self, board, dice_values):
        """Check if the player has any valid moves.

        Args:
            board: The game board
            dice_values: List of available dice values

        Returns:
            bool: True if there are valid moves, False otherwise
        """
        # This could use MoveValidator but for simplicity,
        # we're delegating this to the GameController
        return True  # Placeholder - actual logic in GameController