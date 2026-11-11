from typing import cast

import numpy as np
from numpy.typing import NDArray

from game_elements import (
    EXPECTED_CARD_VALUE,
    Ablagestapel,
    Card,
    Deck,
    Drawable,
)
from genetics import Genome


class Grid:
    grid_cards: NDArray[np.object_]
    grid_face_up: NDArray[np.bool_]
    columns_active: NDArray[np.int_]

    def __init__(self):
        self.grid_cards = np.full((3, 4), None, dtype=np.object_)
        self.grid_face_up = np.zeros((3, 4), dtype=np.bool_)
        self.columns_active = np.arange(4, dtype=np.int_)

    def fill_grid(self, cards: list[Card]):
        if len(cards) != 12:
            raise ValueError("Exactly 12 cards are required to fill the grid")
        self.grid_cards = np.array(cards, dtype=np.object_).reshape((3, 4))

    def flip_card(self, row, column):
        self._is_row_valid(row)
        self._is_column_valid(column)
        self.grid_face_up[row][column] = True

    def display(self) -> str:
        result = ""
        for row in range(3):
            for col in range(4):
                card = self.grid_cards[row][col]
                result += (
                    str(card)
                    if card and self.grid_face_up[row][col]
                    else " -- "
                )
                if col < 3:
                    result += " | "
            result += "\n"
        return result

    def remove_column(self, col: int):
        if not self.is_column_removable(col):
            raise ValueError("Column is not removable")

        self.columns_active = self.columns_active[self.columns_active != col]
        self.grid_cards[:, col] = None
        self.grid_face_up[:, col] = False

    def is_column_removable(self, col: int) -> bool:
        cards = [self.grid_cards[row][col] for row in range(3)]
        return (
            col in self.columns_active
            and all(card is not None for card in cards)
            and len({card.value for card in cards if card is not None}) == 1
        )

    def _visible_cards_in_column(self, col: int) -> list[Card]:
        self._is_column_valid(col)
        cards = [
            self.grid_cards[row][col]
            for row in range(3)
            if self.grid_face_up[row][col]
        ]
        return [card for card in cards if card is not None]

    def has_columns_with_same_value(self, card: Card) -> dict[int, int]:
        matching_columns = {}
        for col in range(4):
            cards = self._visible_cards_in_column(col)
            # checks if all visible cards in the column are the same and match the given card
            if len(set(cards)) == 1 and cards[0] == card:
                matching_columns[col] = len(cards)
        return matching_columns

    def count_cards_by_column(self) -> dict[int, dict[Card, int]]:
        """Count visible cards by value in each active column."""
        counts = np.zeros(self.grid_cards.shape)

        for col in self.columns_active:
            column_counts = {}
            for card in self._visible_cards_in_column(int(col)):
                column_counts[card] = column_counts.get(card, 0) + 1
            counts[int(col)] = column_counts
        return counts

    def grid_values(self, with_face_down: bool = True) -> NDArray[np.float64]:
        values = np.full((3, 4), EXPECTED_CARD_VALUE, dtype=np.float64)
        if not with_face_down:
            values[:] = np.nan
        for row, col in np.ndindex(values.shape):
            card = self.grid_cards[row, col]
            if self.grid_face_up[row, col] and isinstance(card, Card):
                values[row, col] = card.value
        return values

    def _column_sums(self, with_face_down: bool = True) -> NDArray[np.float64]:
        return np.array(
            [
                sum(self.grid_values(with_face_down=with_face_down)[:, col])
                for col in range(4)
            ]
        )

    def _is_column_valid(self, column: int) -> None:
        if not (0 <= column < 4):
            raise ValueError("Invalid column")
        if not column in self.columns_active:
            raise ValueError("Column is not active")

    def _is_row_valid(self, row: int) -> None:
        if not (0 <= row < 3):
            raise ValueError("Invalid row")

    def __getitem__(self, key: tuple[int, int]) -> Card | None:
        """Enable reading: card = grid[row, col]"""
        row, col = key
        self._is_column_valid(col)
        self._is_row_valid(row)
        return cast(Card | None, self.grid_cards[row, col])

    def __setitem__(self, key: tuple[int, int], value: Card | None) -> None:
        """Enable writing: grid[row, col] = card"""
        row, col = key
        self._is_row_valid(row)
        self._is_column_valid(col)
        self.grid_cards[row, col] = value


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

    def place_decision(self, card: Card) -> tuple[int, int]:
        # Implement your decision logic here
        # For now, just return the first available cell
        gain = np.array(self.grid.grid_values()) - card.value
        column_match = self.grid.has_columns_with_same_value(card)
        column_gain = self.grid.grid_values(with_face_down=False)
        reveals_info = self.grid.grid_face_up
        column_counts = self.grid.count_cards_by_column()
        breaks_match = np.zeros(self.grid.grid_cards.shape, dtype=np.int_)
        for col, counts in column_counts.items():
            for row in np.flatnonzero(self.grid.grid_face_up[:, col]):
                card = self.grid[row, col]
                if card is not None and counts.get(card, 0) >= 2:
                    breaks_match[row, col] = 1

        for row in range(3):
            for col in range(4):
                if not self.grid.grid_face_up[row][col]:
                    return row, col
        raise ValueError("No available cell to place the card")

    def place_card(self, card: Card, ablage: Ablagestapel) -> None:
        row, col = self.place_decision(card)

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
            top_card * self.genome.params[0]
            + self.genome.params[1] * len(col_dict)
            + self.genome.params[2] * sum(col_dict.values())
        )
        if score >= self.genome.take_discard_thresh:
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
