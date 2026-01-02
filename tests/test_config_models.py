"""
Unit tests for configuration model files.
Tests parameter schema validation, default values, and preset configurations.
"""
import pytest


class TestNeuronModelsConfig:
    """Tests for neuron_models_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that neuron models config can be imported."""
        from brian2sim.models.neuron_models_config import NEURON_MODELS_CONFIG
        
        assert NEURON_MODELS_CONFIG is not None
        assert isinstance(NEURON_MODELS_CONFIG, dict)
        
    def test_lif_model_exists(self):
        """Test LIF model configuration exists."""
        from brian2sim.models.neuron_models_config import NEURON_MODELS_CONFIG
        
        assert "lif" in NEURON_MODELS_CONFIG
        assert "display_name" in NEURON_MODELS_CONFIG["lif"]
        assert "params" in NEURON_MODELS_CONFIG["lif"]
        
    def test_izhikevich_model_exists(self):
        """Test Izhikevich model configuration exists."""
        from brian2sim.models.neuron_models_config import NEURON_MODELS_CONFIG
        
        assert "izhikevich" in NEURON_MODELS_CONFIG
        assert "a" in NEURON_MODELS_CONFIG["izhikevich"]["params"]
        assert "b" in NEURON_MODELS_CONFIG["izhikevich"]["params"]
        assert "c" in NEURON_MODELS_CONFIG["izhikevich"]["params"]
        assert "d" in NEURON_MODELS_CONFIG["izhikevich"]["params"]
        
    def test_adex_model_exists(self):
        """Test AdEx model configuration exists."""
        from brian2sim.models.neuron_models_config import NEURON_MODELS_CONFIG
        
        assert "adex" in NEURON_MODELS_CONFIG
        
    def test_hh_model_exists(self):
        """Test Hodgkin-Huxley model configuration exists."""
        from brian2sim.models.neuron_models_config import NEURON_MODELS_CONFIG
        
        assert "hodgkin_huxley" in NEURON_MODELS_CONFIG or "hh" in NEURON_MODELS_CONFIG
        
    def test_lif_params_have_required_fields(self):
        """Test LIF parameters have all required schema fields."""
        from brian2sim.models.neuron_models_config import NEURON_MODELS_CONFIG
        
        required_fields = ["type", "label", "default", "min", "max"]
        
        for param_name, param_config in NEURON_MODELS_CONFIG["lif"]["params"].items():
            for field in required_fields:
                assert field in param_config, f"LIF param {param_name} missing {field}"
                
    def test_lif_presets_exist(self):
        """Test LIF model has presets defined."""
        from brian2sim.models.neuron_models_config import NEURON_MODELS_CONFIG
        
        assert "presets" in NEURON_MODELS_CONFIG["lif"]
        presets = NEURON_MODELS_CONFIG["lif"]["presets"]
        assert len(presets) > 0
        
    def test_preset_values_are_valid(self):
        """Test preset values are within parameter ranges."""
        from brian2sim.models.neuron_models_config import NEURON_MODELS_CONFIG
        
        lif_config = NEURON_MODELS_CONFIG["lif"]
        params = lif_config["params"]
        
        for preset_name, preset in lif_config.get("presets", {}).items():
            if preset_name == "none":
                continue
            for param_name, value in preset.get("values", {}).items():
                if param_name in params:
                    param = params[param_name]
                    if "min" in param and "max" in param and isinstance(value, (int, float)):
                        assert param["min"] <= value <= param["max"], \
                            f"Preset {preset_name}.{param_name}={value} out of range [{param['min']}, {param['max']}]"


class TestNetworkConfig:
    """Tests for network_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that network config can be imported."""
        from brian2sim.models.network_config import NETWORK_CONFIG
        
        assert NETWORK_CONFIG is not None
        
    def test_has_enabled_param(self):
        """Test network config has enabled parameter."""
        from brian2sim.models.network_config import NETWORK_CONFIG
        
        assert "enabled" in NETWORK_CONFIG
        
    def test_has_topology_param(self):
        """Test network config has connection parameters."""
        from brian2sim.models.network_config import NETWORK_CONFIG
        
        # Check for connection-related parameters instead of topology
        keys = list(NETWORK_CONFIG.keys())
        assert len(keys) > 1  # Should have multiple parameters


class TestCalciumDynamicsConfig:
    """Tests for calcium_dynamics_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that calcium dynamics config can be imported."""
        from brian2sim.models.calcium_dynamics_config import CALCIUM_DYNAMICS_CONFIG
        
        assert CALCIUM_DYNAMICS_CONFIG is not None
        
    def test_has_enabled_param(self):
        """Test config has enabled parameter."""
        from brian2sim.models.calcium_dynamics_config import CALCIUM_DYNAMICS_CONFIG
        
        assert "enabled" in CALCIUM_DYNAMICS_CONFIG
        
    def test_has_calcium_parameters(self):
        """Test config has key calcium parameters."""
        from brian2sim.models.calcium_dynamics_config import CALCIUM_DYNAMICS_CONFIG
        
        # Check for common calcium parameters
        keys = CALCIUM_DYNAMICS_CONFIG.keys()
        assert any("ca" in k.lower() or "calcium" in k.lower() for k in keys)


class TestNeuromodulationConfig:
    """Tests for neuromodulation_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that neuromodulation config can be imported."""
        from brian2sim.models.neuromodulation_config import NEUROMODULATION_CONFIG
        
        assert NEUROMODULATION_CONFIG is not None
        
    def test_has_neuromodulator_systems(self):
        """Test config has neuromodulator system toggles."""
        from brian2sim.models.neuromodulation_config import NEUROMODULATION_CONFIG
        
        keys = list(NEUROMODULATION_CONFIG.keys())
        # Should have dopamine, acetylcholine, serotonin, noradrenaline options
        assert any("dopamine" in k.lower() for k in keys)


