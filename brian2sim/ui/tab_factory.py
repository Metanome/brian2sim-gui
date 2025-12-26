"""
Tab Factory for constructing MainWindow tabs.
Extracts tab creation logic from MainWindow._init_ui().
"""

from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from brian2sim.ui.tabs.advanced_network_ui import create_advanced_network_group
from brian2sim.ui.tabs.calcium_dynamics_ui import create_calcium_dynamics_group

# Import tab creation functions
from brian2sim.ui.tabs.config_manager_ui import create_config_management_group
from brian2sim.ui.tabs.gap_junctions_ui import create_gap_junctions_group
from brian2sim.ui.tabs.homeostatic_plasticity_ui import create_homeostatic_plasticity_group
from brian2sim.ui.tabs.input_patterns_ui import create_input_patterns_group
from brian2sim.ui.tabs.multicompartment_ui import create_multicompartment_group
from brian2sim.ui.tabs.network_options_ui import create_network_options_group
from brian2sim.ui.tabs.neuromodulation_ui import create_neuromodulation_group
from brian2sim.ui.tabs.neuron_models_ui import create_neuron_model_group
from brian2sim.ui.tabs.noise_options_ui import create_noise_options_group
from brian2sim.ui.tabs.short_term_plasticity_ui import create_short_term_plasticity_group
from brian2sim.ui.tabs.sim_params_ui import create_simulation_parameters_group
from brian2sim.ui.tabs.simulation_ui import create_simulation_tab
from brian2sim.ui.tabs.synaptic_receptors_ui import create_synaptic_receptors_group


class TabFactory:
    """Factory class for creating MainWindow tabs."""

    # Tab configuration: name -> (title, user_level, visible_by_default)
    TAB_CONFIG = {
        "core": ("Core", "beginner", True),
        "network": ("Network", "intermediate", False),
        "simulation": ("Simulation", "beginner", True),
        "synapses": ("Synapses", "intermediate", False),
        "plasticity": ("Plasticity", "advanced", False),
        "neuromodulation": ("Neuromodulation", "advanced", False),
        "multicompartment": ("Multi-Compartment", "advanced", False),
    }

    def __init__(self, main_window):
        """Initialize the tab factory.

        Args:
            main_window: The MainWindow instance to create tabs for.
        """
        self.main_window = main_window

    def create_all_tabs(self, tab_widget):
        """Create all tabs and add them to the tab widget.

        Args:
            tab_widget: QTabWidget to add tabs to.

        Returns:
            dict: Tab info dictionary for visibility management.
        """
        tab_info = {}

        # Create each tab
        tab_info["core"] = self._create_core_tab(tab_widget)
        tab_info["network"] = self._create_network_tab(tab_widget)
        tab_info["simulation"] = self._create_simulation_tab(tab_widget)
        tab_info["synapses"] = self._create_synapses_tab(tab_widget)
        tab_info["plasticity"] = self._create_plasticity_tab(tab_widget)
        tab_info["neuromodulation"] = self._create_neuromodulation_tab(tab_widget)
        tab_info["multicompartment"] = self._create_multicompartment_tab(tab_widget)

        return tab_info

    def _create_scrollable_tab(self, content_widget, tab_widget, tab_key):
        """Create a scrollable tab with proper configuration.

        Args:
            content_widget: The widget containing tab content.
            tab_widget: QTabWidget to add tab to.
            tab_key: Key for this tab (e.g., "core", "network").

        Returns:
            dict: Tab info dictionary for this tab.
        """
        title, level, visible = self.TAB_CONFIG[tab_key]

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        tab_index = tab_widget.addTab(scroll_area, title)

        return {"index": tab_index, "widget": scroll_area, "level": level, "visible": visible}

    def _create_core_tab(self, tab_widget):
        """Create the Core tab with config, neuron model, sim params, noise, and input patterns."""
        content = QWidget()
        layout = QVBoxLayout(content)

        # Configuration Management
        layout.addWidget(create_config_management_group(self.main_window))

        # Neuron Model Selection
        layout.addWidget(create_neuron_model_group(self.main_window))

        # Simulation Parameters
        layout.addWidget(create_simulation_parameters_group(self.main_window))

        # Noise Options
        layout.addWidget(create_noise_options_group(self.main_window))

        # Input Patterns
        layout.addWidget(create_input_patterns_group(self.main_window))

        return self._create_scrollable_tab(content, tab_widget, "core")

    def _create_network_tab(self, tab_widget):
        """Create the Network tab with network options, advanced features, and gap junctions."""
        content = QWidget()
        layout = QVBoxLayout(content)

        # Network Options
        layout.addWidget(create_network_options_group(self.main_window))

        # Advanced Network Features
        layout.addWidget(create_advanced_network_group(self.main_window))

        # Gap Junctions
        layout.addWidget(create_gap_junctions_group(self.main_window))

        return self._create_scrollable_tab(content, tab_widget, "network")

    def _create_simulation_tab(self, tab_widget):
        """Create the Simulation tab."""
        simulation_widget = create_simulation_tab(self.main_window)

        title, level, visible = self.TAB_CONFIG["simulation"]
        tab_index = tab_widget.addTab(simulation_widget, title)

        return {"index": tab_index, "widget": simulation_widget, "level": level, "visible": visible}

    def _create_synapses_tab(self, tab_widget):
        """Create the Synapses tab with receptors and short-term plasticity."""
        content = QWidget()
        layout = QVBoxLayout(content)

        # Synaptic Receptors
        layout.addWidget(create_synaptic_receptors_group(self.main_window))

        # Short-Term Plasticity
        layout.addWidget(create_short_term_plasticity_group(self.main_window))

        return self._create_scrollable_tab(content, tab_widget, "synapses")

    def _create_plasticity_tab(self, tab_widget):
        """Create the Plasticity tab with calcium dynamics and homeostatic plasticity."""
        content = QWidget()
        layout = QVBoxLayout(content)

        # Calcium Dynamics
        layout.addWidget(create_calcium_dynamics_group(self.main_window))

        # Homeostatic Plasticity
        layout.addWidget(create_homeostatic_plasticity_group(self.main_window))

        return self._create_scrollable_tab(content, tab_widget, "plasticity")

    def _create_neuromodulation_tab(self, tab_widget):
        """Create the Neuromodulation tab."""
        content = create_neuromodulation_group(self.main_window)
        return self._create_scrollable_tab(content, tab_widget, "neuromodulation")

    def _create_multicompartment_tab(self, tab_widget):
        """Create the Multi-Compartment tab."""
        content = create_multicompartment_group(self.main_window)
        return self._create_scrollable_tab(content, tab_widget, "multicompartment")
