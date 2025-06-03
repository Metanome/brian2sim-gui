PRESET_DEFAULT_TEXT = "Select a preset..."
PRESET_CUSTOM_TEXT = "Custom"

# Neuron model configurations with biologically-accurate parameters
NEURON_MODELS_CONFIG = {
    "lif": {
        "display_name": "Leaky Integrate-and-Fire (LIF)",
        "params": {            "tau_m": {
                "type": float,
                "label": "τm (ms):",
                "tooltip": "Membrane time constant in milliseconds.\nTypical ranges:\n• Pyramidal neurons: 20-30 ms\n• Fast-spiking interneurons: 10-15 ms\n• Motor neurons: 15-25 ms",
                "default": 20.0,
                "min": 5.0,
                "max": 100.0,
                "step": 0.5
            },
            "v_rest": {
                "type": float,
                "label": "Vrest (mV):",
                "tooltip": "Resting membrane potential in millivolts.\nTypical ranges:\n• Cortical neurons: -70 to -65 mV\n• Hippocampal neurons: -65 to -60 mV\n• Motor neurons: -70 to -65 mV",
                "default": -70.0,
                "min": -80.0,
                "max": -50.0,
                "step": 0.5
            }
        },
        "presets": {
            "none": {"display_name": PRESET_DEFAULT_TEXT, "values": {}},
            "regular_spiking": {
                "display_name": "Regular Spiking Pyramidal",
                "values": {
                    "tau_m": 20.0,     # Membrane time constant (ms)
                    "v_rest": -70.0    # Resting potential (mV)
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 0.5,
                    "num_neurons": 1,
                    "lif_threshold": -55.0,
                    "lif_reset": -70.0,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.1,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "fast_spiking": {
                "display_name": "Fast Spiking Interneuron",
                "values": {
                    "tau_m": 10.0,     # Fast membrane time constant
                    "v_rest": -70.0    # Typical resting potential
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 0.8,     # Higher input current for FS cells
                    "num_neurons": 1,
                    "lif_threshold": -55.0,
                    "lif_reset": -70.0,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.05,   # Less noise for precise firing
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "adapting": {
                "display_name": "Adapting Neuron",
                "values": {
                    "tau_m": 25.0,     # Slower membrane time constant
                    "v_rest": -65.0    # Slightly higher resting potential
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 0.4,
                    "num_neurons": 1,
                    "lif_threshold": -52.0,    # Higher threshold
                    "lif_reset": -65.0,        # Higher reset
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.15,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "cortical_regular_spiking": {
                "display_name": "Cortical Regular Spiking",
                "values": {
                    "tau_m": 20.0,      # Membrane time constant (ms)
                    "v_rest": -70.0,    # Resting potential (mV)
                },
                "sim_params": {
                    "sim_time": 500,          # Simulation duration (ms)
                    "input_current": 0.5,     # Input current (nA)
                    "num_neurons": 1,
                    "lif_threshold": -55.0,   # Spike threshold (mV)
                    "lif_reset": -70.0,       # Reset potential (mV)
                    "current_start": 100,     # Start time of input (ms)
                    "current_duration": 300    # Duration of input (ms)
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.1,   # σ = 0.1 nA for biological membrane noise
                    "noise_method": "additive" 
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "hippocampal_pyramidal": {
                "display_name": "Hippocampal Pyramidal",
                "values": {
                    "tau_m": 25.0,     # Membrane time constant (ms)
                    "v_rest": -65.0,   # Resting potential (mV)
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 0.4,     # Lower input current for pyramidal cells
                    "num_neurons": 1,
                    "lif_threshold": -50.0,   # Higher threshold than RS cells
                    "lif_reset": -65.0,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.15,  # Higher noise for pyramidal cells
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "fast_spiking_interneuron": {
                "display_name": "Fast-Spiking Interneuron",
                "values": {
                    "tau_m": 10.0,     # Faster membrane time constant
                    "v_rest": -70.0,   # Resting potential (mV)
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 0.8,     # Higher input current for FS cells
                    "num_neurons": 1,
                    "lif_threshold": -55.0,
                    "lif_reset": -70.0,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.05,  # Lower noise for precise FS firing
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "cortical_network": {
                "display_name": "Cortical Microcircuit",
                "values": {
                    "tau_m": 20.0,    # Membrane time constant (ms)
                    "v_rest": -70.0,  # Resting potential (mV)
                },
                "sim_params": {
                    "sim_time": 1000,
                    "input_current": 0.5,
                    "num_neurons": 100,      # Larger network
                    "lif_threshold": -55.0,
                    "lif_reset": -70.0,
                    "current_start": 100,
                    "current_duration": 800
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.1,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": True,
                    "topology_type": "random",
                    "syn_weight": 0.2,       # Moderate synaptic strength
                    "syn_prob": 0.1,         # Sparse connectivity
                    "syn_delay": 2.0         # 2ms synaptic delay
                }
            }
        }
    },
    "izhikevich": {
        "display_name": "Izhikevich",
        "params": {
            "a": {
                "type": float,
                "label": "a:",
                "tooltip": "Recovery time scale.\nTypical ranges:\n• Regular spiking: 0.02\n• Fast spiking: 0.1\n• Chattering: 0.02",
                "default": 0.02,
                "min": 0.001,
                "max": 0.2,
                "step": 0.001
            },
            "b": {
                "type": float,
                "label": "b:",
                "tooltip": "Sensitivity of recovery to voltage.\nTypical ranges: 0.2-0.25",
                "default": 0.2,
                "min": 0.0,
                "max": 0.3,
                "step": 0.01
            },
            "c": {
                "type": float,
                "label": "c:",
                "tooltip": "Post-spike reset voltage.\nTypical ranges:\n• Regular spiking: -65\n• Chattering: -50",
                "default": -65.0,
                "min": -75.0,
                "max": -40.0,
                "step": 1.0
            },
            "d": {
                "type": float,
                "label": "d:",
                "tooltip": "Post-spike recovery increment.\nTypical ranges:\n• Regular spiking: 8\n• Fast spiking: 2\n• Chattering: 2",
                "default": 8.0,
                "min": 0.0,
                "max": 10.0,
                "step": 0.5
            }
        },
        "presets": {
            "none": {"display_name": PRESET_DEFAULT_TEXT, "values": {}},
            "regular_spiking": {
                "display_name": "Regular Spiking",
                "values": {
                    "a": 0.02,     # Slow recovery
                    "b": 0.2,      # Standard sensitivity
                    "c": -65.0,    # Standard reset voltage
                    "d": 8.0       # Strong spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 10.0,
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 1.0,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "chattering": {
                "display_name": "Chattering",
                "values": {
                    "a": 0.02,     # Slow recovery
                    "b": 0.2,      # Standard sensitivity
                    "c": -50.0,    # Higher reset for bursting
                    "d": 2.0       # Weak spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 10.0,
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 1.0,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "fast_spiking": {
                "display_name": "Fast Spiking",
                "values": {
                    "a": 0.1,      # Fast recovery
                    "b": 0.2,      # Standard sensitivity
                    "c": -65.0,    # Standard reset voltage
                    "d": 2.0       # Weak spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 10.0,
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.5,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "intrinsically_bursting": {
                "display_name": "Intrinsically Bursting",
                "values": {
                    "a": 0.02,     # Slow recovery
                    "b": 0.2,      # Standard sensitivity
                    "c": -55.0,    # Intermediate reset voltage
                    "d": 4.0       # Moderate spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 10.0,
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.8,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "network": {
                "display_name": "Small Network",
                "values": {
                    "a": 0.02,     # Regular spiking parameters
                    "b": 0.2,
                    "c": -65.0,
                    "d": 8.0
                },
                "sim_params": {
                    "sim_time": 1000,
                    "input_current": 10.0,
                    "num_neurons": 50,
                    "current_start": 100,
                    "current_duration": 800
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 1.0,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": True,
                    "topology_type": "random",
                    "syn_weight": 15.0,
                    "syn_prob": 0.1
                }
            },
            "lts": {
                "display_name": "Low-threshold Spiking",
                "values": {
                    "a": 0.02,     # Slow recovery
                    "b": 0.25,     # Higher subthreshold sensitivity
                    "c": -65.0,    # Standard reset voltage
                    "d": 2.0       # Weak spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 7.0,    # Lower current needed due to low threshold
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.5,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "resonator": {
                "display_name": "Resonator",
                "values": {
                    "a": 0.1,      # Fast recovery
                    "b": 0.26,     # Higher subthreshold sensitivity
                    "c": -65.0,    # Standard reset voltage
                    "d": 0.0       # No spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 9.0,
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.5,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "mixed_mode": {
                "display_name": "Mixed Mode",
                "values": {
                    "a": 0.02,     # Slow recovery
                    "b": 0.2,      # Standard sensitivity
                    "c": -55.0,    # Higher reset voltage
                    "d": 4.0       # Moderate spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 10.0,
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 0.8,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            }
        }
    },
    "adex": {
        "display_name": "Adaptive Exponential Integrate-and-Fire (AdEx)",
        "params": {
            "C": {
                "type": float,
                "label": "C (pF):",
                "tooltip": "Membrane capacitance in picofarads.\nTypical ranges: 100-300 pF",
                "default": 200.0,
                "min": 50.0,
                "max": 500.0,
                "step": 10.0
            },
            "gL": {
                "type": float,
                "label": "gL (nS):",
                "tooltip": "Leak conductance in nanosiemens.\nTypical ranges: 5-20 nS",
                "default": 10.0,
                "min": 1.0,
                "max": 30.0,
                "step": 0.5
            },
            "EL": {
                "type": float,
                "label": "EL (mV):",
                "tooltip": "Leak reversal potential in millivolts.\nTypical ranges: -75 to -60 mV",
                "default": -70.0,
                "min": -80.0,
                "max": -50.0,
                "step": 0.5
            },
            "VT": {
                "type": float,
                "label": "VT (mV):",
                "tooltip": "Spike threshold in millivolts.\nTypical ranges: -55 to -45 mV",
                "default": -50.0,
                "min": -60.0,
                "max": -40.0,
                "step": 0.5
            },
            "delT": {
                "type": float,
                "label": "ΔT (mV):",
                "tooltip": "Slope factor in millivolts.\nTypical ranges: 0.5-3 mV",
                "default": 2.0,
                "min": 0.1,
                "max": 5.0,
                "step": 0.1
            },
            "a": {
                "type": float,
                "label": "a (nS):",
                "tooltip": "Subthreshold adaptation in nanosiemens.\nTypical ranges: 1-4 nS for regular spiking",
                "default": 2.0,
                "min": 0.0,
                "max": 10.0,
                "step": 0.1
            },
            "tauw": {
                "type": float,
                "label": "τw (ms):",
                "tooltip": "Adaptation time constant in milliseconds.\nTypical ranges: 20-200 ms",
                "default": 30.0,
                "min": 1.0,
                "max": 500.0,
                "step": 1.0
            },
            "b": {
                "type": float,
                "label": "b (pA):",
                "tooltip": "Spike-triggered adaptation in picoamperes.\nTypical ranges: 20-100 pA for regular spiking",
                "default": 60.0,
                "min": 0.0,
                "max": 500.0,
                "step": 5.0
            }
        },
        "presets": {
            "none": {"display_name": PRESET_DEFAULT_TEXT, "values": {}},
            "regular_spiking": {
                "display_name": "Regular Spiking",
                "values": {
                    "C": 200.0,      # Membrane capacitance (pF)
                    "gL": 10.0,      # Leak conductance (nS)
                    "EL": -70.0,     # Leak reversal potential (mV)
                    "VT": -50.0,     # Spike threshold (mV)
                    "delT": 2.0,     # Slope factor (mV)
                    "a": 2.0,        # Subthreshold adaptation (nS)
                    "tauw": 30.0,    # Adaptation time constant (ms)
                    "b": 60.0        # Spike-triggered adaptation (pA)
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 500.0,  # Current in pA
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 50.0,  # Noise in pA
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "bursting": {
                "display_name": "Intrinsic Bursting",
                "values": {
                    "C": 130.0,       # Membrane capacitance (pF)
                    "gL": 18.0,       # Leak conductance (nS)
                    "EL": -58.0,      # Leak reversal potential (mV)
                    "VT": -50.0,      # Spike threshold (mV)
                    "delT": 2.0,      # Slope factor (mV)
                    "a": 4.0,         # Stronger subthreshold adaptation
                    "tauw": 150.0,    # Slower adaptation
                    "b": 120.0        # Stronger spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 400.0,
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 40.0,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "fast_spiking": {
                "display_name": "Fast Spiking",
                "values": {
                    "C": 100.0,       # Lower capacitance for fast dynamics
                    "gL": 10.0,       # Standard leak conductance
                    "EL": -70.0,      # Typical leak reversal potential
                    "VT": -50.0,      # Standard threshold
                    "delT": 1.5,      # Sharper spike initiation
                    "a": 0.0,         # No subthreshold adaptation
                    "tauw": 30.0,     # Standard adaptation time constant
                    "b": 0.0          # No spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 300.0,  # Lower current needed due to lack of adaptation
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 30.0,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "delayed_spiking": {
                "display_name": "Delayed Spiking",
                "values": {
                    "C": 200.0,       # Standard capacitance
                    "gL": 12.0,       # Higher leak conductance
                    "EL": -70.0,      # Standard leak potential
                    "VT": -50.0,      # Standard threshold
                    "delT": 1.5,      # Sharper spike initiation
                    "a": 0.5,         # Weak subthreshold adaptation
                    "tauw": 100.0,    # Slower adaptation
                    "b": 80.0         # Strong spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 1000,  # Longer simulation to see delay
                    "input_current": 200.0,
                    "num_neurons": 1,
                    "current_start": 200,
                    "current_duration": 600
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 20.0,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "low_threshold": {
                "display_name": "Low-threshold Spiking",
                "values": {
                    "C": 150.0,       # Lower capacitance
                    "gL": 10.0,       # Standard leak conductance
                    "EL": -65.0,      # Higher resting potential
                    "VT": -55.0,      # Higher threshold
                    "delT": 3.0,      # Broader spike initiation
                    "a": 2.0,         # Moderate subthreshold adaptation
                    "tauw": 40.0,     # Faster adaptation
                    "b": 40.0         # Moderate spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 500,
                    "input_current": 150.0,  # Lower current needed
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 300
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 15.0,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "tonic_adapting": {
                "display_name": "Tonic Spiking with Adaptation",
                "values": {
                    "C": 200.0,       # Standard capacitance
                    "gL": 10.0,       # Standard leak conductance
                    "EL": -70.0,      # Standard leak potential
                    "VT": -50.0,      # Standard threshold
                    "delT": 2.0,      # Standard slope factor
                    "a": 3.0,         # Strong subthreshold adaptation
                    "tauw": 150.0,    # Slow adaptation
                    "b": 100.0        # Strong spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 1000,
                    "input_current": 400.0,
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 800
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 40.0,
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            },
            "irregular": {
                "display_name": "Irregular Spiking",
                "values": {
                    "C": 180.0,       # Slightly lower capacitance
                    "gL": 8.0,        # Lower leak conductance
                    "EL": -68.0,      # Standard leak potential
                    "VT": -52.0,      # Higher threshold
                    "delT": 2.5,      # Broader spike initiation
                    "a": 4.0,         # Strong subthreshold adaptation
                    "tauw": 200.0,    # Very slow adaptation
                    "b": 40.0         # Moderate spike-triggered adaptation
                },
                "sim_params": {
                    "sim_time": 1000,
                    "input_current": 300.0,
                    "num_neurons": 1,
                    "current_start": 100,
                    "current_duration": 800
                },
                "noise_options": {
                    "noise_enabled": True,
                    "noise_intensity": 60.0,  # Higher noise for irregularity
                    "noise_method": "additive"
                },
                "network_options": {
                    "synapse_enabled": False
                }
            }
        }
    },
    "custom": {
        "display_name": "Custom Equations",
        "params": {
            "custom_eqs": {
                "type": str,
                "label": "Equations:",
                "tooltip": "Enter Brian2 differential equations.\nExample: dv/dt = (I-v)/(10*ms) : 1",
                "default": "dv/dt = (I-v)/(10*ms) : 1\nI : 1"
            },
            "custom_threshold": {
                "type": str,
                "label": "Threshold:",
                "tooltip": "Condition for spike generation.\nExample: v > -50*mV",
                "default": "v > -50*mV"
            },
            "custom_reset": {
                "type": str,
                "label": "Reset:",
                "tooltip": "Reset statements after spike.\nExample: v = -70*mV",
                "default": "v = -70*mV"
            }
        },
        "presets": {
            "none": {"display_name": "Custom", "values": {}},
            "example_lif": {
                "display_name": "Example LIF",
                "values": {
                    "custom_eqs": "dv/dt = (I-v)/(10*ms) : 1\nI : 1",
                    "custom_threshold": "v > -50*mV",
                    "custom_reset": "v = -70*mV"
                }
            },
            "example_izh": {
                "display_name": "Example Izhikevich",
                "values": {
                    "custom_eqs": "dv/dt = (0.04*v**2 + 5*v + 140 - u + I)/ms : 1\ndu/dt = (0.02*(0.2*v - u))/ms : 1\nI : 1",
                    "custom_threshold": "v >= 30",
                    "custom_reset": "v = -65; u += 8"
                }
            }
        }
    }
}

# Model presets indexed by key for easy access in code
MODEL_PRESETS = {model_key: config["presets"] 
                for model_key, config in NEURON_MODELS_CONFIG.items()}
