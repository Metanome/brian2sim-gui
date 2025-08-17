from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLabel, QLineEdit, QDoubleSpinBox, QTextEdit, QComboBox, QSpinBox, QCheckBox,
    QGridLayout, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer

class BaseFormGenerator(QWidget):
    """Base class for all form generators with common functionality"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.forms = {}
        self.param_widgets = {}
        self.preset_combos = {}
        self.param_labels = {}
        self.cell_widgets = {}  # For form generators that use cell widgets (like NoiseOptions)
        self.dependency_handlers = {}
        self.initialized = False
        
        # Create forms for all form generators
        self._create_forms()
        self._setup_dependencies()
        self._handle_initial_visibility()
        self.initialized = True

    def _create_forms(self):
        """Default implementation of form creation - should be overridden by subclasses"""
        # This is a default implementation for when BaseFormGenerator is used directly
        pass

    def _handle_initial_visibility(self):
        """Handle initial visibility of all widgets based on their dependencies"""
            
        # Hide any widgets with dependencies
        for form_key in self.forms.keys():
            current_config = self.config.get(form_key) if isinstance(self.config.get(form_key), dict) and form_key in self.config else self.config
            param_widgets = self.get_param_widgets(form_key)
            param_labels = self.param_labels.get(form_key, {})
            
            for param_key, param_config in current_config.items():
                if isinstance(param_config, dict) and param_config.get("depends_on"):
                    widget = param_widgets.get(param_key)
                    label = param_labels.get(param_key)
                    if widget:
                        widget.setVisible(False)
                    if label:
                        label.setVisible(False)
        
        # Then update visibility based on current control values
        self._update_all_dependencies()

    def _create_widget_for_param(self, param_key, param_config):
        """Create appropriate widget based on parameter configuration"""
        param_type = param_config.get("type", str)
        default_value = param_config.get("default")
        tooltip = param_config.get("tooltip", "")
        min_val = param_config.get("min")
        max_val = param_config.get("max")
        step = param_config.get("step", 0.1)
        decimals = param_config.get("decimals", 3)
        
        input_widget = None
        
        if param_type == "bool":
            input_widget = QCheckBox()
            if default_value is not None:
                input_widget.setChecked(default_value)
        elif param_type == "int":
            input_widget = QSpinBox()
            if min_val is not None:
                input_widget.setMinimum(min_val)
            if max_val is not None:
                input_widget.setMaximum(max_val)
            if default_value is not None:
                input_widget.setValue(default_value)
        elif param_type == "double" or param_type == float:
            input_widget = QDoubleSpinBox()
            input_widget.setDecimals(decimals)
            input_widget.setSingleStep(step)
            if min_val is not None:
                input_widget.setMinimum(min_val)
            if max_val is not None:
                input_widget.setMaximum(max_val)
            if default_value is not None:
                input_widget.setValue(default_value)
        elif param_type == "combo":
            input_widget = QComboBox()
            options = param_config.get("options", [])
            display_options = param_config.get("display_options", options)
            for i, option in enumerate(options):
                display_text = display_options[i] if i < len(display_options) else option
                input_widget.addItem(display_text, userData=option)
            if default_value is not None and default_value in options:
                input_widget.setCurrentIndex(options.index(default_value))
        elif param_type == str and param_key == "custom_eqs":
            input_widget = QTextEdit()
            input_widget.setMinimumHeight(80)
            if default_value is not None: 
                input_widget.setPlaceholderText(default_value or "dv/dt = ...")
            else: 
                input_widget.setPlaceholderText("dv/dt = ...")
        elif param_type == str:
            input_widget = QLineEdit()
            if default_value is not None: 
                input_widget.setPlaceholderText(str(default_value))
        else:
            input_widget = QLineEdit()
            if default_value is not None: 
                input_widget.setPlaceholderText(str(default_value))
        
        if input_widget:
            input_widget.setToolTip(tooltip)
        
        return input_widget    
      
    def _setup_dependencies(self):
        """Setup dependency handling for conditional parameter visibility"""
            
        for form_key in self.forms.keys():
            param_widgets = self.get_param_widgets(form_key)
            param_labels = self.param_labels.get(form_key, {})
            current_config = self.config.get(form_key) if isinstance(self.config.get(form_key), dict) and form_key in self.config else self.config
            
            # Init handlers dict for this form
            if form_key not in self.dependency_handlers:
                self.dependency_handlers[form_key] = {}
            
            # Setup dependencies
            for param_key, param_config in current_config.items():
                if isinstance(param_config, dict) and param_config.get("depends_on"):
                    widget = param_widgets.get(param_key)
                    label = param_labels.get(param_key)
                    
                    for ctrl_param, expected_val in param_config["depends_on"].items():
                        ctrl_widget = param_widgets.get(ctrl_param)
                        if ctrl_widget and widget:
                            def make_handler(c_widget, target_widget, target_label, exp_val):
                                def handler():
                                    current_val = None
                                    if hasattr(c_widget, 'currentData'):
                                        current_val = c_widget.currentData()
                                    elif hasattr(c_widget, 'currentText'):
                                        current_val = c_widget.currentText()
                                    elif hasattr(c_widget, 'isChecked'):
                                        current_val = c_widget.isChecked()
                                    
                                    # Handle both single values and lists of expected values
                                    if isinstance(exp_val, list):
                                        show = current_val in exp_val
                                    else:
                                        show = (current_val == exp_val)
                                        
                                    if target_widget:
                                        target_widget.setVisible(show)
                                    if target_label:
                                        target_label.setVisible(show)
                                return handler
                            
                            h = make_handler(ctrl_widget, widget, label, expected_val)
                            self.dependency_handlers[form_key][f"{param_key}_{ctrl_param}"] = h
                            
                            if hasattr(ctrl_widget, 'currentIndexChanged'):
                                ctrl_widget.currentIndexChanged.connect(h)
                            elif hasattr(ctrl_widget, 'stateChanged'): 
                                ctrl_widget.stateChanged.connect(h)
                            elif hasattr(ctrl_widget, 'textChanged'):
                                ctrl_widget.textChanged.connect(h)
                                
                            # Set initial state
                            h()
            
    def _update_all_dependencies(self):
        """Update all dependency-based visibility"""
        for handlers in self.dependency_handlers.values():
            for h in handlers.values():
                if callable(h):
                    h()
                
    def connect_preset_reset(self, preset_combo, form_key_for_widgets="main", reset_callback=None):
        """Connect parameter changes to reset preset dropdown to 'Custom'"""
        if not preset_combo:
            return
            
        def reset_to_custom_state():
            if preset_combo.count() > 0 and preset_combo.currentIndex() != 0:
                 # Check if "Custom" or a similar placeholder is at index 0
                if "custom" in preset_combo.itemText(0).lower() or "select" in preset_combo.itemText(0).lower():
                    preset_combo.setCurrentIndex(0)
            if reset_callback:
                reset_callback()
        
        relevant_param_widgets = self.get_param_widgets(form_key_for_widgets)

        for param_key, widget in relevant_param_widgets.items():
            if widget == preset_combo: # Don't connect the preset combo to itself
                continue
            
            if hasattr(widget, 'valueChanged'): # QSpinBox, QDoubleSpinBox
                widget.valueChanged.connect(reset_to_custom_state)
            elif hasattr(widget, 'currentIndexChanged'): # QComboBox
                widget.currentIndexChanged.connect(reset_to_custom_state)
            elif hasattr(widget, 'stateChanged'): # QCheckBox
                widget.stateChanged.connect(reset_to_custom_state)
            elif hasattr(widget, 'textChanged'): # QLineEdit, QTextEdit
                widget.textChanged.connect(reset_to_custom_state)

    def get_form_widget(self, key=None):
        if key is None:
            return next(iter(self.forms.values())) if self.forms else None
        return self.forms.get(key)

    def get_param_widgets(self, key=None):
        if key is None:
            if "main" in self.param_widgets:
                 return self.param_widgets["main"]
            return next(iter(self.param_widgets.values())) if self.param_widgets else {}
        return self.param_widgets.get(key, {})
    
    def get_preset_combo(self, key=None):
        if key is None:
            if "main" in self.preset_combos:
                return self.preset_combos["main"]
            return next(iter(self.preset_combos.values())) if self.preset_combos else None
        return self.preset_combos.get(key)

    def load_params_from_config(self, config_data, key=None):
        param_widgets_to_load = self.get_param_widgets(key)
        for param_key, widget in param_widgets_to_load.items():
            value = config_data.get(param_key)
            if value is not None:
                if isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                elif isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(bool(value))
                elif isinstance(widget, QComboBox):
                    index = widget.findData(value)
                    if index != -1:
                        widget.setCurrentIndex(index)
                    else: # Fallback to text if itemData not used or value not found
                        index = widget.findText(str(value))
                        if index != -1:
                             widget.setCurrentIndex(index)
                elif isinstance(widget, QTextEdit):
                    widget.setText(str(value))
                elif isinstance(widget, QLineEdit):
                    widget.setText(str(value))
    
    def get_params_for_save(self, key=None):
        param_widgets_to_save = self.get_param_widgets(key)
        params_to_save = {}
        for param_key, widget in param_widgets_to_save.items():
            if isinstance(widget, QDoubleSpinBox):
                params_to_save[param_key] = widget.value()
            elif isinstance(widget, QSpinBox):
                params_to_save[param_key] = widget.value()
            elif isinstance(widget, QCheckBox):
                params_to_save[param_key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                params_to_save[param_key] = widget.currentData() # Assumes userData is set
                if params_to_save[param_key] is None: # Fallback if no userData
                    params_to_save[param_key] = widget.currentText()
            elif isinstance(widget, QTextEdit):
                params_to_save[param_key] = widget.toPlainText()
            elif isinstance(widget, QLineEdit):
                params_to_save[param_key] = widget.text()
        return params_to_save


class SimParamsFormGenerator(BaseFormGenerator):
    """Form generator for simulation parameters"""
    
    def _create_forms(self):
        # Main widget for the whole section, this will have QVBoxLayout
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0,0,0,0) # Use tight packing for the section

        # Container for the grid of parameters
        params_container_widget = QWidget()
        params_grid = QGridLayout(params_container_widget) # Grid layout on the container
        params_grid.setSpacing(8)
        
        param_widgets = {}
        self.param_labels["main"] = {} # Initialize labels for "main" form
        self.cell_widgets["main"] = {}  # Initialize cell widgets for dependency control
        
        num_cols = 3
        row, col = 0, 0
        
        for param_key, param_config_item in self.config.items():
            # Skip the hidden neuron_model control parameter
            if param_config_item.get("hidden", False):
                # Create a hidden combo box for neuron model sync
                input_widget = self._create_widget_for_param(param_key, param_config_item)
                param_widgets[param_key] = input_widget
                continue
                
            input_widget = self._create_widget_for_param(param_key, param_config_item)
            
            if input_widget:
                cell_widget = QWidget()
                actual_label_text = param_config_item.get("label", param_key.replace("_", " ").title())
                label_for_param = QLabel(actual_label_text)
                label_for_param.setToolTip(param_config_item.get("tooltip", ""))

                if isinstance(input_widget, QCheckBox):
                    cell_layout = QHBoxLayout(cell_widget)
                    input_widget.setToolTip(param_config_item.get("tooltip", ""))
                    cell_layout.addWidget(input_widget) # Checkbox first
                    cell_layout.addWidget(label_for_param) # Then its label
                    cell_layout.addStretch()
                else:
                    # Standard layout: Label on top, input below
                    cell_layout = QVBoxLayout(cell_widget)
                    label_for_param.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
                    cell_layout.addWidget(label_for_param)
                    cell_layout.addWidget(input_widget)
                
                cell_layout.setContentsMargins(1, 1, 1, 1)
                params_grid.addWidget(cell_widget, row, col)
                
                param_widgets[param_key] = input_widget
                self.param_labels["main"][param_key] = label_for_param # Store the QLabel
                self.cell_widgets["main"][param_key] = cell_widget  # Store cell widget for dependency control

                if param_config_item.get("initially_hidden", False) or param_config_item.get("depends_on"):
                    cell_widget.setVisible(False)

                col += 1
                if col >= num_cols:
                    col, row = 0, row + 1
        
        section_layout.addWidget(params_container_widget) # Add grid container to section layout
        self.forms["main"] = section_widget # This is the main widget for the form
        self.param_widgets["main"] = param_widgets

    def _setup_dependencies(self):
        """Override dependency setup to handle cell widgets in grid layout like NoiseOptionsFormGenerator"""
        for form_key in self.forms.keys():
            param_widgets = self.get_param_widgets(form_key)
            param_labels = self.param_labels.get(form_key, {})
            cell_widgets = self.cell_widgets.get(form_key, {})
            current_config = self.config.get(form_key) if isinstance(self.config.get(form_key), dict) and form_key in self.config else self.config
            
            # Init handlers dict for this form
            if form_key not in self.dependency_handlers:
                self.dependency_handlers[form_key] = {}
            
            # Setup dependencies
            for param_key, param_config in current_config.items():
                if isinstance(param_config, dict) and param_config.get("depends_on"):
                    widget = param_widgets.get(param_key)
                    label = param_labels.get(param_key)
                    cell_widget = cell_widgets.get(param_key)  # Get cell widget for this parameter
                    
                    for ctrl_param, expected_val in param_config["depends_on"].items():
                        ctrl_widget = param_widgets.get(ctrl_param)
                        if ctrl_widget and (widget or cell_widget):
                            def make_handler(c_widget, target_widget, target_label, target_cell, exp_val):
                                def handler():
                                    current_val = None
                                    if hasattr(c_widget, 'currentData'):
                                        current_val = c_widget.currentData()                                    
                                    elif hasattr(c_widget, 'currentText'):
                                        current_val = c_widget.currentText()
                                    elif hasattr(c_widget, 'isChecked'):
                                        current_val = c_widget.isChecked()
                                    
                                    # Calculate show status for all widget types
                                    if isinstance(exp_val, list):
                                        show = current_val in exp_val
                                    else:
                                        show = (current_val == exp_val)
                                    
                                    # For sim params, control cell widget visibility if available
                                    if target_cell:
                                        # Try a more aggressive approach for QGridLayout
                                        grid_layout = target_cell.parent().layout()
                                        if grid_layout and hasattr(grid_layout, 'indexOf'):
                                            # Get the current position of the widget in the grid
                                            index = grid_layout.indexOf(target_cell)                                            
                                            if index >= 0:
                                                row, col, row_span, col_span = grid_layout.getItemPosition(index)
                                                if show:
                                                    # For showing: ensure visibility and force layout update
                                                    target_cell.setVisible(True)
                                                    
                                                    # CRITICAL: Also make child widgets visible!
                                                    # Use findChildren with direct=True to only get direct children
                                                    direct_children = [child for child in target_cell.children() if isinstance(child, QWidget)]
                                                    for child in direct_children:
                                                        child.setVisible(True)
                                                    
                                                    # Also check all descendants for completeness
                                                    all_children = target_cell.findChildren(QWidget)
                                                    for child in all_children:
                                                        if not child.isVisible():
                                                            child.setVisible(True)
                                                    
                                                    # Remove and re-add to force grid layout to recalculate
                                                    grid_layout.removeWidget(target_cell)
                                                    grid_layout.addWidget(target_cell, row, col, row_span, col_span)
                                                    
                                                    # Force the cell widget to update its layout
                                                    if target_cell.layout():
                                                        target_cell.layout().invalidate()
                                                        target_cell.layout().activate()
                                                        target_cell.layout().update()
                                                    target_cell.updateGeometry()
                                                    target_cell.adjustSize()
                                                else:
                                                    # For hiding: just set invisible (children will be hidden automatically)
                                                    target_cell.setVisible(False)
                                                  
                                                # Force comprehensive grid layout refresh
                                                grid_layout.invalidate()
                                                grid_layout.activate()
                                                grid_layout.update()
                                                
                                                # Force parent widget updates
                                                parent = target_cell.parent()
                                                if parent:
                                                    parent.updateGeometry()
                                                    parent.update()
                                                    
                                                    # Also update grandparent
                                                    if parent.parent():
                                                        parent.parent().updateGeometry()
                                                        parent.parent().update()
                                            else:
                                                # Fallback to simple visibility
                                                target_cell.setVisible(show)
                                        else:
                                            target_cell.setVisible(show)
                                    else:
                                        # Fallback to individual widget control
                                        if target_widget:
                                            target_widget.setVisible(show)
                                        if target_label:
                                            target_label.setVisible(show)
                                return handler
                            
                            h = make_handler(ctrl_widget, widget, label, cell_widget, expected_val)
                            self.dependency_handlers[form_key][f"{param_key}_{ctrl_param}"] = h
                            
                            if hasattr(ctrl_widget, 'currentIndexChanged'):
                                ctrl_widget.currentIndexChanged.connect(h)
                            elif hasattr(ctrl_widget, 'stateChanged'): 
                                ctrl_widget.stateChanged.connect(h)
                            elif hasattr(ctrl_widget, 'textChanged'):
                                ctrl_widget.textChanged.connect(h)
                                  # Set initial state
                            h()

    def sync_neuron_model(self, neuron_model_key=None):
        """Synchronize the hidden neuron_model parameter with the main neuron model combo"""
        # If no model key provided, get current selection from main neuron model combo
        if neuron_model_key is None:
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'neuron_model_combo'):
                neuron_model_key = self.main_window.neuron_model_combo.currentData()
            else:
                return  # Can't sync without a model key
        
        param_widgets = self.get_param_widgets("main")
        neuron_model_widget = param_widgets.get("neuron_model")
        if neuron_model_widget and hasattr(neuron_model_widget, 'setCurrentText'):
            # Find the index for the model key
            index = neuron_model_widget.findData(neuron_model_key)
            if index >= 0:
                neuron_model_widget.setCurrentIndex(index)
            # Update all dependencies after sync
            self._update_all_dependencies()


class NoiseOptionsFormGenerator(BaseFormGenerator):
    """Form generator for noise options. Uses QVBoxLayout with an enable checkbox and a QGridLayout for params."""
    
    def __init__(self, config):
        super().__init__(config)
        self.cell_widgets = {}  # Store cell widgets for dependency control
    
    def _create_forms(self):
        # Main widget for the whole section
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0,0,0,0)
        section_layout.setSpacing(5) # Reduce spacing between items in this QVBoxLayout

        param_widgets = {}
        self.param_labels["main"] = {}
        self.cell_widgets["main"] = {}  # Initialize cell widgets for this form

        # Create the 'params_group_widget' that will contain the grid of parameters
        self.params_group_widget = QWidget() # Store as instance variable for access

        # Check if "enabled" toggle exists in config
        has_enabled_toggle = "enabled" in self.config
        
        if has_enabled_toggle:
            enabled_config = self.config["enabled"]
            enable_checkbox = self._create_widget_for_param("enabled", enabled_config)
            
            if enable_checkbox:
                enable_layout = QHBoxLayout()
                enable_layout.setContentsMargins(8, 5, 0, 5) # Add top/bottom margins
                enable_layout.addWidget(enable_checkbox)
                
                default_enable_label = "Enable Noise Options"
                enable_label_text = enabled_config.get("label", default_enable_label)
                enable_label = QLabel(enable_label_text)
                enable_layout.addWidget(enable_label)
                enable_layout.addStretch()
                section_layout.addLayout(enable_layout)
                
                param_widgets["enabled"] = enable_checkbox
                
                enable_checkbox.stateChanged.connect(
                    lambda state, wg=self.params_group_widget: wg.setVisible(state == Qt.CheckState.Checked.value)
                )
                # Set initial state of the group widget
                self.params_group_widget.setVisible(enable_checkbox.isChecked())
        else:
            # If no "enabled" toggle, the group is visible by default.
            self.params_group_widget.setVisible(True)

        # Layout for the parameters within the group widget
        params_grid = QGridLayout(self.params_group_widget) # Layout for the group widget
        params_grid.setSpacing(8)
        
        param_configs = {k: v for k, v in self.config.items() if k != "enabled"}
        num_cols = 2
        row, col = 0, 0
        
        for param_key, param_config_item in param_configs.items():
            input_widget = self._create_widget_for_param(param_key, param_config_item)
            
            if input_widget:
                cell_widget = QWidget()
                actual_label_text = param_config_item.get("label", param_key.replace("_", " ").title())
                label_for_param = QLabel(actual_label_text)
                label_for_param.setToolTip(param_config_item.get("tooltip", ""))

                if isinstance(input_widget, QCheckBox):
                    cell_layout = QHBoxLayout(cell_widget)
                    input_widget.setToolTip(param_config_item.get("tooltip", ""))
                    cell_layout.addWidget(input_widget) 
                    cell_layout.addWidget(label_for_param) 
                    cell_layout.addStretch()
                else:
                    cell_layout = QVBoxLayout(cell_widget)
                    label_for_param.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
                    cell_layout.addWidget(label_for_param)
                    cell_layout.addWidget(input_widget)

                cell_layout.setContentsMargins(1, 1, 1, 1)
                params_grid.addWidget(cell_widget, row, col)
                param_widgets[param_key] = input_widget
                self.param_labels["main"][param_key] = label_for_param
                self.cell_widgets["main"][param_key] = cell_widget  # Store cell widget for dependency control
                
                if param_config_item.get("depends_on"):
                    cell_widget.setVisible(False)
                
                col += 1
                if col >= num_cols:
                    col, row = 0, row + 1
        
        section_layout.addWidget(self.params_group_widget) # Add the group of parameters
        
        self.forms["main"] = section_widget
        self.param_widgets["main"] = param_widgets

    def _setup_dependencies(self):
        """Override dependency setup to handle cell widgets in grid layout"""
        for form_key in self.forms.keys():
            param_widgets = self.get_param_widgets(form_key)
            param_labels = self.param_labels.get(form_key, {})
            cell_widgets = self.cell_widgets.get(form_key, {})
            current_config = self.config.get(form_key) if isinstance(self.config.get(form_key), dict) and form_key in self.config else self.config
            
            # Init handlers dict for this form
            if form_key not in self.dependency_handlers:
                self.dependency_handlers[form_key] = {}
            
            # Setup dependencies
            for param_key, param_config in current_config.items():
                if isinstance(param_config, dict) and param_config.get("depends_on"):
                    widget = param_widgets.get(param_key)
                    label = param_labels.get(param_key)
                    cell_widget = cell_widgets.get(param_key)  # Get cell widget for this parameter
                    for ctrl_param, expected_val in param_config["depends_on"].items():
                        ctrl_widget = param_widgets.get(ctrl_param)
                        if ctrl_widget and (widget or cell_widget):
                            def make_handler(c_widget, target_widget, target_label, target_cell, exp_val):
                                def handler():
                                    current_val = None
                                    if hasattr(c_widget, 'currentData'):
                                        current_val = c_widget.currentData()                                    
                                    elif hasattr(c_widget, 'currentText'):
                                        current_val = c_widget.currentText()
                                    elif hasattr(c_widget, 'isChecked'):
                                        current_val = c_widget.isChecked()
                                    
                                    # Calculate show status for all widget types
                                    if isinstance(exp_val, list):
                                        show = current_val in exp_val
                                    else:
                                        show = (current_val == exp_val)
                                    
                                    # For noise options, control cell widget visibility if available
                                    if target_cell:
                                        # Try a more aggressive approach for QGridLayout
                                        grid_layout = target_cell.parent().layout()
                                        if grid_layout and hasattr(grid_layout, 'indexOf'):
                                            # Get the current position of the widget in the grid
                                            index = grid_layout.indexOf(target_cell)                                            
                                            if index >= 0:
                                                row, col, row_span, col_span = grid_layout.getItemPosition(index)
                                                if show:
                                                    # For showing: ensure visibility and force layout update
                                                    target_cell.setVisible(True)
                                                    
                                                    # CRITICAL: Also make child widgets visible!
                                                    # Use findChildren with direct=True to only get direct children
                                                    direct_children = [child for child in target_cell.children() if isinstance(child, QWidget)]
                                                    for child in direct_children:
                                                        child.setVisible(True)
                                                    
                                                    # Also check all descendants for completeness
                                                    all_children = target_cell.findChildren(QWidget)
                                                    for child in all_children:
                                                        if not child.isVisible():
                                                            child.setVisible(True)
                                                    
                                                    # Remove and re-add to force grid layout to recalculate
                                                    grid_layout.removeWidget(target_cell)
                                                    grid_layout.addWidget(target_cell, row, col, row_span, col_span)
                                                    
                                                    # Force the cell widget to update its layout
                                                    if target_cell.layout():
                                                        target_cell.layout().invalidate()
                                                        target_cell.layout().activate()
                                                        target_cell.layout().update()
                                                    target_cell.updateGeometry()
                                                    target_cell.adjustSize()
                                                else:
                                                    # For hiding: just set invisible (children will be hidden automatically)
                                                    target_cell.setVisible(False)
                                                  # Force comprehensive grid layout refresh
                                                grid_layout.invalidate()
                                                grid_layout.activate()
                                                grid_layout.update()
                                                
                                                # Force parent widget updates
                                                parent = target_cell.parent()
                                                if parent:
                                                    parent.updateGeometry()
                                                    parent.update()
                                                    
                                                    # Also update grandparent
                                                    if parent.parent():
                                                        parent.parent().updateGeometry()
                                                        parent.parent().update()
                                            else:
                                                # Fallback to simple visibility
                                                target_cell.setVisible(show)
                                        else:
                                            target_cell.setVisible(show)
                                    else:
                                        # Fallback to individual widget control
                                        if target_widget:
                                            target_widget.setVisible(show)
                                        if target_label:
                                            target_label.setVisible(show)
                                return handler
                            
                            h = make_handler(ctrl_widget, widget, label, cell_widget, expected_val)
                            self.dependency_handlers[form_key][f"{param_key}_{ctrl_param}"] = h
                            
                            if hasattr(ctrl_widget, 'currentIndexChanged'):
                                ctrl_widget.currentIndexChanged.connect(h)
                            elif hasattr(ctrl_widget, 'stateChanged'): 
                                ctrl_widget.stateChanged.connect(h)
                            elif hasattr(ctrl_widget, 'textChanged'):
                                ctrl_widget.textChanged.connect(h)
                                
                            # Set initial state
                            h()


class NetworkOptionsFormGenerator(BaseFormGenerator):
    """Form generator for network options. Uses QVBoxLayout with an enable checkbox and QFormLayout for params."""
    
    def _create_forms(self):
        # Main widget for the whole section
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0,0,0,0)
        section_layout.setSpacing(5)

        param_widgets = {}
        self.param_labels["main"] = {}

        # Create the params group widget that will contain all the parameter widgets
        self.params_group_widget = QWidget()        # Check if "enabled" toggle exists in config
        has_enabled_toggle = "enabled" in self.config
        if has_enabled_toggle:
            enabled_config = self.config["enabled"]
            enable_checkbox = self._create_widget_for_param("enabled", enabled_config)
            
            if enable_checkbox:
                enable_layout = QHBoxLayout()
                enable_layout.setContentsMargins(8, 5, 0, 5)
                enable_layout.addWidget(enable_checkbox)
                
                enable_label_text = enabled_config.get("label", "Enable Network Options")
                enable_label = QLabel(enable_label_text)
                enable_layout.addWidget(enable_label)
                enable_layout.addStretch()
                section_layout.addLayout(enable_layout)
                
                param_widgets["enabled"] = enable_checkbox
                enable_checkbox.stateChanged.connect(
                    lambda state, wg=self.params_group_widget: wg.setVisible(state == Qt.CheckState.Checked.value)                )
                # Set initial state of the group widget
                self.params_group_widget.setVisible(enable_checkbox.isChecked())
        else:
            # If no enabled toggle, group is visible by default
            self.params_group_widget.setVisible(True)

        # Create form layout for parameters
        params_form_layout = QFormLayout(self.params_group_widget)
        params_form_layout.setSpacing(8)
        
        # Filter out enabled config and process remaining parameters
        param_configs = {k: v for k, v in self.config.items() if k != "enabled"}
        for param_key, param_config_item in param_configs.items():
            label_text = param_config_item.get("label", param_key.replace("_", " ").title())
            input_widget = self._create_widget_for_param(param_key, param_config_item)
            
            if input_widget:
                label_widget = QLabel(label_text)
                label_widget.setToolTip(param_config_item.get("tooltip", ""))                
                params_form_layout.addRow(label_widget, input_widget)
                param_widgets[param_key] = input_widget
                self.param_labels["main"][param_key] = label_widget
                  # Set initial visibility based on whether this parameter depends on others
                if param_config_item.get("depends_on"):
                    label_widget.setVisible(False)
                    input_widget.setVisible(False)
        
        section_layout.addWidget(self.params_group_widget)
        self.forms["main"] = section_widget
        self.param_widgets["main"] = param_widgets

        network_topology_widget = param_widgets.get("network_topology")
        if network_topology_widget:
            network_topology_widget.currentIndexChanged.connect(self._update_all_dependencies)


class AdvancedNetworkFormGenerator(BaseFormGenerator):
    """Form generator for advanced network features"""
    
    def _create_forms(self):
        for section_key, section_config_dict in self.config.items():
            if not isinstance(section_config_dict, dict):
                continue

            section_widget = QWidget()
            section_main_layout = QVBoxLayout(section_widget)
            section_main_layout.setContentsMargins(0,0,0,0)
            section_main_layout.setSpacing(5)
                        
            section_param_widgets = {}
            self.param_labels[section_key] = {} 

            params_group_widget = QWidget() 

            has_enabled_toggle = "enabled" in section_config_dict
            if has_enabled_toggle:
                enabled_config = section_config_dict["enabled"]
                section_enable_checkbox = self._create_widget_for_param(f"{section_key}_enabled", enabled_config)
                
                if section_enable_checkbox:
                    enable_layout = QHBoxLayout()
                    enable_layout.addWidget(section_enable_checkbox)
                    
                    default_enable_label = f"Enable {section_key.replace('_', ' ').title()}"
                    enable_label_text = enabled_config.get("label", default_enable_label)
                    enable_label = QLabel(enable_label_text)
                    enable_layout.addWidget(enable_label)    
                    enable_layout.addStretch()
                    section_main_layout.addLayout(enable_layout)
                    
                    section_param_widgets["enabled"] = section_enable_checkbox

                    section_enable_checkbox.stateChanged.connect(
                        lambda state, wg=params_group_widget: wg.setVisible(state == Qt.CheckState.Checked.value)
                    )
                    params_group_widget.setVisible(section_enable_checkbox.isChecked())
            else:
                params_group_widget.setVisible(True)
            
            form_layout = QFormLayout(params_group_widget) 
            form_layout.setSpacing(8)
            
            param_configs_for_form = {k: v for k, v in section_config_dict.items() if k != "enabled"}
            for param_key, param_config_item in param_configs_for_form.items():
                if not isinstance(param_config_item, dict):
                    continue 

                label_text = param_config_item.get("label", param_key.replace("_", " ").title())
                input_widget = self._create_widget_for_param(param_key, param_config_item)
                
                if input_widget:
                    label_widget = QLabel(label_text)
                    label_widget.setToolTip(param_config_item.get("tooltip", ""))
                    form_layout.addRow(label_widget, input_widget)
                    
                    section_param_widgets[param_key] = input_widget
                    self.param_labels[section_key][param_key] = label_widget
                    
                    # Start hidden if has dependencies
                    if param_config_item.get("depends_on"):
                        label_widget.setVisible(False)
                        input_widget.setVisible(False)
            
            section_main_layout.addWidget(params_group_widget)
            
            self.forms[section_key] = section_widget
            self.param_widgets[section_key] = section_param_widgets
            
            # Setup special handlers for parameter updates (like STDP type changing values)
            self._setup_parameter_update_handlers(section_key, section_param_widgets)
    
    def _setup_parameter_update_handlers(self, section_key, param_widgets):
        """Setup handlers for dropdowns that should update other parameter values"""
        if section_key == "stdp":
            # Handle STDP type changes to update parameter defaults
            stdp_type_widget = param_widgets.get("stdp_type")
            if stdp_type_widget:
                stdp_type_widget.currentIndexChanged.connect(
                    lambda: self._update_stdp_parameters(param_widgets)
                )
    
    def _update_stdp_parameters(self, param_widgets):
        """Update STDP parameter values based on selected STDP type"""
        from advanced_network_config import STDP_TYPE_DEFAULTS
        
        stdp_type_widget = param_widgets.get("stdp_type")
        if not stdp_type_widget:
            return
            
        stdp_type = stdp_type_widget.currentData()
        if not stdp_type or stdp_type not in STDP_TYPE_DEFAULTS:
            return
            
        defaults = STDP_TYPE_DEFAULTS[stdp_type]
        
        # Update each parameter widget with the new default value
        for param_name, default_value in defaults.items():
            widget = param_widgets.get(param_name)
            if widget and hasattr(widget, 'setValue'):
                widget.setValue(default_value)


class NeuronModelFormGenerator(BaseFormGenerator):
    """Form generator for neuron models - uses QFormLayout per model."""
    
    def __init__(self, neuron_models_config):
        self.neuron_models_config = neuron_models_config 
        self.model_forms = {} 
        self.model_param_widgets = {} 
        self.model_preset_combos = {} 
        super().__init__(neuron_models_config)

    def _create_forms(self):
        for model_key, model_config_dict in self.config.items():
            model_widget = QWidget()
            params_form_layout = QFormLayout(model_widget)
            params_form_layout.setSpacing(8)
            
            current_model_param_widgets = {}
            # Initialize param_labels for this model_key
            self.param_labels[model_key] = {}

            # Parameters for the current model
            model_actual_params = model_config_dict.get("params", {})
            for param_key, param_config_item in model_actual_params.items():
                label_text = param_config_item.get("label", param_key.replace("_", " ").title())
                input_widget = self._create_widget_for_param(param_key, param_config_item)
                
                if input_widget:
                    label_widget = QLabel(label_text)
                    label_widget.setToolTip(param_config_item.get("tooltip", ""))
                    params_form_layout.addRow(label_widget, input_widget)
                    
                    current_model_param_widgets[param_key] = input_widget
                    self.param_labels[model_key][param_key] = label_widget

                    if param_config_item.get("depends_on"):
                        label_widget.setVisible(False)
                        input_widget.setVisible(False)
            
            self.model_forms[model_key] = model_widget
            self.model_param_widgets[model_key] = current_model_param_widgets

            # Preset combo for this model
            preset_combo = QComboBox()
            preset_combo.addItem("-- Select Preset --")
            if model_config_dict.get("presets"):
                for preset_name in model_config_dict["presets"].keys():
                    preset_combo.addItem(preset_name)
            self.model_preset_combos[model_key] = preset_combo

    # Overridden methods to work with per-model_key structure
    def get_form_widget(self, model_key):
        return self.model_forms.get(model_key)

    def get_param_widgets(self, model_key):
        return self.model_param_widgets.get(model_key, {})
    
    def get_preset_combo(self, model_key):
        return self.model_preset_combos.get(model_key)

    def load_params_from_config(self, model_key, config_data):
        param_widgets_to_load = self.get_param_widgets(model_key)
        for param_key, widget in param_widgets_to_load.items():
            value = config_data.get(param_key)
            if value is not None:
                if isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                elif isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(bool(value))
                elif isinstance(widget, QComboBox):
                    index = widget.findData(value)
                    if index != -1:
                        widget.setCurrentIndex(index)
                    else:
                        index = widget.findText(str(value))
                        if index != -1:
                             widget.setCurrentIndex(index)
                elif isinstance(widget, QTextEdit):
                    widget.setText(str(value))
                elif isinstance(widget, QLineEdit):
                    widget.setText(str(value))
    
    def get_params_for_save(self, model_key):
        param_widgets_to_save = self.get_param_widgets(model_key)
        params_to_save = {}
        for param_key, widget in param_widgets_to_save.items():
            if isinstance(widget, QDoubleSpinBox):
                params_to_save[param_key] = widget.value()
            elif isinstance(widget, QSpinBox):
                params_to_save[param_key] = widget.value()
            elif isinstance(widget, QCheckBox):
                params_to_save[param_key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                params_to_save[param_key] = widget.currentData()
                if params_to_save[param_key] is None:
                    params_to_save[param_key] = widget.currentText()
            elif isinstance(widget, QTextEdit):
                params_to_save[param_key] = widget.toPlainText()
            elif isinstance(widget, QLineEdit):
                params_to_save[param_key] = widget.text()
        return params_to_save

    def apply_preset(self, model_key, preset_name):
        """Applies a preset to the specified neuron model's form."""
        model_config_data = self.neuron_models_config.get(model_key, {})
        presets = model_config_data.get("presets", {})
        preset_values = presets.get(preset_name)

        if preset_values:
            self.load_params_from_config(model_key, preset_values)
            preset_combo = self.get_preset_combo(model_key)
            if preset_combo:
                 idx = preset_combo.findText(preset_name)
                 if idx != -1:
                      preset_combo.setCurrentIndex(idx)

