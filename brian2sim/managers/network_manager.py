from PyQt6.QtCore import QObject, pyqtSignal


class NetworkManager(QObject):
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def connect_signals(self):
        """Connect UI signals to handle parameter changes"""
        # Get all widgets from the form generator
        if hasattr(self.main_window, "network_form_generator"):
            param_widgets = self.main_window.network_form_generator.get_param_widgets()
            for param_key, widget in param_widgets.items():
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(self.on_param_changed)
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(self.on_param_changed)
                elif hasattr(widget, "stateChanged"):
                    widget.stateChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any network parameter changes"""
        self.param_changed.emit()

    def get_config(self):
        """Collects network configuration from the UI elements."""
        if not hasattr(self.main_window, "network_form_generator"):
            return {"enabled": False}

        param_widgets = self.main_window.network_form_generator.get_param_widgets()
        enabled_checkbox = param_widgets.get("enabled")

        if not enabled_checkbox or not enabled_checkbox.isChecked():
            return {"enabled": False}

        # Start with basic options
        options = {
            "enabled": True,
        }

        # Get parameter values from form widgets
        params = self.main_window.network_form_generator.get_params_for_save()
        options.update(params)

        # Extract topology parameters
        if "network_topology" in params:
            topology_type = params["network_topology"]
            options["network_topology"] = topology_type

            # Identify which parameters belong to the current topology
            topology_params = {}
            for key, value in params.items():
                # Skip non-topology parameters
                if key in ["enabled", "synaptic_weight", "network_topology", "syn_prob"]:
                     continue

                # Add topology-specific parameters
                topology_params[key] = value

            if topology_params:
                options["topology_params"] = topology_params

        return options

    def load_config(self, data):
        """Loads network options into the UI elements."""
        if (
            not data
            or not isinstance(data, dict)
            or not hasattr(self.main_window, "network_form_generator")
        ):
            return

        # Get all widgets from form generator
        param_widgets = self.main_window.network_form_generator.get_param_widgets()

        # Set synapse enabled state
        enabled_checkbox = param_widgets.get("enabled")
        is_enabled = data.get("enabled", False)
        
        if enabled_checkbox:
            enabled_checkbox.setChecked(is_enabled)

        if not is_enabled:
            return  # Don't load other options if synapses are disabled

        # Set basic parameters
        weight_input = param_widgets.get("synaptic_weight")
        if weight_input:
            weight_input.setValue(data.get("synaptic_weight", 1.0))
            
        prob_input = param_widgets.get("syn_prob")
        if prob_input:
            prob_input.setValue(data.get("syn_prob", 0.1))

        # Set topology type
        topology_combo = param_widgets.get("network_topology")
        topology_type = data.get("network_topology")
        
        if topology_type and topology_combo:
            for i in range(topology_combo.count()):
                if topology_combo.itemData(i) == topology_type:
                    topology_combo.setCurrentIndex(i)
                    break

        # Set topology parameters
        topology_params = data.get("topology_params", {})
        for param_key, value in topology_params.items():
            widget = param_widgets.get(param_key)
            if widget:
                try:
                    widget.setValue(float(value))
                except (ValueError, TypeError):
                    pass  # Skip if value can't be converted

    def apply_preset_values(self, preset_values):
        """Apply preset values to network parameters using the config-driven approach"""
        if not isinstance(preset_values, dict) or not hasattr(
            self.main_window, "network_form_generator"
        ):
            return

        param_widgets = self.main_window.network_form_generator.get_param_widgets()

        # Apply synapse enable/disable
        enabled_checkbox = param_widgets.get("enabled")
        is_enabled = preset_values.get("enabled", None)
        
        if enabled_checkbox and is_enabled is not None:
             enabled_checkbox.setChecked(is_enabled)

        if not enabled_checkbox or not enabled_checkbox.isChecked():
            return  # Don't apply other presets if disabled
            
        # Apply topology if present
        topology_combo = param_widgets.get("network_topology")
        topology_type = preset_values.get("network_topology")
        
        if topology_combo and topology_type:
             for i in range(topology_combo.count()):
                if topology_combo.itemData(i) == topology_type:
                    topology_combo.setCurrentIndex(i)
                    break
            
        # Apply all parameters that have matching widgets
        for param_key, value in preset_values.items():
            widget = param_widgets.get(param_key)
            if widget and hasattr(widget, "setValue"):
                try:
                    widget.setValue(float(value))
                except (ValueError, TypeError):
                    pass  # Skip if value can't be converted
        
        # Sync visibility - calls form generator's centralized method
        self.main_window.network_form_generator.sync_params_visibility()

    def reset_to_defaults(self):
        """Reset network options to their default values."""
        if hasattr(self.main_window, "network_form_generator"):
            self.main_window.network_form_generator.reset_to_defaults()
