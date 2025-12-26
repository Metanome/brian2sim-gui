from PyQt6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


def create_config_management_group(main_window):
    """
    Creates the 'Configuration Management' group box and its content.
    Only includes Export and Import buttons as required.
    """
    actions_group = QGroupBox("Configuration Management")
    actions_layout = QVBoxLayout()
    actions_group.setLayout(actions_layout)

    buttons_layout = QHBoxLayout()
    actions_layout.addLayout(buttons_layout)

    main_window.export_config_button = QPushButton("Export Configuration")
    main_window.export_config_button.setToolTip("Export current settings to a JSON file.")
    main_window.export_config_button.clicked.connect(main_window.save_configuration)
    buttons_layout.addWidget(main_window.export_config_button)

    main_window.import_config_button = QPushButton("Import Configuration")
    main_window.import_config_button.setToolTip("Import settings from a JSON file.")
    main_window.import_config_button.clicked.connect(main_window.load_configuration)
    buttons_layout.addWidget(main_window.import_config_button)

    return actions_group


def create_scenario_presets_group(main_window):
    """
    Creates the 'Presets' group box for scenario presets (LIF only, as in Flask app).
    """
    presets_group = QGroupBox("2. Presets")
    layout = QVBoxLayout()
    presets_group.setLayout(layout)

    row_layout = QHBoxLayout()
    label = QLabel("Presets:")
    label.setToolTip("Quickly set parameters for common scenarios. Overrides current settings.")
    row_layout.addWidget(label)

    main_window.scenario_preset_combo = QComboBox()
    main_window.scenario_preset_combo.setToolTip(
        "Quickly set parameters for common scenarios. Overrides current settings."
    )
    # Add scenario presets (LIF only, as in Flask app)
    scenario_presets = [
        ("custom", "Custom"),
        ("lif_quickstart", "LIF Quickstart"),
        ("balanced_random", "Balanced Random Network"),
        ("strongly_coupled", "Strongly Coupled Network"),
        ("sparse_excitatory", "Sparse Excitatory Network"),
        ("inhibition_dominated", "Inhibition-Dominated Network"),
        ("noisy_single", "Noisy Single Neuron"),
        ("synchronous_bursting", "Synchronous Bursting"),
        ("minimal", "Minimal Network"),
    ]
    for key, name in scenario_presets:
        main_window.scenario_preset_combo.addItem(name, userData=key)
    row_layout.addWidget(main_window.scenario_preset_combo)
    layout.addLayout(row_layout)

    desc = QLabel("Set your own parameters or pick a preset to see a typical network scenario.")
    desc.setStyleSheet("font-size: 10px; color: gray;")
    layout.addWidget(desc)

    return presets_group
