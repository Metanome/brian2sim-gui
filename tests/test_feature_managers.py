"""
Comprehensive tests for all feature managers.
Tests UI managers for noise, network, advanced features, and parameter handling.
"""
import pytest
from unittest.mock import Mock, MagicMock
from brian2sim.managers.noise_manager import NoiseManager
from brian2sim.managers.network_manager import NetworkManager
from brian2sim.managers.sim_params_manager import SimParamsManager
from brian2sim.managers.neuron_models_manager import NeuronModelsManager


class TestNoiseManager:
    """Tests for NoiseManager."""
    
    def test_manager_creation(self):
        """Test creating NoiseManager."""
        mock_window = Mock()
        manager = NoiseManager(mock_window)
        
        assert manager is not None
        assert manager.main_window == mock_window
        
    def test_get_config_disabled(self):
        """Test getting noise config when disabled."""
        mock_window = Mock()
        mock_window.noise_form_generator = Mock()
        
        mock_checkbox = Mock()
        mock_checkbox.isChecked.return_value = False
        
        mock_window.noise_form_generator.get_param_widgets.return_value = {
            "enabled": mock_checkbox
        }
        
        manager = NoiseManager(mock_window)
        options = manager.get_config()
        
        assert options["enabled"] is False
        
    def test_get_config_enabled(self):
        """Test getting noise config when enabled."""
        mock_window = Mock()
        mock_window.noise_form_generator = Mock()
        
        mock_checkbox = Mock()
        mock_checkbox.isChecked.return_value = True
        
        mock_window.noise_form_generator.get_param_widgets.return_value = {
            "enabled": mock_checkbox
        }
        mock_window.noise_form_generator.get_params_for_save.return_value = {
            "enabled": True,
            "method": "Gaussian",
            "intensity": 0.1
        }
        
        manager = NoiseManager(mock_window)
        options = manager.get_config()
        
        assert options["enabled"] is True
        assert "method" in options
        assert "intensity" in options
        
    def test_load_config(self):
        """Test loading noise config into UI."""
        mock_window = Mock()
        mock_window.noise_form_generator = Mock()
        
        manager = NoiseManager(mock_window)
        
        data = {"enabled": True, "method": "Gaussian", "intensity": 0.2}
        manager.load_config(data)
        
        assert mock_window.noise_form_generator.load_params_from_config.called
        
    def test_apply_preset_values(self):
        """Test applying preset noise values."""
        mock_window = Mock()
        mock_window.noise_form_generator = Mock()
        
        manager = NoiseManager(mock_window)
        
        preset = {
            "enabled": True,
            "intensity": 0.5,
            "method": "Ornstein-Uhlenbeck"
        }
        
        manager.apply_preset_values(preset)
        assert mock_window.noise_form_generator.load_params_from_config.called


class TestNetworkManager:
    """Tests for NetworkManager."""
    
    def test_manager_creation(self):
        """Test creating NetworkManager."""
        mock_window = Mock()
        manager = NetworkManager(mock_window)
        
        assert manager is not None
        assert manager.main_window == mock_window
        
    def test_get_config_disabled(self):
        """Test getting network config when disabled."""
        mock_window = Mock()
        mock_window.network_form_generator = Mock()
        
        mock_checkbox = Mock()
        mock_checkbox.isChecked.return_value = False
        
        mock_window.network_form_generator.get_param_widgets.return_value = {
            "enabled": mock_checkbox
        }
        
        manager = NetworkManager(mock_window)
        options = manager.get_config()
        
        assert options["enabled"] is False
        
    def test_get_config_enabled(self):
        """Test getting network config when enabled."""
        mock_window = Mock()
        mock_window.network_form_generator = Mock()
        
        mock_checkbox = Mock()
        mock_checkbox.isChecked.return_value = True
        
        mock_window.network_form_generator.get_param_widgets.return_value = {
            "enabled": mock_checkbox
        }
        mock_window.network_form_generator.get_params_for_save.return_value = {
            "enabled": True,
            "network_topology": "random",
            "connection_probability": 0.1,
            "synaptic_weight": 0.5
        }
        
        manager = NetworkManager(mock_window)
        options = manager.get_config()
        
        assert options["enabled"] is True
        assert "network_topology" in options
        
    def test_load_config(self):
        """Test loading network config into UI."""
        mock_window = Mock()
        mock_window.network_form_generator = Mock()
        
        mock_checkbox = Mock()
        mock_weight = Mock()
        mock_topology = Mock()
        mock_topology.count.return_value = 3
        mock_topology.itemData.side_effect = ["random", "all_to_all", "small_world"]
        
        mock_window.network_form_generator.get_param_widgets.return_value = {
            "enabled": mock_checkbox,
            "synaptic_weight": mock_weight,
            "network_topology": mock_topology
        }
        
        manager = NetworkManager(mock_window)
        
        data = {
            "enabled": True,
            "network_topology": "random",
            "synaptic_weight": 0.8
        }
        
        manager.load_config(data)
        
        assert mock_checkbox.setChecked.called


