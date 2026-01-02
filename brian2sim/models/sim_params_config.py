"""
Simulation parameters configuration for Brian2 neural network simulator.
Matches exactly with the original sim_params_ui.py structure.
"""

SIM_PARAMS_CONFIG = {
    "neuron_model": {
        "label": "Neuron Model:",
        "type": "combo",
        "options": ["lif", "izhikevich", "adex", "hodgkin_huxley", "custom"],
        "display_options": [
            "Leaky Integrate-and-Fire",
            "Izhikevich",
            "Adaptive Exponential",
            "Hodgkin-Huxley",
            "Custom",
        ],
        "default": "lif",
        "tooltip": "Select the neuron model type for the simulation.",
        "hidden": True,  # This will be synchronized with the main neuron model combo box
    },
    "sim_time": {
        "label": "Simulation Time (ms):",
        "type": "int",
        "default": 1000,
        "min": 1,
        "max": 1000000,
        "tooltip": "Total duration of the simulation in milliseconds (ms). Typically 500-2000ms for simple neural simulations.",
    },
    "performance_mode": {
        "label": "Performance Mode:",
        "type": "combo",
        "options": ["python", "cpp_standalone", "cpp_parallel"],
        "display_options": [
            "Python (Default)",
            "C++ Standalone (Faster)",
            "C++ Parallel (Multi-threaded)",
        ],
        "default": "python",
        "tooltip": "Execution mode for Brian2:\n• Python: Default, good for debugging\n• C++ Standalone: Compiles to C++, ~10x faster\n• C++ Parallel: Uses OpenMP for multi-threading",
    },
    "dt": {
        "label": "Time Step (ms):",
        "type": "double",
        "default": 0.1,
        "min": 0.001,
        "max": 1.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Simulation time step (dt) in milliseconds.\n"
        "Smaller values = more accurate but slower.\n"
        "• 0.1 ms: Standard for most simulations\n"
        "• 0.01 ms: High precision for fast dynamics\n"
        "• 0.5-1.0 ms: Fast but less accurate",
    },
    "integration_method": {
        "label": "Integration Method:",
        "type": "combo",
        "options": ["auto", "exact", "euler", "rk2", "rk4", "heun", "milstein"],
        "display_options": [
            "Auto (Recommended)",
            "Exact (Linear ODEs)",
            "Euler (Fast)",
            "Runge-Kutta 2nd Order",
            "Runge-Kutta 4th Order",
            "Heun (Stochastic)",
            "Milstein (Stochastic)",
        ],
        "default": "auto",
        "tooltip": "Numerical integration method for differential equations:\n"
        "• Auto: Brian2 chooses optimal method\n"
        "• Exact: For linear equations only\n"
        "• Euler: Fast, first-order accuracy\n"
        "• RK2/RK4: Higher accuracy\n"
        "• Heun/Milstein: For stochastic equations",
    },
    "input_current": {
        "label": "Input Current (nA):",
        "type": "double",
        "default": 0.5,
        "min": 0.0,
        "max": 10.0,
        "step": 0.1,
        "decimals": 3,
        "tooltip": "Constant current injection into neurons. Range: 0.1-2.0 nA for typical LIF neurons.",
    },
    "num_neurons": {
        "label": "Number of Neurons:",
        "type": "int",
        "default": 100,
        "min": 1,
        "max": 10000,
        "tooltip": "Number of neurons in the network. Small networks (10-100) for basic simulations, larger networks (1000+) for complex dynamics.",
    },
    "current_start": {
        "label": "Current Start (ms):",
        "type": "int",
        "default": 100,
        "min": 0,
        "max": 1000000,
        "tooltip": "Start time of current injection (ms). Often delayed (100-200ms) to allow system to reach steady state and observe pre-stimulus behavior.",
    },
    "current_duration": {
        "label": "Current Duration (ms):",
        "type": "int",
        "default": 500,
        "min": 0,
        "max": 1000000,
        "tooltip": "Duration of current injection in milliseconds (ms). Typically 20-50% of total simulation time for observing both onset and sustained responses.",
    },
    "v_threshold": {
        "label": "Threshold (mV):",
        "type": "double",
        "default": -50.0,
        "min": -80.0,
        "max": 0.0,
        "step": 1.0,
        "decimals": 1,
        "tooltip": "Membrane potential threshold for spike generation. Typical cortical values: -50 to -55 mV.",
        "depends_on": {"neuron_model": "lif"},  # Show only when LIF model is selected
    },
    "v_reset": {
        "label": "Reset (mV):",
        "type": "double",
        "default": -65.0,
        "min": -90.0,
        "max": -40.0,
        "step": 1.0,
        "decimals": 1,
        "tooltip": "Post-spike reset potential. Should be below threshold, typically -65 to -70 mV.",
        "depends_on": {"neuron_model": ["lif", "adex"]},  # Show for LIF and AdEx
    },
    # State Management
    "store_state": {
        "label": "Store State Name:",
        "type": "text",
        "default": "",
        "tooltip": "Name to store the final network state under.\\n"
        "Allows restoring this state in future simulations.\\n"
        "Leave empty to disable.",
    },
    "restore_state": {
        "label": "Restore State Name:",
        "type": "text",
        "default": "",
        "tooltip": "Name of a previously stored state to restore at start.\\n"
        "Useful for continuing simulations or parameter sweeps.\\n"
        "Leave empty to start from scratch.",
    },
}
