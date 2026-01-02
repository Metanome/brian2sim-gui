"""
Unit tests for MenuBarManager functionality.
Tests the menu bar actions without requiring full GUI instantiation.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from brian2sim.ui.menu_bar import MenuBarManager
from brian2sim.managers.parameter_validation import ValidationResult


class TestMenuBarManager:
    """Test suite for MenuBarManager."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window with necessary managers."""
        main_window = Mock()
        
        # Mock managers that exist
        main_window.neuron_models_manager = Mock()
        main_window.sim_params_manager = Mock()
        main_window.noise_options_manager = Mock()
        main_window.input_patterns_manager = Mock()
        main_window.network_options_manager = Mock()
        main_window.advanced_network_manager = Mock()
        
        # Mock validation manager
        main_window.validation_manager = Mock()
        main_window.validation_manager.current_errors = []
        
        # Mock config manager
        main_window.config_manager = Mock()
        
        # Mock code generator
        main_window.code_generator = Mock()
        main_window.code_generator.generate_code = Mock(return_value="# Generated code")
        
        # Mock menuBar
        main_window.menuBar = Mock(return_value=Mock())
        
        # Mock tabs
        main_window.tabs = Mock()
        main_window.tab_info = {}
        
        # Mock methods called by menu_bar
        main_window.load_configuration = Mock()
        main_window.save_configuration = Mock()
        main_window.close = Mock()
        main_window.set_user_level = Mock()
        
        return main_window

    @pytest.fixture
    def menu_bar_manager(self, mock_main_window):
        """Create a MenuBarManager instance."""
        return MenuBarManager(mock_main_window)

    def test_initialization(self, menu_bar_manager, mock_main_window):
        """Test MenuBarManager initializes correctly."""
        assert menu_bar_manager.main_window == mock_main_window

    def test_setup_menu_bar(self, menu_bar_manager, mock_main_window):
        """Test menu bar setup doesn't crash."""
        # This should not raise any exceptions
        menu_bar_manager.setup_menu_bar()
        
        # Verify menuBar was called
        mock_main_window.menuBar.assert_called()

    def test_new_simulation_with_reset_methods(self, menu_bar_manager, mock_main_window):
        """Test new_simulation when managers have reset_to_defaults."""
        # Set up managers with reset_to_defaults method
        mock_main_window.neuron_models_manager.reset_to_defaults = Mock()
        mock_main_window.sim_params_manager.reset_to_defaults = Mock()
        mock_main_window.input_patterns_manager.reset_to_defaults = Mock()
        
        # Mock QMessageBox to return Yes
        with patch('brian2sim.ui.menu_bar.QMessageBox') as mock_msgbox:
            mock_msgbox.StandardButton.Yes = 1
            mock_msgbox.StandardButton.No = 0
            mock_msgbox.question.return_value = 1  # Yes
            
            menu_bar_manager.new_simulation()
            
            # Verify reset was called on managers that have the method
            mock_main_window.input_patterns_manager.reset_to_defaults.assert_called()

    def test_new_simulation_without_reset_methods(self, menu_bar_manager, mock_main_window):
        """Test new_simulation when managers don't have reset_to_defaults."""
        # Remove reset_to_defaults from managers (use delattr if it exists)
        for manager_name in ['neuron_models_manager', 'sim_params_manager', 'noise_options_manager']:
            manager = getattr(mock_main_window, manager_name)
            if hasattr(manager, 'reset_to_defaults'):
                delattr(manager, 'reset_to_defaults')
        
        # Mock QMessageBox to return Yes
        with patch('brian2sim.ui.menu_bar.QMessageBox') as mock_msgbox:
            mock_msgbox.StandardButton.Yes = 1
            mock_msgbox.StandardButton.No = 0
            mock_msgbox.question.return_value = 1  # Yes
            
            # This should not raise AttributeError
            menu_bar_manager.new_simulation()

    def test_show_validation_dialog_no_errors(self, menu_bar_manager, mock_main_window):
        """Test validation dialog when there are no errors."""
        mock_main_window.validation_manager.current_errors = []
        
        with patch('brian2sim.ui.menu_bar.QMessageBox') as mock_msgbox:
            menu_bar_manager.show_validation_dialog()
            
            # Should show information dialog about valid parameters
            mock_msgbox.information.assert_called()

    def test_show_validation_dialog_with_errors(self, menu_bar_manager, mock_main_window):
        """Test validation dialog with errors that have parameter attribute."""
        # Create validation results with parameter attribute
        error = ValidationResult(
            is_valid=False,
            message="Test error message",
            severity="error",
            parameter="test_param"
        )
        warning = ValidationResult(
            is_valid=True,
            message="Test warning",
            severity="warning",
            parameter="warn_param"
        )
        
        mock_main_window.validation_manager.current_errors = [error, warning]
        
        with patch('brian2sim.ui.menu_bar.QDialog') as mock_dialog, \
             patch('brian2sim.ui.menu_bar.QVBoxLayout'), \
             patch('brian2sim.ui.menu_bar.QTextEdit') as mock_text, \
             patch('brian2sim.ui.menu_bar.QPushButton'), \
             patch('brian2sim.ui.menu_bar.QHBoxLayout'):
            
            mock_dialog_instance = Mock()
            mock_dialog.return_value = mock_dialog_instance
            
            mock_text_instance = Mock()
            mock_text.return_value = mock_text_instance
            
            menu_bar_manager.show_validation_dialog()
            
            # Verify text was set with parameter info
            mock_text_instance.setPlainText.assert_called()
            call_args = mock_text_instance.setPlainText.call_args[0][0]
            assert "test_param" in call_args
            assert "Test error message" in call_args

    def test_export_config_calls_save_config_to_file(self, menu_bar_manager, mock_main_window):
        """Test export_config calls the correct ConfigManager method."""
        with patch('brian2sim.ui.menu_bar.QFileDialog') as mock_dialog, \
             patch('brian2sim.ui.menu_bar.QMessageBox'):
            
            mock_dialog.getSaveFileName.return_value = ("test_config.json", "")
            
            menu_bar_manager.export_config()
            
            # Verify save_config_to_file was called
            mock_main_window.config_manager.save_config_to_file.assert_called_once_with("test_config.json")

    def test_generate_code_shows_dialog(self, menu_bar_manager, mock_main_window):
        """Test generate_code creates and shows dialog."""
        with patch('brian2sim.ui.menu_bar.QDialog') as mock_dialog, \
             patch('brian2sim.ui.menu_bar.QVBoxLayout'), \
             patch('brian2sim.ui.menu_bar.QTextEdit'), \
             patch('brian2sim.ui.menu_bar.QPushButton'), \
             patch('brian2sim.ui.menu_bar.QHBoxLayout'):
            
            mock_dialog_instance = Mock()
            mock_dialog.return_value = mock_dialog_instance
            
            menu_bar_manager.generate_code()
            
            # Verify code generator was called
            mock_main_window.code_generator.generate_code.assert_called()
            # Verify dialog was executed
            mock_dialog_instance.exec.assert_called()

    def test_set_user_level_calls_main_window(self, menu_bar_manager, mock_main_window):
        """Test set_user_level calls main_window.set_user_level."""
        with patch('brian2sim.ui.menu_bar.QMessageBox'):
            menu_bar_manager.set_user_level("advanced")
            
            mock_main_window.set_user_level.assert_called_once_with("advanced")

    def test_toggle_tab_visibility_essential_tabs(self, menu_bar_manager, mock_main_window):
        """Test that essential tabs cannot be hidden."""
        with patch('brian2sim.ui.menu_bar.QMessageBox') as mock_msgbox:
            menu_bar_manager.toggle_tab_visibility("core")
            
            # Should show information that it can't be hidden
            mock_msgbox.information.assert_called()

    def test_copy_to_clipboard(self, menu_bar_manager, mock_main_window):
        """Test copy_to_clipboard function."""
        with patch('PyQt6.QtWidgets.QApplication') as mock_app, \
             patch('brian2sim.ui.menu_bar.QMessageBox'):
            
            mock_clipboard = Mock()
            mock_app.clipboard.return_value = mock_clipboard
            
            menu_bar_manager.copy_to_clipboard("test code")
            
            mock_clipboard.setText.assert_called_once_with("test code")

    def test_run_simulation(self, menu_bar_manager, mock_main_window):
        """Test run_simulation calls simulation_manager.start_simulation."""
        mock_main_window.simulation_manager = Mock()
        mock_main_window.simulation_manager.start_simulation = Mock()
        
        menu_bar_manager.run_simulation()
        
        mock_main_window.simulation_manager.start_simulation.assert_called_once()


