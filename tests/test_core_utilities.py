"""
Unit tests for core utility classes.
Tests code generation, configuration management, and results processing.
"""
import pytest
import os
import tempfile
from brian2sim.core.code_generator import CodeGenerator


class TestCodeGenerator:
    """Tests for code generation utilities."""
    
    def test_generator_creation(self):
        """Test creating code generator."""
        generator = CodeGenerator()
        assert generator is not None
        
    def test_generate_python_script(self):
        """Test generating standalone Python script."""
        generator = CodeGenerator()
        
        params = {
            "simulation": {"num_neurons": 100, "sim_time": 1000, "dt": 0.1},
            "neuron_model": {"model_key": "lif", "parameters": {}},
            "network": {"synaptic_connections": True, "topology": "random"}
        }
        
        code = generator.generate_simulation_code(params)
        
        assert code is not None
        assert "import brian2" in code or "from brian2 import" in code
        assert "NeuronGroup" in code or "run_simulation" in code
        
    def test_generated_code_has_run_command(self):
        """Test that generated code includes run() call."""
        generator = CodeGenerator()
        
        params = {
            "simulation": {"num_neurons": 10, "sim_time": 100, "dt": 0.1},
            "neuron_model": {"model_key": "lif", "parameters": {}}
        }
        
        code = generator.generate_simulation_code(params)
        
        assert "run(" in code or "Network" in code
        
    def test_header_generation(self):
        """Test that generated code includes header."""
        generator = CodeGenerator()
        header = generator._generate_header()
        
        assert len(header) > 0
        assert any("Brian2" in line for line in header)
        
    def test_imports_generation(self):
        """Test imports generation."""
        generator = CodeGenerator()
        imports = generator._generate_imports()
        
        assert len(imports) > 0
        assert any("brian2" in line.lower() for line in imports)
        
    def test_code_includes_monitoring(self):
        """Test that generated code can include monitors."""
        generator = CodeGenerator()
        
        params = {
            "simulation": {"num_neurons": 10, "sim_time": 100, "dt": 0.1},
            "neuron_model": {"model_key": "lif", "parameters": {}},
            "monitoring": {"spike_monitor": True, "state_monitor": True}
        }
        
        code = generator.generate_simulation_code(params)
        
        # Check for monitor-related code
        assert "Monitor" in code or "monitor" in code.lower()


class TestCodeGeneratorEdgeCases:
    """Tests for edge cases in code generation."""
    
    def test_generate_code_minimal_config(self):
        """Test code generation with minimal configuration."""
        generator = CodeGenerator()
        
        minimal_params = {
            "simulation": {"num_neurons": 1, "sim_time": 10, "dt": 0.1}
        }
        
        code = generator.generate_simulation_code(minimal_params)
        # Should generate valid code even with minimal config
        assert "brian2" in code.lower()
        assert len(code) > 100  # Should be substantial code
        
    def test_empty_parameters(self):
        """Test handling of empty parameters dict."""
        generator = CodeGenerator()
        
        code = generator.generate_simulation_code({})
        # Should still generate something without crashing
        assert code is not None
        assert isinstance(code, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
