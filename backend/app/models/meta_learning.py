"""
Meta-Learning Models
Tracks algorithm performance, parameter optimization, and recursive self-improvement
"""

from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class MetaLearningTrial(Base):
    """Meta-learning trial with recursive improvement tracking"""
    __tablename__ = "meta_learning_trials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Trial configuration
    algorithm_family = Column(String(100), nullable=False)  # 'compression', 'prediction', 'optimization'
    target_metric = Column(String(100), nullable=False)  # 'compression_ratio', 'throughput', 'quality'

    # Meta-learning parameters
    learning_rate = Column(Float, default=0.01)
    iteration_count = Column(Integer, default=0)
    max_iterations = Column(Integer, default=100)
    convergence_threshold = Column(Float, default=0.001)

    # Multi-dimensional parameter space
    parameter_space = Column(JSON, nullable=False)  # Define search space
    current_parameters = Column(JSON, nullable=False)  # Current best parameters

    # Statistical inference configuration
    inference_method = Column(String(50), default='bayesian')  # bayesian, frequentist, bootstrap
    confidence_level = Column(Float, default=0.95)

    # Performance tracking
    best_score = Column(Float, nullable=True)
    current_score = Column(Float, nullable=True)
    improvement_rate = Column(Float, nullable=True)

    # Recursive self-improvement
    parent_trial_id = Column(Integer, ForeignKey('meta_learning_trials.id'), nullable=True)
    recursion_depth = Column(Integer, default=0)
    self_modification_enabled = Column(Boolean, default=False)

    # Status
    status = Column(String(50), default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    iterations = relationship("MetaLearningIteration", back_populates="trial", cascade="all, delete-orphan")
    child_trials = relationship("MetaLearningTrial", remote_side=[id])

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MetaLearningIteration(Base):
    """Individual iteration within a meta-learning trial"""
    __tablename__ = "meta_learning_iterations"

    id = Column(Integer, primary_key=True, index=True)
    trial_id = Column(Integer, ForeignKey('meta_learning_trials.id'), nullable=False)
    iteration_number = Column(Integer, nullable=False)

    # Parameters tested in this iteration
    parameters = Column(JSON, nullable=False)

    # Metrics collected
    metrics = Column(JSON, nullable=False)

    # Primary performance score
    score = Column(Float, nullable=False)

    # Statistical analysis
    confidence_interval = Column(JSON, nullable=True)  # [lower, upper]
    statistical_significance = Column(Float, nullable=True)  # p-value

    # Synthetic data used (if any)
    synthetic_data_config = Column(JSON, nullable=True)

    # Phase information
    phase = Column(String(50), nullable=True)  # exploration, exploitation, refinement

    # Execution details
    duration_seconds = Column(Float, nullable=False)
    throughput = Column(Float, nullable=True)  # operations per second

    # Relationships
    trial = relationship("MetaLearningTrial", back_populates="iterations")

    created_at = Column(DateTime, default=datetime.utcnow)


class AlgorithmPerformance(Base):
    """Aggregated algorithm performance across all trials"""
    __tablename__ = "algorithm_performance"

    id = Column(Integer, primary_key=True, index=True)
    algorithm_name = Column(String(100), nullable=False, unique=True, index=True)
    algorithm_family = Column(String(100), nullable=False)

    # Performance statistics
    total_trials = Column(Integer, default=0)
    successful_trials = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    best_score = Column(Float, nullable=True)
    worst_score = Column(Float, nullable=True)

    # Best known parameters
    best_parameters = Column(JSON, nullable=True)

    # Meta-statistics
    average_convergence_iterations = Column(Float, nullable=True)
    average_throughput = Column(Float, nullable=True)
    reliability_score = Column(Float, nullable=True)  # 0-1

    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    times_selected = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExperimentRun(Base):
    """Enhanced experiment with multi-dimensional parameters"""
    __tablename__ = "experiment_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Experiment type
    experiment_type = Column(String(100), nullable=False)  # compression, meta_learning, hybrid

    # Multi-dimensional parameter configuration
    parameter_dimensions = Column(JSON, nullable=False)  # List of parameter dimensions
    parameter_values = Column(JSON, nullable=False)  # Actual values for each dimension

    # Statistical methods
    statistical_methods = Column(JSON, nullable=False)  # List of methods to apply

    # Multi-phase configuration
    phases = Column(JSON, nullable=False)  # List of phases with algorithms
    current_phase = Column(Integer, default=0)

    # Results
    results = Column(JSON, nullable=True)
    evaluation_metrics = Column(JSON, nullable=True)

    # Meta-learning integration
    meta_learning_trial_id = Column(Integer, ForeignKey('meta_learning_trials.id'), nullable=True)

    # Status
    status = Column(String(50), default='pending')
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
