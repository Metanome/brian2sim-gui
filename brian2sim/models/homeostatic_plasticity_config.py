# homeostatic_plasticity_config.py
# Configuration for homeostatic plasticity mechanisms in Brian2Sim GUI
# Homeostatic plasticity maintains network stability by regulating activity levels

HOMEOSTATIC_PLASTICITY_CONFIG = {
    "enabled": {
        "type": "bool",
        "default": False,
        "label": "Enable Homeostatic Plasticity",
        "tooltip": "Enable homeostatic plasticity mechanisms for network stability",
    },
    # Target activity levels
    "target_firing_rate": {
        "type": "double",
        "default": 5.0,  # Hz
        "min": 0.1,
        "max": 50.0,
        "decimals": 1,
        "suffix": " Hz",
        "label": "Target Firing Rate",
        "tooltip": "Target firing rate for homeostatic regulation (Hz)",
        "depends_on": {"enabled": True},
    },
    "target_window": {
        "type": "double",
        "default": 1000.0,  # ms
        "min": 100.0,
        "max": 10000.0,
        "decimals": 1,
        "suffix": " ms",
        "label": "Target Window",
        "tooltip": "Time window for calculating average firing rate (ms)",
        "depends_on": {"enabled": True},
    },
    "regulation_threshold": {
        "type": "double",
        "default": 0.2,  # relative deviation
        "min": 0.05,
        "max": 1.0,
        "decimals": 2,
        "label": "Regulation Threshold",
        "tooltip": "Relative deviation from target that triggers homeostatic regulation",
        "depends_on": {"enabled": True},
    },
    # Synaptic scaling
    "synaptic_scaling": {
        "type": "bool",
        "default": True,
        "label": "Synaptic Scaling",
        "tooltip": "Enable multiplicative synaptic scaling",
        "depends_on": {"enabled": True},
    },
    "scaling_rate": {
        "type": "double",
        "default": 0.01,  # per second
        "min": 0.001,
        "max": 0.1,
        "decimals": 4,
        "suffix": " /s",
        "label": "Scaling Rate",
        "tooltip": "Rate of synaptic weight scaling (per second)",
        "depends_on": {"synaptic_scaling": True},
    },
    "min_weight_scaling": {
        "type": "double",
        "default": 0.1,
        "min": 0.01,
        "max": 0.9,
        "decimals": 2,
        "label": "Minimum Weight Scaling",
        "tooltip": "Minimum allowed synaptic weight scaling factor",
        "depends_on": {"synaptic_scaling": True},
    },
    "max_weight_scaling": {
        "type": "double",
        "default": 5.0,
        "min": 1.1,
        "max": 10.0,
        "decimals": 1,
        "label": "Maximum Weight Scaling",
        "tooltip": "Maximum allowed synaptic weight scaling factor",
        "depends_on": {"synaptic_scaling": True},
    },
    # Intrinsic excitability regulation
    "intrinsic_regulation": {
        "type": "bool",
        "default": True,
        "label": "Intrinsic Excitability Regulation",
        "tooltip": "Enable regulation of intrinsic neuron excitability",
        "depends_on": {"enabled": True},
    },
    "excitability_target": {
        "type": "combo",
        "default": "firing_rate",
        "options": ["firing_rate", "membrane_potential", "spike_threshold"],
        "label": "Excitability Target",
        "tooltip": "Which intrinsic property to regulate",
        "depends_on": {"intrinsic_regulation": True},
    },
    "threshold_adaptation": {
        "type": "bool",
        "default": True,
        "label": "Threshold Adaptation",
        "tooltip": "Enable adaptive spike threshold adjustment",
        "depends_on": {"enabled": True},
    },
    "threshold_rate": {
        "type": "double",
        "default": 0.005,  # per second
        "min": 0.0001,
        "max": 0.05,
        "decimals": 5,
        "suffix": " /s",
        "label": "Threshold Adaptation Rate",
        "tooltip": "Rate of spike threshold adaptation (per second)",
        "depends_on": {"threshold_adaptation": True},
    },
    "min_threshold": {
        "type": "double",
        "default": -60.0,  # mV
        "min": -80.0,
        "max": -40.0,
        "decimals": 1,
        "suffix": " mV",
        "label": "Minimum Threshold",
        "tooltip": "Minimum allowed spike threshold (mV)",
        "depends_on": {"threshold_adaptation": True},
    },
    "max_threshold": {
        "type": "double",
        "default": -40.0,  # mV
        "min": -60.0,
        "max": -20.0,
        "decimals": 1,
        "suffix": " mV",
        "label": "Maximum Threshold",
        "tooltip": "Maximum allowed spike threshold (mV)",
        "depends_on": {"threshold_adaptation": True},
    },
    # Metaplasticity
    "metaplasticity": {
        "type": "bool",
        "default": False,
        "label": "Metaplasticity",
        "tooltip": "Enable activity-dependent changes in plasticity",
        "depends_on": {"enabled": True},
    },
    "metaplasticity_threshold": {
        "type": "double",
        "default": 10.0,  # Hz
        "min": 1.0,
        "max": 100.0,
        "decimals": 1,
        "suffix": " Hz",
        "label": "Metaplasticity Threshold",
        "tooltip": "Activity threshold for metaplastic changes (Hz)",
        "depends_on": {"metaplasticity": True},
    },
    "meta_ltp_scaling": {
        "type": "double",
        "default": 1.2,
        "min": 0.5,
        "max": 3.0,
        "decimals": 2,
        "label": "LTP Scaling Factor",
        "tooltip": "Scaling factor for LTP under high activity",
        "depends_on": {"metaplasticity": True},
    },
    "meta_ltd_scaling": {
        "type": "double",
        "default": 0.8,
        "min": 0.1,
        "max": 1.5,
        "decimals": 2,
        "label": "LTD Scaling Factor",
        "tooltip": "Scaling factor for LTD under high activity",
        "depends_on": {"metaplasticity": True},
    },
    # BCM-like sliding threshold
    "bcm_plasticity": {
        "type": "bool",
        "default": False,
        "label": "BCM Plasticity",
        "tooltip": "Enable BCM-like plasticity with sliding threshold",
        "depends_on": {"enabled": True},
    },
    "bcm_tau": {
        "type": "double",
        "default": 10000.0,  # ms
        "min": 1000.0,
        "max": 100000.0,
        "decimals": 1,
        "suffix": " ms",
        "label": "BCM Time Constant",
        "tooltip": "Time constant for BCM threshold sliding (ms)",
        "depends_on": {"bcm_plasticity": True},
    },
    "bcm_power": {
        "type": "double",
        "default": 2.0,
        "min": 1.0,
        "max": 4.0,
        "decimals": 1,
        "label": "BCM Power",
        "tooltip": "Power for BCM threshold calculation",
        "depends_on": {"bcm_plasticity": True},
    },
    # Network-level homeostasis
    "network_regulation": {
        "type": "bool",
        "default": False,
        "label": "Network-Level Regulation",
        "tooltip": "Enable global network activity regulation",
        "depends_on": {"enabled": True},
    },
    "network_target_rate": {
        "type": "double",
        "default": 15.0,  # Hz (population rate)
        "min": 1.0,
        "max": 100.0,
        "decimals": 1,
        "suffix": " Hz",
        "label": "Network Target Rate",
        "tooltip": "Target population firing rate (Hz)",
        "depends_on": {"network_regulation": True},
    },
    "global_scaling": {
        "type": "bool",
        "default": False,
        "label": "Global Weight Scaling",
        "tooltip": "Apply uniform scaling to all synaptic weights",
        "depends_on": {"network_regulation": True},
    },
    "inhibitory_gain_control": {
        "type": "bool",
        "default": True,
        "label": "Inhibitory Gain Control",
        "tooltip": "Regulate inhibitory strength for network balance",
        "depends_on": {"network_regulation": True},
    },
    "inhibitory_scaling_rate": {
        "type": "double",
        "default": 0.02,  # per second
        "min": 0.001,
        "max": 0.1,
        "decimals": 4,
        "suffix": " /s",
        "label": "Inhibitory Scaling Rate",
        "tooltip": "Rate of inhibitory weight scaling (per second)",
        "depends_on": {"inhibitory_gain_control": True},
    },
    # Developmental homeostasis
    "developmental_regulation": {
        "type": "bool",
        "default": False,
        "label": "Developmental Regulation",
        "tooltip": "Enable age-dependent homeostatic changes",
        "depends_on": {"enabled": True},
    },
    "development_stages": {
        "type": "combo",
        "default": "adult",
        "options": ["embryonic", "neonatal", "juvenile", "adult", "aging"],
        "label": "Development Stage",
        "tooltip": "Current developmental stage",
        "depends_on": {"developmental_regulation": True},
    },
    "age_scaling_factor": {
        "type": "double",
        "default": 1.0,
        "min": 0.1,
        "max": 3.0,
        "decimals": 2,
        "label": "Age Scaling Factor",
        "tooltip": "Age-dependent scaling of homeostatic mechanisms",
        "depends_on": {"developmental_regulation": True},
    },
    # Activity detection methods
    "activity_detection": {
        "type": "combo",
        "default": "spike_count",
        "options": ["spike_count", "calcium_proxy", "synaptic_activity", "membrane_potential"],
        "label": "Activity Detection Method",
        "tooltip": "Method for detecting neural activity levels",
    },
    "detection_window": {
        "type": "double",
        "default": 500.0,  # ms
        "min": 50.0,
        "max": 5000.0,
        "decimals": 1,
        "suffix": " ms",
        "label": "Detection Window",
        "tooltip": "Time window for activity detection (ms)",
    },
    "smoothing_tau": {
        "type": "double",
        "default": 2000.0,  # ms
        "min": 100.0,
        "max": 20000.0,
        "decimals": 1,
        "suffix": " ms",
        "label": "Smoothing Time Constant",
        "tooltip": "Time constant for activity smoothing (ms)",
    },
    # Advanced regulation mechanisms
    "calcium_homeostasis": {
        "type": "bool",
        "default": False,
        "label": "Calcium Homeostasis",
        "tooltip": "Enable calcium-dependent homeostatic regulation",
    },
    "calcium_target": {
        "type": "double",
        "default": 0.1,  # μM
        "min": 0.01,
        "max": 1.0,
        "decimals": 3,
        "suffix": " μM",
        "label": "Target Calcium Level",
        "tooltip": "Target intracellular calcium concentration (μM)",
    },
    "calcium_regulation_rate": {
        "type": "double",
        "default": 0.001,  # per second
        "min": 0.0001,
        "max": 0.01,
        "decimals": 5,
        "suffix": " /s",
        "label": "Calcium Regulation Rate",
        "tooltip": "Rate of calcium-dependent homeostatic changes",
    },
    # Compensation mechanisms
    "compensation_delay": {
        "type": "double",
        "default": 60000.0,  # ms (1 minute)
        "min": 1000.0,
        "max": 600000.0,  # 10 minutes
        "decimals": 1,
        "suffix": " ms",
        "label": "Compensation Delay",
        "tooltip": "Delay before homeostatic compensation begins (ms)",
    },
    "compensation_strength": {
        "type": "double",
        "default": 1.0,
        "min": 0.1,
        "max": 5.0,
        "decimals": 2,
        "label": "Compensation Strength",
        "tooltip": "Strength of homeostatic compensation mechanisms",
    },
    "bidirectional_regulation": {
        "type": "bool",
        "default": True,
        "label": "Bidirectional Regulation",
        "tooltip": "Allow both up and down regulation of activity",
    },
}

