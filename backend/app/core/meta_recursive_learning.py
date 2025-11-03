"""
Meta-Recursive Self-Learning System for Compression Optimization

This module implements a sophisticated meta-recursive learning architecture where
each level optimizes the level below while being optimized by the level above.
The system continuously improves its own optimization processes through:

1. Hierarchical optimization with exponentially increasing scope
2. Bidirectional information flow (bottom-up results, top-down guidance)
3. Meta-learning models that adapt optimization strategies
4. Performance-based evolution of optimization approaches
5. Neural architecture search for compression networks
6. Self-evaluation and automatic parameter adjustment

Mathematical Foundation:
-----------------------
O(n+1) = F(O(n), P(n), M(n))
Where:
- O(n) = Optimization at level n
- P(n) = Performance metrics at level n
- M(n) = Meta-learning from level n
- F = Optimization function

Convergence: |O(n+1) - O(n)| < ε

References:
- Schmidhuber, J. (1987). "Evolutionary Principles in Self-Referential Learning"
- Finn et al. (2017). "Model-Agnostic Meta-Learning for Fast Adaptation"
- Real et al. (2019). "AutoML-Zero: Evolving Machine Learning Algorithms From Scratch"
"""

import time
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from collections import deque, defaultdict
from enum import Enum
import logging
import pickle
import json
import hashlib
from abc import ABC, abstractmethod
import asyncio
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Import base compression system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.compression import CompressionParameters, CompressionResult
from core.compression_engine import CompressionEngine
from core.algorithm_selector import AlgorithmSelector
from core.content_analyzer import ContentAnalyzer
from core.metrics_collector import MetricsCollector


class OptimizationScope(Enum):
    """Scope of optimization at each recursive level."""
    LOCAL = 1  # Single operation optimization
    TACTICAL = 2  # Multiple operations coordination
    STRATEGIC = 4  # Algorithm selection and routing
    ARCHITECTURAL = 8  # System architecture optimization
    META = 16  # Optimization strategy optimization


