"""
Parameter validation system for Brian2Sim GUI.
Provides comprehensive validation with clear error messages.
"""

import re
from typing import Any, Dict, List

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox


class ValidationResult:
    """Represents the result of a parameter validation."""

    def __init__(self, is_valid: bool = True, message: str = "", severity: str = "error", parameter: str = ""):
        self.is_valid = is_valid
        self.message = message
        self.severity = severity  # "error", "warning", "info"
        self.parameter = parameter  # Name of the parameter being validated

    def __bool__(self):
        return self.is_valid


class ParameterValidator:
    """Comprehensive parameter validation system."""

    def __init__(self):
        self.validation_rules = {}
        self.cross_parameter_rules = []
        self.setup_default_rules()

    def setup_default_rules(self):
        """Setup default validation rules for common neuroscience parameters."""

        # Voltage rules (typical biological ranges)
        self.add_range_rule(
            "voltage", -100, 50, "mV", "Membrane potential should be between -100mV and +50mV"
        )

        # Long time constant rules (Must come before generic tau rule)
        self.add_range_rule("bcm_tau", 0.1, 100000, "ms")
        self.add_range_rule("smoothing_tau", 0.1, 100000, "ms")
        self.add_range_rule("desensitization_tau", 0.1, 100000, "ms")

        # Time constant rules
        self.add_range_rule(
            "tau", 0.1, 1000, "ms", "Time constants should be between 0.1ms and 1000ms"
        )

        # Conductance rules
        self.add_range_rule(
            "conductance", 0, 1000, "nS", "Conductances should be between 0 and 1000 nS"
        )

        # Probability rules
        self.add_range_rule("probability", 0, 1, "", "Probabilities must be between 0 and 1")

        # Concentration rules
        self.add_range_rule(
            "concentration", 0, 1000, "mM", "Concentrations should be between 0 and 1000 mM"
        )

        # Setup cross-parameter validation rules
        self.setup_cross_parameter_rules()

    def add_range_rule(
        self, param_pattern: str, min_val: float, max_val: float, unit: str = "", message: str = ""
    ):
        """Add a range validation rule for parameters matching a pattern."""
        if not message:
            message = f"Value must be between {min_val} and {max_val} {unit}".strip()

        self.validation_rules[param_pattern] = {
            "type": "range",
            "min": min_val,
            "max": max_val,
            "unit": unit,
            "message": message,
        }

    def setup_cross_parameter_rules(self):
        """Setup rules that validate relationships between parameters."""

        # NMDA voltage dependency rules
        self.cross_parameter_rules.append(
            {
                "condition": lambda params: params.get("nmda_enabled", False),
                "required_params": ["mg_concentration"],
                "message": "NMDA receptors require Mg2+ concentration to be specified",
                "severity": "error",
            }
        )

        # Calcium dynamics rules
        self.cross_parameter_rules.append(
            {
                "condition": lambda params: params.get("calcium_dynamics_enabled", False),
                "required_params": ["calcium_rest", "calcium_tau"],
                "message": "Calcium dynamics requires rest concentration and time constant",
                "severity": "error",
            }
        )

        # Short-term plasticity rules
        self.cross_parameter_rules.append(
            {
                "condition": lambda params: params.get("short_term_plasticity_enabled", False),
                "conflicting_params": [("facilitation_enabled", "depression_enabled")],
                "message": "Facilitation and depression cannot be enabled simultaneously",
                "severity": "warning",
            }
        )

        # Homeostatic plasticity rules
        self.cross_parameter_rules.append(
            {
                "condition": lambda params: params.get("homeostatic_plasticity_enabled", False),
                "dependencies": [
                    (["target_firing_rate"], "Target firing rate must be specified"),
                    (["scaling_factor"], "Scaling factor must be specified"),
                ],
                "message": "Homeostatic plasticity requires target firing rate and scaling factor",
                "severity": "error",
            }
        )

        # Network size consistency rules
        self.cross_parameter_rules.append(
            {
                "condition": lambda params: True,  # Always check
                "custom_validator": self._validate_network_consistency,
                "message": "Network parameters are inconsistent",
                "severity": "error",
            }
        )

    def _validate_network_consistency(self, params: Dict[str, Any]) -> ValidationResult:
        """Validate network size consistency."""
        # Check for the actual parameter name used in the config
        total_neurons = params.get("num_neurons", 0)
        
        # Fallback: also check for legacy parameter names
        if total_neurons == 0:
            n_exc = params.get("n_excitatory", 0)
            n_inh = params.get("n_inhibitory", 0)
            total_neurons = n_exc + n_inh

        if total_neurons == 0:
            return ValidationResult(False, "Network must have at least one neuron", parameter="Number of Neurons")

        if total_neurons > 10000:
            return ValidationResult(True, "Large networks may be slow to simulate", "warning", parameter="Number of Neurons")

        # Check connection probabilities
        exc_prob = params.get("excitatory_connection_probability", 0)
        inh_prob = params.get("inhibitory_connection_probability", 0)

        if exc_prob > 0.5 or inh_prob > 0.5:
            return ValidationResult(
                True, "High connection probabilities may create dense networks", "warning", parameter="Connection Probability"
            )

        return ValidationResult(True)

    def validate_parameter(self, param_name: str, value: Any) -> ValidationResult:
        """Validate a single parameter value."""

        # Check for matching validation rules
        for pattern, rule in self.validation_rules.items():
            if re.search(pattern, param_name.lower()):
                return self._apply_rule(rule, value, param_name)

        # Default validation for common types
        if isinstance(value, (int, float)):
            if value < 0 and any(
                keyword in param_name.lower() for keyword in ["time", "delay", "duration", "rate"]
            ):
                return ValidationResult(False, f"{param_name} cannot be negative", parameter=param_name)

        return ValidationResult(True)

    def _apply_rule(self, rule: Dict, value: Any, param_name: str) -> ValidationResult:
        """Apply a specific validation rule."""

        if rule["type"] == "range":
            try:
                num_value = float(value)
                if not (rule["min"] <= num_value <= rule["max"]):
                    return ValidationResult(False, rule["message"], parameter=param_name)
            except (ValueError, TypeError):
                return ValidationResult(False, f"{param_name} must be a number", parameter=param_name)

        return ValidationResult(True)

    def validate_all_parameters(self, all_params: Dict[str, Any]) -> List[ValidationResult]:
        """Validate all parameters including cross-parameter rules."""

        results = []

        # Validate individual parameters
        for param_name, value in all_params.items():
            result = self.validate_parameter(param_name, value)
            if not result.is_valid:
                results.append(result)

        # Validate cross-parameter rules
        for rule in self.cross_parameter_rules:
            result = self._validate_cross_parameter_rule(rule, all_params)
            if not result.is_valid:
                results.append(result)

        return results

    def _validate_cross_parameter_rule(
        self, rule: Dict, params: Dict[str, Any]
    ) -> ValidationResult:
        """Validate a cross-parameter rule."""

        # Check if rule condition applies
        if not rule["condition"](params):
            return ValidationResult(True)

        # Custom validator
        if "custom_validator" in rule:
            return rule["custom_validator"](params)

        # Required parameters check
        if "required_params" in rule:
            missing = [p for p in rule["required_params"] if p not in params or params[p] is None]
            if missing:
                return ValidationResult(False, f"{rule['message']}: Missing {', '.join(missing)}")

        # Conflicting parameters check
        if "conflicting_params" in rule:
            for param_group in rule["conflicting_params"]:
                enabled_count = sum(1 for p in param_group if params.get(p, False))
                if enabled_count > 1:
                    return ValidationResult(False, rule["message"])

        # Dependencies check
        if "dependencies" in rule:
            for dep_params, dep_message in rule["dependencies"]:
                missing = [p for p in dep_params if p not in params or params[p] is None]
                if missing:
                    return ValidationResult(False, dep_message)

        return ValidationResult(True)


