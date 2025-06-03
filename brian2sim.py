import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QStackedWidget, QSpinBox, QDoubleSpinBox,
    QCheckBox, QScrollArea, QGridLayout, QFormLayout, QMessageBox, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt

from config_manager import ConfigManager
from neuron_models_ui import create_neuron_model_group
from neuron_models import NeuronModelsManager
from sim_params_ui import create_simulation_parameters_group
from sim_params import SimParamsManager
from noise_options_ui import create_noise_options_group
from noise_options import NoiseOptionsManager
from network_options_ui import create_network_options_group
from network_options import NetworkOptionsManager
from advanced_network_ui import create_advanced_network_group
from advanced_network_manager import AdvancedNetworkManager
from config_manager_ui import create_config_management_group

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brian2Sim")
        self.setGeometry(100, 100, 900, 700)

        # Initialize all managers
        self.config_manager = ConfigManager(self)
        self.neuron_models_manager = NeuronModelsManager(self)
        self.sim_params_manager = SimParamsManager(self)
        self.noise_options_manager = NoiseOptionsManager(self)
        self.network_options_manager = NetworkOptionsManager(self)
        self.advanced_network_manager = AdvancedNetworkManager(self)

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

        # Config Tab UI elements - will be created by config_manager_ui
        self.load_config_button = None
        self.save_config_button = None
        
        # Initialize UI before connecting signals
        self._init_ui()
        
        # Set the sim_params_ui_module for SimParamsManager
        import sim_params_ui
        self.sim_params_manager.sim_params_ui_module = sim_params_ui

        # Connect signals after UI is initialized but before setting initial state
        self.neuron_models_manager.connect_signals()
        self.sim_params_manager.connect_signals()
        self.noise_options_manager.connect_signals()
        self.network_options_manager.connect_signals()
        self.advanced_network_manager.connect_signals()

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

        # --- Main Tab Content Setup ---
        # Create a dedicated QWidget to hold all the content for the main tab.
        # This widget will be placed inside the QScrollArea.
        main_tab_content_holder = QWidget()
        
        # Main layout for this content_holder widget
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

        # --- Network Options ---
        network_options_group = create_network_options_group(self)
        main_tab_layout.addWidget(network_options_group)

        # --- Advanced Network Features ---
        advanced_network_group = create_advanced_network_group(self)
        main_tab_layout.addWidget(advanced_network_group)

        # Scroll Area for the Main Tab's content
        main_tab_scroll_area = QScrollArea()
        main_tab_scroll_area.setWidgetResizable(True)
        main_tab_scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        main_tab_scroll_area.setWidget(main_tab_content_holder)

        # Add the scroll_area (which contains all the content) as the "Main" tab page
        self.tabs.addTab(main_tab_scroll_area, "Main")
        
        # Set initial tab
        self.tabs.setCurrentIndex(0)

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
                self.neuron_models_manager.load_neuron_model_config(config_data.get("neuron_model_settings", {}))
                
                # 2. Load simulation parameters
                self.sim_params_manager.load_sim_params(config_data.get("simulation_parameters", {}))
                
                # 3. Load noise options
                self.noise_options_manager.load_noise_options(config_data.get("noise_options", {}))
                
                # 4. Load network options
                self.network_options_manager.load_network_options(config_data.get("network_options", {}))
                
                # 5. Load advanced network options
                self.advanced_network_manager.load_advanced_network_options(config_data.get("advanced_network_options", {}))

    def save_configuration(self):
        """Save current configuration to a JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", "JSON Files (*.json)")
        if file_path:
            config_data = {
                "neuron_model_settings": self.neuron_models_manager.get_neuron_model_config(),
                "simulation_parameters": self.sim_params_manager.get_sim_params(),
                "noise_options": self.noise_options_manager.get_noise_options(),
                "network_options": self.network_options_manager.get_network_options(),
                "advanced_network_options": self.advanced_network_manager.get_advanced_network_options()            }
            self.config_manager.save_config(config_data, file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
