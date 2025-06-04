from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QSpinBox, QDoubleSpinBox

class SimParamsManager(QObject):
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.sim_params_ui_module = None
        
    def connect_signals(self):
        # Connect value changed signals for all parameters
        params = [
            self.main_window.sim_time_input,
            self.main_window.input_current_input,
            self.main_window.num_neurons_input,
            self.main_window.current_start_input,
            self.main_window.current_duration_input
            # Note: LIF parameters are connected separately via connect_lif_signals()
            # since they are created dynamically
        ]
        for param in params:
            if param is not None:  # Some params might be None if not created yet
                param.valueChanged.connect(self.on_param_changed)
    
    def connect_lif_signals(self):
        """Connect signals for dynamically created LIF parameters"""
        if hasattr(self.main_window, 'lif_threshold_input') and self.main_window.lif_threshold_input is not None:
            self.main_window.lif_threshold_input.valueChanged.connect(self.on_param_changed)
        if hasattr(self.main_window, 'lif_reset_input') and self.main_window.lif_reset_input is not None:
            self.main_window.lif_reset_input.valueChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any simulation parameter changes"""
        self.param_changed.emit()

    def get_sim_params(self):
        """Collects simulation parameters from the UI elements."""
        params = {
            "sim_time": self.main_window.sim_time_input.value(),
            "input_current": self.main_window.input_current_input.value(),
            "num_neurons": self.main_window.num_neurons_input.value(),
            "current_start": self.main_window.current_start_input.value(),
            "current_duration": self.main_window.current_duration_input.value(),
        }
        if self.main_window.neuron_model_combo.currentData() == "lif":
            params["lif_threshold"] = self.main_window.lif_threshold_input.value()
            params["lif_reset"] = self.main_window.lif_reset_input.value()
        return params

    def load_sim_params(self, data):
        """Loads simulation parameters into the UI elements."""
        if not data or not isinstance(data, dict):
            return
            
        if hasattr(self.main_window, 'sim_time_input') and self.main_window.sim_time_input:
            self.main_window.sim_time_input.setValue(data.get("sim_time", 1000))
        
        if hasattr(self.main_window, 'input_current_input') and self.main_window.input_current_input:
            self.main_window.input_current_input.setValue(data.get("input_current", 150.0))
            
        if hasattr(self.main_window, 'num_neurons_input') and self.main_window.num_neurons_input:
            self.main_window.num_neurons_input.setValue(data.get("num_neurons", 100))
            
        if hasattr(self.main_window, 'current_start_input') and self.main_window.current_start_input:
            self.main_window.current_start_input.setValue(data.get("current_start", 100))
            
        if hasattr(self.main_window, 'current_duration_input') and self.main_window.current_duration_input:
            self.main_window.current_duration_input.setValue(data.get("current_duration", 500))
        
        if "lif_threshold" in data:
            self.main_window.lif_threshold_input.setValue(data["lif_threshold"])
        if "lif_reset" in data:
            self.main_window.lif_reset_input.setValue(data["lif_reset"])
        
        # Ensure LIF params visibility is updated after loading, 
        # as the model type might have changed or been loaded.
        # This relies on NeuronModelsManager to have already set the correct model type.
        if self.sim_params_ui_module:
            model_key = self.main_window.neuron_model_combo.currentData()
            self.sim_params_ui_module.update_lif_parameters_visibility_in_sim_params(self.main_window, model_key)

    def update_lif_params_visibility(self, model_key):
        """
        Delegates to the UI module to update visibility of LIF parameters.
        Args:
            model_key: The current model key string from the neuron model combo
        """
        if self.sim_params_ui_module and model_key:
            self.sim_params_ui_module.update_lif_parameters_visibility_in_sim_params(
                self.main_window, 
                model_key
            )

    def apply_preset_values(self, preset_values):
        """Apply preset values to simulation parameters"""
        if "sim_time" in preset_values and self.main_window.sim_time_input:
            self.main_window.sim_time_input.setValue(preset_values["sim_time"])
        if "input_current" in preset_values and self.main_window.input_current_input:
            self.main_window.input_current_input.setValue(preset_values["input_current"])
        if "num_neurons" in preset_values and self.main_window.num_neurons_input:
            self.main_window.num_neurons_input.setValue(preset_values["num_neurons"])
        if "current_start" in preset_values and self.main_window.current_start_input:
            self.main_window.current_start_input.setValue(preset_values["current_start"])
        if "current_duration" in preset_values and self.main_window.current_duration_input:
            self.main_window.current_duration_input.setValue(preset_values["current_duration"])
        if "lif_threshold" in preset_values and self.main_window.lif_threshold_input:
            self.main_window.lif_threshold_input.setValue(preset_values["lif_threshold"])
        if "lif_reset" in preset_values and self.main_window.lif_reset_input:
            self.main_window.lif_reset_input.setValue(preset_values["lif_reset"])

    def get_sim_params_config(self):
        """Get simulation parameters configuration data for config manager."""
        return self.get_sim_params()
