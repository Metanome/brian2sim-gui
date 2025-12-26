"""
Monitor Builder for Brian2 simulations.
Handles setting up spike monitors, state monitors, and results collection.
"""

try:
    import brian2 as b2
    import numpy as np

    BRIAN2_AVAILABLE = True
except ImportError:
    BRIAN2_AVAILABLE = False
    import numpy as np


class MonitorBuilder:
    """Builder class for constructing simulation monitors."""

    def __init__(self):
        self.monitors = {}

    def setup_monitors(self, neurons, synapses=None, variables=None):
        """Setup monitoring of simulation variables."""
        if not BRIAN2_AVAILABLE:
            return {}

        monitors = {}

        # Spike monitor
        monitors["spike_monitor"] = b2.SpikeMonitor(neurons)

        # State monitor for voltage
        monitors["state_monitor"] = b2.StateMonitor(neurons, "v", record=True)

        # Monitor additional variables if specified
        if variables:
            for var in variables:
                if hasattr(neurons, var):
                    monitors[f"{var}_monitor"] = b2.StateMonitor(neurons, var, record=True)

        # Monitor synaptic weights if synapses exist
        if synapses is not None and hasattr(synapses, "w"):
            monitors["weight_monitor"] = b2.StateMonitor(synapses, "w", record=True, dt=10 * b2.ms)

        self.monitors = monitors
        return monitors

    def collect_results(self, monitors, params):
        """Collect simulation results from monitors."""
        if not monitors:
            return {}

        results = {
            "spike_times": {},
            "spike_indices": [],
            "voltage_traces": {},
            "time": None,
            "statistics": {},
        }

        # Get spike data
        if "spike_monitor" in monitors:
            spike_mon = monitors["spike_monitor"]
            results["spike_times"] = {
                i: np.array(spike_mon.t[spike_mon.i == i] / b2.ms)
                for i in range(len(np.unique(spike_mon.i)))
            }
            results["spike_indices"] = np.array(spike_mon.i)
            results["all_spike_times"] = np.array(spike_mon.t / b2.ms)

        # Get voltage traces
        if "state_monitor" in monitors:
            state_mon = monitors["state_monitor"]
            results["time"] = np.array(state_mon.t / b2.ms)
            results["voltage_traces"] = {
                i: np.array(state_mon.v[i] / b2.mV)
                for i in range(min(10, len(state_mon.v)))  # Limit to first 10 neurons
            }

        # Calculate statistics
        results["statistics"] = self._calculate_statistics(monitors, params)

        return results

    def _calculate_statistics(self, monitors, params):
        """Calculate simulation statistics."""
        stats = {}

        if "spike_monitor" in monitors:
            spike_mon = monitors["spike_monitor"]
            sim_time = (
                params.get("simulation", {}).get("sim_time", 100) / 1000
            )  # Convert to seconds
            num_neurons = params.get("simulation", {}).get("num_neurons", 1)

            total_spikes = len(spike_mon.i)
            stats["total_spikes"] = total_spikes
            stats["mean_firing_rate"] = (
                total_spikes / (sim_time * num_neurons) if sim_time > 0 else 0
            )

            # Per-neuron firing rates
            unique_neurons = np.unique(spike_mon.i)
            firing_rates = []
            for neuron_id in unique_neurons:
                neuron_spikes = np.sum(spike_mon.i == neuron_id)
                firing_rates.append(neuron_spikes / sim_time)

            if firing_rates:
                stats["min_firing_rate"] = min(firing_rates)
                stats["max_firing_rate"] = max(firing_rates)
                stats["std_firing_rate"] = np.std(firing_rates)
            else:
                stats["min_firing_rate"] = 0
                stats["max_firing_rate"] = 0
                stats["std_firing_rate"] = 0

        return stats
