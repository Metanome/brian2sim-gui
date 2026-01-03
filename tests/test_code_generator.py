import pytest
import os
from brian2sim.core.code_generator import CodeGenerator

class TestCodeGenerator:
    """Test CodeGenerator class features."""
    
    @pytest.fixture
    def generator(self):
        return CodeGenerator()

    def test_neuron_code_has_gap_junction_support(self, generator):
        """Test that generated neuron code includes I_gap."""
        sim_params = {"num_neurons": 10}
        neuron_params = {"model_key": "lif", "parameters": {"tau_m": 20}}
        
        lines = generator._generate_neuron_code(sim_params, neuron_params)
        code = "\n".join(lines)
        
        assert "I_gap : amp" in code
        assert "I + I_gap" in code
        assert "neurons.I_gap = 0 * amp" in code

    def test_gap_junctions_code(self, generator):
        """Test gap junction code generation."""
        params = {
            "gap_junctions": {
                "enabled": True,
                "conductance": 0.5,
                "junction_type": "symmetric",
                "spatial_organization": "random"
            }
        }
        
        lines = generator._generate_gap_junctions_code(params)
        code = "\n".join(lines)
        
        assert "gap_junctions = Synapses" in code
        assert "g_gap : siemens" in code
        assert "gap_junctions.g_gap = g_gap_conductance" in code
        assert "g_gap_conductance = 0.5 * nS" in code

    def test_synapses_code_simple(self, generator):
        """Test simple synapse generation."""
        network_params = {"weight": 0.5}
        # Empty advanced params
        lines = generator._generate_synapses_code(network_params, {}, {}, {}, {}, {})
        code = "\n".join(lines)
        
        assert "synapses = Synapses" in code
        assert "w : siemens" in code
        # Should not have complex parts
        assert "g_ampa" not in code
        
    def test_synapses_code_advanced(self, generator):
        """Test advanced synapses (Receptors + STP)."""
        network_params = {"weight": 0.5}
        receptors = {
            "enabled": True,
            "ampa_enabled": True,
            "nmda_enabled": True
        }
        stp = {
            "enabled": True,
            "tm_U": 0.2
        }
        
        lines = generator._generate_synapses_code(network_params, {}, receptors, stp, {}, {})
        code = "\n".join(lines)
        
        # Check Receptors
        assert "dg_ampa/dt" in code
        assert "I_ampa" in code
        assert "B_mg" in code # NMDA
        assert "I_syn = I_ampa + I_nmda" in code
        
        # Check STP
        assert "dx/dt" in code
        assert "u += U_stp" in code
        assert "w * r *" in code # Modulation check

    def test_plasticity_code(self, generator):
        """Test plasticity code generation."""
        homeo = {
            "enabled": True,
            "activity_detection": True,
            "synaptic_scaling": True
        }
        
        lines = generator._generate_plasticity_code(homeo, {})
        code = "\n".join(lines)
        
        assert "neurons.run_regularly" in code
        assert "activity = activity" in code
        assert "synapses.run_regularly" in code
        assert "scaling_factor" in code

    def test_multicompartment_fallback(self, generator):
        """Test multicompartment generation returns fallback."""
        multi = {"enabled": True}
        sim = {"num_neurons": 10}
        neuron = {"model_key": "lif"}
        
        lines = generator._generate_multicompartment_code(sim, multi, neuron, {})
        code = "\n".join(lines)
        
        assert "Fallback" in code
        assert "NeuronGroup" in code # Point neuron generated
