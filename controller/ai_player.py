# controller/ai_player.py - AI player implementation

import random
import sys
import os

# Add parent directory to path to allow imports from model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.player import Player
from model.move_validator import MoveValidator


class AIPlayer(Player):
    """AI player for backgammon that makes strategic decisions."""

    def __init__(self, color, difficulty="medium"):
        """Initialize an AI player.

        Args:
            color: "White" or "Black" - the AI's color
            difficulty: "easy", "medium", or "hard" - affects how smart the AI is
        """
        super().__init__(color)
        self.move_validator = None  # Initialize in choose_moves
        self.difficulty = difficulty

    def get_name(self):
        """Get the AI player's name."""
        return f"AI ({self.color})"

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

        # Get all possible move sequences
        all_possible_moves = self.move_validator.get_all_possible_move_sequences(
            self.color, dice_values, board)

        # If no moves available, return empty list
        if not all_possible_moves:
            return []

        # Evaluate each move sequence and choose the best one
        best_sequence = self.evaluate_move_sequences(board, all_possible_moves)

        return best_sequence

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
            temp_board = board.clone()

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

        This is a heuristic evaluation function. A more sophisticated
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
        score += len(board.points[home_index]) * 20  # Bonus for pieces borne off
        score -= len(board.points[opponent_home_index]) * 20  # Penalty for opponent pieces borne off

        # 2. Penalty for pieces on the bar
        bar_index = 25 if self.color == "White" else 0
        opponent_bar_index = 0 if self.color == "White" else 25
        score -= len(board.points[bar_index]) * 10  # Penalty for pieces on the bar
        score += len(board.points[opponent_bar_index]) * 10  # Bonus for opponent pieces on the bar

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
        randomness_factor = 0.05
        if self.difficulty == "easy":
            randomness_factor = 0.3  # More random moves for easy AI
        elif self.difficulty == "hard":
            randomness_factor = 0.01  # Less random moves for hard AI

        score += random.uniform(0, randomness_factor)

        return score