def create_widget_from_config(param_key, param_config):
    """
    Helper function to create widgets for standalone UI components.
    This is a simple wrapper around the BaseFormGenerator's widget creation logic.
    """
    # Create a simple mock generator instance to access the method without full initialization
    class MockFormGenerator:
        def __init__(self):
            pass
            
        def _create_widget_for_param(self, param_key, param_config):
            """Create appropriate widget based on parameter configuration"""
            param_type = param_config.get("type", str)
            default_value = param_config.get("default")
            tooltip = param_config.get("tooltip", "")
            min_val = param_config.get("min")
            max_val = param_config.get("max")
            step = param_config.get("step", 0.1)
            decimals = param_config.get("decimals", 3)
            
            input_widget = None
            
            if param_type == "bool" or param_type == "checkbox":
                input_widget = QCheckBox()
                if default_value is not None:
                    input_widget.setChecked(default_value)
            elif param_type == "int":
                input_widget = QSpinBox()
                if min_val is not None:
                    input_widget.setMinimum(min_val)
                if max_val is not None:
                    input_widget.setMaximum(max_val)
                if default_value is not None:
                    input_widget.setValue(default_value)
            elif param_type == "double" or param_type == "spinbox" or param_type == float:
                input_widget = QDoubleSpinBox()
                input_widget.setDecimals(decimals)
                input_widget.setSingleStep(step)
                if min_val is not None:
                    input_widget.setMinimum(min_val)
                if max_val is not None:
                    input_widget.setMaximum(max_val)
                if default_value is not None:
                    input_widget.setValue(default_value)
            elif param_type == "combo":
                input_widget = QComboBox()
                options = param_config.get("options", [])
                display_options = param_config.get("display_options", options)
                for i, option in enumerate(options):
                    display_text = display_options[i] if i < len(display_options) else option
                    input_widget.addItem(display_text, userData=option)
                if default_value is not None and default_value in options:
                    input_widget.setCurrentIndex(options.index(default_value))
            elif param_config.get("widget") == "text_area" or (param_type == str and param_key == "custom_eqs"):
                input_widget = QTextEdit()
                input_widget.setMinimumHeight(80)
                if default_value is not None: 
                    input_widget.setPlaceholderText(default_value or "dv/dt = ...")
                else: 
                    input_widget.setPlaceholderText("dv/dt = ...")
            elif "choices" in param_config:
                input_widget = QComboBox()
                input_widget.addItems(param_config["choices"])
                default_choice = param_config.get("default")
                if default_choice and default_choice in param_config["choices"]:
                    input_widget.setCurrentText(default_choice)
            else:  # Default to string/line edit
                input_widget = QLineEdit()
                if default_value is not None: 
                    input_widget.setPlaceholderText(str(default_value))
            
            if input_widget:
                input_widget.setToolTip(tooltip)
            
            return input_widget
    
    # Use the mock generator to create the widget
    mock_generator = MockFormGenerator()
    return mock_generator._create_widget_for_param(param_key, param_config)