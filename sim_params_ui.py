from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QSpinBox, QDoubleSpinBox, QWidget, QVBoxLayout
)
from PyQt6.QtCore import Qt
from ui_forms import SimParamsFormGenerator
from sim_params_config import SIM_PARAMS_CONFIG

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
    Creates the QGroupBox for Simulation Parameters using config-driven approach.
    Widgets are stored as attributes of main_window.
    """
    sim_params_group = QGroupBox("Simulation Parameters")
    sim_params_group.setToolTip("Set the core parameters for the simulation environment.")
      # Create form generator
    main_window.sim_params_form_generator = SimParamsFormGenerator(SIM_PARAMS_CONFIG)
    main_window.sim_params_form_generator.main_window = main_window  # Add reference for sync_neuron_model
    
    # Get the form widget and set it as the layout
    form_widget = main_window.sim_params_form_generator.get_form_widget()
    if form_widget:
        sim_params_group.setLayout(form_widget.layout())
        
        # Store references to specific widgets for backward compatibility
        param_widgets = main_window.sim_params_form_generator.get_param_widgets()
        main_window.sim_time_input = param_widgets.get("sim_time")
        main_window.input_current_input = param_widgets.get("input_current") 
        main_window.num_neurons_input = param_widgets.get("num_neurons")
        main_window.current_start_input = param_widgets.get("current_start")
        main_window.current_duration_input = param_widgets.get("current_duration")
        
        # LIF-specific parameters - these will be created when needed
        main_window.lif_threshold_input = param_widgets.get("v_threshold")
        main_window.lif_reset_input = param_widgets.get("v_reset")
        main_window.lif_threshold_cell_widget = None
        main_window.lif_reset_cell_widget = None

        # Store initial values for LIF parameters
        main_window.lif_threshold_value = -55.0  # Typical neuronal threshold
        main_window.lif_reset_value = -70.0  # Typical reset potential        # Legacy grid layout support for LIF parameter insertion
        # Store reference to the form layout for compatibility
        main_window.sim_params_layout = form_widget.layout()
        main_window.sim_params_num_cols = 3
        main_window.sim_params_current_row = 0
        main_window.sim_params_current_col = 0

    return sim_params_group

def update_lif_parameters_visibility_in_sim_params(main_window, current_model_key):
    """
    Updates LIF parameter visibility using the config-driven dependency system.
    Args:
        main_window: The MainWindow instance
        current_model_key: The current model key (string) from the neuron model combo box
    """
    if not current_model_key or not isinstance(current_model_key, str):
        return

    # Check if we have the form generator
    if hasattr(main_window, 'sim_params_form_generator'):
        # Sync the hidden neuron_model parameter with the main neuron model selection
        main_window.sim_params_form_generator.sync_neuron_model(current_model_key)
        
        # Get param widgets for backward compatibility
        param_widgets = main_window.sim_params_form_generator.get_param_widgets()
        
        # Update the main window references for backward compatibility
        if current_model_key.strip().lower() == 'lif':
            main_window.lif_threshold_input = param_widgets.get("v_threshold")
            main_window.lif_reset_input = param_widgets.get("v_reset")
        else:
            main_window.lif_threshold_input = None
            main_window.lif_reset_input = None
        
        # Connect LIF signals if they're now visible
        if hasattr(main_window, 'sim_params_manager'):
            main_window.sim_params_manager.connect_lif_signals()
        
        return

    # Fallback message - this shouldn't happen in the config-driven version
    print("Warning: LIF parameter visibility update called without form generator")
    if hasattr(main_window, 'sim_params_manager'):
        main_window.sim_params_manager.connect_lif_signals()
    
    # Request a layout update
    if hasattr(main_window, 'sim_params_layout'):
        main_window.sim_params_layout.activate()
