# gap_junctions_manager.py
# Manager for gap junctions configuration in Brian2Sim GUI

from PyQt6.QtCore import QObject, pyqtSignal

from brian2sim.models.gap_junctions_config import GAP_JUNCTION_RESEARCH_INFO, GAP_JUNCTIONS_CONFIG


class GapJunctionsManager(QObject):
    """Manager for gap junctions (electrical synapses) configuration."""

    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config = GAP_JUNCTIONS_CONFIG
        self.research_info = GAP_JUNCTION_RESEARCH_INFO

    def connect_signals(self):
        """Connect UI signals to handle parameter changes"""
        # Get all widgets from the form generator
        if hasattr(self.main_window, "gap_junctions_form_generator"):
            param_widgets = self.main_window.gap_junctions_form_generator.get_param_widgets()
            for param_key, widget in param_widgets.items():
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(self.on_param_changed)
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(self.on_param_changed)
                elif hasattr(widget, "stateChanged"):
                    widget.stateChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any gap junctions parameter changes"""
        self.param_changed.emit()

    def get_default_parameters(self):
        """Get default gap junctions parameters."""
        defaults = {}
        for key, config in self.config.items():
            defaults[key] = config.get("default")
        return defaults

    def get_parameters(self):
        """Get current gap junctions parameters from UI."""
        if hasattr(self.main_window, "gap_junctions_form_generator"):
            return self.main_window.gap_junctions_form_generator.get_params_for_save()
        return self.get_default_parameters()

    def validate_parameters(self, params):
        """Validate gap junctions parameters."""
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
        """Get research references for gap junctions."""
        return self.research_info.get("research_references", [])

    def suggest_parameters_for_cell_type(self, cell_type):
        """Suggest parameters based on cell type."""
        suggestions = {}

        if cell_type.lower() in ["interneuron", "inhibitory"]:
            # Interneurons typically have stronger gap junction coupling
            suggestions.update(
                {
                    "conductance": 0.2,  # Higher conductance
                    "connection_probability": 0.15,  # Higher connection probability
                    "coupling_coefficient": 0.2,
                    "spatial_organization": "columnar",
                    "connection_specificity": "interneuron_network",
                }
            )
        elif cell_type.lower() in ["pyramidal", "excitatory"]:
            # Pyramidal cells have weaker, more selective coupling
            suggestions.update(
                {
                    "conductance": 0.05,  # Lower conductance
                    "connection_probability": 0.05,  # Lower connection probability
                    "coupling_coefficient": 0.1,
                    "spatial_organization": "distance_based",
                    "connection_specificity": "same_type_only",
                }
            )
        else:
            # Default mixed population
            suggestions.update(
                {
                    "conductance": 0.1,
                    "connection_probability": 0.1,
                    "coupling_coefficient": 0.1,
                    "spatial_organization": "distance_based",
                    "connection_specificity": "all_to_all",
                }
            )

        return suggestions

    def suggest_parameters_for_brain_region(self, brain_region):
        """Suggest parameters based on brain region."""
        suggestions = {}

        if brain_region.lower() in ["cortex", "neocortex"]:
            suggestions.update(
                {
                    "conductance": 0.08,
                    "connection_probability": 0.08,
                    "spatial_organization": "columnar",
                    "cluster_size": 15,
                    "voltage_dependence": True,
                }
            )
        elif brain_region.lower() in ["hippocampus"]:
            suggestions.update(
                {
                    "conductance": 0.12,
                    "connection_probability": 0.12,
                    "spatial_organization": "radial_clusters",
                    "cluster_size": 8,
                    "activity_dependent": True,
                }
            )
        elif brain_region.lower() in ["thalamus"]:
            suggestions.update(
                {
                    "conductance": 0.15,
                    "connection_probability": 0.15,
                    "spatial_organization": "nearest_neighbor",
                    "neuromodulation": True,
                }
            )
        elif brain_region.lower() in ["brainstem", "reticular"]:
            suggestions.update(
                {
                    "conductance": 0.25,
                    "connection_probability": 0.2,
                    "spatial_organization": "radial_clusters",
                    "cluster_size": 12,
                }
            )
        elif brain_region.lower() in ["cerebellum"]:
            suggestions.update(
                {
                    "conductance": 0.05,
                    "connection_probability": 0.05,
                    "spatial_organization": "columnar",
                    "connection_specificity": "inhibitory_only",
                }
            )

        return suggestions

    def suggest_parameters_for_pathology(self, pathology_type):
        """Suggest parameters for pathological conditions."""
        suggestions = {}

        if pathology_type.lower() == "epilepsy":
            suggestions.update(
                {
                    "pathological_conditions": True,
                    "pathology_type": "epilepsy",
                    "pathology_severity": 0.7,
                    "conductance": 0.3,  # Increased coupling
                    "connection_probability": 0.25,  # Increased connectivity
                    "activity_dependent": True,
                }
            )
        elif pathology_type.lower() == "ischemia":
            suggestions.update(
                {
                    "pathological_conditions": True,
                    "pathology_type": "ischemia",
                    "pathology_severity": 0.8,
                    "conductance": 0.02,  # Reduced coupling
                    "connection_probability": 0.03,  # Reduced connectivity
                    "voltage_dependence": True,
                    "gating_voltage": -50.0,  # Shifted gating
                }
            )
        elif pathology_type.lower() == "aging":
            suggestions.update(
                {
                    "pathological_conditions": True,
                    "pathology_type": "aging",
                    "pathology_severity": 0.4,
                    "conductance": 0.06,  # Moderately reduced
                    "connection_probability": 0.06,
                    "junction_noise": True,
                    "noise_amplitude": 0.02,
                }
            )
        elif pathology_type.lower() == "inflammation":
            suggestions.update(
                {
                    "pathological_conditions": True,
                    "pathology_type": "inflammation",
                    "pathology_severity": 0.6,
                    "conductance": 0.15,  # Variable changes
                    "junction_noise": True,
                    "noise_amplitude": 0.03,
                    "neuromodulation": True,
                }
            )

        return suggestions

    def get_parameter_description(self, param_name):
        """Get description for a specific parameter."""
        if param_name in self.config:
            return self.config[param_name].get("tooltip", "No description available")
        return "Parameter not found"

    def export_parameters(self, params, filename=None):
        """Export parameters to file."""
        import json
        from datetime import datetime

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gap_junctions_params_{timestamp}.json"

        export_data = {
            "gap_junctions_parameters": params,
            "export_timestamp": datetime.now().isoformat(),
            "parameter_descriptions": {k: v.get("tooltip", "") for k, v in self.config.items()},
            "research_info": self.research_info,
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

            if "gap_junctions_parameters" in data:
                params = data["gap_junctions_parameters"]
                validated_params, errors = self.validate_parameters(params)
                return validated_params, errors
            else:
                raise Exception("Invalid file format: missing gap_junctions_parameters")

        except json.JSONDecodeError:
            raise Exception("Invalid JSON file")
        except FileNotFoundError:
            raise Exception("File not found")
        except Exception as e:
            raise Exception(f"Failed to import parameters: {e}")

    def get_coupling_strength_estimate(self, params):
        """Estimate effective coupling strength from parameters."""
        conductance = params.get("conductance", 0.1)
        coupling_coeff = params.get("coupling_coefficient", 0.1)
        connection_prob = params.get("connection_probability", 0.1)

        # Simple estimate: product of key factors
        effective_coupling = conductance * coupling_coeff * connection_prob

        # Adjust for voltage dependence
        if params.get("voltage_dependence", False):
            effective_coupling *= 0.7  # Reduced due to gating

        # Adjust for plasticity
        if params.get("activity_dependent", False):
            plasticity_factor = params.get("potentiation_rate", 0.01) / params.get(
                "depression_rate", 0.001
            )
            effective_coupling *= min(2.0, 1.0 + plasticity_factor * 0.1)

        return effective_coupling

    def generate_network_analysis_suggestions(self, params):
        """Generate suggestions for network analysis based on parameters."""
        suggestions = []

        coupling_strength = self.get_coupling_strength_estimate(params)

        if coupling_strength > 0.01:
            suggestions.append("Strong coupling detected - monitor for network synchronization")
            suggestions.append("Consider recording local field potentials")
            suggestions.append("Analyze cross-correlation between neuron pairs")

        if params.get("activity_dependent", False):
            suggestions.append(
                "Activity-dependent plasticity enabled - track coupling changes over time"
            )
            suggestions.append("Monitor plasticity threshold crossings")

        if params.get("voltage_dependence", False):
            suggestions.append(
                "Voltage-dependent gating enabled - analyze voltage-coupling relationships"
            )

        if params.get("spatial_organization") == "columnar":
            suggestions.append(
                "Columnar organization - analyze within-column vs between-column coupling"
            )

        if params.get("neuromodulation", False):
            suggestions.append("Neuromodulation enabled - track modulator effects on coupling")

        return suggestions

    def reset_to_defaults(self):
        """Reset gap junctions to their default values."""
        if hasattr(self.main_window, "gap_junctions_form_generator"):
            self.main_window.gap_junctions_form_generator.reset_to_defaults()
