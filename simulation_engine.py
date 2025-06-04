"""
Simulation Engine for Brian2 neural network simulator.
Handles the actual execution of Brian2 simulations with progress reporting.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
import time
from datetime import datetime

# Handle Brian2 import
try:
    import brian2 as b2    # Import specific Brian2 components instead of wildcard import
    from brian2 import (
        ms, mV, nA, pA, Hz, second, 
        NeuronGroup, Synapses, SpikeMonitor, StateMonitor,
        run, start_scope, defaultclock, TimedArray, PoissonGroup, rand, randint
    )
    import numpy as np
    BRIAN2_AVAILABLE = True
except ImportError:
    BRIAN2_AVAILABLE = False

class SimulationEngine(QObject):
    """Engine for executing Brian2 neural network simulations."""
    
    # Signals for progress and completion
    progress_updated = pyqtSignal(int, str)     # progress percentage, status message
    simulation_completed = pyqtSignal(bool, dict)  # success flag, results data
    simulation_error = pyqtSignal(str)          # error message
    
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
            # Extract simulation time for progress tracking
            sim_params = params.get('simulation', {})
            self.total_simulation_time = sim_params.get('sim_time', 100)  # ms
            
            # Start progress tracking
            self.progress_timer.start(250)  # Update every 250ms
            
            # Build and run Brian2 simulation
            results = self._execute_brian2_simulation(params)
              # Stop progress tracking
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
        """Execute the actual Brian2 simulation."""
        try:
            self.progress_updated.emit(5, "Initializing Brian2...")
            
            # Check if Brian2 is available
            if not BRIAN2_AVAILABLE:
                raise ImportError("Brian2 is not available. Please install Brian2: pip install brian2")
            
            # Clear any previous Brian2 objects
            b2.start_scope()
              # Extract parameters
            sim_params = params.get('simulation', {})
            neuron_params = params.get('neuron_model', {})
            noise_params = params.get('noise', {})
            network_params = params.get('network', {})
            advanced_params = params.get('advanced_network', {})
            
            # Validate critical parameters
            if not sim_params.get('sim_time') or sim_params.get('sim_time') <= 0:
                raise ValueError("Invalid simulation time. Must be a positive number.")
            
            if not sim_params.get('num_neurons') or sim_params.get('num_neurons') <= 0:
                raise ValueError("Invalid number of neurons. Must be a positive integer.")
            
            self.progress_updated.emit(10, "Building neuron model...")
            
            # Build neurons
            neurons = self._build_neurons(sim_params, neuron_params)
            if neurons is None:
                raise RuntimeError("Failed to build neuron model.")
            
            if self.should_stop:
                return {}
                
            self.progress_updated.emit(25, "Configuring input currents...")
            
            # Add input current
            input_current = self._setup_input_current(sim_params, neurons)
            
            self.progress_updated.emit(35, "Adding noise...")
            
            # Add noise if enabled
            noise_source = self._setup_noise(noise_params, neurons)
            
            self.progress_updated.emit(45, "Building network connections...")
            
            # Build network connections
            synapses = self._build_network(network_params, advanced_params, neurons)
            
            if self.should_stop:
                return {}
                
            self.progress_updated.emit(55, "Setting up monitors...")
            
            # Setup monitors
            monitors = self._setup_monitors(neurons, synapses)
            if not monitors:
                raise RuntimeError("Failed to setup monitoring.")
            
            self.progress_updated.emit(65, "Running simulation...")
            
            # Run the simulation
            sim_time = sim_params.get('sim_time', 100) * b2.ms
              # Custom progress tracking during simulation
            self._run_with_progress_tracking(sim_time)
            
            if self.should_stop:
                return {}
                
            self.progress_updated.emit(95, "Collecting results...")
            
            # Collect results
            results = self._collect_results(monitors, params)
            if not results:
                raise RuntimeError("Failed to collect simulation results.")
            
            self.progress_updated.emit(100, "Simulation completed successfully!")
            return results
        
        except Exception as e:
            error_msg = f"Brian2 simulation failed: {str(e)}"
            self.progress_updated.emit(0, f"Error: {error_msg}")
            self.simulation_error.emit(error_msg)
            print(f"DEBUG: Simulation error - {error_msg}")
            return None

    def _build_neurons(self, sim_params, neuron_params):
        """Build the neuron group based on model parameters."""
        try:
            num_neurons = sim_params.get('num_neurons', 1)
            model_type = neuron_params.get('model_key', 'lif')
            
            if model_type == 'lif':
                # Leaky Integrate-and-Fire
                threshold = sim_params.get('lif_threshold', -50)  # Numeric value
                reset = sim_params.get('lif_reset', -70)          # Numeric value
                tau = neuron_params.get('tau_m', 10) * b2.ms
                v_rest = neuron_params.get('v_rest', -70) * b2.mV
                resistance = neuron_params.get('resistance', 100) * b2.Mohm
                
                eqs = '''
                dv/dt = (-(v - V_rest) + R * I) / tau : volt
                I : amp
                '''
                
                neurons = b2.NeuronGroup(num_neurons, eqs, 
                                    threshold=f'v > {threshold}*mV',    # Numeric + units
                                    reset=f'v = {reset}*mV',           # Numeric + units
                                    namespace={'tau': tau, 'R': resistance, 'V_rest': v_rest})
                neurons.v = reset * b2.mV  # Initialize with units
                
            elif model_type == 'izhikevich':
                parameters = neuron_params.get('parameters', {})
                a = parameters.get('a', 0.02)
                b = parameters.get('b', 0.2) 
                c = parameters.get('c', -65)
                d = parameters.get('d', 8)
                
                eqs = '''
                dv/dt = (0.04*v**2 + 5*v + 140 - u + I)/ms : 1
                du/dt = (a*(b*v - u))/ms : 1
                I : 1
                '''
                
                neurons = b2.NeuronGroup(num_neurons, eqs,
                                       threshold='v >= 30',
                                       reset=f'v = {c}; u += {d}',
                                       namespace={'a': a, 'b': b})
                neurons.v = c
                neurons.u = b * c
                
            else:
                # Hodgkin-Huxley or custom model
                # For now, default to simple LIF
                neurons = b2.NeuronGroup(num_neurons, 
                                       'dv/dt = (-v + R*I)/tau : volt',
                                       threshold='v > -50*mV',
                                       reset='v = -70*mV',
                                       namespace={'tau': 10*b2.ms, 'R': 100*b2.Mohm})
                neurons.v = -70 * b2.mV
            
            return neurons
        except Exception as e:
            print(f"DEBUG: Error building neurons: {str(e)}")
            raise RuntimeError(f"Failed to build neuron model: {str(e)}")
    
    def _setup_input_current(self, sim_params, neurons):
        """Setup input current stimulus."""
        # Fix: Input current should be in pA, not nA
        current_amplitude = sim_params.get('input_current', 0.5) * b2.pA
        current_start = sim_params.get('current_start', 10) * b2.ms
        current_duration = sim_params.get('current_duration', 50) * b2.ms
        
        # Fix: Proper TimedArray setup for current injection timing
        total_sim_time = sim_params.get('sim_time', 100) * b2.ms
        dt_step = 1 * b2.ms  # 1ms resolution for timing
        
        # Create time points for current injection
        time_points = []
        current_values = []
        
        current_time = 0 * b2.ms
        while current_time <= total_sim_time:
            if current_start <= current_time < (current_start + current_duration):
                current_values.append(current_amplitude)
            else:
                current_values.append(0 * b2.pA)
            time_points.append(current_time)
            current_time += dt_step
        
        # Create timed input current with proper timing
        input_current = b2.TimedArray(current_values, dt=dt_step)
        
        # Apply current to neurons
        neurons.run_regularly('I = input_current(t)', dt=0.1*b2.ms)
        
        return input_current
    
    def _setup_noise(self, noise_params, neurons):
        """Setup noise input if enabled."""
        if not noise_params.get('enabled', False):
            return None
            
        intensity = noise_params.get('intensity', 0.1) * b2.nA
        method = noise_params.get('method', 'Gaussian')
        
        if method == 'Gaussian':
            # White noise
            neurons.run_regularly(f'I += {intensity} * randn()', dt=0.1*b2.ms)
        elif method == 'Ornstein-Uhlenbeck':
            # Colored noise (simplified)
            tau_noise = 5 * b2.ms
            neurons.equations += b2.Equations(f'''
                dI_noise/dt = -I_noise/tau_noise + sigma*sqrt(2/tau_noise)*xi : amp
                ''', tau_noise=tau_noise, sigma=intensity)
            neurons.run_regularly('I += I_noise', dt=0.1*b2.ms)
            
        return True
    
    def _build_network(self, network_params, advanced_params, neurons):
        """Build synaptic connections between neurons."""
        if not network_params.get('synapse_enabled', False):
            return None
            
        if len(neurons) < 2:
            return None
            
        synaptic_weight = network_params.get('syn_weight', 0.1) * b2.nA
        topology = network_params.get('topology_type', 'all_to_all')
        
        # Create synapses
        synapses = b2.Synapses(neurons, neurons, 'w : amp', on_pre='I += w')
        
        # Connect based on topology
        topology_params = network_params.get('topology_params', {})
        
        if topology == 'all_to_all':
            allow_self = topology_params.get('allow_self_connections', False)
            if allow_self:
                synapses.connect()
            else:
                synapses.connect(condition='i != j')
        elif topology == 'one_to_one':
            if len(neurons) >= 2:
                synapses.connect(j='i+1', skip_if_invalid=True)
        elif topology == 'random':
            prob = topology_params.get('syn_prob', 0.1)  # Fixed parameter name
            synapses.connect(p=prob)
        elif topology == 'small_world':
            # Small world network (simplified implementation)
            k = topology_params.get('topology_k', 4)
            p_rewire = topology_params.get('topology_p_rewire', 0.1)
            # Create ring lattice first
            for i in range(len(neurons)):
                for j in range(1, k//2 + 1):
                    target = (i + j) % len(neurons)
                    if np.random.rand() < p_rewire:
                        # Rewire to random neuron
                        target = np.random.randint(len(neurons))
                    if target != i:  # Avoid self-connections
                        synapses.connect(i=i, j=target)
        elif topology == 'scale_free':
            # Scale-free network (simplified Barabási–Albert)
            m = topology_params.get('topology_m', 2)
            # Start with complete graph of m nodes
            for i in range(min(m, len(neurons))):
                for j in range(i+1, min(m, len(neurons))):
                    synapses.connect(i=i, j=j)
                    synapses.connect(i=j, j=i)  # Make bidirectional
            # Add remaining nodes with preferential attachment
            for i in range(m, len(neurons)):
                existing_connections = len(synapses.i)
                for _ in range(m):
                    if existing_connections > 0:
                        # Simple preferential attachment
                        target = np.random.randint(i)
                        synapses.connect(i=i, j=target)
        elif topology == 'regular':
            # Regular lattice
            k = topology_params.get('topology_k_reg', 4)
            for i in range(len(neurons)):
                for j in range(1, k//2 + 1):
                    target1 = (i + j) % len(neurons)
                    target2 = (i - j) % len(neurons)
                    if target1 != i:
                        synapses.connect(i=i, j=target1)
                    if target2 != i:
                        synapses.connect(i=i, j=target2)
        elif topology == 'modular':
            # Modular network
            n_modules = topology_params.get('topology_n_modules', 3)
            p_intra = topology_params.get('topology_p_intra', 0.15)
            p_inter = topology_params.get('topology_p_inter', 0.01)
            
            neurons_per_module = len(neurons) // n_modules
            for i in range(len(neurons)):
                module_i = i // neurons_per_module
                for j in range(len(neurons)):
                    if i != j:
                        module_j = j // neurons_per_module
                        if module_i == module_j:
                            # Intra-module connection
                            if np.random.rand() < p_intra:
                                synapses.connect(i=i, j=j)
                        else:
                            # Inter-module connection
                            if np.random.rand() < p_inter:
                                synapses.connect(i=i, j=j)
        
        # Set weights
        synapses.w = synaptic_weight
        
        # Apply advanced network features
        self._apply_advanced_network_features(synapses, advanced_params, neurons)
        
        return synapses
    
    def _apply_advanced_network_features(self, synapses, advanced_params, neurons):
        """Apply advanced network features like Dale's principle, delays, STDP."""
        if not synapses or not advanced_params:
            return
            
        # Dale's principle
        if advanced_params.get('dales_principle', {}).get('enabled', False):
            # Simplified: make some neurons inhibitory
            dales_config = advanced_params['dales_principle']
            ratio = dales_config.get('inhibitory_ratio', 0.2)
            n_inhib = int(len(neurons) * ratio)
            if n_inhib > 0:
                # Make connections from last n_inhib neurons inhibitory
                synapses.w[synapses.i >= (len(neurons) - n_inhib)] *= -1
        
        # Synaptic delays
        if advanced_params.get('synaptic_delays', {}).get('enabled', False):
            delay_config = advanced_params['synaptic_delays']
            if delay_config.get('delay_type') == 'fixed':
                delay = delay_config.get('fixed_delay', 1) * b2.ms
                synapses.delay = delay
            elif delay_config.get('delay_type') == 'uniform':
                min_delay = delay_config.get('min_delay', 0.5) * b2.ms
                max_delay = delay_config.get('max_delay', 2) * b2.ms
                synapses.delay = f'({min_delay} + ({max_delay} - {min_delay}) * rand())'
    def _setup_monitors(self, neurons, synapses):
        """Setup monitoring of simulation variables."""
        try:
            monitors = {}
            
            # Spike monitor
            monitors['spikes'] = b2.SpikeMonitor(neurons)
            
            # Voltage monitor (sample a few neurons to avoid memory issues)
            n_monitor = min(10, len(neurons))
            monitors['voltage'] = b2.StateMonitor(neurons, 'v', record=list(range(n_monitor)))
            
            # Current monitor
            monitors['current'] = b2.StateMonitor(neurons, 'I', record=list(range(n_monitor)))
            
            return monitors
        except Exception as e:
            print(f"DEBUG: Error setting up monitors: {str(e)}")
            raise RuntimeError(f"Failed to setup monitoring: {str(e)}")
    def _run_with_progress_tracking(self, sim_time):
        """Run simulation with progress updates."""
        try:
            dt = 10 * b2.ms  # Progress update interval
            steps = int(sim_time / dt)
            
            for step in range(steps):
                if self.should_stop:
                    break
                    
                # Run a small chunk
                b2.run(dt)
                
                # Update progress
                progress = 65 + int(25 * (step + 1) / steps)  # 65% to 90%
                elapsed_time = (step + 1) * float(dt / b2.ms)
                self.progress_updated.emit(progress, f"Simulating: {elapsed_time:.1f}/{float(sim_time/b2.ms):.1f} ms")
            
            # Run any remaining time
            remaining = sim_time - steps * dt
            if remaining > 0 * b2.ms and not self.should_stop:
                b2.run(remaining)
        except Exception as e:
            print(f"DEBUG: Error during simulation run: {str(e)}")
            raise RuntimeError(f"Simulation run failed: {str(e)}")
    
    def _collect_results(self, monitors, params):
        """Collect simulation results from monitors."""
        results = {
            'parameters': params,
            'timestamp': datetime.now().isoformat(),
            'brian2_available': True
        }
        
        if 'spikes' in monitors:
            spike_monitor = monitors['spikes']
            results['spike_times'] = list(spike_monitor.t / b2.ms)  # Convert to ms
            results['spike_indices'] = list(spike_monitor.i)
            results['spike_count'] = len(spike_monitor.t)
            
        if 'voltage' in monitors:
            voltage_monitor = monitors['voltage']
            results['voltage_times'] = list(voltage_monitor.t / b2.ms)
            results['voltage_traces'] = {}
            for i in range(len(voltage_monitor.v)):
                results['voltage_traces'][i] = list(voltage_monitor.v[i] / b2.mV)
                
        if 'current' in monitors:
            current_monitor = monitors['current']
            results['current_times'] = list(current_monitor.t / b2.ms)
            results['current_traces'] = {}
            for i in range(len(current_monitor.I)):
                results['current_traces'][i] = list(current_monitor.I[i] / b2.nA)
        
        return results
    
    def _run_dummy_simulation(self, params):
        """Run a dummy simulation when Brian2 is not available."""
        self.is_running = True
        self.progress_updated.emit(0, "Brian2 not available - running dummy simulation")
        
        # Simulate some processing time with progress updates
        total_steps = 50
        for step in range(total_steps):
            if self.should_stop:
                self.simulation_completed.emit(False, {})
                return
                
            time.sleep(0.01)  # 10ms delay per step (faster for testing)
            progress = int(100 * (step + 1) / total_steps)
            self.progress_updated.emit(progress, f"Dummy step {step + 1}/{total_steps}")
        
        # Create dummy results
        dummy_results = {
            'parameters': params,
            'timestamp': datetime.now().isoformat(),
            'brian2_available': False,
            'spike_times': [10, 25, 40, 55, 70, 85],  # Dummy spike times
            'spike_indices': [0, 0, 1, 1, 2, 2],     # Dummy neuron indices
            'spike_count': 6,
            'voltage_times': list(range(0, 101, 1)),  # 0 to 100 ms
            'voltage_traces': {
                0: [-70 + 30 * (i % 20 < 10) for i in range(101)],  # Dummy voltage trace
                1: [-70 + 25 * ((i + 10) % 25 < 12) for i in range(101)]
            }
        }
        self.simulation_completed.emit(True, dummy_results)
        self.is_running = False
        return dummy_results
    
    def _update_progress(self):
        """Update progress during simulation."""
        if not self.is_running or not self.simulation_start_time:
            return
            
        elapsed = time.time() - self.simulation_start_time
        # This is called by the timer for general progress updates
        # Actual progress is updated by the simulation steps
