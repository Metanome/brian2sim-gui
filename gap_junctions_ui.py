# gap_junctions_ui.py
# UI components for gap junctions configuration in Brian2Sim GUI

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QGridLayout, QLabel
from ui_forms import BaseFormGenerator
from gap_junctions_config import GAP_JUNCTIONS_CONFIG

def create_gap_junctions_group(main_window):
    """
    Creates the 'Gap Junctions' group box using config-driven approach.
    """
    gap_junctions_group = QGroupBox("Gap Junctions")
    gap_junctions_group.setToolTip("Configure electrical coupling between neurons via gap junctions for synchronized activity.")
    
    # Create form generator
    main_window.gap_junctions_form_generator = GapJunctionsFormGenerator(GAP_JUNCTIONS_CONFIG)
    
    # Get the form widget and set it as the layout
    form_widget = main_window.gap_junctions_form_generator.get_form_widget()
    if form_widget:
        gap_junctions_group.setLayout(form_widget.layout())
        
        # Store references to specific widgets for backward compatibility
        param_widgets = main_window.gap_junctions_form_generator.get_param_widgets()
        main_window.gap_junctions_enabled = param_widgets.get("enabled")
        
        # Connect parameter change signals
        for param_key, widget in param_widgets.items():
            if param_key != "enabled":  # Don't connect the main enable checkbox
                if hasattr(widget, 'valueChanged'):
                    widget.valueChanged.connect(main_window.gap_junctions_manager.on_param_changed)
                elif hasattr(widget, 'currentIndexChanged'):
                    widget.currentIndexChanged.connect(main_window.gap_junctions_manager.on_param_changed)

    return gap_junctions_group

class GapJunctionsFormGenerator(BaseFormGenerator):
    """Form generator for gap junctions configuration using the same pattern as NoiseOptionsFormGenerator."""
    
    def _create_forms(self):
        """Create gap junctions configuration forms."""
        # Create main form layout similar to NoiseOptionsFormGenerator
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
            
            if input_widget:
                cell_widget = QWidget()
                cell_layout = QVBoxLayout(cell_widget)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.setSpacing(2)
                
                label_text = param_config.get("label", param_key.replace("_", " ").title())
                label = QLabel(label_text)
                label.setWordWrap(True)
                
                cell_layout.addWidget(label)
                cell_layout.addWidget(input_widget)
                
                params_layout.addWidget(cell_widget, row, col)
                
                param_widgets[param_key] = input_widget
                self.param_labels["main"][param_key] = label
                self.cell_widgets["main"][param_key] = cell_widget
                
                col += 1
                if col >= num_cols:
                    col = 0
                    row += 1
        
        main_layout.addWidget(params_container)
        main_layout.addStretch()
        
        self.param_widgets["main"] = param_widgets
        self.forms["main"] = main_widget
