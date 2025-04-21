# controller/ai_player.py - Enhanced AI player implementation

import random
import sys
import os
import time

# Add parent directory to path to allow imports from model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.player import Player
from model.move_validator import MoveValidator


class AIPlayer(Player):
    """Enhanced AI player for backgammon with better strategy."""

    def __init__(self, color, difficulty="medium"):
        """Initialize an AI player with configurable difficulty.

        Args:
            color: "White" or "Black" - the AI's color
            difficulty: "easy", "medium", or "hard" - affects AI strategy
        """
        super().__init__(color)
        self.move_validator = None  # Initialize in choose_moves
        self.difficulty = difficulty

        # Strategy weights - will be set based on difficulty
        self.weights = self._get_difficulty_weights(difficulty)

        # Performance tracking
        self.move_times = []
        self.avg_move_time = 0
        self.max_sequences_evaluated = 0

        # Debug mode
        self.debug_mode = False

    def _get_difficulty_weights(self, difficulty):
        """Get strategy weights based on difficulty level.

        Args:
            difficulty: "easy", "medium", or "hard"

        Returns:
            dict: Strategy weights for evaluation
        """
        if difficulty == "easy":
            return {
                'bear_off': 12,  # Weight for bearing off pieces
                'hit': 5,  # Weight for hitting opponent blots
                'home_board': 8,  # Weight for pieces in home board
                'block': 3,  # Weight for creating blocks
                'blot_vuln': 1,  # Weight for blot vulnerability penalty
                'progress': 2,  # Weight for forward progress
                'bar': 8,  # Weight for bar penalty
                'opponent_bar': 3,  # Weight for opponent on bar bonus
                'randomness': 0.3,  # Random factor (makes AI less optimal)
                'endgame_bearing': 15,  # Weight for endgame bearing off strategy
                'prime': 2,  # Weight for creating primes (6 consecutive points)
                'opponent_anchor': 1  # Weight for opponent anchors in home board penalty
            }
        elif difficulty == "hard":
            return {
                'bear_off': 20,  # Weight for bearing off pieces
                'hit': 12,  # Weight for hitting opponent blots
                'home_board': 14,  # Weight for pieces in home board
                'block': 10,  # Weight for creating blocks
                'blot_vuln': 8,  # Weight for blot vulnerability penalty
                'progress': 6,  # Weight for forward progress
                'bar': 15,  # Weight for bar penalty
                'opponent_bar': 9,  # Weight for opponent on bar bonus
                'randomness': 0.01,  # Minimal randomness
                'endgame_bearing': 25,  # Weight for endgame bearing off strategy
                'prime': 12,  # Weight for creating primes (6 consecutive points)
                'opponent_anchor': 8  # Weight for opponent anchors in home board penalty
            }
        else:  # medium (default)
            return {
                'bear_off': 16,  # Weight for bearing off pieces
                'hit': 8,  # Weight for hitting opponent blots
                'home_board': 10,  # Weight for pieces in home board
                'block': 6,  # Weight for creating blocks
                'blot_vuln': 4,  # Weight for blot vulnerability penalty
                'progress': 4,  # Weight for forward progress
                'bar': 12,  # Weight for bar penalty
                'opponent_bar': 6,  # Weight for opponent on bar bonus
                'randomness': 0.05,  # Low randomness
                'endgame_bearing': 20,  # Weight for endgame bearing off strategy
                'prime': 7,  # Weight for creating primes (6 consecutive points)
                'opponent_anchor': 4  # Weight for opponent anchors in home board penalty
            }

    def get_name(self):
        """Get the AI player's name with difficulty level."""
        return f"AI ({self.color}, {self.difficulty})"

    def choose_moves(self, board, dice_values):
        """Choose the best moves for the current dice roll with improved strategy.

        Args:
            board: The game board
            dice_values: List of available dice values

        Returns:
            list: List of (from_point, to_point) tuples representing moves
        """
        start_time = time.time()

        # Initialize the move validator if needed
        if self.move_validator is None:
            self.move_validator = MoveValidator(board)

        # Get all possible move sequences
        all_possible_moves = self.move_validator.get_all_possible_move_sequences(
            self.color, dice_values, board)

        # Track for performance monitoring
        self.max_sequences_evaluated = max(self.max_sequences_evaluated, len(all_possible_moves))

        # If no moves available, return empty list
        if not all_possible_moves:
            return []

        # Evaluate each move sequence and choose the best one
        best_sequence = self.evaluate_move_sequences(board, all_possible_moves)

        # Calculate move time for performance tracking
        move_time = time.time() - start_time
        self.move_times.append(move_time)
        if len(self.move_times) > 10:
            self.move_times.pop(0)  # Keep only last 10 moves
        self.avg_move_time = sum(self.move_times) / len(self.move_times)

        if self.debug_mode:
            print(f"AI evaluated {len(all_possible_moves)} move sequences in {move_time:.3f}s")
            print(f"Selected sequence: {best_sequence}")

        return best_sequence

    def evaluate_move_sequences(self, board, move_sequences):
        """Evaluate all move sequences and choose the best one with improved heuristics.

        Args:
            board: The current board state
            move_sequences: List of move sequences to evaluate

        Returns:
            list: The best move sequence
        """
        if not move_sequences:
            return []

        best_score = float('-inf')
        best_sequence = move_sequences[0]

        # For debugging - track scores and their components
        scores = []

        for sequence in move_sequences:
            # Create a temporary board to simulate this sequence
            temp_board = board.clone()

            # Apply all moves in the sequence
            for from_point, to_point in sequence:
                temp_board.move_piece(from_point, to_point)

            # Score the resulting position
            score, components = self._evaluate_position(temp_board)

            # Store score info for debugging
            if self.debug_mode:
                scores.append((score, sequence, components))

            if score > best_score:
                best_score = score
                best_sequence = sequence

        # Print detailed analysis in debug mode
        if self.debug_mode and scores:
            # Sort by score descending
            scores.sort(key=lambda x: x[0], reverse=True)
            print("\nTop 3 move sequences:")
            for i, (score, seq, components) in enumerate(scores[:3]):
                print(f"{i + 1}. Score: {score:.2f}, Sequence: {seq}")
                for component, value in components.items():
                    print(f"   - {component}: {value:.2f}")
                print()

        return best_sequence

    def _evaluate_position(self, board):
        """Evaluate a board position for the AI with enhanced strategic evaluation.

        Uses multiple strategic elements weighted by AI difficulty.

        Args:
            board: The board to evaluate

        Returns:
            tuple: (score, components) where score is the total position score and
                  components is a dictionary of individual evaluation factors
        """
        score = 0
        opponent_color = "Black" if self.color == "White" else "White"

        # Track score components for debugging
        components = {}

        # 1. Count pieces that have been borne off
        home_index = 27 if self.color == "White" else 26
        opponent_home_index = 26 if self.color == "White" else 27
        born_off_score = len(board.points[home_index]) * self.weights['bear_off']
        score += born_off_score
        components['pieces_borne_off'] = born_off_score / self.weights['bear_off']

        # Penalize for opponent pieces borne off
        opp_born_off_score = -len(board.points[opponent_home_index]) * self.weights['bear_off']
        score += opp_born_off_score
        components['opponent_borne_off'] = opp_born_off_score / self.weights['bear_off']

        # 2. Penalize for pieces on the bar
        bar_index = 25 if self.color == "White" else 0
        opponent_bar_index = 0 if self.color == "White" else 25
        bar_score = -len(board.points[bar_index]) * self.weights['bar']
        score += bar_score
        components['pieces_on_bar'] = bar_score / self.weights['bar']

        # Bonus for opponent pieces on the bar
        opp_bar_score = len(board.points[opponent_bar_index]) * self.weights['opponent_bar']
        score += opp_bar_score
        components['opponent_on_bar'] = opp_bar_score / self.weights['opponent_bar']

        # 3. Check if we can bear off
        can_bear_off = board.can_bear_off(self.color)
        if can_bear_off:
            # Add an extra bonus for having all pieces in the home board
            score += self.weights['home_board']
            components['all_in_home'] = 1.0

            # Add bonus for pieces close to bearing off with improved weighting
            if self.color == "White":
                bearing_score = 0
                for point in range(19, 25):  # White's home board
                    count = board.count_pieces_at(point, self.color)
                    # More points for pieces closer to bearing off
                    bearing_score += count * (point - 18) * self.weights['endgame_bearing'] / 36
                score += bearing_score
                components['bearing_position'] = bearing_score / self.weights['endgame_bearing']
            else:
                bearing_score = 0
                for point in range(1, 7):  # Black's home board
                    count = board.count_pieces_at(point, self.color)
                    # More points for pieces closer to bearing off
                    bearing_score += count * (7 - point) * self.weights['endgame_bearing'] / 36
                score += bearing_score
                components['bearing_position'] = bearing_score / self.weights['endgame_bearing']
        else:
            components['all_in_home'] = 0.0
            components['bearing_position'] = 0.0

        # 4. Evaluate board position with improved strategy
        if self.color == "White":
            # White pieces want to move from 1 to 24
            progress_score = 0
            block_score = 0
            blot_score = 0
            hit_score = 0
            home_score = 0
            prime_score = 0

            # Count pieces in home board and check for primes
            consecutive_points = 0
            max_consecutive = 0

            for point in range(1, 25):
                count = board.count_pieces_at(point, self.color)
                if count > 0:
                    # Progress score - pieces closer to home board
                    if point < 19:  # Not yet in home board
                        progress_score += count * point * self.weights['progress'] / 300
                    else:  # Home board bonus
                        home_score += count * self.weights['home_board'] / 15

                    # Blot vulnerability (single pieces)
                    if count == 1:
                        # Calculate potential hit risk
                        risk = self._calculate_hit_risk(board, point, opponent_color)
                        blot_score -= risk * self.weights['blot_vuln'] / 5

                    # Blocks (2+ pieces are good)
                    if count >= 2:
                        block_score += self.weights['block'] / 24
                        # Check for consecutive blocks (primes)
                        consecutive_points += 1
                        max_consecutive = max(max_consecutive, consecutive_points)
                    else:
                        consecutive_points = 0

                    # Check for potential hits
                    opponent_count = board.count_pieces_at(point, opponent_color)
                    if opponent_count == 1:
                        hit_score += self.weights['hit'] / 8
                else:
                    consecutive_points = 0

                # Check for opponent anchors in our home board
                if 19 <= point <= 24:
                    if board.count_pieces_at(point, opponent_color) >= 2:
                        score -= self.weights['opponent_anchor'] / 6

            # Bonus for primes (6 consecutive points)
            if max_consecutive >= 6:
                prime_score = self.weights['prime']
            elif max_consecutive >= 4:
                prime_score = self.weights['prime'] / 2

            # Add all component scores
            score += progress_score + block_score + blot_score + hit_score + home_score + prime_score

            # Track components
            components.update({
                'forward_progress': progress_score / self.weights['progress'] if self.weights['progress'] > 0 else 0,
                'blocks': block_score / self.weights['block'] if self.weights['block'] > 0 else 0,
                'blot_vulnerability': blot_score / self.weights['blot_vuln'] if self.weights['blot_vuln'] > 0 else 0,
                'hitting_potential': hit_score / self.weights['hit'] if self.weights['hit'] > 0 else 0,
                'home_board_presence': home_score / self.weights['home_board'] if self.weights['home_board'] > 0 else 0,
                'prime_formation': prime_score / self.weights['prime'] if self.weights['prime'] > 0 else 0
            })

        else:
            # Black pieces want to move from 24 to 1
            progress_score = 0
            block_score = 0
            blot_score = 0
            hit_score = 0
            home_score = 0
            prime_score = 0

            # Count pieces in home board and check for primes
            consecutive_points = 0
            max_consecutive = 0

            for point in range(24, 0, -1):
                count = board.count_pieces_at(point, self.color)
                if count > 0:
                    # Progress score - pieces closer to home board
                    if point > 6:  # Not yet in home board
                        progress_score += count * (25 - point) * self.weights['progress'] / 300
                    else:  # Home board bonus
                        home_score += count * self.weights['home_board'] / 15

                    # Blot vulnerability (single pieces)
                    if count == 1:
                        # Calculate potential hit risk
                        risk = self._calculate_hit_risk(board, point, opponent_color)
                        blot_score -= risk * self.weights['blot_vuln'] / 5

                    # Blocks (2+ pieces are good)
                    if count >= 2:
                        block_score += self.weights['block'] / 24
                        # Check for consecutive blocks (primes)
                        consecutive_points += 1
                        max_consecutive = max(max_consecutive, consecutive_points)
                    else:
                        consecutive_points = 0

                    # Check for potential hits
                    opponent_count = board.count_pieces_at(point, opponent_color)
                    if opponent_count == 1:
                        hit_score += self.weights['hit'] / 8
                else:
                    consecutive_points = 0

                # Check for opponent anchors in our home board
                if 1 <= point <= 6:
                    if board.count_pieces_at(point, opponent_color) >= 2:
                        score -= self.weights['opponent_anchor'] / 6

            # Bonus for primes (6 consecutive points)
            if max_consecutive >= 6:
                prime_score = self.weights['prime']
            elif max_consecutive >= 4:
                prime_score = self.weights['prime'] / 2

            # Add all component scores
            score += progress_score + block_score + blot_score + hit_score + home_score + prime_score

            # Track components
            components.update({
                'forward_progress': progress_score / self.weights['progress'] if self.weights['progress'] > 0 else 0,
                'blocks': block_score / self.weights['block'] if self.weights['block'] > 0 else 0,
                'blot_vulnerability': blot_score / self.weights['blot_vuln'] if self.weights['blot_vuln'] > 0 else 0,
                'hitting_potential': hit_score / self.weights['hit'] if self.weights['hit'] > 0 else 0,
                'home_board_presence': home_score / self.weights['home_board'] if self.weights['home_board'] > 0 else 0,
                'prime_formation': prime_score / self.weights['prime'] if self.weights['prime'] > 0 else 0
            })

        # 5. Add a controlled amount of randomness based on difficulty
        randomness = random.uniform(0, self.weights['randomness'])
        score += randomness
        components['randomness'] = randomness / self.weights['randomness'] if self.weights['randomness'] > 0 else 0

        return score, components

    def _calculate_hit_risk(self, board, point, opponent_color):
        """Calculate the risk of a blot being hit by the opponent.

        Args:
            board: The board state
            point: The point number with the blot
            opponent_color: The opponent's color

        Returns:
            float: Risk factor (0-1) with higher values indicating higher risk
        """
        # Basic risk assessment based on distance from opponent pieces
        risk = 0

        if self.color == "White":
            # For White, check Black pieces that can hit (points > our_point)
            for i in range(point + 1, min(point + 6, 25)):
                if board.count_pieces_at(i, opponent_color) > 0:
                    # Closer pieces pose higher risk
                    risk += (7 - (i - point)) / 6

            # Check bar - highest risk
            if board.count_pieces_at(0, opponent_color) > 0:
                # Direct entry to our point
                if point <= 6:
                    risk += 1.0
        else:
            # For Black, check White pieces that can hit (points < our_point)
            for i in range(max(point - 6, 0), point):
                if board.count_pieces_at(i, opponent_color) > 0:
                    # Closer pieces pose higher risk
                    risk += (7 - (point - i)) / 6

            # Check bar - highest risk
            if board.count_pieces_at(25, opponent_color) > 0:
                # Direct entry to our point
                if point >= 19:
                    risk += 1.0

        # Normalize risk to 0-1 range
        return min(risk, 1.0)

    def set_difficulty(self, difficulty):
        """Change the AI difficulty level on the fly.

        Args:
            difficulty: "easy", "medium", or "hard"
        """
        if difficulty in ("easy", "medium", "hard"):
            self.difficulty = difficulty
            self.weights = self._get_difficulty_weights(difficulty)

    def toggle_debug_mode(self):
        """Toggle debug mode for AI analysis output."""
        self.debug_mode = not self.debug_mode
        return self.debug_mode