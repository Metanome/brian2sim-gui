# neuromodulation_ui.py
# UI components for neuromodulation configuration in Brian2Sim GUI

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QGridLayout, QLabel
from ui_forms import BaseFormGenerator
from neuromodulation_config import NEUROMODULATION_CONFIG

def create_neuromodulation_group(main_window):
    """
    Creates the 'Neuromodulation' group box using config-driven approach.
    """
    neuromodulation_group = QGroupBox("Neuromodulation")
    neuromodulation_group.setToolTip("Configure neuromodulatory systems including dopamine, serotonin, acetylcholine, and noradrenaline.")
    
    # Create form generator
    main_window.neuromodulation_form_generator = NeuromodulationFormGenerator(NEUROMODULATION_CONFIG)
    
    # Get the form widget and set it as the layout
    form_widget = main_window.neuromodulation_form_generator.get_form_widget()
    if form_widget:
        neuromodulation_group.setLayout(form_widget.layout())
        
        # Store references to specific widgets for backward compatibility
        param_widgets = main_window.neuromodulation_form_generator.get_param_widgets()
        main_window.neuromodulation_enabled = param_widgets.get("enabled")
        
        # Connect signals to manager
        for param_key, widget in param_widgets.items():
            if hasattr(widget, 'valueChanged'):
                widget.valueChanged.connect(main_window.neuromodulation_manager.on_param_changed)
            elif hasattr(widget, 'currentIndexChanged'):
                widget.currentIndexChanged.connect(main_window.neuromodulation_manager.on_param_changed)
            elif hasattr(widget, 'stateChanged'):
                widget.stateChanged.connect(main_window.neuromodulation_manager.on_param_changed)

    return neuromodulation_group

class NeuromodulationFormGenerator(BaseFormGenerator):
    """Form generator for neuromodulation configuration using the same pattern as other working generators."""
    
    def _create_forms(self):
        """Create neuromodulation configuration forms."""
        # Create main form layout similar to other generators
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container for parameters
        params_container = QWidget()
        params_layout = QGridLayout(params_container)
        params_layout.setSpacing(8)
        
        param_widgets = {}
        self.param_labels["main"] = {}
        self.cell_widgets["main"] = {}
        
        row, col = 0, 0
        num_cols = 3
        
        for param_key, param_config in self.config.items():
            input_widget = self._create_widget_for_param(param_key, param_config)
            param_widgets[param_key] = input_widget
            
            # Add to layout
            params_layout.addWidget(input_widget, row, col)
            
            # Move to next position
            col += 1
            if col >= num_cols:
                col = 0
                row += 1
        
        # Store widgets
        self.param_widgets["main"] = param_widgets
        
        # Add container to main layout
        main_layout.addWidget(params_container)
        
        # Store the main widget
        self.forms["main"] = main_widget
