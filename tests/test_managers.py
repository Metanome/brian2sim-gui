"""
Unit tests for manager classes.
Tests configuration handling, parameter validation, and UI-to-engine translation.
"""
import pytest
from brian2sim.managers.parameter_validation import ParameterValidator, ValidationResult


class TestParameterValidation:
    """Tests for parameter validation."""
    
    def test_validator_creation(self):
        """Test creating a parameter validator."""
        validator = ParameterValidator()
        assert validator is not None
        assert hasattr(validator, 'validation_rules')
        
    def test_validation_result_object(self):
        """Test ValidationResult object."""
        result = ValidationResult(True, "Success")
        assert result.is_valid is True
        assert bool(result) is True
        
        failed_result = ValidationResult(False, "Error")
        assert failed_result.is_valid is False
        assert bool(failed_result) is False
        
    def test_range_validation_rule(self):
        """Test adding and using range validation."""
        validator = ParameterValidator()
        validator.add_range_rule("test_param", 0, 100, "ms")
        
        assert "test_param" in validator.validation_rules
        rule = validator.validation_rules["test_param"]
        assert rule["min"] == 0
        assert rule["max"] == 100
        
    def test_default_voltage_rules(self):
        """Test default voltage validation rules exist."""
        validator = ParameterValidator()
        
        # Should have voltage rules setup by default
        assert "voltage" in validator.validation_rules
        rule = validator.validation_rules["voltage"]
        assert rule["min"] == -100
        assert rule["max"] == 50
        
    def test_cross_parameter_rules(self):
        """Test cross-parameter validation rules."""
        validator = ParameterValidator()
        
        # Should have some cross-parameter rules
        assert len(validator.cross_parameter_rules) > 0
        
        # Check that NMDA rule exists
        nmda_rules = [r for r in validator.cross_parameter_rules 
                      if "nmda" in r.get("message", "").lower()]
        assert len(nmda_rules) > 0


class TestManagerParameterTypes:
    """Tests for different parameter type validations."""
    
    def test_tau_parameter_range(self):
        """Test time constant validation."""
        validator = ParameterValidator()
        
        assert "tau" in validator.validation_rules
        rule = validator.validation_rules["tau"]
        assert rule["min"] == 0.1
        assert rule["max"] == 1000
        
    def test_conductance_parameter_range(self):
        """Test conductance validation."""
        validator = ParameterValidator()
        
        assert "conductance" in validator.validation_rules
        rule = validator.validation_rules["conductance"]
        assert rule["min"] == 0
        assert rule["max"] == 1000
        
    def test_probability_parameter_range(self):
        """Test probability validation."""
        validator = ParameterValidator()
        
        assert "probability" in validator.validation_rules
        rule = validator.validation_rules["probability"]
        assert rule["min"] == 0
        assert rule["max"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
