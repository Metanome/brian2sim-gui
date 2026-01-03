"""
Calcium dynamics manager for Brian2 neural network simulator.
Manages calcium dynamics parameters and validation.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from brian2sim.models.calcium_dynamics_config import CALCIUM_DYNAMICS_CONFIG


class CalciumDynamicsManager(QObject):
    """Manager for calcium dynamics configuration and validation."""

    # Signals for parameter updates
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes
    parameters_changed = pyqtSignal()
    validation_error = pyqtSignal(str)

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.config = CALCIUM_DYNAMICS_CONFIG

    def on_param_changed(self):
        """Called when any calcium dynamics parameter changes"""
        self.param_changed.emit()

    def get_parameters(self):
        """Get current calcium dynamics parameters from UI."""
        params = {}

        if not hasattr(self.main_window, "calcium_dynamics_forms"):
            return {"enabled": False}

        # Collect parameters from all forms
        for section_name, form_data in self.main_window.calcium_dynamics_forms.items():
            section_params = {}
            for param_name, widget in form_data["widgets"].items():
                if hasattr(widget, "isChecked"):
                    section_params[param_name] = widget.isChecked()
                elif hasattr(widget, "value"):
                    section_params[param_name] = widget.value()
                elif hasattr(widget, "currentData"):
                    section_params[param_name] = widget.currentData()
                elif hasattr(widget, "text"):
                    try:
                        section_params[param_name] = float(widget.text())
                    except ValueError:
                        section_params[param_name] = widget.text()
            params[section_name] = section_params

        return params

    def set_parameters(self, params):
        """Set calcium dynamics parameters in UI."""
        if not hasattr(self.main_window, "calcium_dynamics_forms"):
            return

        for section_name, section_params in params.items():
            if section_name in self.main_window.calcium_dynamics_forms:
                form_data = self.main_window.calcium_dynamics_forms[section_name]
                for param_name, value in section_params.items():
                    if param_name in form_data["widgets"]:
                        widget = form_data["widgets"][param_name]
                        if hasattr(widget, "setChecked"):
                            widget.setChecked(bool(value))
                        elif hasattr(widget, "setValue"):
                            widget.setValue(float(value))
                        elif hasattr(widget, "setCurrentData"):
                            widget.setCurrentData(value)
                        elif hasattr(widget, "setText"):
                            widget.setText(str(value))

    def validate_parameters(self, params):
        """Validate calcium dynamics parameters."""
        errors = []

        for section_name, section_params in params.items():
            if section_name in self.config:
                section_config = self.config[section_name]
                for param_name, value in section_params.items():
                    if param_name in section_config["parameters"]:
                        param_config = section_config["parameters"][param_name]

                        # Validate ranges for numeric parameters
                        if param_config["type"] in ["float", "int"]:
                            try:
                                numeric_value = float(value)
                                if "min" in param_config and numeric_value < param_config["min"]:
                                    errors.append(
                                        f"{param_name}: value {numeric_value} below minimum {param_config['min']}"
                                    )
                                if "max" in param_config and numeric_value > param_config["max"]:
                                    errors.append(
                                        f"{param_name}: value {numeric_value} above maximum {param_config['max']}"
                                    )
                            except (ValueError, TypeError):
                                errors.append(f"{param_name}: invalid numeric value {value}")

        return errors

    def connect_signals(self):
        """Connect parameter change signals."""
        # Connect signals will be implemented when UI widgets are created

    def apply_research_preset(self, preset_name):
        """Apply a research-validated parameter preset."""
        presets = {
            "default": {
                "calcium_sources": {"enabled": True, "ca_influx_type": "voltage_dependent"},
                "calcium_buffers": {"enabled": True, "buffer_type": "single_exponential"},
                "calcium_pumps": {"enabled": True, "pump_type": "simple"},
                "calcium_stores": {"enabled": False},
            },
            "detailed": {
                "calcium_sources": {"enabled": True, "ca_influx_type": "channel_specific"},
                "calcium_buffers": {"enabled": True, "buffer_type": "multi_buffer"},
                "calcium_pumps": {"enabled": True, "pump_type": "cooperative"},
                "calcium_stores": {"enabled": True, "store_type": "er_ip3"},
            },
        }

        if preset_name in presets:
            self.set_parameters(presets[preset_name])
            self.parameters_changed.emit()

    def reset_to_defaults(self):
        """Reset calcium dynamics to their default values."""
        if hasattr(self.main_window, "calcium_dynamics_form_generator"):
            self.main_window.calcium_dynamics_form_generator.reset_to_defaults()
