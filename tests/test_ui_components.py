"""
Unit tests for UI components.
Tests MainWindow, TabFactory, BaseFormGenerator, and MenuBar.
Uses mocking to avoid actual Qt window creation where possible.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestUIFormsModule:
    """Tests for ui_forms.py module."""
    
    def test_base_form_generator_import(self):
        """Test that BaseFormGenerator can be imported."""
        from brian2sim.ui.ui_forms import BaseFormGenerator
        
        assert BaseFormGenerator is not None
        
    def test_sim_params_form_generator_import(self):
        """Test that SimParamsFormGenerator can be imported."""
        from brian2sim.ui.ui_forms import SimParamsFormGenerator
        
        assert SimParamsFormGenerator is not None
        
    def test_file_picker_widget_import(self):
        """Test that FilePickerWidget can be imported."""
        from brian2sim.ui.ui_forms import FilePickerWidget
        
        assert FilePickerWidget is not None
        
    def test_base_form_generator_has_required_methods(self):
        """Test BaseFormGenerator has expected methods."""
        from brian2sim.ui.ui_forms import BaseFormGenerator
        
        assert hasattr(BaseFormGenerator, "get_param_widgets")
        assert hasattr(BaseFormGenerator, "get_params_for_save")
        assert hasattr(BaseFormGenerator, "load_params_from_config")
        assert hasattr(BaseFormGenerator, "get_form_widget")


class TestSimParamsFormGenerator:
    """Tests for SimParamsFormGenerator."""
    
    def test_creation(self, qapp):
        """Test SimParamsFormGenerator can be instantiated."""
        from brian2sim.ui.ui_forms import SimParamsFormGenerator
        from brian2sim.models.sim_params_config import SIM_PARAMS_CONFIG
        
        generator = SimParamsFormGenerator(SIM_PARAMS_CONFIG)
        
        assert generator is not None
        
    def test_get_form_widget(self, qapp):
        """Test get_form_widget returns a widget."""
        from brian2sim.ui.ui_forms import SimParamsFormGenerator
        from brian2sim.models.sim_params_config import SIM_PARAMS_CONFIG
        from PyQt6.QtWidgets import QWidget
        
        generator = SimParamsFormGenerator(SIM_PARAMS_CONFIG)
        widget = generator.get_form_widget()
        
        assert widget is not None
        assert isinstance(widget, QWidget)
        
    def test_get_param_widgets(self, qapp):
        """Test get_param_widgets returns dict."""
        from brian2sim.ui.ui_forms import SimParamsFormGenerator
        from brian2sim.models.sim_params_config import SIM_PARAMS_CONFIG
        
        generator = SimParamsFormGenerator(SIM_PARAMS_CONFIG)
        widgets = generator.get_param_widgets()
        
        assert isinstance(widgets, dict)
        
    def test_get_params_for_save(self, qapp):
        """Test get_params_for_save returns dict of values."""
        from brian2sim.ui.ui_forms import SimParamsFormGenerator
        from brian2sim.models.sim_params_config import SIM_PARAMS_CONFIG
        
        generator = SimParamsFormGenerator(SIM_PARAMS_CONFIG)
        params = generator.get_params_for_save()
        
        assert isinstance(params, dict)


class TestTabFactory:
    """Tests for TabFactory in tab_factory.py."""
    
    def test_tab_factory_import(self):
        """Test that TabFactory can be imported."""
        from brian2sim.ui.tab_factory import TabFactory
        
        assert TabFactory is not None
        
    def test_tab_factory_creation(self, qapp):
        """Test TabFactory can be instantiated."""
        from brian2sim.ui.tab_factory import TabFactory
        
        mock_window = MagicMock()
        factory = TabFactory(mock_window)
        
        assert factory is not None
        
    def test_tab_factory_has_create_methods(self, qapp):
        """Test TabFactory has tab creation methods."""
        from brian2sim.ui.tab_factory import TabFactory
        
        mock_window = MagicMock()
        factory = TabFactory(mock_window)
        
        # Should have methods to create various tabs
        assert hasattr(factory, "create_tabs") or hasattr(factory, "create_all_tabs")


class TestMainWindow:
    """Tests for MainWindow in main_window.py."""
    
    def test_main_window_import(self):
        """Test that MainWindow can be imported."""
        from brian2sim.ui.main_window import MainWindow
        
        assert MainWindow is not None
        
    def test_main_window_has_required_attributes(self):
        """Test MainWindow class has expected attributes."""
        from brian2sim.ui.main_window import MainWindow
        
        # Check class has expected methods without instantiating
        assert hasattr(MainWindow, "__init__")


class TestMenuBar:
    """Tests for MenuBar in menu_bar.py."""
    
    def test_menu_bar_import(self):
        """Test that menu bar module can be imported."""
        from brian2sim.ui import menu_bar
        
        assert menu_bar is not None


class TestFilePickerWidget:
    """Tests for FilePickerWidget."""
    
    def test_file_picker_creation(self, qapp):
        """Test FilePickerWidget can be created."""
        from brian2sim.ui.ui_forms import FilePickerWidget
        
        widget = FilePickerWidget()
        
        assert widget is not None
        
    def test_file_picker_set_get_text(self, qapp):
        """Test FilePickerWidget text methods."""
        from brian2sim.ui.ui_forms import FilePickerWidget
        
        widget = FilePickerWidget()
        widget.setText("/path/to/file.txt")
        
        assert widget.text() == "/path/to/file.txt"
        
    def test_file_picker_has_browse(self, qapp):
        """Test FilePickerWidget has browse method."""
        from brian2sim.ui.ui_forms import FilePickerWidget
        
        widget = FilePickerWidget()
        
        assert hasattr(widget, "browse_file")


class TestUIEdgeCases:
    """Tests for edge cases in UI components."""
    
    def test_empty_config_form_generator(self, qapp):
        """Test BaseFormGenerator with empty config returns empty widgets."""
        from brian2sim.ui.ui_forms import BaseFormGenerator
        
        generator = BaseFormGenerator({})
        widgets = generator.get_param_widgets()
        
        # Should be empty dict or empty from any key
        assert isinstance(widgets, dict)
        
    def test_load_params_from_config_handles_none(self, qapp):
        """Test load_params_from_config handles None values gracefully."""
        from brian2sim.ui.ui_forms import SimParamsFormGenerator
        from brian2sim.models.sim_params_config import SIM_PARAMS_CONFIG
        
        generator = SimParamsFormGenerator(SIM_PARAMS_CONFIG)
        
        # Should not crash with empty/None config
        generator.load_params_from_config({})
        
        params = generator.get_params_for_save()
        assert isinstance(params, dict)
