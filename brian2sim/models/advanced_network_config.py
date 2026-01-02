"""
Advanced neuroscience features configuration for Brian2 neural network simulator.
Includes Dale's principle, synaptic delays, STDP, and distance-dependent connectivity.
"""

# ====== DALE'S PRINCIPLE CONFIGURATION ======
DALES_PRINCIPLE_CONFIG = {
    "enabled": {
        "label": "Enable Dale's Principle",
        "type": "bool",
        "default": False,
        "tooltip": "Separate neurons into excitatory and inhibitory populations. "
        "Excitatory neurons (80%) have positive synaptic weights, "
        "inhibitory neurons (20%) have negative weights.",
    },
    "excitatory_ratio": {
        "label": "Excitatory Ratio:",
        "type": "double",
        "default": 0.8,
        "min": 0.1,
        "max": 0.9,
        "step": 0.05,
        "tooltip": "Fraction of neurons that are excitatory. "
        "Cortical networks typically have 80% excitatory, 20% inhibitory neurons.",
    },
    "exc_weight": {
        "label": "Excitatory Weight (nS):",
        "type": "double",
        "default": 1.0,
        "min": 0.01,
        "max": 10.0,
        "step": 0.1,
        "tooltip": "Synaptic weight for excitatory connections. "
        "Typical range: 0.1-5.0 nS for cortical synapses.",
    },
    "inh_weight": {
        "label": "Inhibitory Weight (nS):",
        "type": "double",
        "default": -4.0,
        "min": -20.0,
        "max": -0.1,
        "step": 0.1,
        "tooltip": "Synaptic weight for inhibitory connections (negative). "
        "Typically 3-5x stronger than excitatory weights: -0.5 to -10.0 nS.",
    },
    "exc_reversal": {
        "label": "Excitatory Reversal (mV):",
        "type": "double",
        "default": 0.0,
        "min": -20.0,
        "max": 20.0,
        "step": 1.0,
        "tooltip": "Reversal potential for excitatory synapses. "
        "AMPA/NMDA synapses typically reverse at 0 mV.",
    },
    "inh_reversal": {
        "label": "Inhibitory Reversal (mV):",
        "type": "double",
        "default": -70.0,
        "min": -90.0,
        "max": -50.0,
        "step": 1.0,
        "tooltip": "Reversal potential for inhibitory synapses. "
        "GABA synapses typically reverse at -70 mV (chloride equilibrium).",
    },
}

# ====== SYNAPTIC DELAYS CONFIGURATION ======
SYNAPTIC_DELAYS_CONFIG = {
    "enabled": {
        "label": "Enable Synaptic Delays",
        "type": "bool",
        "default": False,
        "tooltip": "Add realistic time delays to synaptic transmission. "
        "Accounts for axonal conduction and synaptic processing delays.",
    },
    "delay_type": {
        "label": "Delay Distribution:",
        "type": "combo",
        "default": "uniform",
        "options": ["uniform", "normal", "exponential", "distance_dependent"],
        "display_options": ["Uniform", "Normal", "Exponential", "Distance-Dependent"],
        "tooltip": "Type of delay distribution:\n"
        "• Uniform: All delays within a fixed range\n"
        "• Normal: Gaussian distribution around mean\n"
        "• Exponential: Realistic for axonal delays\n"
        "• Distance-dependent: Delays proportional to neuron distance",
    },
    "min_delay": {
        "label": "Minimum Delay (ms):",
        "type": "double",
        "default": 0.5,
        "min": 0.1,
        "max": 10.0,
        "step": 0.1,
        "tooltip": "Minimum synaptic delay. "
        "Cortical synapses: 0.5-1.0 ms minimum for synaptic processing.",
        "depends_on": {"delay_type": "uniform"},
    },
    "max_delay": {
        "label": "Maximum Delay (ms):",
        "type": "double",
        "default": 2.0,
        "min": 0.5,
        "max": 50.0,
        "step": 0.1,
        "tooltip": "Maximum synaptic delay. " "Local circuits: 1-5 ms, long-range: up to 50 ms.",
        "depends_on": {"delay_type": "uniform"},
    },
    "mean_delay": {
        "label": "Mean Delay (ms):",
        "type": "double",
        "default": 1.0,
        "min": 0.1,
        "max": 20.0,
        "step": 0.1,
        "tooltip": "Mean delay for normal/exponential distributions. "
        "Typical cortical delays: 1-3 ms.",
        "depends_on": {"delay_type": ["normal", "exponential"]},
    },
    "delay_std": {
        "label": "Delay Std Dev (ms):",
        "type": "double",
        "default": 0.3,
        "min": 0.1,
        "max": 5.0,
        "step": 0.1,
        "tooltip": "Standard deviation for normal delay distribution. "
        "Typical variability: 0.2-0.5 ms for local circuits.",
        "depends_on": {"delay_type": "normal"},
    },
    "conduction_velocity": {
        "label": "Conduction Velocity (m/s):",
        "type": "double",
        "default": 1.0,
        "min": 0.1,
        "max": 100.0,
        "step": 0.1,
        "tooltip": "Axonal conduction velocity for distance-dependent delays. "
        "Unmyelinated: 0.5-2 m/s, Myelinated: 10-100 m/s, Local: ~1 m/s.",
        "depends_on": {"delay_type": "distance_dependent"},
    },
}

