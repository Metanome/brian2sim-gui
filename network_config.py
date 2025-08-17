"""
Network options configuration for Brian2 neural network simulator.
Defines parameters for synaptic connectivity and network topology.
"""

NETWORK_CONFIG = {
    "enabled": {
        "label": "Enable Synaptic Connections",
        "type": "bool", 
        "default": False,
        "tooltip": "Enable interactions between neurons through synaptic connections. Required for network effects and emergent dynamics."
    },
    "synaptic_weight": {
        "label": "Synaptic Weight (nS):",
        "type": "double",
        "default": 1.0,
        "min": -100.0,
        "max": 100.0,
        "step": 0.1,
        "decimals": 3,
        "tooltip": "Strength of synaptic connections in nanosiemens (nS). Positive values for excitatory (0.1-5.0 nS typical), negative for inhibitory (-0.5 to -10.0 nS typical)."
    },
    "network_topology": {
        "label": "Network Topology:",
        "type": "combo",
        "default": "random",
        "options": ["random", "small_world", "scale_free", "regular", "modular"],
        "display_options": ["Random (Erdős–Rényi)", "Small World (Watts-Strogatz)", "Scale-Free (Barabási–Albert)", "Regular Lattice", "Modular Network"],
        "tooltip": "Network connectivity pattern:\n• Random: Each connection has equal probability\n• Small World: Local clusters with some long-range connections\n• Scale-Free: Few highly connected hubs, many sparsely connected nodes\n• Fully Connected: Every neuron connects to every other"
    },
    # Random topology parameters
    "syn_prob": {
        "label": "Connection Probability:",
        "type": "double",
        "default": 0.1,
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Probability of connection between any two neurons. Cortical networks typically have sparse connectivity (0.1-0.2 for local circuits).",
        "depends_on": {"network_topology": "random"}
    },
    # Small world parameters
    "topology_k": {
        "label": "Neighbors (k):",
        "type": "int",
        "default": 4,
        "min": 2,
        "max": 20,
        "step": 2,
        "tooltip": "Number of nearest neighbors to connect initially (must be even). In cortical networks, neurons typically connect to 2-10% of local population.",
        "depends_on": {"network_topology": "small_world"}
    },
    "topology_p_rewire": {
        "label": "Rewiring Probability:",
        "type": "double", 
        "default": 0.1,
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Probability of rewiring each connection. Values 0.1-0.2 create biologically realistic small-world networks with both local clusters and long-range connections.",
        "depends_on": {"network_topology": "small_world"}
    },
    # Scale-free parameters
    "topology_m": {
        "label": "New Connections (m):",
        "type": "int",
        "default": 3,
        "min": 1,
        "max": 10,
        "step": 1,
        "tooltip": "Number of connections each new node makes. Values 2-4 create realistic hub-based networks similar to certain neural subsystems.",
        "depends_on": {"network_topology": "scale_free"}
    },
    # Regular lattice parameters
    "topology_k_reg": {
        "label": "Neighbors (k):",
        "type": "int",
        "default": 4,
        "min": 2,
        "max": 20,
        "step": 2,
        "tooltip": "Number of nearest neighbors to connect (must be even). Models topographic neural maps with local connectivity.",
        "depends_on": {"network_topology": "regular"}
    },
    # Modular network parameters
    "topology_n_modules": {
        "label": "Number of Modules:",
        "type": "int",
        "default": 4,
        "min": 2,
        "max": 10,
        "step": 1,
        "tooltip": "Number of distinct neural modules. Cortical networks often organize into 3-8 functionally distinct modules.",
        "depends_on": {"network_topology": "modular"}
    },
    "topology_p_intra": {
        "label": "Intra-module Probability:",
        "type": "double",
        "default": 0.15,
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Connection probability within modules. Higher than inter-module (0.1-0.2 typical) to create distinct functional units.",
        "depends_on": {"network_topology": "modular"}
    },
    "topology_p_inter": {
        "label": "Inter-module Probability:",
        "type": "double",
        "default": 0.01,
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
        "decimals": 3,
        "tooltip": "Connection probability between modules. Lower than intra-module (0.01-0.05 typical) to maintain module separation.",
        "depends_on": {"network_topology": "modular"}
    }
}
