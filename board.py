# board.py - Contains the Board class with corrected movement directions
# White pieces move from 1 to 24 (increasing numbers), bearing off to point 25
# Black pieces move from 24 to 1 (decreasing numbers), bearing off to point 0

class Board:
    def __init__(self):
        # Initialize the board with starting positions
        # In backgammon, the points are numbered 1-24
        # White pieces move from 1 to 24 (increasing numbers), bearing off to point 25
        # Black pieces move from 24 to 1 (decreasing numbers), bearing off to point 0
        self.points = [[] for _ in range(28)]  # 0-25 for board, 26-27 for bear off

        # Set up initial pieces
        self.setup_initial_position()

    def setup_initial_position(self):
        # Standard backgammon starting position
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

        # Bar pieces
        self.points[0] = []  # Bar for Black (if hit) - also Black's bear-off target
        self.points[25] = []  # Bar for White (if hit) - also White's bear-off target

        # Home (borne off pieces)
        self.points[26] = []  # Collection of Black pieces that have been borne off
        self.points[27] = []  # Collection of White pieces that have been borne off

    def get_pieces_at(self, point):
        """Get all pieces at a specific point"""
        if 0 <= point <= 27:
            return self.points[point]
        return []

    def count_pieces_at(self, point, color):
        """Count pieces of a specific color at a point"""
        if 0 <= point <= 27:
            return sum(1 for piece in self.points[point] if piece == color)
        return 0

    def move_piece(self, from_point, to_point):
        """Move a piece from one point to another"""
        if 0 <= from_point <= 25 and 0 <= to_point <= 27 and self.points[from_point]:
            # Get the color of the piece to move
            color = self.points[from_point][-1]

            # Special handling for bearing off
            if (color == "White" and to_point == 25) or (color == "Black" and to_point == 0):
                # When bearing off, move piece to the collection of borne-off pieces
                to_point = 27 if color == "White" else 26
                # Move the piece
                self.points[from_point].pop()
                self.points[to_point].append(color)
                return True

            # Check if we're hitting an opponent's blot
            if to_point != 0 and to_point != 25 and to_point != 26 and to_point != 27:  # Not moving to bar or home
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
        """Check if a player has pieces on the bar"""
        if color == "White":
            return len(self.points[25]) > 0
        else:
            return len(self.points[0]) > 0

    def can_bear_off(self, color):
        """Check if a player can bear off pieces"""
        # All pieces must be in the home board (last 6 points)
        if color == "White":
            # Check if any white pieces are outside the home board (points 19-24) or on the bar
            for i in range(1, 19):  # Check points 1-18
                if self.count_pieces_at(i, "White") > 0:
                    return False
            for i in range(25, 26):  # Just check the bar
                if self.count_pieces_at(i, "White") > 0:
                    return False
            return True
        else:
            # Check if any black pieces are outside the home board (points 1-6) or on the bar
            for i in range(0, 1):  # Just check the bar
                if self.count_pieces_at(i, "Black") > 0:
                    return False
            for i in range(7, 25):  # Check points 7-24
                if self.count_pieces_at(i, "Black") > 0:
                    return False
            return True

    def get_valid_moves(self, color, dice_values):
        """Get all valid moves for a given color and dice roll"""
        # This is a complex function that will be implemented as part of move_validator.py
        # For now, return a placeholder
        return []

    def check_winner(self):
        """Check if there's a winner (all pieces borne off)"""
        if len(self.points[27]) == 15:  # All 15 White pieces at home
            return "White"
        elif len(self.points[26]) == 15:  # All 15 Black pieces at home
            return "Black"
        return None