class TestSimParamsManager:
    """Tests for SimParamsManager."""
    
    def test_manager_creation(self):
        """Test creating SimParamsManager."""
        mock_window = Mock()
        manager = SimParamsManager(mock_window)
        
        assert manager is not None
        assert manager.main_window == mock_window
        
    def test_get_sim_params_config(self):
        """Test getting simulation parameters."""
        mock_window = Mock()
        mock_window.sim_params_form_generator = Mock()
        
        mock_window.sim_params_form_generator.get_params_for_save.return_value = {
            "num_neurons": 100,
            "sim_time": 1000,
            "dt": 0.1,
            "input_current": 1.0
        }
        
        manager = SimParamsManager(mock_window)
        params = manager.get_sim_params_config()
        
        assert params["num_neurons"] == 100
        assert params["sim_time"] == 1000
        
    def test_load_sim_params(self):
        """Test loading simulation parameters."""
        mock_window = Mock()
        mock_window.sim_params_form_generator = Mock()
        
        manager = SimParamsManager(mock_window)
        
        data = {
            "num_neurons": 200,
            "sim_time": 2000,
            "dt": 0.1
        }
        
        manager.load_sim_params(data)
        assert mock_window.sim_params_form_generator.load_params_from_config.called


class TestNeuronModelsManager:
    """Tests for NeuronModelsManager."""
    
    def test_manager_creation(self):
        """Test creating NeuronModelsManager."""
        mock_window = Mock()
        manager = NeuronModelsManager(mock_window)
        
        assert manager is not None
        assert manager.main_window == mock_window
        
    def test_get_neuron_model(self):
        """Test getting neuron model configuration."""
        mock_window = Mock()
        mock_window.neuron_model_combo = Mock()
        mock_window.neuron_model_combo.currentData.return_value = "lif"
        
        manager = NeuronModelsManager(mock_window)
        manager.get_neuron_model_config = Mock(return_value={
            "model_key": "lif",
            "parameters": {"tau_m": 20.0, "v_rest": -70.0}
        })
        
        model = manager.get_neuron_model()
        
        assert model["model_key"] == "lif"
        assert "parameters" in model
        
    def test_set_preset_to_custom(self):
        """Test setting preset to custom."""
        mock_window = Mock()
        mock_window.neuron_model_preset_combo = Mock()
        mock_window.neuron_model_preset_combo.findText.return_value = 1
        
        manager = NeuronModelsManager(mock_window)
        manager.set_preset_to_custom()
        
        assert mock_window.neuron_model_preset_combo.setCurrentIndex.called


