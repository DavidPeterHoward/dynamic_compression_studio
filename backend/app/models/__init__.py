"""
Models package for Dynamic Compression Algorithms backend.
"""

# Import all models to ensure they are registered with SQLAlchemy
from .experiment import *
from .synthetic_media import *
from .compression import *
from .file import *
from .prompts import *
from .compression_validation import *

# Core database models
from .compression_algorithms import CompressionAlgorithm
from .compression_requests import CompressionRequest
from .system_metrics import SystemMetrics

__all__ = [
    # Core database models
    "CompressionAlgorithm", "CompressionRequest", "SystemMetrics",

    # Experiment models
    "Experiment", "CompressionProgress", "GenerativeContent", "ExperimentLogCreate",

    # Synthetic media models
    "SyntheticMedia", "SyntheticMediaGeneration", "SyntheticMediaCompression",
    "SyntheticDataBatch", "SyntheticDataSchema", "SyntheticDataExperiment",
    "MediaType", "GenerationStatus",

    # Compression models
    "CompressionLevel", "ContentType", "CompressionParameters",
    "CompressionResult", "CompressionResponse", "CompressionComparison",

    # File models
    "FileUpload", "FileMetadata",

    # Prompt models
    "Prompt", "PromptTemplate", "PromptWorkflow", "PromptEvaluation", "PromptWorkflowExecution",
    "PromptChain", "PromptSemanticAnalysis", "PromptUsage", "PromptOptimization",
    "PromptWorkflowAssociation", "PromptType", "PromptCategory", "EvaluationStatus",

    # Compression validation models
    "CompressionTestResult", "ContentSample", "DimensionalMetric", "AlgorithmPerformanceBaseline",
    "DataIntegrityCheck", "ContentCategory", "DataOrigin", "ValidationStatus",
    "ContentCharacteristics", "CompressionMetrics", "ValidationResult", "ComprehensiveTestRecord"
]