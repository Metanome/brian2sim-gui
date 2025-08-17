from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QSpinBox, QDoubleSpinBox

class SimParamsManager(QObject):
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.sim_params_ui_module = None  # Will be set by the main application
        
    def connect_signals(self):
        # Connect value changed signals for all parameters using the form generator
        if hasattr(self.main_window, 'sim_params_form_generator'):
            param_widgets = self.main_window.sim_params_form_generator.get_param_widgets()
            for param_key, widget in param_widgets.items():
                if widget and hasattr(widget, 'valueChanged'):
                    widget.valueChanged.connect(self.on_param_changed)
        else:
            # Fallback to individual widget connections for backward compatibility
            params = [
                self.main_window.sim_time_input,
                self.main_window.input_current_input,
                self.main_window.num_neurons_input,
                self.main_window.current_start_input,
                self.main_window.current_duration_input
            ]
            for param in params:
                if param is not None:
                    param.valueChanged.connect(self.on_param_changed)
        
        # LIF parameters are now handled through the config-driven system
        self.connect_lif_signals()
    
    def connect_lif_signals(self):
        """Connect signals for LIF parameters if they exist and are visible"""
        if hasattr(self.main_window, 'lif_threshold_input') and self.main_window.lif_threshold_input is not None:
            # Disconnect any existing connection to avoid duplicates
            try:
                self.main_window.lif_threshold_input.valueChanged.disconnect(self.on_param_changed)
            except TypeError:
                pass  # No existing connection
            self.main_window.lif_threshold_input.valueChanged.connect(self.on_param_changed)
            
        if hasattr(self.main_window, 'lif_reset_input') and self.main_window.lif_reset_input is not None:
            # Disconnect any existing connection to avoid duplicates
            try:
                self.main_window.lif_reset_input.valueChanged.disconnect(self.on_param_changed)
            except TypeError:
                pass  # No existing connection
            self.main_window.lif_reset_input.valueChanged.connect(self.on_param_changed)
            
    def on_param_changed(self):
        """Called when any simulation parameter changes"""
        self.param_changed.emit()
        
    def get_sim_params(self):
        """Collects simulation parameters from the UI elements using config-driven approach."""
        if hasattr(self.main_window, 'sim_params_form_generator'):
            # Use config-driven approach
            params = self.main_window.sim_params_form_generator.get_params_for_save()
            # Remove the hidden neuron_model parameter from output
            if "neuron_model" in params:
                del params["neuron_model"]
            return params
        else:
            # Fallback to legacy approach
            params = {
                "sim_time": self.main_window.sim_time_input.value(),
                "input_current": self.main_window.input_current_input.value(),
                "num_neurons": self.main_window.num_neurons_input.value(),
                "current_start": self.main_window.current_start_input.value(),
                "current_duration": self.main_window.current_duration_input.value(),
            }
            if (hasattr(self.main_window, 'neuron_model_combo') and 
                self.main_window.neuron_model_combo.currentData() == "lif"):
                if (hasattr(self.main_window, 'lif_threshold_input') and 
                    self.main_window.lif_threshold_input):                    
                    params["lif_threshold"] = self.main_window.lif_threshold_input.value()
                if (hasattr(self.main_window, 'lif_reset_input') and 
                    self.main_window.lif_reset_input):
                    params["lif_reset"] = self.main_window.lif_reset_input.value()
            return params
            
    def load_sim_params(self, data):
        """Loads simulation parameters into the UI elements using config-driven approach."""
        if not data or not isinstance(data, dict):
            return
            
        if hasattr(self.main_window, 'sim_params_form_generator'):
            # Use config-driven approach
            self.main_window.sim_params_form_generator.load_params_from_save(data)
            # Sync the hidden neuron_model parameter with the main model selection
            self.main_window.sim_params_form_generator.sync_neuron_model()
        else:
            # Fallback to legacy approach
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
            
            # Load LIF parameters if available
            if "lif_threshold" in data and hasattr(self.main_window, 'lif_threshold_input') and self.main_window.lif_threshold_input:
                self.main_window.lif_threshold_input.setValue(data["lif_threshold"])
            if "lif_reset" in data and hasattr(self.main_window, 'lif_reset_input') and self.main_window.lif_reset_input:                self.main_window.lif_reset_input.setValue(data["lif_reset"])
            
            # Update LIF parameters visibility using config-driven approach
            if hasattr(self.main_window, 'neuron_model_combo'):
                model_key = self.main_window.neuron_model_combo.currentData()
                self.update_lif_params_visibility(model_key)
                
    def update_lif_params_visibility(self, model_key):
        """
        Updates visibility of LIF parameters using config-driven approach.
        Args:
            model_key: The current model key string from the neuron model combo
        """
        if hasattr(self.main_window, 'sim_params_form_generator'):
            # Use config-driven approach - sync hidden neuron_model parameter and update dependencies
            self.main_window.sim_params_form_generator.sync_neuron_model()
        else:
            # Fallback to UI module for backward compatibility
            if hasattr(self.main_window, 'sim_params_ui_module') and self.main_window.sim_params_ui_module:
                self.main_window.sim_params_ui_module.update_lif_parameters_visibility_in_sim_params(
                    self.main_window, 
                    model_key
                )
                
    def apply_preset_values(self, preset_values):
        """Apply preset values to simulation parameters using config-driven approach"""
        if hasattr(self.main_window, 'sim_params_form_generator'):
            # Use config-driven approach
            self.main_window.sim_params_form_generator.load_params_from_save(preset_values)
            # Sync the hidden neuron_model parameter with the main model selection
            self.main_window.sim_params_form_generator.sync_neuron_model()
        else:
            # Fallback to legacy approach
            if "sim_time" in preset_values and hasattr(self.main_window, 'sim_time_input') and self.main_window.sim_time_input:
                self.main_window.sim_time_input.setValue(preset_values["sim_time"])
            if "input_current" in preset_values and hasattr(self.main_window, 'input_current_input') and self.main_window.input_current_input:
                self.main_window.input_current_input.setValue(preset_values["input_current"])
            if "num_neurons" in preset_values and hasattr(self.main_window, 'num_neurons_input') and self.main_window.num_neurons_input:
                self.main_window.num_neurons_input.setValue(preset_values["num_neurons"])
            if "current_start" in preset_values and hasattr(self.main_window, 'current_start_input') and self.main_window.current_start_input:
                self.main_window.current_start_input.setValue(preset_values["current_start"])
            if "current_duration" in preset_values and hasattr(self.main_window, 'current_duration_input') and self.main_window.current_duration_input:
                self.main_window.current_duration_input.setValue(preset_values["current_duration"])
            if "lif_threshold" in preset_values and hasattr(self.main_window, 'lif_threshold_input') and self.main_window.lif_threshold_input:
                self.main_window.lif_threshold_input.setValue(preset_values["lif_threshold"])
            if "lif_reset" in preset_values and hasattr(self.main_window, 'lif_reset_input') and self.main_window.lif_reset_input:
                self.main_window.lif_reset_input.setValue(preset_values["lif_reset"])

    def get_sim_params_config(self):
        """Get simulation parameters configuration data for config manager."""
        return self.get_sim_params()
