"""
Input patterns manager for Brian2 neural network simulator.
Handles user interactions and state management for input patterns configuration.
"""

from PyQt6.QtCore import QObject

class InputPatternsManager(QObject):
    """Manager for input patterns configuration and UI interactions."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
    def connect_signals(self):
        """Connect UI signals to handler methods."""
        # Connect the enabled checkbox
        if hasattr(self.main_window, 'input_patterns_forms'):
            enabled_widget = self.main_window.input_patterns_forms.get('enabled')
            if enabled_widget:
                enabled_widget.toggled.connect(self.on_enabled_changed)
                
            # Connect pattern type combo box
            pattern_type_widget = self.main_window.input_patterns_forms.get('pattern_type')
            if pattern_type_widget:
                pattern_type_widget.currentTextChanged.connect(self.on_pattern_type_changed)
    
    def on_enabled_changed(self, enabled):
        """Handle input patterns enabled/disabled state change."""
        # Enable/disable other input pattern controls
        if hasattr(self.main_window, 'input_patterns_forms'):
            for key, widget in self.main_window.input_patterns_forms.items():
                if key != 'enabled' and widget:
                    widget.setEnabled(enabled)
    
    def on_pattern_type_changed(self, pattern_type):
        """Handle pattern type selection change."""
        # This will be handled by the dependency system in BaseFormGenerator
        pass
    
    def get_input_patterns_config(self):
        """Get current input patterns configuration."""
        config = {}
        
        if hasattr(self.main_window, 'input_patterns_forms'):
            for key, widget in self.main_window.input_patterns_forms.items():
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
    
    def load_input_patterns_config(self, config):
        """Load input patterns configuration into UI."""
        if not hasattr(self.main_window, 'input_patterns_forms'):
            return
            
        for key, value in config.items():
            widget = self.main_window.input_patterns_forms.get(key)
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
                    print(f"Error loading input patterns config for {key}: {e}")
