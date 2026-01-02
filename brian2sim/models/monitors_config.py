"""
Monitors configuration for Brian2 neural network simulator.
Defines what data to record during simulation.
"""

MONITORS_CONFIG = {
    # Spike Recording
    "record_spikes": {
        "label": "Record Spikes",
        "type": "bool",
        "default": True,
        "tooltip": "Enable spike time recording using SpikeMonitor.\\n"
        "Essential for raster plots and spike-based analysis.",
    },
    # State Variable Recording
    "record_voltage": {
        "label": "Record Membrane Voltage",
        "type": "bool",
        "default": True,
        "tooltip": "Record membrane potential (v) from neurons.\\n"
        "Required for voltage traces and detailed dynamics analysis.",
    },
    "record_variables": {
        "label": "Additional Variables:",
        "type": "text",
        "default": "",
        "tooltip": "Comma-separated list of additional state variables to record.\\n"
        "Examples: I, w, Ca, g_ampa, u, x\\n"
        "Leave empty to record only voltage.",
    },
    # Recording Subset
    "record_subset": {
        "label": "Record Subset:",
        "type": "combo",
        "default": "all",
        "options": ["all", "first_n", "random_n", "indices"],
        "display_options": ["All Neurons", "First N Neurons", "Random N Neurons", "Specific Indices"],
        "tooltip": "Which neurons to record from:\\n"
        "• All: Record from every neuron (memory intensive)\\n"
        "• First N: Record from first N neurons\\n"
        "• Random N: Record from N random neurons\\n"
        "• Specific: Record from specified indices",
    },
    "subset_n": {
        "label": "Number to Record:",
        "type": "int",
        "default": 10,
        "min": 1,
        "max": 1000,
        "tooltip": "Number of neurons to record when using 'First N' or 'Random N' mode.",
        "depends_on": {"record_subset": ["first_n", "random_n"]},
    },
    "subset_indices": {
        "label": "Neuron Indices:",
        "type": "text",
        "default": "0, 1, 2",
        "tooltip": "Comma-separated list of neuron indices to record.\\n"
        "Example: 0, 10, 50, 99",
        "depends_on": {"record_subset": "indices"},
    },
    # Population Rate
    "record_rate": {
        "label": "Record Population Rate",
        "type": "bool",
        "default": False,
        "tooltip": "Record population firing rate using PopulationRateMonitor.\\n"
        "Useful for analyzing network-level activity dynamics.",
    },
    "rate_bin_size": {
        "label": "Rate Bin Size (ms):",
        "type": "double",
        "default": 10.0,
        "min": 0.1,
        "max": 100.0,
        "step": 1.0,
        "decimals": 1,
        "tooltip": "Time bin size for rate calculation (implicit in PopulationRateMonitor).\\n"
        "Smaller bins = higher temporal resolution but noisier.",
        "depends_on": {"record_rate": True},
    },
    # Recording Interval
    "record_dt": {
        "label": "Recording Interval (ms):",
        "type": "double",
        "default": 0.1,
        "min": 0.01,
        "max": 10.0,
        "step": 0.1,
        "decimals": 2,
        "tooltip": "Time interval between state variable recordings.\\n"
        "Larger values reduce memory usage but lower temporal resolution.\\n"
        "Default matches simulation dt for full resolution.",
    },
    # Synaptic Recording
    "record_synaptic": {
        "label": "Record Synaptic Variables",
        "type": "bool",
        "default": False,
        "tooltip": "Record synaptic state variables (weights, conductances).\\n"
        "Warning: Can use significant memory for large networks.",
    },
    "synaptic_variables": {
        "label": "Synaptic Variables:",
        "type": "text",
        "default": "w",
        "tooltip": "Comma-separated synaptic variables to record.\\n"
        "Examples: w, g, x, u (for STP)",
        "depends_on": {"record_synaptic": True},
    },
}
