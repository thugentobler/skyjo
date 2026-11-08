from dataclasses import dataclass
from random import shuffle


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
        return f"{self.value}"

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


class Ablagestapel:
    cards: list[Card]

    def __init__(self, card: Card):
        self.cards = [card]

    def add_card(self, card: Card):
        self.cards.append(card)

    def show_top_card(self) -> Card:
        return self.cards[-1]

    def draw_card(self) -> Card:
        if not self.cards:
            raise ValueError("No cards left in the discard pile")
        return self.cards.pop()


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

    def turn_cards(self, row, column):
        self._is_row_valid(row)
        self._is_column_valid(column)
        if self.grid_face_up[row][column]:
            raise ValueError("Card is already face up")
        self.grid_face_up[row][column] = not self.grid_face_up[row][column]

    def display(self):
        for row in self.grid_cards:
            print(
                " | ".join(str(card.value) if card else "None" for card in row)
            )

    def remove_column(self, col: int):
        self.columns_active.remove(col)
        for row in range(3):
            self.grid_cards[row][col]
        for row in range(3):
            self.grid_cards[row][col] = None
            self.grid_face_up[row][col] = False

    def _is_column_valid(self, column: int) -> None:
        if not (0 <= column < 4):
            raise ValueError("Invalid column")
        if not column in self.columns_active:
            raise ValueError("Invalid column")

    def _is_row_valid(self, row: int) -> None:
        if not (0 <= row < 3):
            raise ValueError("Invalid row")

    def __getitem__(self, key: tuple):
        """Enable reading: card = grid[row, col]"""
        row, col = key  # Unpacks tuple (row, col)
        if not (0 <= row < 3):
            raise IndexError("Row index out of range")
        if not (0 <= col < 4):
            raise IndexError("Column index out of range")
        return self.grid_cards[row][col]

    def __setitem__(self, key: tuple, value: Card):
        """Enable writing: grid[row, col] = card"""
        row, col = key  # Unpacks tuple (row, col)
        if not (0 <= row < 3):
            raise IndexError("Row index out of range")
        if not (0 <= col < 4):
            raise IndexError("Column index out of range")
        self.grid_cards[row][col] = value


class Player:
    grid: Grid

    def __init__(self):
        self.grid = Grid()

    def fill_grid(self, initial_cards: list[Card]):
        self.grid.fill_grid(initial_cards)

    def place_card(self, row: int, col: int, card: Card) -> Card:
        if 0 > row or row >= 3:
            raise ValueError("Invalid row")
        if 0 > col or col >= 4:
            raise ValueError("Invalid column")
        return_card = self.grid[row, col]
        if return_card is None:
            raise ValueError("No card to replace in this position")
        self.grid[row, col] = card
        return return_card

    def remove_column(self, col: int):
        if 0 <= col < 4:
            for row in range(3):
                self.grid.remove_column(col)
        else:
            raise ValueError("Invalid column")

    def display(self):
        self.grid.display()


class Game:
    def __init__(self):
        self.player = []
        self.deck = Deck()
        self.discard_pile = None

    def game_init(self, n_player: int) -> None:
        self.discard_pile = Ablagestapel(self.deck.draw_card())
        players = [Player() for _ in range(n_player)]

        for player in players:
            initial_cards = [self.deck.draw_card() for _ in range(12)]
            player.fill_grid(initial_cards)

    def __str__(self) -> str:
        result = "-" * 10 + "\n"
        result += "Game: \n"
        # first print the deck size and the ablage size and the value for the ablage
        result += f"Deck count: {self.deck.count} \n"
        result += f"Ablagestapel: {self.discard_pile.show_top_card() if self.discard_pile is not None else 'None'}\n"

        for player in self.player:
            result += player.display() + "\n"

        return result


def game():
    pass


def main():
    game = Game()
    game.game_init(n_player=4)

    print(game)


if __name__ == "__main__":
    main()
