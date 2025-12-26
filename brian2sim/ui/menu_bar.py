"""
Menu bar functionality for Brian2Sim GUI.
Provides main menu organization and actions.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class MenuBarManager(QObject):
    """Manages the main menu bar and its actions."""

    # Signals for menu actions
    new_simulation_requested = pyqtSignal()
    validation_requested = pyqtSignal()
    config_export_requested = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def setup_menu_bar(self):
        """Setup the main menu bar."""
        menubar = self.main_window.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Simulation", self.new_simulation)
        file_menu.addAction("Open Configuration", self.main_window.config_manager.load_config)
        file_menu.addAction("Save Configuration", self.main_window.config_manager.save_config)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.main_window.close)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Validate Parameters", self.show_validation_dialog)
        tools_menu.addAction("Export Configuration", self.export_config)
        tools_menu.addAction("Generate Code", self.generate_code)
        tools_menu.addSeparator()
        tools_menu.addAction("Reset to Defaults", self.reset_to_defaults)

        # View menu
        view_menu = menubar.addMenu("View")

        # User Level submenu
        user_level_menu = view_menu.addMenu("User Level")
        user_level_menu.addAction(
            "Beginner (Core + Simulation)", lambda: self.set_user_level("beginner")
        )
        user_level_menu.addAction(
            "Intermediate (+ Network + Synapses)", lambda: self.set_user_level("intermediate")
        )
        user_level_menu.addAction(
            "Advanced (All Features)", lambda: self.set_user_level("advanced")
        )

        view_menu.addSeparator()

        # Individual tab visibility controls
        # Note: Core and Simulation tabs are always visible (essential)
        view_menu.addAction("Core Tab (Always Visible)", lambda: self.show_tab_info("core"))
        view_menu.addAction(
            "Simulation Tab (Always Visible)", lambda: self.show_tab_info("simulation")
        )
        view_menu.addSeparator()
        view_menu.addAction("Toggle Network Tab", lambda: self.toggle_tab_visibility("network"))
        view_menu.addAction("Toggle Synapses Tab", lambda: self.toggle_tab_visibility("synapses"))
        view_menu.addAction(
            "Toggle Plasticity Tab", lambda: self.toggle_tab_visibility("plasticity")
        )
        view_menu.addAction(
            "Toggle Neuromodulation Tab", lambda: self.toggle_tab_visibility("neuromodulation")
        )
        view_menu.addAction(
            "Toggle Multi-Compartment Tab", lambda: self.toggle_tab_visibility("multicompartment")
        )

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("User Guide", self.show_user_guide)
        help_menu.addAction("Parameter Reference", self.show_parameter_reference)
        help_menu.addAction("Keyboard Shortcuts", self.show_shortcuts)
        help_menu.addSeparator()
        help_menu.addAction("About Brian2", self.show_about_brian2)
        help_menu.addAction("About", self.show_about)

    def new_simulation(self):
        """Create a new simulation with default parameters."""
        reply = QMessageBox.question(
            self.main_window,
            "New Simulation",
            "Are you sure you want to reset all parameters to defaults?\n\n"
            "This will clear all current settings and cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Reset all manager parameters to defaults
                self.main_window.neuron_models_manager.reset_to_defaults()
                self.main_window.sim_params_manager.reset_to_defaults()
                self.main_window.noise_options_manager.reset_to_defaults()
                if hasattr(self.main_window, "input_patterns_manager"):
                    self.main_window.input_patterns_manager.reset_to_defaults()
                self.main_window.network_options_manager.reset_to_defaults()
                self.main_window.advanced_network_manager.reset_to_defaults()

                # Reset additional managers if they exist
                for manager_name in [
                    "gap_junctions_manager",
                    "synaptic_receptors_manager",
                    "calcium_dynamics_manager",
                    "short_term_plasticity_manager",
                    "homeostatic_plasticity_manager",
                    "neuromodulation_manager",
                    "multicompartment_manager",
                ]:
                    if hasattr(self.main_window, manager_name):
                        manager = getattr(self.main_window, manager_name)
                        if hasattr(manager, "reset_to_defaults"):
                            manager.reset_to_defaults()

                QMessageBox.information(
                    self.main_window,
                    "New Simulation",
                    "All parameters have been reset to defaults.",
                )
                self.new_simulation_requested.emit()

            except Exception as e:
                QMessageBox.warning(
                    self.main_window, "Reset Error", f"Error resetting parameters: {str(e)}"
                )

    def show_validation_dialog(self):
        """Show a comprehensive validation results dialog."""
        # Validate and collect errors
        self.main_window.validation_manager.validate_current_parameters()
        validation_results = self.main_window.validation_manager.current_errors

        if not validation_results:
            QMessageBox.information(
                self.main_window,
                "Validation Results",
                "All parameters are valid! ✓\n\nYour configuration is ready for simulation.",
            )
            return

        # Create detailed validation dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Parameter Validation Results")
        dialog.setModal(True)
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)

        # Validation results display
        results_widget = QTextEdit()
        results_widget.setReadOnly(True)

        # Group results by severity
        errors = [r for r in validation_results if r.severity == "error"]
        warnings = [r for r in validation_results if r.severity == "warning"]
        infos = [r for r in validation_results if r.severity == "info"]

        results_text = ""

        # Summary
        results_text += f"VALIDATION SUMMARY\n"
        results_text += f"{'='*50}\n"
        results_text += f"Total Issues: {len(validation_results)}\n"
        results_text += (
            f"Errors: {len(errors)} | Warnings: {len(warnings)} | Info: {len(infos)}\n\n"
        )

        if errors:
            results_text += "🔴 ERRORS (Must be fixed before simulation):\n"
            results_text += f"{'-'*50}\n"
            for result in errors:
                results_text += f"• {result.parameter}: {result.message}\n"
            results_text += "\n"

        if warnings:
            results_text += "🟡 WARNINGS (Recommended to review):\n"
            results_text += f"{'-'*50}\n"
            for result in warnings:
                results_text += f"• {result.parameter}: {result.message}\n"
            results_text += "\n"

        if infos:
            results_text += "ℹ️ INFORMATION (Suggestions for optimization):\n"
            results_text += f"{'-'*50}\n"
            for result in infos:
                results_text += f"• {result.parameter}: {result.message}\n"

        results_widget.setPlainText(results_text)
        layout.addWidget(results_widget)

        # Buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        export_button = QPushButton("Export Report")
        export_button.clicked.connect(lambda: self.export_validation_report(validation_results))

        button_layout.addWidget(export_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        dialog.exec()
        self.validation_requested.emit()

    def export_validation_report(self, validation_results):
        """Export validation results to a file."""
        filename, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Export Validation Report",
            "brian2sim_validation_report.txt",
            "Text Files (*.txt);;All Files (*)",
        )

        if filename:
            try:
                with open(filename, "w") as f:
                    f.write("Brian2Sim Parameter Validation Report\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Generated on: {QFileDialog().directory().dirName()}\n\n")

                    errors = [r for r in validation_results if r.severity == "error"]
                    warnings = [r for r in validation_results if r.severity == "warning"]
                    infos = [r for r in validation_results if r.severity == "info"]

                    f.write(f"SUMMARY:\n")
                    f.write(f"Total Issues: {len(validation_results)}\n")
                    f.write(
                        f"Errors: {len(errors)} | Warnings: {len(warnings)} | Info: {len(infos)}\n\n"
                    )

                    if errors:
                        f.write("ERRORS (Must be fixed):\n")
                        f.write("-" * 30 + "\n")
                        for result in errors:
                            f.write(f"• {result.parameter}: {result.message}\n")
                        f.write("\n")

                    if warnings:
                        f.write("WARNINGS (Recommended to review):\n")
                        f.write("-" * 30 + "\n")
                        for result in warnings:
                            f.write(f"• {result.parameter}: {result.message}\n")
                        f.write("\n")

                    if infos:
                        f.write("INFORMATION (Suggestions):\n")
                        f.write("-" * 30 + "\n")
                        for result in infos:
                            f.write(f"• {result.parameter}: {result.message}\n")

                QMessageBox.information(
                    self.main_window,
                    "Export Complete",
                    f"Validation report exported to:\n{filename}",
                )
            except Exception as e:
                QMessageBox.warning(
                    self.main_window, "Export Error", f"Failed to export report:\n{str(e)}"
                )

    def export_config(self):
        """Export current configuration to a file."""
        filename, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Export Configuration",
            "brian2sim_config.json",
            "JSON Files (*.json);;All Files (*)",
        )

        if filename:
            try:
                self.main_window.config_manager.save_config_to_file(filename)
                QMessageBox.information(
                    self.main_window, "Export Complete", f"Configuration exported to:\n{filename}"
                )
                self.config_export_requested.emit()
            except Exception as e:
                QMessageBox.warning(
                    self.main_window, "Export Error", f"Failed to export configuration:\n{str(e)}"
                )

    def generate_code(self):
        """Generate Brian2 simulation code."""
        try:
            # Generate code using the code generator
            if hasattr(self.main_window, "code_generator"):
                code = self.main_window.code_generator.generate_code(self.main_window)

                # Show code in a dialog
                dialog = QDialog(self.main_window)
                dialog.setWindowTitle("Generated Brian2 Code")
                dialog.setModal(True)
                dialog.resize(800, 600)

                layout = QVBoxLayout(dialog)

                code_widget = QTextEdit()
                code_widget.setPlainText(code)
                code_widget.setFont(self.main_window.font())
                layout.addWidget(code_widget)

                # Buttons
                button_layout = QHBoxLayout()
                save_button = QPushButton("Save Code")
                save_button.clicked.connect(lambda: self.save_generated_code(code))
                copy_button = QPushButton("Copy to Clipboard")
                copy_button.clicked.connect(lambda: self.copy_to_clipboard(code))
                close_button = QPushButton("Close")
                close_button.clicked.connect(dialog.accept)

                button_layout.addWidget(save_button)
                button_layout.addWidget(copy_button)
                button_layout.addStretch()
                button_layout.addWidget(close_button)
                layout.addLayout(button_layout)

                dialog.exec()
            else:
                QMessageBox.information(
                    self.main_window, "Code Generation", "Code generator not available."
                )
        except Exception as e:
            QMessageBox.warning(
                self.main_window, "Code Generation Error", f"Failed to generate code:\n{str(e)}"
            )

    def save_generated_code(self, code):
        """Save generated code to a file."""
        filename, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save Generated Code",
            "brian2_simulation.py",
            "Python Files (*.py);;All Files (*)",
        )

        if filename:
            try:
                with open(filename, "w") as f:
                    f.write(code)
                QMessageBox.information(
                    self.main_window, "Save Complete", f"Code saved to:\n{filename}"
                )
            except Exception as e:
                QMessageBox.warning(
                    self.main_window, "Save Error", f"Failed to save code:\n{str(e)}"
                )

    def copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        from PyQt6.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self.main_window, "Copied", "Code copied to clipboard!")

    def reset_to_defaults(self):
        """Reset all parameters to defaults."""
        self.new_simulation()  # Reuse the new simulation logic

    def show_user_guide(self):
        """Show user guide dialog."""
        user_guide_text = """
        <h2>Brian2Sim User Guide</h2>
       
        <h3>Getting Started</h3>
        <p>1. <b>Main Tab:</b> Configure basic simulation parameters</p>
        <p>2. <b>Network Architecture:</b> Set up network connectivity</p>
        <p>3. <b>Synaptic Properties:</b> Configure synaptic transmission</p>
        <p>4. <b>Plasticity & Dynamics:</b> Set up learning mechanisms</p>
       
        <h3>Parameter Dependencies</h3>
        <p>• NMDA receptors automatically enable calcium dynamics</p>
        <p>• Calcium dynamics enable plasticity mechanisms</p>
        <p>• Some parameters are interdependent - validation will guide you</p>
       
        <h3>Tips</h3>
        <p>• Use Tools → Validate Parameters to check your configuration</p>
        <p>• Export configurations to save your work</p>
        <p>• Generate code to see the underlying Brian2 implementation</p>
        """
        QMessageBox.about(self.main_window, "User Guide", user_guide_text)

    def show_parameter_reference(self):
        """Show parameter reference dialog."""
        param_ref_text = """
        <h2>Parameter Reference</h2>
       
        <h3>Neuron Models</h3>
        <p><b>LIF:</b> Leaky Integrate-and-Fire</p>
        <p><b>AdEx:</b> Adaptive Exponential</p>
        <p><b>Izhikevich:</b> Two-variable model</p>
        <p><b>Hodgkin-Huxley:</b> Detailed conductance-based</p>
       
        <h3>Typical Values</h3>
        <p><b>Membrane potential:</b> -70 to -50 mV</p>
        <p><b>Time constants:</b> 1-100 ms</p>
        <p><b>Conductances:</b> 0.1-10 nS</p>
        <p><b>Connection probability:</b> 0.01-0.5</p>
       
        <h3>Validation Rules</h3>
        <p>• Voltages must be between -100 and +50 mV</p>
        <p>• Time constants must be positive</p>
        <p>• Probabilities must be between 0 and 1</p>
        """
        QMessageBox.about(self.main_window, "Parameter Reference", param_ref_text)

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_text = """
        <h2>Keyboard Shortcuts</h2>
       
        <h3>File Operations</h3>
        <p><b>Ctrl+N:</b> New Simulation</p>
        <p><b>Ctrl+O:</b> Open Configuration</p>
        <p><b>Ctrl+S:</b> Save Configuration</p>
        <p><b>Ctrl+Q:</b> Quit Application</p>
       
        <h3>Tools</h3>
        <p><b>F5:</b> Validate Parameters</p>
        <p><b>Ctrl+G:</b> Generate Code</p>
        <p><b>Ctrl+E:</b> Export Configuration</p>
       
        <h3>Navigation</h3>
        <p><b>Ctrl+1-6:</b> Switch between tabs</p>
        <p><b>F1:</b> Show Help</p>
        """
        QMessageBox.about(self.main_window, "Keyboard Shortcuts", shortcuts_text)

    def show_about_brian2(self):
        """Show information about Brian2."""
        about_brian2_text = """
        <h2>About Brian2</h2>
        <p>Brian2 is a clock-driven simulator for spiking neural networks.</p>
       
        <p><b>Key Features:</b></p>
        <ul>
        <li>Flexible neuron and synapse models</li>
        <li>Efficient simulation engine</li>
        <li>Support for plasticity and learning</li>
        <li>Extensive documentation and examples</li>
        </ul>
       
        <p><b>Learn More:</b></p>
        <p>Website: <a href="https://brian2.readthedocs.io">brian2.readthedocs.io</a></p>
        <p>GitHub: <a href="https://github.com/brian-team/brian2">github.com/brian-team/brian2</a></p>
        """
        QMessageBox.about(self.main_window, "About Brian2", about_brian2_text)

    def show_about(self):
        """Show the About dialog."""
        about_text = """
        <h2>Brian2Sim GUI</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p>A comprehensive graphical interface for Brian2 neural simulations.</p>
       
        <p><b>Key Features:</b></p>
        <ul>
        <li>Multiple neuron models (LIF, AdEx, Izhikevich, HH)</li>
        <li>Flexible network connectivity options</li>
        <li>Synaptic plasticity and dynamics</li>
        <li>Neuromodulation and calcium dynamics</li>
        <li>Real-time parameter validation</li>
        <li>Cross-tab dependency management</li>
        <li>Code generation and export</li>
        </ul>
       
        <p><b>Built with:</b> PyQt6 and Brian2</p>
        <p><b>License:</b> Open Source</p>
       
        <p>Designed for neuroscientists, researchers, and students.</p>
        """
        QMessageBox.about(self.main_window, "About Brian2Sim", about_text)

    def set_user_level(self, level):
        """Set the user level and update tab visibility."""
        if hasattr(self.main_window, "set_user_level"):
            self.main_window.set_user_level(level)
            QMessageBox.information(
                self.main_window,
                "User Level Changed",
                f"Interface switched to {level.title()} level.\n\n"
                f"Tabs have been updated to show features appropriate for your experience level.",
            )

    def toggle_tab_visibility(self, tab_key):
        """Toggle the visibility of a specific tab."""
        # Core and Simulation tabs should never be hidden - they're essential
        if tab_key in ["core", "simulation"]:
            QMessageBox.information(
                self.main_window,
                "Cannot Hide Essential Tab",
                f"{tab_key.title()} tab cannot be hidden as it contains essential functionality for neural simulations.",
            )
            return

        if hasattr(self.main_window, "tab_info") and tab_key in self.main_window.tab_info:
            tab_data = self.main_window.tab_info[tab_key]
            current_index = self.main_window.tabs.indexOf(tab_data["widget"])

            if current_index != -1:
                # Tab is visible, hide it
                self.main_window.tabs.removeTab(current_index)
                tab_data["visible"] = False
                status = "hidden"
            else:
                # Tab is hidden, show it
                self.main_window._restore_tab(tab_key, tab_data)
                tab_data["visible"] = True
                status = "shown"

            tab_name = tab_key.replace("_", " ").title()
            QMessageBox.information(
                self.main_window, "Tab Visibility Changed", f"{tab_name} tab has been {status}."
            )

    def show_tab_info(self, tab_key):
        """Show information about essential tabs that cannot be hidden."""
        if tab_key == "core":
            QMessageBox.information(
                self.main_window,
                "Essential Tab - Core",
                "The Core tab contains fundamental neuron parameters and cannot be hidden.\n\n"
                "This tab includes:\n"
                "• Basic neuron model selection\n"
                "• Essential neuron parameters\n"
                "• Core simulation settings\n\n"
                "These settings are required for any neural simulation.",
            )
        elif tab_key == "simulation":
            QMessageBox.information(
                self.main_window,
                "Essential Tab - Simulation",
                "The Simulation tab contains simulation controls and results display.\n\n"
                "This tab includes:\n"
                "• Simulation run controls\n"
                "• Real-time monitoring\n"
                "• Results visualization\n"
                "• Data export options\n\n"
                "Without this tab, you cannot run simulations or view results.",
            )
