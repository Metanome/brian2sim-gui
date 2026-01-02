from PyQt6.QtCore import QObject, pyqtSignal


class SimParamsManager(QObject):
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.sim_params_ui_module = None  # Will be set by the main application

    def connect_signals(self):
        # Connect value changed signals for all parameters using the form generator
        if hasattr(self.main_window, "sim_params_form_generator"):
            param_widgets = self.main_window.sim_params_form_generator.get_param_widgets()
            for param_key, widget in param_widgets.items():
                if widget and hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any simulation parameter changes"""
        self.param_changed.emit()

    def get_sim_params(self):
        """Collects simulation parameters from the UI elements using config-driven approach."""
        if hasattr(self.main_window, "sim_params_form_generator"):
            # Use config-driven approach
            params = self.main_window.sim_params_form_generator.get_params_for_save()
            # Remove the hidden neuron_model parameter from output
            if "neuron_model" in params:
                del params["neuron_model"]
            return params
        return {}

    def load_sim_params(self, data):
        """Loads simulation parameters into the UI elements using config-driven approach."""
        if not data or not isinstance(data, dict):
            return

        if hasattr(self.main_window, "sim_params_form_generator"):
            # Use config-driven approach
            self.main_window.sim_params_form_generator.load_params_from_config(data)
            # Sync the hidden neuron_model parameter with the main model selection
            self.main_window.sim_params_form_generator.sync_neuron_model()

    def update_lif_params_visibility(self, model_key):
        """
        Updates visibility of LIF parameters using config-driven approach.
        Args:
            model_key: The current model key string from the neuron model combo
        """
        if hasattr(self.main_window, "sim_params_form_generator"):
            # Use config-driven approach - sync hidden neuron_model parameter and update dependencies
            self.main_window.sim_params_form_generator.sync_neuron_model()

    def apply_preset_values(self, preset_values):
        """Apply preset values to simulation parameters using config-driven approach"""
        if hasattr(self.main_window, "sim_params_form_generator"):
            # Use config-driven approach
            self.main_window.sim_params_form_generator.load_params_from_config(preset_values)
            # Sync the hidden neuron_model parameter with the main model selection
            self.main_window.sim_params_form_generator.sync_neuron_model()

    def get_sim_params_config(self):
        """Get simulation parameters configuration data for config manager."""
        return self.get_sim_params()
