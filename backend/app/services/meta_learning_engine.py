"""
Meta-Learning Engine Service
Implements recursive self-improvement, Bayesian optimization, and parameter evolution
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
import asyncio
from scipy.stats import norm
from scipy.optimize import minimize

from app.models.meta_learning import (
    MetaLearningTrial,
    MetaLearningIteration,
    AlgorithmPerformance
)
from app.services.media_generator import MediaGenerator
from app.services.compression_service import CompressionService

logger = logging.getLogger(__name__)


class BayesianOptimizer:
    """Bayesian optimization for parameter search"""

    def __init__(self, parameter_space: Dict[str, List[Any]]):
        self.parameter_space = parameter_space
        self.observations: List[Tuple[Dict, float]] = []

    def acquisition_function(self, params: Dict[str, Any], exploration_weight: float = 0.1) -> float:
        """
        Upper Confidence Bound (UCB) acquisition function
        Balances exploitation (mean) and exploration (uncertainty)
        """
        if not self.observations:
            return 0.0

        # Calculate mean and std dev based on observations
        scores = [score for _, score in self.observations]
        mean_score = np.mean(scores)
        std_score = np.std(scores) if len(scores) > 1 else 1.0

        # Simple distance-based uncertainty estimation
        min_distance = float('inf')
        for obs_params, obs_score in self.observations:
            distance = self._param_distance(params, obs_params)
            min_distance = min(min_distance, distance)

        # Normalize distance to [0, 1] range
        uncertainty = min(min_distance / 10.0, 1.0)

        # UCB formula: mean + exploration_weight * uncertainty
        ucb = mean_score + exploration_weight * uncertainty * std_score
        return ucb

    def _param_distance(self, params1: Dict, params2: Dict) -> float:
        """Calculate normalized distance between parameter sets"""
        distance = 0.0
        count = 0

        for key in params1:
            if key in params2:
                val1, val2 = params1[key], params2[key]

                # Normalize based on parameter type
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    # Numeric parameters
                    param_range = self.parameter_space.get(key, [0, 1])
                    if isinstance(param_range, list) and len(param_range) > 1:
                        range_size = max(param_range) - min(param_range)
                        if range_size > 0:
                            distance += ((val1 - val2) / range_size) ** 2
                            count += 1
                else:
                    # Categorical parameters
                    distance += 0 if val1 == val2 else 1
                    count += 1

        return np.sqrt(distance / max(count, 1))

    def suggest_next_parameters(self, exploration_weight: float = 0.1) -> Dict[str, Any]:
        """
        Suggest next parameter configuration using Bayesian optimization
        """
        # Generate candidate parameter sets
        candidates = self._generate_candidates(n_candidates=20)

        # Evaluate acquisition function for each candidate
        best_candidate = None
        best_score = -float('inf')

        for candidate in candidates:
            score = self.acquisition_function(candidate, exploration_weight)
            if score > best_score:
                best_score = score
                best_candidate = candidate

        return best_candidate or self._sample_random_parameters()

    def _generate_candidates(self, n_candidates: int = 20) -> List[Dict[str, Any]]:
        """Generate candidate parameter configurations"""
        candidates = []

        for _ in range(n_candidates):
            candidate = self._sample_random_parameters()
            candidates.append(candidate)

        return candidates

    def _sample_random_parameters(self) -> Dict[str, Any]:
        """Sample random parameters from parameter space"""
        params = {}

        for key, values in self.parameter_space.items():
            if isinstance(values, list):
                if len(values) > 0:
                    if isinstance(values[0], (int, float)):
                        # Numeric range - sample uniformly
                        params[key] = np.random.uniform(min(values), max(values))
                    else:
                        # Categorical - sample randomly
                        params[key] = np.random.choice(values)
            else:
                params[key] = values

        return params

    def add_observation(self, params: Dict[str, Any], score: float):
        """Add observation to history"""
        self.observations.append((params, score))


class MetaLearningEngine:
    """
    Core meta-learning engine for recursive self-improvement
    """

    def __init__(self, db: Session):
        self.db = db
        self.media_generator = MediaGenerator()
        self.compression_service = CompressionService()

    async def create_trial(
        self,
        name: str,
        algorithm_family: str,
        target_metric: str,
        parameter_space: Dict[str, List[Any]],
        learning_rate: float = 0.01,
        max_iterations: int = 100,
        convergence_threshold: float = 0.001,
        inference_method: str = 'bayesian',
        self_modification_enabled: bool = False,
        description: Optional[str] = None
    ) -> MetaLearningTrial:
        """Create new meta-learning trial"""

        # Initialize with random parameters
        optimizer = BayesianOptimizer(parameter_space)
        initial_params = optimizer._sample_random_parameters()

        trial = MetaLearningTrial(
            name=name,
            description=description,
            algorithm_family=algorithm_family,
            target_metric=target_metric,
            learning_rate=learning_rate,
            max_iterations=max_iterations,
            convergence_threshold=convergence_threshold,
            parameter_space=parameter_space,
            current_parameters=initial_params,
            inference_method=inference_method,
            self_modification_enabled=self_modification_enabled,
            status='created'
        )

        self.db.add(trial)
        self.db.commit()
        self.db.refresh(trial)

        logger.info(f"Created meta-learning trial: {trial.id} - {name}")
        return trial

    async def run_iteration(
        self,
        trial_id: int,
        use_synthetic_data: bool = True,
        synthetic_config: Optional[Dict[str, Any]] = None
    ) -> MetaLearningIteration:
        """
        Execute single iteration of meta-learning trial
        """
        trial = self.db.query(MetaLearningTrial).filter(
            MetaLearningTrial.id == trial_id
        ).first()

        if not trial:
            raise ValueError(f"Trial {trial_id} not found")

        if trial.status == 'completed':
            raise ValueError(f"Trial {trial_id} already completed")

        # Update trial status
        if trial.status == 'created':
            trial.status = 'running'
            trial.started_at = datetime.utcnow()

        start_time = datetime.utcnow()

        # Get parameters for this iteration
        params = trial.current_parameters

        # Execute iteration
        metrics = await self._execute_iteration(
            trial=trial,
            parameters=params,
            use_synthetic_data=use_synthetic_data,
            synthetic_config=synthetic_config
        )

        # Calculate score based on target metric
        score = metrics.get(trial.target_metric, 0.0)

        # Calculate duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        # Calculate throughput (iterations per second)
        throughput = 1.0 / duration if duration > 0 else 0.0

        # Determine phase
        phase = self._determine_phase(trial)

        # Create iteration record
        iteration = MetaLearningIteration(
            trial_id=trial.id,
            iteration_number=trial.iteration_count + 1,
            parameters=params,
            metrics=metrics,
            score=score,
            synthetic_data_config=synthetic_config,
            phase=phase,
            duration_seconds=duration,
            throughput=throughput
        )

        self.db.add(iteration)

        # Update trial
        trial.iteration_count += 1
        trial.current_score = score

        # Update best score
        if trial.best_score is None or score > trial.best_score:
            trial.best_score = score
            logger.info(f"Trial {trial_id} - New best score: {score:.4f}")

        # Calculate improvement rate
        if trial.iteration_count > 1:
            prev_iterations = self.db.query(MetaLearningIteration).filter(
                MetaLearningIteration.trial_id == trial_id
            ).order_by(MetaLearningIteration.iteration_number.desc()).limit(5).all()

            if prev_iterations:
                prev_scores = [it.score for it in prev_iterations]
                trial.improvement_rate = np.mean(np.diff(prev_scores)) if len(prev_scores) > 1 else 0.0

        # Optimize parameters for next iteration
        next_params = await self._optimize_parameters(trial)
        trial.current_parameters = next_params

        # Check convergence
        converged = self._check_convergence(trial)
        if converged:
            trial.status = 'completed'
            trial.completed_at = datetime.utcnow()
            logger.info(f"Trial {trial_id} converged after {trial.iteration_count} iterations")
        elif trial.iteration_count >= trial.max_iterations:
            trial.status = 'completed'
            trial.completed_at = datetime.utcnow()
            logger.info(f"Trial {trial_id} reached max iterations: {trial.max_iterations}")

        self.db.commit()
        self.db.refresh(iteration)

        return iteration

    async def _execute_iteration(
        self,
        trial: MetaLearningTrial,
        parameters: Dict[str, Any],
        use_synthetic_data: bool = True,
        synthetic_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute iteration with given parameters
        Returns metrics dictionary
        """
        metrics = {}

        if trial.algorithm_family == 'compression':
            # Test compression with given parameters
            metrics = await self._test_compression(parameters, use_synthetic_data, synthetic_config)
        elif trial.algorithm_family == 'prediction':
            # Test prediction algorithm
            metrics = await self._test_prediction(parameters)
        elif trial.algorithm_family == 'optimization':
            # Test optimization algorithm
            metrics = await self._test_optimization(parameters)
        else:
            raise ValueError(f"Unknown algorithm family: {trial.algorithm_family}")

        return metrics

    async def _test_compression(
        self,
        parameters: Dict[str, Any],
        use_synthetic_data: bool = True,
        synthetic_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test compression algorithm with parameters"""

        # Generate synthetic data if requested
        if use_synthetic_data:
            synthetic_config = synthetic_config or {
                'complexity': 0.7,
                'entropy': 0.6,
                'redundancy': 0.3,
                'pattern': 'perlin'
            }

            # Generate test image
            test_data = await self.media_generator.generate_image_async(
                width=512,
                height=512,
                structure_type=synthetic_config.get('pattern', 'perlin'),
                complexity=synthetic_config.get('complexity', 0.7),
                entropy=synthetic_config.get('entropy', 0.6),
                redundancy=synthetic_config.get('redundancy', 0.3)
            )
        else:
            # Use real data (placeholder)
            test_data = None

        # Simulate compression metrics
        # In production, this would call actual compression algorithms
        compression_ratio = np.random.uniform(1.5, 3.0) * parameters.get('quality', 0.7)
        processing_time = np.random.uniform(0.5, 2.0) / parameters.get('speed_factor', 1.0)
        quality_score = parameters.get('quality', 0.7) * np.random.uniform(0.8, 1.0)

        metrics = {
            'compression_ratio': compression_ratio,
            'processing_time': processing_time,
            'quality_score': quality_score,
            'throughput': 1.0 / processing_time if processing_time > 0 else 0.0
        }

        return metrics

    async def _test_prediction(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Test prediction algorithm"""
        # Placeholder for prediction testing
        accuracy = np.random.uniform(0.7, 0.95) * parameters.get('model_complexity', 0.8)
        return {'accuracy': accuracy, 'f1_score': accuracy * 0.95}

    async def _test_optimization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Test optimization algorithm"""
        # Placeholder for optimization testing
        convergence_speed = np.random.uniform(0.5, 1.5) / parameters.get('learning_rate', 0.01)
        return {'convergence_speed': convergence_speed, 'final_value': np.random.uniform(0.8, 1.0)}

    def _determine_phase(self, trial: MetaLearningTrial) -> str:
        """Determine current phase of meta-learning"""
        total = trial.max_iterations
        current = trial.iteration_count

        if current < total * 0.3:
            return 'exploration'
        elif current < total * 0.7:
            return 'exploitation'
        else:
            return 'refinement'

    async def _optimize_parameters(self, trial: MetaLearningTrial) -> Dict[str, Any]:
        """
        Optimize parameters for next iteration using configured inference method
        """
        if trial.inference_method == 'bayesian':
            return await self._bayesian_optimize(trial)
        elif trial.inference_method == 'frequentist':
            return await self._frequentist_optimize(trial)
        elif trial.inference_method == 'bootstrap':
            return await self._bootstrap_optimize(trial)
        else:
            logger.warning(f"Unknown inference method: {trial.inference_method}, using Bayesian")
            return await self._bayesian_optimize(trial)

    async def _bayesian_optimize(self, trial: MetaLearningTrial) -> Dict[str, Any]:
        """Bayesian optimization for next parameters"""
        optimizer = BayesianOptimizer(trial.parameter_space)

        # Add all previous observations
        iterations = self.db.query(MetaLearningIteration).filter(
            MetaLearningIteration.trial_id == trial.id
        ).all()

        for iteration in iterations:
            optimizer.add_observation(iteration.parameters, iteration.score)

        # Determine exploration weight based on phase
        phase = self._determine_phase(trial)
        if phase == 'exploration':
            exploration_weight = 0.3
        elif phase == 'exploitation':
            exploration_weight = 0.1
        else:  # refinement
            exploration_weight = 0.05

        # Suggest next parameters
        next_params = optimizer.suggest_next_parameters(exploration_weight)
        return next_params

    async def _frequentist_optimize(self, trial: MetaLearningTrial) -> Dict[str, Any]:
        """Frequentist optimization - gradient-based"""
        # Get recent iterations
        recent_iterations = self.db.query(MetaLearningIteration).filter(
            MetaLearningIteration.trial_id == trial.id
        ).order_by(MetaLearningIteration.iteration_number.desc()).limit(10).all()

        if len(recent_iterations) < 2:
            # Not enough data, use random
            optimizer = BayesianOptimizer(trial.parameter_space)
            return optimizer._sample_random_parameters()

        # Calculate gradient approximation
        current_params = trial.current_parameters
        best_iteration = max(recent_iterations, key=lambda it: it.score)

        # Move towards best parameters
        next_params = {}
        for key in current_params:
            if key in best_iteration.parameters:
                current_val = current_params[key]
                best_val = best_iteration.parameters[key]

                if isinstance(current_val, (int, float)) and isinstance(best_val, (int, float)):
                    # Apply learning rate
                    next_params[key] = current_val + trial.learning_rate * (best_val - current_val)
                else:
                    next_params[key] = best_val
            else:
                next_params[key] = current_params[key]

        return next_params

    async def _bootstrap_optimize(self, trial: MetaLearningTrial) -> Dict[str, Any]:
        """Bootstrap optimization - resampling based"""
        iterations = self.db.query(MetaLearningIteration).filter(
            MetaLearningIteration.trial_id == trial.id
        ).all()

        if len(iterations) < 5:
            # Not enough data
            optimizer = BayesianOptimizer(trial.parameter_space)
            return optimizer._sample_random_parameters()

        # Bootstrap resample and find best
        n_bootstrap = 10
        best_params = None
        best_avg_score = -float('inf')

        for _ in range(n_bootstrap):
            # Resample with replacement
            sample = np.random.choice(iterations, size=len(iterations), replace=True)

            # Calculate average score for each parameter set
            param_scores = {}
            for iteration in sample:
                param_key = str(iteration.parameters)
                if param_key not in param_scores:
                    param_scores[param_key] = []
                param_scores[param_key].append(iteration.score)

            # Find best average
            for param_key, scores in param_scores.items():
                avg_score = np.mean(scores)
                if avg_score > best_avg_score:
                    best_avg_score = avg_score
                    best_params = eval(param_key)  # Convert back to dict

        return best_params or trial.current_parameters

    def _check_convergence(self, trial: MetaLearningTrial) -> bool:
        """Check if trial has converged"""
        if trial.iteration_count < 10:
            return False

        # Get recent iterations
        recent_iterations = self.db.query(MetaLearningIteration).filter(
            MetaLearningIteration.trial_id == trial.id
        ).order_by(MetaLearningIteration.iteration_number.desc()).limit(10).all()

        if len(recent_iterations) < 10:
            return False

        # Check if score variance is below threshold
        scores = [it.score for it in recent_iterations]
        score_std = np.std(scores)

        return score_std < trial.convergence_threshold

    async def recursive_improve(self, trial_id: int) -> MetaLearningTrial:
        """
        Create child trial with improved parameter space based on parent results
        """
        parent_trial = self.db.query(MetaLearningTrial).filter(
            MetaLearningTrial.id == trial_id
        ).first()

        if not parent_trial:
            raise ValueError(f"Trial {trial_id} not found")

        if not parent_trial.self_modification_enabled:
            raise ValueError(f"Trial {trial_id} does not have self-modification enabled")

        # Analyze parent trial results
        best_iterations = self.db.query(MetaLearningIteration).filter(
            MetaLearningIteration.trial_id == trial_id
        ).order_by(MetaLearningIteration.score.desc()).limit(5).all()

        # Refine parameter space based on best results
        refined_space = self._refine_parameter_space(
            parent_trial.parameter_space,
            [it.parameters for it in best_iterations]
        )

        # Create child trial
        child_trial = await self.create_trial(
            name=f"{parent_trial.name} - Generation {parent_trial.recursion_depth + 1}",
            algorithm_family=parent_trial.algorithm_family,
            target_metric=parent_trial.target_metric,
            parameter_space=refined_space,
            learning_rate=parent_trial.learning_rate * 0.9,  # Decrease learning rate
            max_iterations=parent_trial.max_iterations,
            convergence_threshold=parent_trial.convergence_threshold * 0.8,  # Tighter convergence
            inference_method=parent_trial.inference_method,
            self_modification_enabled=True,
            description=f"Recursive improvement from trial {trial_id}"
        )

        child_trial.parent_trial_id = trial_id
        child_trial.recursion_depth = parent_trial.recursion_depth + 1

        self.db.commit()
        self.db.refresh(child_trial)

        logger.info(f"Created recursive child trial {child_trial.id} from parent {trial_id}")
        return child_trial

    def _refine_parameter_space(
        self,
        original_space: Dict[str, List[Any]],
        best_params: List[Dict[str, Any]]
    ) -> Dict[str, List[Any]]:
        """Refine parameter space based on best results"""
        refined = {}

        for key, values in original_space.items():
            if isinstance(values, list) and len(values) > 0:
                if isinstance(values[0], (int, float)):
                    # Numeric parameter - narrow range around best values
                    best_values = [p.get(key, values[0]) for p in best_params if key in p]
                    if best_values:
                        mean_val = np.mean(best_values)
                        std_val = np.std(best_values) if len(best_values) > 1 else (max(values) - min(values)) * 0.1

                        # New range: mean ± 2*std, clipped to original range
                        new_min = max(min(values), mean_val - 2 * std_val)
                        new_max = min(max(values), mean_val + 2 * std_val)

                        refined[key] = [new_min, new_max]
                    else:
                        refined[key] = values
                else:
                    # Categorical - keep most successful values
                    value_counts = {}
                    for p in best_params:
                        if key in p:
                            val = p[key]
                            value_counts[val] = value_counts.get(val, 0) + 1

                    if value_counts:
                        # Keep top 50% of values
                        sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
                        top_values = [v for v, _ in sorted_values[:max(1, len(sorted_values) // 2)]]
                        refined[key] = top_values
                    else:
                        refined[key] = values
            else:
                refined[key] = values

        return refined

    async def update_algorithm_performance(self, trial: MetaLearningTrial):
        """Update aggregated algorithm performance metrics"""
        # Determine algorithm name from parameters
        algorithm_name = trial.current_parameters.get('algorithm', trial.algorithm_family)

        # Get or create performance record
        perf = self.db.query(AlgorithmPerformance).filter(
            AlgorithmPerformance.algorithm_name == algorithm_name
        ).first()

        if not perf:
            perf = AlgorithmPerformance(
                algorithm_name=algorithm_name,
                algorithm_family=trial.algorithm_family
            )
            self.db.add(perf)

        # Update statistics
        perf.total_trials += 1
        if trial.status == 'completed':
            perf.successful_trials += 1

        # Update scores
        if trial.best_score is not None:
            if perf.best_score is None or trial.best_score > perf.best_score:
                perf.best_score = trial.best_score
                perf.best_parameters = trial.current_parameters

            if perf.worst_score is None or trial.best_score < perf.worst_score:
                perf.worst_score = trial.best_score

            # Update rolling average
            if perf.average_score is None:
                perf.average_score = trial.best_score
            else:
                perf.average_score = (perf.average_score * (perf.total_trials - 1) + trial.best_score) / perf.total_trials

        # Update convergence iterations
        if trial.status == 'completed':
            if perf.average_convergence_iterations is None:
                perf.average_convergence_iterations = float(trial.iteration_count)
            else:
                perf.average_convergence_iterations = (
                    (perf.average_convergence_iterations * (perf.successful_trials - 1) + trial.iteration_count)
                    / perf.successful_trials
                )

        # Update reliability score
        perf.reliability_score = perf.successful_trials / perf.total_trials if perf.total_trials > 0 else 0.0

        perf.last_used_at = datetime.utcnow()
        perf.times_selected += 1

        self.db.commit()
        self.db.refresh(perf)

        return perf
