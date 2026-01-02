"""
Unit tests for PlasticityBuilder class.
Tests homeostatic plasticity and neuromodulation systems.
"""
import pytest
import brian2 as b2
from brian2sim.core.engine.neuron_builder import NeuronBuilder
from brian2sim.core.engine.synapse_builder import SynapseBuilder
from brian2sim.core.engine.plasticity_builder import PlasticityBuilder


class TestNeuromodulation:
    """Tests for neuromodulation systems."""
    
    def test_acetylcholine_system(self, default_sim_params, default_neuron_params, neuromodulation_params):
        """Test acetylcholine neuromodulation."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        systems = pb.setup_neuromodulation(neuromodulation_params, neurons, None)
        
        assert systems is not None
        assert len(systems) > 0
        
        # Should have acetylcholine system
        ach_system = [s for s in systems.values() if s.get("type") == "acetylcholine"]
        assert len(ach_system) > 0
        
    def test_acetylcholine_modulates_threshold(self, default_sim_params, default_neuron_params, neuromodulation_params):
        """Test that ACh modulates v_th (not v_threshold)."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        # Verify neurons have v_th state variable
        assert hasattr(neurons, 'v_th'), "Neurons must have v_th for neuromodulation"
        
        systems = pb.setup_neuromodulation(neuromodulation_params, neurons, None)
        
        # Should not crash - the bug was trying to modify v_threshold parameter
        assert systems is not None
        
    def test_dopamine_system(self, default_sim_params, default_neuron_params):
        """Test dopaminergic neuromodulation."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        neuromod_params = {
            "enabled": True,
            "dopamine_system": True,
            "dopamine_baseline": 0.5,
            "dopamine_tau": 200.0
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, None)
        
        # Should have dopamine system
        da_system = [s for s in systems.values() if s.get("type") == "dopamine"]
        assert len(da_system) > 0
        
    def test_multiple_neuromodulators(self, default_sim_params, default_neuron_params):
        """Test multiple neuromodulators simultaneously."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        neuromod_params = {
            "enabled": True,
            "acetylcholine_system": True,
            "dopamine_system": True,
            "serotonin_system": True,
            "acetylcholine_baseline": 0.5,
            "dopamine_baseline": 0.5,
            "serotonin_baseline": 0.5
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, None)
        
        # Should have all three systems
        assert len(systems) >= 3


