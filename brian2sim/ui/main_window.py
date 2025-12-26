import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from brian2sim.core.code_generator import CodeGenerator

# Core
from brian2sim.core.config_manager import ConfigManager
from brian2sim.core.results_manager import ResultsManager
from brian2sim.core.simulation_engine import SimulationEngine
from brian2sim.core.simulation_manager import SimulationManager
from brian2sim.managers.advanced_network_manager import AdvancedNetworkManager
from brian2sim.managers.calcium_dynamics_manager import CalciumDynamicsManager
from brian2sim.managers.cross_tab_dependencies import CrossTabDependencyManager
from brian2sim.managers.gap_junctions_manager import GapJunctionsManager
from brian2sim.managers.homeostatic_plasticity_manager import HomeostaticPlasticityManager
from brian2sim.managers.input_patterns_manager import InputPatternsManager
from brian2sim.managers.multicompartment_manager import MulticompartmentManager
from brian2sim.managers.network_manager import NetworkOptionsManager
from brian2sim.managers.neuromodulation_manager import NeuromodulationManager
from brian2sim.managers.neuron_models_manager import NeuronModelsManager
from brian2sim.managers.noise_manager import NoiseOptionsManager

# Managers
from brian2sim.managers.parameter_validation import ValidationManager
from brian2sim.managers.short_term_plasticity_manager import ShortTermPlasticityManager
from brian2sim.managers.sim_params_manager import SimParamsManager
from brian2sim.managers.synaptic_receptors_manager import SynapticReceptorsManager

