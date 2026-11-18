import random
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat

import config
from game import Game
from genome import Genome
from player import BaselinePlayer, Player


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


def evaluate(genome: Genome, n_games=200, seed=None) -> float:
    if seed is not None:
        random.seed(seed)
    wins = 0
    for i in range(n_games):
        player = [
            Player(f"genome {i}", genome),
            BaselinePlayer("Baseline"),
        ]
        config.DISPLAY_GAME = False
        game = Game(players=player)
        wins += game.play() is player[0]
    return wins / n_games


def select_fittest(pop, k=3):
    return max(random.sample(pop, k), key=lambda g: g.fitness)


def evolve(pop_size=50, generations=20):
    population = [Genome() for _ in range(pop_size)]

    with ProcessPoolExecutor() as executor:
        for generation in range(generations):
            seeds = [random.getrandbits(128) for _ in population]
            print(f"Generation {generation}")
            fitnesses = executor.map(evaluate, population, repeat(200), seeds)
            for genome, fitness in zip(population, fitnesses):
                genome.fitness = fitness

            population.sort(key=lambda g: g.fitness, reverse=True)
            print(generation, population[0].fitness)
            elite = population[:2]
            children = [
                mutate(
                    crossover(
                        select_fittest(population), select_fittest(population)
                    )
                )
                for _ in range(pop_size - len(elite))
            ]
            population = elite + children

            for g in elite:
                g.save(
                    f"./genomes/genome_{generation}_{population.index(g)}.json"
                )

            print(f"Fitness of best genome: {population[0].fitness}")
    return population[0]


if __name__ == "__main__":
    random.seed(23)
    best_genome = evolve()
    print("Best genome fitness:", best_genome.fitness)
