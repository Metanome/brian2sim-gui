\
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QSpinBox, QDoubleSpinBox, QWidget, QVBoxLayout
)
from PyQt6.QtCore import Qt

def _add_param_to_sim_grid_in_ui(main_window, grid_layout, label_text, widget):
    """
    Uses main_window._add_param_to_grid_layout to add a parameter to the simulation grid.
    It relies on main_window having sim_params_current_row, sim_params_current_col, 
    and sim_params_num_cols attributes.
    """
    temp_pos_tracker = [main_window.sim_params_current_row, main_window.sim_params_current_col]
    
    # Assuming _add_param_to_grid_layout is a method of main_window
    main_window._add_param_to_grid_layout(
        grid_layout, 
        label_text, 
        widget, 
        main_window.sim_params_num_cols, 
        temp_pos_tracker 
    )
    
    main_window.sim_params_current_row = temp_pos_tracker[0]
    main_window.sim_params_current_col = temp_pos_tracker[1]

def create_simulation_parameters_group(main_window):
    """
    Creates the QGroupBox for Simulation Parameters and populates it.
    Widgets are stored as attributes of main_window.
    Labels, tooltips, and default values are updated to reflect realistic neuroscience values.
    """
    sim_params_group = QGroupBox("Simulation Parameters")
    main_window.sim_params_layout = QGridLayout()
    sim_params_group.setLayout(main_window.sim_params_layout)

    main_window.sim_params_num_cols = 3
    main_window.sim_params_current_row = 0
    main_window.sim_params_current_col = 0

    sim_params_group.setToolTip("Set the core parameters for the simulation environment.")

    # Simulation Time
    main_window.sim_time_input = QSpinBox()
    main_window.sim_time_input.setRange(1, 1000000)
    main_window.sim_time_input.setValue(1000)  # More realistic simulation duration
    main_window.sim_time_input.setToolTip("Total duration of the simulation in milliseconds (ms). Typically 500-2000ms for simple neural simulations.")
    _add_param_to_sim_grid_in_ui(main_window, main_window.sim_params_layout, "Simulation Time (ms):", main_window.sim_time_input)

    # Input Current
    main_window.input_current_input = QDoubleSpinBox()
    main_window.input_current_input.setDecimals(2)
    main_window.input_current_input.setRange(-10000, 10000)
    main_window.input_current_input.setValue(150.0)  # Standard current for typical neural excitation
    main_window.input_current_input.setToolTip("Input current in picoamperes (pA). Values 100-200pA typically cause neural excitation in most models.")
    _add_param_to_sim_grid_in_ui(main_window, main_window.sim_params_layout, "Input Current:", main_window.input_current_input)

    # Number of Neurons
    main_window.num_neurons_input = QSpinBox()
    main_window.num_neurons_input.setRange(1, 100000)
    main_window.num_neurons_input.setValue(100)  # Reasonable size for network simulations
    main_window.num_neurons_input.setToolTip("Number of neurons in the network. Small networks (10-100) for basic simulations, larger networks (1000+) for complex dynamics.")
    _add_param_to_sim_grid_in_ui(main_window, main_window.sim_params_layout, "Number of Neurons:", main_window.num_neurons_input)

    # Current Start Time (ms)
    main_window.current_start_input = QSpinBox()
    main_window.current_start_input.setRange(0, 1000000)
    main_window.current_start_input.setValue(100)  # Allow system to reach steady state first
    main_window.current_start_input.setToolTip("Start time of current injection (ms). Often delayed (100-200ms) to allow system to reach steady state and observe pre-stimulus behavior.")
    _add_param_to_sim_grid_in_ui(main_window, main_window.sim_params_layout, "Current Start (ms):", main_window.current_start_input)

    # Current Duration (ms)
    main_window.current_duration_input = QSpinBox()
    main_window.current_duration_input.setRange(0, 1000000)
    main_window.current_duration_input.setValue(500)
    main_window.current_duration_input.setToolTip("Duration of current injection in milliseconds (ms). Typically 20-50% of total simulation time for observing both onset and sustained responses.")
    _add_param_to_sim_grid_in_ui(main_window, main_window.sim_params_layout, "Current Duration (ms):", main_window.current_duration_input)

    # LIF-specific parameters - these will be created when needed
    main_window.lif_threshold_input = None
    main_window.lif_reset_input = None
    main_window.lif_threshold_cell_widget = None
    main_window.lif_reset_cell_widget = None

    # Store initial values for LIF parameters
    main_window.lif_threshold_value = -55.0  # Typical neuronal threshold
    main_window.lif_reset_value = -70.0  # Typical reset potential

    # Set column stretching
    for i in range(main_window.sim_params_num_cols):
        main_window.sim_params_layout.setColumnStretch(i, 1)

    return sim_params_group

