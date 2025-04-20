# model/board.py - Board model with game state logic

class Board:
    """Represents the backgammon board state.

    The board has 24 points (1-24), plus special points:
    - 0: Black's bar (also Black's bearing off target)
    - 25: White's bar (also White's bearing off target)
    - 26: Black's home (pieces that have been borne off)
    - 27: White's home (pieces that have been borne off)

    Movement directions:
    - White pieces move from 1 to 24 (increasing numbers), bearing off to point 25/27
    - Black pieces move from 24 to 1 (decreasing numbers), bearing off to point 0/26
    """

    def __init__(self):
        """Initialize a new board with the standard starting position."""
        # Create empty points array (0-27)
        self.points = [[] for _ in range(28)]
        self.setup_initial_position()

    def setup_initial_position(self):
        """Set up the standard backgammon starting position."""
        # Clear the board
        for i in range(28):
            self.points[i] = []

        # Set up initial pieces
        # White pieces
        self.points[1] = ["White"] * 2  # 2 white pieces on point 1
        self.points[12] = ["White"] * 5  # 5 white pieces on point 12
        self.points[17] = ["White"] * 3  # 3 white pieces on point 17
        self.points[19] = ["White"] * 5  # 5 white pieces on point 19

        # Black pieces
        self.points[6] = ["Black"] * 5  # 5 black pieces on point 6
        self.points[8] = ["Black"] * 3  # 3 black pieces on point 8
        self.points[13] = ["Black"] * 5  # 5 black pieces on point 13
        self.points[24] = ["Black"] * 2  # 2 black pieces on point 24

    def get_pieces_at(self, point):
        """Get all pieces at a specific point.

        Args:
            point: The point number (0-27)

        Returns:
            list: List of pieces at the point
        """
        if 0 <= point <= 27:
            return self.points[point].copy()  # Return a copy for safety
        return []

    def count_pieces_at(self, point, color):
        """Count pieces of a specific color at a point.

        Args:
            point: The point number (0-27)
            color: The color to count ("White" or "Black")

        Returns:
            int: Number of pieces of the specified color at the point
        """
        if 0 <= point <= 27:
            return sum(1 for piece in self.points[point] if piece == color)
        return 0

    def count_all_pieces(self, color):
        """Count all pieces of a color on the board.

        Args:
            color: The color to count ("White" or "Black")

        Returns:
            int: Total number of pieces of the color
        """
        return sum(self.count_pieces_at(point, color) for point in range(28))

    def move_piece(self, from_point, to_point):
        """Move a piece from one point to another.

        Args:
            from_point: Source point number (0-25)
            to_point: Destination point number (0-27)

        Returns:
            bool: True if the move was successful, False otherwise
        """
        if 0 <= from_point <= 25 and 0 <= to_point <= 27 and self.points[from_point]:
            # Get the color of the piece to move
            color = self.points[from_point][-1]

            # Special handling for bearing off
            if (color == "White" and to_point == 25) or (color == "Black" and to_point == 0):
                # Redirect to the appropriate home collection
                to_point = 27 if color == "White" else 26

                # Move the piece
                self.points[from_point].pop()
                self.points[to_point].append(color)
                return True

            # Check if we're hitting an opponent's blot (single piece)
            if to_point not in [0, 25, 26, 27]:  # Not moving to bar or home
                if self.points[to_point] and self.points[to_point][0] != color and len(self.points[to_point]) == 1:
                    # Hit opponent's blot - move to the bar
                    opponent_color = self.points[to_point][0]
                    self.points[to_point].pop()

                    if opponent_color == "White":
                        self.points[25].append(opponent_color)  # White goes to bar at index 25
                    else:
                        self.points[0].append(opponent_color)  # Black goes to bar at index 0

            # Move the piece
            self.points[from_point].pop()
            self.points[to_point].append(color)

            return True

        return False

    def has_pieces_on_bar(self, color):
        """Check if a player has pieces on the bar.

        Args:
            color: The player's color ("White" or "Black")

        Returns:
            bool: True if the player has pieces on the bar, False otherwise
        """
        if color == "White":
            return len(self.points[25]) > 0
        else:
            return len(self.points[0]) > 0

    def can_bear_off(self, color):
        """Check if a player can bear off pieces.

        All pieces must be in the home board (last 6 points).

        Args:
            color: The player's color ("White" or "Black")

        Returns:
            bool: True if the player can bear off, False otherwise
        """
        if color == "White":
            # Check if any white pieces are outside the home board (points 19-24) or on the bar
            for i in range(1, 19):  # Check points 1-18
                if self.count_pieces_at(i, "White") > 0:
                    return False

            # Check if any pieces are on the bar
            if self.count_pieces_at(25, "White") > 0:
                return False

            return True
        else:
            # Check if any black pieces are outside the home board (points 1-6) or on the bar
            for i in range(7, 25):  # Check points 7-24
                if self.count_pieces_at(i, "Black") > 0:
                    return False

            # Check if any pieces are on the bar
            if self.count_pieces_at(0, "Black") > 0:
                return False

            return True

    def check_winner(self):
        """Check if there's a winner (all 15 pieces borne off).

        Returns:
            str or None: "White" or "Black" if there's a winner, None otherwise
        """
        if len(self.points[27]) == 15:  # All 15 White pieces at home
            return "White"
        elif len(self.points[26]) == 15:  # All 15 Black pieces at home
            return "Black"
        return None

    def clone(self):
        """Create a deep copy of this board.

        Returns:
            Board: A new board with the same state
        """
        new_board = Board()
        for i in range(28):
            new_board.points[i] = self.points[i].copy()
        return new_board