# Homeostatic plasticity research references and validation ranges (2025 standards)
HOMEOSTATIC_PLASTICITY_RESEARCH_INFO = {
    "description": "Homeostatic plasticity mechanisms maintain stable neural activity levels while preserving the ability to learn and adapt.",
    "physiological_ranges": {
        "target_firing_rate": {
            "range": "1-20 Hz",
            "typical": "3-8 Hz",
            "notes": "Varies by cell type and brain region",
        },
        "scaling_rate": {
            "range": "0.001-0.05 /s",
            "typical": "0.005-0.02 /s",
            "notes": "Depends on experimental conditions and cell type",
        },
        "threshold_adaptation": {
            "range": "0.5-10 mV change",
            "typical": "2-5 mV",
            "notes": "Magnitude of adaptive threshold changes",
        },
    },
    "research_references": [
        "Turrigiano (2008) The self-tuning neuron: synaptic scaling of excitatory synapses. Cell 135:422-435",
        "Marder & Goaillard (2006) Variability, compensation and homeostasis in neuron and network function. Nat Rev Neurosci 7:563-574",
        "Davis (2006) Homeostatic control of neural activity: from phenomenology to molecular design. Annu Rev Neurosci 29:307-323",
        "Pozo & Goda (2010) Unraveling mechanisms of homeostatic synaptic plasticity. Neuron 66:337-351",
        "Keck et al. (2017) Integrating Hebbian and homeostatic plasticity: the current state of the field and future research directions. Phil Trans R Soc B 372:20160158",
        "Zenke et al. (2013) Synaptic plasticity in neural networks needs homeostasis with a fast rate detector. PLoS Comput Biol 9:e1003330",
    ],
    "implementation_notes": {
        "brian2_syntax": "Use StateMonitor for activity detection and run_regularly for homeostatic updates",
        "computational_efficiency": "Homeostatic mechanisms should update on slower timescales than synaptic plasticity",
        "stability_considerations": "Balance between homeostatic regulation and learning capability",
        "validation_tests": "Test network stability, firing rate distributions, and adaptation to perturbations",
    },
    "disease_associations": {
        "autism_spectrum_disorders": "Impaired excitation/inhibition balance and synaptic scaling",
        "epilepsy": "Failed homeostatic compensation leading to hyperexcitability",
        "alzheimer_disease": "Progressive loss of homeostatic mechanisms",
        "depression": "Altered stress response and homeostatic adaptation",
        "schizophrenia": "Disrupted inhibitory homeostasis and network stability",
    },
}
