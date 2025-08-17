"""
Short-term plasticity manager for Brian2 neural network simulator.
Manages short-term synaptic plasticity parameters and validation.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from short_term_plasticity_config import SHORT_TERM_PLASTICITY_CONFIG

class ShortTermPlasticityManager(QObject):
    """Manager for short-term plasticity configuration and validation."""
    
    # Signals for parameter updates
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes
    parameters_changed = pyqtSignal()
    validation_error = pyqtSignal(str)
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.config = SHORT_TERM_PLASTICITY_CONFIG
        
    def on_param_changed(self):
        """Called when any short-term plasticity parameter changes"""
        self.param_changed.emit()
        
    def get_parameters(self):
        """Get current short-term plasticity parameters from UI."""
        params = {}
        
        if not hasattr(self.main_window, 'short_term_plasticity_forms'):
            return {'enabled': False}
            
        # Collect parameters from all forms
        for section_name, form_data in self.main_window.short_term_plasticity_forms.items():
            section_params = {}
            for param_name, widget in form_data['widgets'].items():
                if hasattr(widget, 'isChecked'):
                    section_params[param_name] = widget.isChecked()
                elif hasattr(widget, 'value'):
                    section_params[param_name] = widget.value()
                elif hasattr(widget, 'currentData'):
                    section_params[param_name] = widget.currentData()
                elif hasattr(widget, 'text'):
                    try:
                        section_params[param_name] = float(widget.text())
                    except ValueError:
                        section_params[param_name] = widget.text()
            params[section_name] = section_params
            
        return params
    
    def set_parameters(self, params):
        """Set short-term plasticity parameters in UI."""
        if not hasattr(self.main_window, 'short_term_plasticity_forms'):
            return
            
        for section_name, section_params in params.items():
            if section_name in self.main_window.short_term_plasticity_forms:
                form_data = self.main_window.short_term_plasticity_forms[section_name]
                for param_name, value in section_params.items():
                    if param_name in form_data['widgets']:
                        widget = form_data['widgets'][param_name]
                        if hasattr(widget, 'setChecked'):
                            widget.setChecked(bool(value))
                        elif hasattr(widget, 'setValue'):
                            widget.setValue(float(value))
                        elif hasattr(widget, 'setCurrentData'):
                            widget.setCurrentData(value)
                        elif hasattr(widget, 'setText'):
                            widget.setText(str(value))
    
    def validate_parameters(self, params):
        """Validate short-term plasticity parameters."""
        errors = []
        
        for section_name, section_params in params.items():
            if section_name in self.config:
                section_config = self.config[section_name]
                for param_name, value in section_params.items():
                    if param_name in section_config['parameters']:
                        param_config = section_config['parameters'][param_name]
                        
                        # Validate ranges for numeric parameters
                        if param_config['type'] in ['float', 'int']:
                            try:
                                numeric_value = float(value)
                                if 'min' in param_config and numeric_value < param_config['min']:
                                    errors.append(f"{param_name}: value {numeric_value} below minimum {param_config['min']}")
                                if 'max' in param_config and numeric_value > param_config['max']:
                                    errors.append(f"{param_name}: value {numeric_value} above maximum {param_config['max']}")
                            except (ValueError, TypeError):
                                errors.append(f"{param_name}: invalid numeric value {value}")
        
        return errors
    
    def connect_signals(self):
        """Connect parameter change signals."""
        # Connect signals will be implemented when UI widgets are created
        pass
    
    def apply_research_preset(self, preset_name):
        """Apply a research-validated parameter preset."""
        presets = {
            'facilitation': {
                'facilitation': {'enabled': True, 'U': 0.1, 'tau_F': 100.0},
                'depression': {'enabled': False},
                'depression_facilitation': {'enabled': False}
            },
            'depression': {
                'facilitation': {'enabled': False},
                'depression': {'enabled': True, 'U': 0.5, 'tau_D': 750.0},
                'depression_facilitation': {'enabled': False}
            },
            'paired_pulse': {
                'facilitation': {'enabled': False},
                'depression': {'enabled': False},
                'depression_facilitation': {'enabled': True, 'U': 0.25, 'tau_F': 50.0, 'tau_D': 500.0}
            }
        }
        
        if preset_name in presets:
            self.set_parameters(presets[preset_name])
            self.parameters_changed.emit()