def update_lif_parameters_visibility_in_sim_params(main_window, current_model_key):
    """
    Adds or removes LIF-specific parameter widgets from the simulation parameters grid.
    Args:
        main_window: The MainWindow instance
        current_model_key: The current model key (string) from the neuron model combo box
    """
    if not current_model_key or not isinstance(current_model_key, str):
        return

    # Remove existing LIF widgets if they are present
    if hasattr(main_window, 'lif_threshold_cell_widget') and main_window.lif_threshold_cell_widget:
        main_window.sim_params_layout.removeWidget(main_window.lif_threshold_cell_widget)
        main_window.lif_threshold_cell_widget.deleteLater()
        main_window.lif_threshold_cell_widget = None
    
    if hasattr(main_window, 'lif_reset_cell_widget') and main_window.lif_reset_cell_widget:
        main_window.sim_params_layout.removeWidget(main_window.lif_reset_cell_widget)
        main_window.lif_reset_cell_widget.deleteLater()
        main_window.lif_reset_cell_widget = None

    num_base_sim_params = 5  # Number of base parameters always present
    lif_start_row = num_base_sim_params // main_window.sim_params_num_cols
    lif_start_col = num_base_sim_params % main_window.sim_params_num_cols

    if current_model_key.strip().lower() == 'lif':
        # Create new LIF inputs with biophysically accurate ranges
        main_window.lif_threshold_input = QDoubleSpinBox()
        main_window.lif_threshold_input.setDecimals(1)
        main_window.lif_threshold_input.setRange(-80, -30)  # Biophysical range for spike threshold
        main_window.lif_threshold_input.setValue(-55.0)     # Common pyramidal neuron threshold
        main_window.lif_threshold_input.setToolTip(
            "Spike threshold potential (mV). Biophysical ranges:\n"
            "• Pyramidal neurons: -55 to -50 mV\n"
            "• Fast-spiking interneurons: -45 to -40 mV\n"
            "• Hippocampal pyramidal cells: -50 to -45 mV\n"
            "Must be at least 5-10 mV above reset potential."
        )

        main_window.lif_reset_input = QDoubleSpinBox()
        main_window.lif_reset_input.setDecimals(1)
        main_window.lif_reset_input.setRange(-90, -60)     # Biophysical range for reset potential
        main_window.lif_reset_input.setValue(-70.0)        # Common reset potential
        main_window.lif_reset_input.setToolTip(
            "Post-spike reset potential (mV). Biophysical ranges:\n"
            "• Cortical neurons: -70 to -65 mV\n"
            "• Hippocampal neurons: -75 to -70 mV\n"
            "• Typically near resting potential\n"
            "Must be below threshold by at least 5-10 mV."
        )

        # Add LIF Threshold
        lif_thresh_label = QLabel("Threshold (mV):")
        main_window.lif_threshold_cell_widget = QWidget()
        cell_layout_thresh = QVBoxLayout(main_window.lif_threshold_cell_widget)
        cell_layout_thresh.setContentsMargins(2, 2, 2, 2)
        cell_layout_thresh.addWidget(lif_thresh_label)
        cell_layout_thresh.addWidget(main_window.lif_threshold_input)
        main_window.sim_params_layout.addWidget(main_window.lif_threshold_cell_widget, lif_start_row, lif_start_col)
        
        # Add LIF Reset
        current_col_for_lif = lif_start_col + 1
        if current_col_for_lif >= main_window.sim_params_num_cols:
            current_col_for_lif = 0
            lif_start_row += 1

        lif_reset_label = QLabel("Reset (mV):")
        main_window.lif_reset_cell_widget = QWidget()
        cell_layout_reset = QVBoxLayout(main_window.lif_reset_cell_widget)
        cell_layout_reset.setContentsMargins(2, 2, 2, 2)
        cell_layout_reset.addWidget(lif_reset_label)
        cell_layout_reset.addWidget(main_window.lif_reset_input)
        main_window.sim_params_layout.addWidget(main_window.lif_reset_cell_widget, lif_start_row, current_col_for_lif)
        
        # Store the values
        main_window.lif_threshold_value = main_window.lif_threshold_input.value()
        main_window.lif_reset_value = main_window.lif_reset_input.value()
        
        # Connect signals for the newly created LIF parameters
        if hasattr(main_window, 'sim_params_manager') and main_window.sim_params_manager:
            main_window.sim_params_manager.connect_lif_signals()
    
    # Request a layout update
    main_window.sim_params_layout.activate()
