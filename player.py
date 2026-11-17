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
    is_user: bool = False

    def __init__(self, name: str, genome: Genome | None = None):
        self.name = name
        self.grid = Grid()
        self.genome = genome or Genome()
        self.is_user = name == "Du"

    def fill_grid(self, initial_cards: list[Card]):
        self.grid.fill_grid(initial_cards)

    def _place_decision(self, card: Card) -> tuple[int, int]:
        # TODO: include next player
        # TODO: option to put picked card to ablage and turn one card in the grid face up
        score = (
            self.genome.params.w_gain * self.grid._gain(card)
            + self.genome.params.w_match * self.grid._match(card)
            + self.genome.params.w_col_bonus * self.grid._col_bonus(card)
            + self.genome.params.w_reveal * self.grid._reveal(card)
            + self.genome.params.w_breaks_match * self.grid._breaks_match(card)
        )
        row, col = np.unravel_index(np.argmax(score), score.shape)
        return int(row), int(col)

    def _draw_decision(self, deck: Deck, ablagestapel: Ablagestapel) -> Card:
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
        if score >= self.genome.params.take_discard_thresh:
            return ablagestapel.draw_card()
        else:
            return deck.draw_card()

    def place_card(self, card: Card, ablage: Ablagestapel) -> None:
        row, col = self._place_decision(card)
        print(f"Placing card {card} at row {row+1}, column {col+1}")
        return_card = self.grid.place_card(row, col, card)
        print(f"Returned card to ablage: {return_card}")
        ablage.add_card(return_card)

    def draw_card(self, deck: Deck, ablagestapel: Ablagestapel) -> Card:
        print(f"Top card on ablagestapel: {ablagestapel.top_card}")
        return_card = self._draw_decision(deck, ablagestapel)
        print(f"Drawn card: {return_card}")
        return return_card

    def display(self) -> str:
        result = f"{self.name}\n"
        result += self.grid.display()
        return result


class UserPlayer(Player):
    def __init__(self, name: str, genome=None):
        super().__init__(name, genome)
        self.is_user = True

    def _draw_decision(self, deck: Deck, ablagestapel: Ablagestapel) -> Card:
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
        print(f"You drew: {return_card}")
        return return_card

    def _place_decision(self, card: Card) -> tuple[int, int]:
        # Implement user input logic here
        # For now, just return the first available cell
        while True:
            print("Where do you want to place the card?")
            row = int(input("Enter row (1-3): ")) - 1
            col = int(input("Enter column (1-4): ")) - 1
            try:
                self.grid._is_row_valid(row)
                self.grid._is_column_valid(col)
                return row, col
            except ValueError as e:
                print(e)


class BaselinePlayer(Player):
    def __init__(self, name: str, genome=None):
        super().__init__(name, genome)
        self.is_user = False

    def _place_decision(self, card: Card) -> tuple[int, int]:
        # simple place decision: place in the first available cell
        values = self.grid._values()
        face_up = self.grid.grid_face_up
        eligible = face_up & (values > card.value)
        if np.any(eligible):
            row, col = np.unravel_index(
                np.argmax(np.where(eligible, values, -np.inf)), values.shape
            )
            return int(row), int(col)
        return self.grid.first_available_cell()

    def _draw_decision(self, deck: Deck, ablagestapel: Ablagestapel) -> Card:
        # simple draw decision based on top card value
        if ablagestapel.top_card <= 4:
            return ablagestapel.draw_card()
        else:
            return deck.draw_card()
