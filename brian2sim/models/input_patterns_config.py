"""
Input patterns configuration for Brian2 neural network simulator.
Defines various types of input stimulation patterns based on 2025 research standards.
"""

INPUT_PATTERNS_CONFIG = {
    "enabled": {
        "label": "Enable Input Patterns",
        "type": "bool",
        "default": False,
        "tooltip": "Enable external input patterns beyond constant current injection. Essential for realistic neural network simulations.",
    },
    "pattern_type": {
        "label": "Input Pattern Type:",
        "type": "combo",
        "default": "poisson",
        "options": ["poisson", "rhythmic", "burst", "step", "timed_array", "spike_generator"],
        "display_options": [
            "Poisson Spike Trains",
            "Rhythmic Oscillations",
            "Burst Stimulation",
            "Step Current",
            "Timed Array (Variable)",
            "Spike Generator (Precise)",
        ],
        "tooltip": "Type of input stimulation pattern:\n"
        "• Poisson: Random spike trains (most physiological)\n"
        "• Rhythmic: Oscillatory inputs (alpha, beta, gamma rhythms)\n"
        "• Burst: Brief high-frequency stimulation\n"
        "• Step: Step current changes\n"
        "• Timed Array: Arbitrary time-varying current\n"
        "• Spike Generator: Precise spike times",
        "depends_on": {"enabled": True},
    },
    # Poisson Spike Train Parameters
    "poisson_rate": {
        "label": "Poisson Rate (Hz):",
        "type": "double",
        "default": 10.0,
        "min": 0.1,
        "max": 500.0,
        "step": 0.5,
        "decimals": 1,
        "tooltip": "Firing rate of Poisson spike trains in Hz.\n"
        "Physiological ranges:\n"
        "• Spontaneous activity: 0.1-5 Hz\n"
        "• Sensory input: 5-50 Hz\n"
        "• Strong stimulation: 50-200 Hz\n"
        "• Maximum rates: up to 500 Hz",
        "depends_on": {"enabled": True, "pattern_type": "poisson"},
    },
    "poisson_weight": {
        "label": "Synaptic Weight (nS):",
        "type": "double",
        "default": 0.5,
        "min": 0.01,
        "max": 10.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Strength of synaptic connections from Poisson inputs.\n"
        "Typical values:\n"
        "• Weak inputs: 0.01-0.1 nS\n"
        "• Moderate inputs: 0.1-1.0 nS\n"
        "• Strong inputs: 1.0-10.0 nS",
        "depends_on": {"enabled": True, "pattern_type": "poisson"},
    },
    "poisson_num_sources": {
        "label": "Number of Input Sources:",
        "type": "int",
        "default": 50,
        "min": 1,
        "max": 1000,
        "tooltip": "Number of independent Poisson spike generators.\n"
        "More sources = more realistic convergent input.\n"
        "Typical cortical neurons receive 1000-10000 inputs.",
        "depends_on": {"enabled": True, "pattern_type": "poisson"},
    },
    # Rhythmic Input Parameters
    "rhythmic_frequency": {
        "label": "Oscillation Frequency (Hz):",
        "type": "double",
        "default": 10.0,
        "min": 0.5,
        "max": 100.0,
        "step": 0.5,
        "decimals": 1,
        "tooltip": "Frequency of rhythmic oscillations.\n"
        "Brain rhythm frequencies (2025 research):\n"
        "• Delta: 0.5-4 Hz (sleep, anesthesia)\n"
        "• Theta: 4-8 Hz (hippocampus, memory)\n"
        "• Alpha: 8-12 Hz (relaxed wakefulness)\n"
        "• Beta: 12-30 Hz (motor cortex, attention)\n"
        "• Gamma: 30-100 Hz (binding, consciousness)",
        "depends_on": {"enabled": True, "pattern_type": "rhythmic"},
    },
    "rhythmic_amplitude": {
        "label": "Oscillation Amplitude (nA):",
        "type": "double",
        "default": 0.2,
        "min": 0.01,
        "max": 2.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Amplitude of rhythmic current modulation.",
        "depends_on": {"enabled": True, "pattern_type": "rhythmic"},
    },
    "rhythmic_phase": {
        "label": "Phase Offset (degrees):",
        "type": "double",
        "default": 0.0,
        "min": 0.0,
        "max": 360.0,
        "step": 1.0,
        "decimals": 1,
        "tooltip": "Phase offset for rhythmic inputs (0-360 degrees).",
        "depends_on": {"enabled": True, "pattern_type": "rhythmic"},
    },
    # Burst Stimulation Parameters
    "burst_frequency": {
        "label": "Burst Frequency (Hz):",
        "type": "double",
        "default": 100.0,
        "min": 10.0,
        "max": 1000.0,
        "step": 10.0,
        "decimals": 1,
        "tooltip": "Frequency of spikes within each burst.\n"
        "High-frequency stimulation ranges:\n"
        "• Low: 10-50 Hz\n"
        "• Moderate: 50-200 Hz\n"
        "• High: 200-1000 Hz",
        "depends_on": {"enabled": True, "pattern_type": "burst"},
    },
    "burst_duration": {
        "label": "Burst Duration (ms):",
        "type": "double",
        "default": 10.0,
        "min": 1.0,
        "max": 100.0,
        "step": 1.0,
        "decimals": 1,
        "tooltip": "Duration of each burst in milliseconds.",
        "depends_on": {"enabled": True, "pattern_type": "burst"},
    },
    "burst_interval": {
        "label": "Inter-burst Interval (ms):",
        "type": "double",
        "default": 100.0,
        "min": 10.0,
        "max": 1000.0,
        "step": 10.0,
        "decimals": 1,
        "tooltip": "Time between burst onsets.",
        "depends_on": {"enabled": True, "pattern_type": "burst"},
    },
    # Step Current Parameters
    "step_levels": {
        "label": "Current Levels (nA):",
        "type": "str",
        "default": "0.0, 0.5, 1.0, 0.0",
        "tooltip": "Comma-separated list of current levels in nA.\n"
        "Example: '0.0, 0.5, 1.0, 0.0' creates a step protocol.",
        "depends_on": {"enabled": True, "pattern_type": "step"},
    },
    "step_durations": {
        "label": "Step Durations (ms):",
        "type": "str",
        "default": "100, 200, 200, 100",
        "tooltip": "Comma-separated list of step durations in ms.\n"
        "Must match the number of current levels.",
        "depends_on": {"enabled": True, "pattern_type": "step"},
    },
    # Timed Array Parameters
    "timed_values": {
        "label": "Time-Varying Values (nA):",
        "type": "text",
        "default": "0, 0.2, 0.5, 0.2, 0",
        "tooltip": "Comma-separated list of current values at each time step.",
        "depends_on": {"enabled": True, "pattern_type": "timed_array"},
    },
    "timed_dt": {
        "label": "Time Step (ms):",
        "type": "double",
        "default": 1.0,
        "min": 0.01,
        "max": 100.0,
        "step": 0.1,
        "decimals": 2,
        "tooltip": "Time step size for the timed array values.",
        "depends_on": {"enabled": True, "pattern_type": "timed_array"},
    },
    "timed_array_file_path": {
        "label": "Load from File:",
        "type": "file",
        "default": "",
        "filter": "Data Files (*.npy *.csv *.txt);;All Files (*)",
        "tooltip": "Load time-varying signal from file (overrides text input).\nFormats:\n• .npy: 1D or 2D array\n• .csv: Single column or multiple columns",
        "depends_on": {"enabled": True, "pattern_type": "timed_array"},
    },
    # Spike Generator Parameters
    "spike_indices": {
        "label": "Spike Indices:",
        "type": "text",
        "default": "0, 0, 1, 2",
        "tooltip": "Comma-separated list of neuron indices that spike.",
        "depends_on": {"enabled": True, "pattern_type": "spike_generator"},
    },
    "spike_times": {
        "label": "Spike Times (ms):",
        "type": "text",
        "default": "10, 20, 15, 30",
        "tooltip": "Comma-separated list of spike times (must match indices length).",
        "depends_on": {"enabled": True, "pattern_type": "spike_generator"},
    },
    "spike_file_path": {
        "label": "Load from File:",
        "type": "file",
        "default": "",
        "filter": "Data Files (*.npy *.csv *.txt);;All Files (*)",
        "tooltip": "Load spikes from file (overrides text input).\nFormats:\n• .npy: Dict {'indices':[], 'times':[]} or array\n• .csv: Columns 'index', 'time'",
        "depends_on": {"enabled": True, "pattern_type": "spike_generator"},
    },
}
