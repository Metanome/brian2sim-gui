from PyQt6.QtWidgets import (
    QGroupBox,
)

from brian2sim.models.noise_config import NOISE_CONFIG
from brian2sim.ui.ui_forms import NoiseOptionsFormGenerator


def create_noise_options_group(main_window):
    """
    Creates the 'Noise Options' group box using config-driven approach.
    """
    noise_options_group = QGroupBox("Noise Options")
    noise_options_group.setToolTip(
        "Configure biologically realistic noise to simulate background synaptic activity and channel fluctuations."
    )

    # Create form generator
    main_window.noise_form_generator = NoiseOptionsFormGenerator(NOISE_CONFIG)

    # Get the form widget and set it as the layout
    form_widget = main_window.noise_form_generator.get_form_widget()
    if form_widget:
        noise_options_group.setLayout(form_widget.layout())

        # Store references to specific widgets for backward compatibility
        param_widgets = main_window.noise_form_generator.get_param_widgets()
        main_window.noise_checkbox = param_widgets.get("enabled")
        main_window.noise_intensity_input = param_widgets.get("intensity")
        main_window.noise_method_combo = param_widgets.get("method")
        main_window.noise_correlation_time_input = param_widgets.get("correlation_time")

        # Connect parameter change signals for preset reset functionality
        for param_key, widget in param_widgets.items():
            if param_key != "enabled":  # Don't connect the main enable checkbox
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(main_window.noise_options_manager.on_param_changed)
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(
                        main_window.noise_options_manager.on_param_changed
                    )

    return noise_options_group


def toggle_noise_params_visibility(main_window, state):
    """Toggle visibility of noise parameter widgets based on checkbox state"""
    # The NoiseOptionsFormGenerator now handles parameter visibility automatically
    # through its simplified lambda connection, similar to NetworkOptionsFormGenerator.
    # No additional action needed here since the lambda directly controls the
    # params_group_widget visibility and the dependency system handles the rest.


# Helper function to toggle visibility, can be called by manager
def update_noise_params_visibility(main_window, visible):
    if hasattr(main_window, "noise_params_group"):
        main_window.noise_params_group.setVisible(visible)
