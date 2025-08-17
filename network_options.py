from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QSpinBox

class NetworkOptionsManager(QObject):
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def connect_signals(self):
        """Connect UI signals to handle parameter changes"""
        # Get all widgets from the form generator
        if hasattr(self.main_window, 'network_form_generator'):
            param_widgets = self.main_window.network_form_generator.get_param_widgets()
            for param_key, widget in param_widgets.items():
                if hasattr(widget, 'valueChanged'):
                    widget.valueChanged.connect(self.on_param_changed)
                elif hasattr(widget, 'currentIndexChanged'):
                    widget.currentIndexChanged.connect(self.on_param_changed)
                elif hasattr(widget, 'stateChanged'):
                    widget.stateChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any network parameter changes"""
        self.param_changed.emit()

    def get_network_options(self):
        """Collects network configuration options from the UI elements using the config-driven approach."""
        if not hasattr(self.main_window, 'network_form_generator'):
            return {"synapse_enabled": False}
            
        param_widgets = self.main_window.network_form_generator.get_param_widgets()
        enabled_checkbox = param_widgets.get("enabled")
        
        if not enabled_checkbox or not enabled_checkbox.isChecked():
            return {"synapse_enabled": False}

        # Start with basic options
        options = {
            "synapse_enabled": True,
        }
        
        # Get parameter values from form widgets
        params = self.main_window.network_form_generator.get_params_for_save()
        options.update(params)
        
        # Extract topology parameters
        if "network_topology" in params:
            topology_type = params["network_topology"]
            options["topology_type"] = topology_type
            
            # Identify which parameters belong to the current topology
            topology_params = {}
            for key, value in params.items():
                # Skip non-topology parameters
                if key in ["enabled", "synaptic_weight", "network_topology"]:
                    continue
                    
                # Add topology-specific parameters
                topology_params[key] = value
                
            if topology_params:
                options["topology_params"] = topology_params

        return options

    def load_network_options(self, data):
        """Loads network options into the UI elements."""
        if not data or not isinstance(data, dict) or not hasattr(self.main_window, 'network_form_generator'):
            return
            
        # Get all widgets from form generator
        param_widgets = self.main_window.network_form_generator.get_param_widgets()
        
        # Set synapse enabled state
        enabled_checkbox = param_widgets.get("enabled")
        if enabled_checkbox:
            enabled_checkbox.setChecked(data.get("synapse_enabled", False))
            
        if not data.get("synapse_enabled", False):
            return  # Don't load other options if synapses are disabled
            
        # Set basic parameters
        weight_input = param_widgets.get("synaptic_weight")
        if weight_input:
            weight_input.setValue(data.get("synaptic_weight", 1.0))
            
        # Set topology type
        topology_combo = param_widgets.get("network_topology")
        topology_type = data.get("topology_type")
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
        if not isinstance(preset_values, dict) or not hasattr(self.main_window, 'network_form_generator'):
            return

        param_widgets = self.main_window.network_form_generator.get_param_widgets()
        
        # Apply synapse enable/disable
        enabled_checkbox = param_widgets.get("enabled")
        if enabled_checkbox and "synapse_enabled" in preset_values:
            enabled_checkbox.setChecked(preset_values["synapse_enabled"])
            
        if not enabled_checkbox or not enabled_checkbox.isChecked():
            return  # Don't apply other presets if disabled
              # Apply all parameters that have matching widgets
        for param_key, value in preset_values.items():
            widget = param_widgets.get(param_key)
            if widget and hasattr(widget, 'setValue'):
                try:
                    widget.setValue(float(value))
                except (ValueError, TypeError):
                    pass  # Skip if value can't be converted