# UI
from brian2sim.ui.menu_bar import MenuBarManager
from brian2sim.ui.tab_factory import TabFactory


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brian2Sim")
        self.setGeometry(100, 100, 900, 700)  # Initialize all managers
        self.config_manager = ConfigManager(self)
        self.neuron_models_manager = NeuronModelsManager(self)
        self.sim_params_manager = SimParamsManager(self)
        self.noise_options_manager = NoiseOptionsManager(self)
        self.input_patterns_manager = InputPatternsManager(self)
        self.network_options_manager = NetworkOptionsManager(self)
        self.advanced_network_manager = AdvancedNetworkManager(self)
        self.gap_junctions_manager = GapJunctionsManager(self)
        self.neuromodulation_manager = NeuromodulationManager(self)
        self.homeostatic_plasticity_manager = HomeostaticPlasticityManager(self)
        self.multicompartment_manager = MulticompartmentManager(self)
        self.calcium_dynamics_manager = CalciumDynamicsManager(self)
        self.short_term_plasticity_manager = ShortTermPlasticityManager(self)
        self.synaptic_receptors_manager = SynapticReceptorsManager(self)

        # Initialize cross-tab dependency manager (after all other managers)
        self.cross_tab_dependency_manager = CrossTabDependencyManager(self)

        # Initialize validation manager (after all other managers)
        self.validation_manager = ValidationManager(self)

        # Initialize menu bar manager
        self.menu_bar_manager = MenuBarManager(self)

        # Initialize simulation components
        self.simulation_engine = SimulationEngine()
        self.results_manager = ResultsManager(self)
        self.code_generator = CodeGenerator()
        # Start the simulation manager
        self.simulation_manager = SimulationManager(self)

        # Store references to UI elements that need to be accessed by managers
        self.neuron_model_combo = None
        self.neuron_model_stacked_widget = None
        self.neuron_model_forms = {}
        self.neuron_model_preset_combo = None

        # Simulation Parameters UI elements - will be created by sim_params_ui
        self.sim_time_input = None
        self.input_current_input = None
        self.num_neurons_input = None
        self.current_start_input = None
        self.current_duration_input = None
        self.lif_threshold_input = None
        self.lif_reset_input = None
        self.sim_params_layout = None  # Will be set by sim_params_ui
        # For sim_params_ui to manage grid layout state
        self.sim_params_current_row = 0
        self.sim_params_current_col = 0
        self.sim_params_num_cols = 3

        # Noise Options UI elements - will be created by noise_options_ui
        self.noise_checkbox = None
        self.noise_params_group = None
        self.noise_intensity_input = None
        self.noise_method_combo = None
        self.noise_params_layout = None  # Will be set by noise_options_ui
        # For noise_options_ui to manage grid layout state
        self.noise_params_current_row = 0
        self.noise_params_current_col = 0
        self.noise_params_num_cols = 2

        # Network Options UI elements - will be created by network_options_ui
        self.synaptic_connections_checkbox = None
        self.synapse_params_group = None
        self.synapse_params_layout = None  # QFormLayout
        self.synaptic_weight_input = None
        self.network_topology_combo = None
        self.topology_params_stacked_widget = None
        # Topology-specific forms and their widgets
        self.one_to_one_form = None
        self.all_to_all_form = None
        self.allow_self_connections_checkbox = None
        self.random_form = None
        self.connection_probability_input = None
        self.small_world_form = None
        self.sw_nearest_neighbors_input = None
        self.sw_rewiring_probability_input = None

        # Advanced Network Features UI elements - will be created by advanced_network_ui
        self.dales_principle_checkbox = None
        self.dales_principle_params_group = None
        self.dales_principle_forms = {}
        self.synaptic_delays_checkbox = None
        self.synaptic_delays_params_group = None
        self.synaptic_delays_forms = {}
        self.stdp_checkbox = None
        self.stdp_params_group = None
        self.stdp_forms = {}
        self.stdp_preset_combo = None
        self.distance_connectivity_checkbox = None
        self.distance_connectivity_params_group = None
        self.distance_connectivity_forms = {}
        self.distance_connectivity_preset_combo = None
        self.advanced_network_preset_combo = None

        # Simulation UI elements - will be created by simulation_ui
        self.run_simulation_button = None
        self.stop_simulation_button = None
        self.reset_simulation_button = None
        self.auto_plot_checkbox = None
        self.show_statistics_checkbox = None
        self.simulation_progress_bar = None
        self.simulation_status_label = None
        self.elapsed_time_label = None
        self.remaining_time_label = None
        self.simulation_log = None
        self.results_tabs = None
        self.raster_plot_widget = None
        self.voltage_plot_widget = None
        self.statistics_widget = None

        # Config Tab UI elements - will be created by config_manager_ui
        self.load_config_button = None
        self.save_config_button = None

        # Initialize UI before connecting signals
        self._init_ui()

        # Set the sim_params_ui_module for SimParamsManager
        from brian2sim.ui.tabs import sim_params_ui

        self.sim_params_manager.sim_params_ui_module = sim_params_ui

        # Setup menu bar after UI is initialized
        self.menu_bar_manager.setup_menu_bar()

        # Connect signals after UI is initialized but before setting initial state
        self.neuron_models_manager.connect_signals()
        self.sim_params_manager.connect_signals()
        self.noise_options_manager.connect_signals()
        self.input_patterns_manager.connect_signals()
        self.network_options_manager.connect_signals()
        self.advanced_network_manager.connect_signals()
        self.neuromodulation_manager.connect_signals()
        self.homeostatic_plasticity_manager.connect_signals()
        self.multicompartment_manager.connect_signals()
        self.calcium_dynamics_manager.connect_signals()
        self.short_term_plasticity_manager.connect_signals()
        self.synaptic_receptors_manager.connect_signals()

        # Connect cross-tab dependencies for neuroscientific accuracy
        self.cross_tab_dependency_manager.connect_dependencies()

        # Setup parameter validation (validate on any parameter change)
        for manager_name in [
            "neuron_models_manager",
            "sim_params_manager",
            "noise_options_manager",
            "network_options_manager",
            "gap_junctions_manager",
            "synaptic_receptors_manager",
            "calcium_dynamics_manager",
            "short_term_plasticity_manager",
            "homeostatic_plasticity_manager",
            "neuromodulation_manager",
            "multicompartment_manager",
        ]:
            if hasattr(self, manager_name):
                manager = getattr(self, manager_name)
                if hasattr(manager, "param_changed"):
                    manager.param_changed.connect(
                        self.validation_manager.validate_current_parameters
                    )

        # Connect simulation components
        self.simulation_manager.set_components(
            self.simulation_engine, self.results_manager, self.code_generator
        )

        # Connect simulation manager signals
        self.simulation_manager.progress_updated.connect(self._on_simulation_progress)
        self.simulation_manager.simulation_finished.connect(self._on_simulation_finished)
        self.simulation_manager.log_message.connect(self._on_simulation_log)

        # Set initial model to LIF through the neuron_models_manager
        for i in range(self.neuron_model_combo.count()):
            if self.neuron_model_combo.itemData(i) == "lif":
                self.neuron_model_combo.setCurrentIndex(i)
                break

        # Initial update of neuron model form and visibility
        self.neuron_models_manager.update_neuron_param_form_and_presets(
            self.neuron_model_combo.currentIndex()
        )

    def closeEvent(self, event):
        """Called when the application is closing."""
        try:
            # Validate parameters - returns True if valid
            is_valid = self.validation_manager.validate_current_parameters()
            if not is_valid and self.validation_manager.current_errors:
                # Check if there are actual errors (not just warnings)
                has_errors = any(
                    e.severity == "error" for e in self.validation_manager.current_errors
                )
                if has_errors:
                    reply = QMessageBox.question(
                        self,
                        "Validation Errors",
                        "There are parameter validation errors. Are you sure you want to close?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if reply == QMessageBox.StandardButton.No:
                        event.ignore()
                        return

            event.accept()
        except Exception as e:
            print(f"Error during close: {e}")
            event.accept()

    def _init_ui(self):
        """Initialize the user interface using TabFactory."""
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tab widget for different sections
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Store tab information for dynamic visibility management
        self.current_user_level = "beginner"  # Default to beginner mode

        # Use TabFactory to create all tabs
        tab_factory = TabFactory(self)
        self.tab_info = tab_factory.create_all_tabs(self.tabs)

        # Set initial tab
        self.tabs.setCurrentIndex(0)

        # Apply initial tab visibility for beginner level
        self.set_user_level("beginner")

    def set_user_level(self, level):
        """Set the user level and update tab visibility accordingly."""
        self.current_user_level = level

        # Define which tabs are visible for each user level
        # Core and Simulation tabs are ALWAYS visible - they're essential
        level_visibility = {
            "beginner": ["core", "simulation"],
            "intermediate": ["core", "simulation", "network", "synapses"],
            "advanced": [
                "core",
                "simulation",
                "network",
                "synapses",
                "plasticity",
                "neuromodulation",
                "multicompartment",
            ],
        }

        # Show/hide tabs based on user level
        visible_tabs = level_visibility.get(level, level_visibility["beginner"])

        for tab_key, tab_data in self.tab_info.items():
            # Core and Simulation tabs are always visible - never hide them
            if tab_key in ["core", "simulation"]:
                should_be_visible = True
            else:
                should_be_visible = tab_key in visible_tabs

            tab_data["visible"] = should_be_visible

            if should_be_visible:
                # Check if tab is already in the tab widget
                current_index = self.tabs.indexOf(tab_data["widget"])
                if current_index == -1:
                    # Tab is not currently in widget, add it back in correct position
                    self._restore_tab(tab_key, tab_data)
            else:
                # Hide tab by removing it from tab widget
                current_index = self.tabs.indexOf(tab_data["widget"])
                if current_index != -1:
                    self.tabs.removeTab(current_index)

    def _restore_tab(self, tab_key, tab_data):
        """Restore a tab to its correct position in the tab widget."""
        # Calculate correct position based on tab order
        tab_order = [
            "core",
            "network",
            "simulation",
            "synapses",
            "plasticity",
            "neuromodulation",
            "multicompartment",
        ]
        target_position = tab_order.index(tab_key)

        # Count how many tabs before this one are currently visible
        actual_position = 0
        for i, other_tab_key in enumerate(tab_order[:target_position]):
            if other_tab_key in self.tab_info and self.tab_info[other_tab_key]["visible"]:
                other_index = self.tabs.indexOf(self.tab_info[other_tab_key]["widget"])
                if other_index != -1:
                    actual_position += 1

        # Get the tab title from the widget
        tab_title = {
            "core": "Core",
            "network": "Network",
            "simulation": "Simulation",
            "synapses": "Synapses",
            "plasticity": "Plasticity",
            "neuromodulation": "Neuromodulation",
            "multicompartment": "Multi-Compartment",
        }.get(tab_key, tab_key.title())

        # Insert tab at correct position
        self.tabs.insertTab(actual_position, tab_data["widget"], tab_title)

    def _add_param_to_grid_layout(
        self, grid_layout, label_text, widget, num_cols, current_pos_tracker
    ):
        """
        Adds a label and a widget to the specified QGridLayout, managing row and column positioning.
        Labels are placed above their respective widgets.

        Args:
            grid_layout (QGridLayout): The layout to add to.
            label_text (str): The text for the label.
            widget (QWidget): The widget (e.g., QSpinBox, QLineEdit) for the parameter.
            num_cols (int): The number of columns in this grid section.
            current_pos_tracker (list): A list [row, col] to track current position.
        """
        row, col = current_pos_tracker

        cell_widget = QWidget()
        cell_layout = QVBoxLayout(cell_widget)
        cell_layout.setContentsMargins(2, 2, 2, 2)  # Small margins for compactness
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        cell_layout.addWidget(label)
        cell_layout.addWidget(widget)

        grid_layout.addWidget(cell_widget, row, col)

        current_pos_tracker[1] += 1  # Move to next column
        if current_pos_tracker[1] >= num_cols:
            current_pos_tracker[1] = 0  # Reset column
            current_pos_tracker[0] += 1  # Move to next row

    def update_lif_params_visibility(self, is_lif_model):
        self.sim_params_manager.update_lif_params_visibility(is_lif_model)

    def load_configuration(self):
        """Load configuration from a JSON file and update all UI elements."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            config_data = self.config_manager.load_config(file_path)
            if config_data:
                # Load configuration in a specific order to ensure dependent UI updates work correctly
                # 1. Load neuron model first as other sections may depend on it
                self.neuron_models_manager.load_neuron_model_config(
                    config_data.get("neuron_model", {})
                )

                # 2. Load simulation parameters
                self.sim_params_manager.load_sim_params(config_data.get("simulation", {}))

                # 3. Load noise options
                self.noise_options_manager.load_noise_options(config_data.get("noise", {}))

                # 4. Load input patterns
                self.input_patterns_manager.load_input_patterns_config(
                    config_data.get("input_patterns", {})
                )

                # 5. Load network options
                self.network_options_manager.load_network_options(config_data.get("network", {}))

                # 6. Load advanced network options
                self.advanced_network_manager.load_advanced_network_options(
                    config_data.get("advanced_network", {})
                )

                # 7. Load advanced module configurations
                if hasattr(self, "gap_junctions_ui"):
                    self.gap_junctions_ui.load_params_from_config(
                        config_data.get("gap_junctions", {})
                    )
                if hasattr(self, "synaptic_receptors_ui"):
                    self.synaptic_receptors_ui.load_params_from_config(
                        config_data.get("synaptic_receptors", {})
                    )
                if hasattr(self, "calcium_dynamics_ui"):
                    self.calcium_dynamics_ui.load_params_from_config(
                        config_data.get("calcium_dynamics", {})
                    )
                if hasattr(self, "homeostatic_plasticity_ui"):
                    self.homeostatic_plasticity_ui.load_params_from_config(
                        config_data.get("homeostatic_plasticity", {})
                    )
                if hasattr(self, "neuromodulation_ui"):
                    self.neuromodulation_ui.load_params_from_config(
                        config_data.get("neuromodulation", {})
                    )
                if hasattr(self, "multicompartment_ui"):
                    self.multicompartment_ui.load_params_from_config(
                        config_data.get("multicompartment", {})
                    )
                if hasattr(self, "short_term_plasticity_ui"):
                    self.short_term_plasticity_ui.load_params_from_config(
                        config_data.get("short_term_plasticity", {})
                    )

    def save_configuration(self):
        """Save current configuration to a JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            config_data = {
                "neuron_model": self.neuron_models_manager.get_neuron_model_config(),
                "simulation": self.sim_params_manager.get_sim_params_config(),
                "noise": self.noise_options_manager.get_noise_options_config(),
                "input_patterns": self.input_patterns_manager.get_input_patterns_config(),
                "network": self.network_options_manager.get_network_options_config(),
                "advanced_network": self.advanced_network_manager.get_advanced_network_config(),
            }
            # Add advanced module configurations
            if hasattr(self, "gap_junctions_ui"):
                config_data["gap_junctions"] = self.gap_junctions_ui.get_params_for_save()
            if hasattr(self, "synaptic_receptors_ui"):
                config_data["synaptic_receptors"] = self.synaptic_receptors_ui.get_params_for_save()
            if hasattr(self, "calcium_dynamics_ui"):
                config_data["calcium_dynamics"] = self.calcium_dynamics_ui.get_params_for_save()
            if hasattr(self, "homeostatic_plasticity_ui"):
                config_data["homeostatic_plasticity"] = (
                    self.homeostatic_plasticity_ui.get_params_for_save()
                )
            if hasattr(self, "neuromodulation_ui"):
                config_data["neuromodulation"] = self.neuromodulation_ui.get_params_for_save()
            if hasattr(self, "multicompartment_ui"):
                config_data["multicompartment"] = self.multicompartment_ui.get_params_for_save()
            if hasattr(self, "short_term_plasticity_ui"):
                config_data["short_term_plasticity"] = (
                    self.short_term_plasticity_ui.get_params_for_save()
                )

            self.config_manager.save_config(config_data, file_path)

    def _on_simulation_progress(self, progress, message):
        """Handle simulation progress updates."""
        if hasattr(self, "simulation_progress_bar"):
            self.simulation_progress_bar.setValue(progress)
        if hasattr(self, "simulation_status_label"):
            self.simulation_status_label.setText(message)

    def _on_simulation_finished(self, success):
        """Handle simulation completion."""
        if success:
            if hasattr(self, "simulation_status_label"):
                self.simulation_status_label.setText("Simulation completed successfully!")
        else:
            if hasattr(self, "simulation_status_label"):
                self.simulation_status_label.setText("Simulation failed or was stopped")

    def _on_simulation_log(self, message):
        """Handle simulation log messages."""
        if hasattr(self, "simulation_log"):
            current_text = self.simulation_log.toPlainText()
            if current_text:
                new_text = current_text + "\n" + message
            else:
                new_text = message
            self.simulation_log.setPlainText(new_text)
            # Auto-scroll to bottom
            scrollbar = self.simulation_log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
