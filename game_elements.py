from dataclasses import dataclass
from random import shuffle
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
        return f"Card[{self.value:>2}]"

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self.value * other
        return NotImplemented

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Card):
            return NotImplemented
        return self.value == value.value and self.color == value.color


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

EXPECTED_CARD_VALUE = sum(
    card.value * count for card, count in CARD_DISTRIBUTION.items()
) / sum(CARD_DISTRIBUTION.values())


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
