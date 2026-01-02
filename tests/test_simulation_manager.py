"""
Unit tests for SimulationManager class.
Tests simulation orchestration, progress tracking, and coordination.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtCore import QTimer
import numpy as np
import os
import shutil
import tempfile
from brian2sim.core.simulation_manager import SimulationManager


class TestSimulationManagerBasics:
    """Tests for basic SimulationManager functionality."""
    
    def test_manager_creation(self):
        """Test creating SimulationManager instance."""
        mock_window = Mock()
        manager = SimulationManager(mock_window)
        
        assert manager is not None
        assert manager.main_window == mock_window
        assert manager.is_running is False
        assert manager.simulation_engine is None
        
    def test_set_components(self):
        """Test setting engine and manager components."""
        mock_window = Mock()
        manager = SimulationManager(mock_window)
        
        mock_engine = Mock()
        mock_results = Mock()
        mock_generator = Mock()
        
        manager.set_components(mock_engine, mock_results, mock_generator)
        
        assert manager.simulation_engine == mock_engine
        assert manager.results_manager == mock_results
        assert manager.code_generator == mock_generator
        
    def test_signal_connections(self):
        """Test that signals are properly connected."""
        mock_window = Mock()
        manager = SimulationManager(mock_window)
        
        mock_engine = Mock()
        mock_engine.progress_updated = Mock()
        mock_engine.simulation_completed = Mock()
        mock_engine.simulation_error = Mock()
        
        manager.set_components(mock_engine, None, None)
        
        # Verify signal connections were made
        assert mock_engine.progress_updated.connect.called
        assert mock_engine.simulation_completed.connect.called
        assert mock_engine.simulation_error.connect.called


class TestSimulationLifecycle:
    """Tests for simulation start/stop/reset cycle."""
    
    def test_start_simulation_without_engine(self):
        """Test starting simulation without engine."""
        mock_window = Mock()
        mock_window.neuron_models_manager = Mock()
        mock_window.sim_params_manager = Mock()
        mock_window.noise_options_manager = Mock()
        mock_window.network_options_manager = Mock()
        
        # Configure mocks to return valid data
        mock_window.neuron_models_manager.get_neuron_model_config.return_value = {
            "model_key": "lif", "parameters": {}
        }
        mock_window.sim_params_manager.get_sim_params_config.return_value = {
            "num_neurons": 10, "sim_time": 100, "dt": 0.1
        }
        mock_window.noise_options_manager.get_noise_options_config.return_value = {"enabled": False}
        mock_window.network_options_manager.get_network_options_config.return_value = {"enabled": False}
        
        manager = SimulationManager(mock_window)
        
        # Should not crash without engine
        manager.start_simulation()
        assert manager.is_running is True
        
    def test_prevent_double_start(self):
        """Test that simulation can't be started twice."""
        mock_window = Mock()
        manager = SimulationManager(mock_window)
        manager.is_running = True
        
        manager.start_simulation()
        
        # Should emit warning and not proceed
        assert manager.is_running is True
        
    def test_stop_simulation(self):
        """Test stopping a running simulation."""
        mock_window = Mock()
        mock_window.simulation_progress_bar = Mock()
        mock_window.simulation_status_label = Mock()
        mock_window.run_button = Mock()
        mock_window.stop_button = Mock()
        
        manager = SimulationManager(mock_window)
        manager.is_running = True
        
        mock_engine = Mock()
        manager.set_components(mock_engine, None, None)
        
        manager.stop_simulation()
        
        assert mock_engine.stop_simulation.called
        assert manager.is_running is False
        
    def test_reset_simulation(self):
        """Test resetting simulation state."""
        mock_window = Mock()
        mock_window.simulation_progress_bar = Mock()
        mock_window.simulation_status_label = Mock()
        mock_window.elapsed_time_label = Mock()
        mock_window.remaining_time_label = Mock()
        
        manager = SimulationManager(mock_window)
        manager.simulation_data = {"some": "data"}
        
        mock_results = Mock()
        manager.set_components(None, mock_results, None)
        
        manager.reset_simulation()
        
        assert manager.simulation_data is None
        assert mock_results.clear_results.called


class TestProgressTracking:
    """Tests for progress tracking and UI updates."""
    
    def test_progress_timer_starts(self):
        """Test that progress timer starts with simulation."""
        mock_window = Mock()
        mock_window.neuron_models_manager = Mock()
        mock_window.sim_params_manager = Mock()
        mock_window.noise_options_manager = Mock()
        mock_window.network_options_manager = Mock()
        
        # Configure mocks
        mock_window.neuron_models_manager.get_neuron_model_config.return_value = {
            "model_key": "lif", "parameters": {}
        }
        mock_window.sim_params_manager.get_sim_params_config.return_value = {
            "num_neurons": 10, "sim_time": 100, "dt": 0.1
        }
        mock_window.noise_options_manager.get_noise_options_config.return_value = {"enabled": False}
        mock_window.network_options_manager.get_network_options_config.return_value = {"enabled": False}
        
        manager = SimulationManager(mock_window)
        manager.progress_timer = Mock()
        
        manager.start_simulation()
        
        assert manager.progress_timer.start.called
        
    def test_on_progress_updated(self):
        """Test progress update signal handling."""
        mock_window = Mock()
        
        manager = SimulationManager(mock_window)
        
        # Connect to signal to verify it's emitted
        received_signals = []
        manager.progress_updated.connect(lambda p, m: received_signals.append((p, m)))
        
        manager.on_progress_updated(50, "Running...")
        
        assert len(received_signals) == 1
        assert received_signals[0] == (50, "Running...")


