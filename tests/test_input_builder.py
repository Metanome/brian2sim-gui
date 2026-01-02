"""
Unit tests for InputBuilder class.
Tests input current, noise patterns, and external input generation.
"""
import pytest
import brian2 as b2
from unittest.mock import patch, MagicMock
import numpy as np
from brian2sim.core.engine.input_builder import InputBuilder
from brian2sim.core.engine.neuron_builder import NeuronBuilder


class TestInputCurrent:
    """Tests for input current generation."""
    
    def test_basic_input_current(self, default_sim_params, default_neuron_params):
        """Test basic input current setup."""
        nb = NeuronBuilder()
        ib = InputBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        current = ib.setup_input_current(default_sim_params, neurons, "lif")
        
        assert current is not None
        assert hasattr(current, 'values')
        
    def test_input_current_timing(self):
        """Test that input current respects start and duration."""
        ib = InputBuilder()
        nb = NeuronBuilder()
        
        sim_params = {
            "num_neurons": 5,
            "sim_time": 100,
            "dt": 0.1,
            "v_threshold": -50.0,
            "v_reset": -70.0,
            "input_current": 1.0,
            "current_start": 20,
            "current_duration": 30
        }
        
        neuron_params = {
            "model_key": "lif",
            "parameters": {"tau_m": 20.0, "v_rest": -70.0, "resistance": 100.0, "refractory": 2.0}
        }
        
        neurons = nb.build_neurons(sim_params, neuron_params, {}, {})
        current = ib.setup_input_current(sim_params, neurons, "lif")
        
        assert current is not None
        
    def test_dimensionless_current_izhikevich(self):
        """Test input current for Izhikevich (dimensionless)."""
        ib = InputBuilder()
        nb = NeuronBuilder()
        
        sim_params = {"num_neurons": 5, "sim_time": 100, "dt": 0.1, "input_current": 10.0}
        neuron_params = {
            "model_key": "izhikevich",
            "parameters": {"a": 0.02, "b": 0.2, "c": -65.0, "d": 8.0}
        }
        
        neurons = nb.build_neurons(sim_params, neuron_params, {}, {})
        current = ib.setup_input_current(sim_params, neurons, "izhikevich")
        
        assert current is not None


class TestNoisePatterns:
    """Tests for noise input patterns."""
    
    def test_gaussian_noise(self, default_sim_params, default_neuron_params):
        """Test Gaussian noise setup."""
        nb = NeuronBuilder()
        ib = InputBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        noise_params = {
            "enabled": True,
            "method": "Gaussian",
            "intensity": 0.1
        }
        
        result = ib.setup_noise(noise_params, neurons)
        # Noise returns True when enabled
        assert result is True
        
    def test_ornstein_uhlenbeck_noise(self, default_sim_params, default_neuron_params):
        """Test Ornstein-Uhlenbeck noise."""
        nb = NeuronBuilder()
        ib = InputBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        noise_params = {
            "enabled": True,
            "method": "Ornstein-Uhlenbeck",
            "intensity": 0.05,
            "correlation_time": 10
        }
        
        result = ib.setup_noise(noise_params, neurons)
        assert result is True
        
    def test_noise_disabled(self, default_sim_params, default_neuron_params):
        """Test that disabled noise returns None."""
        nb = NeuronBuilder()
        ib = InputBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        noise_params = {"enabled": False}
        result = ib.setup_noise(noise_params, neurons)
        
        assert result is None


class TestInputPatterns:
    """Tests for external input patterns."""
    
    def test_poisson_input_creation(self, default_sim_params, default_neuron_params):
        """Test Poisson input group creation."""
        nb = NeuronBuilder()
        ib = InputBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        pattern_params = {
            "enabled": True,
            "pattern_type": "poisson",
            "num_inputs": 20,
            "poisson_rate": 50.0,
            "poisson_weight": 0.5
        }
        
        result = ib.setup_input_patterns(pattern_params, neurons)
        
        assert result is not None
        assert "poisson_group" in result
        assert "input_synapses" in result
        
    def test_regular_spiking_input(self, default_sim_params, default_neuron_params):
        """Test regular spiking input."""
        nb = NeuronBuilder()
        ib = InputBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        pattern_params = {
            "enabled": True,
            "pattern_type": "burst",
            "burst_frequency": 100.0
        }
        
        result = ib.setup_input_patterns(pattern_params, neurons)
        
        assert result is not None
        assert "burst_group" in result
        assert "burst_synapses" in result
        
    def test_input_patterns_disabled(self, default_sim_params, default_neuron_params):
        """Test that disabled patterns return None."""
        nb = NeuronBuilder()
        ib = InputBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        pattern_params = {"enabled": False}
        result = ib.setup_input_patterns(pattern_params, neurons)
        
        assert result is None


class TestInputBuilderEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_zero_duration_current(self):
        """Test input with zero duration."""
        ib = InputBuilder()
        nb = NeuronBuilder()
        
        sim_params = {
            "num_neurons": 5,
            "sim_time": 100,
            "dt": 0.1,
            "input_current": 1.0,
            "current_duration": 0
        }
        
        neuron_params = {
            "model_key": "lif",
            "parameters": {"tau_m": 20.0, "v_rest": -70.0, "resistance": 100.0}
        }
        
        neurons = nb.build_neurons(sim_params, neuron_params, {}, {})
        current = ib.setup_input_current(sim_params, neurons, "lif")
        
        # Should still create current source
        assert current is not None
        
    def test_high_intensity_noise(self, default_sim_params, default_neuron_params):
        """Test noise with high intensity."""
        nb = NeuronBuilder()
        ib = InputBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        noise_params = {
            "enabled": True,
            "method": "Gaussian",
            "intensity": 10.0  # Very high
        }
        
        result = ib.setup_noise(noise_params, neurons)
        assert result is True  # Should handle without error



class TestFileImport:
    """Tests for file-based input generation."""

    def test_spike_file_loading_npy(self, default_sim_params, default_neuron_params):
        """Test loading spike times from NPY file."""
        nb = NeuronBuilder()
        ib = InputBuilder()
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        # Mocking numpy.load to return a dict
        fake_data = {'indices': np.array([0, 1]), 'times': np.array([10.0, 20.0])}
        
        with patch('numpy.load', return_value=fake_data), patch('os.path.exists', return_value=True):
            input_params = {
                "enabled": True,
                "pattern_type": "spike_generator",
                "spike_file_path": "fake_spikes.npy"
            }
            result = ib._setup_spike_generator(input_params, neurons)
            
            assert result is not None
            assert hasattr(result["spike_group"], "t")

    def test_timed_array_loading_csv(self, default_sim_params, default_neuron_params):
        """Test loading timed array from CSV file."""
        nb = NeuronBuilder()
        ib = InputBuilder()
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        # Mocking numpy.loadtxt
        fake_values = np.array([0.1, 0.2, 0.3])
        
        with patch('numpy.loadtxt', return_value=fake_values), patch('os.path.exists', return_value=True):
            input_params = {
                "enabled": True,
                "pattern_type": "timed_array",
                "timed_array_file_path": "fake_current.csv",
                "timed_dt": 0.1
            }
            result = ib._setup_timed_array(input_params, neurons)
            
            assert result is not None
            assert "timed_array" in result
            assert "run_reg" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
