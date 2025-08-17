# homeostatic_plasticity_ui.py
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QGridLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from ui_forms import BaseFormGenerator
from homeostatic_plasticity_config import HOMEOSTATIC_PLASTICITY_CONFIG

def create_homeostatic_plasticity_group(main_window):
    homeostatic_plasticity_group = QGroupBox("Homeostatic Plasticity")
    homeostatic_plasticity_group.setToolTip("Configure homeostatic regulation mechanisms.")
    main_window.homeostatic_plasticity_form_generator = HomeostaticPlasticityFormGenerator(HOMEOSTATIC_PLASTICITY_CONFIG)
    form_widget = main_window.homeostatic_plasticity_form_generator.get_form_widget()
    if form_widget:
        homeostatic_plasticity_group.setLayout(form_widget.layout())
        param_widgets = main_window.homeostatic_plasticity_form_generator.get_param_widgets()
        main_window.homeostatic_plasticity_enabled = param_widgets.get("enabled")
        for param_key, widget in param_widgets.items():
            if param_key != "enabled":
                if hasattr(widget, 'valueChanged'):
                    widget.valueChanged.connect(main_window.homeostatic_plasticity_manager.on_param_changed)
                elif hasattr(widget, 'currentIndexChanged'):
                    widget.currentIndexChanged.connect(main_window.homeostatic_plasticity_manager.on_param_changed)
    return homeostatic_plasticity_group

class HomeostaticPlasticityFormGenerator(BaseFormGenerator):
    """Form generator for homeostatic plasticity configuration with checkbox visibility pattern."""
    
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
                
                default_enable_label = "Enable Homeostatic Plasticity"
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
