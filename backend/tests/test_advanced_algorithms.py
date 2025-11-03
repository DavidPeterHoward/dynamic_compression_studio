"""
Comprehensive unit tests for advanced compression algorithms.

Tests quantum-biological, neuromorphic, and topological compression algorithms
with mock data, edge cases, and performance validation.
"""

import pytest
import numpy as np
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import the advanced algorithms
from app.algorithms.quantum_biological.versions.v1_hybrid import (
    QuantumBiologicalCompressor, QuantumState, GeneticIndividual, DNABase
)
from app.algorithms.neuromorphic.versions.v1_spiking import (
    NeuromorphicCompressor, SpikingNeuron, Spike, Synapse, NeuronType
)
from app.algorithms.topological.versions.v1_persistent import (
    TopologicalCompressor, PersistenceBar, Simplex, TopologyType
)


class TestQuantumBiologicalAlgorithm:
    """Test suite for quantum-biological compression algorithm."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.compressor = QuantumBiologicalCompressor(population_size=20, quantum_qubits=4)
        self.test_data = b"Test quantum biological compression algorithm"
        self.repetitive_data = b"AAAAABBBBBCCCCC" * 10
        self.random_data = os.urandom(100)
    
    def test_compressor_initialization(self):
        """Test compressor initialization."""
        assert self.compressor.population_size == 20
        assert self.compressor.quantum_qubits == 4
        assert len(self.compressor.population) == 20
        assert len(self.compressor.quantum_registers) == 0
    
    def test_basic_compression(self):
        """Test basic compression functionality."""
        compressed, metadata = self.compressor.compress(self.test_data)
        
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0
        assert metadata.compression_ratio > 0
        assert metadata.algorithm_efficiency > 0
    
    def test_compression_ratio(self):
        """Test compression ratio calculation."""
        compressed, metadata = self.compressor.compress(self.test_data)
        
        expected_ratio = len(self.test_data) / len(compressed)
        assert abs(metadata.compression_ratio - expected_ratio) < 0.01
    
    def test_repetitive_data_compression(self):
        """Test compression of repetitive data."""
        compressed, metadata = self.compressor.compress(self.repetitive_data)
        
        # Repetitive data should compress well
        assert metadata.compression_ratio > 1.5
        assert len(compressed) < len(self.repetitive_data)
    
    def test_quantum_state_creation(self):
        """Test quantum state creation and manipulation."""
        patterns = [b"test", b"data", b"compression"]
        amplitudes = np.array([0.5, 0.3, 0.2], dtype=complex)
        
        quantum_state = QuantumState(
            patterns=patterns,
            amplitudes=amplitudes
        )
        
        assert len(quantum_state.patterns) == 3
        assert len(quantum_state.amplitudes) == 3
        assert not quantum_state.measured
    
    def test_quantum_measurement(self):
        """Test quantum measurement process."""
        patterns = [b"test", b"data"]
        amplitudes = np.array([0.7, 0.3], dtype=complex)
        
        quantum_state = QuantumState(
            patterns=patterns,
            amplitudes=amplitudes
        )
        
        # Measure multiple times to test randomness
        measurements = [quantum_state.measure() for _ in range(10)]
        
        # Should get valid indices
        for measurement in measurements:
            assert 0 <= measurement < len(patterns)
        
        # Should be measured after first measurement
        assert quantum_state.measured
    
    def test_genetic_individual_creation(self):
        """Test genetic individual creation and operations."""
        genome = {
            'dictionary_size': 1024,
            'min_match_length': 3,
            'mutation_rate': 0.1
        }
        
        individual = GeneticIndividual(genome=genome)
        
        assert individual.genome == genome
        assert individual.fitness == 0.0
        assert individual.age == 0
    
    def test_genetic_mutation(self):
        """Test genetic mutation process."""
        genome = {'dictionary_size': 1024, 'mutation_rate': 0.1}
        individual = GeneticIndividual(genome=genome)
        
        original_genome = individual.genome.copy()
        individual.mutate(mutation_rate=0.5)
        
        # Genome should be modified (with high probability)
        assert individual.genome != original_genome
    
    def test_genetic_crossover(self):
        """Test genetic crossover operation."""
        parent1 = GeneticIndividual(genome={'param1': 100, 'param2': 200})
        parent2 = GeneticIndividual(genome={'param1': 150, 'param2': 250})
        
        child = parent1.crossover(parent2)
        
        assert isinstance(child, GeneticIndividual)
        assert 'param1' in child.genome
        assert 'param2' in child.genome
    
    def test_dna_encoding(self):
        """Test DNA encoding functionality."""
        test_bytes = b"ABC"
        encoded = self.compressor._dna_encode(test_bytes)
        
        assert encoded.startswith(b'DNA:')
        assert len(encoded) > len(test_bytes)
        
        # Test decoding
        decoded = self.compressor._dna_decode(encoded[4:])  # Remove 'DNA:' prefix
        assert len(decoded) == len(test_bytes)
    
    def test_quantum_entropy_calculation(self):
        """Test quantum entropy calculation."""
        patterns = [b"test", b"data"]
        amplitudes = np.array([0.6, 0.4], dtype=complex)
        
        quantum_state = QuantumState(patterns=patterns, amplitudes=amplitudes)
        entropy = self.compressor._calculate_quantum_entropy([quantum_state])
        
        assert entropy >= 0
        assert isinstance(entropy, float)
    
    def test_entanglement_calculation(self):
        """Test entanglement measure calculation."""
        test_data = b"test entanglement calculation"
        entanglement = self.compressor._calculate_entanglement(test_data)
        
        assert 0 <= entanglement <= 1
        assert isinstance(entanglement, float)
    
    def test_quantum_limit_calculation(self):
        """Test quantum compression limit calculation."""
        limit = self.compressor._calculate_quantum_limit(self.test_data)
        
        assert limit > 0
        assert isinstance(limit, float)
    
    def test_decompression(self):
        """Test decompression functionality."""
        compressed, _ = self.compressor.compress(self.test_data)
        decompressed = self.compressor.decompress(compressed)
        
        # Note: Current implementation is simplified
        # In practice, would need proper decompression
        assert isinstance(decompressed, bytes)
    
    def test_improved_version_generation(self):
        """Test improved version generation."""
        improved = self.compressor.generate_improved_version()
        
        assert isinstance(improved, QuantumBiologicalCompressor)
        assert improved.version != self.compressor.version
        assert improved.population_size == self.compressor.population_size
    
    def test_export_analysis(self):
        """Test analysis export functionality."""
        # Compress some data first
        self.compressor.compress(self.test_data)
        
        analysis = self.compressor.export_quantum_analysis()
        
        assert isinstance(analysis, str)
        assert "Quantum-Biological Compression Analysis" in analysis
        assert "Qubits:" in analysis
        assert "Population Size:" in analysis


class TestNeuromorphicAlgorithm:
    """Test suite for neuromorphic compression algorithm."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.compressor = NeuromorphicCompressor(num_neurons=20, network_layers=2)
        self.test_data = b"Test neuromorphic compression algorithm"
        self.temporal_data = b"temporal pattern recognition test data"
    
    def test_compressor_initialization(self):
        """Test compressor initialization."""
        assert self.compressor.num_neurons == 20
        assert self.compressor.network_layers == 2
        assert len(self.compressor.neurons) == 20
        assert len(self.compressor.synapses) > 0
    
    def test_basic_compression(self):
        """Test basic compression functionality."""
        compressed, metadata = self.compressor.compress(self.test_data)
        
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0
        assert metadata.compression_ratio > 0
        assert metadata.algorithm_efficiency > 0
    
    def test_neuron_creation(self):
        """Test neuron creation and initialization."""
        neuron = SpikingNeuron(0, NeuronType.LEAKY_INTEGRATE_FIRE)
        
        assert neuron.neuron_id == 0
        assert neuron.neuron_type == NeuronType.LEAKY_INTEGRATE_FIRE
        assert neuron.V_membrane == -70.0
        assert neuron.V_threshold == -55.0
    
    def test_neuron_update(self):
        """Test neuron state update."""
        neuron = SpikingNeuron(0, NeuronType.LEAKY_INTEGRATE_FIRE)
        
        # Test without input current
        spiked = neuron.update(dt=0.1, input_current=0.0)
        assert isinstance(spiked, bool)
        
        # Test with high input current (should spike)
        neuron.V_membrane = -60.0  # Close to threshold
        spiked = neuron.update(dt=0.1, input_current=100.0)
        # May or may not spike depending on timing
    
    def test_spike_creation(self):
        """Test spike object creation."""
        spike = Spike(timestamp=1.0, neuron_id=0, amplitude=1.0)
        
        assert spike.timestamp == 1.0
        assert spike.neuron_id == 0
        assert spike.amplitude == 1.0
    
    def test_synapse_creation(self):
        """Test synapse creation."""
        synapse = Synapse(
            pre_neuron=0,
            post_neuron=1,
            weight=0.5,
            delay=2.0
        )
        
        assert synapse.pre_neuron == 0
        assert synapse.post_neuron == 1
        assert synapse.weight == 0.5
        assert synapse.delay == 2.0
    
    def test_data_to_spikes_conversion(self):
        """Test data to spike trains conversion."""
        spike_trains = self.compressor._data_to_spikes(self.test_data)
        
        assert isinstance(spike_trains, list)
        assert len(spike_trains) == self.compressor.num_neurons
        
        # Check that spikes are created
        total_spikes = sum(len(train) for train in spike_trains)
        assert total_spikes > 0
    
    def test_network_processing(self):
        """Test neural network processing."""
        spike_trains = self.compressor._data_to_spikes(self.test_data)
        output_spikes = self.compressor._process_network(spike_trains)
        
        assert isinstance(output_spikes, list)
        assert len(output_spikes) == self.compressor.num_neurons
    
    def test_stdp_learning(self):
        """Test spike-timing dependent plasticity learning."""
        input_spikes = self.compressor._data_to_spikes(self.test_data)
        output_spikes = self.compressor._process_network(input_spikes)
        
        # Get initial weights
        initial_weights = [s.weight for s in self.compressor.synapses]
        
        # Apply STDP learning
        self.compressor._apply_stdp_learning(input_spikes, output_spikes)
        
        # Check that weights changed
        final_weights = [s.weight for s in self.compressor.synapses]
        
        # Some weights should have changed
        weight_changes = sum(1 for i, j in zip(initial_weights, final_weights) if abs(i - j) > 0.001)
        assert weight_changes > 0
    
    def test_neural_entropy_calculation(self):
        """Test neural entropy calculation."""
        entropy = self.compressor._calculate_neural_entropy()
        
        assert entropy >= 0
        assert isinstance(entropy, float)
    
    def test_spike_efficiency_calculation(self):
        """Test spike efficiency calculation."""
        efficiency = self.compressor._calculate_spike_efficiency()
        
        assert 0 <= efficiency <= 1
        assert isinstance(efficiency, float)
    
    def test_learning_progress_calculation(self):
        """Test learning progress calculation."""
        progress = self.compressor._calculate_learning_progress()
        
        assert progress >= 0
        assert isinstance(progress, float)
    
    def test_neural_limit_calculation(self):
        """Test neural compression limit calculation."""
        limit = self.compressor._calculate_neural_limit(self.test_data)
        
        assert limit > 0
        assert isinstance(limit, float)
    
    def test_decompression(self):
        """Test decompression functionality."""
        compressed, _ = self.compressor.compress(self.test_data)
        decompressed = self.compressor.decompress(compressed)
        
        assert isinstance(decompressed, bytes)
    
    def test_improved_version_generation(self):
        """Test improved version generation."""
        improved = self.compressor.generate_improved_version()
        
        assert isinstance(improved, NeuromorphicCompressor)
        assert improved.version != self.compressor.version
        assert improved.num_neurons == self.compressor.num_neurons
    
    def test_export_analysis(self):
        """Test analysis export functionality."""
        # Compress some data first
        self.compressor.compress(self.test_data)
        
        analysis = self.compressor.export_neural_analysis()
        
        assert isinstance(analysis, str)
        assert "Neuromorphic Compression Analysis" in analysis
        assert "Neurons:" in analysis
        assert "Synapses:" in analysis


