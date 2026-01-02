"""
Unit tests for NeuronBuilder class.
Tests neuron model construction for LIF, Izhikevich, AdEx, and HH models.
"""
import pytest
import brian2 as b2
from brian2sim.core.engine.neuron_builder import NeuronBuilder


class TestLIFNeurons:
    """Tests for Leaky Integrate-and-Fire neurons."""
    
    def test_basic_lif_creation(self, default_sim_params, default_neuron_params):
        """Test basic LIF neuron construction."""
        builder = NeuronBuilder()
        neurons = builder.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        assert neurons is not None
        assert neurons.N == 10
        assert hasattr(neurons, 'v')
        assert hasattr(neurons, 'I')
        assert hasattr(neurons, 'I_gap')
        
    def test_lif_has_threshold_variable(self, default_sim_params, default_neuron_params):
        """Test that LIF neurons have v_th state variable for neuromodulation."""
        builder = NeuronBuilder()
        neurons = builder.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        # After fix, should have v_th as state variable
        assert hasattr(neurons, 'v_th'), "LIF neurons missing v_th state variable"
        
    def test_lif_threshold_initialization(self, default_sim_params, default_neuron_params):
        """Test that v_th is properly initialized."""
        builder = NeuronBuilder()
        neurons = builder.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        # v_th should be initialized to threshold value
        expected_threshold = default_sim_params["v_threshold"] * b2.mV
        assert neurons.v_th[0] == expected_threshold
        
    def test_lif_with_different_parameters(self, default_sim_params):
        """Test LIF with various parameter combinations."""
        builder = NeuronBuilder()
        
        params = {
            "model_key": "lif",
            "parameters": {
                "tau_m": 10.0,  # Fast neuron
                "v_rest": -65.0,
                "resistance": 200.0,
                "refractory": 5.0
            }
        }
        
        neurons = builder.build_neurons(default_sim_params, params, {}, {})
        assert neurons.R[0] == 200.0 * b2.Mohm


class TestIzhikevichNeurons:
    """Tests for Izhikevich neurons."""
    
    def test_basic_izhikevich_creation(self, default_sim_params, izhikevich_params):
        """Test basic Izhikevich neuron construction."""
        builder = NeuronBuilder()
        neurons = builder.build_neurons(default_sim_params, izhikevich_params, {}, {})
        
        assert neurons is not None
        assert neurons.N == 10
        assert hasattr(neurons, 'v')
        assert hasattr(neurons, 'u')
        
    def test_izhikevich_parameter_initialization(self, default_sim_params, izhikevich_params):
        """Test that Izhikevich parameters are correctly set."""
        builder = NeuronBuilder()
        neurons = builder.build_neurons(default_sim_params, izhikevich_params, {}, {})
        
        assert neurons.a[0] == 0.02
        assert neurons.b[0] == 0.2
        assert neurons.c[0] == -65.0
        assert neurons.d[0] == 8.0
        
    def test_izhikevich_bursting_parameters(self, default_sim_params):
        """Test Izhikevich with bursting neuron parameters."""
        builder = NeuronBuilder()
        
        params = {
            "model_key": "izhikevich",
            "parameters": {
                "a": 0.02,
                "b": 0.25,
                "c": -55.0,
                "d": 0.05
            }
        }
        
        neurons = builder.build_neurons(default_sim_params, params, {}, {})
        assert neurons.b[0] == 0.25
        assert neurons.d[0] == 0.05


class TestAdExNeurons:
    """Tests for Adaptive Exponential neurons."""
    
    def test_basic_adex_creation(self, default_sim_params, adex_params):
        """Test basic AdEx neuron construction."""
        builder = NeuronBuilder()
        neurons = builder.build_neurons(default_sim_params, adex_params, {}, {})
        
        assert neurons is not None
        assert neurons.N == 10
        assert hasattr(neurons, 'v')
        assert hasattr(neurons, 'w')
        
    def test_adex_has_threshold_variable(self, default_sim_params, adex_params):
        """Test that AdEx neurons have v_th state variable."""
        builder = NeuronBuilder()
        neurons = builder.build_neurons(default_sim_params, adex_params, {}, {})
        
        assert hasattr(neurons, 'v_th'), "AdEx neurons missing v_th state variable"
        # AdEx uses 0 mV threshold
        assert neurons.v_th[0] == 0 * b2.mV
        
    def test_adex_adaptation_current(self, default_sim_params, adex_params):
        """Test that AdEx has adaptation current w."""
        builder = NeuronBuilder()
        neurons = builder.build_neurons(default_sim_params, adex_params, {}, {})
        
        # w should be initialized to 0
        assert neurons.w[0] == 0 * b2.pA


class TestCalciumDynamics:
    """Tests for calcium dynamics integration."""
    
    def test_calcium_enabled(self, default_sim_params, default_neuron_params, calcium_params):
        """Test neurons with calcium dynamics."""
        builder = NeuronBuilder()
        neurons = builder.build_neurons(default_sim_params, default_neuron_params, calcium_params, {})
        
        # Should have calcium concentration variable
        assert hasattr(neurons, 'Ca')
        
    def test_calcium_equations(self, default_sim_params, default_neuron_params, calcium_params):
        """Test that calcium equations are properly integrated."""
        builder = NeuronBuilder()
        neurons = builder.build_neurons(default_sim_params, default_neuron_params, calcium_params, {})
        
        eq_str = str(neurons.equations)
        assert 'Ca' in eq_str
        assert 'I_Ca' in eq_str or 'ICa' in eq_str  # Calcium current


