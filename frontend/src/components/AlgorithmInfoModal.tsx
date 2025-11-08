'use client'

import { AnimatePresence, motion } from 'framer-motion'
import { Activity, Atom, Brain, Info, Network, X } from 'lucide-react'

interface AlgorithmInfo {
  name: string
  displayName: string
  category: 'traditional' | 'advanced' | 'experimental'
  description: string
  detailedDescription: string
  mechanism: string[]
  mathematicalFoundation: string[]
  advantages: string[]
  disadvantages: string[]
  useCases: string[]
  complexity: {
    time: string
    space: string
  }
  performance: {
    speed: string
    compressionRatio: string
    memoryUsage: string
  }
  parameters: {
    name: string
    description: string
    defaultValue: string | number
    range?: string
  }[]
  references: string[]
}

interface AlgorithmInfoModalProps {
  isOpen: boolean
  onClose: () => void
  algorithm: string
}

const algorithmData: Record<string, AlgorithmInfo> = {
  quantum_biological: {
    name: 'quantum_biological',
    displayName: 'Quantum-Biological Compression',
    category: 'experimental',
    description: 'Combines quantum computing principles with biological evolution for compression',
    detailedDescription: 'An experimental algorithm that merges quantum superposition, Grover\'s search algorithm, genetic optimization, and DNA-inspired encoding to achieve novel compression patterns. This algorithm explores the intersection of quantum information theory and biological computing paradigms.',
    mechanism: [
      'Quantum Superposition: Patterns exist in superposition states |ψ⟩ = Σ αᵢ|pᵢ⟩',
      'Grover\'s Algorithm: O(√N) pattern search using amplitude amplification',
      'Quantum Gates: Hadamard, Oracle, and Diffusion operations',
      'DNA Encoding: Binary to quaternary (A,T,G,C) mapping with error correction',
      'Genetic Evolution: Tournament selection, crossover, and mutation',
      'Quantum Entanglement: Correlated pattern detection using Bell states',
      'Quantum Interference: Pattern optimization through constructive interference'
    ],
    mathematicalFoundation: [
      'Quantum State: |ψ⟩ = Σ αᵢ|pᵢ⟩ where Σ|αᵢ|² = 1',
      'Grover Operator: G = (2|ψ⟩⟨ψ| - I)(I - 2|target⟩⟨target|)',
      'DNA Encoding: 00→A, 01→T, 10→G, 11→C with GC-content balancing',
      'Fitness Function: f(x) = compression_ratio(x) × speed(x) / memory(x)',
      'Entanglement Measure: E = |⟨ψ₁|ψ₂⟩|² (quantum fidelity)',
      'Holevo Bound: χ = S(ρ) - Σ pᵢ S(ρᵢ) for quantum information',
      'Quantum Kolmogorov Complexity: K_Q(x) for compression limit'
    ],
    advantages: [
      'Quantum speedup: O(√N) vs O(N) classical search',
      'Parallel pattern evaluation through superposition',
      'Adaptive parameter optimization via genetic algorithms',
      'Natural error correction through DNA encoding',
      'Global pattern correlation via entanglement',
      'Self-improving through evolutionary pressure',
      'Novel compression patterns not accessible classically'
    ],
    disadvantages: [
      'Slower than traditional algorithms (experimental overhead)',
      'Higher memory requirements for quantum state simulation',
      'Limited practical compression gains on standard data',
      'Requires parameter tuning for optimal performance',
      'Complex decompression process',
      'Not suitable for real-time applications',
      'Limited hardware acceleration support'
    ],
    useCases: [
      'Research and experimental compression studies',
      'Exploring quantum computing applications',
      'Biological sequence data (DNA, RNA, proteins)',
      'Pattern-rich data with complex correlations',
      'Novel compression algorithm development',
      'Educational demonstrations of quantum principles'
    ],
    complexity: {
      time: 'O(√N × G) where N=data size, G=generations',
      space: 'O(2^Q + P) where Q=qubits, P=population size'
    },
    performance: {
      speed: 'Slow (experimental)',
      compressionRatio: '1.5x - 3x (data-dependent)',
      memoryUsage: 'High (100+ MB for large data)'
    },
    parameters: [
      { name: 'quantum_qubits', description: 'Number of simulated quantum qubits', defaultValue: 8, range: '4-12' },
      { name: 'population_size', description: 'Genetic algorithm population size', defaultValue: 50, range: '20-200' },
      { name: 'grover_iterations', description: 'Grover algorithm iterations', defaultValue: 3, range: '1-10' },
      { name: 'dna_encoding_enabled', description: 'Enable DNA-inspired encoding', defaultValue: 'true' },
      { name: 'entanglement_threshold', description: 'Correlation threshold for entanglement', defaultValue: 0.1, range: '0.0-1.0' }
    ],
    references: [
      'Nielsen & Chuang (2010). "Quantum Computation and Quantum Information"',
      'Grover (1996). "A Fast Quantum Mechanical Algorithm for Database Search"',
      'Adleman (1994). "Molecular Computation of Solutions to Combinatorial Problems"',
      'Holevo (1973). "Bounds for the Quantity of Information"'
    ]
  },
  neuromorphic: {
    name: 'neuromorphic',
    displayName: 'Neuromorphic Compression',
    category: 'experimental',
    description: 'Brain-inspired compression using spiking neural networks',
    detailedDescription: 'A neuromorphic algorithm that mimics biological neural processing using spiking neural networks with spike-timing dependent plasticity (STDP). Encodes data as temporal spike patterns and learns optimal representations through neural plasticity.',
    mechanism: [
      'Spiking Neurons: Leaky integrate-and-fire (LIF) and Izhikevich models',
      'Temporal Coding: Information encoded in precise spike timing',
      'Rate Coding: Information in neuron firing frequency',
      'Population Coding: Distributed representation across neurons',
      'Phase Coding: Spike alignment with oscillatory phases',
      'Burst Coding: Information in spike burst patterns',
      'STDP Learning: Hebbian learning with spike timing',
      'Homeostatic Plasticity: Self-regulation of firing rates',
      'Metaplasticity: Adaptive learning rate modulation'
    ],
    mathematicalFoundation: [
      'Membrane Potential: τ dV/dt = -(V - V_rest) + R × I(t)',
      'Spike Threshold: S(t) = 1 if V(t) > θ, else 0',
      'STDP Rule: Δw = A⁺e^(-Δt/τ⁺) (LTP) or -A⁻e^(Δt/τ⁻) (LTD)',
      'Triplet STDP: Δw = A₃⁺e^(-Δt₁/τ⁺)e^(-Δt₂/τ⁺)',
      'Neural Entropy: H = -Σ p(spike) log₂ p(spike)',
      'Firing Rate: r = N_spikes / time_window',
      'Population Vector: P = Σ rᵢ × wᵢ'
    ],
    advantages: [
      'Energy efficient: Only active neurons consume power',
      'Temporal dynamics capture time-dependent patterns',
      'Continuous learning through STDP',
      'Distributed representation for noise tolerance',
      'Biologically plausible processing',
      'Adaptive to data characteristics',
      'Sparse coding for efficient representation'
    ],
    disadvantages: [
      'Slow processing (neural simulation overhead)',
      'High memory usage for network storage',
      'Requires training on representative data',
      'Non-deterministic due to neural dynamics',
      'Complex parameter tuning',
      'Limited compression ratio on standard data',
      'Difficult to interpret learned representations'
    ],
    useCases: [
      'Temporal sequence data (time series, audio)',
      'Pattern recognition in noisy data',
      'Adaptive compression for changing data',
      'Neuromorphic hardware acceleration',
      'Research in brain-inspired computing',
      'Event-based sensor data compression'
    ],
    complexity: {
      time: 'O(N × M × T) where N=neurons, M=synapses, T=simulation time',
      space: 'O(N²) for synaptic connections'
    },
    performance: {
      speed: 'Slow (neural simulation)',
      compressionRatio: '1.2x - 2.5x (data-dependent)',
      memoryUsage: 'High (50+ MB for 100 neurons)'
    },
    parameters: [
      { name: 'num_neurons', description: 'Number of neurons in network', defaultValue: 100, range: '50-500' },
      { name: 'network_layers', description: 'Number of network layers', defaultValue: 3, range: '1-5' },
      { name: 'spike_threshold', description: 'Spike generation threshold', defaultValue: 0.1, range: '0.05-0.2' },
      { name: 'stdp_learning_rate', description: 'STDP learning rate', defaultValue: 0.01, range: '0.001-0.1' },
      { name: 'temporal_window', description: 'Temporal coding window (ms)', defaultValue: 100, range: '50-200' }
    ],
    references: [
      'Maass (1997). "Networks of Spiking Neurons"',
      'Gerstner & Kistler (2002). "Spiking Neuron Models"',
      'Izhikevich (2003). "Simple Model of Spiking Neurons"',
      'Bi & Poo (1998). "Synaptic Modifications by Correlated Activity"'
    ]
  },
  topological: {
    name: 'topological',
    displayName: 'Topological Compression',
    category: 'experimental',
    description: 'Compression using topological data analysis and persistent homology',
    detailedDescription: 'An algorithm leveraging topological data analysis to identify and compress data based on its intrinsic geometric and topological structure. Uses persistent homology to extract significant topological features that capture the essential shape of data.',
    mechanism: [
      'Point Cloud Representation: Data embedded in metric space',
      'Vietoris-Rips Complex: Simplicial complex construction',
      'Filtration: Multi-scale analysis with increasing radius',
      'Boundary Matrix: Algebraic representation of simplices',
      'Matrix Reduction: Column operations for persistence pairs',
      'Persistence Bars: Birth-death time intervals',
      'Homology Computation: Topological hole detection',
      'Feature Extraction: Significant persistent features',
      'Barcode Encoding: Compressed representation'
    ],
    mathematicalFoundation: [
      'Persistent Homology: H_k(X) = Z_k(X) / B_k(X)',
      'Vietoris-Rips: VR(X, ε) = {σ ⊆ X | diam(σ) ≤ ε}',
      'Filtration: VR(X, ε₁) ⊆ VR(X, ε₂) for ε₁ ≤ ε₂',
      'Boundary Operator: ∂: C_{k+1} → C_k',
      'Persistence: lifetime = death_time - birth_time',
      'Bottleneck Distance: d_B(D₁, D₂) for diagram comparison',
      'Betti Numbers: β_k = rank(H_k) dimensional features'
    ],
    advantages: [
      'Captures global data structure',
      'Multi-scale analysis at different resolutions',
      'Robust to noise and outliers',
      'Dimension reduction to essential features',
      'Coordinate-free representation',
      'Mathematically rigorous framework',
      'Stable under small perturbations'
    ],
    disadvantages: [
      'Very slow computation (O(n³) complexity)',
      'Extremely high memory usage',
      'Limited compression on non-geometric data',
      'Requires careful parameter selection',
      'Difficult to interpret results',
      'Not suitable for real-time processing',
      'Limited practical implementations'
    ],
    useCases: [
      'Geometric and spatial data compression',
      'Shape analysis and recognition',
      'Point cloud data (3D scans, LiDAR)',
      'Network and graph data',
      'Scientific data with intrinsic structure',
      'Research in topological data analysis'
    ],
    complexity: {
      time: 'O(n³) for VR complex, O(n²) for persistence',
      space: 'O(n²) for complex storage'
    },
    performance: {
      speed: 'Very slow (topological computation)',
      compressionRatio: '1.1x - 2x (geometry-dependent)',
      memoryUsage: 'Very high (500+ MB for 1000 points)'
    },
    parameters: [
      { name: 'max_dimension', description: 'Maximum homology dimension', defaultValue: 3, range: '1-4' },
      { name: 'persistence_threshold', description: 'Minimum persistence for features', defaultValue: 0.01, range: '0.001-0.1' },
      { name: 'point_cloud_size', description: 'Size of point cloud representation', defaultValue: 100, range: '50-500' },
      { name: 'filtration_steps', description: 'Number of filtration steps', defaultValue: 20, range: '10-50' }
    ],
    references: [
      'Edelsbrunner & Harer (2010). "Computational Topology"',
      'Zomorodian & Carlsson (2005). "Computing Persistent Homology"',
      'Chazal & Michel (2021). "Introduction to Topological Data Analysis"',
      'Carlsson (2009). "Topology and Data"'
    ]
  }
}

