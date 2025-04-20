# controller/game_controller.py - Main game controller

import pygame
import random
import sys
import os

# Add parent directory to path to allow imports from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.move_validator import MoveValidator
from model.dice import Dice


class GameController:
    """Controls the flow of the backgammon game."""

    def __init__(self, board, human_player, ai_player, renderer):
        """Initialize the game controller.

        Args:
            board: The game board
            human_player: The human player
            ai_player: The AI player
            renderer: The renderer
        """
        self.board = board
        self.human_player = human_player
        self.ai_player = ai_player
        self.renderer = renderer
        self.move_validator = MoveValidator(board)
        self.dice = Dice()

        # Game state variables
        self.current_player = None
        self.selected_point = None
        self.possible_moves = []
        self.game_state = "START"  # START, ROLL_DICE, HUMAN_TURN, AI_TURN, GAME_OVER
        self.is_first_turn = True  # Flag to track if this is the first turn

        # Track last moves for display
        self.last_ai_moves = []
        self.last_human_moves = []

        # Determine who goes first with initial dice roll
        self.determine_first_player()

    def determine_first_player(self):
        """Roll dice to determine who goes first and set initial dice values."""
        self.game_state = "START"
        human_roll = random.randint(1, 6)
        ai_roll = random.randint(1, 6)

        # If tie, roll again
        while human_roll == ai_roll:
            human_roll = random.randint(1, 6)
            ai_roll = random.randint(1, 6)

        # Set dice values for the first turn
        if human_roll > ai_roll:
            # Human won the dice roll, so human goes first
            self.current_player = self.human_player
            self.dice.values = [human_roll, ai_roll]
        else:
            # AI won the dice roll, so AI goes first
            self.current_player = self.ai_player
            self.dice.values = [ai_roll, human_roll]

        self.dice.used = [False, False]

        # Set the appropriate game state and calculate moves
        if self.current_player == self.human_player:
            self.game_state = "HUMAN_TURN"
            self.calculate_possible_moves()
        else:
            self.game_state = "AI_TURN"
            self.process_ai_turn()

    def roll_dice(self):
        """Roll two dice for the current player - but only if not the first turn."""
        if self.is_first_turn:
            # For first turn, dice are already set from determine_first_player
            self.is_first_turn = False
            return

        # Roll the dice
        dice_values, is_doubles = self.dice.roll()

        # Update game state based on whose turn it is
        if self.current_player == self.human_player:
            self.game_state = "HUMAN_TURN"
            self.calculate_possible_moves()
        else:
            self.game_state = "AI_TURN"
            self.process_ai_turn()

    def calculate_possible_moves(self):
        """Calculate all possible moves for the current player."""
        color = self.current_player.get_color()
        self.possible_moves = self.move_validator.get_valid_moves(color, self.dice.get_unused_values())

        # If no valid moves, end turn
        if not self.possible_moves:
            self.end_turn()

    def handle_event(self, event):
        """Handle pygame events.

        Args:
            event: The pygame event to handle
        """
        if self.game_state == "ROLL_DICE":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.roll_dice()

        elif self.game_state == "HUMAN_TURN":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Convert mouse position to board point
                point = self.renderer.get_point_at_position(event.pos)

                if point is not None:
                    if self.selected_point is None:
                        # First click - select a point with player's pieces
                        if self.can_select_point(point):
                            self.selected_point = point
                    else:
                        # Second click - try to move to the target point
                        self.try_move(self.selected_point, point)
                        self.selected_point = None

        elif self.game_state == "GAME_OVER":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Reset game if clicked after game over
                self.board.setup_initial_position()
                self.is_first_turn = True  # Reset first turn flag
                self.determine_first_player()

    def can_select_point(self, point):
        """Check if a point can be selected (has player's pieces).

        Args:
            point: The point number (0-27)

        Returns:
            bool: True if the point can be selected, False otherwise
        """
        color = self.current_player.get_color()

        # If player has pieces on the bar, they must move those first
        if self.board.has_pieces_on_bar(color):
            return (color == "White" and point == 25) or (color == "Black" and point == 0)

        # Otherwise, check if the point has the player's pieces
        return self.board.count_pieces_at(point, color) > 0

    def try_move(self, from_point, to_point):
        """Try to move a piece from one point to another.

        Args:
            from_point: Source point number (0-25)
            to_point: Destination point number (0-27)

        Returns:
            bool: True if the move was successful, False otherwise
        """
        color = self.current_player.get_color()

        # Get unused dice values
        unused_dice = self.dice.get_unused_values()

        # Find the appropriate dice value for this move
        dice_value = self.move_validator.find_dice_for_move(from_point, to_point, color, unused_dice)

        # If no valid dice found, the move is invalid
        if dice_value is None:
            return False

        # Make the move
        move_result = self.board.move_piece(from_point, to_point)
        if move_result:
            # Mark the die as used
            self.dice.mark_used(dice_value)

            # Record the move
            self.last_human_moves.append((from_point, to_point))

            # Check if the turn is over
            if self.dice.all_used():
                self.end_turn()
            else:
                # Calculate new possible moves
                self.calculate_possible_moves()

            return True

        return False

    def process_ai_turn(self):
        """Process the AI player's turn."""
        # Let the AI choose moves
        moves = self.ai_player.choose_moves(self.board, self.dice.get_values())

        # Store AI's moves for display
        self.last_ai_moves = moves.copy()

        # Execute each move
        for from_point, to_point in moves:
            self.board.move_piece(from_point, to_point)

            # Mark the appropriate die as used
            color = self.ai_player.get_color()
            dice_value = self.move_validator.find_dice_for_move(
                from_point, to_point, color, self.dice.get_unused_values())
            if dice_value:
                self.dice.mark_used(dice_value)

        # End AI turn
        self.end_turn()

    def end_turn(self):
        """End the current player's turn and switch to the other player."""
        # Check for a winner
        winner = self.board.check_winner()
        if winner:
            self.game_state = "GAME_OVER"
            return

        # Switch players
        if self.current_player == self.human_player:
            self.current_player = self.ai_player
            # Keep human's last moves for display until AI plays
        else:
            self.current_player = self.human_player
            # Reset human's last moves when it's their turn again
            self.last_human_moves = []

        # Reset for next turn
        self.dice.reset()
        self.selected_point = None
        self.possible_moves = []
        self.game_state = "ROLL_DICE"

    def update(self):
        """Update game state - called every frame."""
        # Any per-frame logic can go here
        pass

    def get_game_state(self):
        """Get the current game state for rendering.

        Returns:
            dict: Dictionary with current game state information
        """
        return {
            "state": self.game_state,
            "current_player": self.current_player.get_color(),
            "dice_values": self.dice.get_values(),
            "dice_used": self.dice.used,
            "selected_point": self.selected_point,
            "possible_moves": self.possible_moves,
            "last_ai_moves": self.last_ai_moves,
            "last_human_moves": self.last_human_moves
        }