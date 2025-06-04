"""
Simulation UI Components for Brian2 neural network simulator.
Creates the simulation tab with controls, progress tracking, and results visualization.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel, 
    QProgressBar, QTextEdit, QScrollArea, QFrame, QSplitter, QTabWidget,
    QGridLayout, QCheckBox, QSpinBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer

# Handle optional matplotlib imports
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    # Create dummy classes for when matplotlib is not available
    class FigureCanvas:
        def __init__(self, *args, **kwargs):
            pass
    
    class Figure:
        def __init__(self, *args, **kwargs):
            pass

# Handle optional numpy import
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

def create_simulation_tab(main_window):
    """
    Creates the simulation tab with controls, progress tracking, and results visualization.
    """
    # Main simulation widget
    sim_widget = QWidget()
    sim_layout = QVBoxLayout(sim_widget)
    
    # Create splitter for main areas
    main_splitter = QSplitter(Qt.Orientation.Horizontal)
    sim_layout.addWidget(main_splitter)
    
    # Left panel for controls
    controls_widget = QWidget()
    controls_layout = QVBoxLayout(controls_widget)
    controls_widget.setMaximumWidth(350)
    controls_widget.setMinimumWidth(300)
    
    # --- Simulation Controls Group ---
    controls_group = create_simulation_controls_group(main_window)
    controls_layout.addWidget(controls_group)
    
    # --- Progress Group ---
    progress_group = create_progress_group(main_window)
    controls_layout.addWidget(progress_group)
    
    # --- Export Group ---
    export_group = create_export_group(main_window)
    controls_layout.addWidget(export_group)
    
    # --- Log Group ---
    log_group = create_log_group(main_window)
    controls_layout.addWidget(log_group)
    
    controls_layout.addStretch()
    
    # Right panel for results
    results_widget = create_results_panel(main_window)
    
    # Add to splitter
    main_splitter.addWidget(controls_widget)
    main_splitter.addWidget(results_widget)
    main_splitter.setStretchFactor(0, 0)  # Controls don't stretch
    main_splitter.setStretchFactor(1, 1)  # Results stretch
    
    return sim_widget

def create_simulation_controls_group(main_window):
    """Create simulation control buttons and settings."""
    controls_group = QGroupBox("Simulation Controls")
    layout = QVBoxLayout(controls_group)
    
    # Main control buttons
    button_layout = QHBoxLayout()
    
    # Run button
    main_window.run_simulation_button = QPushButton("Run Simulation")
    main_window.run_simulation_button.setToolTip("Execute the neural network simulation with current parameters")
    main_window.run_simulation_button.clicked.connect(main_window.simulation_manager.start_simulation)
    button_layout.addWidget(main_window.run_simulation_button)
    
    # Stop button
    main_window.stop_simulation_button = QPushButton("Stop")
    main_window.stop_simulation_button.setToolTip("Stop the running simulation")
    main_window.stop_simulation_button.setEnabled(False)
    main_window.stop_simulation_button.clicked.connect(main_window.simulation_manager.stop_simulation)
    button_layout.addWidget(main_window.stop_simulation_button)
    
    layout.addLayout(button_layout)
    
    # Reset button
    main_window.reset_simulation_button = QPushButton("Reset Results")
    main_window.reset_simulation_button.setToolTip("Clear simulation results and reset plots")
    main_window.reset_simulation_button.clicked.connect(main_window.simulation_manager.reset_simulation)
    layout.addWidget(main_window.reset_simulation_button)
    
    # Quick simulation options
    options_layout = QVBoxLayout()
    
    main_window.auto_plot_checkbox = QCheckBox("Auto-plot results")
    main_window.auto_plot_checkbox.setChecked(True)
    main_window.auto_plot_checkbox.setToolTip("Automatically generate plots when simulation completes")
    options_layout.addWidget(main_window.auto_plot_checkbox)
    
    main_window.show_statistics_checkbox = QCheckBox("Show statistics")
    main_window.show_statistics_checkbox.setChecked(True)
    main_window.show_statistics_checkbox.setToolTip("Display firing rate and other statistics")
    options_layout.addWidget(main_window.show_statistics_checkbox)
    
    layout.addLayout(options_layout)
    
    return controls_group

def create_progress_group(main_window):
    """Create progress tracking components."""
    progress_group = QGroupBox("Progress")
    layout = QVBoxLayout(progress_group)
    
    # Progress bar
    main_window.simulation_progress_bar = QProgressBar()
    main_window.simulation_progress_bar.setRange(0, 100)
    main_window.simulation_progress_bar.setValue(0)
    layout.addWidget(main_window.simulation_progress_bar)
    
    # Status label
    main_window.simulation_status_label = QLabel("Ready to simulate")
    main_window.simulation_status_label.setWordWrap(True)
    layout.addWidget(main_window.simulation_status_label)
    
    # Time estimates
    time_layout = QGridLayout()
    
    time_layout.addWidget(QLabel("Elapsed:"), 0, 0)
    main_window.elapsed_time_label = QLabel("00:00")
    time_layout.addWidget(main_window.elapsed_time_label, 0, 1)
    
    time_layout.addWidget(QLabel("Remaining:"), 1, 0)
    main_window.remaining_time_label = QLabel("--:--")
    time_layout.addWidget(main_window.remaining_time_label, 1, 1)
    
    layout.addLayout(time_layout)
    
    return progress_group

def create_export_group(main_window):
    """Create data export controls."""
    export_group = QGroupBox("Export")
    layout = QVBoxLayout(export_group)
    
    # Export buttons
    export_data_button = QPushButton("Export Data")
    export_data_button.setToolTip("Export simulation data to CSV/JSON format")
    export_data_button.clicked.connect(main_window.simulation_manager.export_data)
    layout.addWidget(export_data_button)
    
    export_plots_button = QPushButton("Export Plots")
    export_plots_button.setToolTip("Save current plots as PNG/PDF")
    export_plots_button.clicked.connect(main_window.simulation_manager.export_plots)
    layout.addWidget(export_plots_button)
    
    generate_code_button = QPushButton("Generate Code")
    generate_code_button.setToolTip("Generate standalone Python script for this simulation")
    generate_code_button.clicked.connect(main_window.simulation_manager.generate_code)
    layout.addWidget(generate_code_button)
    
    return export_group

def create_log_group(main_window):
    """Create simulation log display."""
    log_group = QGroupBox("Simulation Log")
    layout = QVBoxLayout(log_group)
    
    # Log text area
    main_window.simulation_log = QTextEdit()
    main_window.simulation_log.setMaximumHeight(120)
    main_window.simulation_log.setReadOnly(True)
    main_window.simulation_log.setPlainText("Simulation log will appear here...")
    layout.addWidget(main_window.simulation_log)
    
    # Clear log button
    clear_log_button = QPushButton("Clear Log")
    clear_log_button.clicked.connect(main_window.simulation_log.clear)
    layout.addWidget(clear_log_button)
    
    return log_group

def create_results_panel(main_window):
    """Create the results visualization panel."""
    results_widget = QWidget()
    results_layout = QVBoxLayout(results_widget)
    
    # Results tabs
    main_window.results_tabs = QTabWidget()
    results_layout.addWidget(main_window.results_tabs)
    
    # Spike raster plot tab
    main_window.raster_plot_widget = create_plot_widget("Spike Raster Plot")
    main_window.results_tabs.addTab(main_window.raster_plot_widget, "Spike Raster")
    
    # Voltage traces tab
    main_window.voltage_plot_widget = create_plot_widget("Membrane Voltage")
    main_window.results_tabs.addTab(main_window.voltage_plot_widget, "Voltage Traces")
    
    # Statistics tab
    main_window.statistics_widget = create_statistics_widget()
    main_window.results_tabs.addTab(main_window.statistics_widget, "Statistics")
    
    return results_widget

def create_plot_widget(title):
    """Create a matplotlib plot widget or placeholder if matplotlib not available."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    if MATPLOTLIB_AVAILABLE:
        # Create matplotlib figure and canvas
        figure = Figure(figsize=(8, 6), dpi=100)
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        
        # Store references for later use
        widget.figure = figure
        widget.canvas = canvas
        widget.axes = None  # Will be created when plotting
    else:
        # Create placeholder when matplotlib is not available
        placeholder = QLabel(f"{title}\n\n(matplotlib not available)\nInstall matplotlib to view plots")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(placeholder)
        
        # Store dummy references
        widget.figure = None
        widget.canvas = None
        widget.axes = None
    
    return widget

def create_statistics_widget():
    """Create the statistics display widget."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # Statistics text area
    stats_text = QTextEdit()
    stats_text.setReadOnly(True)
    stats_text.setPlainText("Statistics will appear here after simulation...")
    layout.addWidget(stats_text)
    
    # Store reference
    widget.stats_text = stats_text
    
    return widget