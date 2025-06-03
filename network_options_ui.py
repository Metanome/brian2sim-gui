from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QCheckBox, QLabel, QDoubleSpinBox, QComboBox,
    QStackedWidget, QWidget, QFormLayout, QSpinBox
)
from PyQt6.QtCore import Qt
from network_options import NETWORK_TOPOLOGIES_CONFIG

def create_network_options_group(main_window):
    """
    Creates the 'Network Options' group box with improved network topology parameters.
    """
    network_options_group = QGroupBox("Network Options")
    network_options_group.setToolTip("Configure synaptic connectivity and network architecture for multi-neuron simulations.")
    group_layout = QVBoxLayout()
    network_options_group.setLayout(group_layout)

    # Enable Synaptic Connections Checkbox
    main_window.synaptic_connections_checkbox = QCheckBox("Enable synaptic connections")
    main_window.synaptic_connections_checkbox.setToolTip(
        "Enable interactions between neurons through synaptic connections. Required for network effects and emergent dynamics."
    )
    main_window.synaptic_connections_checkbox.stateChanged.connect(
        main_window.network_options_manager.toggle_synapse_params_visibility
    )
    group_layout.addWidget(main_window.synaptic_connections_checkbox)

    # Synapse Parameters Group
    main_window.synapse_params_group = QWidget()
    main_window.synapse_params_layout = QFormLayout()
    main_window.synapse_params_group.setLayout(main_window.synapse_params_layout)
    group_layout.addWidget(main_window.synapse_params_group)

    # Synaptic Weight
    syn_weight_label = QLabel("Synaptic Weight (nS):")
    main_window.synaptic_weight_input = QDoubleSpinBox()
    main_window.synaptic_weight_input.setRange(-100.0, 100.0)
    main_window.synaptic_weight_input.setSingleStep(0.1)
    main_window.synaptic_weight_input.setValue(1.0)
    main_window.synaptic_weight_input.setToolTip(
        "Strength of synaptic connections in nanosiemens (nS). Positive values for excitatory (0.1-5.0 nS typical), "
        "negative for inhibitory (-0.5 to -10.0 nS typical). Stronger weights lead to stronger network effects."
    )
    main_window.synapse_params_layout.addRow(syn_weight_label, main_window.synaptic_weight_input)

    # Network Topology
    topology_type_label = QLabel("Network Topology:")
    main_window.network_topology_combo = QComboBox()
    for key, config in NETWORK_TOPOLOGIES_CONFIG.items():
        main_window.network_topology_combo.addItem(config["display_name"], userData=key)
    
    main_window.network_topology_combo.setToolTip(
        "Select the pattern of connectivity between neurons. Different topologies model various biological neural architectures:\n"
        "- Random: Models local cortical circuits\n"
        "- Small World: Common in brain networks, balancing integration and segregation\n"
        "- Scale Free: Found in certain neural subsystems with hub neurons\n"
        "- Regular: Models topographic neural maps\n"
        "- Modular: Represents functionally specialized neural circuits"
    )
    main_window.network_topology_combo.currentIndexChanged.connect(
        main_window.network_options_manager.update_topology_params_form
    )
    main_window.synapse_params_layout.addRow(topology_type_label, main_window.network_topology_combo)

    # Topology Parameters Stacked Widget
    main_window.topology_params_stacked_widget = QStackedWidget()
    main_window.synapse_params_layout.addWidget(main_window.topology_params_stacked_widget)

    # Create forms for each topology type
    main_window.network_options_manager.topology_forms = {}

    for key, config in NETWORK_TOPOLOGIES_CONFIG.items():
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(0, 5, 0, 0)
        
        param_widgets = {}
        for param_key, param_config in config["params"].items():
            param_label = QLabel(param_config["label"])
            widget = None
            
            if param_config["type"] == "double":
                widget = QDoubleSpinBox()
                widget.setDecimals(3)
                if "step" in param_config: widget.setSingleStep(param_config["step"])
            elif param_config["type"] == "int":
                widget = QSpinBox()
                if "step" in param_config: widget.setSingleStep(param_config["step"])
            elif param_config["type"] == "bool":
                widget = QCheckBox()
            
            if widget:
                if "min" in param_config: widget.setMinimum(param_config["min"])
                if "max" in param_config: widget.setMaximum(param_config["max"])
                widget.setValue(param_config["default"])
                if "tooltip" in param_config: widget.setToolTip(param_config["tooltip"])
                form_layout.addRow(param_label, widget)
                param_widgets[param_key] = widget

                # Store specific widget references
                if key == "all_to_all" and param_key == "allow_self_connections":
                    main_window.allow_self_connections_checkbox = widget
                elif key == "random" and param_key == "connection_probability":
                    main_window.connection_probability_input = widget
                elif key == "small_world":
                    if param_key == "sw_nearest_neighbors":
                        main_window.sw_nearest_neighbors_input = widget
                    elif param_key == "sw_rewiring_probability":
                        main_window.sw_rewiring_probability_input = widget
        
        main_window.network_options_manager.topology_forms[key] = {
            "widget": form_widget,
            "params": param_widgets
        }
        main_window.topology_params_stacked_widget.addWidget(form_widget)

    # Initial visibility and form update
    main_window.synapse_params_group.setVisible(main_window.synaptic_connections_checkbox.isChecked())
    if main_window.network_topology_combo.count() > 0:
        main_window.network_options_manager.update_topology_params_form(0)

    return network_options_group
