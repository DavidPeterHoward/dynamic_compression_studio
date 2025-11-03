"""
API Endpoints for Algorithm Documentation and Performance Data

Provides endpoints to retrieve detailed information about compression algorithms,
including their mechanisms, performance characteristics, and usage guidelines.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/algorithms", tags=["Algorithm Documentation"])


class AlgorithmInfo(BaseModel):
    """Detailed algorithm information."""
    name: str
    display_name: str
    category: str
    description: str
    detailed_description: str
    mechanism: List[str]
    mathematical_foundation: List[str]
    advantages: List[str]
    disadvantages: List[str]
    use_cases: List[str]
    complexity: Dict[str, str]
    performance: Dict[str, str]
    parameters: List[Dict[str, Any]]
    references: List[str]


class AlgorithmListResponse(BaseModel):
    """List of available algorithms with basic info."""
    algorithms: List[Dict[str, str]]
    total: int


# Algorithm documentation database
ALGORITHM_DOCS: Dict[str, Dict[str, Any]] = {
    "quantum_biological": {
        "name": "quantum_biological",
        "display_name": "Quantum-Biological Compression",
        "category": "experimental",
        "description": "Combines quantum computing principles with biological evolution for compression",
        "detailed_description": "An experimental algorithm that merges quantum superposition, Grover's search algorithm, genetic optimization, and DNA-inspired encoding to achieve novel compression patterns.",
        "mechanism": [
            "Quantum Superposition: Patterns exist in superposition states |ψ⟩ = Σ αᵢ|pᵢ⟩",
            "Grover's Algorithm: O(√N) pattern search using amplitude amplification",
            "Quantum Gates: Hadamard, Oracle, and Diffusion operations",
            "DNA Encoding: Binary to quaternary (A,T,G,C) mapping with error correction",
            "Genetic Evolution: Tournament selection, crossover, and mutation",
            "Quantum Entanglement: Correlated pattern detection using Bell states",
        ],
        "mathematical_foundation": [
            "Quantum State: |ψ⟩ = Σ αᵢ|pᵢ⟩ where Σ|αᵢ|² = 1",
            "Grover Operator: G = (2|ψ⟩⟨ψ| - I)(I - 2|target⟩⟨target|)",
            "DNA Encoding: 00→A, 01→T, 10→G, 11→C",
            "Fitness Function: f(x) = compression_ratio(x) × speed(x) / memory(x)",
            "Entanglement Measure: E = |⟨ψ₁|ψ₂⟩|²",
        ],
        "advantages": [
            "Quantum speedup: O(√N) vs O(N) classical search",
            "Parallel pattern evaluation through superposition",
            "Adaptive parameter optimization via genetic algorithms",
            "Natural error correction through DNA encoding",
        ],
        "disadvantages": [
            "Slower than traditional algorithms",
            "Higher memory requirements",
            "Limited practical compression gains",
            "Not suitable for real-time applications",
        ],
        "use_cases": [
            "Research and experimental compression",
            "Biological sequence data",
            "Pattern-rich data with complex correlations",
        ],
        "complexity": {
            "time": "O(√N × G) where N=data size, G=generations",
            "space": "O(2^Q + P) where Q=qubits, P=population size"
        },
        "performance": {
            "speed": "Slow (experimental)",
            "compression_ratio": "1.5x - 3x",
            "memory_usage": "High (100+ MB)"
        },
        "parameters": [
            {"name": "quantum_qubits", "type": "int", "default": 8, "range": "4-12", "description": "Number of simulated quantum qubits"},
            {"name": "population_size", "type": "int", "default": 50, "range": "20-200", "description": "Genetic population size"},
            {"name": "grover_iterations", "type": "int", "default": 3, "range": "1-10", "description": "Grover algorithm iterations"},
        ],
        "references": [
            "Nielsen & Chuang (2010). Quantum Computation and Quantum Information",
            "Grover (1996). A Fast Quantum Mechanical Algorithm for Database Search",
            "Adleman (1994). Molecular Computation of Solutions to Combinatorial Problems",
        ]
    },
    "neuromorphic": {
        "name": "neuromorphic",
        "display_name": "Neuromorphic Compression",
        "category": "experimental",
        "description": "Brain-inspired compression using spiking neural networks",
        "detailed_description": "A neuromorphic algorithm that mimics biological neural processing using spiking neural networks with spike-timing dependent plasticity (STDP).",
        "mechanism": [
            "Spiking Neurons: Leaky integrate-and-fire (LIF) model",
            "Temporal Coding: Information in precise spike timing",
            "Rate Coding: Information in neuron firing frequency",
            "Population Coding: Distributed representation",
            "STDP Learning: Hebbian learning with spike timing",
        ],
        "mathematical_foundation": [
            "Membrane Potential: τ dV/dt = -(V - V_rest) + R × I(t)",
            "Spike Threshold: S(t) = 1 if V(t) > θ",
            "STDP Rule: Δw = A⁺e^(-Δt/τ⁺) or -A⁻e^(Δt/τ⁻)",
            "Neural Entropy: H = -Σ p(spike) log₂ p(spike)",
        ],
        "advantages": [
            "Energy efficient processing",
            "Temporal dynamics capture",
            "Continuous learning through STDP",
            "Noise tolerance",
        ],
        "disadvantages": [
            "Slow processing",
            "High memory usage",
            "Requires training",
            "Non-deterministic",
        ],
        "use_cases": [
            "Temporal sequence data",
            "Pattern recognition in noisy data",
            "Adaptive compression",
        ],
        "complexity": {
            "time": "O(N × M × T) where N=neurons, M=synapses, T=time",
            "space": "O(N²) for connections"
        },
        "performance": {
            "speed": "Slow (neural simulation)",
            "compression_ratio": "1.2x - 2.5x",
            "memory_usage": "High (50+ MB)"
        },
        "parameters": [
            {"name": "num_neurons", "type": "int", "default": 100, "range": "50-500", "description": "Number of neurons"},
            {"name": "network_layers", "type": "int", "default": 3, "range": "1-5", "description": "Network depth"},
            {"name": "stdp_learning_rate", "type": "float", "default": 0.01, "range": "0.001-0.1", "description": "STDP rate"},
        ],
        "references": [
            "Maass (1997). Networks of Spiking Neurons",
            "Gerstner & Kistler (2002). Spiking Neuron Models",
            "Izhikevich (2003). Simple Model of Spiking Neurons",
        ]
    },
    "topological": {
        "name": "topological",
        "display_name": "Topological Compression",
        "category": "experimental",
        "description": "Compression using topological data analysis and persistent homology",
        "detailed_description": "An algorithm leveraging topological data analysis to identify and compress data based on its intrinsic geometric structure.",
        "mechanism": [
            "Point Cloud Representation: Data embedded in metric space",
            "Vietoris-Rips Complex: Simplicial complex construction",
            "Persistent Homology: Topological feature detection",
            "Barcode Encoding: Compressed representation",
        ],
        "mathematical_foundation": [
            "Persistent Homology: H_k(X) = Z_k(X) / B_k(X)",
            "Vietoris-Rips: VR(X, ε) = {σ ⊆ X | diam(σ) ≤ ε}",
            "Boundary Operator: ∂: C_{k+1} → C_k",
            "Betti Numbers: β_k = rank(H_k)",
        ],
        "advantages": [
            "Captures global structure",
            "Multi-scale analysis",
            "Robust to noise",
            "Coordinate-free",
        ],
        "disadvantages": [
            "Very slow computation",
            "Extremely high memory",
            "Limited on non-geometric data",
            "Not real-time",
        ],
        "use_cases": [
            "Geometric data compression",
            "Point cloud data",
            "Network data",
            "Scientific data analysis",
        ],
        "complexity": {
            "time": "O(n³) for VR complex",
            "space": "O(n²) for storage"
        },
        "performance": {
            "speed": "Very slow",
            "compression_ratio": "1.1x - 2x",
            "memory_usage": "Very high (500+ MB)"
        },
        "parameters": [
            {"name": "max_dimension", "type": "int", "default": 3, "range": "1-4", "description": "Maximum homology dimension"},
            {"name": "persistence_threshold", "type": "float", "default": 0.01, "range": "0.001-0.1", "description": "Minimum persistence"},
        ],
        "references": [
            "Edelsbrunner & Harer (2010). Computational Topology",
            "Zomorodian & Carlsson (2005). Computing Persistent Homology",
            "Chazal & Michel (2021). Introduction to Topological Data Analysis",
        ]
    }
}


@router.get("/list", response_model=AlgorithmListResponse)
async def list_algorithms():
    """
    Get list of all available compression algorithms.
    
    Returns basic information about each algorithm including:
    - Name and display name
    - Category (traditional, advanced, experimental)
    - Short description
    """
    algorithms = []
    for algo_name, algo_info in ALGORITHM_DOCS.items():
        algorithms.append({
            "name": algo_info["name"],
            "display_name": algo_info["display_name"],
            "category": algo_info["category"],
            "description": algo_info["description"]
        })
    
    return AlgorithmListResponse(
        algorithms=algorithms,
        total=len(algorithms)
    )


@router.get("/info/{algorithm_name}", response_model=AlgorithmInfo)
async def get_algorithm_info(algorithm_name: str):
    """
    Get detailed information about a specific algorithm.
    
    Args:
        algorithm_name: Name of the algorithm (e.g., 'quantum_biological')
    
    Returns:
        Comprehensive algorithm documentation including:
        - Detailed mechanism of action
        - Mathematical foundations
        - Performance characteristics
        - Use cases and examples
        - Configuration parameters
        - Academic references
    
    Raises:
        HTTPException: 404 if algorithm not found
    """
    if algorithm_name not in ALGORITHM_DOCS:
        raise HTTPException(
            status_code=404,
            detail=f"Algorithm '{algorithm_name}' not found. Available algorithms: {', '.join(ALGORITHM_DOCS.keys())}"
        )
    
    algo_data = ALGORITHM_DOCS[algorithm_name]
    return AlgorithmInfo(**algo_data)


@router.get("/compare")
async def compare_algorithms(
    algorithms: Optional[str] = None
) -> JSONResponse:
    """
    Compare multiple algorithms side by side.
    
    Args:
        algorithms: Comma-separated list of algorithm names
                   (e.g., 'quantum_biological,neuromorphic')
    
    Returns:
        Comparison matrix of algorithms including:
        - Performance characteristics
        - Complexity analysis
        - Feature comparison
    """
    if not algorithms:
        algo_names = list(ALGORITHM_DOCS.keys())
    else:
        algo_names = [a.strip() for a in algorithms.split(',')]
    
    comparison = {
        "algorithms": algo_names,
        "comparison_matrix": {}
    }
    
    # Build comparison matrix
    for feature in ["speed", "compression_ratio", "memory_usage"]:
        comparison["comparison_matrix"][feature] = {}
        for algo_name in algo_names:
            if algo_name in ALGORITHM_DOCS:
                comparison["comparison_matrix"][feature][algo_name] = (
                    ALGORITHM_DOCS[algo_name]["performance"].get(feature, "N/A")
                )
    
    return JSONResponse(content=comparison)


@router.get("/performance/{algorithm_name}")
async def get_algorithm_performance(algorithm_name: str) -> JSONResponse:
    """
    Get performance metrics and benchmarks for an algorithm.
    
    Args:
        algorithm_name: Name of the algorithm
    
    Returns:
        Performance data including:
        - Speed metrics
        - Compression ratios
        - Memory usage
        - Complexity analysis
    """
    if algorithm_name not in ALGORITHM_DOCS:
        raise HTTPException(
            status_code=404,
            detail=f"Algorithm '{algorithm_name}' not found"
        )
    
    algo_data = ALGORITHM_DOCS[algorithm_name]
    
    return JSONResponse(content={
        "algorithm": algorithm_name,
        "performance": algo_data["performance"],
        "complexity": algo_data["complexity"],
        "category": algo_data["category"]
    })