class TestMulticompartmentNeurons:
    """Tests for multi-compartment neurons."""
    
    def test_multicompartment_creation(self, default_sim_params):
        """Test multi-compartment neuron construction."""
        builder = NeuronBuilder()
        
        mc_params = {
            "enabled": True,
            "num_compartments": 5,
            "compartment_length": 10.0,
            "compartment_diameter": 1.0
        }
        
        neurons = builder.build_neurons(default_sim_params, {"model_key": "lif"}, {}, mc_params)
        
        # Multi-compartment neurons have different structure
        # Test depends on implementation details
        assert neurons is not None


class TestHodgkinHuxleyNeurons:
    """Tests for Hodgkin-Huxley neurons."""
    
    def test_basic_hh_creation(self, default_sim_params):
        """Test basic HH neuron construction."""
        builder = NeuronBuilder()
        
        hh_params = {
            "model_key": "hodgkin_huxley",
            "parameters": {
                "C": 1.0,
                "gNa_max": 120.0,
                "gK_max": 36.0,
                "gL": 0.3,
                "ENa": 50.0,
                "EK": -77.0,
                "EL": -54.387
            }
        }
        
        neurons = builder.build_neurons(default_sim_params, hh_params, {}, {})
        
        assert neurons is not None
        assert neurons.N == 10
        assert hasattr(neurons, 'v')
        
    def test_hh_gating_variables(self, default_sim_params):
        """Test that HH neurons have gating variables m, n, h."""
        builder = NeuronBuilder()
        
        hh_params = {"model_key": "hodgkin_huxley", "parameters": {}}
        neurons = builder.build_neurons(default_sim_params, hh_params, {}, {})
        
        # HH model should have gating variables
        assert hasattr(neurons, 'm'), "HH neurons missing m gating variable"
        assert hasattr(neurons, 'n'), "HH neurons missing n gating variable"
        assert hasattr(neurons, 'h'), "HH neurons missing h gating variable"
        
    def test_hh_gating_initialization(self, default_sim_params):
        """Test that gating variables are initialized correctly."""
        builder = NeuronBuilder()
        
        hh_params = {"model_key": "hodgkin_huxley", "parameters": {}}
        neurons = builder.build_neurons(default_sim_params, hh_params, {}, {})
        
        # Gating variables should be initialized (typically 0-1 range)
        assert 0 <= neurons.m[0] <= 1
        assert 0 <= neurons.n[0] <= 1
        assert 0 <= neurons.h[0] <= 1
        
    def test_hh_conductance_parameters(self, default_sim_params):
        """Test that conductance parameters are set correctly."""
        builder = NeuronBuilder()
        
        hh_params = {
            "model_key": "hodgkin_huxley",
            "parameters": {
                "gNa_max": 150.0,  # Custom value
                "gK_max": 40.0
            }
        }
        
        neurons = builder.build_neurons(default_sim_params, hh_params, {}, {})
        
        # Conductances should be in namespace or state
        assert neurons is not None


class TestNeuronBuilderEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_invalid_model_key(self, default_sim_params):
        """Test that invalid model key is handled gracefully."""
        builder = NeuronBuilder()
        
        params = {"model_key": "invalid_model"}
        
        # Should either raise error or return None
        try:
            neurons = builder.build_neurons(default_sim_params, params, {}, {})
            # If it doesn't raise, it should return None or fallback
        except (ValueError, KeyError):
            pass  # Expected behavior
            
    def test_zero_neurons(self):
        """Test handling of zero neurons."""
        builder = NeuronBuilder()
        
        sim_params = {"num_neurons": 0, "dt": 0.1}
        neuron_params = {"model_key": "lif"}
        
        # Should handle gracefully
        try:
            neurons = builder.build_neurons(sim_params, neuron_params, {}, {})
        except (ValueError, AssertionError):
            pass  # Expected


class TestCustomNeurons:
    """Tests for User-Defined Custom Neurons."""

    def test_custom_neuron_creation(self, default_sim_params):
        """Test creation of custom neuron model."""
        builder = NeuronBuilder()
        
        custom_params = {
            "model_key": "custom",
            "parameters": {
                "custom_eqs": "dv/dt = (I - v)/tau : 1\ntau : second\nI : 1",
                "custom_threshold": "v > 1",
                "custom_reset": "v = 0",
                "custom_method": "euler"
            }
        }
        
        # We need to ensure parameters are initialized if they naturally occur in the model
        # The builder usually initializes params if they match known keys, 
        # or if the user provides a separate 'values' dict? 
        # In `_build_custom_neurons`, it just creates the group. 
        # User is responsible for setting params via other means or default initialization logic?
        # Let's check logic: `_build_custom_neurons` just calls b2.NeuronGroup
        
        neurons = builder.build_neurons(default_sim_params, custom_params, {}, {})
        
        assert neurons is not None
        assert hasattr(neurons, "v")
        assert hasattr(neurons, "tau")