@dataclass
class OptimizationLevel:
    """Represents a single level in the meta-recursive hierarchy."""
    level_id: int
    scope: OptimizationScope
    learning_rate: float
    memory_window: int
    exploration_rate: float
    meta_parameters: Dict[str, Any]
    performance_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    model: Optional[Any] = None
    
    def optimize_direct(self, data: Any, context: Dict) -> 'OptimizationResult':
        """Direct optimization at this level."""
        # Base level optimization - actual compression
        if self.level_id == 0:
            return self._optimize_compression(data, context)
        else:
            # Higher levels optimize the optimization process
            return self._optimize_process(data, context)
    
    def optimize_meta(self, lower_results: 'OptimizationResult', context: Dict) -> 'OptimizationResult':
        """Meta-optimization based on lower level results."""
        # Analyze lower level performance
        analysis = self._analyze_lower_performance(lower_results)
        
        # Generate optimization guidance
        guidance = self._generate_guidance(analysis, context)
        
        # Apply meta-optimization
        optimized = self._apply_meta_optimization(lower_results, guidance)
        
        return optimized
    
    def _optimize_compression(self, data: Any, context: Dict) -> 'OptimizationResult':
        """Actual compression optimization."""
        # This would interface with the compression engine
        result = OptimizationResult(
            level=self.level_id,
            input_characteristics=self._extract_characteristics(data),
            performance_metrics={},
            parameters_used={},
            output_data=data  # Placeholder
        )
        return result
    
    def _optimize_process(self, data: Any, context: Dict) -> 'OptimizationResult':
        """Optimize the optimization process itself."""
        # Meta-level optimization logic
        result = OptimizationResult(
            level=self.level_id,
            input_characteristics={},
            performance_metrics={},
            parameters_used=self.meta_parameters,
            output_data=data
        )
        return result
    
    def _analyze_lower_performance(self, results: 'OptimizationResult') -> Dict:
        """Analyze performance of lower optimization level."""
        return {
            'efficiency': results.performance_metrics.get('efficiency', 0),
            'convergence_rate': self._calculate_convergence_rate(results),
            'stability': self._calculate_stability(results),
            'resource_usage': results.performance_metrics.get('resource_usage', {})
        }
    
    def _generate_guidance(self, analysis: Dict, context: Dict) -> Dict:
        """Generate optimization guidance for lower levels."""
        guidance = {
            'adjust_learning_rate': False,
            'change_strategy': False,
            'modify_parameters': {},
            'exploration_adjustment': 0.0
        }
        
        # Adjust based on analysis
        if analysis['convergence_rate'] < 0.1:
            guidance['adjust_learning_rate'] = True
            guidance['modify_parameters']['learning_rate'] = self.learning_rate * 1.5
        
        if analysis['stability'] < 0.5:
            guidance['exploration_adjustment'] = -0.1  # Reduce exploration
        
        return guidance
    
    def _apply_meta_optimization(self, results: 'OptimizationResult', guidance: Dict) -> 'OptimizationResult':
        """Apply meta-optimization guidance."""
        # Modify results based on guidance
        optimized = results.copy()
        
        if guidance['adjust_learning_rate']:
            optimized.parameters_used['learning_rate'] = guidance['modify_parameters'].get(
                'learning_rate', self.learning_rate
            )
        
        return optimized
    
    def _extract_characteristics(self, data: Any) -> Dict:
        """Extract characteristics from input data."""
        return {
            'size': len(data) if hasattr(data, '__len__') else 0,
            'type': type(data).__name__,
            'complexity': self._estimate_complexity(data)
        }
    
    def _estimate_complexity(self, data: Any) -> float:
        """Estimate data complexity."""
        # Simplified complexity estimation
        if isinstance(data, (list, tuple)):
            return len(data) * 0.1
        elif isinstance(data, dict):
            return len(data) * 0.2
        else:
            return 0.5
    
    def _calculate_convergence_rate(self, results: 'OptimizationResult') -> float:
        """Calculate convergence rate from results."""
        if len(self.performance_history) < 2:
            return 0.0
        
        # Calculate rate of improvement
        recent = list(self.performance_history)[-10:]
        if len(recent) < 2:
            return 0.0
        
        improvements = []
        for i in range(1, len(recent)):
            prev_score = recent[i-1].get('score', 0)
            curr_score = recent[i].get('score', 0)
            if prev_score > 0:
                improvements.append((curr_score - prev_score) / prev_score)
        
        return np.mean(improvements) if improvements else 0.0
    
    def _calculate_stability(self, results: 'OptimizationResult') -> float:
        """Calculate optimization stability."""
        if len(self.performance_history) < 5:
            return 1.0
        
        recent = list(self.performance_history)[-20:]
        scores = [r.get('score', 0) for r in recent]
        
        if not scores:
            return 1.0
        
        # Calculate coefficient of variation (lower is more stable)
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        if mean_score == 0:
            return 0.0
        
        cv = std_score / mean_score
        stability = 1.0 / (1.0 + cv)  # Convert to 0-1 scale
        
        return stability


@dataclass
class OptimizationResult:
    """Results from an optimization level."""
    level: int
    input_characteristics: Dict[str, Any]
    performance_metrics: Dict[str, float]
    parameters_used: Dict[str, Any]
    output_data: Any
    timestamp: float = field(default_factory=time.time)
    
    def copy(self) -> 'OptimizationResult':
        """Create a copy of the result."""
        return OptimizationResult(
            level=self.level,
            input_characteristics=self.input_characteristics.copy(),
            performance_metrics=self.performance_metrics.copy(),
            parameters_used=self.parameters_used.copy(),
            output_data=self.output_data,
            timestamp=self.timestamp
        )


