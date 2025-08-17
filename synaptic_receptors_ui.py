# synaptic_receptors_ui.py
# UI components for synaptic receptors configuration in Brian2Sim GUI

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QGridLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from ui_forms import BaseFormGenerator
from synaptic_receptors_config import SYNAPTIC_RECEPTORS_CONFIG

def create_synaptic_receptors_group(main_window):
    """
    Creates the 'Synaptic Receptors' group box using config-driven approach.
    """
    synaptic_receptors_group = QGroupBox("Synaptic Receptors")
    synaptic_receptors_group.setToolTip("Configure AMPA, NMDA, GABA-A, and GABA-B synaptic receptors.")
    
    # Create form generator
    main_window.synaptic_receptors_form_generator = SynapticReceptorsFormGenerator(SYNAPTIC_RECEPTORS_CONFIG)
    
    # Get the form widget and set it as the layout
    form_widget = main_window.synaptic_receptors_form_generator.get_form_widget()
    if form_widget:
        synaptic_receptors_group.setLayout(form_widget.layout())
        
        # Store references to specific widgets for backward compatibility
        param_widgets = main_window.synaptic_receptors_form_generator.get_param_widgets()
        main_window.synaptic_receptors_enabled = param_widgets.get("enabled")
        
        # Connect parameter change signals
        for param_key, widget in param_widgets.items():
            if param_key != "enabled":  # Don't connect the main enable checkbox
                if hasattr(widget, 'valueChanged'):
                    widget.valueChanged.connect(main_window.synaptic_receptors_manager.on_param_changed)
                elif hasattr(widget, 'currentIndexChanged'):
                    widget.currentIndexChanged.connect(main_window.synaptic_receptors_manager.on_param_changed)

    return synaptic_receptors_group

class SynapticReceptorsFormGenerator(BaseFormGenerator):
    """Form generator for synaptic receptors configuration with checkbox visibility pattern."""
    
    def _create_forms(self):
        # Main widget for the whole section
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0,0,0,0)
        section_layout.setSpacing(5)

        param_widgets = {}
        self.param_labels["main"] = {}
        self.cell_widgets["main"] = {}

        # Create the params group widget
        self.params_group_widget = QWidget()

        # Check if "enabled" toggle exists in config
        has_enabled_toggle = "enabled" in self.config
        
        if has_enabled_toggle:
            enabled_config = self.config["enabled"]
            enable_checkbox = self._create_widget_for_param("enabled", enabled_config)
            
            if enable_checkbox:
                enable_layout = QHBoxLayout()
                enable_layout.setContentsMargins(8, 5, 0, 5)
                enable_layout.addWidget(enable_checkbox)
                
                default_enable_label = "Enable Synaptic Receptors"
                enable_label_text = enabled_config.get("label", default_enable_label)
                enable_label = QLabel(enable_label_text)
                enable_layout.addWidget(enable_label)
                enable_layout.addStretch()
                section_layout.addLayout(enable_layout)
                
                param_widgets["enabled"] = enable_checkbox
                
                # Connect checkbox to show/hide params group (only if it's actually a checkbox)
                if hasattr(enable_checkbox, 'stateChanged'):
                    enable_checkbox.stateChanged.connect(
                        lambda state: self.params_group_widget.setVisible(state == 2)
                    )
                    self.params_group_widget.setVisible(enable_checkbox.isChecked())
                else:
                    # If it's not a checkbox, assume it should always be visible
                    self.params_group_widget.setVisible(True)
        else:
            self.params_group_widget.setVisible(True)

        # Layout for parameters
        params_grid = QGridLayout(self.params_group_widget)
        params_grid.setSpacing(8)
        
        param_configs = {k: v for k, v in self.config.items() if k != "enabled"}
        num_cols = 3
        row, col = 0, 0
        
        for param_key, param_config_item in param_configs.items():
            input_widget = self._create_widget_for_param(param_key, param_config_item)
            
            if input_widget:
                cell_widget = QWidget()
                actual_label_text = param_config_item.get("label", param_key.replace("_", " ").title())
                label_for_param = QLabel(actual_label_text)
                label_for_param.setToolTip(param_config_item.get("tooltip", ""))

                cell_layout = QVBoxLayout(cell_widget)
                label_for_param.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
                cell_layout.addWidget(label_for_param)
                cell_layout.addWidget(input_widget)

                cell_layout.setContentsMargins(1, 1, 1, 1)
                params_grid.addWidget(cell_widget, row, col)
                param_widgets[param_key] = input_widget
                self.param_labels["main"][param_key] = label_for_param
                self.cell_widgets["main"][param_key] = cell_widget
                
                col += 1
                if col >= num_cols:
                    col, row = 0, row + 1
        
        section_layout.addWidget(self.params_group_widget)
        
        self.forms["main"] = section_widget
        self.param_widgets["main"] = param_widgets
        
        # Setup dependency handling for parameters with depends_on
        self._setup_dependencies()
