from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QLineEdit, QComboBox

class NoiseOptionsManager(QObject):
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def connect_signals(self):
        """Connect UI signals to handle parameter changes"""
        # Get all widgets from the form generator
        if hasattr(self.main_window, 'noise_form_generator'):
            param_widgets = self.main_window.noise_form_generator.get_param_widgets()
            for param_key, widget in param_widgets.items():
                if hasattr(widget, 'valueChanged'):
                    widget.valueChanged.connect(self.on_param_changed)
                elif hasattr(widget, 'currentIndexChanged'):
                    widget.currentIndexChanged.connect(self.on_param_changed)
                elif hasattr(widget, 'stateChanged'):
                    widget.stateChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any noise parameter changes"""
        self.param_changed.emit()

    def get_noise_options(self):
        """Collects noise configuration options from the UI elements using the config-driven approach."""
        if not hasattr(self.main_window, 'noise_form_generator'):
            return {"enabled": False}
            
        param_widgets = self.main_window.noise_form_generator.get_param_widgets()
        enabled_checkbox = param_widgets.get("enabled")
        
        if not enabled_checkbox or not enabled_checkbox.isChecked():
            return {"enabled": False}

        # Get all parameter values using the form generator
        options = self.main_window.noise_form_generator.get_params_for_save()
        return options

    def load_noise_options(self, data):
        """Loads noise options into the UI elements using the form generator."""
        if not data or not isinstance(data, dict):
            return
            
        if hasattr(self.main_window, 'noise_form_generator'):
            self.main_window.noise_form_generator.load_params_from_config(data)

    def apply_preset_values(self, preset_values):
        """Apply preset values to noise parameters using the form generator."""
        if hasattr(self.main_window, 'noise_form_generator'):
            # Map preset values to the form generator format
            form_data = {}
            if "noise_enabled" in preset_values:
                form_data["enabled"] = preset_values["noise_enabled"]
            if "noise_intensity" in preset_values:
                form_data["intensity"] = preset_values["noise_intensity"]
            if "noise_method" in preset_values:
                form_data["method"] = preset_values["noise_method"]
            
            self.main_window.noise_form_generator.load_params_from_config(form_data)

    def get_noise_options_config(self):
        """Get noise options configuration data for config manager."""
        return self.get_noise_options()
