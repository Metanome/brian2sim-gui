"""
Advanced Network Features UI Components for Brian2 neural network simulator.
Creates UI elements for Dale's principle, synaptic delays, STDP, and distance-dependent connectivity.
"""

from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QDoubleSpinBox, 
    QComboBox, QWidget, QFormLayout, QSpinBox, QPushButton, QTabWidget,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from advanced_network_config import (
    DALES_PRINCIPLE_CONFIG,
    SYNAPTIC_DELAYS_CONFIG,
    STDP_CONFIG,
    DISTANCE_CONNECTIVITY_CONFIG,
    STDP_PRESETS,
    DISTANCE_CONNECTIVITY_PRESETS
)

def create_advanced_network_group(main_window):
    """
    Creates the 'Advanced Network Features' group box with all four major features.
    """
    advanced_group = QGroupBox("Advanced Network Features")
    advanced_group.setToolTip(
        "Advanced neuroscience features for realistic neural network modeling:\n"
        "• Dale's Principle: Excitatory/inhibitory neuron separation\n"
        "• Synaptic Delays: Realistic transmission delays\n"
        "• STDP: Spike-timing dependent plasticity\n"
        "• Distance-Dependent Connectivity: Spatial network organization"
    )
    
    main_layout = QVBoxLayout()
    advanced_group.setLayout(main_layout)
    
    # Create tabbed interface for better organization
    tabs = QTabWidget()
    main_layout.addWidget(tabs)
    
    # Dale's Principle Tab
    dales_tab = create_dales_principle_tab(main_window)
    tabs.addTab(dales_tab, "Dale's Principle")
    
    # Synaptic Delays Tab
    delays_tab = create_synaptic_delays_tab(main_window)
    tabs.addTab(delays_tab, "Synaptic Delays")
    
    # STDP Tab
    stdp_tab = create_stdp_tab(main_window)
    tabs.addTab(stdp_tab, "STDP")
    
    # Distance Connectivity Tab
    distance_tab = create_distance_connectivity_tab(main_window)
    tabs.addTab(distance_tab, "Spatial Connectivity")
    
    return advanced_group

def create_dales_principle_tab(main_window):
    """Create Dale's Principle configuration tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    # Enable checkbox
    main_window.dales_principle_checkbox = QCheckBox("Enable Dale's Principle")
    main_window.dales_principle_checkbox.setToolTip(
        "Separate neurons into excitatory (positive weights) and inhibitory (negative weights) populations. "
        "This fundamental principle states that each neuron releases the same neurotransmitter at all synapses."
    )
    layout.addWidget(main_window.dales_principle_checkbox)
    
    # Parameters group
    main_window.dales_principle_params_group = QWidget()
    params_layout = QFormLayout(main_window.dales_principle_params_group)
    layout.addWidget(main_window.dales_principle_params_group)
    
    # Create parameter widgets
    main_window.dales_principle_forms = {"params": {}}
    
    for param_key, param_config in DALES_PRINCIPLE_CONFIG.items():
        if param_key == "enabled":
            continue
            
        label = QLabel(param_config["label"])
        widget = None
        
        if param_config["type"] == "double":
            widget = QDoubleSpinBox()
            widget.setDecimals(3)
            widget.setMinimum(param_config.get("min", -1000.0))
            widget.setMaximum(param_config.get("max", 1000.0))
            widget.setSingleStep(param_config.get("step", 0.1))
            widget.setValue(param_config["default"])
        elif param_config["type"] == "int":
            widget = QSpinBox()
            widget.setMinimum(param_config.get("min", 0))
            widget.setMaximum(param_config.get("max", 1000))
            widget.setSingleStep(param_config.get("step", 1))
            widget.setValue(param_config["default"])
        elif param_config["type"] == "bool":
            widget = QCheckBox()
            widget.setChecked(param_config["default"])
            
        if widget:
            widget.setToolTip(param_config.get("tooltip", ""))
            params_layout.addRow(label, widget)
            main_window.dales_principle_forms["params"][param_key] = widget
    
    # Connect signals
    main_window.dales_principle_checkbox.stateChanged.connect(
        main_window.advanced_network_manager.toggle_dales_principle_visibility
    )
    
    # Initial visibility
    main_window.dales_principle_params_group.setVisible(False)
    
    layout.addStretch()
    return tab

def create_synaptic_delays_tab(main_window):
    """Create Synaptic Delays configuration tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    # Enable checkbox
    main_window.synaptic_delays_checkbox = QCheckBox("Enable Synaptic Delays")
    main_window.synaptic_delays_checkbox.setToolTip(
        "Add realistic time delays to synaptic transmission. "
        "Accounts for axonal conduction time and synaptic processing delays."
    )
    layout.addWidget(main_window.synaptic_delays_checkbox)
    
    # Parameters group
    main_window.synaptic_delays_params_group = QWidget()
    params_layout = QFormLayout(main_window.synaptic_delays_params_group)
    layout.addWidget(main_window.synaptic_delays_params_group)
    
    # Create parameter widgets
    main_window.synaptic_delays_forms = {"params": {}, "labels": {}}
    
    for param_key, param_config in SYNAPTIC_DELAYS_CONFIG.items():
        if param_key == "enabled":
            continue
            
        label = QLabel(param_config["label"])
        widget = None
        
        if param_config["type"] == "double":
            widget = QDoubleSpinBox()
            widget.setDecimals(3)
            widget.setMinimum(param_config.get("min", 0.0))
            widget.setMaximum(param_config.get("max", 1000.0))
            widget.setSingleStep(param_config.get("step", 0.1))
            widget.setValue(param_config["default"])
        elif param_config["type"] == "combo":
            widget = QComboBox()
            # Use display_options if available, otherwise fall back to options
            if "display_options" in param_config:
                widget.addItems(param_config["display_options"])
                # Set current index based on default value in options
                try:
                    default_index = param_config["options"].index(param_config["default"])
                    widget.setCurrentIndex(default_index)
                except (ValueError, KeyError):
                    widget.setCurrentText(param_config["default"])
            else:
                widget.addItems(param_config["options"])
                widget.setCurrentText(param_config["default"])
            
        if widget:
            widget.setToolTip(param_config.get("tooltip", ""))
            params_layout.addRow(label, widget)
            main_window.synaptic_delays_forms["params"][param_key] = widget
            main_window.synaptic_delays_forms["labels"][param_key] = label
    
    # Connect signals
    main_window.synaptic_delays_checkbox.stateChanged.connect(
        main_window.advanced_network_manager.toggle_synaptic_delays_visibility
    )
      # Connect delay type change to update parameter visibility
    if "delay_type" in main_window.synaptic_delays_forms["params"]:
        main_window.synaptic_delays_forms["params"]["delay_type"].currentIndexChanged.connect(
            main_window.advanced_network_manager.update_delay_params_visibility
        )
    
    # Initial visibility
    main_window.synaptic_delays_params_group.setVisible(False)
    
    # Set initial parameter visibility based on default delay type
    if hasattr(main_window, 'advanced_network_manager'):
        main_window.advanced_network_manager.update_delay_params_visibility(0)
    
    layout.addStretch()
    return tab

