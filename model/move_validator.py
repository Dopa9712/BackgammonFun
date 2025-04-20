# model/move_validator.py - Move validation logic for backgammon

class MoveValidator:
    """Validates moves in the backgammon game."""

    def __init__(self, board):
        """Initialize the move validator.

        Args:
            board: The game board
        """
        self.board = board

    def get_valid_moves(self, color, dice_values, board=None):
        """Get all valid moves for a given color and dice roll.

        Args:
            color: "White" or "Black" - the player's color
            dice_values: List of available dice values
            board: Optional custom board state (default: use self.board)

        Returns:
            list: List of (from_point, to_point) tuples representing valid moves
        """
        if board is None:
            board = self.board

        all_moves = []
        for die in dice_values:
            moves = self.get_valid_moves_for_die(color, die, board)
            all_moves.extend(moves)

        return all_moves

    def get_valid_moves_for_die(self, color, die_value, board=None):
        """Get all valid moves for a specific die value.

        Args:
            color: "White" or "Black" - the player's color
            die_value: The value of the die to use
            board: Optional custom board state (default: use self.board)

        Returns:
            list: List of (from_point, to_point) tuples representing valid moves
        """
        if board is None:
            board = self.board

        valid_moves = []

        # Check if player has pieces on the bar
        if board.has_pieces_on_bar(color):
            # Must move pieces from the bar first
            bar_point = 25 if color == "White" else 0

            # Calculate entry point
            if color == "White":
                # White enters at points 1-6 (from the bar at 25)
                entry_point = die_value  # die value 1-6 corresponds to points 1-6
            else:
                # Black enters at points 19-24 (from the bar at 0)
                entry_point = 25 - die_value  # e.g., die 1 = point 24, die 6 = point 19

            # Check if entry is valid
            if self.is_valid_entry(entry_point, color, board):
                valid_moves.append((bar_point, entry_point))

            # If player has pieces on the bar, they can only move those
            return valid_moves

        # No pieces on the bar, check regular moves and bearing off
        if color == "White":
            # White moves from low to high points (1→24), then bears off to point 25
            for from_point in range(1, 25):  # Check points 1 up to 24
                # Skip points without player's pieces
                if board.count_pieces_at(from_point, color) == 0:
                    continue

                # Check for bearing off
                if board.can_bear_off(color) and self.can_bear_off_with_die(from_point, die_value, color, board):
                    valid_moves.append((from_point, 25))

                # Check regular move
                to_point = from_point + die_value
                if 1 <= to_point <= 24 and self.is_valid_move(from_point, to_point, color, board):
                    valid_moves.append((from_point, to_point))
        else:
            # Black moves from high to low points (24→1), then bears off to point 0
            for from_point in range(24, 0, -1):  # Check points 24 down to 1
                # Skip points without player's pieces
                if board.count_pieces_at(from_point, color) == 0:
                    continue

                # Check for bearing off
                if board.can_bear_off(color) and self.can_bear_off_with_die(from_point, die_value, color, board):
                    valid_moves.append((from_point, 0))

                # Check regular move
                to_point = from_point - die_value
                if 1 <= to_point <= 24 and self.is_valid_move(from_point, to_point, color, board):
                    valid_moves.append((from_point, to_point))

        return valid_moves

    def is_valid_entry(self, entry_point, color, board):
        """Check if a piece can enter from the bar to the given point.

        Args:
            entry_point: The point to enter at
            color: The player's color
            board: The board state

        Returns:
            bool: True if the entry is valid, False otherwise
        """
        # Check if the entry point is valid (1-24)
        if not 1 <= entry_point <= 24:
            return False

        # Check if the entry point is not blocked by opponent
        pieces = board.get_pieces_at(entry_point)
        if not pieces:
            # Empty point is valid
            return True

        if pieces[0] != color and len(pieces) >= 2:
            # Point is blocked by opponent (2+ pieces)
            return False

        # Point is either empty, has our pieces, or has a single opponent piece
        return True

    def is_valid_move(self, from_point, to_point, color, board):
        """Check if a move is valid.

        This only checks if the destination point is valid for landing.
        It does NOT check the path between points - in backgammon,
        pieces can jump over blocked points.

        Args:
            from_point: Starting point
            to_point: Destination point
            color: Player's color
            board: Board state

        Returns:
            bool: True if the move is valid, False otherwise
        """
        # Check if destination is valid (1-24)
        if not 1 <= to_point <= 24:
            return False

        # Get the source pieces and verify they match the expected color
        source_pieces = board.get_pieces_at(from_point)
        if not source_pieces or source_pieces[0] != color:
            return False  # No pieces or wrong color at source point

        # Check if the destination point is not blocked by opponent
        dest_pieces = board.get_pieces_at(to_point)

        # Empty point is always valid
        if not dest_pieces:
            return True

        # Get the color of pieces at the destination point
        dest_color = dest_pieces[0]

        # If destination has opponent's pieces
        if dest_color != color:
            # Cannot land on a point with 2+ opponent pieces
            if len(dest_pieces) >= 2:
                return False
            # Can land on a point with exactly 1 opponent piece (hit)
            return True

        # If destination has pieces of the same color, it's valid
        return True

    def can_bear_off_with_die(self, from_point, die_value, color, board):
        """Check if a player can bear off a piece with a specific die value.

        Args:
            from_point: The point to bear off from
            die_value: The die value being used
            color: "White" or "Black" - the player's color
            board: The board state

        Returns:
            bool: True if the player can bear off with this die, False otherwise
        """
        # Must have all pieces in home board to bear off
        if not board.can_bear_off(color):
            return False

        if color == "White":
            # White's home board is points 19-24
            if from_point < 19:
                # Can't bear off from outside home board
                return False

            exact_value_needed = 25 - from_point

            # Exact value always works
            if die_value == exact_value_needed:
                return True

            # Higher value only works if no pieces on higher points
            if die_value > exact_value_needed:
                # Check if there are any white pieces on higher points
                for p in range(from_point + 1, 25):
                    if board.count_pieces_at(p, color) > 0:
                        return False
                return True

            # Lower value never works for bearing off
            return False
        else:
            # Black's home board is points 1-6
            if from_point > 6:
                # Can't bear off from outside home board
                return False

            exact_value_needed = from_point

            # Exact value always works
            if die_value == exact_value_needed:
                return True

            # Higher value only works if no pieces on lower points
            if die_value > exact_value_needed:
                # Check if there are any black pieces on lower points
                for p in range(1, from_point):
                    if board.count_pieces_at(p, color) > 0:
                        return False
                return True

            # Lower value never works for bearing off
            return False

    def find_dice_for_move(self, from_point, to_point, color, available_dice):
        """Find the appropriate dice value for a given move.

        Args:
            from_point: Starting point
            to_point: Destination point
            color: Player's color
            available_dice: List of available dice values

        Returns:
            int or None: The dice value to use, or None if no valid dice
        """
        # For pieces coming from the bar
        if (color == "White" and from_point == 25):
            # White uses die value equal to entry point
            dice_needed = to_point
            if dice_needed in available_dice:
                # Check if entry is valid
                if self.is_valid_entry(to_point, color, self.board):
                    return dice_needed
            return None
        elif (color == "Black" and from_point == 0):
            # Black uses die value 25 - entry point
            dice_needed = 25 - to_point
            if dice_needed in available_dice:
                # Check if entry is valid
                if self.is_valid_entry(to_point, color, self.board):
                    return dice_needed
            return None
        # For bearing off
        elif (color == "White" and to_point == 25):
            # Must be able to bear off
            if not self.board.can_bear_off(color) or from_point < 19:
                return None

            exact_dice = 25 - from_point

            # Exact value is available - use it
            if exact_dice in available_dice:
                return exact_dice

            # Check for larger dice if no pieces on higher points
            larger_dice = [d for d in available_dice if d > exact_dice]
            if larger_dice:
                # Check if there are pieces on higher points
                has_higher_pieces = False
                for p in range(from_point + 1, 25):
                    if self.board.count_pieces_at(p, color) > 0:
                        has_higher_pieces = True
                        break

                if not has_higher_pieces:
                    return min(larger_dice)  # Use smallest larger dice

            return None
        elif (color == "Black" and to_point == 0):
            # Must be able to bear off
            if not self.board.can_bear_off(color) or from_point > 6:
                return None

            exact_dice = from_point

            # Exact value is available - use it
            if exact_dice in available_dice:
                return exact_dice

            # Check for larger dice if no pieces on lower points
            larger_dice = [d for d in available_dice if d > exact_dice]
            if larger_dice:
                # Check if there are pieces on lower points
                has_lower_pieces = False
                for p in range(1, from_point):
                    if self.board.count_pieces_at(p, color) > 0:
                        has_lower_pieces = True
                        break

                if not has_lower_pieces:
                    return min(larger_dice)  # Use smallest larger dice

            return None
        # For regular moves
        else:
            if color == "White":
                dice_needed = to_point - from_point
            else:  # Black
                dice_needed = from_point - to_point

            if dice_needed in available_dice:
                # Make sure the destination is valid for landing
                if self.is_valid_move(from_point, to_point, color, self.board):
                    return dice_needed

            return None

    def get_all_possible_move_sequences(self, color, dice_values, board=None):
        """Generate all possible valid move sequences using the given dice.

        Args:
            color: The player's color
            dice_values: List of dice values
            board: Optional board state (default: self.board)

        Returns:
            list: List of move sequences, where each sequence is a list of (from, to) tuples
        """
        if board is None:
            board = self.board

        # Copy dice values to avoid modifying the original
        remaining_dice = dice_values.copy()

        # Initialize with empty sequence
        sequences = [[]]

        # Generate move sequences recursively
        return self._generate_move_sequences(board, remaining_dice, sequences, [], color)

    def _generate_move_sequences(self, board, remaining_dice, sequences, current_sequence, color):
        """Recursively generate all valid move sequences.

        Args:
            board: The current board state
            remaining_dice: List of unused dice values
            sequences: List of valid sequences found so far
            current_sequence: The sequence being built
            color: The player's color

        Returns:
            list: Updated list of valid move sequences
        """
        # If no more dice, this sequence is complete
        if not remaining_dice:
            if current_sequence:  # Only add non-empty sequences
                sequences.append(current_sequence)
            return sequences

        # Create a temporary board to simulate moves
        temp_board = board.clone()

        # Apply all moves in the current sequence to the temporary board
        for from_point, to_point in current_sequence:
            temp_board.move_piece(from_point, to_point)

        # Get all valid moves with the next die
        die = remaining_dice[0]
        valid_moves = self.get_valid_moves_for_die(color, die, temp_board)

        # If no valid moves with this die, try the next die or end sequence
        if not valid_moves:
            # Skip this die and continue with remaining dice
            new_remaining = remaining_dice[1:]
            return self._generate_move_sequences(board, new_remaining, sequences, current_sequence, color)

        # Try each valid move and continue recursively
        new_sequences = sequences.copy()
        for from_point, to_point in valid_moves:
            # Create a new sequence with this move
            new_sequence = current_sequence.copy()
            new_sequence.append((from_point, to_point))

            # Continue with remaining dice
            new_remaining = remaining_dice[1:]
            new_sequences = self._generate_move_sequences(board, new_remaining, new_sequences, new_sequence, color)

        return new_sequences