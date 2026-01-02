"""
Unit tests for CrossTabDependencyManager.
Tests cross-tab parameter dependencies and neuroscientific consistency validation.
"""
import pytest
from unittest.mock import MagicMock, patch
from brian2sim.managers.cross_tab_dependencies import CrossTabDependencyManager


class TestCrossTabDependencyManager:
    """Tests for CrossTabDependencyManager initialization and rules."""
    
    def test_manager_creation(self):
        """Test manager can be created with mock main window."""
        mock_window = MagicMock()
        manager = CrossTabDependencyManager(mock_window)
        
        assert manager is not None
        assert manager.main_window == mock_window
        assert manager.dependency_rules is not None
        
    def test_dependency_rules_defined(self):
        """Test that all expected dependency rules are defined."""
        mock_window = MagicMock()
        manager = CrossTabDependencyManager(mock_window)
        
        rules = manager.dependency_rules
        
        # Check all expected rules exist
        assert "nmda_calcium_coupling" in rules
        assert "calcium_plasticity_coupling" in rules
        assert "receptor_stp_coupling" in rules
        assert "gap_junction_sync_coupling" in rules
        
    def test_nmda_calcium_rule_structure(self):
        """Test NMDA-Calcium coupling rule has correct structure."""
        mock_window = MagicMock()
        manager = CrossTabDependencyManager(mock_window)
        
        rule = manager.dependency_rules["nmda_calcium_coupling"]
        
        assert rule["source_tab"] == "synaptic_receptors"
        assert rule["source_param"] == "nmda_enabled"
        assert rule["target_tab"] == "calcium_dynamics"
        assert "rule" in rule
        
    def test_calcium_plasticity_rule_structure(self):
        """Test Calcium-Plasticity coupling rule has correct structure."""
        mock_window = MagicMock()
        manager = CrossTabDependencyManager(mock_window)
        
        rule = manager.dependency_rules["calcium_plasticity_coupling"]
        
        assert rule["source_tab"] == "calcium_dynamics"
        assert rule["source_param"] == "enabled"
        assert rule["target_tab"] == "homeostatic_plasticity"


class TestDependencyConnections:
    """Tests for connecting and updating dependencies."""
    
    def test_connect_dependencies_no_managers(self):
        """Test connect_dependencies handles missing managers gracefully."""
        mock_window = MagicMock(spec=[])  # Empty spec - no attributes
        manager = CrossTabDependencyManager(mock_window)
        
        # Should not raise
        manager.connect_dependencies()
        
    def test_connect_dependencies_with_managers(self):
        """Test connect_dependencies connects to manager signals."""
        mock_window = MagicMock()
        mock_manager = MagicMock()
        mock_manager.param_changed = MagicMock()
        
        mock_window.synaptic_receptors_manager = mock_manager
        
        manager = CrossTabDependencyManager(mock_window)
        manager.connect_dependencies()
        
        # Should have connected to param_changed signal
        mock_manager.param_changed.connect.assert_called()
        
    def test_update_dependencies_calls_apply_rule(self):
        """Test update_dependencies applies all rules."""
        mock_window = MagicMock()
        manager = CrossTabDependencyManager(mock_window)
        
        with patch.object(manager, "_apply_dependency_rule") as mock_apply:
            manager.update_dependencies()
            
            # Should call apply for each rule
            assert mock_apply.call_count == len(manager.dependency_rules)


class TestParameterValueRetrieval:
    """Tests for getting and setting parameter values."""
    
    def test_get_parameter_value_checkbox(self):
        """Test getting checkbox parameter value."""
        mock_window = MagicMock()
        mock_form_gen = MagicMock()
        mock_checkbox = MagicMock()
        mock_checkbox.isChecked.return_value = True
        mock_form_gen.get_param_widgets.return_value = {"enabled": mock_checkbox}
        
        mock_window.test_tab_form_generator = mock_form_gen
        
        manager = CrossTabDependencyManager(mock_window)
        value = manager._get_parameter_value("test_tab", "enabled")
        
        assert value == True
        
    def test_get_parameter_value_spinbox(self):
        """Test getting spinbox parameter value."""
        mock_window = MagicMock()
        mock_form_gen = MagicMock()
        mock_spinbox = MagicMock(spec=["value"])
        mock_spinbox.value.return_value = 42.0
        mock_form_gen.get_param_widgets.return_value = {"rate": mock_spinbox}
        
        mock_window.test_tab_form_generator = mock_form_gen
        
        manager = CrossTabDependencyManager(mock_window)
        value = manager._get_parameter_value("test_tab", "rate")
        
        assert value == 42.0
        
    def test_get_parameter_value_combobox(self):
        """Test getting combobox parameter value."""
        mock_window = MagicMock()
        mock_form_gen = MagicMock()
        mock_combo = MagicMock(spec=["currentText"])
        mock_combo.currentText.return_value = "option_1"
        mock_form_gen.get_param_widgets.return_value = {"method": mock_combo}
        
        mock_window.test_tab_form_generator = mock_form_gen
        
        manager = CrossTabDependencyManager(mock_window)
        value = manager._get_parameter_value("test_tab", "method")
        
        assert value == "option_1"
        
    def test_get_parameter_value_missing(self):
        """Test getting non-existent parameter returns None."""
        mock_window = MagicMock(spec=[])
        manager = CrossTabDependencyManager(mock_window)
        
        value = manager._get_parameter_value("nonexistent", "param")
        
        assert value is None
        
    def test_set_parameter_enabled(self):
        """Test enabling/disabling parameter widgets."""
        mock_window = MagicMock()
        mock_form_gen = MagicMock()
        mock_widget = MagicMock()
        mock_form_gen.get_param_widgets.return_value = {"test_param": mock_widget}
        
        mock_window.test_tab_form_generator = mock_form_gen
        
        manager = CrossTabDependencyManager(mock_window)
        manager._set_parameter_enabled("test_tab", "test_param", False)
        
        mock_widget.setEnabled.assert_called_with(False)


