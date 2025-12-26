# short_term_plasticity_ui.py
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

from brian2sim.models.short_term_plasticity_config import SHORT_TERM_PLASTICITY_CONFIG
from brian2sim.ui.ui_forms import BaseFormGenerator


def create_short_term_plasticity_group(main_window):
    short_term_plasticity_group = QGroupBox("Short-Term Plasticity")
    short_term_plasticity_group.setToolTip("Configure facilitation and depression mechanisms.")
    main_window.short_term_plasticity_form_generator = ShortTermPlasticityFormGenerator(
        SHORT_TERM_PLASTICITY_CONFIG
    )
    # Alias for simulation_manager compatibility
    main_window.short_term_plasticity_ui = main_window.short_term_plasticity_form_generator
    form_widget = main_window.short_term_plasticity_form_generator.get_form_widget()
    if form_widget:
        short_term_plasticity_group.setLayout(form_widget.layout())
        param_widgets = main_window.short_term_plasticity_form_generator.get_param_widgets()
        main_window.short_term_plasticity_enabled = param_widgets.get("enabled")
        for param_key, widget in param_widgets.items():
            if param_key != "enabled":
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(
                        main_window.short_term_plasticity_manager.on_param_changed
                    )
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(
                        main_window.short_term_plasticity_manager.on_param_changed
                    )
    return short_term_plasticity_group


class ShortTermPlasticityFormGenerator(BaseFormGenerator):
    """Form generator for short-term plasticity configuration with checkbox visibility pattern."""

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

                default_enable_label = "Enable Short-Term Plasticity"
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
            "Plasticity Model": {"keys": ["plasticity_type"]},
            "Tsodyks-Markram Parameters": {
                "keys": ["tm_U", "tm_tau_d", "tm_tau_f"],
                "model_id": "tsodyks_markram",
            },
            "Simple Facilitation Parameters": {
                "keys": ["fac_tau", "fac_increment", "fac_max"],
                "model_id": "simple_facilitation",
            },
            "Simple Depression Parameters": {
                "keys": ["dep_tau", "dep_factor", "dep_min"],
                "model_id": "simple_depression",
            },
            "Synapse Specificity": {"keys": ["excitatory_plasticity", "inhibitory_plasticity"]},
            "Calcium Dependence": {
                "toggle": "calcium_dependence",
                "keys": ["vesicle_pool_size", "replenishment_rate"],
            },
        }

        processed_keys = set(["enabled"])
        wrapper_layout = QVBoxLayout(self.params_group_widget)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(10)

        model_groups = {}  # Store references to model-specific groups

        # 3. Create Group Boxes
        for group_title, group_data in groups.items():
            toggle_key = group_data.get("toggle")
            group_keys = group_data.get("keys", [])
            model_id = group_data.get("model_id")

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

                if model_id:
                    model_groups[model_id] = group_box

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

        # 5. Logic for Plasticity Model Switching
        if "plasticity_type" in param_widgets and model_groups:
            combo = param_widgets["plasticity_type"]

            def update_model_visibility():
                # Get current model ID (value, not display text)
                # Assuming the widget is a QComboBox and we used the config options
                # The BaseFormGenerator stores the internal value in currentData() if configured,
                # or we might need to map from index.
                # Standard QComboBox with options: index matches config['options']
                if hasattr(combo, "currentText"):  # It's a combo
                    idx = combo.currentIndex()
                    # We need to access the raw options from config to get the ID
                    options = self.config["plasticity_type"].get("options", [])
                    if 0 <= idx < len(options):
                        current_id = options[idx]
                    else:
                        current_id = ""

                    for mid, mbox in model_groups.items():
                        mbox.setVisible(mid == current_id)

            if hasattr(combo, "currentIndexChanged"):
                combo.currentIndexChanged.connect(update_model_visibility)
                # Initial update
                update_model_visibility()

        section_layout.addStretch()

        self.forms["main"] = section_widget
        self.param_widgets["main"] = param_widgets

        self._setup_dependencies()
