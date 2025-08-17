"""
Synaptic receptor types configuration for Brian2 neural network simulator.
Implements AMPA, NMDA, GABA_A, and GABA_B receptors based on 2025 research standards.
"""

SYNAPTIC_RECEPTORS_CONFIG = {
    "enabled": {
        "label": "Enable Multiple Receptor Types",
        "type": "bool",
        "default": False,
        "tooltip": "Enable realistic synaptic transmission with multiple receptor types.\n"
                  "Essential for accurate modeling of excitatory and inhibitory transmission."
    },
    
    # AMPA Receptors (Fast Excitatory)
    "ampa_enabled": {
        "label": "AMPA Receptors",
        "type": "bool",
        "default": True,
        "tooltip": "Fast glutamatergic excitatory transmission.\n"
                  "Mediates rapid synaptic responses (~1-2ms decay).",
        "depends_on": {"enabled": True}
    },
    "ampa_tau_rise": {
        "label": "AMPA Rise Time (ms):",
        "type": "double",
        "default": 0.2,
        "min": 0.1,
        "max": 2.0,
        "step": 0.1,
        "decimals": 2,
        "tooltip": "AMPA receptor activation time constant.\n"
                  "Research range: 0.1-0.5ms (very fast)",
        "depends_on": {"ampa_enabled": True}
    },
    "ampa_tau_decay": {
        "label": "AMPA Decay Time (ms):",
        "type": "double",
        "default": 2.0,
        "min": 1.0,
        "max": 10.0,
        "step": 0.1,
        "decimals": 1,
        "tooltip": "AMPA receptor deactivation time constant.\n"
                  "Research range: 1-5ms (fast decay)",
        "depends_on": {"ampa_enabled": True}
    },
    "ampa_reversal": {
        "label": "AMPA Reversal Potential (mV):",
        "type": "double",
        "default": 0.0,
        "min": -20.0,
        "max": 20.0,
        "step": 1.0,
        "decimals": 1,
        "tooltip": "AMPA receptor reversal potential.\n"
                  "Typically 0mV (non-selective cation channel)",
        "depends_on": {"ampa_enabled": True}
    },
    
    # NMDA Receptors (Slow Excitatory, Voltage-dependent)
    "nmda_enabled": {
        "label": "NMDA Receptors",
        "type": "bool",
        "default": True,
        "tooltip": "Slow glutamatergic excitatory transmission with Mg²⁺ block.\n"
                  "Critical for synaptic plasticity and learning.",
        "depends_on": {"enabled": True}
    },
    "nmda_tau_rise": {
        "label": "NMDA Rise Time (ms):",
        "type": "double",
        "default": 2.0,
        "min": 1.0,
        "max": 10.0,
        "step": 0.1,
        "decimals": 1,
        "tooltip": "NMDA receptor activation time constant.\n"
                  "Research range: 1-5ms (slower than AMPA)",
        "depends_on": {"nmda_enabled": True}
    },
    "nmda_tau_decay": {
        "label": "NMDA Decay Time (ms):",
        "type": "double",
        "default": 100.0,
        "min": 50.0,
        "max": 300.0,
        "step": 10.0,
        "decimals": 1,
        "tooltip": "NMDA receptor deactivation time constant.\n"
                  "Research range: 50-200ms (very slow)",
        "depends_on": {"nmda_enabled": True}
    },
    "nmda_reversal": {
        "label": "NMDA Reversal Potential (mV):",
        "type": "double",
        "default": 0.0,
        "min": -20.0,
        "max": 20.0,
        "step": 1.0,
        "decimals": 1,
        "tooltip": "NMDA receptor reversal potential.\n"
                  "Typically 0mV (Ca²⁺ permeable)",
        "depends_on": {"nmda_enabled": True}
    },
    "nmda_mg_concentration": {
        "label": "Mg²⁺ Concentration (mM):",
        "type": "double",
        "default": 1.0,
        "min": 0.0,
        "max": 5.0,
        "step": 0.1,
        "decimals": 1,
        "tooltip": "Extracellular Mg²⁺ concentration for voltage-dependent block.\n"
                  "Physiological range: 0.8-2.0mM",
        "depends_on": {"nmda_enabled": True}
    },
    
    # GABA_A Receptors (Fast Inhibitory)
    "gaba_a_enabled": {
        "label": "GABA_A Receptors",
        "type": "bool",
        "default": True,
        "tooltip": "Fast GABAergic inhibitory transmission.\n"
                  "Mediates rapid inhibition (~5-10ms decay).",
        "depends_on": {"enabled": True}
    },
    "gaba_a_tau_rise": {
        "label": "GABA_A Rise Time (ms):",
        "type": "double",
        "default": 0.5,
        "min": 0.1,
        "max": 2.0,
        "step": 0.1,
        "decimals": 2,
        "tooltip": "GABA_A receptor activation time constant.\n"
                  "Research range: 0.2-1.0ms",
        "depends_on": {"gaba_a_enabled": True}
    },
    "gaba_a_tau_decay": {
        "label": "GABA_A Decay Time (ms):",
        "type": "double",
        "default": 6.0,
        "min": 3.0,
        "max": 20.0,
        "step": 0.5,
        "decimals": 1,
        "tooltip": "GABA_A receptor deactivation time constant.\n"
                  "Research range: 3-15ms",
        "depends_on": {"gaba_a_enabled": True}
    },
    "gaba_a_reversal": {
        "label": "GABA_A Reversal Potential (mV):",
        "type": "double",
        "default": -70.0,
        "min": -90.0,
        "max": -50.0,
        "step": 1.0,
        "decimals": 1,
        "tooltip": "GABA_A receptor reversal potential.\n"
                  "Typically -70 to -80mV (Cl⁻ dependent)",
        "depends_on": {"gaba_a_enabled": True}
    },
    
    # GABA_B Receptors (Slow Inhibitory, Metabotropic)
    "gaba_b_enabled": {
        "label": "GABA_B Receptors",
        "type": "bool",
        "default": False,
        "tooltip": "Slow GABAergic inhibitory transmission via K⁺ channels.\n"
                  "G-protein coupled, very slow kinetics (~100-500ms).",
        "depends_on": {"enabled": True}
    },
    "gaba_b_tau_rise": {
        "label": "GABA_B Rise Time (ms):",
        "type": "double",
        "default": 50.0,
        "min": 20.0,
        "max": 100.0,
        "step": 5.0,
        "decimals": 1,
        "tooltip": "GABA_B receptor activation time constant.\n"
                  "Research range: 30-80ms (very slow)",
        "depends_on": {"gaba_b_enabled": True}
    },
    "gaba_b_tau_decay": {
        "label": "GABA_B Decay Time (ms):",
        "type": "double",
        "default": 200.0,
        "min": 100.0,
        "max": 1000.0,
        "step": 50.0,
        "decimals": 1,
        "tooltip": "GABA_B receptor deactivation time constant.\n"
                  "Research range: 150-500ms (extremely slow)",
        "depends_on": {"gaba_b_enabled": True}
    },
    "gaba_b_reversal": {
        "label": "GABA_B Reversal Potential (mV):",
        "type": "double",
        "default": -90.0,
        "min": -110.0,
        "max": -70.0,
        "step": 1.0,
        "decimals": 1,
        "tooltip": "GABA_B receptor reversal potential.\n"
                  "Typically -90mV (K⁺ channel mediated)",
        "depends_on": {"gaba_b_enabled": True}
    },
    
    # Synaptic Weight Configuration
    "ampa_weight_ratio": {
        "label": "AMPA Weight Ratio:",
        "type": "double",
        "default": 1.0,
        "min": 0.0,
        "max": 5.0,
        "step": 0.1,
        "decimals": 2,
        "tooltip": "Relative strength of AMPA component.\n"
                  "Total synaptic weight is scaled by this ratio.",
        "depends_on": {"ampa_enabled": True}
    },
    "nmda_weight_ratio": {
        "label": "NMDA Weight Ratio:",
        "type": "double",
        "default": 0.3,
        "min": 0.0,
        "max": 2.0,
        "step": 0.05,
        "decimals": 2,
        "tooltip": "Relative strength of NMDA component.\n"
                  "Typically 20-40% of AMPA strength in cortex.",
        "depends_on": {"nmda_enabled": True}
    },
    "gaba_a_weight_ratio": {
        "label": "GABA_A Weight Ratio:",
        "type": "double",
        "default": 1.0,
        "min": 0.0,
        "max": 10.0,
        "step": 0.1,
        "decimals": 2,
        "tooltip": "Relative strength of GABA_A component.\n"
                  "Often stronger than excitatory synapses.",
        "depends_on": {"gaba_a_enabled": True}
    },
    "gaba_b_weight_ratio": {
        "label": "GABA_B Weight Ratio:",
        "type": "double",
        "default": 0.5,
        "min": 0.0,
        "max": 3.0,
        "step": 0.1,
        "decimals": 2,
        "tooltip": "Relative strength of GABA_B component.\n"
                  "Usually weaker than GABA_A but longer lasting.",
        "depends_on": {"gaba_b_enabled": True}
    }
}
