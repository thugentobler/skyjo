from game_elements import Ablagestapel, Card, Deck, Drawable


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

    def has_grid_columns_with_value(self, card: Card) -> list[int]:
        for row in range(3):
            for col in range(4):
                card = self.grid_cards[row][col]

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

    def draw_card(self, deck: Deck, ablagestapel: Ablagestapel) -> Card:
        score = self.genome.params[0] * ablagestapel.show_top_card().value + 
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
