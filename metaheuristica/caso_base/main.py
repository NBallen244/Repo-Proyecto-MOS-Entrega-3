import sys
import os
import time

# Add the directory containing cargaBase.py to Python's search path
script_dir = os.path.dirname(os.path.abspath("cargaDatos.py"))
sys.path.insert(0, script_dir)

from carga_datos.cargaDatos import cargar_datos_base as cargar_datos
from metaheuristica import funciones_ga as ga
def evolve_population(self):
    """
    Evolve the population to the next generation using elitism, crossover, and mutation.
    """
    # Evaluate current population
    population_fitness = [(i, self.evaluate_fitness(solution)) 
                            for i, solution in enumerate(self.population)]
    
    # Sort by fitness (lower is better)
    population_fitness.sort(key=lambda x: x[1])
    
    # Keep elite solutions
    num_elite = max(1, int(self.elitism_rate * self.population_size))
    elite_indices = [idx for idx, _ in population_fitness[:num_elite]]
    new_population = [deepcopy(self.population[idx]) for idx in elite_indices]
    
    # Fill the rest of the population with offspring
    while len(new_population) < self.population_size:
        # Select parents
        parent1, parent2 = self.select_parents()
        
        # Crossover
        child1, child2 = self.crossover(parent1, parent2)
        
        # Mutation
        child1 = self.mutate(child1)
        child2 = self.mutate(child2)
        
        # Add to new population
        new_population.append(child1)
        if len(new_population) < self.population_size:
            new_population.append(child2)
    
    self.population = new_population

def solve(self, verbose=True, early_stopping_generations=50):
    """
    Run the genetic algorithm to solve the MTSP.
    
    Args:
        verbose (bool): Whether to print progress information
        early_stopping_generations (int): Stop if no improvement for this many generations
        
    Returns:
        best_solution, best_fitness
    """
    # Initialize population
    self.initialize_population()
    
    # Track best solution and convergence
    best_solution = None
    best_fitness = float('inf')
    generations_without_improvement = 0
    start_time = time.time()
    
    # Main loop
    for generation in range(self.generations):
        # Evolve population
        self.evolve_population()
        
        # Find best solution in current population
        current_best = None
        current_best_fitness = float('inf')
        
        for solution in self.population:
            fitness = self.evaluate_fitness(solution)
            if fitness < current_best_fitness:
                current_best = solution
                current_best_fitness = fitness
        
        # Update global best
        if current_best_fitness < best_fitness:
            best_solution = deepcopy(current_best)
            best_fitness = current_best_fitness
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1
        
        # Store history
        self.fitness_history.append(current_best_fitness)
        self.best_solution_history.append(best_fitness)
        
        # Print progress
        if verbose and generation % 10 == 0:
            elapsed_time = time.time() - start_time
            print(f"Generation {generation}: Best Fitness = {best_fitness:.2f}, "
                    f"Current Best = {current_best_fitness:.2f}, "
                    f"Time = {elapsed_time:.2f}s")
        
        # Early stopping
        if generations_without_improvement >= early_stopping_generations:
            if verbose:
                print(f"Early stopping at generation {generation} due to no improvement "
                        f"for {early_stopping_generations} generations.")
            break
    
    # Final results
    self.best_solution = best_solution
    self.best_fitness = best_fitness
    
    if verbose:
        total_time = time.time() - start_time
        print(f"Optimization complete. Best fitness: {best_fitness:.2f}, "
                f"Time: {total_time:.2f}s")
        
    return best_solution, best_fitness
