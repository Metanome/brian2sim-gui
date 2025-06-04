from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QCheckBox, QLabel, QDoubleSpinBox, QComboBox,
    QWidget, QGridLayout
)
from PyQt6.QtCore import Qt
from noise_options import NOISE_CONFIG

def create_noise_options_group(main_window):
    """
    Creates the 'Noise Options' group box and its content with improved parameters.
    Connects UI elements to the NoiseOptionsManager.
    """
    noise_options_group = QGroupBox("Noise Options")
    noise_options_group.setToolTip("Configure biologically realistic noise to simulate background synaptic activity and channel fluctuations.")
    group_layout = QVBoxLayout()
    noise_options_group.setLayout(group_layout)

    # Add Noise Checkbox
    main_window.noise_checkbox = QCheckBox("Enable Background Noise")
    main_window.noise_checkbox.setToolTip("Enable stochastic fluctuations to model biological variability in neural activity.")
    main_window.noise_checkbox.stateChanged.connect(main_window.noise_options_manager.toggle_noise_params_visibility)
    group_layout.addWidget(main_window.noise_checkbox)

    # Noise Parameters Group
    main_window.noise_params_group = QWidget()
    main_window.noise_params_layout = QGridLayout()
    main_window.noise_params_group.setLayout(main_window.noise_params_layout)
    group_layout.addWidget(main_window.noise_params_group)

    current_row = 0
    current_col = 0
    num_cols = 2

    # Noise Intensity
    noise_intensity_label_text = "Noise Intensity (nA):"
    main_window.noise_intensity_input = QDoubleSpinBox()
    config = NOISE_CONFIG["intensity"]
    main_window.noise_intensity_input.setRange(config["min"], config["max"])
    main_window.noise_intensity_input.setSingleStep(config["step"])
    main_window.noise_intensity_input.setValue(config["default"])
    main_window.noise_intensity_input.setDecimals(3)
    main_window.noise_intensity_input.setToolTip(config["tooltip"])
    
    intensity_cell_widget = QWidget()
    intensity_cell_layout = QVBoxLayout(intensity_cell_widget)
    intensity_cell_layout.setContentsMargins(0,0,0,0)
    intensity_label = QLabel(noise_intensity_label_text)
    intensity_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
    intensity_cell_layout.addWidget(intensity_label)
    intensity_cell_layout.addWidget(main_window.noise_intensity_input)
    main_window.noise_params_layout.addWidget(intensity_cell_widget, current_row, current_col)
    current_col += 1

    # Noise Method
    noise_method_label_text = "Noise Type:"
    main_window.noise_method_combo = QComboBox()
    for method_key, method_config in NOISE_CONFIG["methods"].items():
        main_window.noise_method_combo.addItem(method_config["display_name"], userData=method_key)
    main_window.noise_method_combo.setCurrentText(NOISE_CONFIG["methods"]["Gaussian"]["display_name"])
    main_window.noise_method_combo.setToolTip("Select the type of noise process to simulate different aspects of neural variability.")

    method_cell_widget = QWidget()
    method_cell_layout = QVBoxLayout(method_cell_widget)
    method_cell_layout.setContentsMargins(0,0,0,0)
    method_label = QLabel(noise_method_label_text)
    method_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
    method_cell_layout.addWidget(method_label)
    method_cell_layout.addWidget(main_window.noise_method_combo)
    main_window.noise_params_layout.addWidget(method_cell_widget, current_row, current_col)

    # Initial visibility
    main_window.noise_params_group.setVisible(main_window.noise_checkbox.isChecked())

    return noise_options_group

# Helper function to toggle visibility, can be called by manager
def update_noise_params_visibility(main_window, visible):
    main_window.noise_params_group.setVisible(visible)
