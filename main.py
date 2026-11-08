from dataclasses import dataclass
from random import randint, shuffle
from typing import Protocol


@dataclass(frozen=True)
class Color:
    name: str
    value: str


blue = Color("Blue", "3e44a3")
light_blue = Color("Light Blue", "46d8ec")
green = Color("Green", "7ddb51")
yellow = Color("Yellow", "f6ee25")
red = Color("Red", "e12b2a")


@dataclass(frozen=True)
class Card:
    value: int
    color: Color

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise TypeError("Card value must be an integer")
        if not isinstance(self.color, Color):
            raise TypeError("Card color must be an instance of Color")
        if not (-2 <= self.value <= 12):
            raise ValueError("Card value must be between -2 and 12")

    def __str__(self):
        return f"[{self.value:>2}]"

    def __repr__(self):
        return self.__str__()


CARD_DISTRIBUTION = {
    Card(-2, blue): 5,
    Card(-1, blue): 10,
    Card(0, light_blue): 15,
    Card(1, green): 10,
    Card(2, green): 10,
    Card(3, green): 10,
    Card(4, green): 10,
    Card(5, yellow): 10,
    Card(6, yellow): 10,
    Card(7, yellow): 10,
    Card(8, yellow): 10,
    Card(9, red): 10,
    Card(10, red): 10,
    Card(11, red): 10,
    Card(12, red): 10,
}


class Drawable(Protocol):
    def draw_card(self) -> Card: ...

    @property
    def count(self) -> int: ...


class Deck:
    cards: list[Card]

    def __init__(self):
        self.cards = []
        for card, count in CARD_DISTRIBUTION.items():
            self.cards.extend([card] * count)
        self.shuffle()

    def shuffle(self):
        shuffle(self.cards)

    def draw_card(self) -> Card:
        if not self.cards:
            raise ValueError("No cards left in the deck")
        return self.cards.pop()

    @property
    def count(self) -> int:
        return len(self.cards)

    def __str__(self):
        return f"Deck({self.count})"


class Ablagestapel:
    cards: list[Card]

    def __init__(self):
        self.cards = []

    def add_card(self, card: Card):
        self.cards.append(card)

    def show_top_card(self) -> Card:
        return self.cards[-1]

    def draw_card(self) -> Card:
        if not self.cards:
            raise ValueError("No cards left in the discard pile")
        return self.cards.pop()

    @property
    def count(self) -> int:
        return len(self.cards)

    def __str__(self):
        return (
            f"{self.cards[-1] if self.cards else 'None'}, count: {self.count}"
        )


class Grid:
    grid_cards: list[list[Card | None]]
    grid_face_up: list[list[bool]]
    columns_active: list[int]

    def __init__(self):
        self.grid_cards = [[None for _ in range(4)] for _ in range(3)]
        self.grid_face_up = [[False for _ in range(4)] for _ in range(3)]
        self.columns_active = [x for x in range(4)]

    def fill_grid(self, cards: list[Card]):
        if len(cards) != 12:
            raise ValueError("Exactly 12 cards are required to fill the grid")
        idx = 0
        for row in range(3):
            for col in range(4):
                self.grid_cards[row][col] = cards[idx]
                idx += 1

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

        self.columns_active.remove(col)
        for row in range(3):
            self.grid_cards[row][col] = None
            self.grid_face_up[row][col] = False

    def is_column_removable(self, col: int) -> bool:
        cards = [self.grid_cards[row][col] for row in range(3)]
        return (
            col in self.columns_active
            and all(card is not None for card in cards)
            and len({card.value for card in cards if card is not None}) == 1
        )

    def _is_column_valid(self, column: int) -> None:
        if not (0 <= column < 4):
            raise ValueError("Invalid column")
        if not column in self.columns_active:
            raise ValueError("Column is not active")

    def _is_row_valid(self, row: int) -> None:
        if not (0 <= row < 3):
            raise ValueError("Invalid row")

    def __getitem__(self, key: tuple):
        """Enable reading: card = grid[row, col]"""
        row, col = key  # Unpacks tuple (row, col)
        self._is_column_valid(col)
        self._is_row_valid(row)
        return self.grid_cards[row][col]

    def __setitem__(self, key: tuple, value: Card):
        """Enable writing: grid[row, col] = card"""
        row, col = key  # Unpacks tuple (row, col)
        self._is_row_valid(row)
        self._is_column_valid(col)
        self.grid_cards[row][col] = value


class Player:
    name: str
    grid: Grid

    def __init__(self, name: str):
        self.name = name
        self.grid = Grid()

    def fill_grid(self, initial_cards: list[Card]):
        self.grid.fill_grid(initial_cards)

    def place_card(
        self, row: int, col: int, card: Card, ablage: Ablagestapel
    ) -> None:
        self.grid.flip_card(row, col)
        return_card = self.grid[row, col]
        self.grid[row, col] = card
        ablage.add_card(return_card)

    def draw_card(self, deck: Drawable) -> Card:
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


class Game:
    def __init__(self):
        self.players = []
        self.deck = Deck()
        self.discard_pile = Ablagestapel()

    def game_init(self, n_player: int) -> None:
        self.discard_pile.add_card(self.deck.draw_card())
        self.players = [Player(f"Player {i+1}") for i in range(n_player)]

        for player in self.players:
            initial_cards = [self.deck.draw_card() for _ in range(12)]
            player.fill_grid(initial_cards)

            # Flip two cards for each player
            columns = [0, 1, 2, 3]
            for _ in range(2):
                row = randint(0, 2)
                col = columns.pop(randint(0, len(columns) - 1))
                player.grid.flip_card(row, col)

    def round(self):
        for player in self.players:
            card = player.draw_card(self.deck)
            player.place_card(0, 1, card, self.discard_pile)

    def __str__(self) -> str:
        result = "-" * 10 + "\n"
        result += "Game: \n"
        # first print the deck size and the ablage size and the value for the ablage
        result += f"Deck count: {self.deck.count} \n"
        result += f"Ablagestapel: {self.discard_pile}\n"

        for player in self.players:
            result += player.display() + "\n"

        return result


def main():
    game = Game()
    game.game_init(n_player=4)
    print(game)
    game.round()
    print(game)


if __name__ == "__main__":
    main()
