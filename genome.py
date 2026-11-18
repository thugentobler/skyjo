import json
import os
import random


class Params:
    def __init__(self):
        # weights for draw decision making
        self.w_topcard = random.uniform(0, 1)
        self.w_count = random.uniform(0, 1)
        self.w_col_count = random.uniform(0, 1)
        self.w_gain_topcard = random.uniform(0, 1)
        self.take_discard_thresh = random.uniform(0, 1)

        # weights for place decision making
        self.w_gain = random.uniform(0, 1)
        self.w_match = random.uniform(0, 1)
        self.w_col_bonus = random.uniform(0, 1)
        self.w_reveal = random.uniform(0, 1)
        self.w_breaks_match = random.uniform(0, 1)
        self.place_card_thresh = random.uniform(0, 1)
        self.w_gain_next_player = random.uniform(0, 1)

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
        for key, value in params_dict.items():
            setattr(self.params, key, value)
