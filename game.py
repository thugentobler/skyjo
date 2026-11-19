import glob
import os
from random import randint

import config
from game_elements import Ablagestapel, Deck
from genome import Genome
from player import Player, UserPlayer


class Game:
    def __init__(self, players: list[Player]):
        self.players = players
        self.deck = Deck()
        self.discard_pile = Ablagestapel()

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

    def play(self) -> Player:
        while True:
            for index, player in enumerate(self.players):
                if config.DISPLAY_GAME:
                    print(f"--- {player.name}'s turn ---")
                    print(self)
                card = player.draw_card(self.deck, self.discard_pile)
                next_player = self.players[(index + 1) % len(self.players)]
                player.place_card(
                    card, self.discard_pile, next_player.grid_view()
                )

                if player.grid.is_full:
                    final_players = (
                        self.players[index + 1 :] + self.players[:index]
                    )

                    for final_player in final_players:
                        card = final_player.draw_card(
                            self.deck, self.discard_pile
                        )
                        next_player = self.players[
                            (self.players.index(final_player) + 1)
                            % len(self.players)
                        ]
                        if config.DISPLAY_GAME:
                            print(f"--- {final_player.name}'s turn ---")
                        final_player.place_card(
                            card, self.discard_pile, next_player.grid_view()
                        )
                        final_player.grid.reveal_all()

                    # Return the player with the lowest score
                    winner = min(
                        self.players, key=lambda p: p.grid.total_score()
                    )
                    if config.DISPLAY_GAME:
                        print(self._final_score(winner))
                    return winner

    def __str__(self) -> str:
        result = "-" * 10 + "\n"
        # first print the deck size and the ablage size and the value for the ablage
        result += f"Deck count: {self.deck.count} \n"
        result += f"Ablagestapel: {self.discard_pile}\n"

        for player in self.players:
            result += player.display() + "\n"

        return result

    def _final_score(self, winner: Player) -> str:
        result = "-" * 10 + "\n"
        result += "Final scores:\n"
        print(self)
        for p in self.players:
            result += f"{p.name}: {p.grid.total_score()}\n"
        result += "Winner:\n"
        result += f"{winner.name}\n"
        return result


def load_latest_genome() -> Genome:

    files = glob.glob("./genomes/*.json")
    if not files:
        return Genome()
    latest_file = max(files, key=os.path.getctime)
    genome = Genome()
    genome.load(latest_file)
    return genome


def main():
    print("Welcome to Skyjo!")
    print("How many human players will participate?")
    num_human_players = int(input())
    players: list[Player] = []
    for i in range(num_human_players):
        print(f"Enter username for human player {i+1}:")
        username = input().strip()
        players.append(UserPlayer(username))
    print("How many other players should participate?")
    num_players = int(input())
    players += [
        Player(f"Player {i+1}", load_latest_genome())
        for i in range(num_players)
    ]
    players.append(UserPlayer(username))

    game = Game(players)
    game.play()


if __name__ == "__main__":
    main()