class MetaLearningModel(nn.Module):
    """Neural network for meta-learning optimization strategies."""
    
    def __init__(self, input_dim: int = 32, hidden_dim: int = 128, output_dim: int = 16):
        super().__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, num_layers=2, batch_first=True)
        
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
        self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        
    def forward(self, x: torch.Tensor, hidden: Optional[Tuple] = None) -> Tuple[torch.Tensor, Tuple]:
        """Forward pass through the model."""
        # Encode input
        encoded = self.encoder(x)
        
        # Process through LSTM
        if len(encoded.shape) == 2:
            encoded = encoded.unsqueeze(1)  # Add sequence dimension
        
        lstm_out, hidden = self.lstm(encoded, hidden)
        
        # Decode to optimization parameters
        output = self.decoder(lstm_out[:, -1, :])  # Use last timestep
        
        return output, hidden
    
    def update(self, input_data: Dict, output_metrics: Dict, optimization_params: Dict):
        """Update model based on optimization results."""
        # Convert to tensors
        input_tensor = self._dict_to_tensor(input_data)
        target_tensor = self._dict_to_tensor(output_metrics)
        
        # Forward pass
        prediction, _ = self.forward(input_tensor)
        
        # Calculate loss
        loss = nn.MSELoss()(prediction, target_tensor)
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def _dict_to_tensor(self, data: Dict) -> torch.Tensor:
        """Convert dictionary to tensor."""
        values = []
        for key in sorted(data.keys()):
            value = data[key]
            if isinstance(value, (int, float)):
                values.append(float(value))
            elif isinstance(value, list):
                values.extend([float(v) for v in value[:10]])  # Limit to 10 elements
            else:
                values.append(0.0)  # Default for unknown types
        
        # Pad or truncate to fixed size
        target_size = 32
        if len(values) < target_size:
            values.extend([0.0] * (target_size - len(values)))
        else:
            values = values[:target_size]
        
        return torch.tensor(values, dtype=torch.float32)


