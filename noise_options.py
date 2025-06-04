from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QLineEdit, QComboBox

# Configuration for noise parameters in neural simulations
NOISE_CONFIG = {
    "intensity": {
        "min": 0.0,
        "max": 5.0,
        "default": 0.1,
        "step": 0.01,
        "tooltip": "Standard deviation of the noise in nA. Range: 0.1-1.0 nA for background noise, up to 5.0 nA for strong perturbations."
    },
    "methods": {
        "Gaussian": {
            "display_name": "Gaussian White Noise",
            "tooltip": "Adds uncorrelated Gaussian noise to each time step. Models thermal and channel noise in neurons."
        },
        "Ornstein-Uhlenbeck": {
            "display_name": "Ornstein-Uhlenbeck Process",
            "tooltip": "Temporally correlated noise that better models biological background activity. Has a characteristic correlation time."
        }
    }
}

class NoiseOptionsManager(QObject):
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # self.noise_options_ui_module = None # Not strictly needed if UI module doesn't call manager

    def connect_signals(self):
        # Connect noise parameter change signals
        if self.main_window.noise_checkbox:
            self.main_window.noise_checkbox.stateChanged.connect(self.on_param_changed)
        if self.main_window.noise_intensity_input:
            self.main_window.noise_intensity_input.valueChanged.connect(self.on_param_changed)
        if self.main_window.noise_method_combo:
            self.main_window.noise_method_combo.currentIndexChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any noise parameter changes"""
        self.param_changed.emit()

    def toggle_noise_params_visibility(self, state):
        """ 
        Toggles the visibility of the noise parameters group based on checkbox state.
        Called by the stateChanged signal of the noise_checkbox.
        """
        # Import the ui module locally to avoid circular import at module level
        # if noise_options_ui were to import NoiseOptionsManager for other reasons.
        import noise_options_ui 
        is_checked = (state == Qt.CheckState.Checked.value)
        noise_options_ui.update_noise_params_visibility(self.main_window, is_checked)

    def get_noise_options(self):
        """Collects noise options from the UI elements."""
        if not self.main_window.noise_checkbox.isChecked():
            return {"enabled": False}
            
        # Ensure noise_intensity_input is treated as a float if it's QLineEdit
        try:
            intensity_value = float(self.main_window.noise_intensity_input.text())
        except ValueError:
            intensity_value = 0.0 # Default or error value
            
        options = {
            "enabled": True,
            "intensity": intensity_value,
            "method": self.main_window.noise_method_combo.currentText()
        }
        return options

    def load_noise_options(self, data):
        """Loads noise options into the UI elements."""
        if not data or not isinstance(data, dict):
            return
            
        enabled = data.get("enabled", False)
        self.main_window.noise_checkbox.setChecked(enabled)
        
        if hasattr(self.main_window, 'noise_intensity_input') and self.main_window.noise_intensity_input:
            self.main_window.noise_intensity_input.setValue(data.get("intensity", 0.1))
            
        if hasattr(self.main_window, 'noise_method_combo') and self.main_window.noise_method_combo:
            # Find the item with matching display name
            for i in range(self.main_window.noise_method_combo.count()):
                if self.main_window.noise_method_combo.itemText(i) == data.get("method"):
                    self.main_window.noise_method_combo.setCurrentIndex(i)
                    break

    def apply_preset_values(self, preset_values):
        """Apply preset values to noise parameters"""
        if "noise_enabled" in preset_values and self.main_window.noise_checkbox:
            self.main_window.noise_checkbox.setChecked(preset_values["noise_enabled"])
        if "noise_intensity" in preset_values and self.main_window.noise_intensity_input:
            self.main_window.noise_intensity_input.setValue(preset_values["noise_intensity"])
        if "noise_method" in preset_values and self.main_window.noise_method_combo:
            index = self.main_window.noise_method_combo.findText(preset_values["noise_method"])
            if index >= 0:
                self.main_window.noise_method_combo.setCurrentIndex(index)

    def get_noise_options_config(self):
        """Get noise options configuration data for config manager."""
        return self.get_noise_options()