# ====== STDP CONFIGURATION ======
STDP_CONFIG = {
    "enabled": {
        "label": "Enable STDP",
        "type": "bool",
        "default": False,
        "tooltip": "Spike-Timing Dependent Plasticity: synaptic weights change based on "
        "relative timing of pre- and post-synaptic spikes.",
    },
    "stdp_type": {
        "label": "STDP Type:",
        "type": "combo",
        "default": "additive",
        "options": ["additive", "multiplicative", "all_to_all", "nearest_spike"],
        "display_options": ["Additive", "Multiplicative", "All-to-All", "Nearest Spike"],
        "tooltip": "STDP rule type:\n"
        "• Additive: Simple +/- weight changes\n"
        "• Multiplicative: Weight-dependent changes\n"
        "• All-to-all: All spike pairs contribute\n"
        "• Nearest spike: Only nearest pre/post spikes",
    },
    "tau_pre": {
        "label": "Pre-synaptic τ (ms):",
        "type": "double",
        "default": 20.0,
        "min": 1.0,
        "max": 100.0,
        "step": 1.0,
        "tooltip": "Time constant for pre-synaptic trace decay. "
        "Typical range: 10-50 ms, affects LTD window duration.",
    },
    "tau_post": {
        "label": "Post-synaptic τ (ms):",
        "type": "double",
        "default": 20.0,
        "min": 1.0,
        "max": 100.0,
        "step": 1.0,
        "tooltip": "Time constant for post-synaptic trace decay. "
        "Typical range: 10-50 ms, affects LTP window duration.",
    },
    "A_plus": {
        "label": "LTP Amplitude (nS):",
        "type": "double",
        "default": 0.01,
        "min": 0.001,
        "max": 0.1,
        "step": 0.001,
        "tooltip": "Long-Term Potentiation amplitude (pre before post). "
        "Typical range: 0.005-0.02 for additive STDP.",
    },
    "A_minus": {
        "label": "LTD Amplitude (nS):",
        "type": "double",
        "default": 0.0105,
        "min": 0.001,
        "max": 0.1,
        "step": 0.001,
        "tooltip": "Long-Term Depression amplitude (post before pre). "
        "Often slightly larger than LTP (1.05x) to maintain balance.",
    },
    "w_min": {
        "label": "Minimum Weight (nS):",
        "type": "double",
        "default": 0.0,
        "min": -10.0,
        "max": 0.0,
        "step": 0.1,
        "tooltip": "Minimum allowed synaptic weight. "
        "Prevents weights from becoming too negative.",
    },
    "w_max": {
        "label": "Maximum Weight (nS):",
        "type": "double",
        "default": 5.0,
        "min": 1.0,
        "max": 20.0,
        "step": 0.1,
        "tooltip": "Maximum allowed synaptic weight. "
        "Prevents runaway potentiation, typical: 2-10x initial weight.",
    },
}

