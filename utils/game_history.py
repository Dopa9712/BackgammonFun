# utils/game_history.py - Game history tracking for move review

import copy
import time
from datetime import datetime


class GameHistory:
    """Tracks the history of a backgammon game for later review."""

    def __init__(self):
        """Initialize the game history tracker."""
        self.move_history = []
        self.board_states = []
        self.dice_history = []
        self.current_game_id = None
        self.review_index = -1  # -1 means viewing current state
        self.is_in_review_mode = False

        # Initialize a new game
        self.start_new_game()

    def start_new_game(self):
        """Start tracking a new game."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_game_id = f"game_{timestamp}"
        self.move_history = []
        self.board_states = []
        self.dice_history = []
        self.is_in_review_mode = False
        self.review_index = -1

    def record_move(self, player_color, from_point, to_point, board, dice_values, dice_used):
        """Record a single move in the game history.

        Args:
            player_color: Color of the player making the move ("White" or "Black")
            from_point: Starting point of the move
            to_point: Ending point of the move
            board: Current board state after the move
            dice_values: Current dice values
            dice_used: Which dice have been used
        """
        # Don't record if in review mode
        if self.is_in_review_mode:
            return

        # Create move record
        move_record = {
            "player": player_color,
            "from": from_point,
            "to": to_point,
            "timestamp": time.time()
        }

        # Create dice record
        dice_record = {
            "values": dice_values.copy(),
            "used": dice_used.copy()
        }

        # Record the move
        self.move_history.append(move_record)

        # Create a deep copy of the board state
        board_state = copy.deepcopy(board.points)
        self.board_states.append(board_state)

        # Record dice state
        self.dice_history.append(dice_record)

    def record_turn_start(self, player_color, board, dice_values):
        """Record the start of a new turn with a dice roll.

        Args:
            player_color: Color of the player starting their turn
            board: Current board state
            dice_values: Dice values that were rolled
        """
        # Don't record if in review mode
        if self.is_in_review_mode:
            return

        # Create turn start record
        move_record = {
            "player": player_color,
            "action": "roll",
            "values": dice_values.copy(),
            "timestamp": time.time()
        }

        # Create dice record
        dice_record = {
            "values": dice_values.copy(),
            "used": [False] * len(dice_values)
        }

        # Record the turn start
        self.move_history.append(move_record)

        # Create a deep copy of the board state
        board_state = copy.deepcopy(board.points)
        self.board_states.append(board_state)

        # Record dice state
        self.dice_history.append(dice_record)

    def get_review_state(self):
        """Get the board and dice state for the current review index.

        Returns:
            tuple: (board_state, dice_record, index, total_states)
        """
        if not self.is_in_review_mode or not self.board_states:
            return None, None, 0, 0

        index = self.review_index
        if index < 0 or index >= len(self.board_states):
            index = len(self.board_states) - 1

        board_state = self.board_states[index]
        dice_record = self.dice_history[index] if index < len(self.dice_history) else None

        return board_state, dice_record, index + 1, len(self.board_states)

    def get_move_description(self, index):
        """Get a human-readable description of the move at the given index.

        Args:
            index: Index of the move to describe

        Returns:
            str: Description of the move
        """
        if index < 0 or index >= len(self.move_history):
            return "No move available"

        move = self.move_history[index]
        player = move["player"]

        if "action" in move and move["action"] == "roll":
            return f"{player} rolled {move['values']}"
        else:
            from_point = move["from"]
            to_point = move["to"]
            return f"{player} moved from {from_point} to {to_point}"

    def start_review_mode(self):
        """Enter review mode, starting at the most recent state."""
        if not self.board_states:
            return False

        self.is_in_review_mode = True
        self.review_index = len(self.board_states) - 1
        return True

    def exit_review_mode(self):
        """Exit review mode."""
        self.is_in_review_mode = False
        self.review_index = -1

    def move_to_previous_state(self):
        """Move to the previous state in the review."""
        if not self.is_in_review_mode or not self.board_states:
            return False

        if self.review_index > 0:
            self.review_index -= 1
            return True
        return False

    def move_to_next_state(self):
        """Move to the next state in the review."""
        if not self.is_in_review_mode or not self.board_states:
            return False

        if self.review_index < len(self.board_states) - 1:
            self.review_index += 1
            return True
        return False

    def move_to_first_state(self):
        """Move to the first state in the review."""
        if not self.is_in_review_mode or not self.board_states:
            return False

        if self.board_states:
            self.review_index = 0
            return True
        return False

    def move_to_last_state(self):
        """Move to the last state (current state) in the review."""
        if not self.is_in_review_mode or not self.board_states:
            return False

        if self.board_states:
            self.review_index = len(self.board_states) - 1
            return True
        return False

    def is_reviewing(self):
        """Check if currently in review mode."""
        return self.is_in_review_mode

    def get_move_count(self):
        """Get the number of recorded moves."""
        return len(self.move_history)

    def get_current_index(self):
        """Get the current review index."""
        return self.review_index

    def get_most_recent_moves(self, count=5):
        """Get the most recent moves.

        Args:
            count: Number of recent moves to return

        Returns:
            list: List of recent move records
        """
        if not self.move_history:
            return []

        start_index = max(0, len(self.move_history) - count)
        return self.move_history[start_index:]