class TestAdvancedManagers:
    """Tests for advanced feature managers."""
    
    def test_gap_junctions_manager(self):
        """Test gap junctions manager exists and has basic functionality."""
        from brian2sim.managers.gap_junctions_manager import GapJunctionsManager
        
        mock_window = Mock()
        manager = GapJunctionsManager(mock_window)
        
        assert manager is not None
        
    def test_calcium_dynamics_manager(self):
        """Test calcium dynamics manager exists."""
        from brian2sim.managers.calcium_dynamics_manager import CalciumDynamicsManager
        
        mock_window = Mock()
        manager = CalciumDynamicsManager(mock_window)
        
        assert manager is not None
        
    def test_neuromodulation_manager(self):
        """Test neuromodulation manager exists."""
        from brian2sim.managers.neuromodulation_manager import NeuromodulationManager
        
        mock_window = Mock()
        manager = NeuromodulationManager(mock_window)
        
        assert manager is not None
        
    def test_homeostatic_plasticity_manager(self):
        """Test homeostatic plasticity manager exists."""
        from brian2sim.managers.homeostatic_plasticity_manager import HomeostaticPlasticityManager
        
        mock_window = Mock()
        manager = HomeostaticPlasticityManager(mock_window)
        
        assert manager is not None
        
    def test_short_term_plasticity_manager(self):
        """Test short-term plasticity manager exists."""
        from brian2sim.managers.short_term_plasticity_manager import ShortTermPlasticityManager
        
        mock_window = Mock()
        manager = ShortTermPlasticityManager(mock_window)
        
        assert manager is not None
        
    def test_multicompartment_manager(self):
        """Test multicompartment manager exists."""
        from brian2sim.managers.multicompartment_manager import MulticompartmentManager
        
        mock_window = Mock()
        manager = MulticompartmentManager(mock_window)
        
        assert manager is not None
        
    def test_synaptic_receptors_manager(self):
        """Test synaptic receptors manager exists."""
        from brian2sim.managers.synaptic_receptors_manager import SynapticReceptorsManager
        
        mock_window = Mock()
        manager = SynapticReceptorsManager(mock_window)
        
        assert manager is not None
        
    def test_input_patterns_manager(self):
        """Test input patterns manager exists."""
        from brian2sim.managers.input_patterns_manager import InputPatternsManager
        
        mock_window = Mock()
        manager = InputPatternsManager(mock_window)
        
        assert manager is not None
        
    def test_advanced_network_manager(self):
        """Test advanced network manager exists."""
        from brian2sim.managers.advanced_network_manager import AdvancedNetworkManager
        
        mock_window = Mock()
        manager = AdvancedNetworkManager(mock_window)
        
        assert manager is not None


class TestManagerSignals:
    """Tests for manager signal handling."""
    
    def test_noise_manager_signals(self):
        """Test noise manager param_changed signal."""
        mock_window = Mock()
        manager = NoiseManager(mock_window)
        
        signal_emitted = False
        def on_signal():
            nonlocal signal_emitted
            signal_emitted = True
            
        manager.param_changed.connect(on_signal)
        manager.on_param_changed()
        
        assert signal_emitted is True
        
    def test_network_manager_signals(self):
        """Test network manager param_changed signal."""
        mock_window = Mock()
        manager = NetworkManager(mock_window)
        
        signal_emitted = False
        def on_signal():
            nonlocal signal_emitted
            signal_emitted = True
            
        manager.param_changed.connect(on_signal)
        manager.on_param_changed()
        
        assert signal_emitted is True


class TestManagerEdgeCases:
    """Tests for manager edge cases."""
    
    def test_noise_manager_no_form_generator(self):
        """Test noise manager without form generator."""
        mock_window = Mock()
        del mock_window.noise_form_generator
        
        manager = NoiseManager(mock_window)
        options = manager.get_config()
        
        assert options["enabled"] is False
        
    def test_network_manager_no_form_generator(self):
        """Test network manager without form generator."""
        mock_window = Mock()
        del mock_window.network_form_generator
        
        manager = NetworkManager(mock_window)
        options = manager.get_config()
        
        assert options["enabled"] is False
        
    def test_load_none_data(self):
        """Test loading None data doesn't crash."""
        mock_window = Mock()
        mock_window.noise_form_generator = Mock()
        
        manager = NoiseManager(mock_window)
        manager.load_config(None)
        
        # Should not crash
        
    def test_load_invalid_data_type(self):
        """Test loading invalid data type."""
        mock_window = Mock()
        mock_window.noise_form_generator = Mock()
        
        manager = NoiseManager(mock_window)
        manager.load_config("invalid")
        
        # Should not crash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
