from PyQt6.QtWidgets import QGroupBox

from brian2sim.models.monitors_config import MONITORS_CONFIG
from brian2sim.ui.ui_forms import BaseFormGenerator


class MonitorsManager:
    """Manager for Monitors UI interactions."""

    def __init__(self, form_generator):
        self.form_generator = form_generator
        self.connect_signals()

    def connect_signals(self):
        """Connect signals for interaction logic."""
        # No complex interactions logic needed yet for monitors
        pass

    def get_params_for_save(self):
        """Get parameters for saving/simulation."""
        return self.form_generator.get_params_for_save()

    def load_params_from_config(self, config_data):
        """Load parameters from configuration dictionary."""
        self.form_generator.load_params_from_config(config_data)


def create_monitors_group(main_window):
    """
    Creates the QGroupBox for Monitors configuration.
    """
    group = QGroupBox("Monitors Configuration")
    group.setToolTip("Configure what data to record during the simulation.")
    
    # Create form generator
    form_generator = BaseFormGenerator(MONITORS_CONFIG)
    
    # Create manager and attach to main_window
    manager = MonitorsManager(form_generator)
    main_window.monitors_manager = manager
    main_window.monitors_ui = manager  # consistency alias
    
    # Get widget
    form_widget = form_generator.get_form_widget()
    if form_widget:
        group.setLayout(form_widget.layout())
        
    return group
