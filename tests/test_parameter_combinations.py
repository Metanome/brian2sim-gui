"""
Property-based tests for parameter combinations.
Uses hypothesis to generate random valid parameter combinations
and verify the system handles them without crashing.
"""
import pytest

# Try to import hypothesis, skip if not available
try:
    from hypothesis import given, strategies as st, settings, assume
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Create dummy decorators
    def given(*args, **kwargs):
        def decorator(func):
            return pytest.mark.skip(reason="hypothesis not installed")(func)
        return decorator
    class st:
        @staticmethod
        def floats(*args, **kwargs): return None
        @staticmethod
        def integers(*args, **kwargs): return None
        @staticmethod
        def booleans(): return None
        @staticmethod
        def sampled_from(*args): return None
    def settings(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from brian2sim.managers.parameter_validation import ParameterValidator, ValidationResult


# Parameter strategies
voltage_strategy = st.floats(min_value=-100.0, max_value=50.0, allow_nan=False)
tau_strategy = st.floats(min_value=0.1, max_value=1000.0, allow_nan=False)
probability_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
concentration_strategy = st.floats(min_value=0.0, max_value=1000.0, allow_nan=False)
neuron_count_strategy = st.integers(min_value=1, max_value=10000)


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestRandomValidParameters:
    """Tests with randomly generated valid parameters."""
    
    @given(voltage=voltage_strategy)
    @settings(max_examples=50)
    def test_random_valid_voltage(self, voltage):
        """Test random valid voltages pass validation."""
        validator = ParameterValidator()
        result = validator.validate_parameter("membrane_voltage", voltage)
        
        assert result.is_valid, f"Valid voltage {voltage} failed validation"
        
    @given(tau=tau_strategy)
    @settings(max_examples=50)
    def test_random_valid_tau(self, tau):
        """Test random valid time constants pass validation."""
        validator = ParameterValidator()
        result = validator.validate_parameter("membrane_tau", tau)
        
        assert result.is_valid, f"Valid tau {tau} failed validation"
        
    @given(prob=probability_strategy)
    @settings(max_examples=50)
    def test_random_valid_probability(self, prob):
        """Test random valid probabilities pass validation."""
        validator = ParameterValidator()
        result = validator.validate_parameter("connection_probability", prob)
        
        assert result.is_valid, f"Valid probability {prob} failed validation"
        
    @given(conc=concentration_strategy)
    @settings(max_examples=50)
    def test_random_valid_concentration(self, conc):
        """Test random valid concentrations pass validation."""
        validator = ParameterValidator()
        result = validator.validate_parameter("mg_concentration", conc)
        
        assert result.is_valid, f"Valid concentration {conc} failed validation"


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestRandomInvalidParameters:
    """Tests with randomly generated invalid parameters."""
    
    @given(voltage=st.floats(min_value=51.0, max_value=200.0, allow_nan=False))
    @settings(max_examples=25)
    def test_random_high_voltage_invalid(self, voltage):
        """Test high voltages are invalid."""
        validator = ParameterValidator()
        result = validator.validate_parameter("membrane_voltage", voltage)
        
        assert not result.is_valid, f"High voltage {voltage} should be invalid"
        
    @given(prob=st.floats(min_value=1.01, max_value=10.0, allow_nan=False))
    @settings(max_examples=25)
    def test_random_high_probability_invalid(self, prob):
        """Test probabilities > 1 are invalid."""
        validator = ParameterValidator()
        result = validator.validate_parameter("connection_probability", prob)
        
        assert not result.is_valid, f"Probability {prob} > 1 should be invalid"


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class TestRandomParameterCombinations:
    """Tests with random combinations of parameters."""
    
    @given(
        n_exc=neuron_count_strategy,
        n_inh=neuron_count_strategy,
        exc_prob=probability_strategy,
        inh_prob=probability_strategy,
    )
    @settings(max_examples=50)
    def test_random_network_params(self, n_exc, n_inh, exc_prob, inh_prob):
        """Test random network parameter combinations don't crash."""
        validator = ParameterValidator()
        
        params = {
            "n_excitatory": n_exc,
            "n_inhibitory": n_inh,
            "excitatory_connection_probability": exc_prob,
            "inhibitory_connection_probability": inh_prob,
        }
        
        # Should not crash
        results = validator.validate_all_parameters(params)
        
        assert isinstance(results, list)
        
    @given(
        nmda_enabled=st.booleans(),
        calcium_enabled=st.booleans(),
        mg_conc=concentration_strategy,
    )
    @settings(max_examples=50)
    def test_random_receptor_calcium_combo(self, nmda_enabled, calcium_enabled, mg_conc):
        """Test random NMDA/Calcium combinations don't crash."""
        validator = ParameterValidator()
        
        params = {
            "nmda_enabled": nmda_enabled,
            "calcium_dynamics_enabled": calcium_enabled,
            "mg_concentration": mg_conc if nmda_enabled else None,
            "calcium_rest": 0.0001 if calcium_enabled else None,
            "calcium_tau": 20.0 if calcium_enabled else None,
        }
        
        # Should not crash
        results = validator.validate_all_parameters(params)
        
        assert isinstance(results, list)


class TestBoundaryFuzzing:
    """Tests at boundary conditions without hypothesis."""
    
    @pytest.mark.parametrize("voltage", [-100.0, -99.9, -50.0, 0.0, 49.9, 50.0])
    def test_voltage_boundaries(self, voltage):
        """Test voltages at and near boundaries."""
        validator = ParameterValidator()
        result = validator.validate_parameter("membrane_voltage", voltage)
        
        assert result.is_valid
        
    @pytest.mark.parametrize("voltage", [-100.1, -150.0, 50.1, 100.0])
    def test_voltage_out_of_bounds(self, voltage):
        """Test voltages outside boundaries."""
        validator = ParameterValidator()
        result = validator.validate_parameter("membrane_voltage", voltage)
        
        assert not result.is_valid
        
    @pytest.mark.parametrize("tau", [0.1, 0.2, 1.0, 100.0, 999.9, 1000.0])
    def test_tau_boundaries(self, tau):
        """Test time constants at and near boundaries."""
        validator = ParameterValidator()
        result = validator.validate_parameter("membrane_tau", tau)
        
        assert result.is_valid
        
    @pytest.mark.parametrize("tau", [0.01, 0.09, 1000.1, 2000.0])
    def test_tau_out_of_bounds(self, tau):
        """Test time constants outside boundaries."""
        validator = ParameterValidator()
        result = validator.validate_parameter("membrane_tau", tau)
        
        assert not result.is_valid
        
    @pytest.mark.parametrize("prob", [0.0, 0.001, 0.5, 0.999, 1.0])
    def test_probability_boundaries(self, prob):
        """Test probabilities at and near boundaries."""
        validator = ParameterValidator()
        result = validator.validate_parameter("connection_probability", prob)
        
        assert result.is_valid
        
    @pytest.mark.parametrize("prob", [-0.1, -0.001, 1.001, 1.5])
    def test_probability_out_of_bounds(self, prob):
        """Test probabilities outside boundaries."""
        validator = ParameterValidator()
        result = validator.validate_parameter("connection_probability", prob)
        
        assert not result.is_valid


class TestParameterCombinationMatrix:
    """Test specific parameter combinations that might be problematic."""
    
    @pytest.mark.parametrize("model,calcium,nmda,stp", [
        ("lif", False, False, False),
        ("lif", True, False, False),
        ("lif", True, True, False),
        ("lif", True, True, True),
        ("izhikevich", True, True, True),
        ("adex", True, True, True),
        ("hodgkin_huxley", True, True, True),
    ])
    def test_model_feature_combinations(self, model, calcium, nmda, stp):
        """Test various model + feature combinations pass validation."""
        validator = ParameterValidator()
        
        params = {
            "model_type": model,
            "calcium_dynamics_enabled": calcium,
            "calcium_rest": 0.0001 if calcium else None,
            "calcium_tau": 20.0 if calcium else None,
            "nmda_enabled": nmda,
            "mg_concentration": 1.0 if nmda else None,
            "short_term_plasticity_enabled": stp,
            "n_excitatory": 100,
            "n_inhibitory": 25,
        }
        
        # Should not crash
        results = validator.validate_all_parameters(params)
        assert isinstance(results, list)
        
    @pytest.mark.parametrize("n_neurons", [1, 10, 100, 1000, 5000])
    def test_various_network_sizes(self, n_neurons):
        """Test validation with various network sizes."""
        validator = ParameterValidator()
        
        params = {
            "n_excitatory": n_neurons,
            "n_inhibitory": n_neurons // 4,
            "excitatory_connection_probability": 0.1,
        }
        
        results = validator.validate_all_parameters(params)
        
        # Should not crash, though may have warnings
        assert isinstance(results, list)
