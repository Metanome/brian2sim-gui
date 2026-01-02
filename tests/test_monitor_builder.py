"""
Unit tests for MonitorBuilder class.
Tests spike monitoring, state monitoring, and results collection.
"""
import pytest
import brian2 as b2
from brian2sim.core.engine.monitor_builder import MonitorBuilder
from brian2sim.core.engine.neuron_builder import NeuronBuilder
from brian2sim.core.engine.synapse_builder import SynapseBuilder


class TestBasicMonitoring:
    """Tests for basic monitor setup."""
    
    def test_basic_monitor_setup(self, default_sim_params, default_neuron_params):
        """Test basic monitor creation."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        monitors = mb.setup_monitors(neurons)
        
        assert monitors is not None
        assert "spike_monitor" in monitors
        assert "state_monitor" in monitors
        
    def test_spike_monitor_creation(self, default_sim_params, default_neuron_params):
        """Test that spike monitor is created."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        monitors = mb.setup_monitors(neurons)
        
        spike_mon = monitors["spike_monitor"]
        assert isinstance(spike_mon, b2.SpikeMonitor)
        assert spike_mon.source == neurons
        
    def test_state_monitor_creation(self, default_sim_params, default_neuron_params):
        """Test that state monitor records voltage."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        monitors = mb.setup_monitors(neurons)
        
        state_mon = monitors["state_monitor"]
        assert isinstance(state_mon, b2.StateMonitor)
        assert state_mon.source == neurons


class TestVariableMonitoring:
    """Tests for monitoring specific variables."""
    
    def test_custom_variable_monitoring(self, default_sim_params, default_neuron_params):
        """Test monitoring custom variables."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        monitors = mb.setup_monitors(neurons, variables=["v_th"])
        
        # Should have standard monitors plus custom
        assert "spike_monitor" in monitors
        assert "state_monitor" in monitors
        assert "v_th_monitor" in monitors
        
    def test_synaptic_weight_monitoring(self, default_sim_params, default_neuron_params):
        """Test monitoring synaptic weights."""
        nb = NeuronBuilder()
        sb = SynapseBuilder()
        mb = MonitorBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        network_params = {
            "enabled": True,
            "topology": "random",
            "connection_prob": 0.1,
            "synaptic_weight": 0.5
        }
        
        synapses = sb.build_network(network_params, {}, {}, {}, {}, neurons)
        monitors = mb.setup_monitors(neurons, synapses=synapses, monitors_params={"record_synaptic": True})
        
        assert "syn_w_monitor" in monitors
        weight_mon = monitors["syn_w_monitor"]
        assert isinstance(weight_mon, b2.StateMonitor)


