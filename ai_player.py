# ai_player.py - Updated AI player class with corrected movement directions

import random
from move_validator import MoveValidator


class AIPlayer:
    def __init__(self, color):
        """Initialize an AI player.

        Args:
            color: "White" or "Black" - the AI's color
        """
        self.color = color
        self.move_validator = None  # Initialize in choose_moves

    def get_name(self):
        """Get the AI player's name."""
        return f"AI ({self.color})"

    def get_color(self):
        """Get the AI player's color."""
        return self.color

    def choose_moves(self, board, dice_values):
        """Choose the best moves for the current dice roll.

        Args:
            board: The game board
            dice_values: List of available dice values

        Returns:
            list: List of (from_point, to_point) tuples representing moves
        """
        # Initialize the move validator if needed
        if self.move_validator is None:
            self.move_validator = MoveValidator(board)

        # Get all possible moves
        all_possible_moves = self.get_all_possible_move_sequences(board, dice_values)

        # If no moves available, return empty list
        if not all_possible_moves:
            return []

        # Evaluate each move sequence and choose the best one
        best_sequence = self.evaluate_move_sequences(board, all_possible_moves)

        return best_sequence

    def get_all_possible_move_sequences(self, board, dice_values):
        """Get all possible sequences of moves for the given dice values.

        Args:
            board: The game board
            dice_values: List of available dice values

        Returns:
            list: List of move sequences, where each sequence is a list of (from, to) tuples
        """
        # This is a complex function in real backgammon.
        # For now, we'll implement a simplified version that generates valid single moves.

        # Copy dice values to avoid modifying the original
        remaining_dice = dice_values.copy()

        # Initialize with empty sequence
        sequences = [[]]

        # Generate move sequences recursively
        return self._generate_move_sequences(board, remaining_dice, sequences, [])

    def _generate_move_sequences(self, board, remaining_dice, sequences, current_sequence):
        """Recursively generate all valid move sequences.

        Args:
            board: The current board state
            remaining_dice: List of unused dice values
            sequences: List of valid sequences found so far
            current_sequence: The sequence being built

        Returns:
            list: Updated list of valid move sequences
        """
        # If no more dice, this sequence is complete
        if not remaining_dice:
            if current_sequence:  # Only add non-empty sequences
                sequences.append(current_sequence)
            return sequences

        # Create a temporary board to simulate moves
        temp_board = self._clone_board(board)

        # Apply all moves in the current sequence to the temporary board
        for from_point, to_point in current_sequence:
            temp_board.move_piece(from_point, to_point)

        # Get all valid moves with the next die
        die = remaining_dice[0]
        valid_moves = self.move_validator.get_valid_moves_for_die(self.color, die, temp_board)

        # If no valid moves with this die, try the next die or end sequence
        if not valid_moves:
            # Skip this die and continue with remaining dice
            new_remaining = remaining_dice[1:]
            return self._generate_move_sequences(board, new_remaining, sequences, current_sequence)

        # Try each valid move and continue recursively
        new_sequences = sequences.copy()
        for from_point, to_point in valid_moves:
            # Create a new sequence with this move
            new_sequence = current_sequence.copy()
            new_sequence.append((from_point, to_point))

            # Continue with remaining dice
            new_remaining = remaining_dice[1:]
            new_sequences = self._generate_move_sequences(board, new_remaining, new_sequences, new_sequence)

        return new_sequences

    def _clone_board(self, board):
        """Create a copy of the board for move simulation.

        In a real implementation, the Board class would have a clone method.
        For simplicity, we'll create a basic copy here.

        Args:
            board: The board to clone

        Returns:
            Board: A copy of the board
        """
        # This is a simplified version - in a real implementation,
        # the Board class would provide a proper clone or copy method
        from board import Board
        new_board = Board()

        # Copy all pieces
        for point in range(28):
            new_board.points[point] = board.points[point].copy()

        return new_board

    def evaluate_move_sequences(self, board, move_sequences):
        """Evaluate all move sequences and choose the best one.

        Args:
            board: The current board state
            move_sequences: List of move sequences to evaluate

        Returns:
            list: The best move sequence
        """
        if not move_sequences:
            return []

        # For a simple AI, we'll use a set of heuristics to score moves
        best_score = float('-inf')
        best_sequence = move_sequences[0]

        for sequence in move_sequences:
            # Create a temporary board to simulate this sequence
            temp_board = self._clone_board(board)

            # Apply all moves in the sequence
            for from_point, to_point in sequence:
                temp_board.move_piece(from_point, to_point)

            # Score the resulting position
            score = self._evaluate_position(temp_board)

            if score > best_score:
                best_score = score
                best_sequence = sequence

        return best_sequence

    def _evaluate_position(self, board):
        """Evaluate a board position for the AI.

        This is a simple heuristic evaluation function. A more sophisticated
        AI would use a more complex evaluation function.

        Args:
            board: The board to evaluate

        Returns:
            float: Score for the position (higher is better for AI)
        """
        score = 0
        opponent_color = "Black" if self.color == "White" else "White"

        # 1. Count pieces that have been borne off - biggest priority
        home_index = 27 if self.color == "White" else 26
        opponent_home_index = 26 if self.color == "White" else 27
        score += len(board.points[home_index]) * 20  # INCREASED bonus for pieces borne off
        score -= len(board.points[opponent_home_index]) * 20  # INCREASED penalty for opponent pieces borne off

        # 2. Penalty for pieces on the bar
        bar_index = 25 if self.color == "White" else 0
        opponent_bar_index = 0 if self.color == "White" else 25
        score -= len(board.points[bar_index]) * 10  # INCREASED penalty for pieces on the bar
        score += len(board.points[opponent_bar_index]) * 10  # INCREASED bonus for opponent pieces on the bar

        # 3. Check if we can bear off
        can_bear_off = board.can_bear_off(self.color)
        if can_bear_off:
            # Add an extra bonus for having all pieces in the home board
            score += 15

            # Add bonus for pieces close to bearing off
            if self.color == "White":
                for point in range(19, 25):  # White's home board
                    count = board.count_pieces_at(point, self.color)
                    # More points for pieces closer to bearing off
                    score += count * (point - 18) * 2
            else:
                for point in range(1, 7):  # Black's home board
                    count = board.count_pieces_at(point, self.color)
                    # More points for pieces closer to bearing off
                    score += count * (7 - point) * 2

        # 4. Evaluate board position
        if self.color == "White":
            # White pieces want to move from 1 to 24
            for point in range(1, 25):
                count = board.count_pieces_at(point, self.color)
                if count > 0:
                    # Pieces closer to home get higher scores
                    # Increased weight for pieces in home board or approaching it
                    if point >= 19:  # Home board
                        score += count * point / 2
                    else:
                        score += count * point / 5

                    # Blots (single pieces) are vulnerable
                    if count == 1:
                        score -= 2

                    # Blocked points (2+ pieces) are good
                    if count >= 2:
                        score += 1

                    # Check for opponent blots that can be hit
                    opponent_count = board.count_pieces_at(point, opponent_color)
                    if opponent_count == 1:
                        score += 3  # Bonus for potential hits
        else:
            # Black pieces want to move from 24 to 1
            for point in range(1, 25):
                count = board.count_pieces_at(point, self.color)
                if count > 0:
                    # Pieces closer to home get higher scores
                    # Increased weight for pieces in home board or approaching it
                    if point <= 6:  # Home board
                        score += count * (25 - point) / 2
                    else:
                        score += count * (25 - point) / 5

                    # Blots (single pieces) are vulnerable
                    if count == 1:
                        score -= 2

                    # Blocked points (2+ pieces) are good
                    if count >= 2:
                        score += 1

                    # Check for opponent blots that can be hit
                    opponent_count = board.count_pieces_at(point, opponent_color)
                    if opponent_count == 1:
                        score += 3  # Bonus for potential hits

        # 5. Add a tiny bit of randomness for variety (smaller impact now)
        score += random.uniform(0, 0.05)

        return score