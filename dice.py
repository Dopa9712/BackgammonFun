# dice.py - Contains the Dice class for handling dice rolls

import random


class Dice:
    def __init__(self):
        """Initialize the dice with no values."""
        self.values = []
        self.used = []

    def roll(self):
        """Roll two dice and return their values.

        If the dice show the same number (doubles), the player gets to use
        that number four times.

        Returns:
            tuple: (dice_values, is_doubles)
                dice_values: A list of the dice values (2 or 4 elements)
                is_doubles: A boolean indicating if doubles were rolled
        """
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)

        # Check for doubles
        is_doubles = (die1 == die2)

        if is_doubles:
            # For doubles, the player gets to use each die four times
            self.values = [die1, die1, die1, die1]
        else:
            self.values = [die1, die2]

        # Reset used flags
        self.used = [False] * len(self.values)

        return self.values, is_doubles

    def get_values(self):
        """Get the current dice values.

        Returns:
            list: The current dice values
        """
        return self.values

    def get_unused_values(self):
        """Get dice values that haven't been used yet.

        Returns:
            list: Unused dice values
        """
        return [self.values[i] for i in range(len(self.values)) if not self.used[i]]

    def mark_used(self, value):
        """Mark a die with the given value as used.

        Args:
            value: The die value to mark as used

        Returns:
            bool: True if a die was successfully marked, False otherwise
        """
        for i in range(len(self.values)):
            if self.values[i] == value and not self.used[i]:
                self.used[i] = True
                return True
        return False

    def mark_used_at_index(self, index):
        """Mark a die at a specific index as used.

        Args:
            index: The index of the die to mark as used

        Returns:
            bool: True if successfully marked, False if index invalid or already used
        """
        if 0 <= index < len(self.values) and not self.used[index]:
            self.used[index] = True
            return True
        return False

    def all_used(self):
        """Check if all dice have been used.

        Returns:
            bool: True if all dice are used, False otherwise
        """
        return all(self.used)

    def has_unused(self):
        """Check if there are any unused dice.

        Returns:
            bool: True if there are unused dice, False otherwise
        """
        return any(not used for used in self.used)

    def reset(self):
        """Reset dice to empty state."""
        self.values = []
        self.used = []