# homeostatic_plasticity_manager.py
# Manager for homeostatic plasticity configuration with research-based validation

from typing import Dict, List, Tuple

from PyQt6.QtCore import QObject, pyqtSignal


class HomeostaticPlasticityManager(QObject):
    """Manager for homeostatic plasticity parameters with validation and research-based suggestions."""

    param_changed = pyqtSignal()  # Signal emitted when any parameter changes

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.parameter_combinations = self._initialize_parameter_combinations()
        self.research_presets = self._initialize_research_presets()

    def connect_signals(self):
        """Connect UI signals to handle parameter changes"""
        # Get all widgets from the form generator
        if hasattr(self.main_window, "homeostatic_plasticity_form_generator"):
            param_widgets = (
                self.main_window.homeostatic_plasticity_form_generator.get_param_widgets()
            )
            for param_key, widget in param_widgets.items():
                if hasattr(widget, "valueChanged"):
                    widget.valueChanged.connect(self.on_param_changed)
                elif hasattr(widget, "currentIndexChanged"):
                    widget.currentIndexChanged.connect(self.on_param_changed)
                elif hasattr(widget, "stateChanged"):
                    widget.stateChanged.connect(self.on_param_changed)

    def on_param_changed(self):
        """Called when any homeostatic plasticity parameter changes"""
        self.param_changed.emit()

    def get_parameters(self):
        """Get current homeostatic plasticity parameters from UI."""
        if hasattr(self.main_window, "homeostatic_plasticity_form_generator"):
            return self.main_window.homeostatic_plasticity_form_generator.get_params_for_save()
        return {}

    def _initialize_parameter_combinations(self) -> Dict:
        """Initialize validated parameter combinations for different experimental contexts."""
        return {
            "cortical_culture": {
                "target_firing_rate": 2.5,  # Hz, typical for cortical cultures
                "scaling_rate": 0.01,  # Slow scaling for stable cultures
                "threshold_rate": 0.001,  # Very slow threshold adaptation
                "bcm_tau": 10000,  # Long time constant for stable learning
                "network_target_rate": 5.0,  # Network average
                "dysfunction_severity": 0.0,
                "reference": "Turrigiano & Nelson, Nat Rev Neurosci (2004)",
            },
            "acute_slice": {
                "target_firing_rate": 1.0,  # Lower for slice preparations
                "scaling_rate": 0.005,  # Slower scaling in acute preparations
                "threshold_rate": 0.0005,  # Minimal threshold adaptation
                "bcm_tau": 5000,  # Shorter for acute experiments
                "network_target_rate": 2.0,
                "dysfunction_severity": 0.0,
                "reference": "Desai et al., Neuron (1999)",
            },
            "in_vivo_normal": {
                "target_firing_rate": 5.0,  # Higher for in vivo conditions
                "scaling_rate": 0.02,  # Faster adaptation in vivo
                "threshold_rate": 0.002,  # More dynamic threshold adaptation
                "bcm_tau": 15000,  # Longer for complex in vivo dynamics
                "network_target_rate": 8.0,
                "dysfunction_severity": 0.0,
                "reference": "Hengen et al., Cell (2013)",
            },
            "epilepsy_model": {
                "target_firing_rate": 15.0,  # Elevated in epilepsy
                "scaling_rate": 0.001,  # Impaired scaling
                "threshold_rate": -0.001,  # Reversed threshold adaptation
                "bcm_tau": 5000,  # Disrupted metaplasticity
                "network_target_rate": 20.0,
                "dysfunction_severity": 0.7,
                "reference": "Turrigiano, Annu Rev Neurosci (2012)",
            },
            "autism_model": {
                "target_firing_rate": 8.0,  # Altered E/I balance
                "scaling_rate": 0.005,  # Reduced scaling efficiency
                "threshold_rate": 0.0001,  # Impaired threshold adaptation
                "bcm_tau": 20000,  # Altered metaplasticity
                "network_target_rate": 12.0,
                "dysfunction_severity": 0.4,
                "reference": "Nelson & Valakh, Curr Opin Neurobiol (2015)",
            },
            "alzheimer_model": {
                "target_firing_rate": 1.5,  # Reduced activity
                "scaling_rate": 0.002,  # Severely impaired scaling
                "threshold_rate": 0.0,  # Lost threshold adaptation
                "bcm_tau": 30000,  # Prolonged time constants
                "network_target_rate": 3.0,
                "dysfunction_severity": 0.8,
                "reference": "Palop & Mucke, Nat Neurosci (2016)",
            },
            "development_early": {
                "target_firing_rate": 10.0,  # High activity during development
                "scaling_rate": 0.05,  # Rapid scaling during critical periods
                "threshold_rate": 0.005,  # Dynamic threshold changes
                "bcm_tau": 8000,  # Faster metaplasticity
                "network_target_rate": 15.0,
                "dysfunction_severity": 0.0,
                "reference": "Turrigiano, Curr Opin Neurobiol (2017)",
            },
            "sensory_deprivation": {
                "target_firing_rate": 0.5,  # Very low due to deprivation
                "scaling_rate": 0.03,  # Compensatory upscaling
                "threshold_rate": -0.001,  # Threshold reduction
                "bcm_tau": 12000,  # Modified metaplasticity
                "network_target_rate": 1.0,
                "dysfunction_severity": 0.2,
                "reference": "Maffei & Turrigiano, PLoS Biol (2008)",
            },
        }

    def _initialize_research_presets(self) -> Dict:
        """Initialize research-validated parameter presets for different mechanisms."""
        return {
            "synaptic_scaling_classic": {
                "synaptic_scaling": True,
                "scaling_rate": 0.01,
                "min_weight_scaling": 0.1,
                "max_weight_scaling": 10.0,
                "target_firing_rate": 2.0,
                "target_window": 86400,  # 24 hours
                "description": "Classic multiplicative synaptic scaling (Turrigiano et al.)",
                "reference": "Turrigiano et al., Nature (1998)",
            },
            "bcm_plasticity_standard": {
                "bcm_plasticity": True,
                "bcm_tau": 10000,
                "bcm_power": 2,
                "metaplasticity": True,
                "metaplasticity_threshold": 1.0,
                "description": "BCM rule with sliding threshold",
                "reference": "Bienenstock et al., J Neurosci (1982)",
            },
            "intrinsic_homeostasis": {
                "intrinsic_regulation": True,
                "excitability_target": 2.5,
                "threshold_adaptation": True,
                "threshold_rate": 0.001,
                "min_threshold": -60.0,
                "max_threshold": -45.0,
                "description": "Intrinsic excitability homeostasis",
                "reference": "Desai et al., Nat Neurosci (1999)",
            },
            "network_homeostasis": {
                "network_regulation": True,
                "network_target_rate": 5.0,
                "global_scaling": True,
                "inhibitory_gain_control": True,
                "inhibitory_scaling_rate": 0.005,
                "description": "Network-level homeostatic regulation",
                "reference": "Vogels et al., Science (2011)",
            },
            "calcium_homeostasis": {
                "calcium_homeostasis": True,
                "calcium_target": 100.0,  # nM
                "calcium_regulation_rate": 0.1,
                "activity_detection": True,
                "detection_window": 3600,  # 1 hour
                "description": "Calcium-based activity sensing",
                "reference": "Ibata et al., Neuron (2008)",
            },
        }

    def validate_parameters(self, params: Dict) -> Tuple[bool, List[str]]:
        """
        Validate homeostatic plasticity parameters.

        Args:
            params: Dictionary of parameters to validate

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []

        if not params.get("enabled", False):
            return True, []

        # Check target firing rate
        target_rate = params.get("target_firing_rate", 2.0)
        if target_rate < 0.1:
            warnings.append("Target firing rate very low - may cause instability")
        elif target_rate > 20.0:
            warnings.append("Target firing rate very high - typical for pathological conditions")

        # Check scaling parameters
        if params.get("synaptic_scaling", False):
            scaling_rate = params.get("scaling_rate", 0.01)
            if scaling_rate > 0.1:
                warnings.append("Scaling rate very high - may cause oscillations")
            elif scaling_rate < 0.001:
                warnings.append("Scaling rate very low - homeostasis may be too slow")

            min_scaling = params.get("min_weight_scaling", 0.1)
            max_scaling = params.get("max_weight_scaling", 10.0)
            if max_scaling / min_scaling > 1000:
                warnings.append("Very large scaling range - may cause extreme weight changes")

        # Check threshold adaptation
        if params.get("threshold_adaptation", False):
            threshold_rate = params.get("threshold_rate", 0.001)
            min_thresh = params.get("min_threshold", -60.0)
            max_thresh = params.get("max_threshold", -45.0)

            if threshold_rate > 0.01:
                warnings.append("Threshold adaptation rate high - may cause instability")
            if max_thresh - min_thresh < 5.0:
                warnings.append("Small threshold range - limited adaptation capability")

        # Check BCM parameters
        if params.get("bcm_plasticity", False):
            bcm_tau = params.get("bcm_tau", 10000)
            if bcm_tau < 1000:
                warnings.append("BCM tau very short - may cause rapid threshold changes")
            elif bcm_tau > 100000:
                warnings.append("BCM tau very long - threshold may not adapt effectively")

        # Check network regulation
        if params.get("network_regulation", False):
            network_rate = params.get("network_target_rate", 5.0)
            if network_rate > target_rate * 3:
                warnings.append(
                    "Network target much higher than cellular target - check consistency"
                )

        # Check disease state consistency
        dysfunction_severity = params.get("dysfunction_severity", 0.0)
        if dysfunction_severity > 0.5:
            if params.get("scaling_rate", 0.01) > 0.02:
                warnings.append("High dysfunction severity with fast scaling - may be unrealistic")

        # Check calcium homeostasis
        if params.get("calcium_homeostasis", False):
            ca_target = params.get("calcium_target", 100.0)
            if ca_target < 50.0 or ca_target > 500.0:
                warnings.append("Calcium target outside typical range (50-500 nM)")

        return len(warnings) == 0, warnings

    def suggest_parameters(self, context: str, cell_type: str = "pyramidal") -> Dict:
        """
        Suggest parameters based on experimental context and cell type.

        Args:
            context: Experimental context ('culture', 'slice', 'in_vivo', 'disease')
            cell_type: Type of neuron ('pyramidal', 'interneuron', 'granule')

        Returns:
            Dictionary of suggested parameters
        """
        base_params = self.parameter_combinations.get(
            f"{context}_normal", self.parameter_combinations["cortical_culture"]
        )

        # Adjust for cell type
        if cell_type == "interneuron":
            base_params = base_params.copy()
            base_params["target_firing_rate"] *= 2.0  # Interneurons fire faster
            base_params["scaling_rate"] *= 0.5  # More stable
            base_params["threshold_rate"] *= 1.5  # More dynamic
        elif cell_type == "granule":
            base_params = base_params.copy()
            base_params["target_firing_rate"] *= 0.3  # Sparse coding
            base_params["scaling_rate"] *= 2.0  # More plastic
            base_params["bcm_tau"] *= 0.7  # Faster metaplasticity

        return base_params

    def get_disease_modifications(self, disease_type: str) -> Dict:
        """Get parameter modifications for specific disease models."""
        disease_mods = {
            "epilepsy": {
                "scaling_rate": 0.001,  # Impaired
                "threshold_rate": -0.001,  # Reversed
                "dysfunction_severity": 0.7,
                "network_target_rate": 15.0,
            },
            "autism": {
                "scaling_rate": 0.005,  # Reduced
                "inhibitory_scaling_rate": 0.001,  # Severely impaired
                "dysfunction_severity": 0.4,
                "network_target_rate": 10.0,
            },
            "alzheimer": {
                "scaling_rate": 0.002,  # Severely impaired
                "threshold_rate": 0.0,  # Lost
                "dysfunction_severity": 0.8,
                "bcm_tau": 30000,  # Prolonged
            },
            "depression": {
                "scaling_rate": 0.003,  # Reduced
                "target_firing_rate": 1.0,  # Hypoactivity
                "dysfunction_severity": 0.5,
                "network_target_rate": 2.0,
            },
        }

        return disease_mods.get(disease_type, {})

    def get_experimental_protocols(self) -> Dict:
        """Get protocols for testing homeostatic plasticity."""
        return {
            "activity_blockade": {
                "description": "Block activity with TTX to trigger scaling",
                "duration": 24,  # hours
                "expected_change": "Multiplicative synaptic upscaling",
                "reference": "Turrigiano et al., Nature (1998)",
            },
            "activity_enhancement": {
                "description": "Enhance activity with bicuculline",
                "duration": 6,  # hours
                "expected_change": "Synaptic downscaling",
                "reference": "Turrigiano & Nelson, Nat Rev Neurosci (2004)",
            },
            "sensory_deprivation": {
                "description": "Monocular deprivation in visual cortex",
                "duration": 48,  # hours
                "expected_change": "Homeostatic scaling of deprived inputs",
                "reference": "Maffei & Turrigiano, PLoS Biol (2008)",
            },
            "chronic_silencing": {
                "description": "Chronic activity reduction",
                "duration": 168,  # 1 week
                "expected_change": "Intrinsic excitability increase",
                "reference": "Desai et al., Nat Neurosci (1999)",
            },
        }

    def calculate_time_constants(self, experimental_duration: float) -> Dict:
        """
        Calculate appropriate time constants for given experimental duration.

        Args:
            experimental_duration: Duration in hours

        Returns:
            Dictionary of suggested time constants
        """
        # Rule of thumb: homeostatic mechanisms should act over 1/10 to 1/2 of experiment duration
        duration_seconds = experimental_duration * 3600

        return {
            "target_window": min(duration_seconds / 4, 86400),  # Max 24 hours
            "bcm_tau": duration_seconds / 8,
            "detection_window": max(duration_seconds / 20, 3600),  # Min 1 hour
            "smoothing_tau": duration_seconds / 100,
        }

    def get_physiological_ranges(self) -> Dict:
        """Get physiologically realistic parameter ranges."""
        return {
            "target_firing_rate": {
                "min": 0.1,
                "max": 50.0,
                "unit": "Hz",
                "typical": (1.0, 10.0),
                "note": "Varies by cell type and brain region",
            },
            "scaling_rate": {
                "min": 0.0001,
                "max": 0.1,
                "unit": "1/s",
                "typical": (0.001, 0.02),
                "note": "Slow process, hours to days",
            },
            "threshold_rate": {
                "min": -0.01,
                "max": 0.01,
                "unit": "mV/s",
                "typical": (0.0001, 0.002),
                "note": "Can be negative in pathological conditions",
            },
            "bcm_tau": {
                "min": 1000,
                "max": 100000,
                "unit": "s",
                "typical": (5000, 20000),
                "note": "Time constant for sliding threshold",
            },
            "calcium_target": {
                "min": 50,
                "max": 500,
                "unit": "nM",
                "typical": (80, 200),
                "note": "Basal calcium concentration",
            },
        }

    def export_parameters_for_brian2(self, params: Dict) -> str:
        """Export parameters as Brian2-compatible code."""
        if not params.get("enabled", False):
            return "# Homeostatic plasticity disabled"

        code_lines = [
            "# Homeostatic plasticity parameters",
            f"target_rate = {params.get('target_firing_rate', 2.0)} * Hz",
            f"homeostatic_tau = {params.get('target_window', 86400)} * second",
        ]

        if params.get("synaptic_scaling", False):
            code_lines.extend(
                [
                    f"scaling_rate = {params.get('scaling_rate', 0.01)} / second",
                    f"min_weight = {params.get('min_weight_scaling', 0.1)}",
                    f"max_weight = {params.get('max_weight_scaling', 10.0)}",
                ]
            )

        if params.get("threshold_adaptation", False):
            code_lines.extend(
                [
                    f"threshold_rate = {params.get('threshold_rate', 0.001)} * mV / second",
                    f"min_threshold = {params.get('min_threshold', -60.0)} * mV",
                    f"max_threshold = {params.get('max_threshold', -45.0)} * mV",
                ]
            )

        return "\n".join(code_lines)

    def reset_to_defaults(self):
        """Reset homeostatic plasticity to their default values."""
        if hasattr(self.main_window, "homeostatic_plasticity_form_generator"):
            self.main_window.homeostatic_plasticity_form_generator.reset_to_defaults()
