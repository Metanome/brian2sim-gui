"""
Comprehensive tests for ResultsManager class.
Tests plot generation, statistics calculation, and export functionality.
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from brian2sim.core.results_manager import ResultsManager, MATPLOTLIB_AVAILABLE, NUMPY_AVAILABLE


class TestResultsManagerBasics:
    """Tests for basic ResultsManager functionality."""
    
    def test_manager_creation(self):
        """Test creating ResultsManager instance."""
        mock_window = Mock()
        manager = ResultsManager(mock_window)
        
        assert manager is not None
        assert manager.main_window == mock_window
        assert manager.current_results is None
        
    def test_clear_results(self):
        """Test clearing results."""
        mock_window = Mock()
        mock_window.raster_plot_widget = Mock()
        mock_window.voltage_plot_widget = Mock()
        mock_window.statistics_widget = Mock()
        mock_window.statistics_widget.stats_text = Mock()
        
        manager = ResultsManager(mock_window)
        manager.current_results = {"some": "data"}
        
        manager.clear_results()
        
        assert manager.current_results is None


class TestPlotUpdates:
    """Tests for plot update functionality."""
    
    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="Matplotlib not available")
    def test_update_plots(self):
        """Test updating plots with results data."""
        mock_window = Mock()
        mock_window.raster_plot_widget = Mock()
        mock_window.raster_plot_widget.figure = MagicMock()
        mock_window.raster_plot_widget.canvas = Mock()
        
        mock_window.voltage_plot_widget = Mock()
        mock_window.voltage_plot_widget.figure = MagicMock()
        mock_window.voltage_plot_widget.canvas = Mock()
        
        manager = ResultsManager(mock_window)
        
        results_data = {
            "raw_data": {
                "spike_monitor": {
                    "t": [10, 20, 30, 40, 50],
                    "i": [0, 1, 0, 2, 1],
                    "type": "spikes"
                },
                "state_monitor_v": {
                    "t": [0, 0.1, 0.2, 0.3, 0.4],
                    "values": [
                        [-0.070, -0.065, -0.060, -0.065, -0.070],
                        [-0.070, -0.068, -0.066, -0.068, -0.070]
                    ],
                    "indices": [0, 1],
                    "type": "trace"
                }
            }
        }
        
        manager.update_plots(results_data)
        
        # Should update current results
        assert manager.current_results == results_data
        
    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="Matplotlib not available")
    def test_update_raster_plot_with_spikes(self):
        """Test raster plot update with spike data."""
        mock_window = Mock()
        mock_window.raster_plot_widget = Mock()
        mock_window.raster_plot_widget.figure = MagicMock()
        mock_window.raster_plot_widget.canvas = Mock()
        
        manager = ResultsManager(mock_window)
        
        results_data = {
            "raw_data": {
                "spike_monitor": {
                    "t": [10, 20, 30],
                    "i": [0, 1, 2],
                    "type": "spikes"
                }
            }
        }
        
        manager._update_raster_plot(results_data)
        
        # Verify plot was updated
        assert mock_window.raster_plot_widget.figure.clear.called
        assert mock_window.raster_plot_widget.canvas.draw.called
        
    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="Matplotlib not available")
    def test_update_raster_plot_no_spikes(self):
        """Test raster plot update with no spikes."""
        mock_window = Mock()
        mock_window.raster_plot_widget = Mock()
        mock_window.raster_plot_widget.figure = MagicMock()
        mock_window.raster_plot_widget.canvas = Mock()
        
        manager = ResultsManager(mock_window)
        
        results_data = {
            "raw_data": {}
        }
        
        manager._update_raster_plot(results_data)
        
        # Should still update plot with "no spikes" message
        assert mock_window.raster_plot_widget.canvas.draw.called
        
    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="Matplotlib not available")
    def test_update_voltage_plot(self):
        """Test voltage plot update."""
        mock_window = Mock()
        mock_window.voltage_plot_widget = Mock()
        mock_window.voltage_plot_widget.figure = MagicMock()
        mock_window.voltage_plot_widget.canvas = Mock()
        
        manager = ResultsManager(mock_window)
        
        results_data = {
            "raw_data": {
                "state_monitor_v": {
                    "t": [0, 0.1, 0.2],
                    "values": [
                        [-0.070, -0.065, -0.060],
                        [-0.070, -0.068, -0.066]
                    ],
                    "indices": [0, 1],
                    "type": "trace"
                }
            }
        }
        
        manager._update_voltage_plot(results_data)
        
        # Verify plot was updated
        assert mock_window.voltage_plot_widget.figure.clear.called
        assert mock_window.voltage_plot_widget.canvas.draw.called

    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="Matplotlib not available")
    def test_update_plots_dynamic(self):
        """Test dynamic plotting for raw data."""
        mock_window = Mock()
        # Mock results tabs
        mock_window.results_tabs = Mock()
        
        manager = ResultsManager(mock_window)
        
        # We need to clean up patches if any
        with patch('brian2sim.core.results_manager.create_plot_widget') as mock_create:
            mock_widget = MagicMock()
            mock_widget.figure = MagicMock()
            mock_create.return_value = mock_widget
            
            results_data = {
                "raw_data": {
                    "state_monitor_g_Ca": {
                        "type": "trace",
                        "t": [0, 1],
                        "values": [[0.1, 0.2]],
                        "unit": "S",
                        "indices": [0]
                    }
                }
            }
            
            # Mock other updates
            manager._update_raster_plot = Mock()
            manager._update_voltage_plot = Mock()
            
            manager.update_plots(results_data)
            
            # Check addTab called
            assert mock_window.results_tabs.addTab.called
            args = mock_window.results_tabs.addTab.call_args
            assert args[0][1] == "g_Ca"


class TestStatistics:
    """Tests for statistics calculation."""
    
    def test_update_statistics(self):
        """Test updating statistics display."""
        mock_window = Mock()
        mock_window.statistics_widget = Mock()
        mock_window.statistics_widget.stats_text = Mock()
        
        manager = ResultsManager(mock_window)
        
        results_data = {
            "raw_data": {
                "spike_monitor": {
                    "t": [10, 20, 30, 40, 50],
                    "i": [0, 1, 0, 2, 1]
                }
            }
        }
        
        manager.update_statistics(results_data)
        
        # Should update statistics text
        assert mock_window.statistics_widget.stats_text.setPlainText.called
        
    def test_calculate_statistics(self):
        """Test statistics calculation."""
        mock_window = Mock()
        manager = ResultsManager(mock_window)
        
        results_data = {
            "raw_data": {
                "spike_monitor": {
                    "t": [10, 20, 30, 40, 50],
                    "i": [0, 1, 0, 2, 1]
                }
            },
            "parameters": {"simulation": {"sim_time": 100}}
        }
        
        stats_text = manager._calculate_statistics(results_data)
        
        assert isinstance(stats_text, str)
        assert len(stats_text) > 0


class TestExportFunctionality:
    """Tests for export functionality."""
    
    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="Matplotlib not available")
    def test_export_plots(self):
        """Test exporting plots to files."""
        mock_window = Mock()
        mock_window.raster_plot_widget = Mock()
        mock_window.raster_plot_widget.figure = MagicMock()
        mock_window.voltage_plot_widget = Mock()
        mock_window.voltage_plot_widget.figure = MagicMock()
        
        manager = ResultsManager(mock_window)
        manager.current_results = {"spike_times": [10, 20]}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            exported = manager.export_plots(tmpdir)
            
            # Should return list of exported files
            assert isinstance(exported, list)
            
    def test_export_plots_no_results(self):
        """Test exporting plots with no results."""
        mock_window = Mock()
        manager = ResultsManager(mock_window)
        manager.current_results = None
        
        exported = manager.export_plots("/tmp")
        
        # Should return empty list
        assert exported == []
        
    def test_export_plots_no_matplotlib(self):
        """Test export behavior when matplotlib unavailable."""
        mock_window = Mock()
        manager = ResultsManager(mock_window)
        manager.current_results = {"spike_times": [10, 20]}
        
        with patch('brian2sim.core.results_manager.MATPLOTLIB_AVAILABLE', False):
            exported = manager.export_plots("/tmp")
            assert exported == []


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_update_plots_no_matplotlib(self):
        """Test plot update when matplotlib not available."""
        mock_window = Mock()
        manager = ResultsManager(mock_window)
        
        # Mock the message display method to avoid creating actual widgets
        with patch('brian2sim.core.results_manager.MATPLOTLIB_AVAILABLE', False):
            with patch.object(manager, '_show_no_matplotlib_message'):
                # Should not crash
                manager.update_plots({"spike_times": []})
            
    def test_update_statistics_no_widget(self):
        """Test statistics update when widget doesn't exist."""
        mock_window = Mock()
        del mock_window.statistics_widget  # Remove attribute
        
        manager = ResultsManager(mock_window)
        
        # Should not crash
        manager.update_statistics({"spike_times": []})
        
    def test_clear_results_missing_widgets(self):
        """Test clearing results when widgets missing."""
        mock_window = Mock()
        # No plot widgets
        
        manager = ResultsManager(mock_window)
        manager.current_results = {"data": "value"}
        
        # Should not crash
        manager.clear_results()
        assert manager.current_results is None
        
    def test_update_plots_with_error(self):
        """Test plot update handles errors gracefully."""
        mock_window = Mock()
        mock_window.raster_plot_widget = Mock()
        mock_window.raster_plot_widget.figure = Mock(side_effect=Exception("Plot error"))
        
        manager = ResultsManager(mock_window)
        
        # Should not crash
        manager.update_plots({"spike_times": [10, 20]})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