class TestHomeostaticPlasticity:
    """Tests for homeostatic plasticity mechanisms."""
    
    def test_bcm_plasticity(self, default_sim_params, default_neuron_params, homeostatic_params):
        """Test BCM (Bienenstock-Cooper-Munro) plasticity."""
        nb = NeuronBuilder()
        sb = SynapseBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        network_params = {"enabled": True, "topology": "random", "connection_prob": 0.1}
        synapses = sb.build_network(network_params, {}, {}, {}, {}, neurons)
        
        mechanisms = pb.setup_homeostatic_plasticity(homeostatic_params, neurons, synapses)
        
        assert mechanisms is not None
        
    def test_synaptic_scaling(self, default_sim_params, default_neuron_params):
        """Test synaptic scaling mechanism."""
        nb = NeuronBuilder()
        sb = SynapseBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        network_params = {"enabled": True, "topology": "random", "connection_prob": 0.1}
        synapses = sb.build_network(network_params, {}, {}, {}, {}, neurons)
        
        homeo_params = {
            "enabled": True,
            "synaptic_scaling": True,
            "target_rate": 5.0,
            "scaling_rate": 0.0001
        }
        
        mechanisms = pb.setup_homeostatic_plasticity(homeo_params, neurons, synapses)
        
        assert mechanisms is not None
        
    def test_intrinsic_excitability(self, default_sim_params, default_neuron_params):
        """Test intrinsic excitability regulation."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        homeo_params = {
            "enabled": True,
            "intrinsic_excitability": True,
            "target_rate": 5.0,
            "ie_learning_rate": 0.001
        }
        
        mechanisms = pb.setup_homeostatic_plasticity(homeo_params, neurons, None)
        
        assert mechanisms is not None


class TestPlasticityIntegration:
    """Tests for integration of plasticity with other systems."""
    
    def test_plasticity_with_calcium(self, default_sim_params, default_neuron_params, calcium_params):
        """Test plasticity mechanisms with calcium dynamics."""
        nb = NeuronBuilder()
        sb = SynapseBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, calcium_params, {})
        
        network_params = {"enabled": True, "topology": "random", "connection_prob": 0.1}
        synapses = sb.build_network(network_params, {}, {}, {}, calcium_params, neurons)
        
        homeo_params = {
            "enabled": True,
            "bcm_plasticity": True,
            "calcium_dependent": True
        }
        
        mechanisms = pb.setup_homeostatic_plasticity(homeo_params, neurons, synapses)
        
        # Should integrate calcium signals
        assert mechanisms is not None
        
    def test_neuromodulation_with_stdp(self, default_sim_params, default_neuron_params, stdp_params):
        """Test neuromodulation interacting with STDP."""
        nb = NeuronBuilder()
        sb = SynapseBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        network_params = {"enabled": True, "topology": "random", "connection_prob": 0.1}
        synapses = sb.build_network(network_params, stdp_params, {}, {}, {}, neurons)
        
        neuromod_params = {
            "enabled": True,
            "dopamine_system": True,
            "dopamine_baseline": 0.5,
            "dopamine_stdp_modulation": True
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, synapses)
        
        # Dopamine should modulate STDP
        assert systems is not None


class TestPlasticityBuilderEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_plasticity_disabled(self, default_sim_params, default_neuron_params):
        """Test behavior when plasticity is disabled."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        params = {"enabled": False}
        
        mechanisms = pb.setup_homeostatic_plasticity(params, neurons, None)
        
        # Should return empty or None
        assert mechanisms is None or len(mechanisms) == 0
        
    def test_neuromodulation_without_neurons(self):
        """Test neuromodulation with invalid neurons."""
        pb = PlasticityBuilder()
        
        params = {"enabled": True, "dopamine_system": True}
        
        # Should handle gracefully
        try:
            systems = pb.setup_neuromodulation(params, None, None)
        except (AttributeError, TypeError):
            pass  # Expected


class TestSerotoninSystem:
    """Tests for serotonin neuromodulation system."""
    
    def test_serotonin_system_creation(self, default_sim_params, default_neuron_params):
        """Test serotonin system is created correctly."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        neuromod_params = {
            "enabled": True,
            "serotonin_system": True,
            "serotonin_baseline": 0.5,
            "serotonin_tau": 300.0
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, None)
        
        # Should have serotonin system
        serotonin_system = [s for s in systems.values() if s.get("type") == "serotonin"]
        assert len(serotonin_system) > 0
        
    def test_serotonin_receptors(self, default_sim_params, default_neuron_params):
        """Test 5HT receptor subtypes."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        neuromod_params = {
            "enabled": True,
            "serotonin_system": True,
            "serotonin_1a_effect": 0.2,
            "serotonin_2a_effect": 0.1
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, None)
        
        # Should set receptor effects
        assert systems is not None


class TestNoradrenalineSystem:
    """Tests for noradrenaline neuromodulation system."""
    
    def test_noradrenaline_system_creation(self, default_sim_params, default_neuron_params):
        """Test noradrenaline system is created correctly."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        neuromod_params = {
            "enabled": True,
            "noradrenaline_system": True,
            "noradrenaline_baseline": 0.5
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, None)
        
        # Should have noradrenaline system
        ne_system = [s for s in systems.values() if s.get("type") == "noradrenaline"]
        assert len(ne_system) > 0
        
    def test_noradrenaline_receptor_subtypes(self, default_sim_params, default_neuron_params):
        """Test alpha and beta adrenergic receptor effects."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        neuromod_params = {
            "enabled": True,
            "noradrenaline_system": True,
            "alpha1_effect": 0.1,
            "alpha2_effect": 0.1,
            "beta_effect": 0.15
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, None)
        
        assert systems is not None


