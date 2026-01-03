from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
)

from brian2sim.models.network_config import NETWORK_CONFIG
from brian2sim.ui.ui_forms import NetworkFormGenerator


def create_network_group(main_window):
    """
    Creates the 'Network' group box using config-driven approach.
    """
    network_group = QGroupBox("Network")
    network_group.setToolTip(
        "Configure synaptic connectivity and network architecture for multi-neuron simulations."
    )

    # Create form generator
    main_window.network_form_generator = NetworkFormGenerator(NETWORK_CONFIG)

    # Get the form widget and add it to the group box layout
    form_widget = main_window.network_form_generator.get_form_widget()
    if form_widget:
        # Create a layout for the group box and add the form widget to it
        # This preserves the parent-child hierarchy so visibility toggling works
        group_layout = QVBoxLayout(network_group)
        group_layout.setContentsMargins(5, 5, 5, 5)
        group_layout.addWidget(form_widget)

        # Get access to widgets
        param_widgets = main_window.network_form_generator.get_param_widgets()

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

    return network_group


def toggle_network_params_visibility(main_window, state):
    """Toggle visibility of network parameter widgets based on checkbox state"""
    # The NetworkFormGenerator now handles parameter visibility automatically
    # through its simplified lambda connection, similar to NoiseFormGenerator.
    # No additional action needed here since the lambda directly controls the
    # params_group_widget visibility and the dependency system handles the rest.
