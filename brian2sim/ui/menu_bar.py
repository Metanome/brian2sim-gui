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
    QStyle,
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
        style = self.main_window.style()

        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = file_menu.addAction("New", self.new_simulation)
        new_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        
        open_action = file_menu.addAction("Open...", self.main_window.load_configuration)
        open_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        
        save_action = file_menu.addAction("Save...", self.main_window.save_configuration)
        save_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit", self.main_window.close)
        exit_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))

        # Simulation menu
        simulation_menu = menubar.addMenu("Simulation")
        
        run_action = simulation_menu.addAction("Run", self.run_simulation)
        run_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        val_action = simulation_menu.addAction("Validate Parameters", self.show_validation_dialog)
        val_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        
        gen_action = simulation_menu.addAction("Generate Code", self.generate_code)
        gen_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)) # Fallback icon

        # View menu - checkable items for tab visibility
        view_menu = menubar.addMenu("View")
        
        # Store tab actions for updating checked state
        self.tab_actions = {}
        
        # Define tabs with their display names (Core and Simulation always visible)
        tab_items = [
            ("core", "Core", True),  # (key, name, always_visible)
            ("simulation", "Simulation", True),
            ("network", "Network", False),
            ("synapses", "Synapses", False),
            ("plasticity", "Plasticity", False),
            ("neuromodulation", "Neuromodulation", False),
            ("multicompartment", "Multi-Compartment", False),
        ]
        
        for tab_key, tab_name, always_visible in tab_items:
            action = view_menu.addAction(tab_name)
            action.setCheckable(True)
            
            if always_visible:
                # Core and Simulation are always checked and disabled
                action.setChecked(True)
                action.setEnabled(False)
                action.setToolTip(f"{tab_name} tab is always visible")
            else:
                # Initial state will be synced after tabs are created
                action.setChecked(True)  # Default to checked, sync later
                # Connect toggle action
                action.triggered.connect(
                    lambda checked, key=tab_key: self.toggle_tab_visibility(key, checked)
                )
            
            self.tab_actions[tab_key] = action

        # Help menu
        help_menu = menubar.addMenu("Help")
        
        doc_action = help_menu.addAction("Documentation", self.show_documentation)
        doc_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton))
        
        help_menu.addSeparator()
        
        about_action = help_menu.addAction("About", self.show_about)
        about_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))

    def sync_tab_checkboxes(self):
        """Sync menu checkbox states with actual tab visibility.
        
        Call this after tabs have been created/initialized.
        """
        if not hasattr(self, "tab_actions"):
            return
        if not hasattr(self.main_window, "tab_info"):
            return
            
        for tab_key, action in self.tab_actions.items():
            if tab_key in ["core", "simulation"]:
                # Essential tabs are always visible
                action.setChecked(True)
            elif tab_key in self.main_window.tab_info:
                # Sync with actual tab visibility
                tab_data = self.main_window.tab_info[tab_key]
                is_visible = tab_data.get("visible", True)
                action.setChecked(is_visible)

    def run_simulation(self):
        """Start the simulation."""
        if hasattr(self.main_window, "simulation_manager"):
            self.main_window.simulation_manager.start_simulation()
        else:
            QMessageBox.warning(
                self.main_window,
                "Simulation Error",
                "Simulation manager not available."
            )

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
                # Reset all manager parameters to defaults (check if method exists)
                core_managers = [
                    "neuron_models_manager",
                    "sim_params_manager",
                    "noise_manager",
                    "input_patterns_manager",
                    "network_manager",
                    "advanced_network_manager",
                ]
                for manager_name in core_managers:
                    if hasattr(self.main_window, manager_name):
                        manager = getattr(self.main_window, manager_name)
                        if hasattr(manager, "reset_to_defaults"):
                            manager.reset_to_defaults()

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
        if hasattr(self.main_window, "simulation_manager"):
            self.main_window.simulation_manager.generate_code()
        else:
            QMessageBox.warning(
                self.main_window, "Error", "Simulation manager not available."
            )


    def reset_to_defaults(self):
        """Reset all parameters to defaults."""
        self.new_simulation()  # Reuse the new simulation logic

    def show_documentation(self):
        """Show the documentation dialog."""
        from brian2sim.ui.help_dialog import HelpDialog
        dialog = HelpDialog(self.main_window)
        dialog.exec()

    def show_about(self):
        """Show the About dialog."""
        from brian2sim.ui.help_dialog import HelpDialog
        dialog = HelpDialog(self.main_window, start_tab_index=1)
        dialog.exec()



    def toggle_tab_visibility(self, tab_key, checked):
        """Set the visibility of a specific tab based on checked state."""
        # Core and Simulation tabs should never be hidden - they're essential
        if tab_key in ["core", "simulation"]:
            return

        if hasattr(self.main_window, "tab_info") and tab_key in self.main_window.tab_info:
            tab_data = self.main_window.tab_info[tab_key]
            current_index = self.main_window.tabs.indexOf(tab_data["widget"])

            if checked and current_index == -1:
                # Tab should be visible but isn't - show it
                self.main_window._restore_tab(tab_key, tab_data)
                tab_data["visible"] = True
            elif not checked and current_index != -1:
                # Tab should be hidden but is visible - hide it
                self.main_window.tabs.removeTab(current_index)
                tab_data["visible"] = False

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