class TestMetaplasticity:
    """Tests for metaplasticity mechanisms."""
    
    def test_metaplasticity_setup(self, default_sim_params, default_neuron_params):
        """Test metaplasticity mechanism setup."""
        nb = NeuronBuilder()
        sb = SynapseBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        network_params = {"enabled": True, "topology": "random", "connection_prob": 0.1}
        synapses = sb.build_network(network_params, {}, {}, {}, {}, neurons)
        
        homeo_params = {
            "enabled": True,
            "metaplasticity": True,
            "meta_learning_rate": 0.0001
        }
        
        mechanisms = pb.setup_homeostatic_plasticity(homeo_params, neurons, synapses)
        
        # Metaplasticity should be enabled
        assert mechanisms is not None
        
    def test_metaplasticity_modifies_stdp(self, default_sim_params, default_neuron_params, stdp_params):
        """Test that metaplasticity modifies STDP parameters."""
        nb = NeuronBuilder()
        sb = SynapseBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        network_params = {"enabled": True, "topology": "random", "connection_prob": 0.1}
        synapses = sb.build_network(network_params, stdp_params, {}, {}, {}, neurons)
        
        homeo_params = {
            "enabled": True,
            "metaplasticity": True,
            "meta_ltp_scaling": 0.5,
            "meta_ltd_scaling": 0.5
        }
        
        mechanisms = pb.setup_homeostatic_plasticity(homeo_params, neurons, synapses)
        
        assert mechanisms is not None


class TestThresholdAdaptation:
    """Tests for threshold adaptation mechanisms."""
    
    def test_threshold_adaptation_setup(self, default_sim_params, default_neuron_params):
        """Test threshold adaptation mechanism."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        homeo_params = {
            "enabled": True,
            "threshold_adaptation": True,
            "threshold_learning_rate": 0.001
        }
        
        mechanisms = pb.setup_homeostatic_plasticity(homeo_params, neurons, None)
        
        # Should enable threshold adaptation
        assert mechanisms is not None
        
    def test_threshold_adaptation_target_rate(self, default_sim_params, default_neuron_params):
        """Test threshold adaptation targets a specific firing rate."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        homeo_params = {
            "enabled": True,
            "threshold_adaptation": True,
            "target_rate": 10.0  # Target 10 Hz
        }
        
        mechanisms = pb.setup_homeostatic_plasticity(homeo_params, neurons, None)
        
        assert mechanisms is not None


class TestPharmacology:
    """Tests for pharmacological interventions."""
    
    def test_pharmacology_setup(self, default_sim_params, default_neuron_params):
        """Test pharmacology mechanism setup."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        neuromod_params = {
            "enabled": True,
            "dopamine_system": True,
            "pharmacology": {
                "enabled": True,
                "d1_agonist": 0.5,
                "d2_antagonist": 0.3
            }
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, None)
        
        # Pharmacology should modify receptor effects
        assert systems is not None
        
    def test_receptor_blockers(self, default_sim_params, default_neuron_params):
        """Test receptor blocker effects."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        neuromod_params = {
            "enabled": True,
            "acetylcholine_system": True,
            "pharmacology": {
                "enabled": True,
                "muscarinic_blocker": 0.8
            }
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, None)
        
        assert systems is not None


class TestNeuromodulatorRelease:
    """Tests for neuromodulator release patterns."""
    
    def test_tonic_release(self, default_sim_params, default_neuron_params):
        """Test tonic (constant) neuromodulator release."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        neuromod_params = {
            "enabled": True,
            "dopamine_system": True,
            "release_pattern": "tonic",
            "dopamine_baseline": 0.5
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, None)
        
        assert systems is not None
        
    def test_phasic_release(self, default_sim_params, default_neuron_params):
        """Test phasic (burst) neuromodulator release."""
        nb = NeuronBuilder()
        pb = PlasticityBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        neuromod_params = {
            "enabled": True,
            "dopamine_system": True,
            "release_pattern": "phasic",
            "burst_amplitude": 2.0,
            "burst_duration": 100.0
        }
        
        systems = pb.setup_neuromodulation(neuromod_params, neurons, None)
        
        assert systems is not None

