"""
Statistical Inference Module
Implements Bayesian, Frequentist, and Bootstrap methods for statistical analysis
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from scipy import stats
from scipy.stats import norm, t as t_dist
import logging

logger = logging.getLogger(__name__)


class StatisticalInference:
    """
    Comprehensive statistical inference methods for meta-learning
    """

    @staticmethod
    def bayesian_inference(
        observations: List[float],
        prior_mean: float = 0.0,
        prior_std: float = 1.0,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Bayesian inference with conjugate priors (Normal-Normal model)

        Args:
            observations: List of observed values
            prior_mean: Prior mean
            prior_std: Prior standard deviation
            confidence_level: Credible interval confidence level

        Returns:
            Dictionary with posterior statistics
        """
        if not observations:
            return {
                'posterior_mean': prior_mean,
                'posterior_std': prior_std,
                'credible_interval': (prior_mean - 2 * prior_std, prior_mean + 2 * prior_std),
                'n_observations': 0
            }

        observations = np.array(observations)
        n = len(observations)
        data_mean = np.mean(observations)
        data_std = np.std(observations, ddof=1) if n > 1 else prior_std

        # Bayesian update (conjugate Normal-Normal)
        prior_precision = 1.0 / (prior_std ** 2)
        data_precision = n / (data_std ** 2) if data_std > 0 else 1.0

        posterior_precision = prior_precision + data_precision
        posterior_std = np.sqrt(1.0 / posterior_precision)

        posterior_mean = (
            prior_precision * prior_mean + data_precision * data_mean
        ) / posterior_precision

        # Credible interval
        z_score = norm.ppf((1 + confidence_level) / 2)
        credible_interval = (
            posterior_mean - z_score * posterior_std,
            posterior_mean + z_score * posterior_std
        )

        return {
            'posterior_mean': float(posterior_mean),
            'posterior_std': float(posterior_std),
            'credible_interval': (float(credible_interval[0]), float(credible_interval[1])),
            'prior_mean': prior_mean,
            'prior_std': prior_std,
            'data_mean': float(data_mean),
            'data_std': float(data_std),
            'n_observations': n
        }

    @staticmethod
    def frequentist_inference(
        observations: List[float],
        confidence_level: float = 0.95,
        null_hypothesis_mean: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Frequentist inference with t-test and confidence intervals

        Args:
            observations: List of observed values
            confidence_level: Confidence interval level
            null_hypothesis_mean: Mean to test against (for hypothesis testing)

        Returns:
            Dictionary with frequentist statistics
        """
        if len(observations) < 2:
            return {
                'mean': observations[0] if observations else 0.0,
                'std': 0.0,
                'confidence_interval': (0.0, 0.0),
                'n_observations': len(observations),
                'p_value': None,
                't_statistic': None
            }

        observations = np.array(observations)
        n = len(observations)
        mean = np.mean(observations)
        std = np.std(observations, ddof=1)
        se = std / np.sqrt(n)

        # Confidence interval using t-distribution
        df = n - 1
        t_critical = t_dist.ppf((1 + confidence_level) / 2, df)
        confidence_interval = (
            mean - t_critical * se,
            mean + t_critical * se
        )

        # Hypothesis test (if null hypothesis provided)
        t_statistic = None
        p_value = None
        if null_hypothesis_mean is not None:
            t_statistic = (mean - null_hypothesis_mean) / se if se > 0 else 0.0
            p_value = 2 * (1 - t_dist.cdf(abs(t_statistic), df))

        return {
            'mean': float(mean),
            'std': float(std),
            'standard_error': float(se),
            'confidence_interval': (float(confidence_interval[0]), float(confidence_interval[1])),
            'n_observations': n,
            'degrees_of_freedom': df,
            't_statistic': float(t_statistic) if t_statistic is not None else None,
            'p_value': float(p_value) if p_value is not None else None
        }

    @staticmethod
    def bootstrap_inference(
        observations: List[float],
        n_bootstrap: int = 1000,
        confidence_level: float = 0.95,
        statistic_fn: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Bootstrap resampling for confidence intervals

        Args:
            observations: List of observed values
            n_bootstrap: Number of bootstrap samples
            confidence_level: Confidence interval level
            statistic_fn: Function to compute statistic (default: mean)

        Returns:
            Dictionary with bootstrap statistics
        """
        if not observations:
            return {
                'estimate': 0.0,
                'bootstrap_mean': 0.0,
                'bootstrap_std': 0.0,
                'confidence_interval': (0.0, 0.0),
                'n_observations': 0,
                'n_bootstrap': n_bootstrap
            }

        if statistic_fn is None:
            statistic_fn = np.mean

        observations = np.array(observations)
        n = len(observations)

        # Original estimate
        original_estimate = statistic_fn(observations)

        # Bootstrap resampling
        bootstrap_estimates = []
        for _ in range(n_bootstrap):
            # Resample with replacement
            bootstrap_sample = np.random.choice(observations, size=n, replace=True)
            bootstrap_estimates.append(statistic_fn(bootstrap_sample))

        bootstrap_estimates = np.array(bootstrap_estimates)

        # Bootstrap statistics
        bootstrap_mean = np.mean(bootstrap_estimates)
        bootstrap_std = np.std(bootstrap_estimates)

        # Percentile confidence interval
        alpha = 1 - confidence_level
        lower_percentile = 100 * alpha / 2
        upper_percentile = 100 * (1 - alpha / 2)

        confidence_interval = (
            np.percentile(bootstrap_estimates, lower_percentile),
            np.percentile(bootstrap_estimates, upper_percentile)
        )

        return {
            'estimate': float(original_estimate),
            'bootstrap_mean': float(bootstrap_mean),
            'bootstrap_std': float(bootstrap_std),
            'confidence_interval': (float(confidence_interval[0]), float(confidence_interval[1])),
            'n_observations': n,
            'n_bootstrap': n_bootstrap,
            'bootstrap_distribution': bootstrap_estimates.tolist()[:100]  # First 100 samples
        }

    @staticmethod
    def monte_carlo_simulation(
        model_fn: callable,
        parameter_distributions: Dict[str, Tuple[str, Any]],
        n_simulations: int = 1000
    ) -> Dict[str, Any]:
        """
        Monte Carlo simulation for uncertainty propagation

        Args:
            model_fn: Function that takes parameters and returns result
            parameter_distributions: Dict of {param_name: (distribution_type, params)}
                Example: {'learning_rate': ('uniform', (0.001, 0.1))}
            n_simulations: Number of simulations

        Returns:
            Dictionary with simulation results
        """
        results = []

        for _ in range(n_simulations):
            # Sample parameters from distributions
            params = {}
            for param_name, (dist_type, dist_params) in parameter_distributions.items():
                if dist_type == 'uniform':
                    params[param_name] = np.random.uniform(*dist_params)
                elif dist_type == 'normal':
                    params[param_name] = np.random.normal(*dist_params)
                elif dist_type == 'lognormal':
                    params[param_name] = np.random.lognormal(*dist_params)
                else:
                    raise ValueError(f"Unknown distribution type: {dist_type}")

            # Run model
            try:
                result = model_fn(**params)
                results.append(result)
            except Exception as e:
                logger.warning(f"Monte Carlo simulation error: {e}")
                continue

        if not results:
            return {
                'mean': 0.0,
                'std': 0.0,
                'confidence_interval_95': (0.0, 0.0),
                'n_simulations': 0
            }

        results = np.array(results)

        return {
            'mean': float(np.mean(results)),
            'median': float(np.median(results)),
            'std': float(np.std(results)),
            'min': float(np.min(results)),
            'max': float(np.max(results)),
            'confidence_interval_95': (
                float(np.percentile(results, 2.5)),
                float(np.percentile(results, 97.5))
            ),
            'confidence_interval_99': (
                float(np.percentile(results, 0.5)),
                float(np.percentile(results, 99.5))
            ),
            'n_simulations': len(results),
            'percentile_25': float(np.percentile(results, 25)),
            'percentile_75': float(np.percentile(results, 75))
        }

    @staticmethod
    def cross_validation_scores(
        data: List[float],
        n_folds: int = 5,
        model_fn: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        K-fold cross-validation for model evaluation

        Args:
            data: List of data points
            n_folds: Number of folds
            model_fn: Function to evaluate (default: mean prediction)

        Returns:
            Dictionary with cross-validation scores
        """
        if len(data) < n_folds:
            return {
                'mean_score': 0.0,
                'std_score': 0.0,
                'scores': [],
                'n_folds': n_folds
            }

        data = np.array(data)
        fold_size = len(data) // n_folds
        scores = []

        for fold in range(n_folds):
            # Split data
            start_idx = fold * fold_size
            end_idx = start_idx + fold_size if fold < n_folds - 1 else len(data)

            test_data = data[start_idx:end_idx]
            train_data = np.concatenate([data[:start_idx], data[end_idx:]])

            # Train and evaluate
            if model_fn is None:
                # Simple mean prediction
                prediction = np.mean(train_data)
                score = -np.mean((test_data - prediction) ** 2)  # Negative MSE
            else:
                score = model_fn(train_data, test_data)

            scores.append(score)

        scores = np.array(scores)

        return {
            'mean_score': float(np.mean(scores)),
            'std_score': float(np.std(scores)),
            'scores': scores.tolist(),
            'n_folds': n_folds,
            'best_fold': int(np.argmax(scores)),
            'worst_fold': int(np.argmin(scores))
        }

    @staticmethod
    def ab_test(
        group_a: List[float],
        group_b: List[float],
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        A/B test with t-test and effect size

        Args:
            group_a: Observations from group A (control)
            group_b: Observations from group B (treatment)
            confidence_level: Confidence level

        Returns:
            Dictionary with A/B test results
        """
        if len(group_a) < 2 or len(group_b) < 2:
            return {
                'mean_a': np.mean(group_a) if group_a else 0.0,
                'mean_b': np.mean(group_b) if group_b else 0.0,
                'p_value': None,
                'significant': False,
                'effect_size': 0.0
            }

        group_a = np.array(group_a)
        group_b = np.array(group_b)

        # Two-sample t-test
        t_statistic, p_value = stats.ttest_ind(group_a, group_b)

        # Effect size (Cohen's d)
        pooled_std = np.sqrt(
            ((len(group_a) - 1) * np.var(group_a, ddof=1) +
             (len(group_b) - 1) * np.var(group_b, ddof=1)) /
            (len(group_a) + len(group_b) - 2)
        )

        cohens_d = (np.mean(group_b) - np.mean(group_a)) / pooled_std if pooled_std > 0 else 0.0

        # Statistical significance
        alpha = 1 - confidence_level
        significant = p_value < alpha

        # Relative improvement
        mean_a = np.mean(group_a)
        mean_b = np.mean(group_b)
        relative_improvement = ((mean_b - mean_a) / mean_a * 100) if mean_a != 0 else 0.0

        return {
            'mean_a': float(mean_a),
            'mean_b': float(mean_b),
            'std_a': float(np.std(group_a, ddof=1)),
            'std_b': float(np.std(group_b, ddof=1)),
            't_statistic': float(t_statistic),
            'p_value': float(p_value),
            'significant': bool(significant),
            'effect_size_cohens_d': float(cohens_d),
            'relative_improvement_percent': float(relative_improvement),
            'confidence_level': confidence_level,
            'n_a': len(group_a),
            'n_b': len(group_b)
        }

    @staticmethod
    def hypothesis_test(
        observations: List[float],
        null_value: float,
        alternative: str = 'two-sided',
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        One-sample hypothesis test

        Args:
            observations: List of observations
            null_value: Null hypothesis value
            alternative: 'two-sided', 'greater', or 'less'
            confidence_level: Confidence level

        Returns:
            Dictionary with hypothesis test results
        """
        if len(observations) < 2:
            return {
                'test_statistic': 0.0,
                'p_value': 1.0,
                'reject_null': False,
                'alternative': alternative
            }

        observations = np.array(observations)

        # One-sample t-test
        t_statistic, p_value_two_sided = stats.ttest_1samp(observations, null_value)

        # Adjust p-value for one-sided tests
        if alternative == 'greater':
            p_value = p_value_two_sided / 2 if t_statistic > 0 else 1 - p_value_two_sided / 2
        elif alternative == 'less':
            p_value = p_value_two_sided / 2 if t_statistic < 0 else 1 - p_value_two_sided / 2
        else:  # two-sided
            p_value = p_value_two_sided

        # Decision
        alpha = 1 - confidence_level
        reject_null = p_value < alpha

        return {
            'test_statistic': float(t_statistic),
            'p_value': float(p_value),
            'reject_null': bool(reject_null),
            'significance_level': alpha,
            'confidence_level': confidence_level,
            'alternative': alternative,
            'sample_mean': float(np.mean(observations)),
            'null_value': null_value,
            'n_observations': len(observations)
        }

    @staticmethod
    def confidence_interval_comparison(
        groups: Dict[str, List[float]],
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Compare confidence intervals across multiple groups

        Args:
            groups: Dictionary of {group_name: observations}
            confidence_level: Confidence level

        Returns:
            Dictionary with comparison results
        """
        results = {}

        for group_name, observations in groups.items():
            if len(observations) < 2:
                results[group_name] = {
                    'mean': observations[0] if observations else 0.0,
                    'ci': (0.0, 0.0)
                }
                continue

            obs = np.array(observations)
            mean = np.mean(obs)
            se = np.std(obs, ddof=1) / np.sqrt(len(obs))

            # t-distribution confidence interval
            df = len(obs) - 1
            t_critical = t_dist.ppf((1 + confidence_level) / 2, df)
            ci = (mean - t_critical * se, mean + t_critical * se)

            results[group_name] = {
                'mean': float(mean),
                'std': float(np.std(obs, ddof=1)),
                'ci': (float(ci[0]), float(ci[1])),
                'n': len(obs)
            }

        # Find best group
        best_group = max(results.keys(), key=lambda k: results[k]['mean']) if results else None

        return {
            'groups': results,
            'best_group': best_group,
            'confidence_level': confidence_level
        }

    @staticmethod
    def statistical_power_analysis(
        effect_size: float,
        alpha: float = 0.05,
        power: float = 0.8,
        alternative: str = 'two-sided'
    ) -> Dict[str, Any]:
        """
        Statistical power analysis for sample size determination

        Args:
            effect_size: Expected effect size (Cohen's d)
            alpha: Significance level
            power: Desired statistical power
            alternative: 'two-sided' or 'one-sided'

        Returns:
            Dictionary with power analysis results
        """
        # Critical value for alpha
        if alternative == 'two-sided':
            z_alpha = norm.ppf(1 - alpha / 2)
        else:
            z_alpha = norm.ppf(1 - alpha)

        # Critical value for power
        z_beta = norm.ppf(power)

        # Required sample size per group (approximate formula)
        if effect_size == 0:
            n_required = float('inf')
        else:
            n_required = ((z_alpha + z_beta) / effect_size) ** 2

        return {
            'required_sample_size_per_group': int(np.ceil(n_required)) if n_required != float('inf') else None,
            'effect_size': effect_size,
            'alpha': alpha,
            'power': power,
            'alternative': alternative,
            'total_sample_size': int(np.ceil(n_required * 2)) if n_required != float('inf') else None
        }
