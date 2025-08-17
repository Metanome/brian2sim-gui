"""
Synaptic receptors manager for Brian2 neural network simulator.
Handles user interactions and state management for synaptic receptor configuration.
"""

from PyQt6.QtCore import QObject, pyqtSignal

class SynapticReceptorsManager(QObject):
    """Manager for synaptic receptors configuration and UI interactions."""
    param_changed = pyqtSignal()  # Signal emitted when any parameter changes
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
    def connect_signals(self):
        """Connect UI signals to handler methods."""
        # Get all widgets from the form generator
        if hasattr(self.main_window, 'synaptic_receptors_form_generator'):
            param_widgets = self.main_window.synaptic_receptors_form_generator.get_param_widgets()
            for param_key, widget in param_widgets.items():
                if hasattr(widget, 'valueChanged'):
                    widget.valueChanged.connect(self.on_param_changed)
                elif hasattr(widget, 'currentIndexChanged'):
                    widget.currentIndexChanged.connect(self.on_param_changed)
                elif hasattr(widget, 'stateChanged'):
                    widget.stateChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any synaptic receptors parameter changes"""
        self.param_changed.emit()
    
    def on_enabled_changed(self, enabled):
        """Handle synaptic receptors enabled/disabled state change."""
        if hasattr(self.main_window, 'synaptic_receptors_forms'):
            for key, widget in self.main_window.synaptic_receptors_forms.items():
                if key != 'enabled' and widget:
                    widget.setEnabled(enabled)
    
    def update_receptor_dependencies(self):
        """Update parameter visibility based on enabled receptor types."""
        # This will be handled by the dependency system in BaseFormGenerator
        pass
    
    def get_synaptic_receptors_config(self):
        """Get current synaptic receptors configuration."""
        config = {}
        
        if hasattr(self.main_window, 'synaptic_receptors_forms'):
            for key, widget in self.main_window.synaptic_receptors_forms.items():
                if widget is not None:
                    if hasattr(widget, 'isChecked'):  # QCheckBox
                        config[key] = widget.isChecked()
                    elif hasattr(widget, 'value'):  # QSpinBox, QDoubleSpinBox
                        config[key] = widget.value()
                    elif hasattr(widget, 'text'):  # QLineEdit
                        config[key] = widget.text()
                    elif hasattr(widget, 'currentData'):  # QComboBox
                        config[key] = widget.currentData()
        
        return config
    
    def load_synaptic_receptors_config(self, config):
        """Load synaptic receptors configuration into UI."""
        if not hasattr(self.main_window, 'synaptic_receptors_forms'):
            return
            
        for key, value in config.items():
            widget = self.main_window.synaptic_receptors_forms.get(key)
            if widget is not None:
                try:
                    if hasattr(widget, 'setChecked'):  # QCheckBox
                        widget.setChecked(bool(value))
                    elif hasattr(widget, 'setValue'):  # QSpinBox, QDoubleSpinBox
                        widget.setValue(value)
                    elif hasattr(widget, 'setText'):  # QLineEdit
                        widget.setText(str(value))
                    elif hasattr(widget, 'setCurrentText'):  # QComboBox
                        widget.setCurrentText(str(value))
                except (ValueError, TypeError) as e:
                    print(f"Error loading synaptic receptors config for {key}: {e}")
