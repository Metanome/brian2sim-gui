"""
Monitor Builder for Brian2 simulations.
Handles setting up spike monitors, state monitors, and results collection.
"""

from datetime import datetime

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

    def setup_monitors(self, neurons, synapses=None, variables=None, monitors_params=None):
        """Setup monitoring of simulation variables."""
        if not BRIAN2_AVAILABLE:
            return {}
            
        monitors_params = monitors_params or {}
        monitors = {}
        
        # 1. Spike Recording
        if monitors_params.get("record_spikes", True):
            monitors["spike_monitor"] = b2.SpikeMonitor(neurons)

        # 2. Determine Recording Subset (Indices)
        record_subset_mode = monitors_params.get("record_subset", "all")
        n_neurons = len(neurons)
        record_indices = True  # Default to all
        
        if record_subset_mode == "first_n":
            n = min(n_neurons, monitors_params.get("subset_n", 10))
            record_indices = list(range(n))
        elif record_subset_mode == "random_n":
            n = min(n_neurons, monitors_params.get("subset_n", 10))
            if n > 0:
                record_indices = np.random.choice(n_neurons, size=n, replace=False).tolist()
                record_indices.sort()
        elif record_subset_mode == "indices":
            idx_str = monitors_params.get("subset_indices", "0")
            try:
                indices = [int(x.strip()) for x in idx_str.split(",") if x.strip().isdigit()]
                record_indices = [i for i in indices if 0 <= i < n_neurons]
                if not record_indices:
                    record_indices = [0] # Fallback
            except ValueError:
                record_indices = [0] # Fallback
        
        # Recording time step
        rec_dt = monitors_params.get("record_dt", 0.1) * b2.ms

        # 3. Voltage Recording
        if monitors_params.get("record_voltage", True):
            monitors["state_monitor"] = b2.StateMonitor(
                neurons, "v", record=record_indices, dt=rec_dt
            )

        # 4. Additional Variables
        vars_to_record = []
        if variables:
            vars_to_record.extend(variables)
            
        extra_vars_str = monitors_params.get("record_variables", "")
        if extra_vars_str:
            extra_vars = [x.strip() for x in extra_vars_str.split(",") if x.strip()]
            vars_to_record.extend(extra_vars)
            
        # Deduplicate
        vars_to_record = list(set(vars_to_record))
        
        for var in vars_to_record:
            if hasattr(neurons, var):
                monitors[f"{var}_monitor"] = b2.StateMonitor(
                    neurons, var, record=record_indices, dt=rec_dt
                )

        # 5. Synaptic Recording
        if synapses is not None:
             if monitors_params.get("record_synaptic", False):
                 syn_vars_str = monitors_params.get("synaptic_variables", "w")
                 syn_vars = [x.strip() for x in syn_vars_str.split(",") if x.strip()]
                 
                 for var in syn_vars:
                     if hasattr(synapses, var):
                         monitors[f"syn_{var}_monitor"] = b2.StateMonitor(
                             synapses, var, record=True, dt=10 * b2.ms
                         )

        self.monitors = monitors
        return monitors
        
    def collect_results(self, monitors, params):
        """Collect simulation results from monitors."""
        if not monitors:
            return {}

        results = {
            "statistics": {},
            "timestamp": datetime.now().isoformat(),
            "brian2_available": BRIAN2_AVAILABLE,
            "parameters": params,
            "raw_data": {} # New container for generic results
        }
        
        # Iterate over all monitors
        for name, monitor in monitors.items():
            # 1. SpikeMonitor
            if isinstance(monitor, b2.SpikeMonitor):
                # Convert to numpy arrays immediately
                t_data = np.array(monitor.t / b2.ms) # Store logic: Time is always ms
                i_data = np.array(monitor.i)
                
                results["raw_data"][name] = {
                    "type": "spikes",
                    "t": t_data,
                    "i": i_data,
                    "count": monitor.num_spikes
                }

            # 2. StateMonitor
            elif isinstance(monitor, b2.StateMonitor):
                # Get time array (ms)
                t_data = np.array(monitor.t / b2.ms)
                
                for var_name in monitor.record_variables:
                    # Access data: monitor.varname
                    data_attr = getattr(monitor, var_name)
                    
                    # Convert to dimensionless base units (e.g., Volts, Amps)
                    data_values = np.array(data_attr)
                    
                    results["raw_data"][f"{name}_{var_name}"] = {
                        "type": "trace",
                        "t": t_data,
                        "values": data_values, # 2D array [neuron_idx, time]
                        "unit": str(data_attr.unit) if hasattr(data_attr, "unit") else "1",
                        "indices": np.array(monitor.record) if hasattr(monitor, "record") else []
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
