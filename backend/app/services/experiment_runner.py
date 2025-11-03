"""
Experiment Runner Service
Multi-phase experiment execution with dynamic algorithm selection
"""

from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
import logging
import asyncio
from itertools import product

from app.models.meta_learning import ExperimentRun, MetaLearningTrial
from app.services.statistical_inference import StatisticalInference
from app.services.meta_learning_engine import MetaLearningEngine

logger = logging.getLogger(__name__)


class ParameterGrid:
    """
    Multi-dimensional parameter grid generator
    """

    def __init__(self, parameter_dimensions: Dict[str, List[Any]]):
        """
        Args:
            parameter_dimensions: Dict of {dimension_name: [values]}
        """
        self.parameter_dimensions = parameter_dimensions

    def generate_grid(self, method: str = 'grid') -> List[Dict[str, Any]]:
        """
        Generate parameter combinations

        Args:
            method: 'grid' for full grid, 'random' for random sampling

        Returns:
            List of parameter dictionaries
        """
        if method == 'grid':
            return self._grid_search()
        elif method == 'random':
            return self._random_search()
        else:
            raise ValueError(f"Unknown method: {method}")

    def _grid_search(self) -> List[Dict[str, Any]]:
        """Full grid search - all combinations"""
        if not self.parameter_dimensions:
            return [{}]

        keys = list(self.parameter_dimensions.keys())
        values = [self.parameter_dimensions[k] for k in keys]

        # Generate all combinations
        combinations = list(product(*values))

        # Convert to list of dicts
        result = []
        for combo in combinations:
            param_dict = {k: v for k, v in zip(keys, combo)}
            result.append(param_dict)

        return result

    def _random_search(self, n_samples: int = 50) -> List[Dict[str, Any]]:
        """Random search - sample parameter space"""
        result = []

        for _ in range(n_samples):
            param_dict = {}
            for key, values in self.parameter_dimensions.items():
                if isinstance(values, list):
                    if len(values) > 0:
                        if isinstance(values[0], (int, float)):
                            # Sample uniformly from range
                            param_dict[key] = np.random.uniform(min(values), max(values))
                        else:
                            # Random choice from categorical
                            param_dict[key] = np.random.choice(values)
                else:
                    param_dict[key] = values

            result.append(param_dict)

        return result

    def get_size(self) -> int:
        """Get total number of combinations in grid"""
        if not self.parameter_dimensions:
            return 0

        size = 1
        for values in self.parameter_dimensions.values():
            size *= len(values) if isinstance(values, list) else 1

        return size


class ExperimentPhase:
    """
    Single phase of multi-phase experiment
    """

    def __init__(
        self,
        name: str,
        algorithm: str,
        parameter_space: Dict[str, List[Any]],
        metric_weights: Optional[Dict[str, float]] = None,
        transition_criteria: Optional[Dict[str, Any]] = None,
        statistical_method: str = 'bayesian'
    ):
        self.name = name
        self.algorithm = algorithm
        self.parameter_space = parameter_space
        self.metric_weights = metric_weights or {}
        self.transition_criteria = transition_criteria or {}
        self.statistical_method = statistical_method
        self.results: List[Dict[str, Any]] = []

    def evaluate_transition(self) -> bool:
        """
        Check if phase should transition to next

        Returns:
            True if transition criteria met
        """
        if not self.transition_criteria or not self.results:
            return False

        # Check minimum iterations
        min_iterations = self.transition_criteria.get('min_iterations', 0)
        if len(self.results) < min_iterations:
            return False

        # Check score threshold
        score_threshold = self.transition_criteria.get('score_threshold')
        if score_threshold is not None:
            recent_scores = [r['score'] for r in self.results[-10:]]
            avg_score = np.mean(recent_scores)
            if avg_score < score_threshold:
                return False

        # Check convergence
        if self.transition_criteria.get('check_convergence', False):
            if len(self.results) >= 10:
                recent_scores = [r['score'] for r in self.results[-10:]]
                score_std = np.std(recent_scores)
                convergence_threshold = self.transition_criteria.get('convergence_threshold', 0.01)
                if score_std > convergence_threshold:
                    return False

        return True

    def calculate_weighted_score(self, metrics: Dict[str, float]) -> float:
        """
        Calculate weighted score from metrics

        Args:
            metrics: Dictionary of metric values

        Returns:
            Weighted score
        """
        if not self.metric_weights:
            # Default: use first metric
            return list(metrics.values())[0] if metrics else 0.0

        score = 0.0
        total_weight = 0.0

        for metric_name, weight in self.metric_weights.items():
            if metric_name in metrics:
                score += weight * metrics[metric_name]
                total_weight += weight

        # Normalize by total weight
        return score / total_weight if total_weight > 0 else 0.0


