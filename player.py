import numpy as np
from numpy.typing import NDArray

import config
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
    is_user: bool = False

    def __init__(self, name: str, genome: Genome | None = None):
        self.name = name
        self.grid = Grid()
        self.genome = genome or Genome()
        self.is_user = name == "Du"

    def fill_grid(self, initial_cards: list[Card]):
        self.grid.fill_grid(initial_cards)

    def _place_decision(
        self, card: Card, next_player_grid: NDArray[np.float64]
    ) -> tuple[int, int]:
        score = (
            self.genome.params.w_gain * self.grid._gain(card)
            + self.genome.params.w_match * self.grid._match(card)
            + self.genome.params.w_col_bonus * self.grid._col_bonus(card)
            + self.genome.params.w_reveal * self.grid._reveal(card)
            + self.genome.params.w_breaks_match * self.grid._breaks_match(card)
            - self.genome.params.w_gain_next_player
            * self.grid._gain_next_player(card, next_player_grid)
        )
        # TODO: refine _gain_next_player calculation

        # mask off the inactive columns
        score[:, ~self.grid.columns_active] = -np.inf

        row, col = np.unravel_index(np.argmax(score), score.shape)
        return int(row), int(col)

    def _turn_over_decision(self) -> None:
        # TODO: refine the choosing of the face down position to turn up

        for row in range(ROWS):
            for col in range(COLS):
                if self.grid.is_face_down_and_active(row, col):
                    self.grid.flip_card(row, col)
                    if config.DISPLAY_GAME:
                        print(
                            f"Turned over card at row {row+1}, column {col+1}"
                        )
                    return

    def _draw_decision(
        self, deck: Deck, ablagestapel: Ablagestapel
    ) -> Card | None:
        # col_dict = self.grid.get_matching_columns_count(ablagestapel.top_card)
        score = (
            self.genome.params.w_topcard * ablagestapel.top_card.value
            + self.genome.params.w_count
            * np.count_nonzero(self.grid._values() == ablagestapel.top_card)
            + self.genome.params.w_col_count
            * np.count_nonzero(
                np.sum(
                    self.grid._values() == ablagestapel.top_card,
                    axis=0,
                )
                >= 2
            )
            + self.genome.params.w_gain_topcard
            * np.max(
                self.grid._values()
                - np.full_like(
                    self.grid._values(), ablagestapel.top_card.value
                )
            )
        )
        if score >= self.genome.params.take_ablagestapel_thresh:
            return ablagestapel.draw_card()
        else:
            return_card = deck.draw_card()
            # TODO: value the drawn card against the current grid state
            score = self.genome.params.w_count * np.count_nonzero(
                self.grid._values() == ablagestapel.top_card
            ) + self.genome.params.w_col_count * np.count_nonzero(
                np.sum(
                    self.grid._values() == ablagestapel.top_card,
                    axis=0,
                )
                >= 2
            )

            # If the score is below the threshold, choose a random face-down card
            return (
                return_card
                if score > self.genome.params.discard_thresh
                else None
            )

    def place_card(
        self,
        card: Card | None,
        ablage: Ablagestapel,
        next_player_grid: NDArray[np.float64],
    ) -> None:
        if card is None:
            self._turn_over_decision()
            return

        row, col = self._place_decision(card, next_player_grid)
        if config.DISPLAY_GAME:
            print(f"Placing card {card} at row {row+1}, column {col+1}")
        return_card = self.grid.place_card(row, col, card)
        if config.DISPLAY_GAME:
            print(f"Returned card to ablage: {return_card}")
        ablage.add_card(return_card)

    def draw_card(self, deck: Deck, ablagestapel: Ablagestapel) -> Card | None:
        if config.DISPLAY_GAME:
            print(f"Top card on ablagestapel: {ablagestapel.top_card}")
        return_card = self._draw_decision(deck, ablagestapel)
        if config.DISPLAY_GAME:
            print(f"Drawn card: {return_card}")
        return return_card

    def display(self) -> str:
        result = f"{self.name}\n"
        result += self.grid.display()
        return result

    def grid_view(self) -> NDArray[np.float64]:
        return self.grid._values(False)


class UserPlayer(Player):
    def __init__(self, name: str, genome=None):
        super().__init__(name, genome)
        self.is_user = True

    def _draw_decision(
        self, deck: Deck, ablagestapel: Ablagestapel
    ) -> Card | None:
        choice = (
            input(
                f"Do you want to take the top card {ablagestapel.top_card}? (y/n): "
            )
            .strip()
            .lower()
        ) or "y"
        if choice == "y":
            return_card = ablagestapel.draw_card()
        else:
            return_card = deck.draw_card()
            if config.DISPLAY_GAME:
                print(f"You drew: {return_card}")
            print("Do you want to keep this card?")
            choice = (input("(y/n): ").strip().lower()) or "y"
            if choice != "y":
                ablagestapel.add_card(return_card)
                return None

        return return_card

    def _turn_over_decision(self) -> tuple[int, int]:
        print("Which card do you want to turn over?")
        row = int(input("Enter row (1-3): ")) - 1
        col = int(input("Enter column (1-4): ")) - 1

        while not self.grid.is_face_down_and_active(row, col):
            print("Selected cell is already face up. Please try again.")
            row = int(input("Enter row (1-3): ")) - 1
            col = int(input("Enter column (1-4): ")) - 1
        return row, col

    def _place_decision(
        self, card: Card, next_player_grid: NDArray[np.float64]
    ) -> tuple[int, int]:
        print("Where do you want to place the card?")
        row = int(input("Enter row (1-3): ")) - 1
        col = int(input("Enter column (1-4): ")) - 1
        while not self.grid._is_row_valid(row):
            print("Invalid row. Please try again.")
            row = int(input("Enter row (1-3): ")) - 1
        while not self.grid._is_column_valid(col):
            print("Invalid column. Please try again.")
            col = int(input("Enter column (1-4): ")) - 1

        return row, col


class BaselinePlayer(Player):
    def __init__(self, name: str, genome=None):
        super().__init__(name, genome)
        self.is_user = False

    def _draw_decision(self, deck: Deck, ablagestapel: Ablagestapel) -> Card:
        # simple draw decision based on top card value
        if ablagestapel.top_card <= 4:
            return ablagestapel.draw_card()
        else:
            return deck.draw_card()

    def _place_decision(
        self, card: Card, next_player_grid: NDArray[np.float64]
    ) -> tuple[int, int]:
        # simple place decision: place in the first available cell
        values = self.grid._values()
        eligible = self.grid.face_up_and_active & (values > card.value)
        if np.any(eligible):
            row, col = np.unravel_index(
                np.argmax(np.where(eligible, values, -np.inf)), values.shape
            )
            return int(row), int(col)
        return self.grid.first_face_down_cell()
