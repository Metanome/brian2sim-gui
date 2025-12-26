"""
Advanced Network Features Manager for Brian2 neural network simulator.
Handles Dale's principle, synaptic delays, STDP, and distance-dependent connectivity.
"""

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QSpinBox

from brian2sim.models.advanced_network_config import (
    ADVANCED_NETWORK_PRESETS,
    DALES_PRINCIPLE_CONFIG,
    DISTANCE_CONNECTIVITY_CONFIG,
    DISTANCE_CONNECTIVITY_PRESETS,
    STDP_CONFIG,
    STDP_PRESETS,
    STDP_TYPE_DEFAULTS,
    SYNAPTIC_DELAYS_CONFIG,
)


class AdvancedNetworkManager(QObject):
    """Manager for advanced neuroscience features in network simulations."""

    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.feature_forms = {}  # Will store UI forms for each feature

    def connect_signals(self):
        """Connect all advanced network parameter change signals."""
        # Connect signals for Dale's Principle
        if (
            hasattr(self.main_window, "dales_principle_forms")
            and self.main_window.dales_principle_forms
        ):
            if "params" in self.main_window.dales_principle_forms:
                for param_key, widget in self.main_window.dales_principle_forms["params"].items():
                    self._connect_widget_signal(widget)

        # Connect signals for Synaptic Delays
        if (
            hasattr(self.main_window, "synaptic_delays_forms")
            and self.main_window.synaptic_delays_forms
        ):
            if "params" in self.main_window.synaptic_delays_forms:
                for param_key, widget in self.main_window.synaptic_delays_forms["params"].items():
                    self._connect_widget_signal(widget)

        # Connect signals for STDP
        if hasattr(self.main_window, "stdp_forms") and self.main_window.stdp_forms:
            if "params" in self.main_window.stdp_forms:
                for param_key, widget in self.main_window.stdp_forms["params"].items():
                    self._connect_widget_signal(widget)

        # Connect signals for Distance Connectivity
        if (
            hasattr(self.main_window, "distance_connectivity_forms")
            and self.main_window.distance_connectivity_forms
        ):
            if "params" in self.main_window.distance_connectivity_forms:
                for param_key, widget in self.main_window.distance_connectivity_forms[
                    "params"
                ].items():
                    self._connect_widget_signal(widget)

        # Connect main feature enable/disable checkboxes
        feature_checkboxes = [
            "dales_principle_checkbox",
            "synaptic_delays_checkbox",
            "stdp_checkbox",
            "distance_connectivity_checkbox",
        ]

        for checkbox_name in feature_checkboxes:
            if hasattr(self.main_window, checkbox_name):
                checkbox = getattr(self.main_window, checkbox_name)
                if checkbox:
                    checkbox.stateChanged.connect(self.on_param_changed)

    def _connect_widget_signal(self, widget):
        """Helper method to connect appropriate signal for a widget."""
        if isinstance(widget, QCheckBox):
            widget.stateChanged.connect(self.on_param_changed)
        elif isinstance(widget, QComboBox):
            widget.currentIndexChanged.connect(self.on_param_changed)
        elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
            widget.valueChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any advanced network parameter changes."""
        self.param_changed.emit()

    def toggle_dales_principle_visibility(self, state):
        """Toggle visibility of Dale's principle parameters."""
        if hasattr(self.main_window, "dales_principle_params_group"):
            self.main_window.dales_principle_params_group.setVisible(
                state == Qt.CheckState.Checked.value
            )

    def toggle_synaptic_delays_visibility(self, state):
        """Toggle visibility of synaptic delays parameters."""
        if hasattr(self.main_window, "synaptic_delays_params_group"):
            self.main_window.synaptic_delays_params_group.setVisible(
                state == Qt.CheckState.Checked.value
            )

    def toggle_stdp_visibility(self, state):
        """Toggle visibility of STDP parameters."""
        if hasattr(self.main_window, "stdp_params_group"):
            self.main_window.stdp_params_group.setVisible(state == Qt.CheckState.Checked.value)

    def toggle_distance_connectivity_visibility(self, state):
        """Toggle visibility of distance-dependent connectivity parameters."""
        if hasattr(self.main_window, "distance_connectivity_params_group"):
            self.main_window.distance_connectivity_params_group.setVisible(
                state == Qt.CheckState.Checked.value
            )

    def update_delay_params_visibility(self, index):
        """Update visibility of delay parameters based on selected delay type."""
        if not hasattr(self.main_window, "synaptic_delays_forms"):
            return

        delay_type_widget = self.main_window.synaptic_delays_forms["params"].get("delay_type")
        if not delay_type_widget:
            return

        # Get actual delay type value from combo box
        delay_type_config = self._get_param_config("synaptic_delays", "delay_type")
        actual_delay_type = self._get_combo_value(delay_type_widget, delay_type_config)

        # Show/hide parameters based on delay type
        params_visibility = {
            "uniform": ["min_delay", "max_delay"],
            "normal": ["mean_delay", "delay_std", "min_delay", "max_delay"],
            "exponential": ["mean_delay", "min_delay", "max_delay"],
            "distance_dependent": ["conduction_velocity", "min_delay"],
        }

        visible_params = params_visibility.get(actual_delay_type, [])

        # Control visibility of both widgets and labels directly
        for param_key in self.main_window.synaptic_delays_forms["params"].keys():
            if param_key != "delay_type" and param_key != "enabled":
                is_visible = param_key in visible_params

                # Hide/show the parameter widget
                if param_key in self.main_window.synaptic_delays_forms["params"]:
                    self.main_window.synaptic_delays_forms["params"][param_key].setVisible(
                        is_visible
                    )
                # Hide/show the parameter label
                if param_key in self.main_window.synaptic_delays_forms["labels"]:
                    self.main_window.synaptic_delays_forms["labels"][param_key].setVisible(
                        is_visible
                    )

    def update_stdp_params_visibility(self, index):
        """Update visibility of STDP parameters based on selected STDP type."""
        if not hasattr(self.main_window, "stdp_forms"):
            return

        stdp_type_widget = self.main_window.stdp_forms["params"].get("stdp_type")
        if not stdp_type_widget:
            return

        # Get actual STDP type value from combo box
        stdp_type_config = self._get_param_config("stdp", "stdp_type")
        actual_stdp_type = self._get_combo_value(stdp_type_widget, stdp_type_config)

        # Update parameter values based on STDP type
        if actual_stdp_type in STDP_TYPE_DEFAULTS:
            type_defaults = STDP_TYPE_DEFAULTS[actual_stdp_type]
            for param_key, default_value in type_defaults.items():
                if param_key in self.main_window.stdp_forms["params"]:
                    widget = self.main_window.stdp_forms["params"][param_key]
                    if hasattr(widget, "setValue"):
                        widget.setValue(default_value)

        # Define which parameters should be visible for each STDP type
        # For now, all STDP types use the same basic parameters
        # This could be extended in the future for different parameter sets
        all_stdp_params = ["tau_pre", "tau_post", "A_plus", "A_minus", "w_min", "w_max"]

        # Show all parameters for now - can be customized per STDP type later
        visible_params = all_stdp_params

        # Control visibility of both widgets and labels directly
        for param_key in self.main_window.stdp_forms["params"].keys():
            if param_key != "stdp_type" and param_key != "enabled":
                is_visible = param_key in visible_params

                # Hide/show the parameter widget
                if param_key in self.main_window.stdp_forms["params"]:
                    self.main_window.stdp_forms["params"][param_key].setVisible(is_visible)

                # Hide/show the parameter label
                if param_key in self.main_window.stdp_forms["labels"]:
                    self.main_window.stdp_forms["labels"][param_key].setVisible(is_visible)

    def update_distance_params_visibility(self, index):
        """Update visibility of distance connectivity parameters based on function type."""
        if not hasattr(self.main_window, "distance_connectivity_forms"):
            return

        function_widget = self.main_window.distance_connectivity_forms["params"].get(
            "connection_function"
        )
        if not function_widget:
            return

        # Get actual function type value from combo box
        function_type_config = self._get_param_config(
            "distance_connectivity", "connection_function"
        )
        actual_function_type = self._get_combo_value(function_widget, function_type_config)

        # Show/hide parameters based on connection function
        params_visibility = {
            "exponential": ["connection_length", "max_distance", "base_probability", "space_scale"],
            "gaussian": ["connection_length", "max_distance", "base_probability", "space_scale"],
            "power_law": ["max_distance", "base_probability", "power_exponent", "space_scale"],
            "step": ["max_distance", "base_probability", "space_scale"],
            "linear": ["max_distance", "base_probability", "space_scale"],
        }

        visible_params = params_visibility.get(actual_function_type, [])

        # Control visibility of both widgets and labels directly
        for param_key in self.main_window.distance_connectivity_forms["params"].keys():
            if param_key not in ["connection_function", "enabled", "spatial_layout"]:
                is_visible = param_key in visible_params

                # Hide/show the parameter widget
                if param_key in self.main_window.distance_connectivity_forms["params"]:
                    self.main_window.distance_connectivity_forms["params"][param_key].setVisible(
                        is_visible
                    )

                # Hide/show the parameter label
                if param_key in self.main_window.distance_connectivity_forms["labels"]:
                    self.main_window.distance_connectivity_forms["labels"][param_key].setVisible(
                        is_visible
                    )

    def get_advanced_network_options(self):
        """Collect all advanced network configuration options from UI elements."""
        options = {}

        # Dale's Principle
        if (
            hasattr(self.main_window, "dales_principle_checkbox")
            and self.main_window.dales_principle_checkbox.isChecked()
        ):
            dales_options = {"enabled": True}
            if (
                hasattr(self.main_window, "dales_principle_forms")
                and self.main_window.dales_principle_forms
            ):
                dales_options.update(
                    self._collect_feature_params(
                        "dales_principle", self.main_window.dales_principle_forms
                    )
                )
            options["dales_principle"] = dales_options
        else:
            options["dales_principle"] = {"enabled": False}

        # Synaptic Delays
        if (
            hasattr(self.main_window, "synaptic_delays_checkbox")
            and self.main_window.synaptic_delays_checkbox.isChecked()
        ):
            delays_options = {"enabled": True}
            if (
                hasattr(self.main_window, "synaptic_delays_forms")
                and self.main_window.synaptic_delays_forms
            ):
                delays_options.update(
                    self._collect_feature_params(
                        "synaptic_delays", self.main_window.synaptic_delays_forms
                    )
                )
            options["synaptic_delays"] = delays_options
        else:
            options["synaptic_delays"] = {"enabled": False}

        # STDP
        if (
            hasattr(self.main_window, "stdp_checkbox")
            and self.main_window.stdp_checkbox.isChecked()
        ):
            stdp_options = {"enabled": True}
            if hasattr(self.main_window, "stdp_forms") and self.main_window.stdp_forms:
                stdp_options.update(
                    self._collect_feature_params("stdp", self.main_window.stdp_forms)
                )
            options["stdp"] = stdp_options
        else:
            options["stdp"] = {"enabled": False}

        # Distance-Dependent Connectivity
        if (
            hasattr(self.main_window, "distance_connectivity_checkbox")
            and self.main_window.distance_connectivity_checkbox.isChecked()
        ):
            distance_options = {"enabled": True}
            if (
                hasattr(self.main_window, "distance_connectivity_forms")
                and self.main_window.distance_connectivity_forms
            ):
                distance_options.update(
                    self._collect_feature_params(
                        "distance_connectivity", self.main_window.distance_connectivity_forms
                    )
                )
            options["distance_connectivity"] = distance_options
        else:
            options["distance_connectivity"] = {"enabled": False}

        return options

    def load_advanced_network_options(self, data):
        """Load advanced network options into UI elements."""
        if not data or not isinstance(data, dict):
            return

        # Load Dale's Principle options
        dales_data = data.get("dales_principle", {})
        if hasattr(self.main_window, "dales_principle_checkbox"):
            self.main_window.dales_principle_checkbox.setChecked(dales_data.get("enabled", False))

        if dales_data.get("enabled", False) and hasattr(self.main_window, "dales_principle_forms"):
            self._load_feature_params(self.main_window.dales_principle_forms, dales_data)

        # Load Synaptic Delays options
        delays_data = data.get("synaptic_delays", {})
        if hasattr(self.main_window, "synaptic_delays_checkbox"):
            self.main_window.synaptic_delays_checkbox.setChecked(delays_data.get("enabled", False))

        if delays_data.get("enabled", False) and hasattr(self.main_window, "synaptic_delays_forms"):
            self._load_feature_params(self.main_window.synaptic_delays_forms, delays_data)

        # Load STDP options
        stdp_data = data.get("stdp", {})
        if hasattr(self.main_window, "stdp_checkbox"):
            self.main_window.stdp_checkbox.setChecked(stdp_data.get("enabled", False))

        if stdp_data.get("enabled", False) and hasattr(self.main_window, "stdp_forms"):
            self._load_feature_params(self.main_window.stdp_forms, stdp_data)

        # Load Distance Connectivity options
        distance_data = data.get("distance_connectivity", {})
        if hasattr(self.main_window, "distance_connectivity_checkbox"):
            self.main_window.distance_connectivity_checkbox.setChecked(
                distance_data.get("enabled", False)
            )

        if distance_data.get("enabled", False) and hasattr(
            self.main_window, "distance_connectivity_forms"
        ):
            self._load_feature_params(self.main_window.distance_connectivity_forms, distance_data)

    def _load_feature_params(self, forms, data):
        """Helper method to load parameters into form widgets."""
        if not forms or "params" not in forms:
            return

        for param_key, widget in forms["params"].items():
            if param_key in data:
                try:
                    if hasattr(widget, "setValue"):
                        widget.setValue(float(data[param_key]))
                    elif hasattr(widget, "setCurrentText"):
                        # For combo boxes, we need to handle display_options mapping
                        value = str(data[param_key])

                        # Try to find the parameter configuration to check for display_options
                        param_config = None
                        if (
                            hasattr(self.main_window, "synaptic_delays_forms")
                            and forms == self.main_window.synaptic_delays_forms
                        ):
                            param_config = SYNAPTIC_DELAYS_CONFIG.get(param_key)
                        elif (
                            hasattr(self.main_window, "stdp_forms")
                            and forms == self.main_window.stdp_forms
                        ):
                            param_config = STDP_CONFIG.get(param_key)
                        elif (
                            hasattr(self.main_window, "distance_connectivity_forms")
                            and forms == self.main_window.distance_connectivity_forms
                        ):
                            param_config = DISTANCE_CONNECTIVITY_CONFIG.get(param_key)

                        if (
                            param_config
                            and param_config.get("type") == "combo"
                            and "display_options" in param_config
                        ):
                            # Map actual value to display value
                            try:
                                value_index = param_config["options"].index(value)
                                display_value = param_config["display_options"][value_index]
                                widget.setCurrentText(display_value)
                            except (ValueError, IndexError):
                                # Fallback to original value if mapping fails
                                widget.setCurrentText(value)
                        else:
                            widget.setCurrentText(value)
                    elif hasattr(widget, "setChecked"):
                        widget.setChecked(bool(data[param_key]))
                except (ValueError, TypeError):
                    pass  # Skip if value can't be converted

    def _collect_feature_params(self, feature_name, forms):
        """Collect parameters for a feature, handling combo boxes with display_options."""
        params = {}
        if not forms or "params" not in forms:
            return params

        for param_key, widget in forms["params"].items():
            if hasattr(widget, "value"):
                params[param_key] = widget.value()
            elif hasattr(widget, "currentText"):
                # For combo boxes, check if we need to map display value to actual value
                param_config = self._get_param_config(feature_name, param_key)
                if param_config.get("type") == "combo":
                    params[param_key] = self._get_combo_value(widget, param_config)
                else:
                    params[param_key] = widget.currentText()
            elif hasattr(widget, "isChecked"):
                params[param_key] = widget.isChecked()
        return params

    def apply_advanced_preset(self, preset_name):
        """Apply a complete advanced network preset."""
        if preset_name not in ADVANCED_NETWORK_PRESETS:
            return

        preset = ADVANCED_NETWORK_PRESETS[preset_name]

        # Apply Dale's principle preset
        if "dales_principle" in preset:
            dales_preset = preset["dales_principle"]
            if hasattr(self.main_window, "dales_principle_checkbox"):
                self.main_window.dales_principle_checkbox.setChecked(
                    dales_preset.get("enabled", False)
                )
            if dales_preset.get("enabled", False) and hasattr(
                self.main_window, "dales_principle_forms"
            ):
                self._load_feature_params(self.main_window.dales_principle_forms, dales_preset)

        # Apply synaptic delays preset
        if "synaptic_delays" in preset:
            delays_preset = preset["synaptic_delays"]
            if hasattr(self.main_window, "synaptic_delays_checkbox"):
                self.main_window.synaptic_delays_checkbox.setChecked(
                    delays_preset.get("enabled", False)
                )
            if delays_preset.get("enabled", False) and hasattr(
                self.main_window, "synaptic_delays_forms"
            ):
                self._load_feature_params(self.main_window.synaptic_delays_forms, delays_preset)

        # Apply STDP preset
        if "stdp" in preset:
            stdp_preset = preset["stdp"]
            if hasattr(self.main_window, "stdp_checkbox"):
                self.main_window.stdp_checkbox.setChecked(stdp_preset.get("enabled", False))
            if stdp_preset.get("enabled", False) and hasattr(self.main_window, "stdp_forms"):
                self._load_feature_params(self.main_window.stdp_forms, stdp_preset)

        # Apply distance connectivity preset
        if "distance_connectivity" in preset:
            distance_preset = preset["distance_connectivity"]
            if hasattr(self.main_window, "distance_connectivity_checkbox"):
                self.main_window.distance_connectivity_checkbox.setChecked(
                    distance_preset.get("enabled", False)
                )
            if distance_preset.get("enabled", False) and hasattr(
                self.main_window, "distance_connectivity_forms"
            ):
                self._load_feature_params(
                    self.main_window.distance_connectivity_forms, distance_preset
                )

    def apply_stdp_preset(self, preset_name):
        """Apply a specific STDP preset."""
        if preset_name not in STDP_PRESETS:
            return

        preset = STDP_PRESETS[preset_name]
        if hasattr(self.main_window, "stdp_forms") and "params" in preset:
            self._load_feature_params(self.main_window.stdp_forms, preset["params"])

    def apply_distance_connectivity_preset(self, preset_name):
        """Apply a specific distance connectivity preset."""
        if preset_name not in DISTANCE_CONNECTIVITY_PRESETS:
            return

        preset = DISTANCE_CONNECTIVITY_PRESETS[preset_name]
        if hasattr(self.main_window, "distance_connectivity_forms") and "params" in preset:
            self._load_feature_params(
                self.main_window.distance_connectivity_forms, preset["params"]
            )

    def get_brian2_advanced_code(self, options):
        """Generate Brian2 code for advanced network features."""
        code_parts = []

        # Dale's Principle code generation
        if options.get("dales_principle", {}).get("enabled", False):
            dales_opts = options["dales_principle"]
            exc_ratio = dales_opts.get("excitatory_ratio", 0.8)
            exc_weight = dales_opts.get("exc_weight", 1.0)
            inh_weight = dales_opts.get("inh_weight", -4.0)
            exc_rev = dales_opts.get("exc_reversal", 0.0)
            inh_rev = dales_opts.get("inh_reversal", -70.0)

            code_parts.append(
                f"""
# Dale's Principle: Separate excitatory and inhibitory populations
N_exc = int({exc_ratio} * N)
N_inh = N - N_exc
neuron_type = np.zeros(N, dtype=int)  # 0=excitatory, 1=inhibitory
neuron_type[N_exc:] = 1

# Synaptic weights based on neuron type
syn_weights = np.where(neuron_type[synapses.i] == 0, {exc_weight}, {inh_weight})
syn_reversals = np.where(neuron_type[synapses.i] == 0, {exc_rev}, {inh_rev})
synapses.w = syn_weights * nS
synapses.E_syn = syn_reversals * mV
"""
            )

        # Synaptic Delays code generation
        if options.get("synaptic_delays", {}).get("enabled", False):
            delays_opts = options["synaptic_delays"]
            delay_type = delays_opts.get("delay_type", "uniform")
            min_delay = delays_opts.get("min_delay", 0.5)
            max_delay = delays_opts.get("max_delay", 2.0)
            mean_delay = delays_opts.get("mean_delay", 1.0)
            delay_std = delays_opts.get("delay_std", 0.3)

            if delay_type == "uniform":
                code_parts.append(
                    f"""
# Uniform synaptic delays
synapses.delay = 'uniform({min_delay}, {max_delay}) * ms'
"""
                )
            elif delay_type == "normal":
                code_parts.append(
                    f"""
# Normal distribution synaptic delays
synapses.delay = 'clip(normal({mean_delay}, {delay_std}), {min_delay}, {max_delay}) * ms'
"""
                )
            elif delay_type == "exponential":
                code_parts.append(
                    f"""
# Exponential distribution synaptic delays
synapses.delay = 'clip(exponential({mean_delay}), {min_delay}, {max_delay}) * ms'
"""
                )

        # STDP code generation
        if options.get("stdp", {}).get("enabled", False):
            stdp_opts = options["stdp"]
            stdp_type = stdp_opts.get("stdp_type", "additive")
            tau_pre = stdp_opts.get("tau_pre", 20.0)
            tau_post = stdp_opts.get("tau_post", 20.0)
            A_plus = stdp_opts.get("A_plus", 0.01)
            A_minus = stdp_opts.get("A_minus", 0.0105)
            w_min = stdp_opts.get("w_min", 0.0)
            w_max = stdp_opts.get("w_max", 5.0)

            if stdp_type == "additive":
                code_parts.append(
                    f"""
# Additive STDP
synapses.model += '''
dA_pre/dt = -A_pre / ({tau_pre} * ms) : 1 (event-driven)
dA_post/dt = -A_post / ({tau_post} * ms) : 1 (event-driven)
'''
synapses.on_pre += '''
A_pre += {A_plus}
w = clip(w + A_post, {w_min}, {w_max})
'''
synapses.on_post += '''
A_post += {A_plus}
w = clip(w - A_pre * {A_minus}, {w_min}, {w_max})
'''
"""
                )

        # Distance-dependent connectivity would be handled during network creation
        # This is more complex and requires spatial neuron positions

        return "\n".join(code_parts)

    def _get_combo_value(self, widget, config):
        """Get the actual value from a combo box that may use display_options."""
        if not hasattr(widget, "currentIndex"):
            return widget.currentText() if hasattr(widget, "currentText") else None

        current_index = widget.currentIndex()

        # If config has display_options, map index back to actual option value
        if "display_options" in config and "options" in config:
            if 0 <= current_index < len(config["options"]):
                return config["options"][current_index]

        # Fallback to currentText for backwards compatibility
        return widget.currentText() if hasattr(widget, "currentText") else None

    def _get_param_config(self, feature_name, param_key):
        """Get parameter configuration for a specific feature and parameter."""
        config_map = {
            "dales_principle": DALES_PRINCIPLE_CONFIG,
            "synaptic_delays": SYNAPTIC_DELAYS_CONFIG,
            "stdp": STDP_CONFIG,
            "distance_connectivity": DISTANCE_CONNECTIVITY_CONFIG,
        }
        return config_map.get(feature_name, {}).get(param_key, {})

    def get_advanced_network_config(self):
        """Get advanced network configuration data for config manager."""
        return self.get_advanced_network_options()
