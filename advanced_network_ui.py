"""
Advanced Network Features UI Components for Brian2 neural network simulator.
Creates UI elements for Dale's principle, synaptic delays, STDP, and distance-dependent connectivity.
"""

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QTabWidget, QHBoxLayout, QLabel, QComboBox, QWidget
from PyQt6.QtCore import Qt
from ui_forms import AdvancedNetworkFormGenerator
from advanced_network_config import (
    ADVANCED_NETWORK_CONFIG,
    ADVANCED_NETWORK_PRESETS
)

def create_advanced_network_group(main_window):
    """
    Creates the 'Advanced Network Features' group box using config-driven approach.
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
    
    # Initialize storage for form generators and widgets
    main_window.advanced_form_generators = {}
    main_window.advanced_feature_widgets = {}
    
    # Define tab configuration
    tab_configs = [
        ("dales_principle", "Dale's Principle", "dales_principle"), 
        ("synaptic_delays", "Synaptic Delays", "synaptic_delays"),
        ("stdp", "STDP", "stdp"),
        ("distance_connectivity", "Spatial Connectivity", "distance_connectivity")
    ]
    
    # Create tabs using config-driven approach
    for config_key, tab_title, feature_name in tab_configs:
        if config_key in ADVANCED_NETWORK_CONFIG:
            tab_widget = create_feature_tab(main_window, config_key, feature_name)
            tabs.addTab(tab_widget, tab_title)
    
    return advanced_group

def create_feature_tab(main_window, config_key, feature_name):
    """
    Create a tab for an advanced network feature using config-driven approach.
    """
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    # Get configuration for this feature
    feature_config = ADVANCED_NETWORK_CONFIG[config_key]
    
    # Create form generator
    form_generator = AdvancedNetworkFormGenerator({config_key: feature_config})
    main_window.advanced_form_generators[feature_name] = form_generator
    
    # Get the form widget
    form_widget = form_generator.get_form_widget(config_key)
    if form_widget:
        layout.addWidget(form_widget)
        
        # Store widget references for backward compatibility
        param_widgets = form_generator.get_param_widgets(config_key)
        main_window.advanced_feature_widgets[feature_name] = param_widgets
        
        # Store specific widget references for each feature
        _store_widget_references(main_window, feature_name, param_widgets, form_generator)
    
    # Add presets if available (but skip for STDP and distance_connectivity to keep things simple)
    if feature_name in ADVANCED_NETWORK_PRESETS and feature_name not in ["stdp", "distance_connectivity"]:
        preset_layout = create_preset_section(main_window, feature_name, form_generator)
        layout.insertLayout(0, preset_layout)  # Insert at top
    
    layout.addStretch()
    return tab

def create_preset_section(main_window, feature_name, form_generator):
    """Create preset selection section for features that support it."""
    preset_layout = QHBoxLayout()
    
    preset_label = QLabel(f"{feature_name.replace('_', ' ').title()} Presets:")
    preset_combo = QComboBox()
    preset_combo.addItem("-- Select Preset --", None)
    
    # Add presets from configuration
    presets = ADVANCED_NETWORK_PRESETS[feature_name]
    for preset_key, preset_info in presets.items():
        preset_combo.addItem(preset_info["name"], preset_key)
    
    # Connect preset selection
    preset_combo.currentIndexChanged.connect(
        lambda index: apply_preset_if_selected(main_window, feature_name, preset_combo, form_generator)
    )
    
    preset_layout.addWidget(preset_label)
    preset_layout.addWidget(preset_combo)
    preset_layout.addStretch()
    
    # Store reference
    if not hasattr(main_window, 'advanced_preset_combos'):
        main_window.advanced_preset_combos = {}
    main_window.advanced_preset_combos[feature_name] = preset_combo
    
    return preset_layout

def apply_preset_if_selected(main_window, feature_name, preset_combo, form_generator):
    """Apply preset values if a valid preset is selected."""
    preset_key = preset_combo.currentData()
    if preset_key and hasattr(main_window, 'advanced_network_manager'):
        # Call appropriate preset method based on feature
        if feature_name == "stdp":
            main_window.advanced_network_manager.apply_stdp_preset(preset_key)
        elif feature_name == "distance_connectivity":
            main_window.advanced_network_manager.apply_distance_connectivity_preset(preset_key)

def _store_widget_references(main_window, feature_name, param_widgets, form_generator):
    """Store widget references for backward compatibility with existing manager code."""
    
    if feature_name == "dales_principle":
        main_window.dales_principle_checkbox = param_widgets.get("enabled")
        main_window.excitatory_ratio_input = param_widgets.get("excitatory_ratio") 
        main_window.exc_weight_input = param_widgets.get("exc_weight")
        main_window.inh_weight_input = param_widgets.get("inh_weight")
        
    elif feature_name == "synaptic_delays":
        main_window.synaptic_delays_checkbox = param_widgets.get("enabled")
        main_window.delay_type_combo = param_widgets.get("delay_type")
        main_window.min_delay_input = param_widgets.get("min_delay")
        main_window.max_delay_input = param_widgets.get("max_delay")
        main_window.delay_mean_input = param_widgets.get("delay_mean")
        main_window.delay_std_input = param_widgets.get("delay_std")
        main_window.delay_tau_input = param_widgets.get("delay_tau")
        main_window.conduction_velocity_input = param_widgets.get("conduction_velocity")
        main_window.distance_scale_input = param_widgets.get("distance_scale")
        
    elif feature_name == "stdp":
        main_window.stdp_checkbox = param_widgets.get("enabled")
        main_window.stdp_type_combo = param_widgets.get("stdp_type")
        main_window.A_plus_input = param_widgets.get("A_plus")
        main_window.A_minus_input = param_widgets.get("A_minus")
        main_window.tau_plus_input = param_widgets.get("tau_plus")
        main_window.tau_minus_input = param_widgets.get("tau_minus")
        main_window.w_max_input = param_widgets.get("w_max")
        main_window.w_min_input = param_widgets.get("w_min")
        
        # Store preset combo reference
        if hasattr(main_window, 'advanced_preset_combos') and feature_name in main_window.advanced_preset_combos:
            main_window.stdp_preset_combo = main_window.advanced_preset_combos[feature_name]
        
    elif feature_name == "distance_connectivity":
        main_window.distance_connectivity_checkbox = param_widgets.get("enabled")
        main_window.distance_profile_combo = param_widgets.get("distance_profile")
        main_window.spatial_scale_input = param_widgets.get("spatial_scale")
        main_window.max_distance_input = param_widgets.get("max_distance")
        main_window.gaussian_sigma_input = param_widgets.get("gaussian_sigma")
        main_window.exponential_lambda_input = param_widgets.get("exponential_lambda")
        main_window.power_law_alpha_input = param_widgets.get("power_law_alpha")
        main_window.power_law_beta_input = param_widgets.get("power_law_beta")
        
        # Store preset combo reference
        if hasattr(main_window, 'advanced_preset_combos') and feature_name in main_window.advanced_preset_combos:
            main_window.distance_preset_combo = main_window.advanced_preset_combos[feature_name]
