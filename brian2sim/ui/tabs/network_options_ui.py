from PyQt6.QtWidgets import (
    QGroupBox,
)

from brian2sim.models.network_config import NETWORK_CONFIG
from brian2sim.ui.ui_forms import NetworkOptionsFormGenerator


def create_network_options_group(main_window):
    """
    Creates the 'Network Options' group box using config-driven approach.
    """
    network_options_group = QGroupBox("Network Options")
    network_options_group.setToolTip(
        "Configure synaptic connectivity and network architecture for multi-neuron simulations."
    )

    # Create form generator
    main_window.network_form_generator = NetworkOptionsFormGenerator(NETWORK_CONFIG)

    # Get the form widget and set it as the layout
    form_widget = main_window.network_form_generator.get_form_widget()
    if form_widget:
        network_options_group.setLayout(form_widget.layout())

        # Get access to the enabled checkbox to connect visibility toggle
        param_widgets = main_window.network_form_generator.get_param_widgets()
        enabled_checkbox = param_widgets.get("enabled")

        # Connect signals
        if enabled_checkbox:
            enabled_checkbox.stateChanged.connect(
                lambda state: toggle_network_params_visibility(main_window, state)
            )

        # Connect parameter change signals for preset reset functionality
        for param_key, widget in param_widgets.items():
            if param_key != "enabled":  # Don't connect the main enable checkbox
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(
                        main_window.network_manager.on_param_changed
                    )
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(
                        main_window.network_manager.on_param_changed
                    )

    return network_options_group


def toggle_network_params_visibility(main_window, state):
    """Toggle visibility of network parameter widgets based on checkbox state"""
    # The NetworkOptionsFormGenerator now handles parameter visibility automatically
    # through its simplified lambda connection, similar to NoiseOptionsFormGenerator.
    # No additional action needed here since the lambda directly controls the
    # params_group_widget visibility and the dependency system handles the rest.
