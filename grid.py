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
    columns_active: NDArray[np.bool_]

    def __init__(self):
        self.grid_cards = np.full((ROWS, COLS), None, dtype=np.object_)
        self.grid_face_up = np.zeros((ROWS, COLS), dtype=np.bool_)
        self.columns_active = np.ones(COLS, dtype=np.bool_)

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
                    if not self.columns_active[col]
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

        self.columns_active[col] = False
        self.grid_cards[:, col] = None

    def is_column_removable(self, col: int) -> bool:
        cards = [self.grid_cards[row, col] for row in range(ROWS)]
        return (
            self.columns_active[col]
            and all(card is not None for card in cards)
            and all(self.grid_face_up[row, col] for row in range(ROWS))
            and len({card.value for card in cards if card is not None}) == 1
        )

    # Function for the genome to evaluate potential moves based on different criteria

    def _gain(self, card: Card) -> NDArray[np.int64]:
        gains = np.full((ROWS, COLS), card.value, dtype=np.int64)
        values = self._values(with_face_down=True)
        return gains - values

    def _match(self, card: Card) -> NDArray[np.int64]:
        cards_match = self.grid_cards == card
        return (cards_match & self.grid_face_up).astype(np.int64)

    def _col_bonus(self, card: Card) -> NDArray[np.int64]:
        col_bonus = np.zeros((ROWS, COLS), dtype=np.int64)
        for col in range(COLS):
            for row in range(ROWS):
                temp = self.grid_cards.copy()
                temp[row, col] = card
                cards_of_col = [temp[r, col] for r in range(ROWS)]
                if (
                    self.columns_active[col]
                    and all(card is not None for card in cards_of_col)
                    and all(
                        self.grid_face_up[r, col]
                        for r in range(ROWS)
                        if r != row
                    )
                    and len(
                        {
                            card.value
                            for card in cards_of_col
                            if card is not None
                        }
                    )
                    == 1
                ):
                    col_bonus[row, col] = 1
        return col_bonus

    def _reveal(self, card: Card) -> NDArray[np.int64]:
        return np.where(self.grid_face_up, 1, 0)

    def _breaks_match(self, card: Card) -> NDArray[np.int64]:
        cards_match = self.grid_cards == card
        return ((~cards_match) & self.grid_face_up).astype(np.int64)

    def _gain_next_player(
        self, card: Card, next_player_grid: NDArray[np.int64]
    ) -> NDArray[np.int64]:
        gains = np.zeros((ROWS, COLS), dtype=np.int64)
        for row, col in np.ndindex(self.grid_cards.shape):
            discard_card = self.grid_cards[row, col]
            temp = next_player_grid.copy()
            temp[row, col] = (
                discard_card.value
                if isinstance(discard_card, Card)
                else EXPECTED_CARD_VALUE
            )
            if np.all(temp[:, col] != EXPECTED_CARD_VALUE):
                gains[row, col] = 1
        return gains

    def _values(self, with_face_down: bool = True) -> NDArray[np.int64]:
        values = np.full((ROWS, COLS), EXPECTED_CARD_VALUE, dtype=np.int64)
        if not with_face_down:
            values = np.full((ROWS, COLS), np.nan, dtype=np.int64)
        for row, col in np.ndindex(values.shape):
            card = self.grid_cards[row, col]
            if self.grid_face_up[row, col] and isinstance(card, Card):
                values[row, col] = card.value
        return values

    def total_score(self) -> int:
        return int(np.nansum(self._values(with_face_down=False)))

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
        if not self.columns_active[column]:
            raise ValueError("Column is not active")

    def _is_row_valid(self, row: int) -> None:
        if not (0 <= row < ROWS):
            raise ValueError("Invalid row")

    def __getitem__(self, key: tuple[int, int]) -> Card | None:
        """Enable reading: card = grid[row, col]"""
        row, col = key
        self._is_column_valid(col)
        self._is_row_valid(row)
        if not self.grid_face_up[row, col]:
            return None
        return cast(Card | None, self.grid_cards[row, col])

    def __setitem__(self, key: tuple[int, int], value: Card | None) -> None:
        """Enable writing: grid[row, col] = card"""
        row, col = key
        self._is_row_valid(row)
        self._is_column_valid(col)
        self.grid_cards[row, col] = value
