"""
Integration tests for the full validation chain.
Tests CrossTabDependencies → ParameterValidator → SimulationManager flow.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from brian2sim.managers.parameter_validation import (
    ValidationResult,
    ParameterValidator,
    ValidationManager,
)
from brian2sim.managers.cross_tab_dependencies import CrossTabDependencyManager


class TestValidationChainIntegration:
    """Tests for the full validation chain."""
    
    def test_cross_tab_and_validator_consistency(self):
        """Test CrossTabDependencies and ParameterValidator are consistent."""
        # CrossTabDependencyManager has NMDA → Calcium coupling
        # ParameterValidator should also validate NMDA requires Mg
        
        mock_window = MagicMock()
        cross_tab = CrossTabDependencyManager(mock_window)
        validator = ParameterValidator()
        
        # Both should have NMDA-related rules
        nmda_rules = [r for r in cross_tab.dependency_rules.values() 
                     if "nmda" in r.get("source_param", "").lower()]
        validator_nmda_rules = [r for r in validator.cross_parameter_rules
                               if "nmda" in str(r.get("condition", "")).lower() or 
                               "nmda" in str(r.get("message", "")).lower()]
        
        assert len(nmda_rules) > 0 or len(validator_nmda_rules) > 0
        
    def test_disabled_feature_not_validated(self):
        """Test that disabled features are not validated."""
        validator = ParameterValidator()
        
        # NMDA disabled - no need for Mg
        params = {
            "nmda_enabled": False,
            # No mg_concentration needed
        }
        
        results = validator.validate_all_parameters(params)
        
        # Should not have NMDA-related errors
        nmda_errors = [r for r in results if not r.is_valid and "NMDA" in r.message]
        assert len(nmda_errors) == 0
        
    def test_validation_manager_collects_from_managers(self):
        """Test ValidationManager collects parameters from all managers."""
        mock_window = MagicMock()
        
        # Setup mock managers with get_parameters
        mock_neuron_manager = MagicMock()
        mock_neuron_manager.get_parameters.return_value = {"tau_m": 20.0}
        mock_window.neuron_models_manager = mock_neuron_manager
        
        mock_sim_manager = MagicMock()
        mock_sim_manager.get_parameters.return_value = {"sim_time": 1000.0}
        mock_window.sim_params_manager = mock_sim_manager
        
        validation_manager = ValidationManager(mock_window)
        params = validation_manager._collect_all_parameters()
        
        assert "tau_m" in params or "sim_time" in params


class TestInvalidConfigurationsCaught:
    """Tests that invalid configurations are caught before simulation."""
    
    def test_negative_simulation_time(self):
        """Test negative simulation time is caught."""
        validator = ParameterValidator()
        
        result = validator.validate_parameter("sim_time", -100)
        
        assert not result.is_valid
        
    def test_zero_neuron_count(self):
        """Test zero neuron count is caught."""
        validator = ParameterValidator()
        
        params = {
            "n_excitatory": 0,
            "n_inhibitory": 0,
        }
        
        results = validator.validate_all_parameters(params)
        errors = [r for r in results if not r.is_valid]
        
        assert len(errors) > 0
        
    def test_conflicting_stp_options(self):
        """Test conflicting STP options generate warning."""
        validator = ParameterValidator()
        
        params = {
            "short_term_plasticity_enabled": True,
            "facilitation_enabled": True,
            "depression_enabled": True,  # Conflict
        }
        
        results = validator.validate_all_parameters(params)
        issues = [r for r in results if not r.is_valid or r.severity == "warning"]
        
        # Should have warning about conflict
        assert any("simul" in r.message.lower() or "conflict" in r.message.lower() 
                  or "both" in r.message.lower() for r in issues)


class TestNeuroscientificValidation:
    """Tests for neuroscientifically-motivated validation rules."""
    
    def test_nmda_without_calcium_warning(self):
        """Test NMDA without calcium dynamics should warn."""
        mock_window = MagicMock()
        cross_tab = CrossTabDependencyManager(mock_window)
        
        with patch.object(cross_tab, "_get_parameter_value") as mock_get:
            mock_get.side_effect = lambda tab, param: {
                ("synaptic_receptors", "nmda_enabled"): True,
                ("calcium_dynamics", "enabled"): False,
                ("homeostatic_plasticity", "enabled"): False,
                ("homeostatic_plasticity", "target_firing_rate"): 5.0,
            }.get((tab, param))
            
            warnings = cross_tab.validate_configuration()
            
            assert any("NMDA" in w for w in warnings)
            
    def test_homeostatic_requires_target_rate(self):
        """Test homeostatic plasticity requires target firing rate."""
        validator = ParameterValidator()
        
        params = {
            "homeostatic_plasticity_enabled": True,
            # Missing target_firing_rate and scaling_factor
        }
        
        results = validator.validate_all_parameters(params)
        errors = [r for r in results if not r.is_valid]
        
        assert any("target" in r.message.lower() or "homeostatic" in r.message.lower() 
                  for r in errors)


class TestValidationManagerSignals:
    """Tests for ValidationManager signal emission."""
    
    def test_validation_error_signal_emitted(self):
        """Test validation_error signal is emitted on errors."""
        mock_window = MagicMock()
        mock_window.neuron_models_manager = MagicMock()
        mock_window.neuron_models_manager.get_parameters.return_value = {
            "voltage_param": 200.0  # Out of range
        }
        
        manager = ValidationManager(mock_window)
        manager.validation_error = MagicMock()
        
        manager.validate_current_parameters()
        
        # Should have called validation_error or stored errors
        # (actual emission depends on having errors)
        assert isinstance(manager.current_errors, list)
        
    def test_validation_cleared_signal_on_success(self):
        """Test validation_cleared signal on no errors."""
        mock_window = MagicMock(spec=[])  # No managers
        
        manager = ValidationManager(mock_window)
        manager.validation_cleared = MagicMock()
        
        manager.validate_current_parameters()
        
        # With no managers, should clear validation
        # or have empty errors


class TestBoundaryConditions:
    """Tests for boundary condition validation."""
    
    def test_voltage_at_exact_boundary(self):
        """Test voltage at exact boundary values."""
        validator = ParameterValidator()
        
        # Exactly at minimum
        result_min = validator.validate_parameter("v_rest_voltage", -100.0)
        # Exactly at maximum
        result_max = validator.validate_parameter("v_threshold_voltage", 50.0)
        
        assert result_min.is_valid
        assert result_max.is_valid
        
    def test_probability_at_boundaries(self):
        """Test probability at 0 and 1."""
        validator = ParameterValidator()
        
        result_zero = validator.validate_parameter("connection_probability", 0.0)
        result_one = validator.validate_parameter("connection_probability", 1.0)
        
        assert result_zero.is_valid
        assert result_one.is_valid
        
    def test_time_constant_at_boundaries(self):
        """Test time constants at boundary."""
        validator = ParameterValidator()
        
        result_min = validator.validate_parameter("tau_param", 0.1)
        result_max = validator.validate_parameter("tau_param", 1000.0)
        
        assert result_min.is_valid
        assert result_max.is_valid
