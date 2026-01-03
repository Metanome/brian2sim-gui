# cross_tab_dependencies.py
# Cross-tab parameter dependencies for neuroscientifically accurate UI behavior

from PyQt6.QtCore import QObject, pyqtSignal


class CrossTabDependencyManager(QObject):
    """Manages parameter dependencies across different tabs for neuroscientific accuracy."""

    dependency_changed = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.dependency_rules = self._define_dependency_rules()

    def _define_dependency_rules(self):
        """Define cross-tab dependency rules."""
        return {
            # NMDA receptors enable calcium dynamics options
            "nmda_calcium_coupling": {
                "source_tab": "synaptic_receptors",
                "source_param": "nmda_enabled",
                "target_tab": "calcium_dynamics",
                "target_params": ["ca_sources"],
                "rule": "enable_nmda_sources",
            },
            # Calcium dynamics enable calcium-dependent plasticity
            "calcium_plasticity_coupling": {
                "source_tab": "calcium_dynamics",
                "source_param": "enabled",
                "target_tab": "homeostatic_plasticity",
                "target_params": ["ca_dependent_scaling", "ca_threshold_plasticity"],
                "rule": "enable_ca_dependent_plasticity",
            },
            # Synaptic receptors affect short-term plasticity options
            "receptor_stp_coupling": {
                "source_tab": "synaptic_receptors",
                "source_param": "enabled",
                "target_tab": "short_term_plasticity",
                "target_params": ["receptor_specific_dynamics"],
                "rule": "enable_receptor_specific_stp",
            },
            # Gap junctions affect network synchrony parameters
            "gap_junction_sync_coupling": {
                "source_tab": "gap_junctions",
                "source_param": "enabled",
                "target_tab": "network",
                "target_params": ["synchrony_analysis", "electrical_coupling_strength"],
                "rule": "enable_electrical_coupling_analysis",
            },
        }

    def connect_dependencies(self):
        """Connect cross-tab dependency signals."""
        # Connect to parameter change signals from all relevant managers
        managers = [
            "synaptic_receptors_manager",
            "calcium_dynamics_manager",
            "homeostatic_plasticity_manager",
            "short_term_plasticity_manager",
            "gap_junctions_manager",
            "network_manager",
        ]

        for manager_name in managers:
            if hasattr(self.main_window, manager_name):
                manager = getattr(self.main_window, manager_name)
                if hasattr(manager, "param_changed"):
                    manager.param_changed.connect(self.update_dependencies)

    def update_dependencies(self):
        """Update all cross-tab dependencies when any parameter changes."""
        for rule_name, rule in self.dependency_rules.items():
            self._apply_dependency_rule(rule_name, rule)

    def _apply_dependency_rule(self, rule_name, rule):
        """Apply a specific dependency rule."""
        try:
            # Get source parameter value
            source_value = self._get_parameter_value(rule["source_tab"], rule["source_param"])

            # Apply rule-specific logic
            if rule["rule"] == "enable_nmda_sources":
                self._handle_nmda_calcium_coupling(source_value, rule)
            elif rule["rule"] == "enable_ca_dependent_plasticity":
                self._handle_calcium_plasticity_coupling(source_value, rule)
            elif rule["rule"] == "enable_receptor_specific_stp":
                self._handle_receptor_stp_coupling(source_value, rule)
            elif rule["rule"] == "enable_electrical_coupling_analysis":
                self._handle_gap_junction_sync_coupling(source_value, rule)

        except Exception as e:
            print(f"Error applying dependency rule {rule_name}: {e}")

    def _get_parameter_value(self, tab_name, param_name):
        """Get parameter value from a specific tab."""
        form_generator_name = f"{tab_name}_form_generator"
        if hasattr(self.main_window, form_generator_name):
            form_generator = getattr(self.main_window, form_generator_name)
            param_widgets = form_generator.get_param_widgets()
            if param_name in param_widgets:
                widget = param_widgets[param_name]
                if hasattr(widget, "isChecked"):
                    return widget.isChecked()
                elif hasattr(widget, "value"):
                    return widget.value()
                elif hasattr(widget, "currentText"):
                    return widget.currentText()
        return None

    def _set_parameter_enabled(self, tab_name, param_name, enabled):
        """Enable/disable a parameter in a specific tab."""
        form_generator_name = f"{tab_name}_form_generator"
        if hasattr(self.main_window, form_generator_name):
            form_generator = getattr(self.main_window, form_generator_name)
            param_widgets = form_generator.get_param_widgets()
            if param_name in param_widgets:
                param_widgets[param_name].setEnabled(enabled)

    def _handle_nmda_calcium_coupling(self, nmda_enabled, rule):
        """Handle NMDA → Calcium dynamics coupling."""
        # If NMDA is enabled, enable NMDA-related calcium source options
        ca_source_params = ["ca_sources", "nmda_ca_fraction", "nmda_ca_permeability"]
        for param in ca_source_params:
            self._set_parameter_enabled(rule["target_tab"], param, nmda_enabled)

    def _handle_calcium_plasticity_coupling(self, ca_enabled, rule):
        """Handle Calcium dynamics → Homeostatic plasticity coupling."""
        # If calcium dynamics enabled, enable calcium-dependent plasticity options
        for param in rule["target_params"]:
            self._set_parameter_enabled(rule["target_tab"], param, ca_enabled)

    def _handle_receptor_stp_coupling(self, receptors_enabled, rule):
        """Handle Synaptic receptors → Short-term plasticity coupling."""
        # If synaptic receptors enabled, enable receptor-specific STP options
        for param in rule["target_params"]:
            self._set_parameter_enabled(rule["target_tab"], param, receptors_enabled)

    def _handle_gap_junction_sync_coupling(self, gap_enabled, rule):
        """Handle Gap junctions → Network synchrony coupling."""
        # If gap junctions enabled, enable electrical coupling analysis options
        for param in rule["target_params"]:
            self._set_parameter_enabled(rule["target_tab"], param, gap_enabled)

    def validate_configuration(self):
        """Validate current configuration for neuroscientific consistency."""
        warnings = []

        # Check NMDA without calcium dynamics
        nmda_enabled = self._get_parameter_value("synaptic_receptors", "nmda_enabled")
        ca_enabled = self._get_parameter_value("calcium_dynamics", "enabled")
        if nmda_enabled and not ca_enabled:
            warnings.append(
                "NMDA receptors are enabled but calcium dynamics are disabled. "
                "NMDA is a major calcium source - consider enabling calcium dynamics."
            )

        # Check homeostatic plasticity without target activity
        hp_enabled = self._get_parameter_value("homeostatic_plasticity", "enabled")
        target_rate = self._get_parameter_value("homeostatic_plasticity", "target_firing_rate")
        if hp_enabled and (target_rate is None or target_rate <= 0):
            warnings.append(
                "Homeostatic plasticity is enabled but target firing rate is not set properly."
            )

        return warnings
