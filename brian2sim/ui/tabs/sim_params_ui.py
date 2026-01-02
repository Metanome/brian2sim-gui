from PyQt6.QtWidgets import (
    QGroupBox,
)

from brian2sim.models.sim_params_config import SIM_PARAMS_CONFIG
from brian2sim.ui.ui_forms import SimParamsFormGenerator


def create_simulation_parameters_group(main_window):
    """
    Creates the QGroupBox for Simulation Parameters using config-driven approach.
    Widgets are stored as attributes of main_window.
    """
    sim_params_group = QGroupBox("Simulation Parameters")
    sim_params_group.setToolTip("Set the core parameters for the simulation environment.")
    # Create form generator
    main_window.sim_params_form_generator = SimParamsFormGenerator(SIM_PARAMS_CONFIG)
    main_window.sim_params_form_generator.main_window = (
        main_window  # Add reference for sync_neuron_model
    )

    # Get the form widget and set it as the layout
    form_widget = main_window.sim_params_form_generator.get_form_widget()
    if form_widget:
        sim_params_group.setLayout(form_widget.layout())

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
    if hasattr(main_window, "sim_params_form_generator"):
        # Sync the hidden neuron_model parameter with the main neuron model selection
        # This will automatically show/hide depends_on fields via the FormGenerator logic
        main_window.sim_params_form_generator.sync_neuron_model(current_model_key)
        return

    # Fallback message - this shouldn't happen in the config-driven version
    print("Warning: LIF parameter visibility update called without form generator")

    # Request a layout update
    if hasattr(main_window, "sim_params_layout"):
        main_window.sim_params_layout.activate()