class TestDataExport:
    """Tests for data export functionality."""
    
    @patch('brian2sim.core.simulation_manager.QFileDialog')
    def test_export_data_no_data(self, mock_dialog):
        """Test export when no data available."""
        mock_window = Mock()
        manager = SimulationManager(mock_window)
        manager.simulation_data = None
        
        with patch('brian2sim.core.simulation_manager.QMessageBox') as mock_msg:
            manager.export_data()
            assert mock_msg.warning.called
            
    @patch('brian2sim.core.simulation_manager.QMessageBox')
    @patch('brian2sim.core.simulation_manager.QFileDialog')
    def test_export_data_json(self, mock_dialog, mock_msgbox):
        """Test JSON export."""
        mock_window = Mock()
        manager = SimulationManager(mock_window)
        manager.simulation_data = {"spike_times": [10, 20, 30]}
        
        mock_dialog.getSaveFileName.return_value = ("test.json", "JSON Files (*.json)")
        
        with patch('builtins.open', create=True) as mock_open:
            manager.export_data()
            assert mock_open.called
            
    @patch('brian2sim.core.simulation_manager.QFileDialog')
    def test_export_plots(self, mock_dialog):
        """Test plot export."""
        mock_window = Mock()
        mock_window.results_tabs = Mock()
        
        manager = SimulationManager(mock_window)
        mock_results = Mock()
        mock_results.export_plots.return_value = ["plot1.png", "plot2.png"]
        
        manager.set_components(None, mock_results, None)
        
        mock_dialog.getExistingDirectory.return_value = "/test/dir"
        
        with patch('brian2sim.core.simulation_manager.QMessageBox'):
            manager.export_plots()
            assert mock_results.export_plots.called

    def test_export_csv_multifile(self):
        """Test that _export_to_csv creates multiple files for different data types."""
        mock_window = Mock()
        manager = SimulationManager(mock_window)
        
        # Prepare dummy data
        manager.simulation_data = {
            "raw_data": {
                "spike_monitor": {
                    "t": np.array([10, 20]),
                    "i": np.array([0, 1]),
                    "type": "spikes"
                },
                "state_monitor_v": {
                     "t": np.array([0, 0.1, 0.2]),
                     "values": np.array([
                        [-0.070, -0.060, -0.050], 
                        [-0.070, -0.065, -0.060]
                     ]),
                     "indices": np.array([0, 1]),
                     "type": "trace"
                },
                "state_monitor_g_Ca": {
                    "type": "trace",
                    "t": np.array([0, 0.1, 0.2]),
                    "values": np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]),
                    "indices": [0, 1],
                    "unit": "S"
                }
            }
        }
        
        test_dir = tempfile.mkdtemp()
        try:
            export_path = os.path.join(test_dir, "output.csv")
            
            # Mock _export_to_json to avoid side effects
            with patch.object(manager, '_export_to_json'):
                manager._export_to_csv(export_path)
                
            # Verify files exist
            expected_files = [
                "output_spike_monitor.csv",
                "output_state_monitor_v.csv",
                "output_state_monitor_g_Ca.csv"
            ]
            
            for fname in expected_files:
                fpath = os.path.join(test_dir, fname)
                assert os.path.exists(fpath), f"{fname} not created"
                
                # Check it's not empty
                with open(fpath, 'r') as f:
                    content = f.read()
                    assert len(content) > 0
                    
        finally:
            shutil.rmtree(test_dir)


class TestCodeGeneration:
    """Tests for code generation functionality."""
    
    @patch('brian2sim.core.simulation_manager.QMessageBox')
    @patch('brian2sim.core.simulation_manager.QFileDialog')
    def test_generate_code(self, mock_dialog, mock_msgbox):
        """Test standalone code generation."""
        mock_window = Mock()
        mock_window.neuron_models_manager = Mock()
        mock_window.sim_params_manager = Mock()
        mock_window.noise_options_manager = Mock()
        mock_window.network_options_manager = Mock()
        
        # Configure mocks
        mock_window.neuron_models_manager.get_neuron_model_config.return_value = {
            "model_key": "lif", "parameters": {}
        }
        mock_window.sim_params_manager.get_sim_params_config.return_value = {
            "num_neurons": 10, "sim_time": 100, "dt": 0.1
        }
        mock_window.noise_options_manager.get_noise_options_config.return_value = {"enabled": False}
        mock_window.network_options_manager.get_network_options_config.return_value = {"enabled": False}
        
        manager = SimulationManager(mock_window)
        
        mock_generator = Mock()
        mock_generator.generate_simulation_code.return_value = "# Brian2 code"
        manager.set_components(None, None, mock_generator)
        
        mock_dialog.getSaveFileName.return_value = ("test.py", "Python Files (*.py)")
        
        with patch('builtins.open', create=True):
            manager.generate_code()
            assert mock_generator.generate_simulation_code.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