def create_stdp_tab(main_window):
    """Create STDP configuration tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    # Enable checkbox
    main_window.stdp_checkbox = QCheckBox("Enable STDP (Spike-Timing Dependent Plasticity)")
    main_window.stdp_checkbox.setToolTip(
        "Enable spike-timing dependent plasticity where synaptic weights change "
        "based on the relative timing of pre- and post-synaptic spikes."
    )
    layout.addWidget(main_window.stdp_checkbox)
    
    # STDP Presets
    presets_layout = QHBoxLayout()
    presets_label = QLabel("STDP Presets:")
    main_window.stdp_presets_combo = QComboBox()
    main_window.stdp_presets_combo.addItem("Select preset...", None)
    for preset_key, preset_info in STDP_PRESETS.items():
        main_window.stdp_presets_combo.addItem(preset_info["name"], preset_key)
    
    presets_layout.addWidget(presets_label)
    presets_layout.addWidget(main_window.stdp_presets_combo)
    presets_layout.addStretch()
    layout.addLayout(presets_layout)
    
    # Parameters group
    main_window.stdp_params_group = QWidget()
    params_layout = QFormLayout(main_window.stdp_params_group)
    layout.addWidget(main_window.stdp_params_group)
    
    # Create parameter widgets
    main_window.stdp_forms = {"params": {}, "labels": {}}
    
    for param_key, param_config in STDP_CONFIG.items():
        if param_key == "enabled":
            continue
            
        label = QLabel(param_config["label"])
        widget = None
        
        if param_config["type"] == "double":
            widget = QDoubleSpinBox()
            widget.setDecimals(6)  # Higher precision for STDP parameters
            widget.setMinimum(param_config.get("min", 0.0))
            widget.setMaximum(param_config.get("max", 1000.0))
            widget.setSingleStep(param_config.get("step", 0.001))
            widget.setValue(param_config["default"])
        elif param_config["type"] == "combo":
            widget = QComboBox()
            # Use display_options if available, otherwise fall back to options
            if "display_options" in param_config:
                widget.addItems(param_config["display_options"])
                # Set current index based on default value in options
                try:
                    default_index = param_config["options"].index(param_config["default"])
                    widget.setCurrentIndex(default_index)
                except (ValueError, KeyError):
                    widget.setCurrentText(param_config["default"])
            else:
                widget.addItems(param_config["options"])
                widget.setCurrentText(param_config["default"])
            
        if widget:
            widget.setToolTip(param_config.get("tooltip", ""))
            params_layout.addRow(label, widget)
            main_window.stdp_forms["params"][param_key] = widget
            main_window.stdp_forms["labels"][param_key] = label    # Connect signals
    main_window.stdp_checkbox.stateChanged.connect(
        main_window.advanced_network_manager.toggle_stdp_visibility
    )
    
    # Connect STDP type change to update parameter visibility
    if "stdp_type" in main_window.stdp_forms["params"]:
        main_window.stdp_forms["params"]["stdp_type"].currentIndexChanged.connect(
            main_window.advanced_network_manager.update_stdp_params_visibility
        )
    
    # Connect preset selection to auto-apply
    main_window.stdp_presets_combo.currentIndexChanged.connect(
        lambda: main_window.advanced_network_manager.apply_stdp_preset(
            main_window.stdp_presets_combo.currentData()
        ) if main_window.stdp_presets_combo.currentData() else None
    )
    
    # Initial visibility
    main_window.stdp_params_group.setVisible(False)
    
    layout.addStretch()
    return tab

def create_distance_connectivity_tab(main_window):
    """Create Distance-Dependent Connectivity configuration tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    # Enable checkbox
    main_window.distance_connectivity_checkbox = QCheckBox("Enable Distance-Dependent Connectivity")
    main_window.distance_connectivity_checkbox.setToolTip(
        "Connection probability depends on spatial distance between neurons. "
        "Models realistic spatial organization of neural circuits."
    )
    layout.addWidget(main_window.distance_connectivity_checkbox)
    
    # Distance Connectivity Presets
    presets_layout = QHBoxLayout()
    presets_label = QLabel("Connectivity Presets:")
    main_window.distance_presets_combo = QComboBox()
    main_window.distance_presets_combo.addItem("Select preset...", None)
    for preset_key, preset_info in DISTANCE_CONNECTIVITY_PRESETS.items():
        main_window.distance_presets_combo.addItem(preset_info["name"], preset_key)
    
    presets_layout.addWidget(presets_label)
    presets_layout.addWidget(main_window.distance_presets_combo)
    presets_layout.addStretch()
    layout.addLayout(presets_layout)
    
    # Parameters group
    main_window.distance_connectivity_params_group = QWidget()
    params_layout = QFormLayout(main_window.distance_connectivity_params_group)
    layout.addWidget(main_window.distance_connectivity_params_group)
    
    # Create parameter widgets
    main_window.distance_connectivity_forms = {"params": {}, "labels": {}}
    
    for param_key, param_config in DISTANCE_CONNECTIVITY_CONFIG.items():
        if param_key == "enabled":
            continue
            
        label = QLabel(param_config["label"])
        widget = None
        
        if param_config["type"] == "double":
            widget = QDoubleSpinBox()
            widget.setDecimals(3)
            widget.setMinimum(param_config.get("min", 0.0))
            widget.setMaximum(param_config.get("max", 10000.0))
            widget.setSingleStep(param_config.get("step", 0.1))
            widget.setValue(param_config["default"])
        elif param_config["type"] == "combo":
            widget = QComboBox()
            # Use display_options if available, otherwise fall back to options
            if "display_options" in param_config:
                widget.addItems(param_config["display_options"])
                # Set current index based on default value in options
                try:
                    default_index = param_config["options"].index(param_config["default"])
                    widget.setCurrentIndex(default_index)
                except (ValueError, KeyError):
                    widget.setCurrentText(param_config["default"])
            else:
                widget.addItems(param_config["options"])
                widget.setCurrentText(param_config["default"])
            
        if widget:
            widget.setToolTip(param_config.get("tooltip", ""))
            params_layout.addRow(label, widget)
            main_window.distance_connectivity_forms["params"][param_key] = widget
            main_window.distance_connectivity_forms["labels"][param_key] = label
    
    # Connect signals
    main_window.distance_connectivity_checkbox.stateChanged.connect(
        main_window.advanced_network_manager.toggle_distance_connectivity_visibility
    )
    
    # Connect function type change to update parameter visibility
    if "connection_function" in main_window.distance_connectivity_forms["params"]:
        main_window.distance_connectivity_forms["params"]["connection_function"].currentIndexChanged.connect(
            main_window.advanced_network_manager.update_distance_params_visibility
        )
    
    # Connect preset selection to auto-apply
    main_window.distance_presets_combo.currentIndexChanged.connect(
        lambda: main_window.advanced_network_manager.apply_distance_connectivity_preset(
            main_window.distance_presets_combo.currentData()
        ) if main_window.distance_presets_combo.currentData() else None
    )
    
    # Initial visibility
    main_window.distance_connectivity_params_group.setVisible(False)
    
    # Set initial parameter visibility based on default connection function
    if hasattr(main_window, 'advanced_network_manager'):
        main_window.advanced_network_manager.update_distance_params_visibility(0)
    
    layout.addStretch()
    return tab