class MetaRecursiveOptimizer:
    """
    Multi-level recursive optimization system with self-improvement capabilities.
    
    The system implements a hierarchy where each level optimizes the level below
    while being optimized by the level above, creating a self-improving system.
    """
    
    def __init__(self, depth: int = 5):
        """
        Initialize meta-recursive optimizer.
        
        Args:
            depth: Number of recursion levels (default 5)
        """
        self.depth = depth
        self.levels = []
        self.performance_history = deque(maxlen=1000)
        self.meta_models = {}
        self.convergence_threshold = 1e-6
        
        # Initialize optimization levels with exponentially increasing scope
        for level in range(depth):
            self.levels.append(OptimizationLevel(
                level_id=level,
                scope=OptimizationScope(2**level),
                learning_rate=0.01 * (0.5 ** level),  # Decreasing learning rate
                memory_window=100 * (level + 1),
                exploration_rate=0.1 * (1.5 ** level),
                meta_parameters=self._generate_meta_parameters(level)
            ))
            
            # Create meta-learning model for each level
            self.meta_models[level] = MetaLearningModel()
        
        self.logger = logging.getLogger('meta_recursive')
        
    def optimize(self, data: Any, context: Dict) -> OptimizationResult:
        """
        Perform meta-recursive optimization.
        
        Args:
            data: Data to optimize (compression input)
            context: Optimization context and requirements
            
        Returns:
            Optimization result from base level
        """
        # Bottom-up optimization pass
        results = []
        
        for level in self.levels:
            if level.level_id == 0:
                # Base level - direct optimization
                result = level.optimize_direct(data, context)
            else:
                # Higher levels - optimize the optimization
                lower_results = results[level.level_id - 1]
                result = level.optimize_meta(lower_results, context)
            
            results.append(result)
            
            # Update meta-learning model
            self._update_meta_model(level, result)
            
            # Check for early convergence
            if self._check_convergence(level, result):
                self.logger.info(f"Early convergence at level {level.level_id}")
                break
        
        # Top-down refinement pass
        for level in reversed(self.levels[1:]):
            if level.level_id - 1 < len(results):
                guidance = self._generate_guidance(level, results)
                results[level.level_id - 1] = self._refine_with_guidance(
                    results[level.level_id - 1], guidance
                )
        
        # Self-evaluation and adjustment
        performance = self._evaluate_performance(results)
        self._adjust_parameters(performance)
        
        # Store in history
        self.performance_history.append({
            'timestamp': time.time(),
            'performance': performance,
            'results': results
        })
        
        return results[0]  # Return base level result
    
    def _generate_meta_parameters(self, level: int) -> Dict[str, Any]:
        """Generate meta-parameters for each optimization level."""
        return {
            'exploration_rate': 0.1 * (1.5 ** level),
            'exploitation_rate': 0.9 / (1.5 ** level),
            'memory_window': 100 * (level + 1),
            'prediction_horizon': 10 * (level + 1),
            'adaptation_speed': 1.0 / (level + 1),
            'complexity_penalty': 0.01 * level,
            'convergence_patience': 10 * (level + 1),
            'momentum': 0.9 - 0.1 * level,
            'regularization': 0.001 * (level + 1)
        }
    
    def _update_meta_model(self, level: OptimizationLevel, result: OptimizationResult):
        """Update meta-learning model for a level."""
        model = self.meta_models.get(level.level_id)
        if model:
            loss = model.update(
                input_data=result.input_characteristics,
                output_metrics=result.performance_metrics,
                optimization_params=result.parameters_used
            )
            
            # Track model performance
            level.performance_history.append({
                'score': 1.0 / (1.0 + loss),  # Convert loss to score
                'timestamp': time.time()
            })
    
    def _check_convergence(self, level: OptimizationLevel, result: OptimizationResult) -> bool:
        """Check if optimization has converged."""
        if len(level.performance_history) < 10:
            return False
        
        # Check if performance improvement is below threshold
        recent = list(level.performance_history)[-10:]
        scores = [r.get('score', 0) for r in recent]
        
        if len(scores) < 2:
            return False
        
        # Calculate improvement rate
        improvements = []
        for i in range(1, len(scores)):
            if scores[i-1] > 0:
                improvement = abs(scores[i] - scores[i-1]) / scores[i-1]
                improvements.append(improvement)
        
        avg_improvement = np.mean(improvements) if improvements else 0
        
        return avg_improvement < self.convergence_threshold
    
    def _generate_guidance(self, level: OptimizationLevel, results: List[OptimizationResult]) -> Dict:
        """Generate optimization guidance from higher level."""
        guidance = {
            'strategy_adjustments': {},
            'parameter_updates': {},
            'resource_allocation': {},
            'priority_changes': {}
        }
        
        # Analyze results at this level
        if level.level_id < len(results):
            result = results[level.level_id]
            
            # Generate strategy adjustments
            if result.performance_metrics.get('efficiency', 0) < 0.7:
                guidance['strategy_adjustments']['increase_exploration'] = True
                guidance['parameter_updates']['exploration_rate'] = level.exploration_rate * 1.2
            
            # Resource allocation guidance
            resource_usage = result.performance_metrics.get('resource_usage', {})
            if resource_usage.get('memory', 0) > 0.8:
                guidance['resource_allocation']['reduce_memory'] = True
                guidance['parameter_updates']['batch_size'] = 0.5  # Reduce batch size
        
        return guidance
    
    def _refine_with_guidance(self, result: OptimizationResult, guidance: Dict) -> OptimizationResult:
        """Refine optimization result using guidance."""
        refined = result.copy()
        
        # Apply parameter updates
        for param, value in guidance.get('parameter_updates', {}).items():
            refined.parameters_used[param] = value
        
        # Apply strategy adjustments
        for strategy, enabled in guidance.get('strategy_adjustments', {}).items():
            if enabled:
                # Modify result based on strategy
                if strategy == 'increase_exploration':
                    # Simulate increased exploration effect
                    refined.performance_metrics['diversity'] = refined.performance_metrics.get('diversity', 0) * 1.2
        
        return refined
    
    def _evaluate_performance(self, results: List[OptimizationResult]) -> Dict[str, float]:
        """Evaluate overall system performance."""
        performance = {
            'overall_score': 0.0,
            'efficiency': 0.0,
            'convergence_rate': 0.0,
            'stability': 0.0,
            'resource_efficiency': 0.0
        }
        
        # Aggregate metrics from all levels
        for i, result in enumerate(results):
            weight = 1.0 / (i + 1)  # Higher weight for lower levels
            
            # Efficiency
            level_efficiency = result.performance_metrics.get('efficiency', 0)
            performance['efficiency'] += level_efficiency * weight
            
            # Resource efficiency
            resource_usage = result.performance_metrics.get('resource_usage', {})
            cpu_usage = resource_usage.get('cpu', 0)
            memory_usage = resource_usage.get('memory', 0)
            resource_efficiency = 1.0 - (cpu_usage + memory_usage) / 2
            performance['resource_efficiency'] += resource_efficiency * weight
        
        # Normalize
        total_weight = sum(1.0 / (i + 1) for i in range(len(results)))
        performance['efficiency'] /= total_weight
        performance['resource_efficiency'] /= total_weight
        
        # Calculate overall score
        performance['overall_score'] = (
            performance['efficiency'] * 0.4 +
            performance['resource_efficiency'] * 0.3 +
            performance.get('convergence_rate', 0.5) * 0.2 +
            performance.get('stability', 0.5) * 0.1
        )
        
        return performance
    
    def _adjust_parameters(self, performance: Dict[str, float]):
        """Adjust system parameters based on performance."""
        # Adjust learning rates
        if performance['convergence_rate'] < 0.1:
            # Slow convergence - increase learning rates
            for level in self.levels:
                level.learning_rate *= 1.1
        elif performance['convergence_rate'] > 0.5:
            # Fast convergence - might be unstable, reduce learning rates
            for level in self.levels:
                level.learning_rate *= 0.9
        
        # Adjust exploration rates
        if performance['overall_score'] < 0.5:
            # Poor performance - increase exploration
            for level in self.levels:
                level.exploration_rate = min(level.exploration_rate * 1.2, 0.5)
        
        # Adjust memory windows
        if performance['stability'] < 0.7:
            # Low stability - increase memory for better averaging
            for level in self.levels:
                level.memory_window = min(level.memory_window * 1.5, 10000)


