# controller/game_controller.py - Updated with history review features

import pygame
import random
import sys
import os
import time

# Add parent directory to path to allow imports from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.move_validator import MoveValidator
from model.dice import Dice
from utils.game_history import GameHistory


class GameController:
    """Controls the flow of the backgammon game with improved state handling."""

    # Game state constants for better code readability
    STATE_START = "START"
    STATE_ROLL_DICE = "ROLL_DICE"
    STATE_HUMAN_TURN = "HUMAN_TURN"
    STATE_AI_TURN = "AI_TURN"
    STATE_GAME_OVER = "GAME_OVER"
    STATE_PAUSED = "PAUSED"  # Pause state
    STATE_REVIEW = "REVIEW"  # New state for reviewing game history

    def __init__(self, board, human_player, ai_player, renderer):
        """Initialize the game controller with enhanced state tracking."""
        self.board = board
        self.human_player = human_player
        self.ai_player = ai_player
        self.renderer = renderer
        self.move_validator = MoveValidator(board)
        self.dice = Dice()

        # Game history tracking
        self.game_history = GameHistory()

        # Game state variables with better organization
        self.current_player = None
        self.selected_point = None
        self.possible_moves = []
        self.game_state = self.STATE_START
        self.is_first_turn = True

        # Track last moves for display and analysis
        self.last_ai_moves = []
        self.last_human_moves = []

        # Additional state tracking for better game flow
        self.turn_count = 0
        self.cannot_move = False  # Flag for when player has no valid moves
        self.roll_animation_active = False
        self.animation_start_time = 0
        self.ai_thinking_start_time = 0
        self.ai_min_think_time = 0.5  # Minimum AI "thinking" time in seconds

        # Game options
        self.ai_difficulty = "medium"
        self.show_possible_moves = True  # Option to show/hide move hints
        self.debug_mode = False

        # Review mode controls
        self.review_board = None
        self.review_dice_values = []
        self.review_dice_used = []
        self.show_move_history = False
        self.review_messages = []

        # Process logs for improved debugging
        self.game_log = []
        self.log_enabled = True

        # Start the game by determining who goes first
        self.determine_first_player()

    # Add this method to the GameController class
    def test_review_mode(self):
        # Record a dummy state for testing
        self.game_history.record_turn_start("Test", self.board, [1, 2])
        print(f"Test state recorded. Total states: {len(self.game_history.board_states)}")

        # Try entering review mode
        result = self.enter_review_mode()
        print(f"Enter review mode result: {result}, Current state: {self.game_state}")

        # Exit review mode
        self.exit_review_mode()
        print(f"Exited review mode. Current state: {self.game_state}")

    def determine_first_player(self):
        """Roll dice to determine who goes first with improved visualization."""
        self.game_state = self.STATE_START
        self.log("Game started - determining first player")

        # Roll until we get different values
        human_roll = random.randint(1, 6)
        ai_roll = random.randint(1, 6)

        while human_roll == ai_roll:
            human_roll = random.randint(1, 6)
            ai_roll = random.randint(1, 6)

        # Set initial dice values
        if human_roll > ai_roll:
            self.log(f"Human won initial roll: {human_roll} vs {ai_roll}")
            self.current_player = self.human_player
            self.dice.values = [human_roll, ai_roll]
        else:
            self.log(f"AI won initial roll: {ai_roll} vs {human_roll}")
            self.current_player = self.ai_player
            self.dice.values = [ai_roll, human_roll]

        self.dice.used = [False, False]

        # Start tracking history with initial state
        self.game_history.start_new_game()
        # Record initial state
        self.game_history.record_turn_start(self.current_player.get_color(), self.board, self.dice.values)

        # Set the appropriate game state
        if self.current_player == self.human_player:
            self.game_state = self.STATE_HUMAN_TURN
            self.calculate_possible_moves()
        else:
            self.game_state = self.STATE_AI_TURN
            self.ai_thinking_start_time = time.time()
            # Process AI turn in update loop for smoother experience

            # Record a dummy state for testing
            self.game_history.record_turn_start("Test", self.board, [1, 2])
            print(f"Test state recorded. Total states: {len(self.game_history.board_states)}")

            # Try entering review mode
            result = self.enter_review_mode()
            print(f"Enter review mode result: {result}, Current state: {self.game_state}")

            # Exit review mode
            self.exit_review_mode()
            print(f"Exited review mode. Current state: {self.game_state}")

        # Then call this in determine_first_player:
        self.test_review_mode()

    def roll_dice(self):
        """Roll dice with improved state management and animation control."""
        if self.roll_animation_active:
            return  # Don't allow rolling while animation is active

        self.roll_animation_active = True
        self.animation_start_time = time.time()

        # For first turn, dice are already set
        if self.is_first_turn:
            self.is_first_turn = False
            self.roll_animation_active = False
            return

        # Roll the dice and log the result
        dice_values, is_doubles = self.dice.roll()
        self.log(f"{self.current_player.get_color()} rolled: {dice_values}" +
                 (" (doubles!)" if is_doubles else ""))

        # Record the dice roll in history
        self.game_history.record_turn_start(self.current_player.get_color(), self.board, dice_values)

        # Update game state
        if self.current_player == self.human_player:
            self.game_state = self.STATE_HUMAN_TURN
            self.calculate_possible_moves()
        else:
            self.game_state = self.STATE_AI_TURN
            self.ai_thinking_start_time = time.time()
            # Process AI turn in update loop

    def calculate_possible_moves(self):
        """Calculate all possible moves with improved handling of no-move situations."""
        color = self.current_player.get_color()
        self.possible_moves = self.move_validator.get_valid_moves(color, self.dice.get_unused_values())

        # Handle the case where there are no valid moves
        if not self.possible_moves:
            self.log(f"{color} has no valid moves with dice {self.dice.get_unused_values()}")
            self.cannot_move = True

            # Small delay before ending turn automatically
            self.animation_start_time = time.time()
            self.roll_animation_active = True  # Reusing this flag for the delay
        else:
            self.cannot_move = False

    def handle_event(self, event):
        """Handle pygame events with improved state management and error handling."""
        # Handle global events regardless of game state
        if event.type == pygame.KEYDOWN:
            # Toggle debug mode with F1
            if event.key == pygame.K_F1:
                self.toggle_debug_mode()
                return

            # Toggle show possible moves with F2
            elif event.key == pygame.K_F2:
                self.show_possible_moves = not self.show_possible_moves
                self.log(f"Move hints {'enabled' if self.show_possible_moves else 'disabled'}")
                return

            # Toggle pause with P or Escape
            elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                if self.game_state == self.STATE_REVIEW:
                    self.exit_review_mode()
                else:
                    self.toggle_pause()
                return

            # Reset game with R
            elif event.key == pygame.K_r:
                self.reset_game()
                return

            # Toggle review mode with H (History)
            elif event.key == pygame.K_h:
                if self.game_state != self.STATE_REVIEW:
                    self.enter_review_mode()
                else:
                    self.exit_review_mode()
                return

        # Handle review mode navigation
        if self.game_state == self.STATE_REVIEW:
            if event.type == pygame.KEYDOWN:
                # Navigation keys for review mode
                if event.key == pygame.K_LEFT:
                    self.review_previous_state()
                    return
                elif event.key == pygame.K_RIGHT:
                    self.review_next_state()
                    return
                elif event.key == pygame.K_HOME:
                    self.review_first_state()
                    return
                elif event.key == pygame.K_END:
                    self.review_last_state()
                    return

            # Handle review mode clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicked on review navigation buttons
                if self.handle_review_button_click(event.pos):
                    return

        # Skip event handling if animations are active
        if self.roll_animation_active:
            return

        # Handle events based on game state
        if self.game_state == self.STATE_ROLL_DICE:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.roll_dice()

        elif self.game_state == self.STATE_HUMAN_TURN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Convert mouse position to board point with error handling
                try:
                    point = self.renderer.get_point_at_position(event.pos)
                    if point is not None:
                        self.handle_point_click(point)
                except Exception as e:
                    self.log(f"Error handling click: {e}")

        elif self.game_state == self.STATE_GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.reset_game()

        elif self.game_state == self.STATE_PAUSED:
            # Handle pause screen clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.toggle_pause()

    # New review mode methods
    def enter_review_mode(self):
        """Enter review mode to see game history."""
        if self.game_state in [self.STATE_PAUSED, self.STATE_GAME_OVER]:
            return

        if self.game_history.get_move_count() == 0:
            self.log("No moves to review yet.")
            return

        self._pre_review_state = self.game_state
        self.game_state = self.STATE_REVIEW

        # Start review mode at the current state
        if self.game_history.start_review_mode():
            self.log("Entered review mode. Use arrow keys to navigate through moves.")
            self.update_review_state()
        else:
            self.log("No game history available to review.")
            self.game_state = self._pre_review_state

    def exit_review_mode(self):
        """Exit review mode and return to the game."""
        if self.game_state != self.STATE_REVIEW:
            return

        self.game_history.exit_review_mode()
        self.game_state = self._pre_review_state
        self.log("Exited review mode.")

        # Clear review-specific data
        self.review_board = None
        self.review_dice_values = []
        self.review_dice_used = []
        self.review_messages = []

    def review_previous_state(self):
        """Go to the previous state in history."""
        if self.game_history.move_to_previous_state():
            self.update_review_state()
            return True
        return False

    def review_next_state(self):
        """Go to the next state in history."""
        if self.game_history.move_to_next_state():
            self.update_review_state()
            return True
        return False

    def review_first_state(self):
        """Go to the first state in history."""
        if self.game_history.move_to_first_state():
            self.update_review_state()
            return True
        return False

    def review_last_state(self):
        """Go to the last state in history."""
        if self.game_history.move_to_last_state():
            self.update_review_state()
            return True
        return False

    def update_review_state(self):
        """Update the review display with the current history state."""
        board_state, dice_record, index, total = self.game_history.get_review_state()

        if board_state:
            # Create a temporary board with this state for rendering
            self.review_board = self.board.clone()
            self.review_board.points = board_state

            # Set dice values for display
            if dice_record:
                self.review_dice_values = dice_record["values"]
                self.review_dice_used = dice_record["used"]
            else:
                self.review_dice_values = []
                self.review_dice_used = []

            # Create move description
            move_description = self.game_history.get_move_description(index - 1)
            self.review_messages = [
                f"Review Mode: Move {index} of {total}",
                move_description,
                "◄ ► arrows: Navigate moves | Home/End: First/Last move | Esc: Exit"
            ]

    def handle_review_button_click(self, pos):
        """Handle clicks on review navigation buttons."""
        # Define button areas
        width, height = self.renderer.width, self.renderer.height

        # Previous button (left 25% of screen bottom)
        prev_button = pygame.Rect(0, height - 50, width * 0.25, 50)
        # Next button (right 25% of screen bottom)
        next_button = pygame.Rect(width * 0.75, height - 50, width * 0.25, 50)
        # First move button (left 25% of screen top)
        first_button = pygame.Rect(0, 0, width * 0.25, 50)
        # Last move button (right 25% of screen top)
        last_button = pygame.Rect(width * 0.75, 0, width * 0.25, 50)
        # Exit button (center of screen top)
        exit_button = pygame.Rect(width * 0.4, 0, width * 0.2, 50)

        if prev_button.collidepoint(pos):
            return self.review_previous_state()
        elif next_button.collidepoint(pos):
            return self.review_next_state()
        elif first_button.collidepoint(pos):
            return self.review_first_state()
        elif last_button.collidepoint(pos):
            return self.review_last_state()
        elif exit_button.collidepoint(pos):
            self.exit_review_mode()
            return True

        return False

    def handle_point_click(self, point):
        """Handle a click on a board point with improved move validation."""
        if self.selected_point is None:
            # First click - select a point with player's pieces
            if self.can_select_point(point):
                self.selected_point = point
                self.log(f"Selected point {point}")
        else:
            # Second click - try to move to the target point
            success = self.try_move(self.selected_point, point)
            if success:
                self.log(f"Moved from {self.selected_point} to {point}")
            else:
                self.log(f"Invalid move from {self.selected_point} to {point}")

            self.selected_point = None

    def can_select_point(self, point):
        """Check if a point can be selected with improved validation logic."""
        color = self.current_player.get_color()

        # Check if player has pieces on the bar
        if self.board.has_pieces_on_bar(color):
            if (color == "White" and point == 25) or (color == "Black" and point == 0):
                return True
            else:
                self.log(f"{color} must move pieces from the bar first")
                return False

        # Check if the point has player's pieces
        has_pieces = self.board.count_pieces_at(point, color) > 0

        # Check if any of the possible moves start from this point
        valid_start_point = any(from_p == point for from_p, _ in self.possible_moves)

        return has_pieces and valid_start_point

    def try_move(self, from_point, to_point):
        """Try to move a piece with improved validation and animation."""
        color = self.current_player.get_color()

        # Get unused dice values
        unused_dice = self.dice.get_unused_values()

        # Quick check - is this move in our possible_moves list?
        if (from_point, to_point) not in self.possible_moves:
            return False

        # Find the appropriate dice value
        dice_value = self.move_validator.find_dice_for_move(from_point, to_point, color, unused_dice)
        if dice_value is None:
            return False

        # Make the move
        move_result = self.board.move_piece(from_point, to_point)
        if move_result:
            # Mark the die as used
            self.dice.mark_used(dice_value)

            # Record the move in history
            self.game_history.record_move(color, from_point, to_point, self.board,
                                          self.dice.get_values(), self.dice.used)

            # Record the move
            self.last_human_moves.append((from_point, to_point))

            # Add animation (stub for future implementation)
            self.renderer.add_move_animation(from_point, to_point, color)

            # Check if the turn is over
            if self.dice.all_used():
                self.end_turn()
            else:
                # Recalculate possible moves after this move
                self.calculate_possible_moves()

            return True

        return False

    def process_ai_turn(self):
        """Process the AI player's turn with improved timing and animation."""
        # Let the AI choose moves
        self.log(f"AI ({self.ai_player.get_color()}) thinking...")
        moves = self.ai_player.choose_moves(self.board, self.dice.get_values())
        self.log(f"AI chose moves: {moves}")

        # Store AI's moves for display
        self.last_ai_moves = moves.copy()

        # If no moves available, just end the turn
        if not moves:
            self.log("AI has no valid moves")
            self.end_turn()
            return

        # Execute each move with animation (in a more controlled way)
        for from_point, to_point in moves:
            # Make the move on the board
            self.board.move_piece(from_point, to_point)

            # Record the move in history
            self.game_history.record_move(self.ai_player.get_color(), from_point, to_point,
                                          self.board, self.dice.get_values(), self.dice.used)

            # Add animation (stub for future implementation)
            self.renderer.add_move_animation(from_point, to_point, self.ai_player.get_color())

            # Mark the appropriate die as used
            color = self.ai_player.get_color()
            dice_value = self.move_validator.find_dice_for_move(
                from_point, to_point, color, self.dice.get_unused_values())
            if dice_value:
                self.dice.mark_used(dice_value)

        # End AI turn
        self.end_turn()

    def end_turn(self):
        """End the current player's turn with improved flow control."""
        # Check for a winner
        winner = self.board.check_winner()
        if winner:
            self.game_state = self.STATE_GAME_OVER
            self.log(f"Game over! {winner} wins!")
            return

        # Switch players
        if self.current_player == self.human_player:
            self.current_player = self.ai_player
            # Keep human's last moves for display until AI plays
        else:
            self.current_player = self.human_player
            # Reset human's last moves when it's their turn again
            self.last_human_moves = []

        # Increment turn counter
        self.turn_count += 1
        self.log(f"Turn {self.turn_count}: {self.current_player.get_color()}'s turn")

        # Reset for next turn
        self.dice.reset()
        self.selected_point = None
        self.possible_moves = []
        self.cannot_move = False
        self.game_state = self.STATE_ROLL_DICE

    def update(self):
        """Update game state - called every frame with improved timing control."""
        current_time = time.time()

        # Handle animations and delays
        if self.roll_animation_active:
            # If enough time has passed, end the animation
            if current_time - self.animation_start_time > 0.3:  # 300ms delay
                self.roll_animation_active = False

                # If we're in "cannot move" state, end the turn
                if self.cannot_move:
                    self.end_turn()

        # Handle AI turn processing with a minimum think time
        if self.game_state == self.STATE_AI_TURN and not self.roll_animation_active:
            # Only process AI turn once enough time has passed
            if current_time - self.ai_thinking_start_time >= self.ai_min_think_time:
                self.process_ai_turn()

    def get_game_state(self):
        """Get the current game state for rendering with enhanced information."""
        if self.game_state == self.STATE_REVIEW:
            # Return the review state for rendering
            return {
                "state": self.STATE_REVIEW,
                "board": self.review_board,  # Use the historical board
                "dice_values": self.review_dice_values,
                "dice_used": self.review_dice_used,
                "review_messages": self.review_messages,
                "review_mode": True,
                "current_player": None,  # Not relevant in review mode
                "selected_point": None,
                "possible_moves": [],
                "last_ai_moves": [],
                "last_human_moves": [],
                "debug_mode": self.debug_mode
            }
        else:
            # Return the regular game state
            return {
                "state": self.game_state,
                "board": self.board,  # Regular board
                "current_player": self.current_player.get_color(),
                "dice_values": self.dice.get_values(),
                "dice_used": self.dice.used,
                "selected_point": self.selected_point,
                "possible_moves": self.possible_moves if self.show_possible_moves else [],
                "last_ai_moves": self.last_ai_moves,
                "last_human_moves": self.last_human_moves,
                "turn_count": self.turn_count,
                "cannot_move": self.cannot_move,
                "debug_mode": self.debug_mode,
                "review_mode": False
            }

    def toggle_debug_mode(self):
        """Toggle debug mode for development."""
        self.debug_mode = not self.debug_mode
        self.renderer.toggle_debug_mode()
        self.log(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}")

    def toggle_pause(self):
        """Toggle game pause state."""
        if self.game_state == self.STATE_PAUSED:
            # Resume from previous state
            self.game_state = self._pre_pause_state
            self.log("Game resumed")
        else:
            # Pause the game
            self._pre_pause_state = self.game_state
            self.game_state = self.STATE_PAUSED
            self.log("Game paused")

    def reset_game(self):
        """Reset the game to initial state."""
        self.log("Game reset")
        self.board.setup_initial_position()
        self.is_first_turn = True
        self.turn_count = 0
        self.last_ai_moves = []
        self.last_human_moves = []
        self.selected_point = None
        self.possible_moves = []
        self.cannot_move = False

        # Start a new history record
        self.game_history.start_new_game()

        # Exit review mode if active
        if self.game_state == self.STATE_REVIEW:
            self.exit_review_mode()

        self.determine_first_player()

    def log(self, message):
        """Log a game event if logging is enabled."""
        if not self.log_enabled:
            return

        timestamp = time.strftime("%H:%M:%S", time.localtime())
        log_entry = f"[{timestamp}] {message}"

        # Add to game log and print to console
        self.game_log.append(log_entry)
        print(log_entry)

        # Keep log at a reasonable size
        if len(self.game_log) > 100:
            self.game_log = self.game_log[-100:]

    def set_ai_difficulty(self, difficulty):
        """Set AI difficulty level."""
        if difficulty in ("easy", "medium", "hard"):
            self.ai_difficulty = difficulty
            if hasattr(self.ai_player, 'difficulty'):
                self.ai_player.difficulty = difficulty
            self.log(f"AI difficulty set to {difficulty}")