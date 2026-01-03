"""
Results Manager for Brian2 neural network simulator.
Handles visualization and management of simulation results.
"""

import os
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout

# Handle optional matplotlib imports
# Handle optional matplotlib imports
try:
    import matplotlib
    matplotlib.use('QtAgg')  # Use interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Handle optional numpy import
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from brian2sim.ui.tabs.simulation_ui import create_plot_widget


class ResultsManager:
    """Manager for simulation results visualization and export."""

    def __init__(self, main_window):
        self.main_window = main_window
        self.current_results = None
        self.dynamic_widgets = {}  # Store references to dynamically created plot widgets

    def update_plots(self, results_data):
        """Update all plot displays with new simulation results."""
        self.current_results = results_data

        if not MATPLOTLIB_AVAILABLE:
            self._show_no_matplotlib_message()
            return

        try:
            # Update spike raster plot
            self._update_raster_plot(results_data)

            # Update voltage traces plot
            self._update_voltage_plot(results_data)
            
            # Dynamic Plots from raw_data
            if "raw_data" in results_data:
                for key, info in results_data["raw_data"].items():
                    # Skip if it's the standard voltage/spikes which are handled above
                    # (Unless we want to double plot? No, standard ones are fine)
                    if key in ["spike_monitor", "state_monitor_v"]:
                         continue
                         
                    if info.get("type") == "trace":
                        self._update_generic_trace_plot(key, info)

            # Update analysis plots
            self._update_psth_plot(results_data)
            self._update_fft_plot(results_data)
            self._update_isi_plot(results_data)
                        
        except Exception as e:
            print(f"Error updating plots: {e}")

    def update_statistics(self, results_data):
        """Update statistics display with new simulation results."""
        if not hasattr(self.main_window, "statistics_widget"):
            return

        try:
            stats_text = self._calculate_statistics(results_data)
            self.main_window.statistics_widget.stats_text.setPlainText(stats_text)
        except Exception as e:
            print(f"Error updating statistics: {e}")

    def clear_results(self):
        """Clear all results displays."""
        self.current_results = None

        # Clear plots
        widgets = [
            "raster_plot_widget",
            "voltage_plot_widget",
            "psth_plot_widget",
            "fft_plot_widget",
            "isi_plot_widget",
        ]
        
        for widget_name in widgets:
            if hasattr(self.main_window, widget_name):
                self._clear_plot_widget(getattr(self.main_window, widget_name))

        # Clear statistics
        if hasattr(self.main_window, "statistics_widget"):
            self.main_window.statistics_widget.stats_text.setPlainText(
                "Statistics will appear here after simulation..."
            )

    def export_plots(self, directory):
        """Export current plots to image files."""
        if not self.current_results or not MATPLOTLIB_AVAILABLE:
            return []

        exported_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        plot_map = {
            "raster_plot_widget": "spike_raster",
            "voltage_plot_widget": "voltage_traces",
            "psth_plot_widget": "psth_plot",
            "fft_plot_widget": "fft_plot",
            "isi_plot_widget": "isi_histogram"
        }

        try:
            for widget_name, file_prefix in plot_map.items():
                if hasattr(self.main_window, widget_name):
                    widget = getattr(self.main_window, widget_name)
                    if widget.figure:
                        filename = os.path.join(directory, f"{file_prefix}_{timestamp}.png")
                        widget.figure.savefig(filename, dpi=300, bbox_inches="tight")
                        exported_files.append(filename)

        except Exception as e:
            print(f"Error exporting plots: {e}")

        return exported_files

    def _update_raster_plot(self, results_data):
        """Update the spike raster plot."""
        if not hasattr(self.main_window, "raster_plot_widget"):
            return

        widget = self.main_window.raster_plot_widget
        if not widget.figure:
            return

        # Clear previous plot
        widget.figure.clear()

        # Create new axes
        ax = widget.figure.add_subplot(111)

        # Get spike data from raw_data
        raw = results_data.get("raw_data", {})
        spikes_data = raw.get("spike_monitor", {})
        spike_times = spikes_data.get("t", [])
        spike_indices = spikes_data.get("i", [])

        if len(spike_times) > 0 and len(spike_indices) > 0:
            # Create raster plot
            ax.scatter(spike_times, spike_indices, s=10, alpha=0.7, c="black")
            ax.set_xlabel("Time (ms)")
            ax.set_ylabel("Neuron Index")
            ax.set_title(f"Spike Raster Plot ({len(spike_times)} spikes)")
            ax.grid(True, alpha=0.3)

            # Set reasonable limits
            if len(spike_times) > 0:
                ax.set_xlim(0, max(spike_times) * 1.05)
            if len(spike_indices) > 0:
                ax.set_ylim(-0.5, max(spike_indices) + 0.5)
        else:
            # No spikes to display
            ax.text(
                0.5,
                0.5,
                "No spikes detected",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=12,
            )
            ax.set_xlabel("Time (ms)")
            ax.set_ylabel("Neuron Index")
            ax.set_title("Spike Raster Plot")

        widget.figure.tight_layout()
        widget.canvas.draw()

    def _update_voltage_plot(self, results_data):
        """Update the voltage traces plot."""
        if not hasattr(self.main_window, "voltage_plot_widget"):
            return

        widget = self.main_window.voltage_plot_widget
        if not widget.figure:
            return

        # Clear previous plot
        widget.figure.clear()

        # Create new axes
        ax = widget.figure.add_subplot(111)

        # Get voltage data from raw_data
        raw = results_data.get("raw_data", {})
        v_data = raw.get("state_monitor_v", {})
        voltage_times = v_data.get("t", [])
        
        voltage_traces = {}
        values = v_data.get("values")
        indices = v_data.get("indices", [])
        
        if values is not None and len(values) > 0:
            # Limit to first 20 traces if many
            n_traces = min(len(values), 20)
            for i in range(n_traces):
                nid = indices[i] if i < len(indices) else i
                # Convert V to mV for display
                voltage_traces[int(nid)] = values[i] * 1000

        if len(voltage_times) > 0 and voltage_traces:
            # Plot voltage traces for each monitored neuron
            colors = ["blue", "red", "green", "orange", "purple", "brown", "pink", "gray"]

            for i, (neuron_id, trace) in enumerate(voltage_traces.items()):
                if len(voltage_times) == len(trace):
                    color = colors[i % len(colors)]
                    ax.plot(
                        voltage_times,
                        trace,
                        label=f"Neuron {neuron_id}",
                        color=color,
                        linewidth=1.5,
                        alpha=0.8,
                    )

            ax.set_xlabel("Time (ms)")
            ax.set_ylabel("Membrane Voltage (mV)")
            ax.set_title("Membrane Voltage Traces")
            ax.grid(True, alpha=0.3)

            # Add legend if multiple traces
            if len(voltage_traces) > 1:
                ax.legend(loc="upper right", fontsize=8)

            # Set reasonable y-limits for voltage
            if NUMPY_AVAILABLE:
                all_voltages = []
                for trace in voltage_traces.values():
                    all_voltages.extend(trace)
                if all_voltages:
                    v_min, v_max = min(all_voltages), max(all_voltages)
                    v_range = v_max - v_min
                    ax.set_ylim(v_min - 0.1 * v_range, v_max + 0.1 * v_range)
        else:
            # No voltage data to display
            ax.text(
                0.5,
                0.5,
                "No voltage data available",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=12,
            )
            ax.set_xlabel("Time (ms)")
            ax.set_ylabel("Membrane Voltage (mV)")
            ax.set_title("Membrane Voltage Traces")

        widget.figure.tight_layout()
        widget.canvas.draw()

    def _update_psth_plot(self, results_data):
        """Update the Population Statistics (PSTH) plot."""
        if not hasattr(self.main_window, "psth_plot_widget") or not NUMPY_AVAILABLE:
            return
            
        widget = self.main_window.psth_plot_widget
        if not widget.figure: return
        widget.figure.clear()
        ax = widget.figure.add_subplot(111)
        
        raw = results_data.get("raw_data", {})
        spikes = raw.get("spike_monitor", {})
        spike_times = spikes.get("t")
        
        if spike_times is None or len(spike_times) == 0:
            self._show_no_data(ax, "No spikes for PSTH")
        else:
            sim_params = results_data.get("parameters", {}).get("simulation", {})
            sim_time = sim_params.get("sim_time", 100)
            num_neurons = sim_params.get("num_neurons", 1)
            
            # Binning (e.g., 5ms bins)
            bin_width = 5.0 # ms
            bins = np.arange(0, sim_time + bin_width, bin_width)
            hist, _ = np.histogram(spike_times, bins=bins)
            
            # Convert to Rate (Hz/neuron)
            # rate = count / (bin_width_s * num_neurons)
            rate = hist / ((bin_width / 1000.0) * num_neurons)
            centers = (bins[:-1] + bins[1:]) / 2
            
            ax.plot(centers, rate, color='black', linewidth=1.5)
            ax.set_xlabel("Time (ms)")
            ax.set_ylabel("Population Rate (Hz)")
            ax.set_title(f"Population Rate (bin={bin_width}ms)")
            ax.grid(True, alpha=0.3)
            
        widget.figure.tight_layout()
        widget.canvas.draw()
        
    def _update_fft_plot(self, results_data):
        """Update the Power Spectrum (FFT) plot."""
        if not hasattr(self.main_window, "fft_plot_widget") or not NUMPY_AVAILABLE:
            return
            
        widget = self.main_window.fft_plot_widget
        if not widget.figure: return
        widget.figure.clear()
        ax = widget.figure.add_subplot(111)
        
        raw = results_data.get("raw_data", {})
        spikes = raw.get("spike_monitor", {})
        spike_times = spikes.get("t")
        
        if spike_times is None or len(spike_times) < 10:
             self._show_no_data(ax, "Insufficient data for FFT")
        else:
            sim_params = results_data.get("parameters", {}).get("simulation", {})
            sim_time = sim_params.get("sim_time", 100)
            
            # Use finer bins for FFT (e.g. 1ms) to capture higher freqs
            bin_width = 1.0 # ms
            fs = 1000.0 / bin_width # Sample rate (Hz)
            
            bins = np.arange(0, sim_time + bin_width, bin_width)
            hist, _ = np.histogram(spike_times, bins=bins)
            
            # FFT
            n = len(hist)
            fft_vals = np.fft.rfft(hist - np.mean(hist)) # Remove DC component
            power = np.abs(fft_vals)**2
            freqs = np.fft.rfftfreq(n, d=1/fs)
            
            # Smooth curve (optional)
            try:
                from scipy.ndimage import gaussian_filter1d
                power = gaussian_filter1d(power, sigma=2.0)
            except ImportError:
                # Scipy not available, skip smoothing
                pass
            
            # Plot 0-100Hz (Brain rhythms range)
            mask = (freqs > 1) & (freqs < 100)
            ax.plot(freqs[mask], power[mask], color='purple')
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("Power")
            ax.set_title("Population Power Spectrum")
            ax.grid(True, alpha=0.3)
            
        widget.figure.tight_layout()
        widget.canvas.draw()
        
    def _update_isi_plot(self, results_data):
        """Update Inter-Spike Interval Histogram."""
        if not hasattr(self.main_window, "isi_plot_widget") or not NUMPY_AVAILABLE:
            return
            
        widget = self.main_window.isi_plot_widget
        if not widget.figure: return
        widget.figure.clear()
        ax = widget.figure.add_subplot(111)
        
        raw = results_data.get("raw_data", {})
        spikes = raw.get("spike_monitor", {})
        spike_times = spikes.get("t")
        spike_indices = spikes.get("i")
        
        if spike_times is None or len(spike_times) < 50:
            self._show_no_data(ax, "Insufficient spikes for ISI")
        else:
            # Calculate ISIs per neuron
            isis = []
            
            # This can be slow for many spikes/neurons
            # Optimization: Sort by index AND time to ensure correct ISIs
            # lexsort sorts by the last key first (primary), so we pass (spike_times, spike_indices)
            sort_idx = np.lexsort((spike_times, spike_indices))
            sorted_times = spike_times[sort_idx]
            sorted_indices = spike_indices[sort_idx]
            
            # Find split points
            _, start_indices = np.unique(sorted_indices, return_index=True)
            
            # Vectorized approach or loop over neurons?
            # Creating split arrays
            neuron_spike_groups = np.split(sorted_times, start_indices[1:])
            
            for group in neuron_spike_groups:
                if len(group) > 1:
                    # Differences between consecutive spikes
                    diffs = np.diff(group)
                    isis.extend(diffs)
            
            isis = np.array(isis)
            
            if len(isis) > 0:
                # Plot Histogram (Log scale often better, but linear standard first)
                # Cap at 200ms for visibility of bursting/regularity
                ax.hist(isis, bins=50, range=(0, 200), color='green', alpha=0.7)
                ax.set_xlabel("Inter-Spike Interval (ms)")
                ax.set_ylabel("Count")
                ax.set_title("ISI Distribution")
                ax.grid(True, alpha=0.3)
                
                # Add stats
                cv = np.std(isis) / np.mean(isis) if np.mean(isis) > 0 else 0
                ax.text(0.7, 0.8, f"CV: {cv:.2f}", transform=ax.transAxes, 
                        bbox=dict(facecolor='white', alpha=0.8))
            else:
                 self._show_no_data(ax, "No repeated spikes found")
            
        widget.figure.tight_layout()
        widget.canvas.draw()

    def _show_no_data(self, ax, message):
        ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes, color="gray")
        ax.set_xticks([])
        ax.set_yticks([])

    def _update_generic_trace_plot(self, key, info):
        """Update or create a generic trace plot for custom variables."""
        # Clean key for display (e.g. state_monitor_g_Ca -> g_Ca)
        display_name = key.replace("state_monitor_", "").replace("monitor_", "")
        
        # Check if widget exists
        if key not in self.dynamic_widgets:
            # check if main window has results tabs
            if not hasattr(self.main_window, "results_tabs"): return
            
            # Create new widget
            widget = create_plot_widget(f"{display_name} Traces")
            self.main_window.results_tabs.addTab(widget, display_name)
            self.dynamic_widgets[key] = widget
            
        widget = self.dynamic_widgets[key]
        if not widget.figure: return
        
        # Clear
        widget.figure.clear()
        ax = widget.figure.add_subplot(111)
        
        # Data
        t = info.get("t")
        values = info.get("values")
        unit = info.get("unit", "")
        indices = info.get("indices", [])
        
        if t is not None and values is not None:
            # Plot first 20 traces
            num_traces = min(len(values), 20)
            colors = ["blue", "red", "green", "orange", "purple", "brown", "pink", "gray"]
            
            for i in range(num_traces):
                neuron_idx = indices[i] if len(indices) > i else i
                color = colors[i % len(colors)]
                ax.plot(
                    t, 
                    values[i], 
                    label=f"Neuron {neuron_idx}",
                    color=color,
                    alpha=0.7,
                    linewidth=1.0
                )
            
            ax.set_xlabel("Time (ms)")
            ax.set_ylabel(f"{display_name} ({unit})")
            ax.set_title(f"{display_name} Traces")
            ax.grid(True, alpha=0.3)
            
            if num_traces > 0:
                ax.legend(loc="upper right", fontsize=8)
                
        else:
            ax.text(0.5, 0.5, "No data", transform=ax.transAxes)
            
        widget.figure.tight_layout()
        widget.canvas.draw()

    def _calculate_statistics(self, results_data):
        """Calculate and format simulation statistics."""
        stats_lines = []

        # Basic simulation info
        stats_lines.append("=== SIMULATION STATISTICS ===\n")

        timestamp = results_data.get("timestamp", "Unknown")
        stats_lines.append(f"Timestamp: {timestamp}")
        stats_lines.append(f"Brian2 Available: {results_data.get('brian2_available', False)}")

        # Simulation parameters
        params = results_data.get("parameters", {})
        sim_params = params.get("simulation", {})

        if sim_params:
            stats_lines.append(f"\nSimulation Duration: {sim_params.get('sim_time', 'N/A')} ms")
            stats_lines.append(f"Number of Neurons: {sim_params.get('num_neurons', 'N/A')}")
            stats_lines.append(f"Input Current: {sim_params.get('input_current', 'N/A')} nA")

        # Neuron model info
        neuron_params = params.get("neuron_model", {})
        if neuron_params:
            stats_lines.append(f"Neuron Model: {neuron_params.get('model_key', 'N/A')}")

        # Spike statistics
        raw = results_data.get("raw_data", {})
        spikes_data = raw.get("spike_monitor", {})
        spike_times = spikes_data.get("t", [])
        spike_indices = spikes_data.get("i", [])

        stats_lines.append(f"\n=== SPIKE ANALYSIS ===")
        stats_lines.append(f"Total Spikes: {len(spike_times)}")

        if len(spike_times) > 0 and sim_params.get("sim_time"):
            sim_duration_s = sim_params["sim_time"] / 1000.0  # Convert ms to seconds
            num_neurons = int(sim_params.get("num_neurons", 1))
            total_firing_rate = len(spike_times) / sim_duration_s
            avg_firing_rate = total_firing_rate / max(1, num_neurons)
            stats_lines.append(f"Overall Firing Rate: {avg_firing_rate:.2f} Hz")

        # Per-neuron statistics
        if len(spike_indices) > 0:
            unique_neurons = set(spike_indices)
            stats_lines.append(f"Active Neurons: {len(unique_neurons)}")

            if len(unique_neurons) > 0:
                stats_lines.append(f"\nPer-Neuron Spike Counts:")
                neuron_spike_counts = {}
                for idx in spike_indices:
                    neuron_spike_counts[idx] = neuron_spike_counts.get(idx, 0) + 1

                for neuron_id in sorted(neuron_spike_counts.keys()):
                    count = neuron_spike_counts[neuron_id]
                    if sim_params.get("sim_time"):
                        rate = count / (sim_params["sim_time"] / 1000.0)
                        stats_lines.append(f"  Neuron {neuron_id}: {count} spikes ({rate:.2f} Hz)")
                    else:
                        stats_lines.append(f"  Neuron {neuron_id}: {count} spikes")

        # Network statistics
        network_params = params.get("network", {})
        if network_params and network_params.get("synaptic_connections", False):
            stats_lines.append(f"\n=== NETWORK FEATURES ===")
            stats_lines.append(f"Synaptic Connections: Enabled")
            stats_lines.append(f"Network Topology: {network_params.get('network_topology', 'N/A')}")
            stats_lines.append(
                f"Synaptic Weight: {network_params.get('synaptic_weight', 'N/A')} nA"
            )

        # Advanced features
        advanced_params = params.get("advanced", {})
        if advanced_params:
            stats_lines.append(f"\n=== ADVANCED FEATURES ===")
            for feature in ["dales_principle", "synaptic_delays", "stdp", "distance_connectivity"]:
                if feature in advanced_params and advanced_params[feature].get("enabled", False):
                    stats_lines.append(f"{feature.replace('_', ' ').title()}: Enabled")

        # Noise information
        noise_params = params.get("noise", {})
        if noise_params and noise_params.get("enabled", False):
            stats_lines.append(f"\n=== NOISE PARAMETERS ===")
            stats_lines.append(f"Noise Method: {noise_params.get('method', 'N/A')}")
            stats_lines.append(f"Noise Intensity: {noise_params.get('intensity', 'N/A')} nA")

        return "\n".join(stats_lines)

    def _clear_plot_widget(self, widget):
        """Clear a plot widget."""
        if not widget.figure:
            return

        widget.figure.clear()
        if MATPLOTLIB_AVAILABLE:
            # Add placeholder text
            ax = widget.figure.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                "No data to display",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=12,
                color="gray",
            )
            ax.set_xticks([])
            ax.set_yticks([])
            widget.canvas.draw()

    def _show_no_matplotlib_message(self):
        """Show message when matplotlib is not available."""
        if hasattr(self.main_window, "raster_plot_widget"):
            self._add_message_to_widget(
                self.main_window.raster_plot_widget,
                "matplotlib not available\nInstall matplotlib to view plots",
            )

        if hasattr(self.main_window, "voltage_plot_widget"):
            self._add_message_to_widget(
                self.main_window.voltage_plot_widget,
                "matplotlib not available\nInstall matplotlib to view plots",
            )

    def _add_message_to_widget(self, widget, message):
        """Add a text message to a widget."""
        # Clear existing layout
        layout = widget.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            layout = QVBoxLayout(widget)

        # Add message label
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(label)
