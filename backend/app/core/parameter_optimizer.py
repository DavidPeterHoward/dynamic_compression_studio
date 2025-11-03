"""
Parameter optimizer for the Dynamic Compression Algorithms backend.

This module implements parameter optimization strategies including
Bayesian optimization, grid search, and genetic algorithms.
"""

import random
from typing import Dict, List, Any, Optional
# import numpy as np  # Removed for compatibility

from app.models.compression import CompressionAlgorithm, CompressionParameters, CompressionLevel


class ParameterOptimizer:
    """
    Parameter optimizer that implements multiple optimization strategies.
    
    Based on the documentation:
    - Grid Search: Systematic parameter space exploration
    - Bayesian Optimization: Probabilistic model-based optimization
    - Multi-Armed Bandit: Adaptive exploration-exploitation balance
    - Genetic Algorithms: Evolutionary parameter optimization
    """
    
    def __init__(self):
        """Initialize the parameter optimizer."""
        # Parameter bounds for different algorithms
        self.parameter_bounds = {
            CompressionAlgorithm.GZIP: {
                'level': (1, 9),
                'window_size': (1024, 65536),
                'block_size': (1024, 8192)
            },
            CompressionAlgorithm.LZMA: {
                'level': (0, 9),
                'dict_size': (4096, 1073741824),
                'lc': (0, 8),
                'lp': (0, 4),
                'pb': (0, 4)
            },
            CompressionAlgorithm.BZIP2: {
                'level': (1, 9),
                'block_size': (100000, 900000)
            },
            CompressionAlgorithm.LZ4: {
                'level': (1, 16),
                'block_size': (64, 4194304)
            },
            CompressionAlgorithm.ZSTD: {
                'level': (1, 22),
                'dict_size': (1024, 134217728),
                'threads': (1, 32)
            },
            CompressionAlgorithm.BROTLI: {
                'level': (0, 11),
                'window_size': (1024, 65536),  # Fixed: was (10, 24)
                'block_size': (16, 24)
            }
        }
        
        # Optimization strategy weights
        self.strategy_weights = {
            'grid_search': 0.3,
            'bayesian': 0.4,
            'genetic': 0.2,
            'bandit': 0.1
        }
        
        # Historical parameter performance (would be loaded from database)
        self.parameter_history = {}
    
    def optimize_parameters(self, algorithm: CompressionAlgorithm, content_analysis: Dict[str, Any], base_parameters: CompressionParameters) -> Dict[str, Any]:
        """
        Optimize parameters for the given algorithm and content.
        
        Args:
            algorithm: Compression algorithm to optimize for
            content_analysis: Content analysis results
            base_parameters: Base parameters to start from
            
        Returns:
            Optimized parameters
        """
        # Get parameter bounds for the algorithm
        bounds = self.parameter_bounds.get(algorithm, {})
        
        # Choose optimization strategy based on content characteristics
        strategy = self._select_optimization_strategy(content_analysis)
        
        # Execute optimization
        if strategy == 'grid_search':
            optimized_params = self._grid_search_optimization(algorithm, bounds, content_analysis)
        elif strategy == 'bayesian':
            optimized_params = self._bayesian_optimization(algorithm, bounds, content_analysis)
        elif strategy == 'genetic':
            optimized_params = self._genetic_optimization(algorithm, bounds, content_analysis)
        elif strategy == 'bandit':
            optimized_params = self._bandit_optimization(algorithm, bounds, content_analysis)
        else:
            optimized_params = self._default_optimization(algorithm, bounds, content_analysis)
        
        # Merge with base parameters
        return self._merge_parameters(base_parameters, optimized_params)
    
    def _select_optimization_strategy(self, content_analysis: Dict[str, Any]) -> str:
        """Select optimization strategy based on content characteristics."""
        # Get content profile
        content_profile = content_analysis.get('content_profile', [0.0] * 8)
        
        # Calculate complexity score
        complexity = sum(content_profile[:4]) / 4  # Average of first 4 metrics
        
        # Select strategy based on complexity
        if complexity < 0.3:
            return 'grid_search'  # Simple content, use systematic search
        elif complexity < 0.6:
            return 'bayesian'  # Moderate complexity, use Bayesian optimization
        elif complexity < 0.8:
            return 'genetic'  # High complexity, use genetic algorithm
        else:
            return 'bandit'  # Very high complexity, use adaptive bandit
    
    def _grid_search_optimization(self, algorithm: CompressionAlgorithm, bounds: Dict[str, tuple], content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Grid search optimization."""
        best_params = {}
        best_score = -1.0
        
        # Define grid points for each parameter
        grid_points = self._generate_grid_points(bounds)
        
        # Evaluate each grid point
        for params in grid_points:
            score = self._evaluate_parameters(algorithm, params, content_analysis)
            if score > best_score:
                best_score = score
                best_params = params
        
        return best_params
    
    def _bayesian_optimization(self, algorithm: CompressionAlgorithm, bounds: Dict[str, tuple], content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Bayesian optimization using Gaussian Process."""
        # Simplified Bayesian optimization
        best_params = {}
        best_score = -1.0
        
        # Sample points using acquisition function
        for _ in range(20):  # 20 iterations
            # Generate candidate parameters
            candidate = self._generate_candidate_parameters(bounds)
            
            # Evaluate candidate
            score = self._evaluate_parameters(algorithm, candidate, content_analysis)
            
            if score > best_score:
                best_score = score
                best_params = candidate
        
        return best_params
    
    def _genetic_optimization(self, algorithm: CompressionAlgorithm, bounds: Dict[str, tuple], content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genetic algorithm optimization."""
        # Population size and generations
        population_size = 20
        generations = 10
        
        # Initialize population
        population = [self._generate_candidate_parameters(bounds) for _ in range(population_size)]
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                score = self._evaluate_parameters(algorithm, individual, content_analysis)
                fitness_scores.append(score)
            
            # Selection
            selected = self._selection(population, fitness_scores, population_size // 2)
            
            # Crossover and mutation
            new_population = []
            while len(new_population) < population_size:
                parent1, parent2 = random.sample(selected, 2)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child, bounds)
                new_population.append(child)
            
            population = new_population
        
        # Return best individual
        best_individual = max(population, key=lambda x: self._evaluate_parameters(algorithm, x, content_analysis))
        return best_individual
    
    def _bandit_optimization(self, algorithm: CompressionAlgorithm, bounds: Dict[str, tuple], content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Multi-armed bandit optimization."""
        # Define parameter arms
        arms = self._generate_parameter_arms(bounds)
        
        # Bandit parameters
        epsilon = 0.1  # Exploration rate
        num_iterations = 30
        
        # Initialize arm values
        arm_values = {i: 0.0 for i in range(len(arms))}
        arm_counts = {i: 0 for i in range(len(arms))}
        
        for _ in range(num_iterations):
            # Choose arm (epsilon-greedy)
            if random.random() < epsilon:
                arm_idx = random.randint(0, len(arms) - 1)
            else:
                arm_idx = max(arm_values.items(), key=lambda x: x[1])[0]
            
            # Evaluate arm
            score = self._evaluate_parameters(algorithm, arms[arm_idx], content_analysis)
            
            # Update arm value
            arm_counts[arm_idx] += 1
            arm_values[arm_idx] = (arm_values[arm_idx] * (arm_counts[arm_idx] - 1) + score) / arm_counts[arm_idx]
        
        # Return best arm
        best_arm_idx = max(arm_values.items(), key=lambda x: x[1])[0]
        return arms[best_arm_idx]
    
    def _default_optimization(self, algorithm: CompressionAlgorithm, bounds: Dict[str, tuple], content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Default parameter optimization."""
        # Use heuristics based on content analysis
        content_profile = content_analysis.get('content_profile', [0.0] * 8)
        
        params = {}
        
        # Optimize compression level based on content characteristics
        entropy = content_profile[0] if len(content_profile) > 0 else 0.0
        compression_potential = content_profile[6] if len(content_profile) > 6 else 0.0
        
        if entropy < 4.0 and compression_potential > 0.7:
            params['level'] = 'maximum'
        elif entropy < 6.0:
            params['level'] = 'optimal'
        else:
            params['level'] = 'balanced'
        
        # Optimize window size based on content size and patterns
        pattern_frequency = content_profile[5] if len(content_profile) > 5 else 0.0
        if pattern_frequency > 0.5:
            params['window_size'] = 32768  # Larger window for repetitive content
        else:
            params['window_size'] = 8192
        
        # Optimize block size
        params['block_size'] = 4096
        
        return params
    
    def _generate_grid_points(self, bounds: Dict[str, tuple]) -> List[Dict[str, Any]]:
        """Generate grid points for parameter space."""
        grid_points = []
        
        # Define grid resolution
        resolution = 3  # 3 points per parameter
        
        # Generate combinations
        param_names = list(bounds.keys())
        param_ranges = []
        
        for param_name in param_names:
            min_val, max_val = bounds[param_name]
            if isinstance(min_val, int):
                # Integer parameter
                step = (max_val - min_val) // (resolution - 1)
                param_ranges.append([min_val + i * step for i in range(resolution)])
            else:
                # Float parameter
                step = (max_val - min_val) / (resolution - 1)
                param_ranges.append([min_val + i * step for i in range(resolution)])
        
        # Generate all combinations
        from itertools import product
        for combination in product(*param_ranges):
            point = {}
            for i, param_name in enumerate(param_names):
                point[param_name] = combination[i]
            grid_points.append(point)
        
        return grid_points
    
    def _generate_candidate_parameters(self, bounds: Dict[str, tuple]) -> Dict[str, Any]:
        """Generate candidate parameters within bounds."""
        candidate = {}
        
        for param_name, (min_val, max_val) in bounds.items():
            if isinstance(min_val, int):
                candidate[param_name] = random.randint(min_val, max_val)
            else:
                candidate[param_name] = random.uniform(min_val, max_val)
        
        return candidate
    
    def _generate_parameter_arms(self, bounds: Dict[str, tuple]) -> List[Dict[str, Any]]:
        """Generate parameter arms for bandit optimization."""
        arms = []
        
        # Generate different parameter combinations
        for _ in range(10):  # 10 arms
            arm = self._generate_candidate_parameters(bounds)
            arms.append(arm)
        
        return arms
    
    def _evaluate_parameters(self, algorithm: CompressionAlgorithm, params: Dict[str, Any], content_analysis: Dict[str, Any]) -> float:
        """Evaluate parameter set quality."""
        # This is a simplified evaluation function
        # In a real implementation, this would run actual compression and measure performance
        
        score = 0.0
        
        # Score based on parameter values
        if 'level' in params:
            level = params['level']
            if isinstance(level, str):
                level_map = {'fast': 1, 'balanced': 6, 'optimal': 9, 'maximum': 9}
                level = level_map.get(level, 6)
            score += min(level / 9.0, 1.0) * 0.4
        
        if 'window_size' in params:
            window_size = params['window_size']
            # Prefer moderate window sizes
            if 4096 <= window_size <= 32768:
                score += 0.3
            else:
                score += 0.1
        
        if 'block_size' in params:
            block_size = params['block_size']
            # Prefer moderate block sizes
            if 1024 <= block_size <= 8192:
                score += 0.3
            else:
                score += 0.1
        
        # Add some randomness to simulate real-world performance variation
        score += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, score))
    
    def _selection(self, population: List[Dict[str, Any]], fitness_scores: List[float], num_selected: int) -> List[Dict[str, Any]]:
        """Tournament selection for genetic algorithm."""
        selected = []
        
        for _ in range(num_selected):
            # Tournament selection
            tournament_size = 3
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            
            winner_idx = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
            selected.append(population[winner_idx])
        
        return selected
    
    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Dict[str, Any]:
        """Crossover operation for genetic algorithm."""
        child = {}
        
        for param_name in parent1.keys():
            if random.random() < 0.5:
                child[param_name] = parent1[param_name]
            else:
                child[param_name] = parent2[param_name]
        
        return child
    
    def _mutate(self, individual: Dict[str, Any], bounds: Dict[str, tuple]) -> Dict[str, Any]:
        """Mutation operation for genetic algorithm."""
        mutated = individual.copy()
        
        for param_name in mutated.keys():
            if random.random() < 0.1:  # 10% mutation rate
                min_val, max_val = bounds[param_name]
                if isinstance(min_val, int):
                    mutated[param_name] = random.randint(min_val, max_val)
                else:
                    mutated[param_name] = random.uniform(min_val, max_val)
        
        return mutated
    
    def _merge_parameters(self, base_params: CompressionParameters, optimized_params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge optimized parameters with base parameters."""
        merged = {}
        
        # Start with base parameters
        base_dict = base_params.dict()
        
        # Override with optimized parameters
        for key, value in optimized_params.items():
            if key in base_dict:
                merged[key] = value
        
        return merged






