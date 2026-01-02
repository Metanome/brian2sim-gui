"""
Simulation Engine for Brian2 neural network simulator.
Handles the actual execution of Brian2 simulations with progress reporting.

This module uses modular builder classes for constructing simulation components.
"""

import time
from datetime import datetime

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

# Handle Brian2 import
try:
    import brian2 as b2
    import numpy as np

    BRIAN2_AVAILABLE = True
except ImportError:
    BRIAN2_AVAILABLE = False
    import numpy as np

# Import builder classes
from brian2sim.core.engine.input_builder import InputBuilder
from brian2sim.core.engine.monitor_builder import MonitorBuilder
from brian2sim.core.engine.neuron_builder import NeuronBuilder
from brian2sim.core.engine.plasticity_builder import PlasticityBuilder
from brian2sim.core.engine.synapse_builder import SynapseBuilder


class SimulationEngine(QObject):
    """
    Engine for executing Brian2 neural network simulations.

    This class orchestrates the simulation by delegating component construction
    to specialized builder classes, then running the assembled network.
    """

    # Signals for progress and completion
    progress_updated = pyqtSignal(int, str)
    simulation_completed = pyqtSignal(bool, dict)
    simulation_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.should_stop = False
        self.current_simulation = None

        # Progress tracking
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress)
        self.simulation_start_time = None
        self.total_simulation_time = 0

        # Initialize builder instances
        self.neuron_builder = NeuronBuilder()
        self.input_builder = InputBuilder()
        self.synapse_builder = SynapseBuilder()
        self.plasticity_builder = PlasticityBuilder()
        self.monitor_builder = MonitorBuilder()

        # Simulation objects
        self.network = None
        self.neurons = None
        self.synapses = None
        self.gap_junctions = None
        self.monitors = None

    def run_simulation(self, params):
        """Run the Brian2 simulation with given parameters."""
        if self.is_running:
            self.simulation_error.emit("Simulation already running")
            return

        if not BRIAN2_AVAILABLE:
            return self._run_dummy_simulation(params)

        self.is_running = True
        self.should_stop = False
        self.simulation_start_time = time.time()

        try:
            sim_params = params.get("simulation", {})
            self.total_simulation_time = sim_params.get("sim_time", 100)

            self.progress_timer.start(250)
            results = self._execute_brian2_simulation(params)
            self.progress_timer.stop()

            if self.should_stop:
                self.simulation_completed.emit(False, {})
            else:
                self.progress_updated.emit(100, "Simulation completed")
                self.simulation_completed.emit(True, results)

        except Exception as e:
            self.progress_timer.stop()
            self.simulation_error.emit(str(e))
        finally:
            self.is_running = False
            self.should_stop = False

    def stop_simulation(self):
        """Request simulation stop."""
        self.should_stop = True
        if self.progress_timer.isActive():
            self.progress_timer.stop()

    def _execute_brian2_simulation(self, params):
        """Execute the actual Brian2 simulation using builder classes."""
        # Initialize timing for standalone calls (used in tests)
        if self.simulation_start_time is None:
            self.simulation_start_time = time.time()

        try:
            self.progress_updated.emit(5, "Initializing Brian2...")

            if not BRIAN2_AVAILABLE:
                raise ImportError(
                    "Brian2 is not available. Please install Brian2: pip install brian2"
                )

            # Set performance mode
            sim_params = params.get("simulation", {})
            performance_mode = sim_params.get("performance_mode", "python")

            if performance_mode == "cpp_standalone":
                b2.set_device("cpp_standalone", build_on_run=True)
            elif performance_mode == "cpp_parallel":
                b2.set_device("cpp_standalone", build_on_run=True)
                b2.prefs.devices.cpp_standalone.openmp_threads = 4
            else:
                b2.prefs.codegen.target = "numpy"

            b2.start_scope()

            # Extract all parameters
            neuron_params = params.get("neuron_model", {})
            noise_params = params.get("noise", {})
            network_params = params.get("network", {})
            advanced_params = params.get("advanced_network", {})
            input_patterns_params = params.get("input_patterns", {})
            synaptic_receptors_params = params.get("synaptic_receptors", {})
            short_term_plasticity_params = params.get("short_term_plasticity", {})
            calcium_dynamics_params = params.get("calcium_dynamics", {})
            gap_junctions_params = params.get("gap_junctions", {})
            homeostatic_plasticity_params = params.get("homeostatic_plasticity", {})
            neuromodulation_params = params.get("neuromodulation", {})
            multicompartment_params = params.get("multicompartment", {})
            monitors_params = params.get("monitors", {})

            # Validate critical parameters
            sim_time_val = sim_params.get("sim_time")
            if sim_time_val is None or sim_time_val <= 0:
                raise ValueError("Invalid simulation time. Must be a positive number.")

            num_neurons_val = sim_params.get("num_neurons")
            if num_neurons_val is None or num_neurons_val <= 0:
                raise ValueError("Invalid number of neurons. Must be a positive integer.")

            # ===== BUILD NEURONS =====
            self.progress_updated.emit(10, "Building neuron model...")
            self.neurons = self.neuron_builder.build_neurons(
                sim_params, neuron_params, calcium_dynamics_params, multicompartment_params
            )

            if self.neurons is None:
                raise RuntimeError("Failed to build neuron model.")

            if self.should_stop:
                return {}

            # ===== SETUP INPUT CURRENT =====
            self.progress_updated.emit(25, "Configuring input currents...")
            model_type = neuron_params.get("model_key", "lif")
            self.input_builder.setup_input_current(sim_params, self.neurons, model_type)


            # ===== SETUP NOISE =====
            self.progress_updated.emit(35, "Adding noise...")
            self.input_builder.setup_noise(noise_params, self.neurons)

            # ===== SETUP INPUT PATTERNS =====
            self.progress_updated.emit(40, "Setting up input patterns...")
            input_sources = self.input_builder.setup_input_patterns(
                input_patterns_params, self.neurons
            )

            if self.should_stop:
                return {}

            # ===== BUILD NETWORK =====
            self.progress_updated.emit(45, "Building network connections...")
            self.synapses = self.synapse_builder.build_network(
                network_params,
                advanced_params,
                synaptic_receptors_params,
                short_term_plasticity_params,
                calcium_dynamics_params,
                self.neurons,
            )

            # ===== BUILD GAP JUNCTIONS =====
            self.progress_updated.emit(50, "Building gap junctions...")
            self.gap_junctions = self.synapse_builder.build_gap_junctions(
                gap_junctions_params, self.neurons
            )

            # ===== SETUP HOMEOSTATIC PLASTICITY =====
            self.progress_updated.emit(52, "Setting up homeostatic plasticity...")
            homeostatic_mechanisms = self.plasticity_builder.setup_homeostatic_plasticity(
                homeostatic_plasticity_params, self.neurons, self.synapses
            )

            # ===== SETUP NEUROMODULATION =====
            self.progress_updated.emit(54, "Setting up neuromodulation...")
            neuromodulation_systems = self.plasticity_builder.setup_neuromodulation(
                neuromodulation_params, self.neurons, self.synapses
            )

            if self.should_stop:
                return {}

            # ===== SETUP MONITORS =====
            self.progress_updated.emit(55, "Setting up monitors...")
            self.monitors = self.monitor_builder.setup_monitors(
                self.neurons, self.synapses, monitors_params=monitors_params
            )

            if not self.monitors:
                raise RuntimeError("Failed to setup monitoring.")

            # ===== CREATE NETWORK =====
            self.progress_updated.emit(60, "Creating network...")
            net_objects = [self.neurons]

            if self.synapses:
                net_objects.append(self.synapses)
            if self.gap_junctions:
                net_objects.append(self.gap_junctions)

            net_objects.extend(list(self.monitors.values()))

            # Add input sources
            if input_sources:
                if isinstance(input_sources, dict):
                    for key, obj in input_sources.items():
                        # Add any Brian2 simulation object (NeuronGroup, Synapses, etc.)
                        # We exclude TimedArray explicitly as it shouldn't be added to Network
                        if isinstance(obj, b2.TimedArray):
                            continue
                            
                        if hasattr(obj, "custom_operation") or isinstance(
                            obj, (b2.NeuronGroup, b2.Synapses, b2.PoissonGroup, b2.SpikeGeneratorGroup)
                        ):
                             net_objects.append(obj)
                        # Detect checkers/runners from run_regularly (which have 'code' attribute usually)
                        elif hasattr(obj, "code") or hasattr(obj, "clock"):
                             net_objects.append(obj)

            self.network = b2.Network(net_objects)

            # ===== RUN SIMULATION =====
            self.progress_updated.emit(65, "Running simulation...")
            sim_time = sim_params.get("sim_time", 100) * b2.ms
            self._run_with_progress_tracking(sim_time)

            if self.should_stop:
                return {}

            # ===== COLLECT RESULTS =====
            self.progress_updated.emit(95, "Collecting results...")
            results = self.monitor_builder.collect_results(self.monitors, params)

            if not results:
                raise RuntimeError("Failed to collect simulation results.")

            self.progress_updated.emit(100, "Simulation completed successfully!")
            return results

        except ValueError as e:
            # Re-raise validation errors for proper error handling
            raise
        except Exception as e:
            error_msg = f"Brian2 simulation failed: {str(e)}"
            self.progress_updated.emit(0, f"Error: {error_msg}")
            self.simulation_error.emit(error_msg)
            print(f"DEBUG: Simulation error - {error_msg}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "brian2_available": True, "success": False}



    def _run_with_progress_tracking(self, sim_time):
        """Run simulation with progress updates."""
        # Split into chunks for progress updates
        chunk_duration = min(sim_time / 10, 50 * b2.ms)
        num_chunks = max(1, int(sim_time / chunk_duration))
        actual_chunk = sim_time / num_chunks

        for i in range(num_chunks):
            if self.should_stop:
                return

            progress = 65 + int((i / num_chunks) * 30)
            elapsed = time.time() - self.simulation_start_time
            self.progress_updated.emit(progress, f"Running... ({elapsed:.1f}s elapsed)")

            self.network.run(actual_chunk)

    def _update_progress(self):
        """Update progress during simulation."""
        if not self.is_running:
            return

        elapsed = time.time() - self.simulation_start_time
        expected_time = self.total_simulation_time / 100
        progress = min(90, int(65 + (elapsed / max(expected_time, 1)) * 25))

        self.progress_updated.emit(progress, f"Running simulation... ({elapsed:.1f}s elapsed)")

    def _run_dummy_simulation(self, params):
        """Run a dummy simulation when Brian2 is not available."""
        self.is_running = True

        try:
            self.progress_updated.emit(10, "Running dummy simulation...")

            sim_params = params.get("simulation", {})
            num_neurons = sim_params.get("num_neurons", 10)
            sim_time = sim_params.get("sim_time", 100)

            # Generate fake spike data
            spike_times = []
            spike_indices = []

            for i in range(num_neurons):
                n_spikes = np.random.randint(5, 20)
                times = np.sort(np.random.uniform(0, sim_time, n_spikes))
                spike_times.extend(times)
                spike_indices.extend([i] * n_spikes)

            # Generate fake voltage traces
            voltage_times = np.linspace(0, sim_time, 1000)
            voltage_traces = {}
            for i in range(min(10, num_neurons)):
                base = -70 + np.random.randn(len(voltage_times)) * 5
                voltage_traces[i] = base

            results = {
                "spike_times": np.array(spike_times),
                "spike_indices": np.array(spike_indices),
                "voltage_times": voltage_times,
                "voltage_traces": voltage_traces,
                "statistics": {
                    "total_spikes": len(spike_times),
                    "mean_firing_rate": len(spike_times) / (sim_time / 1000 * num_neurons),
                    "simulation_time": sim_time,
                    "num_neurons": num_neurons,
                },
                "timestamp": datetime.now().isoformat(),
                "brian2_available": False,
                "parameters": params,
            }

            self.progress_updated.emit(100, "Dummy simulation completed")
            self.simulation_completed.emit(True, results)
            return results

        except Exception as e:
            self.simulation_error.emit(f"Dummy simulation failed: {str(e)}")
            return None
        finally:
            self.is_running = False