class ExperimentRunner:
    """
    Multi-phase experiment runner with statistical analysis
    """

    def __init__(self, db: Session):
        self.db = db
        self.meta_learning_engine = MetaLearningEngine(db)
        self.statistical_inference = StatisticalInference()

    async def create_experiment(
        self,
        name: str,
        description: Optional[str],
        experiment_type: str,
        parameter_dimensions: Dict[str, List[Any]],
        statistical_methods: List[str],
        phases: List[Dict[str, Any]],
        meta_learning_trial_id: Optional[int] = None
    ) -> ExperimentRun:
        """
        Create new experiment

        Args:
            name: Experiment name
            description: Description
            experiment_type: Type of experiment
            parameter_dimensions: Multi-dimensional parameter space
            statistical_methods: List of statistical methods to apply
            phases: List of phase configurations
            meta_learning_trial_id: Optional link to meta-learning trial

        Returns:
            Created ExperimentRun
        """
        # Generate parameter values
        param_grid = ParameterGrid(parameter_dimensions)
        parameter_values = param_grid.generate_grid(method='grid')

        experiment = ExperimentRun(
            name=name,
            description=description,
            experiment_type=experiment_type,
            parameter_dimensions=parameter_dimensions,
            parameter_values=parameter_values,
            statistical_methods=statistical_methods,
            phases=phases,
            current_phase=0,
            status='created',
            meta_learning_trial_id=meta_learning_trial_id
        )

        self.db.add(experiment)
        self.db.commit()
        self.db.refresh(experiment)

        logger.info(f"Created experiment: {experiment.id} - {name}")
        logger.info(f"  Parameter grid size: {len(parameter_values)}")
        logger.info(f"  Phases: {len(phases)}")

        return experiment

    async def run_experiment(
        self,
        experiment_id: int,
        max_iterations_per_phase: int = 100
    ) -> ExperimentRun:
        """
        Execute multi-phase experiment

        Args:
            experiment_id: Experiment ID
            max_iterations_per_phase: Max iterations per phase

        Returns:
            Completed experiment
        """
        experiment = self.db.query(ExperimentRun).filter(
            ExperimentRun.id == experiment_id
        ).first()

        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        if experiment.status == 'completed':
            raise ValueError(f"Experiment {experiment_id} already completed")

        # Update status
        experiment.status = 'running'
        experiment.started_at = datetime.utcnow()
        self.db.commit()

        all_results = []

        # Execute each phase
        for phase_idx, phase_config in enumerate(experiment.phases):
            logger.info(f"Experiment {experiment_id} - Starting phase {phase_idx + 1}/{len(experiment.phases)}")

            experiment.current_phase = phase_idx
            self.db.commit()

            # Create phase
            phase = ExperimentPhase(
                name=phase_config.get('name', f'Phase {phase_idx + 1}'),
                algorithm=phase_config['algorithm'],
                parameter_space=phase_config.get('parameter_space', experiment.parameter_dimensions),
                metric_weights=phase_config.get('metric_weights'),
                transition_criteria=phase_config.get('transition_criteria'),
                statistical_method=phase_config.get('statistical_method', 'bayesian')
            )

            # Run phase
            phase_results = await self._run_phase(
                experiment=experiment,
                phase=phase,
                max_iterations=max_iterations_per_phase
            )

            all_results.extend(phase_results)

            # Check if should transition
            if not phase.evaluate_transition() and phase_idx < len(experiment.phases) - 1:
                logger.warning(f"Phase {phase_idx + 1} did not meet transition criteria")

        # Analyze results
        evaluation_metrics = await self._analyze_results(
            experiment=experiment,
            results=all_results
        )

        # Update experiment
        experiment.results = all_results
        experiment.evaluation_metrics = evaluation_metrics
        experiment.status = 'completed'
        experiment.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(experiment)

        logger.info(f"Experiment {experiment_id} completed with {len(all_results)} total iterations")

        return experiment

    async def _run_phase(
        self,
        experiment: ExperimentRun,
        phase: ExperimentPhase,
        max_iterations: int
    ) -> List[Dict[str, Any]]:
        """
        Execute single phase of experiment

        Returns:
            List of iteration results
        """
        param_grid = ParameterGrid(phase.parameter_space)
        param_combinations = param_grid.generate_grid(method='grid')

        # Limit combinations if too many
        if len(param_combinations) > max_iterations:
            logger.info(f"  Grid size {len(param_combinations)} exceeds max {max_iterations}, using random sampling")
            param_combinations = param_grid.generate_grid(method='random')[:max_iterations]

        results = []

        for iteration_idx, params in enumerate(param_combinations):
            logger.debug(f"  Phase {phase.name} - Iteration {iteration_idx + 1}/{len(param_combinations)}")

            # Execute iteration
            metrics = await self._execute_iteration(
                algorithm=phase.algorithm,
                parameters=params,
                experiment_type=experiment.experiment_type
            )

            # Calculate score
            score = phase.calculate_weighted_score(metrics)

            # Statistical analysis
            statistical_results = {}
            for method in experiment.statistical_methods:
                if method == 'bayesian' and len(results) > 0:
                    observations = [r['score'] for r in results] + [score]
                    statistical_results['bayesian'] = self.statistical_inference.bayesian_inference(
                        observations=observations
                    )
                elif method == 'frequentist' and len(results) > 1:
                    observations = [r['score'] for r in results] + [score]
                    statistical_results['frequentist'] = self.statistical_inference.frequentist_inference(
                        observations=observations
                    )
                elif method == 'bootstrap' and len(results) > 4:
                    observations = [r['score'] for r in results] + [score]
                    statistical_results['bootstrap'] = self.statistical_inference.bootstrap_inference(
                        observations=observations,
                        n_bootstrap=100
                    )

            result = {
                'iteration': iteration_idx,
                'phase': phase.name,
                'algorithm': phase.algorithm,
                'parameters': params,
                'metrics': metrics,
                'score': score,
                'statistical_analysis': statistical_results
            }

            results.append(result)
            phase.results.append(result)

            # Check early stopping
            if phase.evaluate_transition():
                logger.info(f"  Phase {phase.name} met transition criteria at iteration {iteration_idx + 1}")
                break

        return results

    async def _execute_iteration(
        self,
        algorithm: str,
        parameters: Dict[str, Any],
        experiment_type: str
    ) -> Dict[str, float]:
        """
        Execute single iteration with algorithm and parameters

        Returns:
            Dictionary of metrics
        """
        # Simulate algorithm execution
        # In production, this would call actual algorithms

        if experiment_type == 'compression':
            compression_ratio = np.random.uniform(1.5, 3.0) * parameters.get('quality', 0.7)
            processing_time = np.random.uniform(0.5, 2.0) / parameters.get('speed', 1.0)
            quality = parameters.get('quality', 0.7) * np.random.uniform(0.8, 1.0)

            return {
                'compression_ratio': compression_ratio,
                'processing_time': processing_time,
                'quality_score': quality,
                'throughput': 1.0 / processing_time if processing_time > 0 else 0.0
            }

        elif experiment_type == 'meta_learning':
            # Link to meta-learning trial
            accuracy = np.random.uniform(0.7, 0.95) * parameters.get('complexity', 0.8)
            convergence = np.random.uniform(10, 50) / parameters.get('learning_rate', 0.01)

            return {
                'accuracy': accuracy,
                'convergence_iterations': convergence,
                'final_score': accuracy * 0.9
            }

        else:
            # Generic metrics
            return {
                'metric_1': np.random.uniform(0.5, 1.0),
                'metric_2': np.random.uniform(0.5, 1.0),
                'metric_3': np.random.uniform(0.5, 1.0)
            }

    async def _analyze_results(
        self,
        experiment: ExperimentRun,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of experiment results

        Returns:
            Dictionary of evaluation metrics
        """
        if not results:
            return {}

        # Extract scores
        scores = [r['score'] for r in results]

        # Basic statistics
        analysis = {
            'total_iterations': len(results),
            'mean_score': float(np.mean(scores)),
            'median_score': float(np.median(scores)),
            'std_score': float(np.std(scores)),
            'min_score': float(np.min(scores)),
            'max_score': float(np.max(scores)),
            'best_iteration': int(np.argmax(scores)),
            'best_parameters': results[int(np.argmax(scores))]['parameters']
        }

        # Phase-wise analysis
        phases = {}
        for result in results:
            phase_name = result.get('phase', 'unknown')
            if phase_name not in phases:
                phases[phase_name] = []
            phases[phase_name].append(result['score'])

        phase_analysis = {}
        for phase_name, phase_scores in phases.items():
            phase_analysis[phase_name] = {
                'mean': float(np.mean(phase_scores)),
                'std': float(np.std(phase_scores)),
                'n_iterations': len(phase_scores),
                'improvement': float(phase_scores[-1] - phase_scores[0]) if len(phase_scores) > 1 else 0.0
            }

        analysis['phases'] = phase_analysis

        # Statistical inference across methods
        statistical_summary = {}
        for method in experiment.statistical_methods:
            if method == 'bayesian':
                statistical_summary['bayesian'] = self.statistical_inference.bayesian_inference(scores)
            elif method == 'frequentist':
                statistical_summary['frequentist'] = self.statistical_inference.frequentist_inference(scores)
            elif method == 'bootstrap':
                statistical_summary['bootstrap'] = self.statistical_inference.bootstrap_inference(
                    scores,
                    n_bootstrap=1000
                )

        analysis['statistical_summary'] = statistical_summary

        # Algorithm comparison (if multiple algorithms used)
        algorithms = {}
        for result in results:
            algo = result.get('algorithm', 'unknown')
            if algo not in algorithms:
                algorithms[algo] = []
            algorithms[algo].append(result['score'])

        if len(algorithms) > 1:
            analysis['algorithm_comparison'] = self.statistical_inference.confidence_interval_comparison(algorithms)

        # Convergence analysis
        if len(scores) > 10:
            # Check if experiment converged
            recent_scores = scores[-10:]
            score_variance = np.var(recent_scores)
            analysis['converged'] = score_variance < 0.01
            analysis['convergence_variance'] = float(score_variance)

        return analysis

    async def add_phase(
        self,
        experiment_id: int,
        phase_config: Dict[str, Any]
    ) -> ExperimentRun:
        """
        Add new phase to existing experiment

        Args:
            experiment_id: Experiment ID
            phase_config: Phase configuration dictionary

        Returns:
            Updated experiment
        """
        experiment = self.db.query(ExperimentRun).filter(
            ExperimentRun.id == experiment_id
        ).first()

        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        if experiment.status == 'running':
            raise ValueError(f"Cannot add phase to running experiment")

        # Add phase
        phases = experiment.phases or []
        phases.append(phase_config)
        experiment.phases = phases

        self.db.commit()
        self.db.refresh(experiment)

        logger.info(f"Added phase to experiment {experiment_id}: {phase_config.get('name', 'unnamed')}")

        return experiment

    async def get_experiment_results(
        self,
        experiment_id: int
    ) -> Dict[str, Any]:
        """
        Get experiment results and analysis

        Returns:
            Dictionary with results and evaluation metrics
        """
        experiment = self.db.query(ExperimentRun).filter(
            ExperimentRun.id == experiment_id
        ).first()

        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        return {
            'id': experiment.id,
            'name': experiment.name,
            'status': experiment.status,
            'experiment_type': experiment.experiment_type,
            'phases': experiment.phases,
            'current_phase': experiment.current_phase,
            'results': experiment.results,
            'evaluation_metrics': experiment.evaluation_metrics,
            'created_at': experiment.created_at.isoformat() if experiment.created_at else None,
            'started_at': experiment.started_at.isoformat() if experiment.started_at else None,
            'completed_at': experiment.completed_at.isoformat() if experiment.completed_at else None
        }
