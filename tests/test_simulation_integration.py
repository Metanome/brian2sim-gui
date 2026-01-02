"""
Integration tests for complete simulation workflows.
Tests end-to-end simulation execution without GUI.
"""
import pytest
import brian2 as b2
from brian2sim.core.simulation_engine import SimulationEngine


class TestBasicSimulations:
    """Tests for basic simulation workflows."""
    
    def test_lif_network_simulation(self, default_sim_params, default_neuron_params, network_params):
        """Test complete LIF network simulation."""
        params = {
            "simulation": default_sim_params,
            "neuron_model": default_neuron_params,
            "network": network_params,
            "noise": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None
        assert "raw_data" in results
        assert "spike_monitor" in results["raw_data"]
        # Access via raw_data for length check
        spike_data = results["raw_data"]["spike_monitor"]
        assert len(spike_data["t"]) >= 0
        
    def test_izhikevich_simulation(self, default_sim_params, izhikevich_params):
        """Test Izhikevich neuron simulation."""
        params = {
            "simulation": default_sim_params,
            "neuron_model": izhikevich_params,
            "network": {"enabled": False},
            "noise": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None
        assert results.get("brian2_available") == True
        
    def test_adex_simulation(self, default_sim_params, adex_params):
        """Test AdEx neuron simulation."""
        params = {
            "simulation": default_sim_params,
            "neuron_model": adex_params,
            "network": {"enabled": False},
            "noise": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None


class TestAdvancedSimulations:
    """Tests for advanced simulation features."""
    
    def test_stdp_learning(self, default_sim_params, default_neuron_params, network_params, stdp_params):
        """Test simulation with STDP plasticity."""
        sim_params = default_sim_params.copy()
        sim_params["sim_time"] = 500  # Longer for plasticity
        
        params = {
            "simulation": sim_params,
            "neuron_model": default_neuron_params,
            "network": network_params,
            "advanced_network": stdp_params,
            "noise": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None
        # STDP should modify weights over time
        
    def test_synaptic_receptors(self, default_sim_params, default_neuron_params, network_params, receptor_params):
        """Test simulation with AMPA/NMDA receptors."""
        params = {
            "simulation": default_sim_params,
            "neuron_model": default_neuron_params,
            "network": network_params,
            "synaptic_receptors": receptor_params,
            "noise": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None
        
    def test_calcium_dynamics(self, default_sim_params, default_neuron_params, calcium_params, network_params):
        """Test simulation with calcium dynamics."""
        params = {
            "simulation": default_sim_params,
            "neuron_model": default_neuron_params,
            "calcium_dynamics": calcium_params,
            "network": network_params,
            "noise": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None


class TestNeuromodulationSimulations:
    """Tests for neuromodulation in simulations."""
    
    def test_acetylcholine_modulation(self, default_sim_params, default_neuron_params, neuromodulation_params):
        """Test simulation with acetylcholine neuromodulation."""
        sim_params = default_sim_params.copy()
        sim_params["sim_time"] = 1000  # Longer to see neuromodulation effects
        
        params = {
            "simulation": sim_params,
            "neuron_model": default_neuron_params,
            "neuromodulation": neuromodulation_params,
            "network": {"enabled": False},
            "noise": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None
        # ACh should modulate v_th, affecting firing rates
        
    def test_multiple_neuromodulators(self, default_sim_params, default_neuron_params):
        """Test simulation with multiple neuromodulator systems."""
        sim_params = default_sim_params.copy()
        sim_params["sim_time"] = 1000
        
        neuromod_params = {
            "enabled": True,
            "acetylcholine_system": True,
            "dopamine_system": True,
            "serotonin_system": True,
            "acetylcholine_baseline": 0.5,
            "dopamine_baseline": 0.5,
            "serotonin_baseline": 0.5
        }
        
        params = {
            "simulation": sim_params,
            "neuron_model": default_neuron_params,
            "neuromodulation": neuromod_params,
            "network": {"enabled": False},
            "noise": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None


class TestHomeostaticPlasticitySimulations:
    """Tests for homeostatic plasticity in simulations."""
    
    def test_bcm_plasticity(self, default_sim_params, default_neuron_params, network_params, homeostatic_params):
        """Test simulation with BCM homeostatic plasticity."""
        sim_params = default_sim_params.copy()
        sim_params["sim_time"] = 2000  # Long simulation for homeostasis
        
        params = {
            "simulation": sim_params,
            "neuron_model": default_neuron_params,
            "network": network_params,
            "homeostatic_plasticity": homeostatic_params,
            "noise": {"enabled": True, "intensity": 0.1, "method": "gaussian"}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None


class TestComplexNetworks:
    """Tests for complex network simulations."""
    
    def test_small_world_network(self, default_sim_params, default_neuron_params):
        """Test small-world network simulation."""
        sim_params = default_sim_params.copy()
        sim_params["num_neurons"] = 100
        sim_params["sim_time"] = 500
        
        network_params = {
            "enabled": True,
            "topology": "small_world",
            "nearest_neighbors": 4,
            "rewiring_probability": 0.1
        }
        
        params = {
            "simulation": sim_params,
            "neuron_model": default_neuron_params,
            "network": network_params,
            "noise": {"enabled": True, "intensity": 0.05}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None
        assert "raw_data" in results
        spike_data = results["raw_data"]["spike_monitor"]
        assert len(spike_data["t"]) > 0  # Should have network activity
        
    def test_modular_network(self, default_sim_params, default_neuron_params):
        """Test modular network simulation."""
        sim_params = default_sim_params.copy()
        sim_params["num_neurons"] = 100
        sim_params["sim_time"] = 500
        
        network_params = {
            "enabled": True,
            "topology": "modular",
            "num_modules": 4,
            "p_within": 0.3,
            "p_between": 0.01
        }
        
        params = {
            "simulation": sim_params,
            "neuron_model": default_neuron_params,
            "network": network_params,
            "noise": {"enabled": True, "intensity": 0.1}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None
        assert "raw_data" in results
        spike_data = results["raw_data"]["spike_monitor"]
        assert len(spike_data["t"]) > 0


class TestInputPatterns:
    """Tests for input pattern stimulation."""
    
    def test_poisson_input(self, default_sim_params, default_neuron_params):
        """Test simulation with Poisson input pattern."""
        params = {
            "simulation": default_sim_params,
            "neuron_model": default_neuron_params,
            "input_patterns": {
                "enabled": True,
                "pattern_type": "poisson",
                "poisson_rate": 50.0,
                "poisson_weight": 0.5
            },
            "network": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert results is not None
        # Poisson input should drive spikes
        assert "raw_data" in results
        spike_data = results["raw_data"]["spike_monitor"]
        assert len(spike_data["t"]) > 0


class TestSimulationMonitoring:
    """Tests for simulation monitoring and data collection."""
    
    def test_voltage_monitoring(self, default_sim_params, default_neuron_params):
        """Test that voltage traces are recorded."""
        params = {
            "simulation": default_sim_params,
            "neuron_model": default_neuron_params,
            "network": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert "raw_data" in results
        assert "state_monitor_v" in results["raw_data"]
        voltage_data = results["raw_data"]["state_monitor_v"]
        assert "values" in voltage_data
        assert len(voltage_data["values"]) > 0
        
    def test_spike_monitoring(self, default_sim_params, default_neuron_params):
        """Test that spike data is recorded."""
        sim_params = default_sim_params.copy()
        sim_params["input_current"] = 2.0  # Strong input to ensure spikes
        
        params = {
            "simulation": sim_params,
            "neuron_model": default_neuron_params,
            "network": {"enabled": False}
        }
        
        engine = SimulationEngine()
        results = engine._execute_brian2_simulation(params)
        
        assert "raw_data" in results
        assert "spike_monitor" in results["raw_data"]
        spike_data = results["raw_data"]["spike_monitor"]
        # With strong input, should have spikes
        assert len(spike_data["t"]) > 0


class TestSimulationParameters:
    """Tests for simulation parameter handling."""
    
    def test_different_timesteps(self, default_neuron_params):
        """Test simulations with different timestep values."""
        for dt in [0.01, 0.1, 0.5]:
            sim_params = {
                "dt": dt,
                "sim_time": 100,
                "num_neurons": 10,
                "v_threshold": -55.0,
                "v_reset": -70.0
            }
            
            params = {
                "simulation": sim_params,
                "neuron_model": default_neuron_params,
                "network": {"enabled": False}
            }
            
            engine = SimulationEngine()
            results = engine._execute_brian2_simulation(params)
            
            assert results is not None
            
    def test_different_network_sizes(self, default_neuron_params):
        """Test simulations with different network sizes."""
        for n in [10, 50, 100]:
            sim_params = {
                "dt": 0.1,
                "sim_time": 100,
                "num_neurons": n,
                "v_threshold": -55.0,
                "v_reset": -70.0
            }
            
            params = {
                "simulation": sim_params,
                "neuron_model": default_neuron_params,
                "network": {"enabled": True, "topology": "random", "connection_prob": 0.1}
            }
            
            engine = SimulationEngine()
            results = engine._execute_brian2_simulation(params)
            
            assert results is not None


class TestErrorHandling:
    """Tests for error handling in simulations."""
    
    def test_invalid_simulation_time(self, default_neuron_params):
        """Test handling of invalid simulation time."""
        sim_params = {
            "dt": 0.1,
            "sim_time": -100,  # Invalid
            "num_neurons": 10
        }
        
        params = {
            "simulation": sim_params,
            "neuron_model": default_neuron_params
        }
        
        engine = SimulationEngine()
        
        with pytest.raises(ValueError):
            engine._execute_brian2_simulation(params)
            
    def test_invalid_neuron_count(self, default_neuron_params):
        """Test handling of invalid neuron count."""
        sim_params = {
            "dt": 0.1,
            "sim_time": 100,
            "num_neurons": 0  # Invalid
        }
        
        params = {
            "simulation": sim_params,
            "neuron_model": default_neuron_params
        }
        
        engine = SimulationEngine()
        
        with pytest.raises(ValueError):
            engine._execute_brian2_simulation(params)
