# synaptic_receptors_ui.py
# UI components for synaptic receptors configuration in Brian2Sim GUI

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from brian2sim.models.synaptic_receptors_config import SYNAPTIC_RECEPTORS_CONFIG
from brian2sim.ui.ui_forms import BaseFormGenerator


def create_synaptic_receptors_group(main_window):
    """
    Creates the 'Synaptic Receptors' group box using config-driven approach.
    """
    synaptic_receptors_group = QGroupBox("Synaptic Receptors")
    synaptic_receptors_group.setToolTip(
        "Configure AMPA, NMDA, GABA-A, and GABA-B synaptic receptors."
    )

    # Create form generator
    main_window.synaptic_receptors_form_generator = SynapticReceptorsFormGenerator(
        SYNAPTIC_RECEPTORS_CONFIG
    )
    # Alias for simulation_manager compatibility
    main_window.synaptic_receptors_ui = main_window.synaptic_receptors_form_generator

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
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(
                        main_window.synaptic_receptors_manager.on_param_changed
                    )
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(
                        main_window.synaptic_receptors_manager.on_param_changed
                    )

    return synaptic_receptors_group


class SynapticReceptorsFormGenerator(BaseFormGenerator):
    """Form generator for synaptic receptors configuration with grouped layout."""

    def _create_forms(self):
        # Main widget for the whole section
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(5)

        param_widgets = {}
        self.param_labels["main"] = {}
        self.cell_widgets["main"] = {}

        # Wrapper widget that holds all groups (to allow hiding everything when disabled)
        self.params_group_widget = QWidget()
        self.params_group_widget.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum
        )

        # Main vertical layout for the wrapper
        wrapper_layout = QVBoxLayout(self.params_group_widget)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(10)

        # 1. Handle Global "Enabled" Toggle
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

                # Connect checkbox to show/hide the whole wrapper
                if hasattr(enable_checkbox, "stateChanged"):
                    enable_checkbox.stateChanged.connect(
                        lambda state: self.params_group_widget.setVisible(state == 2)
                    )
                    self.params_group_widget.setVisible(enable_checkbox.isChecked())
                else:
                    self.params_group_widget.setVisible(True)
        else:
            self.params_group_widget.setVisible(True)

        # 2. Define Groups with Toggles
        # Format: "Title": { "toggle": "param_key", "keys": [...] }
        groups = {
            "AMPA Receptors": {
                "toggle": "ampa_enabled",
                "keys": ["ampa_tau_rise", "ampa_tau_decay", "ampa_reversal", "ampa_weight_ratio"],
            },
            "NMDA Receptors": {
                "toggle": "nmda_enabled",
                "keys": [
                    "nmda_tau_rise",
                    "nmda_tau_decay",
                    "nmda_reversal",
                    "nmda_mg_concentration",
                    "nmda_weight_ratio",
                ],
            },
            "GABA_A Receptors": {
                "toggle": "gaba_a_enabled",
                "keys": [
                    "gaba_a_tau_rise",
                    "gaba_a_tau_decay",
                    "gaba_a_reversal",
                    "gaba_a_weight_ratio",
                ],
            },
            "GABA_B Receptors": {
                "toggle": "gaba_b_enabled",
                "keys": [
                    "gaba_b_tau_rise",
                    "gaba_b_tau_decay",
                    "gaba_b_reversal",
                    "gaba_b_weight_ratio",
                ],
            },
        }

        # Keep track of handled keys
        processed_keys = set(["enabled"])

        # 3. Create Group Boxes
        for group_title, group_data in groups.items():
            toggle_key = group_data.get("toggle")
            group_keys = group_data.get("keys", [])

            group_box = QGroupBox(group_title)
            # Use a QVBoxLayout for the group to stack Checkbox on top of Grid
            group_main_layout = QVBoxLayout(group_box)
            group_main_layout.setSpacing(5)
            group_main_layout.setContentsMargins(10, 10, 10, 10)

            # 3a. Create Toggle (Enable Checkbox) if exists
            group_toggle_widget = None
            if toggle_key and toggle_key in self.config:
                toggle_config = self.config[toggle_key]
                # Force label to be explicit "Enable ..."
                toggle_widget = QCheckBox(f"Enable {group_title}")
                toggle_widget.setToolTip(toggle_config.get("tooltip", ""))

                # Load initial value
                default_val = toggle_config.get("default", False)
                toggle_widget.setChecked(default_val)

                group_main_layout.addWidget(toggle_widget)
                param_widgets[toggle_key] = toggle_widget
                processed_keys.add(toggle_key)
                group_toggle_widget = toggle_widget

            # 3b. Create Container for Parameters
            params_container = QWidget()
            params_grid = QGridLayout(params_container)
            params_grid.setSpacing(8)
            params_grid.setContentsMargins(0, 5, 0, 0)

            valid_keys = [k for k in group_keys if k in self.config]
            row, col = 0, 0
            num_cols = 2

            has_items = False
            for param_key in valid_keys:
                if self._add_param_to_grid(param_key, params_grid, row, col, param_widgets):
                    processed_keys.add(param_key)
                    has_items = True
                    col += 1
                    if col >= num_cols:
                        col, row = 0, row + 1

            if has_items:
                group_main_layout.addWidget(params_container)

                # Connect toggle to container visibility
                if group_toggle_widget:
                    group_toggle_widget.toggled.connect(params_container.setVisible)
                    params_container.setVisible(group_toggle_widget.isChecked())

                wrapper_layout.addWidget(group_box)
            elif group_toggle_widget:  # Show group even if only toggle exists
                wrapper_layout.addWidget(group_box)

        # 4. Handle Leftover Parameters
        leftover_keys = [k for k in self.config.keys() if k not in processed_keys]
        if leftover_keys:
            leftover_box = QGroupBox("Other Parameters")
            leftover_layout = QGridLayout(leftover_box)
            leftover_layout.setSpacing(8)
            row, col = 0, 0
            num_cols = 2

            for param_key in leftover_keys:
                if self._add_param_to_grid(param_key, leftover_layout, row, col, param_widgets):
                    col += 1
                    if col >= num_cols:
                        col, row = 0, row + 1

            wrapper_layout.addWidget(leftover_box)

        section_layout.addWidget(self.params_group_widget)
        section_layout.addStretch()

        self.forms["main"] = section_widget
        self.param_widgets["main"] = param_widgets

        self._setup_dependencies()

    def _add_param_to_grid(self, param_key, grid_layout, row, col, param_widgets):
        """Helper to create and add a parameter widget to a grid layout."""
        param_config_item = self.config.get(param_key)
        if not param_config_item:
            return False

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
            grid_layout.addWidget(cell_widget, row, col)

            param_widgets[param_key] = input_widget
            self.param_labels["main"][param_key] = label_for_param
            self.cell_widgets["main"][param_key] = cell_widget
            return True
        return False
