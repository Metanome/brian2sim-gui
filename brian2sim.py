import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QStackedWidget, QSpinBox, QDoubleSpinBox,
    QCheckBox, QScrollArea, QGridLayout, QFormLayout, QMessageBox, QFileDialog, QFrame,
    QDialog, QTextEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt

from parameter_validation import ValidationManager
from menu_bar import MenuBarManager
from config_manager import ConfigManager
from neuron_models_ui import create_neuron_model_group
from neuron_models import NeuronModelsManager
from sim_params_ui import create_simulation_parameters_group
from sim_params import SimParamsManager
from noise_options_ui import create_noise_options_group
from noise_options import NoiseOptionsManager
from input_patterns_ui import create_input_patterns_group
from input_patterns_manager import InputPatternsManager
from network_options_ui import create_network_options_group
from network_options import NetworkOptionsManager
from advanced_network_ui import create_advanced_network_group
from advanced_network_manager import AdvancedNetworkManager
from config_manager_ui import create_config_management_group
from simulation_ui import create_simulation_tab
from simulation_manager import SimulationManager
from simulation_engine import SimulationEngine
from results_manager import ResultsManager
from code_generator import CodeGenerator
from gap_junctions_ui import create_gap_junctions_group
from gap_junctions_manager import GapJunctionsManager
from neuromodulation_ui import create_neuromodulation_group
from neuromodulation_manager import NeuromodulationManager
from homeostatic_plasticity_ui import create_homeostatic_plasticity_group
from homeostatic_plasticity_manager import HomeostaticPlasticityManager
from multicompartment_ui import create_multicompartment_group
from multicompartment_manager import MulticompartmentManager
from calcium_dynamics_ui import create_calcium_dynamics_group
from calcium_dynamics_manager import CalciumDynamicsManager
from short_term_plasticity_ui import create_short_term_plasticity_group
from short_term_plasticity_manager import ShortTermPlasticityManager
from synaptic_receptors_ui import create_synaptic_receptors_group
from synaptic_receptors_manager import SynapticReceptorsManager
from cross_tab_dependencies import CrossTabDependencyManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brian2Sim")
        self.setGeometry(100, 100, 900, 700)        # Initialize all managers
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
        self.sim_params_layout = None # Will be set by sim_params_ui
        # For sim_params_ui to manage grid layout state
        self.sim_params_current_row = 0
        self.sim_params_current_col = 0
        self.sim_params_num_cols = 3

        # Noise Options UI elements - will be created by noise_options_ui
        self.noise_checkbox = None
        self.noise_params_group = None
        self.noise_intensity_input = None
        self.noise_method_combo = None
        self.noise_params_layout = None # Will be set by noise_options_ui
        # For noise_options_ui to manage grid layout state
        self.noise_params_current_row = 0
        self.noise_params_current_col = 0
        self.noise_params_num_cols = 2

        # Network Options UI elements - will be created by network_options_ui
        self.synaptic_connections_checkbox = None
        self.synapse_params_group = None
        self.synapse_params_layout = None # QFormLayout
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
        import sim_params_ui
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
        for manager_name in ['neuron_models_manager', 'sim_params_manager', 'noise_options_manager',
                           'network_options_manager', 'gap_junctions_manager', 'synaptic_receptors_manager',
                           'calcium_dynamics_manager', 'short_term_plasticity_manager', 
                           'homeostatic_plasticity_manager', 'neuromodulation_manager', 'multicompartment_manager']:
            if hasattr(self, manager_name):
                manager = getattr(self, manager_name)
                if hasattr(manager, 'param_changed'):
                    manager.param_changed.connect(self.validation_manager.validate_current_parameters)
        
        # Connect simulation components
        self.simulation_manager.set_components(
            self.simulation_engine, 
            self.results_manager, 
            self.code_generator
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
        self.neuron_models_manager.update_neuron_param_form_and_presets(self.neuron_model_combo.currentIndex())
        
    def closeEvent(self, event):
        """Called when the application is closing."""
        try:
            # Validate all parameters before closing
            validation_results = self.validation_manager.validate_all_parameters()
            if any(result.severity == 'error' for result in validation_results):
                reply = QMessageBox.question(self, 'Validation Errors', 
                    'There are parameter validation errors. Are you sure you want to close?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    event.ignore()
                    return
            
            self.config_manager.save_config()
            event.accept()
        except Exception as e:
            print(f"Error during close: {e}")
            event.accept()        # Connect signals after UI is initialized but before setting initial state
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
        for manager_name in ['neuron_models_manager', 'sim_params_manager', 'noise_options_manager',
                           'network_options_manager', 'gap_junctions_manager', 'synaptic_receptors_manager',
                           'calcium_dynamics_manager', 'short_term_plasticity_manager', 
                           'homeostatic_plasticity_manager', 'neuromodulation_manager', 'multicompartment_manager']:
            if hasattr(self, manager_name):
                manager = getattr(self, manager_name)
                if hasattr(manager, 'param_changed'):
                    manager.param_changed.connect(self.validation_manager.validate_current_parameters)
        
        # Connect simulation components
        self.simulation_manager.set_components(
            self.simulation_engine, 
            self.results_manager, 
            self.code_generator
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
        self.neuron_models_manager.update_neuron_param_form_and_presets(self.neuron_model_combo.currentIndex())

    def _init_ui(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tab widget for different sections
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Store tab information for dynamic visibility management
        self.tab_info = {}
        self.current_user_level = "beginner"  # Default to beginner mode

        # --- Main Tab Content Setup ---
        # Create a dedicated QWidget to hold all the content for the main tab.
        # This widget will be placed inside the QScrollArea.
        main_tab_content_holder = QWidget()
        
        # Main layout for this content_holder widget using standard layout
        main_tab_layout = QVBoxLayout(main_tab_content_holder)

        # --- Configuration Management ---
        config_management_group = create_config_management_group(self)
        main_tab_layout.addWidget(config_management_group)

        # --- Neuron Model Selection ---
        neuron_model_group = create_neuron_model_group(self)
        main_tab_layout.addWidget(neuron_model_group)

        # --- Simulation Parameters ---
        sim_params_group = create_simulation_parameters_group(self)
        main_tab_layout.addWidget(sim_params_group)

        # --- Noise Options ---
        noise_options_group = create_noise_options_group(self)
        main_tab_layout.addWidget(noise_options_group)

        # --- Input Patterns ---
        input_patterns_group = create_input_patterns_group(self)
        main_tab_layout.addWidget(input_patterns_group)

        # Scroll Area for the Main Tab's content
        main_tab_scroll_area = QScrollArea()
        # --- Core Tab (formerly Main) ---
        main_tab_scroll_area.setWidgetResizable(True)
        main_tab_scroll_area.setWidget(main_tab_content_holder)        
        core_tab_index = self.tabs.addTab(main_tab_scroll_area, "Core")
        self.tab_info["core"] = {
            "index": core_tab_index,
            "widget": main_tab_scroll_area,
            "level": "beginner",
            "visible": True
        }
        
        # --- Network Architecture Tab ---
        network_arch_content_holder = QWidget()
        network_arch_layout = QVBoxLayout(network_arch_content_holder)
        
        # Network Options
        network_options_group = create_network_options_group(self)
        network_arch_layout.addWidget(network_options_group)
        
        # Advanced Network Features
        advanced_network_group = create_advanced_network_group(self)
        network_arch_layout.addWidget(advanced_network_group)
        
        # Gap Junctions (part of network connectivity)
        gap_junctions_group = create_gap_junctions_group(self)
        network_arch_layout.addWidget(gap_junctions_group)
        
        # Network Architecture scroll area
        network_arch_scroll = QScrollArea()
        network_arch_scroll.setWidgetResizable(True)
        network_arch_scroll.setWidget(network_arch_content_holder)
        network_tab_index = self.tabs.addTab(network_arch_scroll, "Network")
        self.tab_info["network"] = {
            "index": network_tab_index,
            "widget": network_arch_scroll,
            "level": "intermediate",
            "visible": False  # Hidden by default for beginners
        }
        
        # --- Simulation Tab ---
        simulation_tab = create_simulation_tab(self)
        sim_tab_index = self.tabs.addTab(simulation_tab, "Simulation")
        self.tab_info["simulation"] = {
            "index": sim_tab_index,
            "widget": simulation_tab,
            "level": "beginner",
            "visible": True
        }
        
        # --- Synaptic Properties Tab ---
        synaptic_props_content_holder = QWidget()
        synaptic_props_layout = QVBoxLayout(synaptic_props_content_holder)
        
        # Synaptic Receptors
        synaptic_receptors_group = create_synaptic_receptors_group(self)
        synaptic_props_layout.addWidget(synaptic_receptors_group)
        
        # Short-Term Plasticity (affects synaptic transmission)
        short_term_plasticity_group = create_short_term_plasticity_group(self)
        synaptic_props_layout.addWidget(short_term_plasticity_group)
        
        # Synaptic Properties scroll area
        synaptic_props_scroll = QScrollArea()
        synaptic_props_scroll.setWidgetResizable(True)
        synaptic_props_scroll.setWidget(synaptic_props_content_holder)
        synaptic_tab_index = self.tabs.addTab(synaptic_props_scroll, "Synapses")
        self.tab_info["synapses"] = {
            "index": synaptic_tab_index,
            "widget": synaptic_props_scroll,
            "level": "intermediate",
            "visible": False
        }
        
        # --- Plasticity & Dynamics Tab ---
        plasticity_dynamics_content_holder = QWidget()
        plasticity_dynamics_layout = QVBoxLayout(plasticity_dynamics_content_holder)
        
        # Calcium Dynamics (underlying mechanism for many plasticity forms)
        calcium_dynamics_group = create_calcium_dynamics_group(self)
        plasticity_dynamics_layout.addWidget(calcium_dynamics_group)
        
        # Homeostatic Plasticity (often calcium-dependent)
        homeostatic_plasticity_group = create_homeostatic_plasticity_group(self)
        plasticity_dynamics_layout.addWidget(homeostatic_plasticity_group)
        
        # Plasticity & Dynamics scroll area
        plasticity_dynamics_scroll = QScrollArea()
        plasticity_dynamics_scroll.setWidgetResizable(True)
        plasticity_dynamics_scroll.setWidget(plasticity_dynamics_content_holder)
        plasticity_tab_index = self.tabs.addTab(plasticity_dynamics_scroll, "Plasticity")
        self.tab_info["plasticity"] = {
            "index": plasticity_tab_index,
            "widget": plasticity_dynamics_scroll,
            "level": "advanced",
            "visible": False
        }
        
        # --- Neuromodulation Tab ---
        neuromodulation_group = create_neuromodulation_group(self)
        neuromodulation_scroll = QScrollArea()
        neuromodulation_scroll.setWidgetResizable(True)
        neuromodulation_scroll.setWidget(neuromodulation_group)
        neuromodulation_tab_index = self.tabs.addTab(neuromodulation_scroll, "Neuromodulation")
        self.tab_info["neuromodulation"] = {
            "index": neuromodulation_tab_index,
            "widget": neuromodulation_scroll,
            "level": "advanced",
            "visible": False
        }
        
        # --- Multi-Compartment Tab ---
        multicompartment_group = create_multicompartment_group(self)
        multicompartment_scroll = QScrollArea()
        multicompartment_scroll.setWidgetResizable(True)
        multicompartment_scroll.setWidget(multicompartment_group)
        multicompartment_tab_index = self.tabs.addTab(multicompartment_scroll, "Multi-Compartment")
        self.tab_info["multicompartment"] = {
            "index": multicompartment_tab_index,
            "widget": multicompartment_scroll,
            "level": "advanced",
            "visible": False
        }
        
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
            "advanced": ["core", "simulation", "network", "synapses", "plasticity", "neuromodulation", "multicompartment"]
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
        tab_order = ["core", "network", "simulation", "synapses", "plasticity", "neuromodulation", "multicompartment"]
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
            "multicompartment": "Multi-Compartment"
        }.get(tab_key, tab_key.title())
        
        # Insert tab at correct position
        self.tabs.insertTab(actual_position, tab_data["widget"], tab_title)

    def _add_param_to_grid_layout(self, grid_layout, label_text, widget, num_cols, current_pos_tracker):
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
        cell_layout.setContentsMargins(2,2,2,2) # Small margins for compactness
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
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "JSON Files (*.json)")
        if file_path:
            config_data = self.config_manager.load_config(file_path)
            if config_data:
                # Load configuration in a specific order to ensure dependent UI updates work correctly
                # 1. Load neuron model first as other sections may depend on it
                self.neuron_models_manager.load_neuron_model_config(config_data.get("neuron_model", {}))
                
                # 2. Load simulation parameters
                self.sim_params_manager.load_sim_params(config_data.get("simulation", {}))
                
                # 3. Load noise options
                self.noise_options_manager.load_noise_options(config_data.get("noise", {}))
                
                # 4. Load input patterns
                self.input_patterns_manager.load_input_patterns_config(config_data.get("input_patterns", {}))
                
                # 5. Load network options
                self.network_options_manager.load_network_options(config_data.get("network", {}))
                
                # 5. Load advanced network options
                self.advanced_network_manager.load_advanced_network_options(config_data.get("advanced_network", {}))

    def save_configuration(self):
        """Save current configuration to a JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", "JSON Files (*.json)")
        if file_path:
            config_data = {
                "neuron_model": self.neuron_models_manager.get_neuron_model_config(),
                "simulation": self.sim_params_manager.get_sim_params_config(),
                "noise": self.noise_options_manager.get_noise_options_config(),
                "input_patterns": self.input_patterns_manager.get_input_patterns_config(),
                "network": self.network_options_manager.get_network_options_config(),
                "advanced_network": self.advanced_network_manager.get_advanced_network_config()
            }
            self.config_manager.save_config(config_data, file_path)

    def _on_simulation_progress(self, progress, message):
        """Handle simulation progress updates."""
        if hasattr(self, 'simulation_progress_bar'):
            self.simulation_progress_bar.setValue(progress)
        if hasattr(self, 'simulation_status_label'):
            self.simulation_status_label.setText(message)

    def _on_simulation_finished(self, success):
        """Handle simulation completion."""
        if success:
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.setText("Simulation completed successfully!")
        else:
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.setText("Simulation failed or was stopped")

    def _on_simulation_log(self, message):
        """Handle simulation log messages."""
        if hasattr(self, 'simulation_log'):
            current_text = self.simulation_log.toPlainText()
            if current_text:
                new_text = current_text + "\n" + message
            else:
                new_text = message
            self.simulation_log.setPlainText(new_text)
            # Auto-scroll to bottom
            scrollbar = self.simulation_log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
