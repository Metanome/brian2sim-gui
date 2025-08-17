"""
Noise options configuration for Brian2 neural network simulator.
Matches exactly with the original noise_options.py and noise_options_ui.py structure.
"""

NOISE_CONFIG = {
    "enabled": {
        "label": "Enable Background Noise",
        "type": "bool",
        "default": False,
        "tooltip": "Enable stochastic fluctuations to model biological variability in neural activity."
    },
    "intensity": {
        "label": "Noise Intensity (nA):",
        "type": "double",
        "default": 0.1,
        "min": 0.0,
        "max": 2.0,  # Reduced from 5.0 to realistic range based on 2025 research
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Standard deviation of the noise in nA. Research-validated ranges:\n"
                  "• Background noise: 0.01-0.1 nA (thermal/channel noise)\n"
                  "• Synaptic noise: 0.1-0.5 nA (network activity)\n"
                  "• Strong perturbations: 0.5-2.0 nA (experimental stimulation)\n"
                  "Values >2.0 nA are rarely physiological."
    },
    "method": {
        "label": "Noise Method:",
        "type": "combo",
        "default": "Gaussian",
        "options": ["Gaussian", "Ornstein-Uhlenbeck"],
        "display_options": ["Gaussian White Noise", "Ornstein-Uhlenbeck Process"],
        "tooltip": "Type of noise distribution:\n"
                  "• Gaussian: Uncorrelated white noise (thermal/channel noise)\n"
                  "• Ornstein-Uhlenbeck: Temporally correlated noise (background activity)"
    },
    "correlation_time": {
        "label": "Correlation Time (ms):",
        "type": "double",
        "default": 5.0,
        "min": 0.1,
        "max": 50.0,  # Reduced from 100.0 based on current research
        "step": 0.5,
        "decimals": 1,
        "tooltip": "Correlation time constant for Ornstein-Uhlenbeck process.\n"
                  "Physiological ranges (2025 research):\n"
                  "• Fast synaptic noise: 1-5 ms\n"
                  "• Membrane noise: 5-15 ms\n"
                  "• Network fluctuations: 10-50 ms\n"
                  "Longer correlations (>50ms) are typically non-physiological.",
        "depends_on": {"method": "Ornstein-Uhlenbeck"}
    }
}