const AlgorithmInfoModal: React.FC<AlgorithmInfoModalProps> = ({ isOpen, onClose, algorithm }) => {
  const info = algorithmData[algorithm]

  if (!info) return null

  const getIcon = () => {
    switch (algorithm) {
      case 'quantum_biological':
        return <Atom className="w-6 h-6" />
      case 'neuromorphic':
        return <Brain className="w-6 h-6" />
      case 'topological':
        return <Network className="w-6 h-6" />
      default:
        return <Info className="w-6 h-6" />
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'traditional':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30'
      case 'advanced':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30'
      case 'experimental':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30'
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/30'
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border border-slate-700 shadow-2xl"
          >
            {/* Header */}
            <div className="sticky top-0 z-10 flex items-center justify-between p-6 border-b border-slate-700 bg-slate-900/95 backdrop-blur-sm">
              <div className="flex items-center space-x-4">
                <div className="p-3 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30">
                  {getIcon()}
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">{info.displayName}</h2>
                  <span className={`inline-block px-3 py-1 text-xs font-semibold rounded-full border mt-1 ${getCategoryColor(info.category)}`}>
                    {info.category.toUpperCase()}
                  </span>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-slate-700/50 transition-colors"
              >
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-100px)] custom-scrollbar">
              {/* Description */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-2">Overview</h3>
                <p className="text-slate-300">{info.detailedDescription}</p>
              </div>

              {/* Mechanism */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
                  <Activity className="w-5 h-5 mr-2 text-cyan-400" />
                  Mechanism of Action
                </h3>
                <div className="space-y-2">
                  {info.mechanism.map((step, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-slate-800/50 border border-slate-700/50">
                      <span className="flex-shrink-0 w-6 h-6 rounded-full bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-xs font-semibold text-cyan-300">
                        {index + 1}
                      </span>
                      <p className="text-sm text-slate-300">{step}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Mathematical Foundation */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-3">Mathematical Foundation</h3>
                <div className="p-4 rounded-lg bg-slate-800/70 border border-slate-700/50 space-y-2">
                  {info.mathematicalFoundation.map((formula, index) => (
                    <div key={index} className="text-sm font-mono text-cyan-300">
                      {formula}
                    </div>
                  ))}
                </div>
              </div>

              {/* Performance */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-3">Performance Characteristics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                    <div className="text-xs text-slate-400 mb-1">Speed</div>
                    <div className="text-sm font-semibold text-white">{info.performance.speed}</div>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                    <div className="text-xs text-slate-400 mb-1">Compression Ratio</div>
                    <div className="text-sm font-semibold text-white">{info.performance.compressionRatio}</div>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                    <div className="text-xs text-slate-400 mb-1">Memory Usage</div>
                    <div className="text-sm font-semibold text-white">{info.performance.memoryUsage}</div>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                    <div className="text-xs text-slate-400 mb-1">Time Complexity</div>
                    <div className="text-sm font-mono text-cyan-300">{info.complexity.time}</div>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                    <div className="text-xs text-slate-400 mb-1">Space Complexity</div>
                    <div className="text-sm font-mono text-cyan-300">{info.complexity.space}</div>
                  </div>
                </div>
              </div>

              {/* Advantages & Disadvantages */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-green-400 mb-3">✓ Advantages</h3>
                  <ul className="space-y-2">
                    {info.advantages.map((adv, index) => (
                      <li key={index} className="flex items-start space-x-2 text-sm text-slate-300">
                        <span className="text-green-400 mt-0.5">•</span>
                        <span>{adv}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-red-400 mb-3">✗ Disadvantages</h3>
                  <ul className="space-y-2">
                    {info.disadvantages.map((dis, index) => (
                      <li key={index} className="flex items-start space-x-2 text-sm text-slate-300">
                        <span className="text-red-400 mt-0.5">•</span>
                        <span>{dis}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Use Cases */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-3">Optimal Use Cases</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {info.useCases.map((useCase, index) => (
                    <div key={index} className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-sm text-slate-300">
                      {useCase}
                    </div>
                  ))}
                </div>
              </div>

              {/* Parameters */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-3">Configuration Parameters</h3>
                <div className="space-y-3">
                  {info.parameters.map((param, index) => (
                    <div key={index} className="p-4 rounded-lg bg-slate-800/50 border border-slate-700/50">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-cyan-300 font-mono text-sm">{param.name}</span>
                        <span className="text-xs text-slate-400">Default: {String(param.defaultValue)}</span>
                      </div>
                      <p className="text-sm text-slate-300 mb-1">{param.description}</p>
                      {param.range && (
                        <div className="text-xs text-slate-400">Range: {param.range}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* References */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Academic References</h3>
                <div className="space-y-2">
                  {info.references.map((ref, index) => (
                    <div key={index} className="text-sm text-slate-400 italic pl-4 border-l-2 border-slate-700">
                      {ref}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}

export default AlgorithmInfoModal


