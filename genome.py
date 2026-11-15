import random


class Params:
    def __init__(self):
        self.w_topcard = random.uniform(0, 1)
        self.w_column_len = random.uniform(0, 1)
        self.w_sum_cols = random.uniform(0, 1)

        self.take_discard_thresh = random.uniform(0, 1)
        self.w_gain = random.uniform(0, 1)
        self.w_match = random.uniform(0, 1)
        self.w_col_bonus = random.uniform(0, 1)
        self.w_reveal = random.uniform(0, 1)
        self.w_break = random.uniform(0, 1)

    def __iter__(self):
        return iter(vars(self))


class Genome:
    fitness: float

    def __init__(self):
        self.params = Params()
        self.fitness = 0.0
