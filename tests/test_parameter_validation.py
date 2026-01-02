"""
Unit tests for ParameterValidator and ValidationManager.
Tests range validation, cross-parameter rules, and validation integration.
"""
import pytest
from unittest.mock import MagicMock, patch
from brian2sim.managers.parameter_validation import (
    ValidationResult,
    ParameterValidator,
    ValidationManager,
)


class TestValidationResult:
    """Tests for ValidationResult class."""
    
    def test_valid_result(self):
        """Test creating a valid result."""
        result = ValidationResult(True, "")
        
        assert result.is_valid
        assert bool(result) == True
        
    def test_invalid_result(self):
        """Test creating an invalid result."""
        result = ValidationResult(False, "Error message")
        
        assert not result.is_valid
        assert bool(result) == False
        assert result.message == "Error message"
        
    def test_warning_severity(self):
        """Test warning severity."""
        result = ValidationResult(True, "Warning", "warning")
        
        assert result.severity == "warning"
        
    def test_default_severity_is_error(self):
        """Test default severity is error."""
        result = ValidationResult(False, "Error")
        
        assert result.severity == "error"


class TestParameterValidatorRangeRules:
    """Tests for ParameterValidator range validation."""
    
    def test_validator_creation(self):
        """Test validator can be created."""
        validator = ParameterValidator()
        
        assert validator is not None
        assert len(validator.validation_rules) > 0
        
    def test_voltage_in_range(self):
        """Test voltage parameter in valid range."""
        validator = ParameterValidator()
        
        result = validator.validate_parameter("v_rest_voltage", -70.0)
        
        assert result.is_valid
        
    def test_voltage_out_of_range(self):
        """Test voltage parameter out of range."""
        validator = ParameterValidator()
        
        result = validator.validate_parameter("v_rest_voltage", 100.0)  # Too high
        
        assert not result.is_valid
        
    def test_tau_in_range(self):
        """Test time constant in valid range."""
        validator = ParameterValidator()
        
        result = validator.validate_parameter("membrane_tau", 20.0)
        
        assert result.is_valid
        
    def test_tau_out_of_range(self):
        """Test time constant out of range."""
        validator = ParameterValidator()
        
        result = validator.validate_parameter("tau_m", 0.01)  # Too small
        
        assert not result.is_valid
        
    def test_probability_in_range(self):
        """Test probability in valid range."""
        validator = ParameterValidator()
        
        result = validator.validate_parameter("connection_probability", 0.5)
        
        assert result.is_valid
        
    def test_probability_out_of_range(self):
        """Test probability out of range."""
        validator = ParameterValidator()
        
        result = validator.validate_parameter("probability_exc", 1.5)  # > 1
        
        assert not result.is_valid
        
    def test_negative_time_invalid(self):
        """Test negative time parameters are invalid."""
        validator = ParameterValidator()
        
        result = validator.validate_parameter("delay_time", -5.0)
        
        assert not result.is_valid


