"""
Input patterns UI components for Brian2 neural network simulator.
Creates user interface for configuring various input stimulation patterns.
"""

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QWidget
from ui_forms import BaseFormGenerator
from input_patterns_config import INPUT_PATTERNS_CONFIG

def create_input_patterns_group(main_window):
    """Create and return the input patterns configuration group."""
    group = QGroupBox("Input Patterns")
    layout = QVBoxLayout(group)
    
    # Create form using the base form generator
    form_generator = InputPatternsFormGenerator(INPUT_PATTERNS_CONFIG)
    form_widget = form_generator.get_form_widget()
    if form_widget:
        layout.addWidget(form_widget)
    
    # Store form generator reference
    main_window.input_patterns_form_generator = form_generator
    
    return group

class InputPatternsFormGenerator(BaseFormGenerator):
    """Form generator for input patterns configuration."""
    
    def __init__(self, config):
        super().__init__(config)
        
    def _create_forms(self):
        """Create input patterns configuration forms."""
        # Create a simple placeholder form to prevent errors
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Store the form widget properly (not as a dictionary)
        self.forms["main"] = main_widget
        self.param_widgets["main"] = {}
