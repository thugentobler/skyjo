import numpy as np

from game_elements import (
    Ablagestapel,
    Card,
    Deck,
)
from genome import Genome
from grid import Grid

ROWS: int = 3
COLS: int = 4


class Player:
    name: str
    grid: Grid
    genome: Genome

    def __init__(self, name: str, genome: Genome | None = None):
        self.name = name
        self.grid = Grid()
        self.genome = genome or Genome()

    def fill_grid(self, initial_cards: list[Card]):
        self.grid.fill_grid(initial_cards)

    def _place_decision(self, card: Card) -> tuple[int, int]:
        # Implement your decision logic here
        # For now, just return the first available cell
        gain: np.ndarray = self.grid.grid_values() - np.full(
            (ROWS, COLS), card.value, dtype=np.int64
        )
        column_match = self.grid.has_columns_with_same_value(card)
        column_gain = self.grid.grid_values(with_face_down=False)
        reveals_info = self.grid.grid_face_up
        # column_counts = self.grid.count_cards_by_column()
        # breaks_match = np.zeros(self.grid.grid_cards.shape, dtype=np.int_)
        # for col, counts in column_counts.items():
        #     for row in np.flatnonzero(self.grid.grid_face_up[:, col]):
        #         card = self.grid[row, col]
        #         if card is not None and counts.get(card, 0) >= 2:
        #             breaks_match[row, col] = 1

        gain_score = np.max(gain) * self.genome.params.w_gain

        for row in range(ROWS):
            for col in range(COLS):
                if not self.grid.grid_face_up[row][col]:
                    return row, col
        raise ValueError("No available cell to place the card")

    def place_card(self, card: Card, ablage: Ablagestapel) -> None:
        row, col = self._place_decision(card)

        return_card = self.grid[row, col]
        if return_card is None:
            raise ValueError("Cannot replace an empty grid cell")
        self.grid.flip_card(row, col)
        self.grid[row, col] = card
        ablage.add_card(return_card)

    def draw_card(self, deck: Deck, ablagestapel: Ablagestapel) -> Card:
        top_card = ablagestapel.show_top_card()
        col_dict = self.grid.has_columns_with_same_value(top_card)
        score = (
            top_card * self.genome.params.w_topcard
            + self.genome.params.w_column_len * len(col_dict)
            + self.genome.params.w_sum_cols * sum(col_dict.values())
        )
        if score >= self.genome.params.take_discard_thresh:
            return ablagestapel.draw_card()
        else:
            return deck.draw_card()

    def remove_column(self, col: int):
        if 0 <= col < 4:
            for row in range(3):
                self.grid.remove_column(col)
        else:
            raise ValueError("Invalid column")

    def display(self) -> str:
        result = f"{self.name}\n"
        result += self.grid.display()
        return result