# ====== STDP TYPE-SPECIFIC DEFAULTS ======
STDP_TYPE_DEFAULTS = {
    "additive": {
        "tau_pre": 20.0,
        "tau_post": 20.0,
        "A_plus": 0.01,
        "A_minus": 0.0105,
        "w_min": 0.0,
        "w_max": 5.0,
    },
    "multiplicative": {
        "tau_pre": 20.0,
        "tau_post": 20.0,
        "A_plus": 0.02,
        "A_minus": 0.021,
        "w_min": 0.0,
        "w_max": 10.0,
    },
    "all_to_all": {
        "tau_pre": 25.0,
        "tau_post": 25.0,
        "A_plus": 0.008,
        "A_minus": 0.0084,
        "w_min": 0.0,
        "w_max": 8.0,
    },
    "nearest_spike": {
        "tau_pre": 15.0,
        "tau_post": 30.0,
        "A_plus": 0.015,
        "A_minus": 0.016,
        "w_min": 0.0,
        "w_max": 6.0,
    },
}

# ====== DISTANCE-DEPENDENT CONNECTIVITY CONFIGURATION ======
DISTANCE_CONNECTIVITY_CONFIG = {
    "enabled": {
        "label": "Enable Distance-Dependent Connectivity",
        "type": "bool",
        "default": False,
        "tooltip": "Connection probability depends on distance between neurons. "
        "Models spatial organization of neural circuits.",
    },
    "spatial_layout": {
        "label": "Spatial Layout:",
        "type": "combo",
        "default": "2d_grid",
        "options": ["1d_line", "2d_grid", "2d_random", "3d_cube", "3d_random"],
        "display_options": ["1D Line", "2D Grid", "2D Random", "3D Cube", "3D Random"],
        "tooltip": "Spatial arrangement of neurons:\n"
        "• 1D Line: Neurons arranged in a line\n"
        "• 2D Grid: Regular grid (cortical columns)\n"
        "• 2D Random: Random 2D positions\n"
        "• 3D Cube: 3D grid arrangement\n"
        "• 3D Random: Random 3D positions",
    },
    "space_scale": {
        "label": "Space Scale (μm):",
        "type": "double",
        "default": 100.0,
        "min": 10.0,
        "max": 10000.0,
        "step": 10.0,
        "tooltip": "Spatial scale of the network in micrometers. "
        "Local circuits: 100-500 μm, Cortical areas: 1000-10000 μm.",
    },
    "connection_function": {
        "label": "Connection Function:",
        "type": "combo",
        "default": "exponential",
        "options": ["exponential", "gaussian", "power_law", "step", "linear"],
        "display_options": ["Exponential", "Gaussian", "Power Law", "Step Function", "Linear"],
        "tooltip": "Distance-connection probability relationship:\n"
        "• Exponential: P ∝ exp(-d/λ) - most common\n"
        "• Gaussian: P ∝ exp(-d²/2σ²) - local connectivity\n"
        "• Power law: P ∝ d^(-α) - scale-free\n"
        "• Step: Constant P within radius\n"
        "• Linear: P decreases linearly with distance",
    },
    "connection_length": {
        "label": "Connection Length (μm):",
        "type": "double",
        "default": 50.0,
        "min": 1.0,
        "max": 1000.0,
        "step": 5.0,
        "tooltip": "Characteristic length scale for connections. "
        "Exponential: λ (decay constant), Gaussian: σ (standard deviation). "
        "Typical: 20-100 μm for local cortical circuits.",
    },
    "max_distance": {
        "label": "Maximum Distance (μm):",
        "type": "double",
        "default": 200.0,
        "min": 10.0,
        "max": 5000.0,
        "step": 10.0,
        "tooltip": "Maximum connection distance. "
        "Connections beyond this distance have zero probability. "
        "Typical: 2-5x connection length.",
    },
    "base_probability": {
        "label": "Base Probability:",
        "type": "double",
        "default": 0.1,
        "min": 0.001,
        "max": 1.0,
        "step": 0.001,
        "tooltip": "Base connection probability (at distance=0). "
        "Scales the overall connectivity level.",
    },
    "power_exponent": {
        "label": "Power Exponent:",
        "type": "double",
        "default": 2.0,
        "min": 0.5,
        "max": 5.0,
        "step": 0.1,
        "tooltip": "Exponent for power-law connectivity (α). "
        "Higher values = more local connectivity. Typical: 1.5-3.0.",
    },
}

