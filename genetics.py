import random

from game import Game
from genome import Genome
from player import Player


def crossover(a: Genome, b: Genome) -> Genome:
    child = Genome()
    child_params = vars(child.params)
    a_params, b_params = vars(a.params), vars(b.params)
    for name in child_params:
        child_params[name] = random.choice((a_params[name], b_params[name]))
    return child


def mutate(g: Genome, rate=0.1, sigma=0.1) -> Genome:
    params = vars(g.params)
    for name in params:
        if random.random() < rate:
            params[name] += random.gauss(0, sigma)
    return g


def evaluate(genome: Genome, n_games=200) -> float:
    wins = 0
    for i in range(n_games):
        player = Player(f"genome {i}", genome)  # dein Spieler
        game = Game(players=[player])  # dein Spiel
        wins += game.play() is player
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
