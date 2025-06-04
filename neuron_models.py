from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QFormLayout, QLabel, QLineEdit, QDoubleSpinBox, QTextEdit, QComboBox, QWidget
from ui_forms import NeuronModelFormGenerator
from neuron_models_config import NEURON_MODELS_CONFIG, MODEL_PRESETS, PRESET_DEFAULT_TEXT, PRESET_CUSTOM_TEXT

class NeuronModelsManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.form_generator = NeuronModelFormGenerator(NEURON_MODELS_CONFIG)
        self.current_model_name = None
        self.ignore_param_changes = False  # Flag to prevent preset updates during preset loading
    
    def get_neuron_model(self):
        """
        Get the currently selected neuron model configuration.
          Returns:
            dict: Current neuron model configuration including model_key and parameters
        """
        return self.get_neuron_model_config()

    def connect_signals(self):
        self.main_window.neuron_model_combo.currentIndexChanged.connect(self.update_neuron_param_form_and_presets)
        self.main_window.neuron_model_preset_combo.currentIndexChanged.connect(self.apply_neuron_model_preset)
        
        # Connect parameter change signals to update preset selection
        self.main_window.sim_params_manager.param_changed.connect(self.on_param_changed)
        self.main_window.noise_options_manager.param_changed.connect(self.on_param_changed)
        self.main_window.network_options_manager.param_changed.connect(self.on_param_changed)
        self.main_window.advanced_network_manager.param_changed.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any parameter is changed by the user"""
        if not self.ignore_param_changes:
            # Set preset to Custom
            self.set_preset_to_custom()

    def set_preset_to_custom(self):
        """Changes the preset selection to Custom"""
        combo = self.main_window.neuron_model_preset_combo
        custom_idx = combo.findText(PRESET_CUSTOM_TEXT)
        if custom_idx >= 0:
            combo.setCurrentIndex(custom_idx)

    def update_neuron_param_form_and_presets(self, index):
        model_key = self.main_window.neuron_model_combo.currentData()
        if not model_key or not self.main_window.neuron_model_stacked_widget or not self.main_window.neuron_model_forms:
            return
        if model_key in self.main_window.neuron_model_forms:
            form_to_show = self.main_window.neuron_model_forms[model_key]["widget"]
            self.main_window.neuron_model_stacked_widget.setCurrentWidget(form_to_show)
            
            # Connect parameter change signals for this model
            self.connect_param_change_signals(model_key)
        
        # Update preset combo
        self.main_window.neuron_model_preset_combo.blockSignals(True)
        self.main_window.neuron_model_preset_combo.clear()
        self.main_window.neuron_model_preset_combo.addItem(PRESET_DEFAULT_TEXT, userData="none")
        self.main_window.neuron_model_preset_combo.addItem(PRESET_CUSTOM_TEXT, userData="custom")
        if model_key in MODEL_PRESETS:
            for preset_key, preset in MODEL_PRESETS[model_key].items():
                if preset_key not in ["none", "custom"]:  # Skip the special presets
                    self.main_window.neuron_model_preset_combo.addItem(preset["display_name"], userData=preset_key)
        self.main_window.neuron_model_preset_combo.blockSignals(False)        
        
        # Ensure LIF threshold/reset visibility is updated on model change
        self.main_window.sim_params_manager.update_lif_params_visibility(model_key)
        
        # Connect LIF parameter signals if they were just created
        if model_key == "lif":
            self.main_window.sim_params_manager.connect_lif_signals()

    def apply_neuron_model_preset(self, index):
        if not (
            self.main_window.neuron_model_combo and
            self.main_window.neuron_model_preset_combo and
            self.main_window.neuron_model_forms
        ):
            return

        current_model_key = self.main_window.neuron_model_combo.currentData()
        preset_key = self.main_window.neuron_model_preset_combo.itemData(index)
        
        # Return if no model selected or preset is Custom/Default
        if not current_model_key or preset_key in ["none", "custom"]:
            return

        # Enable preset loading mode to prevent param_changed signals
        self.ignore_param_changes = True
        try:
            model_config = NEURON_MODELS_CONFIG.get(current_model_key)
            if model_config and "presets" in model_config:
                preset = model_config["presets"].get(preset_key)
                if preset and "values" in preset:                    
                    # Apply model-specific parameters
                    if current_model_key in self.main_window.neuron_model_forms:
                        param_widgets = self.main_window.neuron_model_forms[current_model_key]["params"]
                        for param_name, value in preset["values"].items():
                            if param_name in param_widgets:
                                widget = param_widgets[param_name]
                                # Handle different widget types
                                if hasattr(widget, 'setPlainText'):  # QTextEdit
                                    widget.setPlainText(str(value))
                                elif hasattr(widget, 'setValue'):   # QSpinBox, QDoubleSpinBox
                                    widget.setValue(value)
                                elif hasattr(widget, 'setText'):    # QLineEdit
                                    widget.setText(str(value))

                    # Apply other parameter sections if defined in the preset
                    if "sim_params" in preset:
                        self.main_window.sim_params_manager.apply_preset_values(preset["sim_params"])
                    if "noise_options" in preset:
                        self.main_window.noise_options_manager.apply_preset_values(preset["noise_options"])
                    if "network_options" in preset:
                        self.main_window.network_options_manager.apply_preset_values(preset["network_options"])
        finally:
            self.ignore_param_changes = False

    def apply_model_specific_preset(self, index):
        """
        Applies the selected model-specific preset to the current neuron model form.
        """
        if index == 0:  # "-- Select Preset --"
            return
        
        # Determine current_model_key similar to update_neuron_param_form_and_presets
        selected_display_name = self.main_window.neuron_model_combo.currentText()
        current_model_key = None
        for key, config_data in NEURON_MODELS_CONFIG.items():
            if config_data["display_name"] == selected_display_name:
                current_model_key = key
                break
        
        if not current_model_key:
            # Fallback or error handling
            combo_idx = self.main_window.neuron_model_combo.currentIndex()
            ordered_keys = list(NEURON_MODELS_CONFIG.keys())
            if 0 <= combo_idx < len(ordered_keys):
                current_model_key = ordered_keys[combo_idx]
            else:
                return


        preset_name = self.main_window.model_specific_preset_combo.itemText(index)
        
        if not current_model_key or not preset_name or preset_name == "-- Select Preset --":
            return

        self.form_generator.apply_preset(current_model_key, preset_name)
        QMessageBox.information(self.main_window, "Preset Applied", 
                                f"Preset \'{preset_name}\' for {NEURON_MODELS_CONFIG[current_model_key]['display_name']} applied.")

    def get_neuron_model_config(self):
        """
        Returns a dictionary containing all neuron model settings for saving to a config file.
        """
        model_key = self.main_window.neuron_model_combo.currentData()
        current_model_name = self.main_window.neuron_model_combo.currentText()
        
        config = {
            "model_key": model_key,
            "model_name": current_model_name,
            "parameters": {}
        }

        # Get model-specific parameters from form
        if model_key in self.main_window.neuron_model_forms:
            param_widgets = self.main_window.neuron_model_forms[model_key]["params"]
            for param_name, widget in param_widgets.items():
                value = None
                
                if isinstance(widget, QDoubleSpinBox):
                    value = widget.value()
                elif isinstance(widget, QTextEdit):
                    text = widget.toPlainText().strip()
                    if text:
                        value = text
                elif isinstance(widget, QLineEdit):
                    text = widget.text().strip()
                    if text:  
                        # Only include non-empty values
                        # Try to convert numeric strings to numbers
                        try:
                            value = float(text)
                        except ValueError:
                            value = text
                
                # Only include non-empty, non-zero values
                if value is not None and (not isinstance(value, (int, float)) or value != 0):
                    config["parameters"][param_name] = value

        # Save current preset if one is selected
        preset_index = self.main_window.neuron_model_preset_combo.currentIndex()
        if preset_index > 0:  
            # 0 is "Select a preset..."
            preset_name = self.main_window.neuron_model_preset_combo.currentText()
            config["preset"] = preset_name

        return config

    def load_neuron_model_config(self, neuron_settings):
        """
        Load neuron model configuration from a dictionary.
        """
        model_key = neuron_settings.get("model_key")
        if model_key in self.main_window.neuron_model_forms:
            self.main_window.neuron_model_combo.setCurrentText(NEURON_MODELS_CONFIG[model_key]["display_name"])
            form = self.main_window.neuron_model_forms[model_key]["widget"]
            self.main_window.neuron_model_stacked_widget.setCurrentWidget(form)
            
            # Block signals while setting values
            self.ignore_param_changes = True
            try:
                param_widgets = self.main_window.neuron_model_forms[model_key]["params"]
                for param_name, value in neuron_settings.get("parameters", {}).items():
                    if param_name in param_widgets:
                        widget = param_widgets[param_name]
                        if isinstance(widget, QDoubleSpinBox):
                            widget.setValue(float(value))
                        elif isinstance(widget, QTextEdit):
                            widget.setPlainText(str(value))
                        elif isinstance(widget, QLineEdit):
                            widget.setText(str(value))

                # Set preset combo to Custom
                combo = self.main_window.neuron_model_preset_combo
                custom_idx = combo.findText(PRESET_CUSTOM_TEXT)
                if custom_idx >= 0:
                    combo.setCurrentIndex(custom_idx)

                # Apply preset if available
                if "preset" in neuron_settings:
                    preset_name = neuron_settings["preset"]
                    preset_key = None
                    for key, preset in MODEL_PRESETS[model_key].items():
                        if preset["display_name"] == preset_name:
                            preset_key = key
                            break
                    if preset_key:
                        combo.setCurrentIndex(combo.findData(preset_key))
                        self.apply_neuron_model_preset(combo.currentIndex())
            finally:
                self.ignore_param_changes = False

    def update_neuron_model_display_name(self, new_name):
        """
        Update the display name of the current neuron model.
        """
        model_key = self.main_window.neuron_model_combo.currentData()
        if model_key:
            NEURON_MODELS_CONFIG[model_key]["display_name"] = new_name
            self.main_window.neuron_model_combo.setItemText(self.main_window.neuron_model_combo.currentIndex(), new_name)

    def add_neuron_model(self, model_key, model_config):
        """
        Add a new neuron model to the manager.
        """
        if model_key in NEURON_MODELS_CONFIG:
            raise ValueError(f"Model key '{model_key}' already exists.")

        # Add the new model config
        NEURON_MODELS_CONFIG[model_key] = model_config

        # Update the model presets mapping
        global MODEL_PRESETS
        MODEL_PRESETS = {model_key: config["presets"] 
                        for model_key, config in NEURON_MODELS_CONFIG.items()}

        # Add the model to the combo box
        self.main_window.neuron_model_combo.addItem(model_config["display_name"], userData=model_key)

    def remove_neuron_model(self, model_key):
        """
        Remove an existing neuron model from the manager.
        """
        if model_key not in NEURON_MODELS_CONFIG:
            raise ValueError(f"Model key '{model_key}' does not exist.")

        # Remove the model config
        del NEURON_MODELS_CONFIG[model_key]

        # Update the model presets mapping
        global MODEL_PRESETS
        MODEL_PRESETS = {model_key: config["presets"] 
                        for model_key, config in NEURON_MODELS_CONFIG.items()}

        # Remove the model from the combo box
        combo_idx = self.main_window.neuron_model_combo.findData(model_key)
        if combo_idx >= 0:
            self.main_window.neuron_model_combo.removeItem(combo_idx)

    def update_neuron_model_param(self, model_key, param_name, value):
        """
        Update a specific parameter of a neuron model.
        """
        if model_key not in NEURON_MODELS_CONFIG:
            raise ValueError(f"Model key '{model_key}' does not exist.")

        # Update the parameter value
        config = NEURON_MODELS_CONFIG[model_key]
        if "params" in config and param_name in config["params"]:
            config["params"][param_name]["default"] = value
        else:
            raise ValueError(f"Parameter '{param_name}' does not exist for model key '{model_key}'.")

    def save_neuron_models_config(self, file_path):
        """
        Save the configuration of all neuron models to a file.
        """
        import json
        with open(file_path, "w") as json_file:
            json.dump(NEURON_MODELS_CONFIG, json_file, indent=4)

    def load_neuron_models_config(self, file_path):
        """
        Load the configuration of neuron models from a file.
        """
        import json
        with open(file_path, "r") as json_file:
            global NEURON_MODELS_CONFIG
            NEURON_MODELS_CONFIG = json.load(json_file)

        # Update the model presets mapping
        global MODEL_PRESETS
        MODEL_PRESETS = {model_key: config["presets"] 
                        for model_key, config in NEURON_MODELS_CONFIG.items()}

    def connect_param_change_signals(self, model_key):
        """Connect parameter widgets to auto-reset preset when manually changed."""
        if model_key not in self.main_window.neuron_model_forms:
            return
        
        param_widgets = self.main_window.neuron_model_forms[model_key]["params"]
        
        for param_name, widget in param_widgets.items():
            # Connect appropriate signals based on widget type
            if hasattr(widget, 'valueChanged'):  # QSpinBox, QDoubleSpinBox
                widget.valueChanged.connect(self.on_param_changed)
            elif hasattr(widget, 'textChanged'):  # QLineEdit, QTextEdit
                widget.textChanged.connect(self.on_param_changed)
