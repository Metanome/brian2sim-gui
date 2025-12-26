"""
Short-term plasticity configuration for Brian2 neural network simulator.
Implements synaptic facilitation and depression based on 2025 research standards.
"""

SHORT_TERM_PLASTICITY_CONFIG = {
    "enabled": {
        "label": "Enable Short-Term Plasticity",
        "type": "bool",
        "default": False,
        "tooltip": "Enable short-term synaptic plasticity (facilitation and depression).\n"
        "Essential for realistic synaptic dynamics and temporal processing.",
    },
    "plasticity_type": {
        "label": "Plasticity Type:",
        "type": "combo",
        "default": "tsodyks_markram",
        "options": ["tsodyks_markram", "simple_facilitation", "simple_depression"],
        "display_options": ["Tsodyks-Markram Model", "Simple Facilitation", "Simple Depression"],
        "tooltip": "Type of short-term plasticity model:\n"
        "• Tsodyks-Markram: Complete model with facilitation and depression\n"
        "• Simple Facilitation: Activity-dependent enhancement\n"
        "• Simple Depression: Activity-dependent reduction",
        "depends_on": {"enabled": True},
    },
    # Tsodyks-Markram Model Parameters (Tsodyks & Markram 1997, 2025 updates)
    "tm_U": {
        "label": "Utilization Factor (U):",
        "type": "double",
        "default": 0.5,
        "min": 0.01,
        "max": 1.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Baseline release probability (utilization factor).\n"
        "Research ranges (2025):\n"
        "• Facilitating synapses: 0.1-0.3\n"
        "• Depressing synapses: 0.4-0.8\n"
        "• Mixed synapses: 0.3-0.6",
        "depends_on": {"plasticity_type": "tsodyks_markram"},
    },
    "tm_tau_d": {
        "label": "Depression Time Constant (ms):",
        "type": "double",
        "default": 800.0,
        "min": 50.0,
        "max": 5000.0,
        "step": 50.0,
        "decimals": 1,
        "tooltip": "Time constant for recovery from depression.\n"
        "Research ranges:\n"
        "• Fast recovery: 50-200ms\n"
        "• Slow recovery: 500-2000ms\n"
        "• Very slow: 2000-5000ms",
        "depends_on": {"plasticity_type": "tsodyks_markram"},
    },
    "tm_tau_f": {
        "label": "Facilitation Time Constant (ms):",
        "type": "double",
        "default": 50.0,
        "min": 10.0,
        "max": 1000.0,
        "step": 10.0,
        "decimals": 1,
        "tooltip": "Time constant for facilitation decay.\n"
        "Research ranges:\n"
        "• Fast facilitation: 10-50ms\n"
        "• Slow facilitation: 100-500ms\n"
        "• Very slow: 500-1000ms",
        "depends_on": {"plasticity_type": "tsodyks_markram"},
    },
    # Simple Facilitation Parameters
    "fac_tau": {
        "label": "Facilitation Decay (ms):",
        "type": "double",
        "default": 100.0,
        "min": 10.0,
        "max": 1000.0,
        "step": 10.0,
        "decimals": 1,
        "tooltip": "Time constant for facilitation decay.",
        "depends_on": {"plasticity_type": "simple_facilitation"},
    },
    "fac_increment": {
        "label": "Facilitation Increment:",
        "type": "double",
        "default": 0.1,
        "min": 0.01,
        "max": 2.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Amount of facilitation per spike.\n"
        "Multiplicative factor added to synaptic strength.",
        "depends_on": {"plasticity_type": "simple_facilitation"},
    },
    "fac_max": {
        "label": "Maximum Facilitation:",
        "type": "double",
        "default": 3.0,
        "min": 1.0,
        "max": 10.0,
        "step": 0.1,
        "decimals": 1,
        "tooltip": "Maximum facilitation factor.\n" "Prevents runaway facilitation.",
        "depends_on": {"plasticity_type": "simple_facilitation"},
    },
    # Simple Depression Parameters
    "dep_tau": {
        "label": "Depression Recovery (ms):",
        "type": "double",
        "default": 500.0,
        "min": 50.0,
        "max": 5000.0,
        "step": 50.0,
        "decimals": 1,
        "tooltip": "Time constant for recovery from depression.",
        "depends_on": {"plasticity_type": "simple_depression"},
    },
    "dep_factor": {
        "label": "Depression Factor:",
        "type": "double",
        "default": 0.8,
        "min": 0.1,
        "max": 0.99,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Multiplicative depression factor per spike.\n"
        "Closer to 1.0 = less depression.",
        "depends_on": {"plasticity_type": "simple_depression"},
    },
    "dep_min": {
        "label": "Minimum Depression:",
        "type": "double",
        "default": 0.1,
        "min": 0.01,
        "max": 0.9,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Minimum synaptic strength during depression.\n"
        "Prevents complete synaptic silencing.",
        "depends_on": {"plasticity_type": "simple_depression"},
    },
    # Synapse Type Specificity
    "excitatory_plasticity": {
        "label": "Apply to Excitatory Synapses",
        "type": "bool",
        "default": True,
        "tooltip": "Apply short-term plasticity to excitatory synapses.\n"
        "Commonly observed in cortical excitatory connections.",
        "depends_on": {"enabled": True},
    },
    "inhibitory_plasticity": {
        "label": "Apply to Inhibitory Synapses",
        "type": "bool",
        "default": False,
        "tooltip": "Apply short-term plasticity to inhibitory synapses.\n"
        "Less common but important for certain interneuron types.",
        "depends_on": {"enabled": True},
    },
    # Advanced Parameters
    "calcium_dependence": {
        "label": "Calcium-Dependent Release",
        "type": "bool",
        "default": False,
        "tooltip": "Include calcium-dependent vesicle release probability.\n"
        "More realistic but computationally intensive.",
        "depends_on": {"enabled": True},
    },
    "vesicle_pool_size": {
        "label": "Vesicle Pool Size:",
        "type": "int",
        "default": 100,
        "min": 10,
        "max": 1000,
        "tooltip": "Number of vesicles in readily releasable pool.\n"
        "Affects magnitude and duration of depression.\n"
        "Typical range: 50-200 vesicles per active zone.",
        "depends_on": {"calcium_dependence": True},
    },
    "replenishment_rate": {
        "label": "Vesicle Replenishment Rate (/s):",
        "type": "double",
        "default": 10.0,
        "min": 0.1,
        "max": 100.0,
        "step": 0.5,
        "decimals": 1,
        "tooltip": "Rate of vesicle pool replenishment.\n"
        "Determines recovery speed from depression.",
        "depends_on": {"calcium_dependence": True},
    },
}
