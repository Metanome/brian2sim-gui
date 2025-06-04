from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QSpinBox

NETWORK_TOPOLOGIES_CONFIG = {
    "random": {
        "display_name": "Random (Erdős–Rényi)",
        "params": {
            "syn_prob": {
                "label": "Connection Probability:", 
                "type": "double", 
                "default": 0.1, 
                "min": 0,
                "max": 1,
                "step": 0.01,
                "tooltip": "Probability of connection between any two neurons. Cortical networks typically have sparse connectivity (0.1-0.2 for local circuits)."
            }
        }
    },
    "small_world": {
        "display_name": "Small World (Watts-Strogatz)",
        "params": {
            "topology_k": {
                "label": "Neighbors (k):",
                "type": "int",
                "default": 4,
                "min": 2,
                "step": 2,
                "tooltip": "Number of nearest neighbors to connect initially (must be even). In cortical networks, neurons typically connect to 2-10% of local population."
            },
            "topology_p_rewire": {
                "label": "Rewiring Probability:",
                "type": "double",
                "default": 0.1,
                "min": 0,
                "max": 1,
                "step": 0.01,
                "tooltip": "Probability of rewiring each connection. Values 0.1-0.2 create biologically realistic small-world networks with both local clusters and long-range connections."
            }
        }
    },
    "scale_free": {
        "display_name": "Scale Free (Barabási–Albert)",
        "params": {
            "topology_m": {
                "label": "New Connections (m):",
                "type": "int",
                "default": 3,
                "min": 1,
                "max": 10,
                "step": 1,
                "tooltip": "Number of connections each new node makes. Values 2-4 create realistic hub-based networks similar to certain neural subsystems."
            }
        }
    },
    "regular": {
        "display_name": "Regular Lattice",
        "params": {
            "topology_k_reg": {
                "label": "Neighbors (k):",
                "type": "int",
                "default": 4,
                "min": 2,
                "max": 20,
                "step": 2,
                "tooltip": "Number of nearest neighbors to connect (must be even). Models topographic neural maps with local connectivity."
            }
        }
    },
    "modular": {
        "display_name": "Modular Network",
        "params": {
            "topology_n_modules": {
                "label": "Number of Modules:",
                "type": "int",
                "default": 4,
                "min": 2,
                "max": 10,
                "step": 1,
                "tooltip": "Number of distinct neural modules. Cortical networks often organize into 3-8 functionally distinct modules."
            },
            "topology_p_intra": {
                "label": "Intra-module Probability:",
                "type": "double",
                "default": 0.15,
                "min": 0,
                "max": 1,
                "step": 0.01,
                "tooltip": "Connection probability within modules. Higher than inter-module (0.1-0.2 typical) to create distinct functional units."
            },
            "topology_p_inter": {
                "label": "Inter-module Probability:",
                "type": "double",
                "default": 0.01,
                "min": 0,
                "max": 1,
                "step": 0.01,
                "tooltip": "Connection probability between modules. Lower than intra-module (0.01-0.05 typical) to maintain module separation."
            }
        }
    }
}