class ValidationManager(QObject):
    """Manager for real-time parameter validation in the GUI."""

    validation_error = pyqtSignal(str, str)  # message, severity
    validation_cleared = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.validator = ParameterValidator()
        self.current_errors = []
        self.validation_enabled = True

    def validate_current_parameters(self) -> bool:
        """Validate all current parameters in the GUI."""

        if not self.validation_enabled:
            return True

        # Collect all parameters from all managers
        all_params = self._collect_all_parameters()

        # Validate parameters
        results = self.validator.validate_all_parameters(all_params)

        # Update error display
        self._update_error_display(results)

        # Return True if no errors (warnings are ok)
        return not any(r for r in results if not r.is_valid and r.severity == "error")

    def _collect_all_parameters(self) -> Dict[str, Any]:
        """Collect parameters from all managers."""
        all_params = {}

        # Map managers to their parameter getter methods
        manager_methods = {
            "neuron_models_manager": "get_neuron_model",
            "sim_params_manager": "get_sim_params",
            "noise_manager": "get_config",
            "input_patterns_manager": "get_input_patterns_config",
            "network_manager": "get_config",
            "advanced_network_manager": "get_config",
            "gap_junctions_manager": "get_parameters",
            "synaptic_receptors_manager": "get_synaptic_receptors_config",
            "calcium_dynamics_manager": "get_parameters",
            "short_term_plasticity_manager": "get_parameters",
            "homeostatic_plasticity_manager": "get_parameters",
            "neuromodulation_manager": "get_parameters",
            "multicompartment_manager": "get_parameters",
        }

        for manager_name, method_name in manager_methods.items():
            if hasattr(self.main_window, manager_name):
                manager = getattr(self.main_window, manager_name)
                if hasattr(manager, method_name):
                    try:
                        params = getattr(manager, method_name)()
                        if isinstance(params, dict):
                            all_params.update(params)
                    except Exception as e:
                        print(f"Error collecting parameters from {manager_name}: {e}")

        return all_params

    def _update_error_display(self, results: List[ValidationResult]):
        """Update the error display in the GUI."""

        self.current_errors = [r for r in results if not r.is_valid]

        if not self.current_errors:
            self.validation_cleared.emit()
            return

        # Group by severity
        errors = [r for r in self.current_errors if r.severity == "error"]
        warnings = [r for r in self.current_errors if r.severity == "warning"]

        if errors:
            error_msg = "\n".join([r.message for r in errors[:3]])  # Show first 3 errors
            if len(errors) > 3:
                error_msg += f"\n... and {len(errors) - 3} more errors"
            self.validation_error.emit(error_msg, "error")
        elif warnings:
            warning_msg = "\n".join([r.message for r in warnings[:3]])  # Show first 3 warnings
            if len(warnings) > 3:
                warning_msg += f"\n... and {len(warnings) - 3} more warnings"
            self.validation_error.emit(warning_msg, "warning")

    def show_validation_dialog(self) -> bool:
        """Show a dialog with all validation issues. Returns True if user wants to continue."""

        if not self.current_errors:
            return True

        errors = [r for r in self.current_errors if r.severity == "error"]
        warnings = [r for r in self.current_errors if r.severity == "warning"]

        dialog_text = ""
        if errors:
            dialog_text += "ERRORS:\n" + "\n".join([f"• {r.message}" for r in errors]) + "\n\n"
        if warnings:
            dialog_text += "WARNINGS:\n" + "\n".join([f"• {r.message}" for r in warnings])

        if errors:
            # Critical errors - must be fixed
            QMessageBox.critical(
                self.main_window,
                "Parameter Validation Errors",
                "The following errors must be fixed before proceeding:\n\n" + dialog_text,
            )
            return False
        else:
            # Only warnings - user can choose to continue
            reply = QMessageBox.question(
                self.main_window,
                "Parameter Validation Warnings",
                "The following warnings were found:\n\n"
                + dialog_text
                + "\n\nDo you want to continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            return reply == QMessageBox.StandardButton.Yes

    def enable_validation(self, enabled: bool):
        """Enable or disable validation."""
        self.validation_enabled = enabled

    def add_custom_rule(self, rule_func, message: str, severity: str = "error"):
        """Add a custom validation rule."""
        self.validator.cross_parameter_rules.append(
            {
                "condition": lambda params: True,
                "custom_validator": rule_func,
                "message": message,
                "severity": severity,
            }
        )