# ====== STDP PRESETS ======
STDP_PRESETS = {
    "visual_cortex": {
        "name": "Visual Cortex STDP",
        "description": "STDP parameters from visual cortex experiments (Bi & Poo, 1998)",
        "params": {
            "stdp_type": "additive",
            "tau_pre": 20.0,
            "tau_post": 20.0,
            "A_plus": 0.01,
            "A_minus": 0.0105,
            "w_min": 0.0,
            "w_max": 5.0,
        },
    },
    "hippocampus": {
        "name": "Hippocampus STDP",
        "description": "STDP parameters from hippocampal CA1 (Zhang et al., 1998)",
        "params": {
            "stdp_type": "additive",
            "tau_pre": 16.8,
            "tau_post": 33.7,
            "A_plus": 0.005,
            "A_minus": 0.00525,
            "w_min": 0.0,
            "w_max": 3.0,
        },
    },
    "balanced_network": {
        "name": "Balanced Network STDP",
        "description": "STDP for excitatory-inhibitory balanced networks (Song et al., 2000)",
        "params": {
            "stdp_type": "multiplicative",
            "tau_pre": 20.0,
            "tau_post": 20.0,
            "A_plus": 0.02,
            "A_minus": 0.021,
            "w_min": 0.0,
            "w_max": 10.0,
        },
    },
    "homeostatic": {
        "name": "Homeostatic STDP",
        "description": "STDP with homeostatic scaling (Turrigiano, 2008)",
        "params": {
            "stdp_type": "all_to_all",
            "tau_pre": 25.0,
            "tau_post": 25.0,
            "A_plus": 0.008,
            "A_minus": 0.0084,
            "w_min": 0.0,
            "w_max": 8.0,
        },
    },
}

# ====== DISTANCE CONNECTIVITY PRESETS ======
DISTANCE_CONNECTIVITY_PRESETS = {
    "cortical_column": {
        "name": "Cortical Column",
        "description": "Local connectivity within a cortical column (~300 μm)",
        "params": {
            "spatial_layout": "2d_grid",
            "space_scale": 300.0,
            "connection_function": "exponential",
            "connection_length": 50.0,
            "max_distance": 150.0,
            "base_probability": 0.15,
            "power_exponent": 2.0,
        },
    },
    "local_circuit": {
        "name": "Local Circuit",
        "description": "Local neural circuit with Gaussian connectivity",
        "params": {
            "spatial_layout": "2d_random",
            "space_scale": 500.0,
            "connection_function": "gaussian",
            "connection_length": 75.0,
            "max_distance": 200.0,
            "base_probability": 0.12,
            "power_exponent": 2.0,
        },
    },
    "scale_free_network": {
        "name": "Scale-Free Network",
        "description": "Power-law connectivity with hub neurons",
        "params": {
            "spatial_layout": "2d_random",
            "space_scale": 1000.0,
            "connection_function": "power_law",
            "connection_length": 100.0,
            "max_distance": 500.0,
            "base_probability": 0.08,
            "power_exponent": 2.5,
        },
    },
    "retinal_network": {
        "name": "Retinal Network",
        "description": "Hexagonal grid with local Gaussian connectivity",
        "params": {
            "spatial_layout": "2d_grid",
            "space_scale": 200.0,
            "connection_function": "gaussian",
            "connection_length": 30.0,
            "max_distance": 80.0,
            "base_probability": 0.2,
            "power_exponent": 2.0,
        },
    },
}

# ====== COMBINED CONFIGURATION ======
# Complete advanced network configuration combining all features
ADVANCED_NETWORK_CONFIG = {
    "dales_principle": DALES_PRINCIPLE_CONFIG,
    "synaptic_delays": SYNAPTIC_DELAYS_CONFIG,
    "stdp": STDP_CONFIG,
    "distance_connectivity": DISTANCE_CONNECTIVITY_CONFIG,
}

# All presets combined
ADVANCED_NETWORK_PRESETS = {
    "stdp": STDP_PRESETS,
    "distance_connectivity": DISTANCE_CONNECTIVITY_PRESETS,
}