class NetworkOptionsManager(QObject):
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.topology_forms = {} # Will be populated by network_options_ui

    def connect_signals(self):
        # Connect network parameter change signals
        if self.main_window.synaptic_connections_checkbox:
            self.main_window.synaptic_connections_checkbox.stateChanged.connect(self.on_param_changed)
        if self.main_window.synaptic_weight_input:
            self.main_window.synaptic_weight_input.valueChanged.connect(self.on_param_changed)
        if self.main_window.network_topology_combo:
            self.main_window.network_topology_combo.currentIndexChanged.connect(self.on_param_changed)
        if self.main_window.connection_probability_input:
            self.main_window.connection_probability_input.valueChanged.connect(self.on_param_changed)
        if self.main_window.sw_nearest_neighbors_input:
            self.main_window.sw_nearest_neighbors_input.valueChanged.connect(self.on_param_changed)
        if self.main_window.sw_rewiring_probability_input:
            self.main_window.sw_rewiring_probability_input.valueChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any network parameter changes"""
        self.param_changed.emit()

    def toggle_synapse_params_visibility(self, state):
        if self.main_window.synapse_params_group:
            self.main_window.synapse_params_group.setVisible(state == Qt.CheckState.Checked.value)

    def update_topology_params_form(self, index):
        if not self.main_window.topology_params_stacked_widget or not self.main_window.network_topology_combo:
            return

        topology_key = self.main_window.network_topology_combo.itemData(index)
        
        if topology_key and topology_key in self.topology_forms:
            form_to_show = self.topology_forms[topology_key]["widget"]
            self.main_window.topology_params_stacked_widget.setCurrentWidget(form_to_show)
        else:
            # Fallback or hide if no/invalid key
            # Ensure a default valid widget is shown or it's cleared
            # This case should ideally not happen if combo and forms are synced
            if self.main_window.topology_params_stacked_widget.count() > 0:
                # Default to the first widget if key is bad, or handle error
                pass # Or log an error, or show a blank placeholder widget

    def get_network_options(self):
        """Collects network configuration options from the UI elements."""
        if not self.main_window.synaptic_connections_checkbox.isChecked():
            return {"synapse_enabled": False}

        options = {
            "synapse_enabled": True,
            "syn_weight": self.main_window.synaptic_weight_input.value() if self.main_window.synaptic_weight_input else 0.2,
        }

        if self.main_window.network_topology_combo:
            current_idx = self.main_window.network_topology_combo.currentIndex()
            topology_key = self.main_window.network_topology_combo.itemData(current_idx)
            if topology_key:
                options["topology_type"] = topology_key
                if topology_key in self.topology_forms:
                    form_info = self.topology_forms[topology_key]
                    topology_params = {}
                    for param_key, widget in form_info["params"].items():
                        topology_params[param_key] = widget.value()
                    if topology_params:
                        options["topology_params"] = topology_params

        return options

    def load_network_options(self, data):
        """Loads network options into the UI elements."""
        if not data or not isinstance(data, dict):
            return
            
        # Set synapse enabled state
        if hasattr(self.main_window, 'synaptic_connections_checkbox') and self.main_window.synaptic_connections_checkbox:
            self.main_window.synaptic_connections_checkbox.setChecked(data.get("synapse_enabled", False))
            
        if not data.get("synapse_enabled", False):
            return  # Don't load other options if synapses are disabled
            
        # Set synaptic weight
        if hasattr(self.main_window, 'synaptic_weight_input') and self.main_window.synaptic_weight_input:
            self.main_window.synaptic_weight_input.setValue(data.get("syn_weight", 1.0))
            
        # Set topology type
        topology_type = data.get("topology_type")
        if topology_type and hasattr(self.main_window, 'network_topology_combo') and self.main_window.network_topology_combo:
            for i in range(self.main_window.network_topology_combo.count()):
                if self.main_window.network_topology_combo.itemData(i) == topology_type:
                    self.main_window.network_topology_combo.setCurrentIndex(i)
                    break
                    
        # Set topology parameters
        topology_params = data.get("topology_params", {})
        if topology_type and topology_type in self.topology_forms:
            form_info = self.topology_forms[topology_type]
            for param_key, widget in form_info["params"].items():
                if param_key in topology_params:
                    try:
                        widget.setValue(float(topology_params[param_key]))
                    except (ValueError, TypeError):
                        pass  # Skip if value can't be converted
                        
        # The checkbox's stateChanged signal will handle visibility

    def apply_preset_values(self, preset_values):
        """Apply preset values to network parameters"""
        if not isinstance(preset_values, dict):
            return

        # Apply synapse enable/disable
        if "synapse_enabled" in preset_values:
            self.main_window.synaptic_connections_checkbox.setChecked(preset_values["synapse_enabled"])
            
        if self.main_window.synaptic_connections_checkbox.isChecked():
            # Apply topology type
            if "topology_type" in preset_values:
                index = self.main_window.network_topology_combo.findText(preset_values["topology_type"])
                if index >= 0:
                    self.main_window.network_topology_combo.setCurrentIndex(index)

            # Set synaptic weight
            if "syn_weight" in preset_values and self.main_window.synaptic_weight_input:
                self.main_window.synaptic_weight_input.setValue(preset_values["syn_weight"])

            # Set topology-specific parameters
            topology_type = self.main_window.network_topology_combo.currentText().lower()
            
            if topology_type == "random":
                if "syn_prob" in preset_values and self.main_window.connection_probability_input:
                    self.main_window.connection_probability_input.setValue(preset_values["syn_prob"])
            
            elif topology_type == "small world":
                if "topology_k" in preset_values and self.main_window.sw_nearest_neighbors_input:
                    self.main_window.sw_nearest_neighbors_input.setValue(preset_values["topology_k"])
                if "topology_p_rewire" in preset_values and self.main_window.sw_rewiring_probability_input:
                    self.main_window.sw_rewiring_probability_input.setValue(preset_values["topology_p_rewire"])

    def get_network_options_config(self):
        """Get network options configuration data for config manager."""
        return self.get_network_options()