class TestValidateConfiguration:
    """Tests for configuration validation."""
    
    def test_validate_nmda_without_calcium_warning(self):
        """Test warning when NMDA enabled but calcium disabled."""
        mock_window = MagicMock()
        manager = CrossTabDependencyManager(mock_window)
        
        with patch.object(manager, "_get_parameter_value") as mock_get:
            mock_get.side_effect = lambda tab, param: {
                ("synaptic_receptors", "nmda_enabled"): True,
                ("calcium_dynamics", "enabled"): False,
                ("homeostatic_plasticity", "enabled"): False,
                ("homeostatic_plasticity", "target_firing_rate"): 5.0,
            }.get((tab, param))
            
            warnings = manager.validate_configuration()
            
            assert len(warnings) >= 1
            assert any("NMDA" in w and "calcium" in w.lower() for w in warnings)
            
    def test_validate_homeostatic_without_target_rate_warning(self):
        """Test warning when homeostatic plasticity has no target rate."""
        mock_window = MagicMock()
        manager = CrossTabDependencyManager(mock_window)
        
        with patch.object(manager, "_get_parameter_value") as mock_get:
            mock_get.side_effect = lambda tab, param: {
                ("synaptic_receptors", "nmda_enabled"): False,
                ("calcium_dynamics", "enabled"): False,
                ("homeostatic_plasticity", "enabled"): True,
                ("homeostatic_plasticity", "target_firing_rate"): 0,
            }.get((tab, param))
            
            warnings = manager.validate_configuration()
            
            assert len(warnings) >= 1
            assert any("Homeostatic" in w for w in warnings)
            
    def test_validate_no_warnings_when_consistent(self):
        """Test no warnings when configuration is consistent."""
        mock_window = MagicMock()
        manager = CrossTabDependencyManager(mock_window)
        
        with patch.object(manager, "_get_parameter_value") as mock_get:
            mock_get.side_effect = lambda tab, param: {
                ("synaptic_receptors", "nmda_enabled"): True,
                ("calcium_dynamics", "enabled"): True,  # Consistent
                ("homeostatic_plasticity", "enabled"): True,
                ("homeostatic_plasticity", "target_firing_rate"): 5.0,  # Valid
            }.get((tab, param))
            
            warnings = manager.validate_configuration()
            
            assert len(warnings) == 0


class TestCouplingHandlers:
    """Tests for specific coupling handler methods."""
    
    def test_handle_nmda_calcium_coupling(self):
        """Test NMDA-Calcium coupling handler."""
        mock_window = MagicMock()
        manager = CrossTabDependencyManager(mock_window)
        
        rule = manager.dependency_rules["nmda_calcium_coupling"]
        
        with patch.object(manager, "_set_parameter_enabled") as mock_set:
            manager._handle_nmda_calcium_coupling(True, rule)
            
            # Should enable calcium source parameters
            assert mock_set.call_count >= 1
            
    def test_handle_gap_junction_sync_coupling(self):
        """Test gap junction sync coupling handler."""
        mock_window = MagicMock()
        manager = CrossTabDependencyManager(mock_window)
        
        rule = manager.dependency_rules["gap_junction_sync_coupling"]
        
        with patch.object(manager, "_set_parameter_enabled") as mock_set:
            manager._handle_gap_junction_sync_coupling(True, rule)
            
            # Should enable sync analysis parameters
            assert mock_set.call_count >= 1
