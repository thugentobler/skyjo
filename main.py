from dataclasses import dataclass
from enum import Enum
from random import shuffle


class Color(Enum):
    BLUE = 1
    LIGHT_BLUE = 2
    GREEN = 3
    YELLOW = 4
    RED = 5


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
        return f"{self.value} of {self.color.name}"

    def __repr__(self):
        return self.__str__()


CARD_DISTRIBUTION = {
    Card(-2, Color.BLUE): 5,
    Card(-1, Color.BLUE): 10,
    Card(0, Color.LIGHT_BLUE): 15,
    Card(1, Color.GREEN): 10,
    Card(2, Color.GREEN): 10,
    Card(3, Color.GREEN): 10,
    Card(4, Color.GREEN): 10,
    Card(5, Color.YELLOW): 10,
    Card(6, Color.YELLOW): 10,
    Card(7, Color.YELLOW): 10,
    Card(8, Color.YELLOW): 10,
    Card(9, Color.RED): 10,
    Card(10, Color.RED): 10,
    Card(11, Color.RED): 10,
    Card(12, Color.RED): 10,
}


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


class Ablagestapel:
    cards: list[Card]

    def __init__(self, card: Card):
        self.cards = [card]

    def add_card(self, card: Card):
        self.cards.append(card)

    def draw_card(self) -> Card:
        if not self.cards:
            raise ValueError("No cards left in the discard pile")
        return self.cards.pop()


class Player:
    grid: list[list[Card | None]]

    def __init__(self):
        self.grid = [[None for _ in range(4)] for _ in range(3)]

    def fill_grid(self, cards: list[Card]):
        if len(cards) != 12:
            raise ValueError("Exactly 12 cards are required to fill the grid")
        idx = 0
        for row in range(3):
            for col in range(4):
                self.grid[row][col] = cards[idx]
                idx += 1

    def display_grid(self):
        for row in self.grid:
            print(" | ".join(str(card.value) if card else "None" for card in row))

    def place_card(self, row: int, col: int, card: Card) -> Card:
        if 0 > row or row >= 3:
            raise ValueError("Invalid row")
        if 0 > col or col >= 4:
            raise ValueError("Invalid column")
        return_card = self.grid[row][col]
        if return_card is None:
            raise ValueError("No card to replace in this position")
        self.grid[row][col] = card
        return return_card

    def remove_column(self, col: int):
        if 0 <= col < 4:
            for row in range(3):
                self.grid[row][col] = None
        else:
            raise ValueError("Invalid column")


def game_init() -> tuple[Deck, Ablagestapel, list[Player]]:
    deck = Deck()
    discard_pile = Ablagestapel(deck.draw_card())
    players = [Player() for _ in range(2)]

    for player in players:
        initial_cards = [deck.draw_card() for _ in range(12)]
        player.fill_grid(initial_cards)
    return deck, discard_pile, players


def main():
    deck, discard_pile, players = game_init()


if __name__ == "__main__":
    main()