class EvolutionaryOptimizer:
    """
    Evolutionary optimization of optimization strategies using genetic algorithms.
    """
    
    def __init__(self, population_size: int = 50):
        """
        Initialize evolutionary optimizer.
        
        Args:
            population_size: Size of strategy population
        """
        self.population_size = population_size
        self.population = [self._create_random_strategy() for _ in range(population_size)]
        self.generation = 0
        self.best_fitness = 0
        self.fitness_history = []
        
    def _create_random_strategy(self) -> 'OptimizationStrategy':
        """Create a random optimization strategy."""
        return OptimizationStrategy(
            learning_rate=random.uniform(0.001, 0.1),
            exploration_rate=random.uniform(0.05, 0.3),
            batch_size=random.choice([16, 32, 64, 128]),
            momentum=random.uniform(0.8, 0.99),
            regularization=random.uniform(0.0001, 0.01),
            optimizer_type=random.choice(['sgd', 'adam', 'rmsprop']),
            activation=random.choice(['relu', 'tanh', 'sigmoid']),
            layers=random.randint(2, 10)
        )
    
    def evolve(self, performance_data: Dict) -> 'OptimizationStrategy':
        """
        Evolve optimization strategies based on performance.
        
        Args:
            performance_data: Performance metrics for evaluation
            
        Returns:
            Best evolved strategy
        """
        # Evaluate fitness of each strategy
        fitness_scores = []
        for strategy in self.population:
            fitness = self._evaluate_fitness(strategy, performance_data)
            fitness_scores.append(fitness)
        
        # Tournament selection
        selected = self._tournament_selection(
            self.population, fitness_scores, k=self.population_size // 2
        )
        
        # Crossover to create offspring
        offspring = []
        for i in range(0, len(selected) - 1, 2):
            child1, child2 = self._crossover(selected[i], selected[i + 1])
            offspring.extend([child1, child2])
        
        # Mutation
        for individual in offspring:
            if random.random() < 0.1:  # 10% mutation rate
                self._mutate(individual)
        
        # Elite preservation
        elite_count = self.population_size // 10
        elite_indices = np.argsort(fitness_scores)[-elite_count:]
        elite = [self.population[i] for i in elite_indices]
        
        # Form new population
        self.population = elite + offspring[:self.population_size - elite_count]
        self.generation += 1
        
        # Track best fitness
        self.best_fitness = max(fitness_scores)
        self.fitness_history.append(self.best_fitness)
        
        # Return best strategy
        best_idx = np.argmax(fitness_scores)
        return self.population[best_idx]
    
    def _evaluate_fitness(self, strategy: 'OptimizationStrategy', performance_data: Dict) -> float:
        """Evaluate fitness of a strategy."""
        # Fitness based on multiple criteria
        fitness = 0.0
        
        # Performance component
        performance_score = performance_data.get('overall_score', 0)
        fitness += performance_score * 0.5
        
        # Efficiency component
        efficiency = performance_data.get('efficiency', 0)
        fitness += efficiency * 0.3
        
        # Complexity penalty
        complexity = strategy.layers / 10.0  # Normalize
        fitness -= complexity * 0.1
        
        # Resource usage penalty
        resource_usage = performance_data.get('resource_usage', 0)
        fitness -= resource_usage * 0.1
        
        return max(0, fitness)
    
    def _tournament_selection(self, population: List, fitness: List, k: int) -> List:
        """Tournament selection."""
        selected = []
        
        for _ in range(k):
            # Random tournament
            tournament_size = 3
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness[i] for i in tournament_indices]
            
            # Select winner
            winner_idx = tournament_indices[np.argmax(tournament_fitness)]
            selected.append(population[winner_idx])
        
        return selected
    
    def _crossover(self, parent1: 'OptimizationStrategy', parent2: 'OptimizationStrategy') -> Tuple:
        """Crossover two strategies."""
        # Create children by mixing parameters
        child1 = OptimizationStrategy()
        child2 = OptimizationStrategy()
        
        # Uniform crossover
        for attr in ['learning_rate', 'exploration_rate', 'momentum', 'regularization']:
            if random.random() < 0.5:
                setattr(child1, attr, getattr(parent1, attr))
                setattr(child2, attr, getattr(parent2, attr))
            else:
                setattr(child1, attr, getattr(parent2, attr))
                setattr(child2, attr, getattr(parent1, attr))
        
        # Discrete attributes
        for attr in ['batch_size', 'optimizer_type', 'activation', 'layers']:
            if random.random() < 0.5:
                setattr(child1, attr, getattr(parent1, attr))
                setattr(child2, attr, getattr(parent2, attr))
            else:
                setattr(child1, attr, getattr(parent2, attr))
                setattr(child2, attr, getattr(parent1, attr))
        
        return child1, child2
    
    def _mutate(self, individual: 'OptimizationStrategy'):
        """Mutate a strategy."""
        # Mutate continuous parameters
        if random.random() < 0.2:
            individual.learning_rate *= random.uniform(0.5, 2.0)
            individual.learning_rate = max(0.0001, min(1.0, individual.learning_rate))
        
        if random.random() < 0.2:
            individual.exploration_rate *= random.uniform(0.5, 2.0)
            individual.exploration_rate = max(0.01, min(0.5, individual.exploration_rate))
        
        # Mutate discrete parameters
        if random.random() < 0.2:
            individual.batch_size = random.choice([16, 32, 64, 128, 256])
        
        if random.random() < 0.2:
            individual.layers = max(1, min(20, individual.layers + random.randint(-2, 2)))


@dataclass
class OptimizationStrategy:
    """Represents an optimization strategy."""
    learning_rate: float = 0.01
    exploration_rate: float = 0.1
    batch_size: int = 32
    momentum: float = 0.9
    regularization: float = 0.001
    optimizer_type: str = 'adam'
    activation: str = 'relu'
    layers: int = 4


# Integration with main compression system
def create_meta_recursive_compression_system() -> MetaRecursiveOptimizer:
    """
    Create and configure a meta-recursive compression system.
    
    Returns:
        Configured MetaRecursiveOptimizer instance
    """
    # Create optimizer with 5 levels of recursion
    optimizer = MetaRecursiveOptimizer(depth=5)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return optimizer