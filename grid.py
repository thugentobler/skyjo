from typing import cast

import numpy as np
from numpy.typing import NDArray

from game_elements import (
    EXPECTED_CARD_VALUE,
    Card,
)

ROWS: int = 3
COLS: int = 4


class Grid:
    grid_cards: NDArray[np.object_]
    grid_face_up: NDArray[np.bool_]
    columns_active: NDArray[np.int_]

    def __init__(self):
        self.grid_cards = np.full((ROWS, COLS), None, dtype=np.object_)
        self.grid_face_up = np.zeros((ROWS, COLS), dtype=np.bool_)
        self.columns_active = np.arange(COLS, dtype=np.int_)

    def fill_grid(self, cards: list[Card]):
        if len(cards) != 12:
            raise ValueError("Exactly 12 cards are required to fill the grid")
        self.grid_cards = np.array(cards, dtype=np.object_).reshape((3, 4))

    def place_card(self, row: int, col: int, card: Card) -> Card:
        self._is_row_valid(row)
        self._is_column_valid(col)
        return_card = self.grid_cards[row, col]
        if return_card is None:
            raise ValueError("Cannot replace an empty grid cell")
        self.grid_cards[row, col] = card
        self.flip_card(row, col)

        # Check if a column is now complete and should be removed
        for c in range(COLS):
            if self.is_column_removable(c):
                self.remove_column(c)
        return return_card

    def flip_card(self, row: int, col: int):
        self._is_row_valid(row)
        self._is_column_valid(col)
        self.grid_face_up[row, col] = True

    def display(self) -> str:
        result = ""
        for row in range(ROWS):
            for col in range(COLS):
                card = self.grid_cards[row, col]
                result += (
                    " -- "
                    if col not in self.columns_active
                    else (
                        str(card)
                        if card
                        and self.grid_face_up[row, col]
                        and isinstance(card, Card)
                        else "[  ]"
                    )
                )
                if col < COLS - 1:
                    result += " | "
            result += "\n"
        return result

    def remove_column(self, col: int):
        if not self.is_column_removable(col):
            raise ValueError("Column is not removable")

        self.columns_active = self.columns_active[self.columns_active != col]
        self.grid_cards[:, col] = None

    def is_column_removable(self, col: int) -> bool:
        cards = [self.grid_cards[row, col] for row in range(ROWS)]
        return (
            col in self.columns_active
            and all(card is not None for card in cards)
            and all(self.grid_face_up[row, col] for row in range(ROWS))
            and len({card.value for card in cards if card is not None}) == 1
        )

    def _visible_cards_in_column(self, col: int) -> list[Card]:
        self._is_column_valid(col)
        cards = [
            self.grid_cards[row, col]
            for row in range(ROWS)
            if self.grid_face_up[row, col]
        ]
        return [card for card in cards if card is not None]

    def has_columns_with_same_value(self, card: Card) -> dict[int, int]:
        matching_columns = {}
        for col in range(COLS):
            cards = self._visible_cards_in_column(col)
            # checks if all visible cards in the column are the same and match the given card
            if len(set(cards)) == 1 and cards[0] == card:
                matching_columns[col] = len(cards)
        return matching_columns

    # def count_cards_by_column(self) -> dict[int, dict[Card, int]]:
    #     """Count visible cards by value in each active column."""
    #     counts = np.zeros(self.grid_cards.shape)

    #     for col in self.columns_active:
    #         column_counts = {}
    #         for card in self._visible_cards_in_column(int(col)):
    #             column_counts[card] = column_counts.get(card, 0) + 1
    #         counts[int(col)] = column_counts
    #     return counts

    def grid_values(self, with_face_down: bool = True) -> NDArray[np.int64]:
        values = np.full((ROWS, COLS), EXPECTED_CARD_VALUE, dtype=np.int64)
        if not with_face_down:
            values = np.full((ROWS, COLS), np.nan, dtype=np.int64)
        for row, col in np.ndindex(values.shape):
            card = self.grid_cards[row, col]
            if self.grid_face_up[row, col] and isinstance(card, Card):
                values[row, col] = card.value
        return values

    def total_score(self) -> int:
        return int(np.nansum(self.grid_values(with_face_down=False)))

    def _column_sums(self, with_face_down: bool = True) -> NDArray[np.float64]:
        return np.array(
            [
                sum(self.grid_values(with_face_down=with_face_down)[:, col])
                for col in range(COLS)
            ]
        )

    def reveal_all(self) -> None:
        self.grid_face_up[:, :] = True

    def first_available_cell(self) -> tuple[int, int]:
        for row in range(ROWS):
            for col in range(COLS):
                if not self.grid_face_up[row, col]:
                    return row, col
        raise ValueError("No available cell to place the card")

    @property
    def is_full(self) -> bool:
        return bool(self.grid_face_up.all())

    def _is_column_valid(self, column: int) -> None:
        if not (0 <= column < COLS):
            raise ValueError("Invalid column")
        if not column in self.columns_active:
            raise ValueError("Column is not active")

    def _is_row_valid(self, row: int) -> None:
        if not (0 <= row < ROWS):
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