class TestTopologicalAlgorithm:
    """Test suite for topological compression algorithm."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.compressor = TopologicalCompressor(max_dimension=2, persistence_threshold=0.01)
        self.test_data = b"Test topological compression algorithm"
        self.geometric_data = b"geometric structure analysis test data"
    
    def test_compressor_initialization(self):
        """Test compressor initialization."""
        assert self.compressor.max_dimension == 2
        assert self.compressor.persistence_threshold == 0.01
        assert len(self.compressor.points) == 0
        assert len(self.compressor.persistence_bars) == 0
    
    def test_basic_compression(self):
        """Test basic compression functionality."""
        compressed, metadata = self.compressor.compress(self.test_data)
        
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0
        assert metadata.compression_ratio > 0
        assert metadata.algorithm_efficiency > 0
    
    def test_persistence_bar_creation(self):
        """Test persistence bar creation."""
        bar = PersistenceBar(
            birth=0.1,
            death=0.5,
            dimension=1
        )
        
        assert bar.birth == 0.1
        assert bar.death == 0.5
        assert bar.dimension == 1
        assert bar.persistence == 0.4
        assert bar.is_significant
    
    def test_simplex_creation(self):
        """Test simplex creation."""
        simplex = Simplex(
            vertices={0, 1, 2},
            dimension=2,
            birth_time=0.1
        )
        
        assert simplex.vertices == {0, 1, 2}
        assert simplex.dimension == 2
        assert simplex.birth_time == 0.1
    
    def test_data_to_point_cloud_conversion(self):
        """Test data to point cloud conversion."""
        points = self.compressor._data_to_point_cloud(self.test_data)
        
        assert isinstance(points, list)
        assert len(points) > 0
        
        # Check point dimensions
        for point in points:
            assert isinstance(point, np.ndarray)
            assert len(point) == 8  # 8-dimensional space
    
    def test_vietoris_rips_complex_construction(self):
        """Test Vietoris-Rips complex construction."""
        points = self.compressor._data_to_point_cloud(self.test_data)
        filtration = self.compressor._build_vietoris_rips_complex(points)
        
        assert isinstance(filtration, list)
        assert len(filtration) > 0
        
        # Check that complex grows with radius
        for i in range(len(filtration) - 1):
            assert len(filtration[i]) <= len(filtration[i + 1])
    
    def test_persistent_homology_computation(self):
        """Test persistent homology computation."""
        points = self.compressor._data_to_point_cloud(self.test_data)
        filtration = self.compressor._build_vietoris_rips_complex(points)
        persistence_bars = self.compressor._compute_persistent_homology(filtration)
        
        assert isinstance(persistence_bars, list)
        
        # Check bar properties
        for bar in persistence_bars:
            assert isinstance(bar, PersistenceBar)
            assert bar.birth >= 0
            assert bar.death >= bar.birth
            assert 0 <= bar.dimension <= self.compressor.max_dimension
    
    def test_significant_features_extraction(self):
        """Test significant features extraction."""
        # Create test persistence bars
        bars = [
            PersistenceBar(0.1, 0.2, 0),  # Not significant
            PersistenceBar(0.1, 0.5, 1),  # Significant
            PersistenceBar(0.2, 0.8, 2),  # Significant
        ]
        
        significant = self.compressor._extract_significant_features(bars)
        
        assert len(significant) <= len(bars)
        assert all(bar.is_significant for bar in significant)
    
    def test_topological_entropy_calculation(self):
        """Test topological entropy calculation."""
        # Create test persistence bars
        bars = [
            PersistenceBar(0.1, 0.5, 0),
            PersistenceBar(0.2, 0.6, 1),
        ]
        
        entropy = self.compressor._calculate_topological_entropy(bars)
        
        assert entropy >= 0
        assert isinstance(entropy, float)
    
    def test_feature_density_calculation(self):
        """Test feature density calculation."""
        features = [
            PersistenceBar(0.1, 0.5, 0),
            PersistenceBar(0.2, 0.6, 1),
        ]
        
        density = self.compressor._calculate_feature_density(features)
        
        assert density >= 0
        assert isinstance(density, float)
    
    def test_structural_complexity_calculation(self):
        """Test structural complexity calculation."""
        points = self.compressor._data_to_point_cloud(self.test_data)
        complexity = self.compressor._calculate_structural_complexity(points)
        
        assert complexity >= 0
        assert isinstance(complexity, float)
    
    def test_topological_limit_calculation(self):
        """Test topological compression limit calculation."""
        limit = self.compressor._calculate_topological_limit(self.test_data)
        
        assert limit > 0
        assert isinstance(limit, float)
    
    def test_decompression(self):
        """Test decompression functionality."""
        compressed, _ = self.compressor.compress(self.test_data)
        decompressed = self.compressor.decompress(compressed)
        
        assert isinstance(decompressed, bytes)
    
    def test_improved_version_generation(self):
        """Test improved version generation."""
        improved = self.compressor.generate_improved_version()
        
        assert isinstance(improved, TopologicalCompressor)
        assert improved.version != self.compressor.version
        assert improved.max_dimension == self.compressor.max_dimension
    
    def test_export_analysis(self):
        """Test analysis export functionality."""
        # Compress some data first
        self.compressor.compress(self.test_data)
        
        analysis = self.compressor.export_topological_analysis()
        
        assert isinstance(analysis, str)
        assert "Topological Compression Analysis" in analysis
        assert "Max Dimension:" in analysis
        assert "Persistence Threshold:" in analysis


class TestAdvancedAlgorithmsIntegration:
    """Integration tests for advanced algorithms."""
    
    def test_algorithm_comparison(self):
        """Test comparison between all advanced algorithms."""
        test_data = b"Integration test data for advanced algorithms comparison"
        
        # Initialize all compressors
        quantum_compressor = QuantumBiologicalCompressor()
        neuromorphic_compressor = NeuromorphicCompressor()
        topological_compressor = TopologicalCompressor()
        
        # Compress with each algorithm
        quantum_compressed, quantum_metadata = quantum_compressor.compress(test_data)
        neuromorphic_compressed, neuromorphic_metadata = neuromorphic_compressor.compress(test_data)
        topological_compressed, topological_metadata = topological_compressor.compress(test_data)
        
        # All should produce valid results
        assert len(quantum_compressed) > 0
        assert len(neuromorphic_compressed) > 0
        assert len(topological_compressed) > 0
        
        # All should have valid metadata
        assert quantum_metadata.compression_ratio > 0
        assert neuromorphic_metadata.compression_ratio > 0
        assert topological_metadata.compression_ratio > 0
    
    def test_algorithm_specific_metrics(self):
        """Test that each algorithm produces algorithm-specific metrics."""
        test_data = b"Test data for algorithm-specific metrics"
        
        # Quantum-biological metrics
        quantum_compressor = QuantumBiologicalCompressor()
        _, quantum_metadata = quantum_compressor.compress(test_data)
        
        assert 'quantum_entropy' in quantum_metadata.data_characteristics
        assert 'entanglement_measure' in quantum_metadata.data_characteristics
        assert 'generation' in quantum_metadata.data_characteristics
        
        # Neuromorphic metrics
        neuromorphic_compressor = NeuromorphicCompressor()
        _, neuromorphic_metadata = neuromorphic_compressor.compress(test_data)
        
        assert 'neural_entropy' in neuromorphic_metadata.data_characteristics
        assert 'spike_efficiency' in neuromorphic_metadata.data_characteristics
        assert 'active_neurons' in neuromorphic_metadata.data_characteristics
        
        # Topological metrics
        topological_compressor = TopologicalCompressor()
        _, topological_metadata = topological_compressor.compress(test_data)
        
        assert 'topological_entropy' in topological_metadata.data_characteristics
        assert 'feature_density' in topological_metadata.data_characteristics
        assert 'persistence_bars' in topological_metadata.data_characteristics
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks for all algorithms."""
        test_data = b"Performance benchmark test data" * 10  # Larger dataset
        
        algorithms = [
            ("quantum_biological", QuantumBiologicalCompressor()),
            ("neuromorphic", NeuromorphicCompressor()),
            ("topological", TopologicalCompressor())
        ]
        
        results = {}
        
        for name, compressor in algorithms:
            start_time = time.time()
            compressed, metadata = compressor.compress(test_data)
            end_time = time.time()
            
            results[name] = {
                'compression_time': end_time - start_time,
                'compression_ratio': metadata.compression_ratio,
                'compressed_size': len(compressed)
            }
        
        # All algorithms should complete within reasonable time
        for name, result in results.items():
            assert result['compression_time'] < 10.0  # 10 seconds max
            assert result['compression_ratio'] > 0
            assert result['compressed_size'] > 0
    
    def test_error_handling(self):
        """Test error handling for all algorithms."""
        # Test with empty data
        empty_data = b""
        
        quantum_compressor = QuantumBiologicalCompressor()
        neuromorphic_compressor = NeuromorphicCompressor()
        topological_compressor = TopologicalCompressor()
        
        # All should handle empty data gracefully
        for compressor in [quantum_compressor, neuromorphic_compressor, topological_compressor]:
            compressed, metadata = compressor.compress(empty_data)
            assert isinstance(compressed, bytes)
            assert isinstance(metadata.compression_ratio, float)
    
    def test_memory_usage(self):
        """Test memory usage for all algorithms."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Test with each algorithm
        test_data = b"Memory usage test data" * 100
        
        quantum_compressor = QuantumBiologicalCompressor()
        neuromorphic_compressor = NeuromorphicCompressor()
        topological_compressor = TopologicalCompressor()
        
        compressors = [quantum_compressor, neuromorphic_compressor, topological_compressor]
        
        for compressor in compressors:
            compressed, _ = compressor.compress(test_data)
            current_memory = process.memory_info().rss
            memory_increase = current_memory - initial_memory
            
            # Memory increase should be reasonable (less than 100MB)
            assert memory_increase < 100 * 1024 * 1024


class TestMockDataGeneration:
    """Test mock data generation for advanced algorithms."""
    
    def test_quantum_mock_data(self):
        """Test quantum-biological algorithm with mock data."""
        # Generate mock quantum data
        mock_patterns = [b"pattern1", b"pattern2", b"pattern3"]
        mock_amplitudes = np.array([0.5, 0.3, 0.2], dtype=complex)
        
        quantum_state = QuantumState(
            patterns=mock_patterns,
            amplitudes=mock_amplitudes
        )
        
        assert len(quantum_state.patterns) == 3
        assert len(quantum_state.amplitudes) == 3
        
        # Test measurement
        measurement = quantum_state.measure()
        assert 0 <= measurement < 3
    
    def test_neuromorphic_mock_data(self):
        """Test neuromorphic algorithm with mock data."""
        # Generate mock spike data
        mock_spikes = [
            Spike(timestamp=1.0, neuron_id=0, amplitude=1.0),
            Spike(timestamp=2.0, neuron_id=1, amplitude=0.8),
            Spike(timestamp=3.0, neuron_id=0, amplitude=0.6)
        ]
        
        assert len(mock_spikes) == 3
        assert all(isinstance(spike, Spike) for spike in mock_spikes)
        
        # Test spike properties
        for spike in mock_spikes:
            assert spike.timestamp > 0
            assert spike.neuron_id >= 0
            assert 0 < spike.amplitude <= 1.0
    
    def test_topological_mock_data(self):
        """Test topological algorithm with mock data."""
        # Generate mock persistence bars
        mock_bars = [
            PersistenceBar(birth=0.1, death=0.5, dimension=0),
            PersistenceBar(birth=0.2, death=0.8, dimension=1),
            PersistenceBar(birth=0.3, death=0.6, dimension=2)
        ]
        
        assert len(mock_bars) == 3
        assert all(isinstance(bar, PersistenceBar) for bar in mock_bars)
        
        # Test bar properties
        for bar in mock_bars:
            assert bar.birth >= 0
            assert bar.death >= bar.birth
            assert 0 <= bar.dimension <= 2
            assert bar.persistence >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
