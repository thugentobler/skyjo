import json
import os
import random


class Params:
    def __init__(self):
        # weights for draw decision making
        # weight for the top card value
        self.w_topcard = random.uniform(0, 1)
        # weight for the count of matching cards
        self.w_count = random.uniform(0, 1)
        # weight for the count of matching columns
        self.w_col_count = random.uniform(0, 1)
        # weight for the gain from taking the top card
        self.w_gain_topcard = random.uniform(0, 1)
        # threshold for taking the top card from ablagestapel
        self.take_ablagestapel_thresh = random.uniform(0, 1)

        # weights for place decision making
        # weight for the gain
        self.w_gain = random.uniform(0, 1)
        # weight for the match
        self.w_match = random.uniform(0, 1)
        # weight for the column bonus
        self.w_col_bonus = random.uniform(0, 1)
        # weight for revealing a card
        self.w_reveal = random.uniform(0, 1)
        # weight for breaking a match
        self.w_breaks_match = random.uniform(0, 1)
        # weight for the gain of the next player
        self.w_gain_next_player = random.uniform(0, 1)

        # weights for turn over decision
        # threshold for discarding a drawn card
        self.discard_thresh = random.uniform(0, 1)

    def __iter__(self):
        return iter(vars(self))


class Genome:
    fitness: float

    def __init__(self):
        self.params = Params()
        self.fitness = 0.0

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(vars(self.params), f)

    def load(self, filepath: str):
        with open(filepath, "r") as f:
            params_dict = json.load(f)
        # Reset all params to 0 for backward compatibility
        for key in vars(self.params):
            setattr(self.params, key, 0)
        # Update with loaded values
        for key, value in params_dict.items():
            setattr(self.params, key, value)
