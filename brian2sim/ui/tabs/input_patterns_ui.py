"""
Input patterns UI components for Brian2 neural network simulator.
Creates user interface for configuring various input stimulation patterns.
"""

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from brian2sim.models.input_patterns_config import INPUT_PATTERNS_CONFIG
from brian2sim.ui.ui_forms import InputPatternsFormGenerator


def create_input_patterns_group(main_window):
    """
    Creates the 'Input Patterns' group box using config-driven approach.
    """
    input_patterns_group = QGroupBox("Input Patterns")
    input_patterns_group.setToolTip(
        "Configure external input stimulation patterns for realistic neural network simulations."
    )

    # Create form generator
    main_window.input_patterns_form_generator = InputPatternsFormGenerator(INPUT_PATTERNS_CONFIG)

    # Get the form widget and set it as the layout
    form_widget = main_window.input_patterns_form_generator.get_form_widget()
    if form_widget:
        input_patterns_group.setLayout(form_widget.layout())

        # Store references to specific widgets for backward compatibility
        param_widgets = main_window.input_patterns_form_generator.get_param_widgets()
        main_window.input_patterns_enabled = param_widgets.get("enabled")
        main_window.input_pattern_type = param_widgets.get("pattern_type")
        main_window.poisson_rate_input = param_widgets.get("poisson_rate")
        main_window.poisson_weight_input = param_widgets.get("poisson_weight")
        main_window.rhythmic_frequency_input = param_widgets.get("rhythmic_frequency")
        main_window.rhythmic_amplitude_input = param_widgets.get("rhythmic_amplitude")
        main_window.burst_rate_input = param_widgets.get("burst_rate")
        main_window.burst_duration_input = param_widgets.get("burst_duration")
        main_window.step_amplitude_input = param_widgets.get("step_amplitude")
        main_window.step_start_time_input = param_widgets.get("step_start_time")
        main_window.step_duration_input = param_widgets.get("step_duration")

        # Store forms for manager access
        main_window.input_patterns_forms = param_widgets
    else:
        # Fallback layout if form generation fails
        fallback_layout = QVBoxLayout(input_patterns_group)
        fallback_layout.addWidget(QWidget())  # Empty placeholder

    return input_patterns_group
