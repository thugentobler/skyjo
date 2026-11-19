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
    _grid_cards: NDArray[np.object_]
    _grid_face_up: NDArray[np.bool_]
    columns_active: NDArray[np.bool_]

    def __init__(self):
        self._grid_cards = np.full((ROWS, COLS), None, dtype=np.object_)
        self._grid_face_up = np.zeros((ROWS, COLS), dtype=np.bool_)
        self.columns_active = np.ones(COLS, dtype=np.bool_)

    def fill_grid(self, cards: list[Card]):
        if len(cards) != 12:
            raise ValueError("Exactly 12 cards are required to fill the grid")
        self._grid_cards = np.array(cards, dtype=np.object_).reshape((3, 4))

    def place_card(self, row: int, col: int, card: Card) -> Card:
        if not self._is_row_valid(row) or not self._is_column_valid(col):
            raise ValueError("Invalid row or column")
        return_card = self._grid_cards[row, col]
        if return_card is None:
            raise ValueError("Cannot replace an empty grid cell")
        self._grid_cards[row, col] = card
        self.flip_card(row, col)

        # Check if a column is now complete and should be removed
        for c in range(COLS):
            if self.is_column_removable(c):
                self.remove_column(c)
        return return_card

    def flip_card(self, row: int, col: int):
        if not self._is_row_valid(row) or not self._is_column_valid(col):
            raise ValueError("Invalid row or column")
        self._grid_face_up[row, col] = True

    def display(self) -> str:
        result = ""
        for row in range(ROWS):
            for col in range(COLS):
                card = self._grid_cards[row, col]
                result += (
                    " -- "
                    if not self.columns_active[col]
                    else (
                        str(card)
                        if card
                        and self._grid_face_up[row, col]
                        and isinstance(card, Card)
                        else "[  ]"
                    )
                )
                if col < COLS - 1:
                    result += " | "
            result += "\n"
        return result

    def grid_face_up(self) -> NDArray[np.bool_]:
        return self._grid_face_up.copy()

    def is_face_down_and_active(self, row: int, col: int) -> bool:
        if not self._is_row_valid(row) or not self._is_column_valid(col):
            raise ValueError("Invalid row or column")
        return not self._grid_face_up[row, col] and self.columns_active[col]

    def remove_column(self, col: int):
        if not self.is_column_removable(col):
            raise ValueError("Column is not removable")

        self.columns_active[col] = False
        self._grid_cards[:, col] = None

    def is_column_removable(self, col: int) -> bool:
        cards = [self._grid_cards[row, col] for row in range(ROWS)]
        return (
            self.columns_active[col]
            and all(card is not None for card in cards)
            and all(self._grid_face_up[row, col] for row in range(ROWS))
            and len({card.value for card in cards if card is not None}) == 1
        )

    # Function for the genome to evaluate potential moves based on different criteria

    def _gain(self, card: Card) -> NDArray[np.float64]:
        gains = np.full((ROWS, COLS), card.value, dtype=np.float64)
        values = self._values(with_face_down=True)
        return gains - values

    def _match(self, card: Card) -> NDArray[np.int64]:
        cards_match = self._grid_cards == card
        return (cards_match & self._grid_face_up).astype(np.int64)

    def _col_bonus(self, card: Card) -> NDArray[np.int64]:
        col_bonus = np.zeros((ROWS, COLS), dtype=np.int64)
        for col in range(COLS):
            for row in range(ROWS):
                temp = self._grid_cards.copy()
                temp[row, col] = card
                cards_of_col = [temp[r, col] for r in range(ROWS)]
                if (
                    self.columns_active[col]
                    and all(card is not None for card in cards_of_col)
                    and all(
                        self._grid_face_up[r, col]
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
        return np.where(self._grid_face_up, 1, 0)

    def _breaks_match(self, card: Card) -> NDArray[np.int64]:
        cards_match = self._grid_cards == card
        return ((~cards_match) & self._grid_face_up).astype(np.int64)

    def _gain_next_player(
        self, card: Card, next_player_grid: NDArray[np.float64]
    ) -> NDArray[np.int64]:
        gains = np.zeros((ROWS, COLS), dtype=np.int64)
        for row, col in np.ndindex(self._grid_cards.shape):
            discard_card = self._grid_cards[row, col]
            temp = next_player_grid.copy()
            temp[row, col] = (
                discard_card.value
                if isinstance(discard_card, Card)
                else EXPECTED_CARD_VALUE
            )
            if np.all(temp[:, col] != EXPECTED_CARD_VALUE):
                gains[row, col] = 1
        return gains

    def _values(self, with_face_down: bool = True) -> NDArray[np.float64]:
        if with_face_down:
            values = np.full(
                (ROWS, COLS), EXPECTED_CARD_VALUE, dtype=np.float64
            )
        else:
            values = np.full((ROWS, COLS), np.nan, dtype=np.float64)
        # Extract the values from the grid cards, using np.nan for empty cells
        grid_values = np.frompyfunc(
            lambda card: card.value if isinstance(card, Card) else np.nan,
            1,
            1,
        )(self._grid_cards)
        return np.where(self.face_up_and_active, grid_values, values)

    @property
    def face_up_and_active(self) -> NDArray[np.bool_]:
        return self._grid_face_up * self.columns_active

    @property
    def face_down_and_active(self) -> NDArray[np.bool_]:
        return (~self._grid_face_up) * self.columns_active

    @property
    def is_full(self) -> bool:
        return bool(self._grid_face_up.all())

    def total_score(self) -> int:
        return int(np.nansum(self._values(with_face_down=False)))

    def reveal_all(self) -> None:
        self._grid_face_up[:, :] = True

    def first_face_down_cell(self) -> tuple[int, int]:
        row, col = np.unravel_index(
            np.argmax(self.face_down_and_active),
            self.face_down_and_active.shape,
        )
        return int(row), int(col)

    def _is_column_valid(self, column: int) -> bool:
        return (0 <= column < COLS) and self.columns_active[column]

    def _is_row_valid(self, row: int) -> bool:
        return 0 <= row < ROWS

    def __getitem__(self, key: tuple[int, int]) -> Card | None:
        """Enable reading: card = grid[row, col]"""
        row, col = key
        if not self._is_column_valid(col) or not self._is_row_valid(row):
            raise ValueError("Invalid row or column")
        if not self._grid_face_up[row, col]:
            return None
        return cast(Card | None, self._grid_cards[row, col])

    def __setitem__(self, key: tuple[int, int], value: Card | None) -> None:
        """Enable writing: grid[row, col] = card"""
        row, col = key
        if not self._is_row_valid(row) or not self._is_column_valid(col):
            raise ValueError("Invalid row or column")
        self._grid_cards[row, col] = value
