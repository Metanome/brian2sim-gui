# multicompartment_manager.py
# Manager for multi-compartment neuron configuration with research-based validation

import os
from typing import Dict, List, Tuple

from PyQt6.QtCore import QObject, pyqtSignal


class MulticompartmentManager(QObject):
    """Manager for multi-compartment neuron parameters with validation and research-based suggestions."""

    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.cell_type_parameters = self._initialize_cell_type_parameters()
        self.morphology_presets = self._initialize_morphology_presets()
        self.validation_rules = self._initialize_validation_rules()

    def connect_signals(self):
        """Connect UI signals to handle parameter changes"""
        # Get all widgets from the form generator
        if hasattr(self.main_window, "multicompartment_form_generator"):
            param_widgets = self.main_window.multicompartment_form_generator.get_param_widgets()
            for param_key, widget in param_widgets.items():
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(self.on_param_changed)
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(self.on_param_changed)
                elif hasattr(widget, "stateChanged"):
                    widget.stateChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any multicompartment parameter changes"""
        self.param_changed.emit()

    def get_parameters(self):
        """Get current multicompartment parameters from UI."""
        if hasattr(self.main_window, "multicompartment_form_generator"):
            return self.main_window.multicompartment_form_generator.get_params_for_save()
        return {}

    def _initialize_cell_type_parameters(self) -> Dict:
        """Initialize research-validated parameters for different cell types."""
        return {
            "L5_pyramidal": {
                "description": "Layer 5 thick-tufted pyramidal neuron",
                "soma_diameter": 16.8,
                "soma_length": 16.8,
                "dendrite_segments": 15,
                "dendrite_length_total": 800.0,
                "dendrite_diameter_proximal": 4.0,
                "dendrite_diameter_distal": 0.5,
                "axon_length": 200.0,
                "ais_length": 30.0,
                "dendrite_branching": True,
                "branch_points": 3,
                "soma_nav_density": 50.0,
                "ais_nav_density": 200.0,
                "dendrite_nav_density": 15.0,
                "soma_kv_density": 30.0,
                "ais_kv_density": 100.0,
                "dendrite_kv_density": 5.0,
                "dendrite_ca_density": 1.0,
                "dendrite_h_density": 0.2,
                "reference": "Hay et al., PLoS Comput Biol (2011)",
                "typical_regions": ["motor_cortex", "somatosensory_cortex", "visual_cortex"],
            },
            "L23_pyramidal": {
                "description": "Layer 2/3 pyramidal neuron",
                "soma_diameter": 14.0,
                "soma_length": 14.0,
                "dendrite_segments": 12,
                "dendrite_length_total": 600.0,
                "dendrite_diameter_proximal": 3.0,
                "dendrite_diameter_distal": 0.5,
                "axon_length": 150.0,
                "ais_length": 25.0,
                "dendrite_branching": True,
                "branch_points": 2,
                "soma_nav_density": 40.0,
                "ais_nav_density": 180.0,
                "dendrite_nav_density": 10.0,
                "soma_kv_density": 25.0,
                "ais_kv_density": 80.0,
                "dendrite_kv_density": 3.0,
                "dendrite_ca_density": 0.5,
                "dendrite_h_density": 0.1,
                "reference": "Almog & Korngreen, PLoS Comput Biol (2014)",
                "typical_regions": ["prefrontal_cortex", "association_cortex"],
            },
            "fast_spiking_IN": {
                "description": "Parvalbumin-positive fast-spiking interneuron",
                "soma_diameter": 12.0,
                "soma_length": 12.0,
                "dendrite_segments": 6,
                "dendrite_length_total": 200.0,
                "dendrite_diameter_proximal": 2.0,
                "dendrite_diameter_distal": 0.5,
                "axon_length": 100.0,
                "ais_length": 20.0,
                "dendrite_branching": False,
                "branch_points": 1,
                "soma_nav_density": 100.0,
                "ais_nav_density": 400.0,
                "dendrite_nav_density": 5.0,
                "soma_kv_density": 80.0,
                "ais_kv_density": 200.0,
                "dendrite_kv_density": 10.0,
                "dendrite_ca_density": 0.1,
                "dendrite_h_density": 0.0,
                "reference": "Teeter et al., Nat Commun (2018)",
                "typical_regions": ["all_cortical_regions", "hippocampus"],
            },
            "basket_cell": {
                "description": "CCK-positive basket cell interneuron",
                "soma_diameter": 15.0,
                "soma_length": 15.0,
                "dendrite_segments": 8,
                "dendrite_length_total": 300.0,
                "dendrite_diameter_proximal": 2.5,
                "dendrite_diameter_distal": 0.5,
                "axon_length": 200.0,
                "ais_length": 25.0,
                "dendrite_branching": True,
                "branch_points": 2,
                "soma_nav_density": 60.0,
                "ais_nav_density": 250.0,
                "dendrite_nav_density": 8.0,
                "soma_kv_density": 40.0,
                "ais_kv_density": 120.0,
                "dendrite_kv_density": 8.0,
                "dendrite_ca_density": 0.3,
                "dendrite_h_density": 0.05,
                "reference": "Katona et al., J Neurosci (1999)",
                "typical_regions": ["hippocampus", "cortex"],
            },
            "chandelier_cell": {
                "description": "Axo-axonic chandelier cell",
                "soma_diameter": 10.0,
                "soma_length": 10.0,
                "dendrite_segments": 5,
                "dendrite_length_total": 150.0,
                "dendrite_diameter_proximal": 1.5,
                "dendrite_diameter_distal": 0.3,
                "axon_length": 300.0,
                "ais_length": 20.0,
                "dendrite_branching": False,
                "branch_points": 1,
                "soma_nav_density": 80.0,
                "ais_nav_density": 300.0,
                "dendrite_nav_density": 3.0,
                "soma_kv_density": 60.0,
                "ais_kv_density": 150.0,
                "dendrite_kv_density": 5.0,
                "dendrite_ca_density": 0.05,
                "dendrite_h_density": 0.0,
                "reference": "Inan & Anderson, Front Neural Circuits (2014)",
                "typical_regions": ["cortex", "hippocampus"],
            },
            "CA1_pyramidal": {
                "description": "Hippocampal CA1 pyramidal neuron",
                "soma_diameter": 18.0,
                "soma_length": 20.0,
                "dendrite_segments": 20,
                "dendrite_length_total": 1200.0,
                "dendrite_diameter_proximal": 5.0,
                "dendrite_diameter_distal": 0.5,
                "axon_length": 300.0,
                "ais_length": 35.0,
                "dendrite_branching": True,
                "branch_points": 4,
                "soma_nav_density": 30.0,
                "ais_nav_density": 150.0,
                "dendrite_nav_density": 20.0,  # Active dendrites
                "soma_kv_density": 20.0,
                "ais_kv_density": 60.0,
                "dendrite_kv_density": 15.0,
                "dendrite_ca_density": 2.0,  # Strong Ca dynamics
                "dendrite_h_density": 0.5,  # HCN channels for theta
                "reference": "Migliore et al., J Neurophysiol (1999)",
                "typical_regions": ["hippocampus"],
            },
            "purkinje_cell": {
                "description": "Cerebellar Purkinje cell",
                "soma_diameter": 25.0,
                "soma_length": 25.0,
                "dendrite_segments": 50,
                "dendrite_length_total": 3000.0,  # Massive dendritic tree
                "dendrite_diameter_proximal": 8.0,
                "dendrite_diameter_distal": 0.2,
                "axon_length": 500.0,
                "ais_length": 40.0,
                "dendrite_branching": True,
                "branch_points": 8,
                "soma_nav_density": 40.0,
                "ais_nav_density": 200.0,
                "dendrite_nav_density": 5.0,
                "soma_kv_density": 100.0,  # Complex K+ channels
                "ais_kv_density": 200.0,
                "dendrite_kv_density": 50.0,
                "dendrite_ca_density": 5.0,  # Very high Ca channel density
                "dendrite_h_density": 0.1,
                "reference": "De Schutter & Bower, J Neurophysiol (1994)",
                "typical_regions": ["cerebellum"],
            },
        }

    def _initialize_morphology_presets(self) -> Dict:
        """Initialize morphological scaling factors for different species and ages."""
        return {
            "species_scaling": {
                "mouse": {
                    "soma_scale": 0.8,
                    "dendrite_scale": 0.7,
                    "axon_scale": 0.6,
                    "description": "Mouse-specific scaling from rat parameters",
                },
                "rat": {
                    "soma_scale": 1.0,
                    "dendrite_scale": 1.0,
                    "axon_scale": 1.0,
                    "description": "Reference species (no scaling)",
                },
                "human": {
                    "soma_scale": 1.5,
                    "dendrite_scale": 2.0,
                    "axon_scale": 3.0,
                    "description": "Human scaling based on comparative studies",
                },
                "cat": {
                    "soma_scale": 1.2,
                    "dendrite_scale": 1.3,
                    "axon_scale": 1.8,
                    "description": "Cat scaling from comparative data",
                },
                "monkey": {
                    "soma_scale": 1.3,
                    "dendrite_scale": 1.6,
                    "axon_scale": 2.2,
                    "description": "Non-human primate scaling",
                },
            },
            "developmental_scaling": {
                "embryonic": {
                    "soma_scale": 0.3,
                    "dendrite_scale": 0.1,
                    "axon_scale": 0.05,
                    "channel_scale": 0.2,
                    "description": "Embryonic stage (minimal dendrites)",
                },
                "neonatal": {
                    "soma_scale": 0.5,
                    "dendrite_scale": 0.3,
                    "axon_scale": 0.2,
                    "channel_scale": 0.4,
                    "description": "Neonatal stage (developing dendrites)",
                },
                "juvenile": {
                    "soma_scale": 0.8,
                    "dendrite_scale": 0.7,
                    "axon_scale": 0.6,
                    "channel_scale": 0.8,
                    "description": "Juvenile stage (growing dendrites)",
                },
                "adult": {
                    "soma_scale": 1.0,
                    "dendrite_scale": 1.0,
                    "axon_scale": 1.0,
                    "channel_scale": 1.0,
                    "description": "Adult stage (fully mature)",
                },
                "aged": {
                    "soma_scale": 0.9,
                    "dendrite_scale": 0.8,
                    "axon_scale": 0.9,
                    "channel_scale": 0.7,
                    "description": "Aged stage (some regression)",
                },
            },
            "brain_region_modifications": {
                "cortex": {
                    "dendrite_complexity": 1.0,
                    "axon_complexity": 1.0,
                    "description": "Standard cortical parameters",
                },
                "hippocampus": {
                    "dendrite_complexity": 1.2,
                    "axon_complexity": 0.8,
                    "description": "Enhanced dendritic integration",
                },
                "cerebellum": {
                    "dendrite_complexity": 2.0,
                    "axon_complexity": 1.5,
                    "description": "Highly complex morphology",
                },
                "thalamus": {
                    "dendrite_complexity": 0.7,
                    "axon_complexity": 1.2,
                    "description": "Relay neuron characteristics",
                },
                "brainstem": {
                    "dendrite_complexity": 0.6,
                    "axon_complexity": 1.8,
                    "description": "Motor neuron characteristics",
                },
            },
        }

    def _initialize_validation_rules(self) -> Dict:
        """Initialize parameter validation rules."""
        return {
            "morphology_constraints": {
                "soma_diameter_range": (5.0, 50.0),
                "dendrite_length_range": (50.0, 5000.0),
                "axon_length_range": (10.0, 10000.0),
                "diameter_taper_ratio": (0.1, 1.0),
                "segment_length_max": 50.0,
            },
            "electrical_constraints": {
                "rm_range": (1000.0, 1000000.0),
                "ra_range": (50.0, 2000.0),
                "cm_range": (0.1, 20.0),
                "channel_density_max": 1000.0,
            },
            "coupling_constraints": {
                "conductance_range": (1e-12, 1e-3),
                "space_constant_min": 50.0,
            },
        }

    def validate_parameters(self, params: Dict) -> Tuple[bool, List[str]]:
        """
        Validate multi-compartment parameters.

        Args:
            params: Dictionary of parameters to validate

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []

        if not params.get("enabled", False):
            return True, []

        # Check basic morphology
        soma_diameter = params.get("soma_diameter", 20.0)
        dendrite_length = params.get("dendrite_length_total", 200.0)

        if soma_diameter < 5.0:
            warnings.append("Soma diameter very small - may cause numerical issues")
        elif soma_diameter > 50.0:
            warnings.append("Soma diameter very large - unusual for most cell types")

        if dendrite_length < 50.0:
            warnings.append("Very short dendrites - limited integration capability")
        elif dendrite_length > 2000.0:
            warnings.append("Very long dendrites - check if appropriate for cell type")

        # Check diameter tapering
        if params.get("dendrite_taper", True):
            prox_diam = params.get("dendrite_diameter_proximal", 3.0)
            dist_diam = params.get("dendrite_diameter_distal", 0.5)
            taper_ratio = dist_diam / prox_diam

            if taper_ratio > 0.8:
                warnings.append("Minimal dendritic tapering - dendrites may be too uniform")
            elif taper_ratio < 0.1:
                warnings.append("Extreme dendritic tapering - check distal diameter")

        # Check compartment numbers
        num_compartments = params.get("num_compartments", 3)
        dendrite_segments = params.get("dendrite_segments", 10)

        if num_compartments < dendrite_segments + 1:
            warnings.append("Total compartments less than dendritic segments - check configuration")

        if num_compartments > 100:
            warnings.append("Very high compartment number - simulation may be slow")

        # Check electrical parameters
        rm_soma = params.get("soma_rm", 10000.0)
        rm_dend = params.get("dendrite_rm", 20000.0)

        if rm_soma < 1000.0:
            warnings.append("Very low soma membrane resistance - check leak conductance")
        elif rm_soma > 100000.0:
            warnings.append("Very high soma membrane resistance - unusual for active cells")

        if rm_dend < rm_soma * 0.5:
            warnings.append("Dendritic Rm much lower than soma - check if intentional")

        # Check ion channel densities
        if params.get("channel_distribution", True):
            nav_soma = params.get("soma_nav_density", 50.0)
            nav_ais = params.get("ais_nav_density", 200.0)
            nav_dend = params.get("dendrite_nav_density", 10.0)

            if nav_ais < nav_soma:
                warnings.append(
                    "AIS Nav density lower than soma - spike initiation may be compromised"
                )

            if nav_dend > nav_soma:
                warnings.append("High dendritic Nav density - check for backpropagating spikes")

            if nav_ais > 500.0:
                warnings.append("Very high AIS Nav density - may cause numerical instability")

        # Check axon configuration
        if params.get("include_axon", True):
            axon_length = params.get("axon_length", 100.0)
            ais_length = params.get("ais_length", 25.0)

            if ais_length > axon_length * 0.5:
                warnings.append("AIS length large fraction of total axon - check proportions")

            if axon_length < 20.0:
                warnings.append("Very short axon - may not capture spike propagation")

        # Check cable properties
        if params.get("cable_equation", True):
            discretization = params.get("spatial_discretization", 10.0)

            if discretization > 25.0:
                warnings.append("Large spatial discretization - may miss important dynamics")
            elif discretization < 2.0:
                warnings.append("Very fine discretization - simulation may be very slow")

        # Check temperature effects
        temperature = params.get("temperature", 37.0)
        if temperature < 25.0 or temperature > 40.0:
            warnings.append("Unusual temperature - check Q10 corrections")

        return len(warnings) == 0, warnings

    def suggest_parameters(self, cell_type: str, brain_region: str, species: str, age: str) -> Dict:
        """
        Suggest parameters based on cell type, brain region, species, and age.

        Args:
            cell_type: Type of neuron
            brain_region: Brain region
            species: Species
            age: Developmental stage

        Returns:
            Dictionary of suggested parameters
        """
        # Start with cell type base parameters
        base_params = self.cell_type_parameters.get(cell_type, {})
        if not base_params:
            # Default to L5 pyramidal if unknown type
            base_params = self.cell_type_parameters["L5_pyramidal"].copy()
        else:
            base_params = base_params.copy()

        # Apply species scaling
        species_scaling = self.morphology_presets["species_scaling"].get(
            species, self.morphology_presets["species_scaling"]["rat"]
        )

        if "soma_diameter" in base_params:
            base_params["soma_diameter"] *= species_scaling["soma_scale"]
            base_params["soma_length"] *= species_scaling["soma_scale"]
            base_params["dendrite_length_total"] *= species_scaling["dendrite_scale"]
            base_params["axon_length"] *= species_scaling["axon_scale"]

        # Apply developmental scaling
        dev_scaling = self.morphology_presets["developmental_scaling"].get(
            age, self.morphology_presets["developmental_scaling"]["adult"]
        )

        if "soma_diameter" in base_params:
            base_params["soma_diameter"] *= dev_scaling["soma_scale"]
            base_params["dendrite_length_total"] *= dev_scaling["dendrite_scale"]
            base_params["axon_length"] *= dev_scaling["axon_scale"]

            # Scale channel densities
            for channel_param in [
                "soma_nav_density",
                "ais_nav_density",
                "dendrite_nav_density",
                "soma_kv_density",
                "ais_kv_density",
                "dendrite_kv_density",
            ]:
                if channel_param in base_params:
                    base_params[channel_param] *= dev_scaling["channel_scale"]

        # Apply brain region modifications
        region_mods = self.morphology_presets["brain_region_modifications"].get(brain_region, {})
        if "dendrite_complexity" in region_mods:
            if "dendrite_segments" in base_params:
                base_params["dendrite_segments"] = int(
                    base_params["dendrite_segments"] * region_mods["dendrite_complexity"]
                )
            if "branch_points" in base_params:
                base_params["branch_points"] = max(
                    1, int(base_params["branch_points"] * region_mods["dendrite_complexity"])
                )

        return base_params

    def calculate_electrical_properties(self, params: Dict) -> Dict:
        """
        Calculate derived electrical properties from morphological parameters.

        Args:
            params: Morphological and electrical parameters

        Returns:
            Dictionary of calculated properties
        """
        import math

        # Calculate soma surface area and capacitance
        soma_diameter = params.get("soma_diameter", 20.0) * 1e-6  # Convert to meters
        soma_length = params.get("soma_length", 20.0) * 1e-6
        soma_area = math.pi * soma_diameter * soma_length  # m²
        soma_area_cm2 = soma_area * 1e4  # Convert to cm²

        soma_cm_specific = params.get("soma_cm", 1.0)  # μF/cm²
        soma_capacitance = soma_area_cm2 * soma_cm_specific * 1e-6  # Convert to F

        # Calculate total dendritic area
        params.get("dendrite_segments", 10)
        dend_length_total = params.get("dendrite_length_total", 200.0) * 1e-6  # Convert to meters
        dend_diam_prox = params.get("dendrite_diameter_proximal", 3.0) * 1e-6
        dend_diam_dist = params.get("dendrite_diameter_distal", 0.5) * 1e-6

        # Approximate dendritic area with tapering
        dend_diam_avg = (dend_diam_prox + dend_diam_dist) / 2
        dend_area = math.pi * dend_diam_avg * dend_length_total  # m²
        dend_area_cm2 = dend_area * 1e4  # Convert to cm²

        dend_cm_specific = params.get("dendrite_cm", 1.0)  # μF/cm²
        dend_capacitance = dend_area_cm2 * dend_cm_specific * 1e-6  # Convert to F

        # Calculate axon properties if included
        axon_area_cm2 = 0
        axon_capacitance = 0
        if params.get("include_axon", True):
            axon_diameter = params.get("axon_diameter", 1.0) * 1e-6  # Convert to meters
            axon_length = params.get("axon_length", 100.0) * 1e-6
            axon_area = math.pi * axon_diameter * axon_length  # m²
            axon_area_cm2 = axon_area * 1e4  # Convert to cm²

            axon_cm_specific = params.get("axon_cm", 1.0)  # μF/cm²
            axon_capacitance = axon_area_cm2 * axon_cm_specific * 1e-6  # Convert to F

        # Calculate total cell properties
        total_area_cm2 = soma_area_cm2 + dend_area_cm2 + axon_area_cm2
        total_capacitance = soma_capacitance + dend_capacitance + axon_capacitance

        # Calculate space constants (approximate)
        soma_rm = params.get("soma_rm", 10000.0)  # Ω·cm²
        soma_ra = params.get("soma_ra", 150.0)  # Ω·cm

        # Space constant = sqrt(rm * d / (4 * ra)) where d is diameter
        soma_lambda = math.sqrt(soma_rm * soma_diameter * 100 / (4 * soma_ra))  # cm

        dend_rm = params.get("dendrite_rm", 20000.0)  # Ω·cm²
        dend_ra = params.get("dendrite_ra", 200.0)  # Ω·cm
        dend_lambda = math.sqrt(dend_rm * dend_diam_avg * 100 / (4 * dend_ra))  # cm

        return {
            "soma_area_cm2": soma_area_cm2,
            "dendrite_area_cm2": dend_area_cm2,
            "axon_area_cm2": axon_area_cm2,
            "total_area_cm2": total_area_cm2,
            "soma_capacitance_pF": soma_capacitance * 1e12,
            "dendrite_capacitance_pF": dend_capacitance * 1e12,
            "axon_capacitance_pF": axon_capacitance * 1e12,
            "total_capacitance_pF": total_capacitance * 1e12,
            "soma_space_constant_um": soma_lambda * 1e4,
            "dendrite_space_constant_um": dend_lambda * 1e4,
            "input_resistance_estimate_MOhm": soma_rm / soma_area_cm2 / 1e6,  # Rough estimate
        }

    def validate_morphology_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate morphology file format and contents.

        Args:
            file_path: Path to morphology file

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(file_path):
            return False, "File does not exist"

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".swc":
            return self._validate_swc_file(file_path)
        elif file_ext == ".hoc":
            return self._validate_hoc_file(file_path)
        elif file_ext == ".asc":
            return self._validate_asc_file(file_path)
        else:
            return False, f"Unsupported file format: {file_ext}"

    def _validate_swc_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate SWC morphology file."""
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()

            data_lines = [
                line for line in lines if not line.strip().startswith("#") and line.strip()
            ]

            if len(data_lines) < 2:
                return False, "SWC file has too few data points"

            # Check format of first data line
            first_line = data_lines[0].strip().split()
            if len(first_line) != 7:
                return False, "SWC format error: expected 7 columns per line"

            # Check if we have soma (type 1)
            has_soma = any("1" in line.split()[1] for line in data_lines if len(line.split()) >= 2)
            if not has_soma:
                return False, "SWC file missing soma compartment (type 1)"

            return True, "Valid SWC file"

        except Exception as e:
            return False, f"Error reading SWC file: {str(e)}"

    def _validate_hoc_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate HOC morphology file."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Basic checks for HOC file
            if "create" not in content and "soma" not in content:
                return False, "HOC file does not appear to contain morphology data"

            return True, "Valid HOC file (basic check)"

        except Exception as e:
            return False, f"Error reading HOC file: {str(e)}"

    def _validate_asc_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate ASC morphology file."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Basic checks for ASC file
            if "(" not in content or ")" not in content:
                return False, "ASC file does not appear to contain valid morphology data"

            return True, "Valid ASC file (basic check)"

        except Exception as e:
            return False, f"Error reading ASC file: {str(e)}"

    def generate_morphology_summary(self, params: Dict) -> str:
        """Generate a summary of the morphological configuration."""
        if not params.get("enabled", False):
            return "Multi-compartment modeling disabled"

        summary = []
        summary.append(f"Multi-compartment model: {params.get('model_type', 'ball_and_stick')}")
        summary.append(f"Total compartments: {params.get('num_compartments', 3)}")

        # Soma info
        soma_diam = params.get("soma_diameter", 20.0)
        soma_len = params.get("soma_length", 20.0)
        summary.append(f"Soma: {soma_diam} × {soma_len} μm")

        # Dendrite info
        dend_segs = params.get("dendrite_segments", 10)
        dend_len = params.get("dendrite_length_total", 200.0)
        summary.append(f"Dendrites: {dend_segs} segments, {dend_len} μm total length")

        # Axon info
        if params.get("include_axon", True):
            axon_len = params.get("axon_length", 100.0)
            ais_len = params.get("ais_length", 25.0)
            summary.append(f"Axon: {axon_len} μm (AIS: {ais_len} μm)")

        # Channel distribution
        if params.get("channel_distribution", True):
            nav_ais = params.get("ais_nav_density", 200.0)
            summary.append(f"AIS Nav density: {nav_ais} mS/cm²")

        # Calculate some properties
        calc_props = self.calculate_electrical_properties(params)
        summary.append(f"Total capacitance: {calc_props['total_capacitance_pF']:.1f} pF")
        summary.append(
            f"Estimated input resistance: {calc_props['input_resistance_estimate_MOhm']:.1f} MΩ"
        )

        return "\n".join(summary)

    def export_parameters_for_brian2(self, params: Dict) -> str:
        """Export parameters as Brian2-compatible code for multi-compartment modeling."""
        if not params.get("enabled", False):
            return "# Multi-compartment modeling disabled"

        code_lines = [
            "# Multi-compartment neuron parameters",
            "from brian2 import *",
            "from brian2.spatialsubunits import *",
            "",
            "# Morphology parameters",
        ]

        # Morphological parameters
        code_lines.extend(
            [
                f"soma_diameter = {params.get('soma_diameter', 20.0)} * umeter",
                f"soma_length = {params.get('soma_length', 20.0)} * umeter",
                f"dendrite_segments = {params.get('dendrite_segments', 10)}",
                f"dendrite_length_total = {params.get('dendrite_length_total', 200.0)} * umeter",
                f"axon_length = {params.get('axon_length', 100.0)} * umeter",
                "",
            ]
        )

        # Electrical parameters
        code_lines.extend(
            [
                "# Electrical parameters",
                f"soma_Cm = {params.get('soma_cm', 1.0)} * uF / cm**2",
                f"soma_Rm = {params.get('soma_rm', 10000.0)} * ohm * cm**2",
                f"soma_Ra = {params.get('soma_ra', 150.0)} * ohm * cm",
                f"dendrite_Cm = {params.get('dendrite_cm', 1.0)} * uF / cm**2",
                f"dendrite_Rm = {params.get('dendrite_rm', 20000.0)} * ohm * cm**2",
                f"dendrite_Ra = {params.get('dendrite_ra', 200.0)} * ohm * cm",
                "",
            ]
        )

        # Ion channel densities
        if params.get("channel_distribution", True):
            code_lines.extend(
                [
                    "# Ion channel densities",
                    f"soma_gNa = {params.get('soma_nav_density', 50.0)} * mS / cm**2",
                    f"ais_gNa = {params.get('ais_nav_density', 200.0)} * mS / cm**2",
                    f"dendrite_gNa = {params.get('dendrite_nav_density', 10.0)} * mS / cm**2",
                    f"soma_gK = {params.get('soma_kv_density', 30.0)} * mS / cm**2",
                    f"ais_gK = {params.get('ais_kv_density', 100.0)} * mS / cm**2",
                    f"dendrite_gK = {params.get('dendrite_kv_density', 5.0)} * mS / cm**2",
                    "",
                ]
            )

        # Temperature correction
        code_lines.extend(
            [
                "# Temperature correction",
                f"temperature = {params.get('temperature', 37.0)}",
                f"q10_Na = {params.get('q10_nav', 3.0)}",
                f"q10_K = {params.get('q10_kv', 2.5)}",
                "temp_factor_Na = q10_Na ** ((temperature - 23) / 10)",
                "temp_factor_K = q10_K ** ((temperature - 23) / 10)",
                "",
            ]
        )

        return "\n".join(code_lines)

    def reset_to_defaults(self):
        """Reset multicompartment to their default values."""
        if hasattr(self.main_window, "multicompartment_form_generator"):
            self.main_window.multicompartment_form_generator.reset_to_defaults()