class TestValidationResultParameter:
    """Test that ValidationResult has the parameter attribute."""

    def test_validation_result_has_parameter(self):
        """Test ValidationResult constructor includes parameter."""
        result = ValidationResult(
            is_valid=False,
            message="Error message",
            severity="error",
            parameter="my_param"
        )
        assert result.parameter == "my_param"
        assert result.message == "Error message"
        assert result.severity == "error"
        assert result.is_valid is False

    def test_validation_result_default_parameter(self):
        """Test ValidationResult has empty default for parameter."""
        result = ValidationResult(is_valid=True, message="OK")
        assert result.parameter == ""


class TestConfigManagerSaveToFile:
    """Test ConfigManager.save_config_to_file method."""

    def test_save_config_to_file_exists(self):
        """Test that save_config_to_file method exists."""
        from brian2sim.core.config_manager import ConfigManager
        
        main_window = Mock()
        cm = ConfigManager(main_window)
        
        assert hasattr(cm, 'save_config_to_file')

    def test_save_config_to_file_calls_save_config(self):
        """Test save_config_to_file calls save_config with gathered config."""
        from brian2sim.core.config_manager import ConfigManager
        
        main_window = Mock()
        # Mock necessary attributes for _get_current_config
        main_window.neuron_models_manager.get_neuron_model_config.return_value = {}
        main_window.sim_params_manager.get_sim_params_config.return_value = {}
        
        cm = ConfigManager(main_window)
        cm.save_config = Mock()
        cm._get_current_config = Mock(return_value={"test": "config"})
        
        cm.save_config_to_file("/path/to/file.json")
        
        cm.save_config.assert_called_once_with({"test": "config"}, "/path/to/file.json")
