from PyQt6.QtCore import QObject, pyqtSignal


class NoiseManager(QObject):
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def connect_signals(self):
        """Connect UI signals to handle parameter changes"""
        # Get all widgets from the form generator
        if hasattr(self.main_window, "noise_form_generator"):
            param_widgets = self.main_window.noise_form_generator.get_param_widgets()
            for param_key, widget in param_widgets.items():
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(self.on_param_changed)
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(self.on_param_changed)
                elif hasattr(widget, "stateChanged"):
                    widget.stateChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any noise parameter changes"""
        self.param_changed.emit()

    def get_config(self):
        """Collects noise configuration from the UI elements."""
        if not hasattr(self.main_window, "noise_form_generator"):
            return {"enabled": False}

        param_widgets = self.main_window.noise_form_generator.get_param_widgets()
        enabled_checkbox = param_widgets.get("enabled")

        if not enabled_checkbox or not enabled_checkbox.isChecked():
            return {"enabled": False}

        # Get all parameter values using the form generator
        options = self.main_window.noise_form_generator.get_params_for_save()
        return options

    def load_config(self, data):
        """Loads noise config into the UI elements using the form generator."""
        if not data or not isinstance(data, dict):
            return

        if hasattr(self.main_window, "noise_form_generator"):
            self.main_window.noise_form_generator.load_params_from_config(data)

    def apply_preset_values(self, preset_values):
        """Apply preset values to noise parameters using the form generator."""
        if not hasattr(self.main_window, "noise_form_generator"):
            return
            
        # Map preset values to the form generator format if needed
        form_data = {}
        
        # Use direct keys only - no legacy support
        if "enabled" in preset_values:
            form_data["enabled"] = preset_values["enabled"]
        
        if "intensity" in preset_values:
            form_data["intensity"] = preset_values["intensity"]
            
        if "method" in preset_values:
            form_data["method"] = preset_values["method"]

        self.main_window.noise_form_generator.load_params_from_config(form_data)
        # Note: visibility sync is now handled automatically by BaseFormGenerator.load_params_from_config()

    def reset_to_defaults(self):
        """Reset noise options to their default values."""
        if hasattr(self.main_window, "noise_form_generator"):
            self.main_window.noise_form_generator.reset_to_defaults()

