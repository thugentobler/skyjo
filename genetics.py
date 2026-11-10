import random

from game import Game
from player import BaselinePlayer, Player


class Genome:
    def __init__(self, params=None, n=8):
        self.params = params or [random.uniform(0, 1) for _ in range(n)]
        self.fitness = None


def crossover(a: Genome, b: Genome) -> Genome:
    return Genome([random.choice(p) for p in zip(a.params, b.params)])


def mutate(g: Genome, rate=0.1, sigma=0.1) -> Genome:
    g.params = [
        p + random.gauss(0, sigma) if random.random() < rate else p
        for p in g.params
    ]
    return g


def evaluate(genome: Genome, n_games=200) -> float:
    wins = 0
    for _ in range(n_games):
        player = Player(strategy_params=genome.params)  # dein Spieler
        game = Game(players=[player, BaselinePlayer()])  # dein Spiel
        wins += game.play().winner is player
    return wins / n_games


def tournament(pop, k=3):
    return max(random.sample(pop, k), key=lambda g: g.fitness)


def evolve(pop_size=50, generations=40):
    population = [Genome() for _ in range(pop_size)]
    for generation in range(generations):
        for genome in population:
            genome.fitness = evaluate(genome)
        population.sort(key=lambda g: g.fitness, reverse=True)
        print(generation, population[0].fitness)
        elite = population[:2]
        children = [
            mutate(crossover(tournament(population), tournament(population)))
            for _ in range(pop_size - len(elite))
        ]
        population = elite + children
    return population[0]
