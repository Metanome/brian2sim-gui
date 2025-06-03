\
# ui_forms.py

from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLabel, QLineEdit, QDoubleSpinBox, QTextEdit, QComboBox
)

class NeuronModelFormGenerator:
    def __init__(self, neuron_models_config):
        self.neuron_models_config = neuron_models_config
        self.model_forms = {}
        self.model_param_widgets = {}
        self.model_preset_combos = {}
        self._create_forms()

    def _create_forms(self):
        # Only threshold/reset are handled in sim params for LIF; all other params are model-specific
        COMMON_PARAMS = {"v_threshold", "v_reset"}  # Only these are handled in sim params, and only for LIF
        for model_key, config in self.neuron_models_config.items():
            widget = QWidget()
            layout = QFormLayout()
            param_widgets = {}
            for param_key, param_config in config["params"].items():
                # For LIF, skip threshold/reset (handled in sim params); for all others, show all params
                if model_key == "lif" and param_key in COMMON_PARAMS:
                    continue
                label_text = param_config.get("label", param_key.replace("_", " ").title())
                param_type = param_config.get("type", str)
                default_value = param_config.get("default")
                tooltip = param_config.get("tooltip", "")
                min_val = param_config.get("min")
                max_val = param_config.get("max")
                step = param_config.get("step", 0.1)
                input_widget = None
                if param_type == float:
                    input_widget = QDoubleSpinBox()
                    input_widget.setDecimals(3)
                    input_widget.setSingleStep(step)
                    if min_val is not None:
                        input_widget.setMinimum(min_val)
                    if max_val is not None:
                        input_widget.setMaximum(max_val)
                    if default_value is not None:
                        input_widget.setValue(default_value)
                elif param_type == str and param_key == "custom_eqs":
                    input_widget = QTextEdit()
                    input_widget.setMinimumHeight(80)
                    if default_value is not None: input_widget.setPlaceholderText(default_value or "dv/dt = ...")
                    else: input_widget.setPlaceholderText("dv/dt = ...")
                elif param_type == str:
                    input_widget = QLineEdit()
                    if default_value is not None: input_widget.setPlaceholderText(str(default_value))
                else:
                    input_widget = QLineEdit()
                    if default_value is not None: input_widget.setPlaceholderText(str(default_value))
                if input_widget:
                    input_widget.setToolTip(tooltip)
                    label_widget = QLabel(label_text)
                    label_widget.setToolTip(tooltip)
                    layout.addRow(label_widget, input_widget)
                    param_widgets[param_key] = input_widget
            widget.setLayout(layout)
            self.model_forms[model_key] = widget
            self.model_param_widgets[model_key] = param_widgets

            # Create preset combo box for this model (remains unchanged)
            preset_combo = QComboBox()
            preset_combo.addItem("-- Select Preset --")
            if config.get("presets"):
                for preset_name in config["presets"].keys():
                    preset_combo.addItem(preset_name)
            self.model_preset_combos[model_key] = preset_combo

    def get_form_widget(self, model_key):
        return self.model_forms.get(model_key)

    def get_param_widgets(self, model_key):
        return self.model_param_widgets.get(model_key, {})
    
    def get_preset_combo(self, model_key):
        return self.model_preset_combos.get(model_key)

    def load_params_from_config(self, model_key, config_data):
        param_widgets = self.get_param_widgets(model_key)
        # model_defaults = self.neuron_models_config[model_key]["defaults"]
        for param_key, widget in param_widgets.items():
            # When loading, we expect config_data to use the param_key directly (e.g., "izh_a")
            value = config_data.get(param_key) 
            # Fallback to default if not in config_data might be needed, or handled by how config is saved/loaded initially
            # if value is None:
            # value = model_defaults.get(param_key)

            if value is not None:
                if isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                elif isinstance(widget, QTextEdit):
                    widget.setText(str(value))
                elif isinstance(widget, QLineEdit):
                    widget.setText(str(value))
    
    def get_params_for_save(self, model_key):
        param_widgets = self.get_param_widgets(model_key)
        params_to_save = {}
        for param_key, widget in param_widgets.items():
            # Save with the direct param_key (e.g., "izh_a")
            if isinstance(widget, QDoubleSpinBox):
                params_to_save[param_key] = widget.value()
            elif isinstance(widget, QTextEdit):
                params_to_save[param_key] = widget.toPlainText()
            elif isinstance(widget, QLineEdit):
                params_to_save[param_key] = widget.text()
        return params_to_save

    def apply_preset(self, model_key, preset_name):
        presets = self.neuron_models_config[model_key].get("presets", {})
        preset_values = presets.get(preset_name)
        if preset_values:
            param_widgets = self.get_param_widgets(model_key)
            for param_key, value in preset_values.items():
                if param_key in param_widgets:
                    widget = param_widgets[param_key]
                    if isinstance(widget, QDoubleSpinBox):
                        widget.setValue(float(value))
                    elif isinstance(widget, QTextEdit):
                        widget.setText(str(value))
                    elif isinstance(widget, QLineEdit):
                        widget.setText(str(value))
