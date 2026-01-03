"""
Simulation Manager for Brian2 neural network simulator.
Coordinates simulation execution, progress tracking, and results management.
"""

import json
import time
import csv
import os
import numpy as np
from datetime import datetime, timedelta

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QMessageBox


class SimulationManager(QObject):
    """Manager for simulation execution and coordination."""

    # Signals for UI updates
    progress_updated = pyqtSignal(int, str)  # progress percentage, status message
    simulation_finished = pyqtSignal(bool)  # success flag
    log_message = pyqtSignal(str)  # log message
    
    # Signals for Engine control (Cross-thread)
    start_simulation_signal = pyqtSignal(dict)
    stop_simulation_signal = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.simulation_engine = None  # Will be set later
        self.results_manager = None  # Will be set later
        self.code_generator = None  # Will be set later

        # Simulation state
        self.is_running = False
        self.simulation_data = None
        self.start_time = None

        # Progress tracking timer
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_display)

    def set_components(self, engine, results_manager, code_generator):
        """Set the simulation components after they're created."""
        self.simulation_engine = engine
        self.results_manager = results_manager
        self.code_generator = code_generator

        # Connect engine signals
        if self.simulation_engine:
            self.simulation_engine.progress_updated.connect(self.on_progress_updated)
            self.simulation_engine.simulation_completed.connect(self.on_simulation_completed)
            self.simulation_engine.simulation_error.connect(self.on_simulation_error)
            
            # Connect manager signals to engine slots
            self.start_simulation_signal.connect(self.simulation_engine.run_simulation)
            self.stop_simulation_signal.connect(self.simulation_engine.stop_simulation)

    def start_simulation(self):
        """Start the neural network simulation."""
        if self.is_running:
            self.log_message.emit("Simulation already running!")
            return

        try:
            # Validate configuration
            if not self._validate_configuration():
                return

            # Get simulation parameters from UI
            params = self._collect_simulation_parameters()

            # Update UI state
            self.is_running = True
            self.start_time = time.time()
            self._update_ui_for_running_state(True)

            # Start progress timer
            self.progress_timer.start(500)  # Update every 500ms

            # Log start
            self.log_message.emit(f"Starting simulation at {datetime.now().strftime('%H:%M:%S')}")
            self.log_message.emit(f"Parameters: {self._format_params_summary(params)}")

            # Start simulation in engine via signal
            if self.simulation_engine:
                self.start_simulation_signal.emit(params)
            else:
                # Fallback for testing without engine
                self._simulate_progress_for_testing()

        except Exception as e:
            self.log_message.emit(f"Error starting simulation: {str(e)}")
            self._update_ui_for_running_state(False)
            self.is_running = False

    def stop_simulation(self):
        """Stop the running simulation."""
        if not self.is_running:
            return

        self.log_message.emit("Stopping simulation...")

        if self.simulation_engine:
            self.stop_simulation_signal.emit()

        self._cleanup_simulation()
        self.log_message.emit("Simulation stopped by user")

    def reset_simulation(self):
        """Reset simulation results and UI."""
        if self.is_running:
            self.stop_simulation()

        # Clear results
        self.simulation_data = None

        # Reset UI
        self.main_window.simulation_progress_bar.setValue(0)
        self.main_window.simulation_status_label.setText("Ready to simulate")
        self.main_window.elapsed_time_label.setText("00:00")
        self.main_window.remaining_time_label.setText("--:--")

        # Clear plots and statistics
        if self.results_manager:
            self.results_manager.clear_results()

        self.log_message.emit("Simulation reset")

    def export_data(self):
        """Export simulation data to file."""
        if not self.simulation_data:
            QMessageBox.warning(
                self.main_window, "No Data", "No simulation data available to export."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Export Simulation Data",
            f"simulation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;CSV Files (*.csv)",
        )

        if file_path:
            try:
                if file_path.endswith(".csv"):
                    self._export_to_csv(file_path)
                else:
                    self._export_to_json(file_path)

                self.log_message.emit(f"Data exported to: {file_path}")
                QMessageBox.information(
                    self.main_window,
                    "Export Complete",
                    f"Data exported successfully to:\n{file_path}",
                )
            except Exception as e:
                error_msg = f"Failed to export data: {str(e)}"
                self.log_message.emit(error_msg)
                QMessageBox.critical(self.main_window, "Export Error", error_msg)

    def export_plots(self):
        """Export current plots to image files."""
        if not hasattr(self.main_window, "results_tabs"):
            QMessageBox.warning(self.main_window, "No Plots", "No plots available to export.")
            return

        dir_path = QFileDialog.getExistingDirectory(
            self.main_window, "Select Directory for Plot Export"
        )

        if dir_path and self.results_manager:
            try:
                exported_files = self.results_manager.export_plots(dir_path)
                if exported_files:
                    files_str = "\n".join(exported_files)
                    self.log_message.emit(f"Plots exported to: {dir_path}")
                    QMessageBox.information(
                        self.main_window,
                        "Export Complete",
                        f"Plots exported successfully:\n{files_str}",
                    )
                else:
                    QMessageBox.warning(
                        self.main_window, "No Plots", "No plots available to export."
                    )
            except Exception as e:
                error_msg = f"Failed to export plots: {str(e)}"
                self.log_message.emit(error_msg)
                QMessageBox.critical(self.main_window, "Export Error", error_msg)

    def generate_code(self):
        """Generate standalone Python code for the simulation."""
        try:
            if not self.code_generator:
                QMessageBox.warning(
                    self.main_window, "Code Generator", "Code generator not available."
                )
                return

            # Collect current parameters
            params = self._collect_simulation_parameters()

            # Generate code
            code = self.code_generator.generate_simulation_code(params)

            # Save to file
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Generated Code",
                f"brian2_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
                "Python Files (*.py)",
            )

            if file_path:
                with open(file_path, "w") as f:
                    f.write(code)

                self.log_message.emit(f"Code generated: {file_path}")
                QMessageBox.information(
                    self.main_window, "Code Generated", f"Simulation code saved to:\n{file_path}"
                )

        except Exception as e:
            error_msg = f"Failed to generate code: {str(e)}"
            self.log_message.emit(error_msg)
            QMessageBox.critical(self.main_window, "Code Generation Error", error_msg)

    def on_progress_updated(self, progress, message):
        """Handle progress updates from simulation engine."""
        self.progress_updated.emit(progress, message)

    def on_simulation_completed(self, success, data):
        """Handle simulation completion."""
        self._cleanup_simulation()

        if success and data:
            self.simulation_data = data
            self.log_message.emit("Simulation completed successfully!")

            # Auto-plot if enabled
            if self.main_window.auto_plot_checkbox.isChecked() and self.results_manager:
                self.results_manager.update_plots(data)

            # Show statistics if enabled
            if self.main_window.show_statistics_checkbox.isChecked() and self.results_manager:
                self.results_manager.update_statistics(data)

        else:
            self.log_message.emit("Simulation completed with errors.")

        self.simulation_finished.emit(success)

    def on_simulation_error(self, error_message):
        """Handle simulation errors."""
        self._cleanup_simulation()
        self.log_message.emit(f"Simulation error: {error_message}")
        QMessageBox.critical(
            self.main_window, "Simulation Error", f"Simulation failed:\n{error_message}"
        )
        self.simulation_finished.emit(False)

    def update_progress_display(self):
        """Update progress display with timing information."""
        if not self.is_running or not self.start_time:
            return

        elapsed = time.time() - self.start_time
        elapsed_str = str(timedelta(seconds=int(elapsed)))

        # Update elapsed time
        self.main_window.elapsed_time_label.setText(elapsed_str)

        # Estimate remaining time based on progress
        current_progress = self.main_window.simulation_progress_bar.value()
        if current_progress > 0:
            total_estimated = elapsed * 100 / current_progress
            remaining = total_estimated - elapsed
            if remaining > 0:
                remaining_str = str(timedelta(seconds=int(remaining)))
                self.main_window.remaining_time_label.setText(remaining_str)

    def _validate_configuration(self):
        """Validate current configuration before starting simulation."""
        # Use existing config manager validation
        if hasattr(self.main_window, "config_manager"):
            try:
                self.main_window.config_manager.validate_all_parameters()
                return True
            except ValueError as e:
                error_msg = f"Configuration validation failed: {str(e)}"
                self.log_message.emit(error_msg)
                QMessageBox.critical(self.main_window, "Configuration Error", error_msg)
                return False
        return True

    def _collect_simulation_parameters(self):
        """Collect all simulation parameters from UI managers."""
        params = {}

        # Get parameters from each manager
        if hasattr(self.main_window, "sim_params_manager"):
            params["simulation"] = self.main_window.sim_params_manager.get_sim_params()

        if hasattr(self.main_window, "neuron_models_manager"):
            params["neuron_model"] = self.main_window.neuron_models_manager.get_neuron_model()

        if hasattr(self.main_window, "noise_manager"):
            params["noise"] = self.main_window.noise_manager.get_config()

        if hasattr(self.main_window, "network_manager"):
            params["network"] = (
                self.main_window.network_manager.get_config()
            )

        if hasattr(self.main_window, "advanced_network_manager"):
            params["advanced_network"] = (
                self.main_window.advanced_network_manager.get_config()
            )

        if hasattr(self.main_window, "input_patterns_manager"):
            params["input_patterns"] = self.main_window.input_patterns_manager.get_parameters()

        # Add gap junctions parameters
        # Add gap junctions parameters
        if hasattr(self.main_window, "gap_junctions_manager"):
            params["gap_junctions"] = self.main_window.gap_junctions_manager.get_parameters()

        # Add synaptic receptors parameters
        if hasattr(self.main_window, "synaptic_receptors_manager"):
            params["synaptic_receptors"] = (
                self.main_window.synaptic_receptors_manager.get_synaptic_receptors_config()
            )
        else:
            params["synaptic_receptors"] = {"enabled": False}

        # Add short-term plasticity parameters
        if hasattr(self.main_window, "short_term_plasticity_manager"):
            params["short_term_plasticity"] = (
                self.main_window.short_term_plasticity_manager.get_parameters()
            )
        else:
            params["short_term_plasticity"] = {"enabled": False}

        # Add calcium dynamics parameters
        if hasattr(self.main_window, "calcium_dynamics_manager"):
            params["calcium_dynamics"] = self.main_window.calcium_dynamics_manager.get_parameters()
        else:
            params["calcium_dynamics"] = {"enabled": False}

        # Add homeostatic plasticity parameters
        if hasattr(self.main_window, "homeostatic_plasticity_manager"):
            params["homeostatic_plasticity"] = (
                self.main_window.homeostatic_plasticity_manager.get_parameters()
            )
        else:
            params["homeostatic_plasticity"] = {"enabled": False}

        # Add neuromodulation parameters
        if hasattr(self.main_window, "neuromodulation_manager"):
            params["neuromodulation"] = self.main_window.neuromodulation_manager.get_parameters()
        else:
            params["neuromodulation"] = {"enabled": False}

        # Add multi-compartment parameters
        if hasattr(self.main_window, "multicompartment_manager"):
            params["multicompartment"] = self.main_window.multicompartment_manager.get_parameters()

        else:
            params["multicompartment"] = {"enabled": False}
            
        # Add monitors parameters
        if hasattr(self.main_window, "monitors_manager"):
            params["monitors"] = self.main_window.monitors_manager.get_params_for_save()
        else:
            params["monitors"] = {}

        return params

    def _format_params_summary(self, params):
        """Create a brief summary of simulation parameters."""
        summary_parts = []

        if "simulation" in params:
            sim = params["simulation"]
            summary_parts.append(f"{sim.get('sim_time', 0)}ms duration")
            summary_parts.append(f"{sim.get('num_neurons', 1)} neurons")

        if "neuron_model" in params:
            model = params["neuron_model"]
            summary_parts.append(f"{model.get('model_key', 'unknown')} model")

        return ", ".join(summary_parts) if summary_parts else "default parameters"

    def _update_ui_for_running_state(self, running):
        """Update UI elements for running/stopped state."""
        self.main_window.run_simulation_button.setEnabled(not running)
        self.main_window.stop_simulation_button.setEnabled(running)

        if running:
            self.main_window.simulation_status_label.setText("Running simulation...")
        else:
            self.main_window.simulation_status_label.setText("Ready to simulate")

    def _cleanup_simulation(self):
        """Clean up simulation state."""
        self.is_running = False
        self.progress_timer.stop()
        self._update_ui_for_running_state(False)
        self.main_window.remaining_time_label.setText("--:--")

    def _export_to_json(self, file_path):
        """Export simulation data to JSON format."""
        with open(file_path, "w") as f:
            json.dump(self.simulation_data, f, indent=2, default=str)

    def _export_to_csv(self, file_path):
        """Export simulation data to CSV format (multi-file)."""
        base_path, _ = os.path.splitext(file_path)
        data = self.simulation_data
        
        if "raw_data" not in data:
            self.log_message.emit("No raw data found to export.")
            return

        for key, info in data["raw_data"].items():
            try:
                # Sanitized filename
                safe_key = "".join([c if c.isalnum() else "_" for c in key])
                curr_path = f"{base_path}_{safe_key}.csv"
                
                if info.get("type") == "spikes":
                     # Export Spikes
                     with open(curr_path, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(["Neuron Index", "Spike Time (ms)"])
                        rows = zip(info.get("i", []), info.get("t", []))
                        writer.writerows(rows)
                        
                elif info.get("type") == "trace":
                     # Export Trace
                     with open(curr_path, 'w', newline='') as f:
                        writer = csv.writer(f)
                        t_arr = info.get("t")
                        if t_arr is None: continue
                        
                        values = info.get("values")
                        indices = info.get("indices", [])
                        
                        # Header
                        labels = [f"Neuron_{idx}" for idx in indices]
                        header = ["Time (ms)"] + labels
                        writer.writerow(header)
                        
                        # Rows
                        num_time = len(t_arr)
                        num_traces = len(values)
                        
                        for i in range(num_time):
                             row = [t_arr[i]]
                             for tr in range(num_traces):
                                 row.append(values[tr][i])
                             writer.writerow(row)
                             
            except Exception as e:
                 self.log_message.emit(f"Error exporting {key}: {str(e)}")

        self.log_message.emit(f"Parameters and data structure also saved to {file_path} (JSON)")
        self._export_to_json(file_path)

    def _simulate_progress_for_testing(self):
        """Simulate progress updates for testing without Brian2."""
        self.test_progress = 0
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self._update_test_progress)
        self.test_timer.start(100)  # Update every 100ms

    def _update_test_progress(self):
        """Update test progress simulation."""
        self.test_progress += 2
        self.progress_updated.emit(self.test_progress, f"Processing step {self.test_progress}%")

        if self.test_progress >= 100:
            self.test_timer.stop()
            # Simulate completion with dummy data
            dummy_data = {
                "raw_data": {},
                "parameters": self._collect_simulation_parameters(),
                "timestamp": datetime.now().isoformat(),
            }
            self.on_simulation_completed(True, dummy_data)
