import pygad
import numpy as np

equation_inputs = [4, -2, 3.5]
Y = 44

def fitness_func(ga_instance, solution, solution_idx):
    out = np.sum(solution * equation_inputs)
    fitness = 1.0/(np.abs(out - Y) + 0.000001)
    return fitness

ga_instance = pygad.GA(num_generations = 100,
                    sol_per_pop = 50,
                    num_parents_mating = 10,
                    num_genes = 3,
                    mutation_type = "random",
                    fitness_func=fitness_func)

ga_instance.run()

solution, solution_fitness, solution_idx = ga_instance.best_solution()