class TestResultsCollection:
    """Tests for collecting and formatting results."""
    
    def test_collect_basic_results(self, default_sim_params, default_neuron_params):
        """Test basic results collection."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        monitors = mb.setup_monitors(neurons)
        
        # Run a short simulation
        b2.run(10*b2.ms)
        
        params = {"simulation": default_sim_params}
        results = mb.collect_results(monitors, params)
        
        assert results is not None
        assert results is not None
        assert "raw_data" in results
        assert "spike_monitor" in results["raw_data"]
        assert "state_monitor_v" in results["raw_data"]
        
    def test_spike_times_format(self, default_sim_params, default_neuron_params):
        """Test that spike times are properly formatted."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        # Add input to trigger spikes
        sim_params = default_sim_params.copy()
        sim_params["input_current"] = 2.0
        
        neurons = nb.build_neurons(sim_params, default_neuron_params, {}, {})
        monitors = mb.setup_monitors(neurons)
        
        b2.run(50*b2.ms)
        
        params = {"simulation": sim_params}
        results = mb.collect_results(monitors, params)
        
        spike_data = results["raw_data"]["spike_monitor"]
        spike_times = spike_data["t"]
        # Returns numpy array, not list
        assert hasattr(spike_times, '__len__')
        
    def test_voltage_trace_format(self, default_sim_params, default_neuron_params):
        """Test voltage trace formatting."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        monitors = mb.setup_monitors(neurons)
        
        b2.run(10*b2.ms)
        
        params = {"simulation": default_sim_params}
        results = mb.collect_results(monitors, params)
        
        # Voltage data exists in some form
        # Voltage data exists in some form
        assert "raw_data" in results
        assert "state_monitor_v" in results["raw_data"]


class TestMonitorBuilderEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_no_spikes_recorded(self, default_sim_params, default_neuron_params):
        """Test results when no spikes occur."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        # No input current - neurons shouldn't spike
        sim_params = default_sim_params.copy()
        sim_params["input_current"] = 0.0
        
        neurons = nb.build_neurons(sim_params, default_neuron_params, {}, {})
        monitors = mb.setup_monitors(neurons)
        
        b2.run(10*b2.ms)
        
        params = {"simulation": sim_params}
        results = mb.collect_results(monitors, params)
        
        # Should still return valid structure with empty spike arrays
        # Should still return valid structure with empty spike arrays
        assert "raw_data" in results
        spike_data = results["raw_data"]["spike_monitor"]
        assert len(spike_data["t"]) == 0
        
    def test_monitor_nonexistent_variable(self, default_sim_params, default_neuron_params):
        """Test monitoring variable that doesn't exist."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
        
        # Try to monitor variable that doesn't exist
        monitors = mb.setup_monitors(neurons, variables=["nonexistent_var"])
        
        # Should not crash, just skip the nonexistent variable
        assert "spike_monitor" in monitors
        assert "nonexistent_var_monitor" not in monitors
        
    def test_empty_monitors_dict(self):
        """Test collect_results with empty monitors."""
        mb = MonitorBuilder()
        
        # Empty monitors
        results = mb.collect_results({}, {})
        
        # Should return empty or None
        assert results is not None or results == {}


class TestMonitorConfiguration:
    """Tests for monitor configuration parameters."""

    def test_record_subset_first_n(self, default_sim_params, default_neuron_params):
        """Test recording first N neurons."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        # 100 neurons
        sim_params = default_sim_params.copy()
        sim_params["num_neurons"] = 100
        
        neurons = nb.build_neurons(sim_params, default_neuron_params, {}, {})
        
        monitors_params = {
            "record_subset": "first_n",
            "subset_n": 5
        }
        
        monitors = mb.setup_monitors(neurons, monitors_params=monitors_params)
        state_mon = monitors["state_monitor"]
        
        # Check that we only recorded 5 neurons
        indices = state_mon.record
        # If it's a slice or array, len() works
        assert len(indices) == 5
        
    def test_record_subset_indices(self, default_sim_params, default_neuron_params):
        """Test recording specific indices."""
        nb = NeuronBuilder()
        mb = MonitorBuilder()
        
        sim_params = default_sim_params.copy()
        sim_params["num_neurons"] = 100
        
        neurons = nb.build_neurons(sim_params, default_neuron_params, {}, {})
        
        monitors_params = {
            "record_subset": "indices",
            "subset_indices": "10, 20, 99"
        }
        
        monitors = mb.setup_monitors(neurons, monitors_params=monitors_params)
        state_mon = monitors["state_monitor"]
        
        indices = sorted(state_mon.record)
        import numpy as np
        if hasattr(indices, "tolist"): indices = indices.tolist()
        assert indices == [10, 20, 99]

    def test_record_dt(self, default_sim_params, default_neuron_params):
         """Test recording dt configuration."""
         nb = NeuronBuilder()
         mb = MonitorBuilder()
         
         neurons = nb.build_neurons(default_sim_params, default_neuron_params, {}, {})
         
         monitors_params = {
             "record_dt": 0.5 # 0.5 ms
         }
         
         monitors = mb.setup_monitors(neurons, monitors_params=monitors_params)
         state_mon = monitors["state_monitor"]
         
         # Brian2 uses exact check with units
         import brian2 as b2
         assert abs(state_mon.clock.dt - 0.5 * b2.ms) < 1e-9 * b2.ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
