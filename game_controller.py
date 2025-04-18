# game_controller.py - Fixed player determination logic

import pygame
import random
from move_validator import MoveValidator


class GameController:
    def __init__(self, board, human_player, ai_player, renderer):
        self.board = board
        self.human_player = human_player
        self.ai_player = ai_player
        self.renderer = renderer
        self.move_validator = MoveValidator(board)

        # Game state variables
        self.current_player = None
        self.dice_values = []
        self.dice_used = []  # Track which dice have been used
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
        """Roll dice to determine who goes first and set initial dice values"""
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
            self.dice_values = [human_roll, ai_roll]
        else:
            # AI won the dice roll, so AI goes first
            self.current_player = self.ai_player
            self.dice_values = [ai_roll, human_roll]

        self.dice_used = [False, False]

        # Set the appropriate game state and calculate moves
        if self.current_player == self.human_player:
            self.game_state = "HUMAN_TURN"
            self.calculate_possible_moves()
        else:
            self.game_state = "AI_TURN"
            self.process_ai_turn()

    def roll_dice(self):
        """Roll two dice for the current player - but only if not the first turn"""
        if self.is_first_turn:
            # For first turn, dice are already set from determine_first_player
            self.is_first_turn = False
            return

        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)

        # If doubles, player gets to move each die value four times
        if die1 == die2:
            self.dice_values = [die1, die1, die1, die1]
        else:
            self.dice_values = [die1, die2]

        self.dice_used = [False] * len(self.dice_values)

        # Update game state based on whose turn it is
        if self.current_player == self.human_player:
            self.game_state = "HUMAN_TURN"
            self.calculate_possible_moves()
        else:
            self.game_state = "AI_TURN"
            self.process_ai_turn()

    def calculate_possible_moves(self):
        """Calculate all possible moves for the current player"""
        color = self.current_player.color
        self.possible_moves = self.move_validator.get_valid_moves(color, self.get_unused_dice())

        # If no valid moves, end turn
        if not self.possible_moves:
            self.end_turn()

    def get_unused_dice(self):
        """Get dice values that haven't been used yet"""
        return [self.dice_values[i] for i in range(len(self.dice_values)) if not self.dice_used[i]]

    def handle_event(self, event):
        """Handle pygame events"""
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
        """Check if a point can be selected (has player's pieces)"""
        color = self.current_player.color

        # If player has pieces on the bar, they must move those first
        if self.board.has_pieces_on_bar(color):
            return (color == "White" and point == 25) or (color == "Black" and point == 0)

        # Otherwise, check if the point has the player's pieces
        return self.board.count_pieces_at(point, color) > 0

    def try_move(self, from_point, to_point):
        """Try to move a piece from one point to another"""
        color = self.current_player.color

        # Get unused dice values
        unused_dice = self.get_unused_dice()

        # Find the appropriate dice value for this move
        dice_value = self.move_validator.find_dice_for_move(from_point, to_point, color, unused_dice)

        # If no valid dice found, the move is invalid
        if dice_value is None:
            return False

        # Find the index of the dice to mark as used
        try:
            dice_index = self.dice_values.index(dice_value)
            while self.dice_used[dice_index]:
                dice_index = self.dice_values.index(dice_value, dice_index + 1)
        except ValueError:
            return False

        # Make the move - this should handle bearing off correctly now
        move_result = self.board.move_piece(from_point, to_point)
        if move_result:
            self.dice_used[dice_index] = True

            # Record the move
            self.last_human_moves.append((from_point, to_point))

            # Check if the turn is over
            if all(self.dice_used):
                self.end_turn()
            else:
                # Calculate new possible moves
                self.calculate_possible_moves()

            return True

        return False

    def _has_higher_pieces(self, from_point, color):
        """Check if there are pieces on higher points (for white bearing off)."""
        for point in range(from_point + 1, 25):
            if self.board.count_pieces_at(point, color) > 0:
                return True
        return False

    def _has_lower_pieces(self, from_point, color):
        """Check if there are pieces on lower points (for black bearing off)."""
        for point in range(1, from_point):
            if self.board.count_pieces_at(point, color) > 0:
                return True
        return False
    def process_ai_turn(self):
        """Process the AI player's turn"""
        # Let the AI choose moves
        moves = self.ai_player.choose_moves(self.board, self.dice_values)

        # Store AI's moves for display
        self.last_ai_moves = moves.copy()

        # Execute each move
        for from_point, to_point in moves:
            self.board.move_piece(from_point, to_point)

        # End AI turn
        self.end_turn()

    def end_turn(self):
        """End the current player's turn and switch to the other player"""
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

        # Reset for next turn and set to ROLL_DICE state
        self.dice_values = []
        self.dice_used = []
        self.selected_point = None
        self.possible_moves = []
        self.game_state = "ROLL_DICE"

    def update(self):
        """Update game state - called every frame"""
        # Add any frame-by-frame logic here
        pass

    def get_game_state(self):
        """Get the current game state for rendering"""
        return {
            "state": self.game_state,
            "current_player": self.current_player.color,
            "dice_values": self.dice_values,
            "dice_used": self.dice_used,
            "selected_point": self.selected_point,
            "possible_moves": self.possible_moves,
            "last_ai_moves": self.last_ai_moves,
            "last_human_moves": self.last_human_moves
        }