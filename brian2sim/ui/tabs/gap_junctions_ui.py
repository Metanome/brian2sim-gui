# gap_junctions_ui.py
# UI components for gap junctions configuration in Brian2Sim GUI

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

from brian2sim.models.gap_junctions_config import GAP_JUNCTIONS_CONFIG
from brian2sim.ui.ui_forms import BaseFormGenerator


def create_gap_junctions_group(main_window):
    """
    Creates the 'Gap Junctions' group box using config-driven approach.
    """
    gap_junctions_group = QGroupBox("Gap Junctions")
    gap_junctions_group.setToolTip(
        "Configure electrical coupling between neurons via gap junctions for synchronized activity."
    )

    # Create form generator
    main_window.gap_junctions_form_generator = GapJunctionsFormGenerator(GAP_JUNCTIONS_CONFIG)
    # Alias for simulation_manager compatibility
    main_window.gap_junctions_ui = main_window.gap_junctions_form_generator

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
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(main_window.gap_junctions_manager.on_param_changed)
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(
                        main_window.gap_junctions_manager.on_param_changed
                    )

    return gap_junctions_group


class GapJunctionsFormGenerator(BaseFormGenerator):
    """Form generator for gap junctions configuration with checkbox visibility pattern."""

    def _create_forms(self):
        # Main widget for the whole section
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(5)

        param_widgets = {}
        self.param_labels["main"] = {}
        self.cell_widgets["main"] = {}

        # Wrapper widget
        self.params_group_widget = QWidget()
        self.params_group_widget.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum
        )

        # 1. Main Enable Toggle
        # 1. Main Enable Toggle
        has_enabled_toggle = "enabled" in self.config
        if has_enabled_toggle:
            enabled_config = self.config["enabled"]
            enable_checkbox = self._create_widget_for_param("enabled", enabled_config)

            if enable_checkbox:
                enable_layout = QHBoxLayout()
                enable_layout.setContentsMargins(8, 5, 0, 5)
                enable_layout.addWidget(enable_checkbox)

                default_enable_label = "Enable Gap Junctions"
                enable_label_text = enabled_config.get("label", default_enable_label)
                enable_label = QLabel(enable_label_text)
                enable_layout.addWidget(enable_label)
                enable_layout.addStretch()
                section_layout.addLayout(enable_layout)

                param_widgets["enabled"] = enable_checkbox

                if hasattr(enable_checkbox, "stateChanged"):
                    enable_checkbox.stateChanged.connect(
                        lambda state: self.params_group_widget.setVisible(state == 2)
                    )
                    self.params_group_widget.setVisible(enable_checkbox.isChecked())
                else:
                    self.params_group_widget.setVisible(True)
        else:
            self.params_group_widget.setVisible(True)

        section_layout.addWidget(self.params_group_widget)

        # 2. Define Groups
        groups = {
            "General Properties": {
                "keys": [
                    "conductance",
                    "connection_probability",
                    "max_distance",
                    "junction_type",
                    "coupling_coefficient",
                    "connection_specificity",
                    "spatial_organization",
                    "cluster_size",
                ]
            },
            "Voltage-Dependent Gating": {
                "toggle": "voltage_dependence",
                "keys": ["gating_voltage", "gating_slope"],
            },
            "Developmental Changes": {
                "toggle": "developmental_changes",
                "keys": ["initial_conductance", "final_conductance", "development_time_constant"],
            },
            "Activity-Dependent Plasticity": {
                "toggle": "activity_dependent",
                "keys": ["plasticity_threshold", "potentiation_rate", "depression_rate"],
            },
            "Neuromodulation": {
                "toggle": "neuromodulation",
                "keys": ["dopamine_modulation", "noradrenaline_modulation"],
            },
            "Junction Noise": {
                "toggle": "junction_noise",
                "keys": ["noise_amplitude", "correlation_time"],
            },
        }

        processed_keys = set(["enabled"])
        wrapper_layout = QVBoxLayout(self.params_group_widget)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(10)

        # 3. Create Group Boxes
        for group_title, group_data in groups.items():
            toggle_key = group_data.get("toggle")
            group_keys = group_data.get("keys", [])

            group_box = QGroupBox(group_title)
            group_main_layout = QVBoxLayout(group_box)
            group_main_layout.setSpacing(5)
            group_main_layout.setContentsMargins(10, 10, 10, 10)

            # 3a. Create Toggle
            group_toggle_widget = None
            if toggle_key and toggle_key in self.config:
                toggle_config = self.config[toggle_key]
                toggle_widget = QCheckBox(f"Enable {group_title}")
                toggle_widget.setToolTip(toggle_config.get("tooltip", ""))
                toggle_widget.setChecked(toggle_config.get("default", False))

                group_main_layout.addWidget(toggle_widget)
                param_widgets[toggle_key] = toggle_widget
                processed_keys.add(toggle_key)
                group_toggle_widget = toggle_widget

            # 3b. Create Container
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
                if group_toggle_widget:
                    group_toggle_widget.toggled.connect(params_container.setVisible)
                    params_container.setVisible(group_toggle_widget.isChecked())
                wrapper_layout.addWidget(group_box)
            elif group_toggle_widget:
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

        section_layout.addStretch()

        self.forms["main"] = section_widget
        self.param_widgets["main"] = param_widgets

        self._setup_dependencies()