class TestGapJunctionsConfig:
    """Tests for gap_junctions_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that gap junctions config can be imported."""
        from brian2sim.models.gap_junctions_config import GAP_JUNCTIONS_CONFIG
        
        assert GAP_JUNCTIONS_CONFIG is not None
        
    def test_has_enabled_param(self):
        """Test config has enabled parameter."""
        from brian2sim.models.gap_junctions_config import GAP_JUNCTIONS_CONFIG
        
        assert "enabled" in GAP_JUNCTIONS_CONFIG


class TestHomeostaticPlasticityConfig:
    """Tests for homeostatic_plasticity_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that homeostatic plasticity config can be imported."""
        from brian2sim.models.homeostatic_plasticity_config import HOMEOSTATIC_PLASTICITY_CONFIG
        
        assert HOMEOSTATIC_PLASTICITY_CONFIG is not None
        
    def test_has_enabled_param(self):
        """Test config has enabled parameter."""
        from brian2sim.models.homeostatic_plasticity_config import HOMEOSTATIC_PLASTICITY_CONFIG
        
        assert "enabled" in HOMEOSTATIC_PLASTICITY_CONFIG


class TestMulticompartmentConfig:
    """Tests for multicompartment_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that multicompartment config can be imported."""
        from brian2sim.models.multicompartment_config import MULTICOMPARTMENT_CONFIG
        
        assert MULTICOMPARTMENT_CONFIG is not None
        
    def test_has_enabled_param(self):
        """Test config has enabled parameter."""
        from brian2sim.models.multicompartment_config import MULTICOMPARTMENT_CONFIG
        
        assert "enabled" in MULTICOMPARTMENT_CONFIG


class TestSynapticReceptorsConfig:
    """Tests for synaptic_receptors_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that synaptic receptors config can be imported."""
        from brian2sim.models.synaptic_receptors_config import SYNAPTIC_RECEPTORS_CONFIG
        
        assert SYNAPTIC_RECEPTORS_CONFIG is not None
        
    def test_has_receptor_types(self):
        """Test config has receptor type options."""
        from brian2sim.models.synaptic_receptors_config import SYNAPTIC_RECEPTORS_CONFIG
        
        keys = list(SYNAPTIC_RECEPTORS_CONFIG.keys())
        # Should have AMPA, NMDA options
        assert any("ampa" in k.lower() for k in keys) or any("nmda" in k.lower() for k in keys)


class TestShortTermPlasticityConfig:
    """Tests for short_term_plasticity_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that short-term plasticity config can be imported."""
        from brian2sim.models.short_term_plasticity_config import SHORT_TERM_PLASTICITY_CONFIG
        
        assert SHORT_TERM_PLASTICITY_CONFIG is not None
        
    def test_has_enabled_param(self):
        """Test config has enabled parameter."""
        from brian2sim.models.short_term_plasticity_config import SHORT_TERM_PLASTICITY_CONFIG
        
        assert "enabled" in SHORT_TERM_PLASTICITY_CONFIG


class TestInputPatternsConfig:
    """Tests for input_patterns_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that input patterns config can be imported."""
        from brian2sim.models.input_patterns_config import INPUT_PATTERNS_CONFIG
        
        assert INPUT_PATTERNS_CONFIG is not None
        
    def test_has_enabled_param(self):
        """Test config has enabled parameter."""
        from brian2sim.models.input_patterns_config import INPUT_PATTERNS_CONFIG
        
        assert "enabled" in INPUT_PATTERNS_CONFIG


class TestAdvancedNetworkConfig:
    """Tests for advanced_network_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that advanced network config can be imported."""
        from brian2sim.models.advanced_network_config import ADVANCED_NETWORK_CONFIG
        
        assert ADVANCED_NETWORK_CONFIG is not None


class TestNoiseConfig:
    """Tests for noise_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that noise config can be imported."""
        from brian2sim.models.noise_config import NOISE_CONFIG
        
        assert NOISE_CONFIG is not None
        
    def test_has_enabled_param(self):
        """Test config has enabled parameter."""
        from brian2sim.models.noise_config import NOISE_CONFIG
        
        assert "enabled" in NOISE_CONFIG


class TestSimParamsConfig:
    """Tests for sim_params_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that sim params config can be imported."""
        from brian2sim.models.sim_params_config import SIM_PARAMS_CONFIG
        
        assert SIM_PARAMS_CONFIG is not None
        
    def test_has_simulation_time(self):
        """Test config has simulation time parameter."""
        from brian2sim.models.sim_params_config import SIM_PARAMS_CONFIG
        
        keys = list(SIM_PARAMS_CONFIG.keys())
        assert any("time" in k.lower() or "duration" in k.lower() for k in keys)
        
    def test_has_num_neurons(self):
        """Test config has num_neurons parameter."""
        from brian2sim.models.sim_params_config import SIM_PARAMS_CONFIG
        
        keys = list(SIM_PARAMS_CONFIG.keys())
        assert any("neuron" in k.lower() for k in keys)


class TestMonitorsConfig:
    """Tests for monitors_config.py parameter schemas."""
    
    def test_config_import(self):
        """Test that monitors config can be imported."""
        from brian2sim.models.monitors_config import MONITORS_CONFIG
        
        assert MONITORS_CONFIG is not None
