"""
Calcium dynamics configuration for Brian2 neural network simulator.
Implements intracellular calcium dynamics and calcium-dependent plasticity (2025 standards).
"""

CALCIUM_DYNAMICS_CONFIG = {
    "enabled": {
        "label": "Enable Calcium Dynamics",
        "type": "bool",
        "default": False,
        "tooltip": "Enable intracellular calcium dynamics and calcium-dependent processes.\n"
        "Essential for accurate modeling of synaptic plasticity and cellular signaling.",
    },
    # Calcium Compartments
    "compartments": {
        "label": "Calcium Compartments:",
        "type": "combo",
        "default": "single",
        "options": ["single", "spine_dendrite", "multiple"],
        "display_options": ["Single Compartment", "Spine-Dendrite", "Multiple Compartments"],
        "tooltip": "Calcium compartmentalization:\n"
        "• Single: Global intracellular calcium\n"
        "• Spine-Dendrite: Separate spine and dendritic calcium\n"
        "• Multiple: Full compartmental calcium dynamics",
        "depends_on": {"enabled": True},
    },
    # Calcium Sources
    "ca_sources": {
        "label": "Calcium Sources:",
        "type": "combo",
        "default": "voltage_nmda",
        "options": ["voltage_only", "nmda_only", "voltage_nmda", "vgcc_nmda"],
        "display_options": ["Voltage-gated only", "NMDA only", "Voltage + NMDA", "VGCC + NMDA"],
        "tooltip": "Sources of calcium influx:\n"
        "• Voltage-gated: L-type, N-type, P/Q-type calcium channels\n"
        "• NMDA: NMDA receptor-mediated calcium influx\n"
        "• Combined: Multiple calcium sources (most realistic)",
        "depends_on": {"enabled": True},
    },
    # Calcium Buffering
    "ca_buffer_enabled": {
        "label": "Calcium Buffering",
        "type": "bool",
        "default": True,
        "tooltip": "Include calcium buffering by proteins (calbindin, calmodulin, etc.).\n"
        "Critical for realistic calcium dynamics.",
        "depends_on": {"enabled": True},
    },
    "buffer_capacity": {
        "label": "Buffer Capacity:",
        "type": "double",
        "default": 200.0,
        "min": 10.0,
        "max": 1000.0,
        "step": 10.0,
        "decimals": 1,
        "tooltip": "Calcium buffering capacity (unitless).\n"
        "Research ranges:\n"
        "• Low buffering: 10-50\n"
        "• Moderate buffering: 50-200\n"
        "• High buffering: 200-1000",
        "depends_on": {"ca_buffer_enabled": True},
    },
    "buffer_kinetics": {
        "label": "Buffer Kinetics (ms):",
        "type": "double",
        "default": 1.0,
        "min": 0.1,
        "max": 50.0,
        "step": 0.1,
        "decimals": 1,
        "tooltip": "Time constant for calcium buffer binding/unbinding.\n"
        "Fast buffers: 0.1-1ms, Slow buffers: 5-50ms",
        "depends_on": {"ca_buffer_enabled": True},
    },
    # Calcium Extrusion
    "ca_extrusion_rate": {
        "label": "Extrusion Rate (/ms):",
        "type": "double",
        "default": 0.1,
        "min": 0.01,
        "max": 10.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Rate of calcium extrusion (pumps, exchangers).\n"
        "Research ranges:\n"
        "• Slow extrusion: 0.01-0.05 /ms\n"
        "• Fast extrusion: 0.1-1.0 /ms\n"
        "• Very fast: 1.0-10.0 /ms",
        "depends_on": {"enabled": True},
    },
    "ca_rest": {
        "label": "Resting [Ca²⁺] (μM):",
        "type": "double",
        "default": 0.1,
        "min": 0.01,
        "max": 1.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Resting intracellular calcium concentration.\n"
        "Physiological range: 0.05-0.2 μM",
        "depends_on": {"enabled": True},
    },
    # Calcium-Dependent Plasticity
    "ca_plasticity_enabled": {
        "label": "Calcium-Dependent Plasticity",
        "type": "bool",
        "default": True,
        "tooltip": "Enable calcium-dependent synaptic plasticity.\n"
        "Implements calcium-controlled STDP and metaplasticity.",
        "depends_on": {"enabled": True},
    },
    "ca_ltp_threshold": {
        "label": "LTP Threshold (μM):",
        "type": "double",
        "default": 1.0,
        "min": 0.1,
        "max": 10.0,
        "step": 0.1,
        "decimals": 1,
        "tooltip": "Calcium threshold for Long-Term Potentiation.\n" "Research ranges: 0.5-2.0 μM",
        "depends_on": {"ca_plasticity_enabled": True},
    },
    "ca_ltd_threshold": {
        "label": "LTD Threshold (μM):",
        "type": "double",
        "default": 0.3,
        "min": 0.05,
        "max": 1.0,
        "step": 0.05,
        "decimals": 2,
        "tooltip": "Calcium threshold for Long-Term Depression.\n" "Research ranges: 0.2-0.5 μM",
        "depends_on": {"ca_plasticity_enabled": True},
    },
    "ca_ltp_rate": {
        "label": "LTP Learning Rate:",
        "type": "double",
        "default": 0.01,
        "min": 0.001,
        "max": 0.1,
        "step": 0.001,
        "decimals": 4,
        "tooltip": "Learning rate for calcium-dependent LTP.\n"
        "Controls speed of synaptic strengthening.",
        "depends_on": {"ca_plasticity_enabled": True},
    },
    "ca_ltd_rate": {
        "label": "LTD Learning Rate:",
        "type": "double",
        "default": 0.005,
        "min": 0.001,
        "max": 0.1,
        "step": 0.001,
        "decimals": 4,
        "tooltip": "Learning rate for calcium-dependent LTD.\n"
        "Controls speed of synaptic weakening.",
        "depends_on": {"ca_plasticity_enabled": True},
    },
    # Calcium Channel Types
    "ltype_channels": {
        "label": "L-type Ca²⁺ Channels",
        "type": "bool",
        "default": True,
        "tooltip": "High-voltage activated, long-lasting calcium channels.\n"
        "Important for gene expression and plasticity.",
        "depends_on": {"ca_sources": ["voltage_only", "voltage_nmda", "vgcc_nmda"]},
    },
    "ltype_conductance": {
        "label": "L-type Conductance (nS):",
        "type": "double",
        "default": 5.0,
        "min": 0.1,
        "max": 50.0,
        "step": 0.1,
        "decimals": 1,
        "tooltip": "Maximum L-type calcium channel conductance.",
        "depends_on": {"ltype_channels": True},
    },
    "ntype_channels": {
        "label": "N-type Ca²⁺ Channels",
        "type": "bool",
        "default": True,
        "tooltip": "High-voltage activated, rapidly inactivating.\n"
        "Important for neurotransmitter release.",
        "depends_on": {"ca_sources": ["voltage_only", "voltage_nmda", "vgcc_nmda"]},
    },
    "ntype_conductance": {
        "label": "N-type Conductance (nS):",
        "type": "double",
        "default": 2.0,
        "min": 0.1,
        "max": 20.0,
        "step": 0.1,
        "decimals": 1,
        "tooltip": "Maximum N-type calcium channel conductance.",
        "depends_on": {"ntype_channels": True},
    },
    # NMDA Calcium Influx
    "nmda_ca_fraction": {
        "label": "NMDA Ca²⁺ Fraction:",
        "type": "double",
        "default": 0.1,
        "min": 0.01,
        "max": 0.5,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Fraction of NMDA current carried by calcium.\n"
        "Research range: 0.05-0.15 (typically ~10%)",
        "depends_on": {"ca_sources": ["nmda_only", "voltage_nmda", "vgcc_nmda"]},
    },
    # Calcium Diffusion
    "ca_diffusion": {
        "label": "Calcium Diffusion",
        "type": "bool",
        "default": False,
        "tooltip": "Include spatial calcium diffusion.\n"
        "Computationally intensive but important for dendritic integration.",
        "depends_on": {"compartments": ["spine_dendrite", "multiple"]},
    },
    "diffusion_constant": {
        "label": "Diffusion Constant (μm²/ms):",
        "type": "double",
        "default": 0.22,
        "min": 0.01,
        "max": 2.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Calcium diffusion constant in cytoplasm.\n"
        "Research value: ~0.22 μm²/ms in dendrites",
        "depends_on": {"ca_diffusion": True},
    },
}
