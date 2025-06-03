from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QLabel, QComboBox, QStackedWidget, QHBoxLayout
)
from neuron_models import NEURON_MODELS_CONFIG, NeuronModelsManager

def create_neuron_model_group(main_window):
    """
    Creates the 'Neuron Model Selection' QGroupBox and its child widgets.
    Uses display_name from NEURON_MODELS_CONFIG for the ComboBox items.
    """
    neuron_model_group = QGroupBox("Neuron Model")
    neuron_model_group_layout = QVBoxLayout()

    # --- Neuron Model Selection ComboBox ---
    model_selection_layout = QHBoxLayout()
    model_label = QLabel("Select Neuron Model:")
    model_label.setToolTip("Choose the mathematical model to simulate neuron behavior.") # Added tooltip
    model_selection_layout.addWidget(model_label)

    # Model Type ComboBox
    main_window.neuron_model_combo = QComboBox()
    for model_key, config_data in NEURON_MODELS_CONFIG.items():
        main_window.neuron_model_combo.addItem(config_data["display_name"], userData=model_key)
    main_window.neuron_model_combo.setToolTip("Select the type of neuron model to use for the simulation.")
    model_selection_layout.addWidget(main_window.neuron_model_combo)
    neuron_model_group_layout.addLayout(model_selection_layout)

    # --- Neuron Model Presets ComboBox ---
    preset_layout = QHBoxLayout()
    preset_label = QLabel("Model Presets:")
    preset_label.setToolTip("Load predefined parameter sets for the selected neuron model.")
    preset_layout.addWidget(preset_label)

    main_window.neuron_model_preset_combo = QComboBox()
    main_window.neuron_model_preset_combo.setToolTip("Select a preset to quickly apply common parameter values.")
    preset_layout.addWidget(main_window.neuron_model_preset_combo)
    neuron_model_group_layout.addLayout(preset_layout)    # --- Neuron Parameter Forms (StackedWidget) ---
    main_window.neuron_model_stacked_widget = QStackedWidget()
    main_window.neuron_model_forms = {}
    for model_key in NEURON_MODELS_CONFIG.keys():
        form_widget = main_window.neuron_models_manager.form_generator.get_form_widget(model_key)
        if form_widget:
            main_window.neuron_model_stacked_widget.addWidget(form_widget)
            main_window.neuron_model_forms[model_key] = {"widget": form_widget, "params": main_window.neuron_models_manager.form_generator.get_param_widgets(model_key)}
    neuron_model_group_layout.addWidget(main_window.neuron_model_stacked_widget)
    neuron_model_group.setLayout(neuron_model_group_layout)

    # Connect signals for model and preset changes
    main_window.neuron_model_combo.currentIndexChanged.connect(main_window.neuron_models_manager.update_neuron_param_form_and_presets)
    main_window.neuron_model_preset_combo.currentIndexChanged.connect(main_window.neuron_models_manager.apply_neuron_model_preset)

    # Connect parameter change signals for all neuron model forms
    for model_key in NEURON_MODELS_CONFIG.keys():
        main_window.neuron_models_manager.connect_param_change_signals(model_key)

    return neuron_model_group
