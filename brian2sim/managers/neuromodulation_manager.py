# neuromodulation_manager.py
# Manager for neuromodulation configuration in Brian2Sim GUI

from PyQt6.QtCore import QObject, pyqtSignal

from brian2sim.models.neuromodulation_config import (
    NEUROMODULATION_CONFIG,
    NEUROMODULATION_RESEARCH_INFO,
)


class NeuromodulationManager(QObject):
    """Manager for neuromodulation systems configuration."""

    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config = NEUROMODULATION_CONFIG
        self.research_info = NEUROMODULATION_RESEARCH_INFO

    def connect_signals(self):
        """Connect UI signals to handle parameter changes"""
        # Get all widgets from the form generator
        if hasattr(self.main_window, "neuromodulation_form_generator"):
            param_widgets = self.main_window.neuromodulation_form_generator.get_param_widgets()
            for param_key, widget in param_widgets.items():
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(self.on_param_changed)
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(self.on_param_changed)
                elif hasattr(widget, "stateChanged"):
                    widget.stateChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any neuromodulation parameter changes"""
        self.param_changed.emit()

    def get_default_parameters(self):
        """Get default neuromodulation parameters."""
        defaults = {}
        for key, config in self.config.items():
            defaults[key] = config.get("default")
        return defaults

    def get_parameters(self):
        """Get current neuromodulation parameters from UI."""
        if hasattr(self.main_window, "neuromodulation_form_generator"):
            return self.main_window.neuromodulation_form_generator.get_params_for_save()
        return self.get_default_parameters()

    def validate_parameters(self, params):
        """Validate neuromodulation parameters."""
        validated = {}
        errors = []

        for key, value in params.items():
            if key not in self.config:
                continue

            config = self.config[key]
            param_type = config.get("type")

            try:
                if param_type == "checkbox":
                    validated[key] = bool(value)
                elif param_type in ["spinbox", "double_spinbox"]:
                    validated[key] = float(value)
                    # Check bounds
                    if "min" in config and validated[key] < config["min"]:
                        validated[key] = config["min"]
                        errors.append(f"{key}: Value below minimum ({config['min']})")
                    if "max" in config and validated[key] > config["max"]:
                        validated[key] = config["max"]
                        errors.append(f"{key}: Value above maximum ({config['max']})")
                elif param_type == "combo":
                    if value in config.get("options", []):
                        validated[key] = value
                    else:
                        validated[key] = config.get("default")
                        errors.append(f"{key}: Invalid option, using default")
                else:
                    validated[key] = value

            except (ValueError, TypeError):
                validated[key] = config.get("default")
                errors.append(f"{key}: Invalid value, using default")

        return validated, errors

    def get_research_validated_ranges(self):
        """Get research-validated parameter ranges."""
        return self.research_info.get("physiological_ranges", {})

    def get_implementation_notes(self):
        """Get implementation and usage notes."""
        return self.research_info.get("implementation_notes", {})

    def get_research_references(self):
        """Get research references for neuromodulation."""
        return self.research_info.get("research_references", [])

    def suggest_parameters_for_brain_region(self, brain_region):
        """Suggest parameters based on brain region."""
        suggestions = {}

        if brain_region.lower() in ["striatum", "basal_ganglia"]:
            # High dopamine innervation
            suggestions.update(
                {
                    "dopamine_system": True,
                    "dopamine_baseline": 0.15,
                    "dopamine_d1_effect": 0.3,
                    "dopamine_d2_effect": -0.2,
                    "acetylcholine_system": True,
                    "acetylcholine_baseline": 0.08,
                }
            )
        elif brain_region.lower() in ["cortex", "prefrontal"]:
            # Moderate dopamine, high acetylcholine
            suggestions.update(
                {
                    "dopamine_system": True,
                    "dopamine_baseline": 0.08,
                    "acetylcholine_system": True,
                    "acetylcholine_baseline": 0.1,
                    "nicotinic_effect": 0.4,
                    "noradrenaline_system": True,
                    "noradrenaline_baseline": 0.04,
                }
            )
        elif brain_region.lower() in ["hippocampus"]:
            # High acetylcholine for learning
            suggestions.update(
                {
                    "acetylcholine_system": True,
                    "acetylcholine_baseline": 0.12,
                    "nicotinic_effect": 0.5,
                    "muscarinic_effect": 0.2,
                    "serotonin_system": True,
                    "serotonin_baseline": 0.03,
                }
            )
        elif brain_region.lower() in ["brainstem", "raphe"]:
            # High serotonin
            suggestions.update(
                {
                    "serotonin_system": True,
                    "serotonin_baseline": 0.1,
                    "5ht1a_effect": -0.15,
                    "5ht2a_effect": 0.2,
                    "noradrenaline_system": True,
                    "noradrenaline_baseline": 0.08,
                }
            )
        elif brain_region.lower() in ["locus_coeruleus"]:
            # High noradrenaline
            suggestions.update(
                {
                    "noradrenaline_system": True,
                    "noradrenaline_baseline": 0.15,
                    "alpha1_effect": 0.3,
                    "beta_effect": 0.25,
                }
            )

        return suggestions

    def suggest_parameters_for_disease(self, disease_type):
        """Suggest parameters for disease states."""
        suggestions = {}

        if disease_type.lower() == "parkinsons":
            suggestions.update(
                {
                    "disease_state": True,
                    "disease_type": "parkinsons",
                    "disease_severity": 0.7,
                    "dopamine_system": True,
                    "dopamine_baseline": 0.03,  # Reduced dopamine
                    "dopamine_d1_effect": 0.1,  # Reduced D1 response
                    "dopamine_d2_effect": -0.05,  # Reduced D2 response
                }
            )
        elif disease_type.lower() == "alzheimers":
            suggestions.update(
                {
                    "disease_state": True,
                    "disease_type": "alzheimers",
                    "disease_severity": 0.6,
                    "acetylcholine_system": True,
                    "acetylcholine_baseline": 0.02,  # Reduced ACh
                    "nicotinic_effect": 0.15,  # Reduced response
                    "muscarinic_effect": 0.08,
                }
            )
        elif disease_type.lower() == "depression":
            suggestions.update(
                {
                    "disease_state": True,
                    "disease_type": "depression",
                    "disease_severity": 0.5,
                    "serotonin_system": True,
                    "serotonin_baseline": 0.01,  # Reduced serotonin
                    "5ht1a_effect": -0.05,
                    "noradrenaline_system": True,
                    "noradrenaline_baseline": 0.015,  # Reduced noradrenaline
                }
            )
        elif disease_type.lower() == "adhd":
            suggestions.update(
                {
                    "disease_state": True,
                    "disease_type": "adhd",
                    "disease_severity": 0.4,
                    "dopamine_system": True,
                    "dopamine_baseline": 0.06,  # Reduced dopamine
                    "noradrenaline_system": True,
                    "noradrenaline_baseline": 0.02,  # Reduced noradrenaline
                }
            )
        elif disease_type.lower() == "schizophrenia":
            suggestions.update(
                {
                    "disease_state": True,
                    "disease_type": "schizophrenia",
                    "disease_severity": 0.6,
                    "dopamine_system": True,
                    "dopamine_baseline": 0.2,  # Altered dopamine signaling
                    "dopamine_d2_effect": -0.3,  # Enhanced D2 response
                    "acetylcholine_system": True,
                    "acetylcholine_baseline": 0.03,  # Reduced ACh
                }
            )

        return suggestions

    def suggest_parameters_for_pharmacology(self, drug_type, concentration=None):
        """Suggest parameters for pharmacological interventions."""
        suggestions = {}

        if "dopamine_agonist" in drug_type.lower():
            suggestions.update(
                {
                    "pharmacology": True,
                    "drug_type": "dopamine_agonist",
                    "drug_concentration": concentration or 0.2,
                    "dopamine_d1_effect": 0.4,  # Enhanced response
                    "dopamine_d2_effect": -0.3,
                }
            )
        elif "dopamine_antagonist" in drug_type.lower():
            suggestions.update(
                {
                    "pharmacology": True,
                    "drug_type": "dopamine_antagonist",
                    "drug_concentration": concentration or 0.1,
                    "dopamine_d1_effect": 0.05,  # Blocked response
                    "dopamine_d2_effect": -0.02,
                }
            )
        elif "acetylcholine_agonist" in drug_type.lower():
            suggestions.update(
                {
                    "pharmacology": True,
                    "drug_type": "acetylcholine_agonist",
                    "drug_concentration": concentration or 0.1,
                    "nicotinic_effect": 0.5,  # Enhanced response
                    "muscarinic_effect": 0.3,
                }
            )
        elif "serotonin" in drug_type.lower():
            if "agonist" in drug_type.lower():
                suggestions.update(
                    {
                        "pharmacology": True,
                        "drug_type": "serotonin_agonist",
                        "drug_concentration": concentration or 0.05,
                        "5ht1a_effect": -0.2,
                        "5ht2a_effect": 0.3,
                    }
                )
            else:
                suggestions.update(
                    {
                        "pharmacology": True,
                        "drug_type": "serotonin_antagonist",
                        "drug_concentration": concentration or 0.1,
                        "5ht1a_effect": -0.02,
                        "5ht2a_effect": 0.05,
                    }
                )

        return suggestions

    def get_parameter_description(self, param_name):
        """Get description for a specific parameter."""
        if param_name in self.config:
            return self.config[param_name].get("tooltip", "No description available")
        return "Parameter not found"

    def validate_concentration_ranges(self, params):
        """Validate that neuromodulator concentrations are physiologically realistic."""
        warnings = []

        # Check dopamine concentration
        if params.get("dopamine_baseline", 0) > 0.5:
            warnings.append("Dopamine baseline concentration is very high (>0.5 μM)")

        # Check acetylcholine concentration
        if params.get("acetylcholine_baseline", 0) > 0.3:
            warnings.append("Acetylcholine baseline concentration is very high (>0.3 μM)")

        # Check serotonin concentration
        if params.get("serotonin_baseline", 0) > 0.1:
            warnings.append("Serotonin baseline concentration is very high (>0.1 μM)")

        # Check release rates
        if params.get("dopamine_release_rate", 0) > 0.05:
            warnings.append("Dopamine release rate is very high (>0.05 μM/ms)")

        # Check clearance times
        if params.get("acetylcholine_clearance_tau", 200) < 50:
            warnings.append("Acetylcholine clearance time is very fast (<50 ms)")

        return warnings

    def estimate_network_effects(self, params):
        """Estimate the overall network effects of neuromodulation."""
        effects = {}

        # Dopamine effects
        if params.get("dopamine_system", False):
            da_baseline = params.get("dopamine_baseline", 0.1)
            d1_effect = params.get("dopamine_d1_effect", 0.2)
            d2_effect = params.get("dopamine_d2_effect", -0.15)

            net_da_effect = da_baseline * (d1_effect + abs(d2_effect))
            effects["dopamine_network_effect"] = net_da_effect

            if net_da_effect > 0.05:
                effects["dopamine_prediction"] = (
                    "Strong dopaminergic modulation - expect enhanced plasticity"
                )
            else:
                effects["dopamine_prediction"] = "Moderate dopaminergic modulation"

        # Acetylcholine effects
        if params.get("acetylcholine_system", False):
            ach_baseline = params.get("acetylcholine_baseline", 0.05)
            nic_effect = params.get("nicotinic_effect", 0.3)
            mus_effect = params.get("muscarinic_effect", 0.15)

            net_ach_effect = ach_baseline * (nic_effect + mus_effect)
            effects["acetylcholine_network_effect"] = net_ach_effect

            if net_ach_effect > 0.02:
                effects["acetylcholine_prediction"] = (
                    "Strong cholinergic modulation - expect enhanced attention/learning"
                )
            else:
                effects["acetylcholine_prediction"] = "Moderate cholinergic modulation"

        # Overall network state prediction
        total_excitatory = 0
        total_inhibitory = 0

        if "dopamine_network_effect" in effects:
            total_excitatory += effects["dopamine_network_effect"]
        if "acetylcholine_network_effect" in effects:
            total_excitatory += effects["acetylcholine_network_effect"]

        if params.get("serotonin_system", False):
            ht1a = abs(params.get("5ht1a_effect", -0.1))
            total_inhibitory += ht1a * params.get("serotonin_baseline", 0.02)

        if total_excitatory > total_inhibitory * 2:
            effects["network_state_prediction"] = "Network likely to be hyperexcitable"
        elif total_inhibitory > total_excitatory * 2:
            effects["network_state_prediction"] = "Network likely to be hypoexcitable"
        else:
            effects["network_state_prediction"] = "Balanced neuromodulatory state"

        return effects

    def export_parameters(self, params, filename=None):
        """Export parameters to file."""
        import json
        from datetime import datetime

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"neuromodulation_params_{timestamp}.json"

        export_data = {
            "neuromodulation_parameters": params,
            "export_timestamp": datetime.now().isoformat(),
            "parameter_descriptions": {k: v.get("tooltip", "") for k, v in self.config.items()},
            "research_info": self.research_info,
            "validation_warnings": self.validate_concentration_ranges(params),
            "network_effects": self.estimate_network_effects(params),
        }

        try:
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)
            return filename
        except Exception as e:
            raise Exception(f"Failed to export parameters: {e}")

    def import_parameters(self, filename):
        """Import parameters from file."""
        import json

        try:
            with open(filename, "r") as f:
                data = json.load(f)

            if "neuromodulation_parameters" in data:
                params = data["neuromodulation_parameters"]
                validated_params, errors = self.validate_parameters(params)
                return validated_params, errors
            else:
                raise Exception("Invalid file format: missing neuromodulation_parameters")

        except json.JSONDecodeError:
            raise Exception("Invalid JSON file")
        except FileNotFoundError:
            raise Exception("File not found")
        except Exception as e:
            raise Exception(f"Failed to import parameters: {e}")

    def reset_to_defaults(self):
        """Reset neuromodulation to their default values."""
        if hasattr(self.main_window, "neuromodulation_form_generator"):
            self.main_window.neuromodulation_form_generator.reset_to_defaults()
