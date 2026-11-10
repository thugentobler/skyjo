from random import randint

from game_elements import Ablagestapel, Deck
from player import Player


class Game:
    def __init__(self, players: list[Player]):
        self.players = players
        self.deck = Deck()
        self.discard_pile = Ablagestapel()

    def game_init(self) -> None:
        self.discard_pile.add_card(self.deck.draw_card())

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

    def play(self):
        while self.deck.count > 0:
            self.round()

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