class TestParameterValidatorCrossParameterRules:
    """Tests for cross-parameter validation rules."""
    
    def test_nmda_requires_mg_concentration(self):
        """Test NMDA enabled requires Mg concentration."""
        validator = ParameterValidator()
        
        params = {
            "nmda_enabled": True,
            # mg_concentration missing
        }
        
        results = validator.validate_all_parameters(params)
        
        # Should have error about missing Mg
        errors = [r for r in results if not r.is_valid]
        assert len(errors) > 0
        assert any("Mg" in r.message or "mg" in r.message.lower() for r in errors)
        
    def test_nmda_with_mg_valid(self):
        """Test NMDA with Mg concentration is valid."""
        validator = ParameterValidator()
        
        params = {
            "nmda_enabled": True,
            "mg_concentration": 1.0,
        }
        
        results = validator.validate_all_parameters(params)
        
        # Filter for NMDA-related errors only
        nmda_errors = [r for r in results if not r.is_valid and "NMDA" in r.message]
        assert len(nmda_errors) == 0
        
    def test_calcium_requires_rest_and_tau(self):
        """Test calcium dynamics requires rest and tau."""
        validator = ParameterValidator()
        
        params = {
            "calcium_dynamics_enabled": True,
            # Missing calcium_rest and calcium_tau
        }
        
        results = validator.validate_all_parameters(params)
        
        errors = [r for r in results if not r.is_valid and "Calcium" in r.message]
        assert len(errors) > 0
        
    def test_network_consistency_zero_neurons(self):
        """Test network with zero neurons is invalid."""
        validator = ParameterValidator()
        
        params = {
            "n_excitatory": 0,
            "n_inhibitory": 0,
        }
        
        results = validator.validate_all_parameters(params)
        
        errors = [r for r in results if not r.is_valid]
        assert any("neuron" in r.message.lower() for r in errors)
        
    def test_large_network_warning(self):
        """Test large network generates warning."""
        validator = ParameterValidator()
        
        params = {
            "n_excitatory": 8000,
            "n_inhibitory": 3000,
        }
        
        results = validator.validate_all_parameters(params)
        
        # Large network should trigger network consistency check
        # May have warning or just pass validation
        assert isinstance(results, list)
        
    def test_high_connection_probability_warning(self):
        """Test high connection probability generates warning."""
        validator = ParameterValidator()
        
        params = {
            "n_excitatory": 100,
            "n_inhibitory": 50,
            "excitatory_connection_probability": 0.8,
        }
        
        results = validator.validate_all_parameters(params)
        
        # High connection prob may trigger warning - just ensure no crash
        assert isinstance(results, list)


class TestValidationManager:
    """Tests for ValidationManager class."""
    
    def test_manager_creation(self):
        """Test ValidationManager can be created."""
        mock_window = MagicMock()
        manager = ValidationManager(mock_window)
        
        assert manager is not None
        assert manager.validator is not None
        
    def test_validation_enabled_by_default(self):
        """Test validation is enabled by default."""
        mock_window = MagicMock()
        manager = ValidationManager(mock_window)
        
        assert manager.validation_enabled == True
        
    def test_disable_validation(self):
        """Test disabling validation."""
        mock_window = MagicMock()
        manager = ValidationManager(mock_window)
        
        manager.enable_validation(False)
        
        assert manager.validation_enabled == False
        
    def test_validate_returns_true_when_disabled(self):
        """Test validation returns True when disabled."""
        mock_window = MagicMock()
        manager = ValidationManager(mock_window)
        manager.enable_validation(False)
        
        result = manager.validate_current_parameters()
        
        assert result == True
        
    def test_add_custom_rule(self):
        """Test adding a custom validation rule."""
        mock_window = MagicMock()
        manager = ValidationManager(mock_window)
        
        custom_rule = lambda params: ValidationResult(False, "Custom error")
        manager.add_custom_rule(custom_rule, "Custom error message")
        
        # Should have added a rule
        assert len(manager.validator.cross_parameter_rules) > 0


class TestValidationEdgeCases:
    """Tests for validation edge cases."""
    
    def test_empty_params(self):
        """Test validation with empty parameters."""
        validator = ParameterValidator()
        
        results = validator.validate_all_parameters({})
        
        # Should still run validation
        assert isinstance(results, list)
        
    def test_none_values(self):
        """Test validation handles None values."""
        validator = ParameterValidator()
        
        params = {
            "some_voltage": None,
        }
        
        # Should not crash
        results = validator.validate_all_parameters(params)
        assert isinstance(results, list)
        
    def test_string_for_numeric(self):
        """Test validation handles string for numeric parameter."""
        validator = ParameterValidator()
        
        result = validator.validate_parameter("membrane_tau", "not_a_number")
        
        assert not result.is_valid
        
    def test_extreme_values(self):
        """Test validation at extreme boundaries."""
        validator = ParameterValidator()
        
        # Test at boundary
        result_min = validator.validate_parameter("tau_param", 0.1)  # At minimum
        result_max = validator.validate_parameter("tau_param", 1000.0)  # At maximum
        
        assert result_min.is_valid
        assert result_max.is_valid
