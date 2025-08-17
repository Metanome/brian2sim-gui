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
    import numpy as np  # Still need numpy for calculations

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
            input_patterns_params = params.get('input_patterns', {})
            synaptic_receptors_params = params.get('synaptic_receptors', {})
            short_term_plasticity_params = params.get('short_term_plasticity', {})
            calcium_dynamics_params = params.get('calcium_dynamics', {})
            gap_junctions_params = params.get('gap_junctions', {})
            homeostatic_plasticity_params = params.get('homeostatic_plasticity', {})
            neuromodulation_params = params.get('neuromodulation', {})
            multicompartment_params = params.get('multicompartment', {})
            
            # Validate critical parameters
            if not sim_params.get('sim_time') or sim_params.get('sim_time') <= 0:
                raise ValueError("Invalid simulation time. Must be a positive number.")
            
            if not sim_params.get('num_neurons') or sim_params.get('num_neurons') <= 0:
                raise ValueError("Invalid number of neurons. Must be a positive integer.")
            
            self.progress_updated.emit(10, "Building neuron model...")
            
            # Build neurons
            neurons = self._build_neurons(sim_params, neuron_params, calcium_dynamics_params, multicompartment_params)
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
            
            self.progress_updated.emit(40, "Setting up input patterns...")
            
            # Add input patterns (Poisson, rhythmic, etc.)
            input_sources = self._setup_input_patterns(input_patterns_params, neurons)
            
            self.progress_updated.emit(45, "Building network connections...")
            
            # Build network connections
            synapses = self._build_network(network_params, advanced_params, synaptic_receptors_params, short_term_plasticity_params, neurons)
            
            self.progress_updated.emit(50, "Building gap junctions...")
            
            # Build gap junctions (electrical synapses)
            gap_junctions = self._build_gap_junctions(gap_junctions_params, neurons)
            
            self.progress_updated.emit(52, "Setting up homeostatic plasticity...")
            
            # Setup homeostatic plasticity mechanisms
            homeostatic_mechanisms = self._setup_homeostatic_plasticity(
                homeostatic_plasticity_params, neurons, synapses
            )
            
            self.progress_updated.emit(54, "Setting up neuromodulation...")
            
            # Setup neuromodulation systems
            neuromodulation_systems = self._setup_neuromodulation(
                neuromodulation_params, neurons, synapses
            )
            
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

    def _build_neurons(self, sim_params, neuron_params, calcium_dynamics_params=None, multicompartment_params=None):
        """Build the neuron group based on model parameters with optional calcium dynamics and multi-compartment structure."""
        try:
            num_neurons = sim_params.get('num_neurons', 1)
            model_type = neuron_params.get('model_key', 'lif')
            
            # Check if multi-compartment modeling is enabled
            multicomp_enabled = multicompartment_params and multicompartment_params.get('enabled', False)
            
            # Check if calcium dynamics should be added
            ca_enabled = calcium_dynamics_params and calcium_dynamics_params.get('enabled', False)
            
            # If multi-compartment is enabled, build compartmental model
            if multicomp_enabled:
                return self._build_multicompartment_neurons(num_neurons, multicompartment_params, neuron_params, calcium_dynamics_params)
            
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
                
                # Add calcium dynamics if enabled
                if ca_enabled:
                    ca_eqs = self._get_calcium_equations(calcium_dynamics_params)
                    eqs += '\n' + ca_eqs
                
                neurons = b2.NeuronGroup(num_neurons, eqs, 
                                    threshold=f'v > {threshold}*mV',    # Numeric + units
                                    reset=f'v = {reset}*mV',           # Numeric + units
                                    namespace={'tau': tau, 'R': resistance, 'V_rest': v_rest})
                neurons.v = reset * b2.mV  # Initialize with units
                
                # Initialize calcium if enabled
                if ca_enabled:
                    self._initialize_calcium(neurons, calcium_dynamics_params)
                
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
                
            elif model_type == 'adex':
                # Adaptive Exponential Integrate-and-Fire (AdEx) - Brette & Gerstner 2005
                parameters = neuron_params.get('parameters', {})
                C = parameters.get('C', 200) * b2.pF          # Membrane capacitance
                gL = parameters.get('gL', 10) * b2.nS         # Leak conductance  
                EL = parameters.get('EL', -70) * b2.mV        # Leak reversal potential
                VT = parameters.get('VT', -50) * b2.mV        # Spike threshold
                delT = parameters.get('delT', 2) * b2.mV      # Slope factor
                a = parameters.get('a', 2) * b2.nS            # Subthreshold adaptation
                tauw = parameters.get('tauw', 30) * b2.ms     # Adaptation time constant
                b = parameters.get('b', 60) * b2.pA           # Spike-triggered adaptation
                
                eqs = '''
                dv/dt = (gL*(EL - v) + gL*delT*exp((v - VT)/delT) - w + I)/C : volt
                dw/dt = (a*(v - EL) - w)/tauw : amp
                I : amp
                '''
                
                neurons = b2.NeuronGroup(num_neurons, eqs,
                                       threshold='v > VT + 5*delT',  # Spike detection
                                       reset='v = EL; w += b',       # Reset and adaptation
                                       namespace={'C': C, 'gL': gL, 'EL': EL, 'VT': VT, 
                                               'delT': delT, 'a': a, 'tauw': tauw, 'b': b})
                neurons.v = EL
                neurons.w = 0 * b2.pA
                
            elif model_type == 'hodgkin_huxley':
                # Hodgkin-Huxley model with voltage-gated sodium and potassium channels
                parameters = neuron_params.get('parameters', {})
                C = parameters.get('C', 1.0) * b2.uF / b2.cm**2      # Membrane capacitance
                gNa_max = parameters.get('gNa_max', 120.0) * b2.mS / b2.cm**2  # Max Na conductance
                gK_max = parameters.get('gK_max', 36.0) * b2.mS / b2.cm**2     # Max K conductance
                gL = parameters.get('gL', 0.3) * b2.mS / b2.cm**2              # Leak conductance
                ENa = parameters.get('ENa', 50.0) * b2.mV             # Na reversal potential
                EK = parameters.get('EK', -77.0) * b2.mV              # K reversal potential
                EL = parameters.get('EL', -54.4) * b2.mV              # Leak reversal potential
                temp = parameters.get('temperature', 6.3)             # Temperature
                
                # Temperature factor (Q10 = 3 for HH kinetics)
                temp_factor = 3**((temp - 6.3)/10)
                
                eqs = '''
                dv/dt = (gL*(EL - v) + gNa*m**3*h*(ENa - v) + gK*n**4*(EK - v) + I)/C : volt
                dm/dt = (alpha_m*(1 - m) - beta_m*m) * temp_factor : 1
                dh/dt = (alpha_h*(1 - h) - beta_h*h) * temp_factor : 1
                dn/dt = (alpha_n*(1 - n) - beta_n*n) * temp_factor : 1
                
                alpha_m = (2.5 - 0.1*(v/mV + 65)) / (exp(2.5 - 0.1*(v/mV + 65)) - 1) / ms : Hz
                beta_m = 4*exp(-(v/mV + 65)/18) / ms : Hz
                alpha_h = 0.07*exp(-(v/mV + 65)/20) / ms : Hz
                beta_h = 1/(exp(3 - 0.1*(v/mV + 65)) + 1) / ms : Hz
                alpha_n = (0.1 - 0.01*(v/mV + 65)) / (exp(1 - 0.1*(v/mV + 65)) - 1) / ms : Hz
                beta_n = 0.125*exp(-(v/mV + 65)/80) / ms : Hz
                
                gNa = gNa_max : siemens/meter**2
                gK = gK_max : siemens/meter**2
                I : amp/meter**2
                '''
                
                neurons = b2.NeuronGroup(num_neurons, eqs,
                                       threshold='v > -40*mV',  # Spike detection
                                       refractory=2*b2.ms,     # Brief refractory period
                                       namespace={'C': C, 'gNa_max': gNa_max, 'gK_max': gK_max,
                                               'gL': gL, 'ENa': ENa, 'EK': EK, 'EL': EL,
                                               'temp_factor': temp_factor})
                
                # Initialize at resting state
                neurons.v = EL
                # Initialize gating variables at steady state for resting potential
                v_rest = float(EL/b2.mV)
                alpha_m_rest = (2.5 - 0.1*(v_rest + 65)) / (np.exp(2.5 - 0.1*(v_rest + 65)) - 1)
                beta_m_rest = 4*np.exp(-(v_rest + 65)/18)
                alpha_h_rest = 0.07*np.exp(-(v_rest + 65)/20)
                beta_h_rest = 1/(np.exp(3 - 0.1*(v_rest + 65)) + 1)
                alpha_n_rest = (0.1 - 0.01*(v_rest + 65)) / (np.exp(1 - 0.1*(v_rest + 65)) - 1)
                beta_n_rest = 0.125*np.exp(-(v_rest + 65)/80)
                
                neurons.m = alpha_m_rest / (alpha_m_rest + beta_m_rest)
                neurons.h = alpha_h_rest / (alpha_h_rest + beta_h_rest)
                neurons.n = alpha_n_rest / (alpha_n_rest + beta_n_rest)
                
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
    
    def _build_multicompartment_neurons(self, num_neurons, multicomp_params, neuron_params, calcium_params=None):
        """Build multi-compartment neuron models using Brian2's spatial extension."""
        try:
            # Try to import spatial neuron support
            try:
                from brian2.spatialsubunits import SpatialNeuron, Section
                spatial_available = True
            except ImportError:
                spatial_available = False
            
            if not spatial_available:
                # Fall back to enhanced point neuron
                print("WARNING: Brian2 spatial extension not available, using enhanced point neuron")
                return self._build_point_neuron_fallback(num_neurons, multicomp_params, neuron_params)
            
            # Get morphological parameters
            soma_diameter = multicomp_params.get('soma_diameter', 20.0) * b2.umeter
            soma_length = multicomp_params.get('soma_length', 20.0) * b2.umeter
            dendrite_segments = multicomp_params.get('dendrite_segments', 10)
            dendrite_length_total = multicomp_params.get('dendrite_length_total', 200.0) * b2.umeter
            dendrite_diam_prox = multicomp_params.get('dendrite_diameter_proximal', 3.0) * b2.umeter
            dendrite_diam_dist = multicomp_params.get('dendrite_diameter_distal', 0.5) * b2.umeter
            
            # Electrical parameters
            soma_cm = multicomp_params.get('soma_cm', 1.0) * b2.uF / b2.cm**2
            soma_rm = multicomp_params.get('soma_rm', 10000.0) * b2.ohm * b2.cm**2
            soma_ra = multicomp_params.get('soma_ra', 150.0) * b2.ohm * b2.cm
            
            dendrite_cm = multicomp_params.get('dendrite_cm', 1.0) * b2.uF / b2.cm**2
            dendrite_rm = multicomp_params.get('dendrite_rm', 20000.0) * b2.ohm * b2.cm**2
            dendrite_ra = multicomp_params.get('dendrite_ra', 200.0) * b2.ohm * b2.cm
            
            # Create morphology
            morphology = self._create_morphology_with_spatial(multicomp_params, Section)
            
            # Base equations for cable equation
            base_eqs = '''
            Im = gL * (EL - v) : amp/meter**2
            gL : siemens/meter**2
            EL : volt
            '''
            
            # Add ion channels if enabled
            if multicomp_params.get('channel_distribution', True):
                ion_channel_eqs = self._get_ion_channel_equations(multicomp_params)
                base_eqs += '\n' + ion_channel_eqs
            
            # Add calcium dynamics if enabled
            if calcium_params and calcium_params.get('enabled', False):
                ca_eqs = self._get_calcium_equations(calcium_params)
                base_eqs += '\n' + ca_eqs
            
            # Create spatial neuron group
            neurons = SpatialNeuron(morphology=morphology,
                                   model=base_eqs,
                                   Cm=soma_cm,
                                   Ri=soma_ra,
                                   threshold='v > -40*mV',
                                   refractory=2*b2.ms,
                                   method='exponential_euler')
            
            # Set membrane properties for different compartments
            self._set_compartment_properties(neurons, multicomp_params)
            
            # Initialize voltages
            neurons.v = multicomp_params.get('v_init', -70.0) * b2.mV
            
            # Initialize calcium if enabled
            if calcium_params and calcium_params.get('enabled', False):
                self._initialize_calcium(neurons, calcium_params)
            
            return neurons
            
        except Exception as e:
            print(f"DEBUG: Error building multi-compartment neurons: {str(e)}")
            # Fall back to enhanced point neuron
            return self._build_point_neuron_fallback(num_neurons, multicomp_params, neuron_params)
    
    def _create_morphology_with_spatial(self, params, Section):
        """Create morphology for multi-compartment neuron using Section class."""
        # Soma
        soma_diam = params.get('soma_diameter', 20.0)
        soma_len = params.get('soma_length', 20.0)
        
        # Create soma section
        soma = Section(diameter=soma_diam*b2.umeter, length=soma_len*b2.umeter, 
                      n=1, type='soma')
        
        # Dendrites
        dendrite_segments = params.get('dendrite_segments', 10)
        dendrite_length_total = params.get('dendrite_length_total', 200.0)
        dendrite_diam_prox = params.get('dendrite_diameter_proximal', 3.0)
        dendrite_diam_dist = params.get('dendrite_diameter_distal', 0.5)
        
        # Calculate segment length
        segment_length = dendrite_length_total / dendrite_segments
        
        dendrites = []
        for i in range(dendrite_segments):
            # Calculate diameter with tapering
            if params.get('dendrite_taper', True):
                taper_factor = 1.0 - (i / dendrite_segments)
                diameter = dendrite_diam_dist + (dendrite_diam_prox - dendrite_diam_dist) * taper_factor
            else:
                diameter = dendrite_diam_prox
            
            dendrite = Section(diameter=diameter*b2.umeter, 
                             length=segment_length*b2.umeter,
                             n=1, type='dendrite')
            dendrites.append(dendrite)
        
        # Connect dendrites to soma
        morphology = soma
        for dendrite in dendrites:
            morphology = morphology.dendrite
        
        # Add axon if enabled
        if params.get('include_axon', True):
            axon_segments = params.get('axon_segments', 3)
            axon_length = params.get('axon_length', 100.0)
            axon_diameter = params.get('axon_diameter', 1.0)
            
            segment_length = axon_length / axon_segments
            
            for i in range(axon_segments):
                axon = Section(diameter=axon_diameter*b2.umeter,
                             length=segment_length*b2.umeter,
                             n=1, type='axon')
                morphology = morphology.axon
        
        return morphology
    
    def _get_ion_channel_equations(self, params):
        """Get ion channel equations for multi-compartment model."""
        eqs = '''
        INa = gNa * m**3 * h * (ENa - v) : amp/meter**2
        IK = gK * n**4 * (EK - v) : amp/meter**2
        
        dm/dt = (alpha_m * (1 - m) - beta_m * m) : 1
        dh/dt = (alpha_h * (1 - h) - beta_h * h) : 1
        dn/dt = (alpha_n * (1 - n) - beta_n * n) : 1
        
        alpha_m = (2.5 - 0.1*(v/mV + 65)) / (exp(2.5 - 0.1*(v/mV + 65)) - 1) / ms : Hz
        beta_m = 4*exp(-(v/mV + 65)/18) / ms : Hz
        alpha_h = 0.07*exp(-(v/mV + 65)/20) / ms : Hz
        beta_h = 1/(exp(3 - 0.1*(v/mV + 65)) + 1) / ms : Hz
        alpha_n = (0.1 - 0.01*(v/mV + 65)) / (exp(1 - 0.1*(v/mV + 65)) - 1) / ms : Hz
        beta_n = 0.125*exp(-(v/mV + 65)/80) / ms : Hz
        
        gNa : siemens/meter**2
        gK : siemens/meter**2
        ENa : volt
        EK : volt
        '''
        
        # Add calcium channels if specified
        if params.get('dendrite_ca_density', 0.0) > 0:
            eqs += '''
            ICa = gCa * mCa**2 * hCa * (ECa - v) : amp/meter**2
            dmCa/dt = (alpha_mCa * (1 - mCa) - beta_mCa * mCa) : 1
            dhCa/dt = (alpha_hCa * (1 - hCa) - beta_hCa * hCa) : 1
            
            alpha_mCa = 0.1 * (v/mV + 40) / (1 - exp(-(v/mV + 40)/10)) / ms : Hz
            beta_mCa = 4 * exp(-(v/mV + 65)/18) / ms : Hz
            alpha_hCa = 0.01 * exp(-(v/mV + 50)/10) / ms : Hz
            beta_hCa = 0.01 * exp(-(v/mV + 20)/10) / ms : Hz
            
            gCa : siemens/meter**2
            ECa : volt
            '''
        
        # Add h-channels if specified
        if params.get('dendrite_h_density', 0.0) > 0:
            eqs += '''
            Ih = gh * mh * (Eh - v) : amp/meter**2
            dmh/dt = (alpha_mh * (1 - mh) - beta_mh * mh) : 1
            
            alpha_mh = 0.001 * 6.43 * (v/mV + 154.9) / (exp((v/mV + 154.9)/11.9) - 1) / ms : Hz
            beta_mh = 0.001 * 193 * exp(v/mV / 33.1) / ms : Hz
            
            gh : siemens/meter**2
            Eh : volt
            '''
        
        return eqs
    
    def _set_compartment_properties(self, neurons, params):
        """Set membrane properties for different compartments."""
        # Set leak conductance and reversal potential
        neurons.gL = 1.0 / params.get('soma_rm', 10000.0) * b2.siemens / b2.meter**2
        neurons.EL = -70.0 * b2.mV
        
        # Set ion channel densities if enabled
        if params.get('channel_distribution', True):
            # Sodium channels
            neurons['soma'].gNa = params.get('soma_nav_density', 50.0) * b2.mS / b2.cm**2
            neurons['dendrite'].gNa = params.get('dendrite_nav_density', 10.0) * b2.mS / b2.cm**2
            if params.get('include_axon', True):
                neurons['axon'].gNa = params.get('ais_nav_density', 200.0) * b2.mS / b2.cm**2
            
            # Potassium channels
            neurons['soma'].gK = params.get('soma_kv_density', 30.0) * b2.mS / b2.cm**2
            neurons['dendrite'].gK = params.get('dendrite_kv_density', 5.0) * b2.mS / b2.cm**2
            if params.get('include_axon', True):
                neurons['axon'].gK = params.get('ais_kv_density', 100.0) * b2.mS / b2.cm**2
            
            # Reversal potentials
            neurons.ENa = 50.0 * b2.mV
            neurons.EK = -90.0 * b2.mV
            
            # Calcium channels in dendrites
            if params.get('dendrite_ca_density', 0.0) > 0:
                neurons['dendrite'].gCa = params.get('dendrite_ca_density', 0.5) * b2.mS / b2.cm**2
                neurons.ECa = 120.0 * b2.mV
            
            # H-channels in dendrites
            if params.get('dendrite_h_density', 0.0) > 0:
                neurons['dendrite'].gh = params.get('dendrite_h_density', 0.1) * b2.mS / b2.cm**2
                neurons.Eh = -30.0 * b2.mV
    
    def _build_point_neuron_fallback(self, num_neurons, multicomp_params, neuron_params):
        """Fallback to point neuron if spatial extension not available."""
        # Use enhanced point neuron with some multi-compartment features
        # Calculate total capacitance and conductance
        
        soma_area = np.pi * multicomp_params.get('soma_diameter', 20.0) * multicomp_params.get('soma_length', 20.0) * 1e-8  # cm²
        dend_area = multicomp_params.get('dendrite_segments', 10) * np.pi * 2.0 * 20.0 * 1e-8  # Approximate
        
        total_cm = (soma_area * multicomp_params.get('soma_cm', 1.0) + 
                   dend_area * multicomp_params.get('dendrite_cm', 1.0)) * b2.uF
        
        # Enhanced LIF with multi-compartment-like properties
        eqs = '''
        dv/dt = (gL*(EL - v) + INa + IK + I)/Cm : volt
        
        INa = gNa * m**3 * h * (ENa - v) : amp
        IK = gK * n**4 * (EK - v) : amp
        
        dm/dt = (alpha_m * (1 - m) - beta_m * m) : 1
        dh/dt = (alpha_h * (1 - h) - beta_h * h) : 1
        dn/dt = (alpha_n * (1 - n) - beta_n * n) : 1
        
        alpha_m = (2.5 - 0.1*(v/mV + 65)) / (exp(2.5 - 0.1*(v/mV + 65)) - 1) / ms : Hz
        beta_m = 4*exp(-(v/mV + 65)/18) / ms : Hz
        alpha_h = 0.07*exp(-(v/mV + 65)/20) / ms : Hz
        beta_h = 1/(exp(3 - 0.1*(v/mV + 65)) + 1) / ms : Hz
        alpha_n = (0.1 - 0.01*(v/mV + 65)) / (exp(1 - 0.1*(v/mV + 65)) - 1) / ms : Hz
        beta_n = 0.125*exp(-(v/mV + 65)/80) / ms : Hz
        
        gL : siemens
        gNa : siemens  
        gK : siemens
        I : amp
        '''
        
        neurons = b2.NeuronGroup(num_neurons, eqs,
                               threshold='v > -40*mV',
                               reset='v = -70*mV',
                               namespace={'Cm': total_cm, 'EL': -70*b2.mV, 
                                        'ENa': 50*b2.mV, 'EK': -90*b2.mV})
        
        # Set conductances based on areas and densities
        soma_gNa = soma_area * multicomp_params.get('soma_nav_density', 50.0) * 1e-3 * b2.siemens
        dend_gNa = dend_area * multicomp_params.get('dendrite_nav_density', 10.0) * 1e-3 * b2.siemens
        
        neurons.gL = soma_area / multicomp_params.get('soma_rm', 10000.0) * b2.siemens
        neurons.gNa = soma_gNa + dend_gNa
        neurons.gK = soma_area * multicomp_params.get('soma_kv_density', 30.0) * 1e-3 * b2.siemens
        
        # Initialize
        neurons.v = -70 * b2.mV
        neurons.m = 0.05
        neurons.h = 0.6
        neurons.n = 0.32
        
        return neurons
    
    def _setup_input_current(self, sim_params, neurons):
        """Setup input current stimulus."""
        # Fixed: Input current should be in nA to match GUI configuration
        current_amplitude = sim_params.get('input_current', 0.5) * b2.nA
        current_start = sim_params.get('current_start', 10) * b2.ms
        current_duration = sim_params.get('current_duration', 50) * b2.ms
        
        # Fixed: Proper TimedArray setup for current injection timing
        total_sim_time = sim_params.get('sim_time', 100) * b2.ms
        dt_step = 0.1 * b2.ms  # 0.1ms resolution for better timing precision
        
        # Create time points for current injection
        time_points = []
        current_values = []
        
        current_time = 0 * b2.ms
        while current_time <= total_sim_time:
            if current_start <= current_time < (current_start + current_duration):
                current_values.append(current_amplitude)
            else:
                current_values.append(0 * b2.nA)
            time_points.append(current_time)
            current_time += dt_step
        
        # Create timed input current with proper timing
        input_current = b2.TimedArray(current_values, dt=dt_step)
        
        # Apply current to neurons with proper Brian2 syntax
        neurons.I = input_current(b2.defaultclock.t)
        
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
    
    def _setup_input_patterns(self, input_params, neurons):
        """Setup external input patterns (Poisson, rhythmic, burst, step)."""
        if not input_params.get('enabled', False):
            return None
            
        pattern_type = input_params.get('pattern_type', 'poisson')
        
        if pattern_type == 'poisson':
            # Poisson spike train inputs
            rate = input_params.get('poisson_rate', 10.0) * b2.Hz
            weight = input_params.get('poisson_weight', 0.5) * b2.nS
            num_sources = input_params.get('poisson_num_sources', 50)
            
            # Create Poisson input group
            poisson_input = b2.PoissonGroup(num_sources, rate)
            
            # Create synapses from Poisson inputs to neurons
            input_synapses = b2.Synapses(poisson_input, neurons, 
                                       'w : siemens', on_pre='I += w * (0*mV - v)')
            
            # Connect each Poisson source to random neurons
            input_synapses.connect(p=0.1)  # 10% connection probability
            input_synapses.w = weight
            
            return {'poisson_group': poisson_input, 'input_synapses': input_synapses}
            
        elif pattern_type == 'rhythmic':
            # Rhythmic oscillatory input
            frequency = input_params.get('rhythmic_frequency', 10.0) * b2.Hz
            amplitude = input_params.get('rhythmic_amplitude', 0.2) * b2.nA
            phase = input_params.get('rhythmic_phase', 0.0) * b2.degree
            
            # Add rhythmic current modulation
            neurons.run_regularly(
                f'I += {amplitude} * sin(2*pi*{frequency}*t + {phase})', 
                dt=0.1*b2.ms
            )
            
            return {'type': 'rhythmic', 'frequency': frequency, 'amplitude': amplitude}
            
        elif pattern_type == 'burst':
            # Burst stimulation pattern
            burst_freq = input_params.get('burst_frequency', 100.0) * b2.Hz
            burst_duration = input_params.get('burst_duration', 10.0) * b2.ms
            burst_interval = input_params.get('burst_interval', 100.0) * b2.ms
            
            # Create burst pattern using PoissonGroup with time-varying rates
            # This is a simplified implementation - could be enhanced with TimedArray
            burst_input = b2.PoissonGroup(10, burst_freq)
            
            # Connect burst inputs
            burst_synapses = b2.Synapses(burst_input, neurons,
                                       'w : siemens', on_pre='I += w * 1*nA')
            burst_synapses.connect(p=0.2)
            burst_synapses.w = 0.5 * b2.nS
            
            return {'burst_group': burst_input, 'burst_synapses': burst_synapses}
            
        elif pattern_type == 'step':
            # Step current protocol
            try:
                levels_str = input_params.get('step_levels', '0.0, 0.5, 1.0, 0.0')
                durations_str = input_params.get('step_durations', '100, 200, 200, 100')
                
                levels = [float(x.strip()) for x in levels_str.split(',')]
                durations = [float(x.strip()) for x in durations_str.split(',')]
                
                if len(levels) != len(durations):
                    print("Warning: Step levels and durations must have same length")
                    return None
                
                # Create step current using TimedArray
                total_time = sum(durations) * b2.ms
                dt_step = 0.1 * b2.ms
                
                times = []
                currents = []
                current_time = 0
                
                for level, duration in zip(levels, durations):
                    duration_ms = duration * b2.ms
                    steps_in_duration = int(duration_ms / dt_step)
                    
                    for _ in range(steps_in_duration):
                        times.append(current_time)
                        currents.append(level * b2.nA)
                        current_time += dt_step
                
                step_current = b2.TimedArray(currents, dt=dt_step)
                neurons.run_regularly('I += step_current(t)', dt=dt_step)
                
                return {'type': 'step', 'levels': levels, 'durations': durations}
                
            except (ValueError, AttributeError) as e:
                print(f"Error parsing step parameters: {e}")
                return None
        
        return None
    
    def _build_network(self, network_params, advanced_params, synaptic_receptors_params, short_term_plasticity_params, neurons):
        """Build synaptic connections between neurons with multiple receptor types and plasticity."""
        if not network_params.get('synapse_enabled', False):
            return None
            
        if len(neurons) < 2:
            return None
            
        # Check if multiple receptor types are enabled
        multi_receptors = synaptic_receptors_params.get('enabled', False)
        stp_enabled = short_term_plasticity_params.get('enabled', False)
        
        if multi_receptors or stp_enabled:
            return self._build_advanced_synapses(network_params, advanced_params, 
                                               synaptic_receptors_params, short_term_plasticity_params, neurons)
        else:
            return self._build_simple_synapses(network_params, advanced_params, neurons)
    
    def _build_simple_synapses(self, network_params, advanced_params, neurons):
        """Build simple synapses (original implementation)."""
        synaptic_weight = network_params.get('synaptic_weight', 0.1) * b2.nA
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
    
    def _build_multi_receptor_synapses(self, network_params, advanced_params, synaptic_receptors_params, neurons):
        """Build synapses with multiple receptor types (AMPA, NMDA, GABA_A, GABA_B)."""
        
        # Determine which receptors are enabled
        ampa_enabled = synaptic_receptors_params.get('ampa_enabled', True)
        nmda_enabled = synaptic_receptors_params.get('nmda_enabled', True)
        gaba_a_enabled = synaptic_receptors_params.get('gaba_a_enabled', True)
        gaba_b_enabled = synaptic_receptors_params.get('gaba_b_enabled', False)
        
        # Get receptor parameters
        receptor_params = {}
        for receptor in ['ampa', 'nmda', 'gaba_a', 'gaba_b']:
            if synaptic_receptors_params.get(f'{receptor}_enabled', False):
                receptor_params[receptor] = {
                    'tau_rise': synaptic_receptors_params.get(f'{receptor}_tau_rise', 1.0) * b2.ms,
                    'tau_decay': synaptic_receptors_params.get(f'{receptor}_tau_decay', 5.0) * b2.ms,
                    'reversal': synaptic_receptors_params.get(f'{receptor}_reversal', 0.0) * b2.mV,
                    'weight_ratio': synaptic_receptors_params.get(f'{receptor}_weight_ratio', 1.0)
                }
        
        # Build synaptic equations based on enabled receptors
        synaptic_eqs = self._build_receptor_equations(receptor_params)
        
        # Create synapses with multiple receptor types
        synapses = b2.Synapses(neurons, neurons, synaptic_eqs, 
                              on_pre=self._build_receptor_on_pre(receptor_params),
                              namespace=self._build_receptor_namespace(receptor_params, synaptic_receptors_params))
        
        # Connect synapses based on topology
        self._connect_synapses(synapses, network_params, neurons)
        
        # Set synaptic weights
        base_weight = network_params.get('synaptic_weight', 1.0) * b2.nS
        for receptor in receptor_params:
            if hasattr(synapses, f'w_{receptor}'):
                setattr(synapses, f'w_{receptor}', 
                       base_weight * receptor_params[receptor]['weight_ratio'])
        
        return synapses
    
    def _build_receptor_equations(self, receptor_params):
        """Build Brian2 equations for multiple receptor types."""
        equations = []
        
        for receptor, params in receptor_params.items():
            # Double exponential synapse model
            equations.append(f'''
            ds_{receptor}/dt = -s_{receptor}/tau_rise_{receptor} : 1
            dx_{receptor}/dt = -x_{receptor}/tau_decay_{receptor} : 1
            I_{receptor} = w_{receptor} * x_{receptor} * (E_{receptor} - v_post) : amp
            w_{receptor} : siemens
            ''')
        
        # Add NMDA voltage dependence if enabled
        if 'nmda' in receptor_params:
            mg_conc = 1.0  # Will be set in namespace
            equations.append(f'''
            mg_block = 1 / (1 + mg_conc * exp(-0.062*v_post/mV) / 3.57) : 1
            I_nmda_blocked = I_nmda * mg_block : amp
            ''')
        
        # Total synaptic current
        current_terms = []
        for receptor in receptor_params:
            if receptor == 'nmda':
                current_terms.append('I_nmda_blocked')
            else:
                current_terms.append(f'I_{receptor}')
        
        if current_terms:
            equations.append(f'I_syn = {" + ".join(current_terms)} : amp')
        
        return '\n'.join(equations)
    
    def _build_receptor_on_pre(self, receptor_params):
        """Build on_pre equations for receptor activation."""
        on_pre_eqs = []
        
        for receptor in receptor_params:
            on_pre_eqs.append(f's_{receptor} += 1')
            on_pre_eqs.append(f'x_{receptor} += s_{receptor}')
        
        return '; '.join(on_pre_eqs)
    
    def _build_receptor_namespace(self, receptor_params, synaptic_receptors_params):
        """Build namespace for receptor parameters."""
        namespace = {}
        
        for receptor, params in receptor_params.items():
            namespace[f'tau_rise_{receptor}'] = params['tau_rise']
            namespace[f'tau_decay_{receptor}'] = params['tau_decay']
            namespace[f'E_{receptor}'] = params['reversal']
        
        # Add NMDA Mg2+ concentration if NMDA is enabled
        if 'nmda' in receptor_params:
            namespace['mg_conc'] = synaptic_receptors_params.get('nmda_mg_concentration', 1.0)
        
        return namespace
    
    def _connect_synapses(self, synapses, network_params, neurons):
        """Connect synapses based on network topology."""
        topology = network_params.get('topology_type', 'all_to_all')
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
            prob = topology_params.get('syn_prob', 0.1)
            synapses.connect(p=prob)
        # Add other topologies as needed
        
        return synapses
    
    def _build_advanced_synapses(self, network_params, advanced_params, synaptic_receptors_params, short_term_plasticity_params, neurons):
        """Build synapses with multiple receptors and/or short-term plasticity."""
        
        # Determine which features are enabled
        multi_receptors = synaptic_receptors_params.get('enabled', False)
        stp_enabled = short_term_plasticity_params.get('enabled', False)
        
        # Start with base synaptic equations
        synaptic_eqs = []
        on_pre_eqs = []
        namespace = {}
        
        # Add receptor equations if enabled
        if multi_receptors:
            receptor_params = self._get_receptor_params(synaptic_receptors_params)
            synaptic_eqs.extend(self._get_receptor_equations(receptor_params))
            on_pre_eqs.extend(self._get_receptor_on_pre(receptor_params))
            namespace.update(self._build_receptor_namespace(receptor_params, synaptic_receptors_params))
        else:
            # Simple synapse model
            synaptic_eqs.append('w : siemens')
            on_pre_eqs.append('I_post += w * (0*mV - v_post)')
        
        # Add short-term plasticity if enabled
        if stp_enabled:
            stp_eqs, stp_on_pre, stp_namespace = self._get_stp_equations(short_term_plasticity_params)
            synaptic_eqs.extend(stp_eqs)
            on_pre_eqs.extend(stp_on_pre)
            namespace.update(stp_namespace)
        
        # Combine equations
        full_equations = '\n'.join(synaptic_eqs)
        full_on_pre = '; '.join(on_pre_eqs)
        
        # Create synapses
        synapses = b2.Synapses(neurons, neurons, full_equations, 
                              on_pre=full_on_pre, namespace=namespace)
        
        # Connect synapses
        self._connect_synapses(synapses, network_params, neurons)
        
        # Initialize synaptic parameters
        self._initialize_synaptic_weights(synapses, network_params, synaptic_receptors_params, short_term_plasticity_params)
        
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
    
    def _get_stp_equations(self, stp_params):
        """Get equations for short-term plasticity."""
        plasticity_type = stp_params.get('plasticity_type', 'tsodyks_markram')
        equations = []
        on_pre = []
        namespace = {}
        
        if plasticity_type == 'tsodyks_markram':
            # Tsodyks-Markram model
            U = stp_params.get('tm_U', 0.5)
            tau_d = stp_params.get('tm_tau_d', 800.0) * b2.ms
            tau_f = stp_params.get('tm_tau_f', 50.0) * b2.ms
            
            equations.extend([
                'dx/dt = (1 - x) / tau_d : 1',  # Recovery from depression
                'du/dt = (U - u) / tau_f : 1',  # Facilitation decay
                'w_stp = w_base * u * x : siemens'  # Effective weight
            ])
            
            on_pre.extend([
                'u += U * (1 - u)',  # Facilitation
                'x *= (1 - u)',      # Depression
            ])
            
            namespace.update({
                'U': U,
                'tau_d': tau_d,
                'tau_f': tau_f
            })
            
        elif plasticity_type == 'simple_facilitation':
            tau_fac = stp_params.get('fac_tau', 100.0) * b2.ms
            fac_inc = stp_params.get('fac_increment', 0.1)
            fac_max = stp_params.get('fac_max', 3.0)
            
            equations.extend([
                'dfac/dt = -fac / tau_fac : 1',
                'w_stp = w_base * (1 + fac) : siemens'
            ])
            
            on_pre.append(f'fac = clip(fac + {fac_inc}, 0, {fac_max - 1})')
            
            namespace['tau_fac'] = tau_fac
            
        elif plasticity_type == 'simple_depression':
            tau_dep = stp_params.get('dep_tau', 500.0) * b2.ms
            dep_factor = stp_params.get('dep_factor', 0.8)
            dep_min = stp_params.get('dep_min', 0.1)
            
            equations.extend([
                'ddep/dt = (1 - dep) / tau_dep : 1',
                'w_stp = w_base * dep : siemens'
            ])
            
            on_pre.append(f'dep = clip(dep * {dep_factor}, {dep_min}, 1)')
            
            namespace['tau_dep'] = tau_dep
        
        return equations, on_pre, namespace
    
    def _initialize_synaptic_weights(self, synapses, network_params, synaptic_receptors_params, short_term_plasticity_params):
        """Initialize synaptic weights and plasticity variables."""
        base_weight = network_params.get('synaptic_weight', 1.0) * b2.nS
        
        # Set base weights
        if hasattr(synapses, 'w_base'):
            synapses.w_base = base_weight
        elif hasattr(synapses, 'w'):
            synapses.w = base_weight
        
        # Initialize STP variables
        if short_term_plasticity_params.get('enabled', False):
            plasticity_type = short_term_plasticity_params.get('plasticity_type', 'tsodyks_markram')
            
            if plasticity_type == 'tsodyks_markram':
                if hasattr(synapses, 'x'):
                    synapses.x = 1  # Start fully recovered
                if hasattr(synapses, 'u'):
                    U = short_term_plasticity_params.get('tm_U', 0.5)
                    synapses.u = U  # Start at baseline
                    
            elif plasticity_type == 'simple_facilitation':
                if hasattr(synapses, 'fac'):
                    synapses.fac = 0  # Start with no facilitation
                    
            elif plasticity_type == 'simple_depression':
                if hasattr(synapses, 'dep'):
                    synapses.dep = 1  # Start fully recovered
    
    def _get_calcium_equations(self, ca_params):
        """Get calcium dynamics equations."""
        ca_rest = ca_params.get('ca_rest', 0.1)  # μM
        extrusion_rate = ca_params.get('ca_extrusion_rate', 0.1)  # /ms
        buffer_enabled = ca_params.get('ca_buffer_enabled', True)
        
        equations = [f'''
        dCa/dt = (Ca_influx - {extrusion_rate}*(Ca - {ca_rest})) / (1 + buffer_ratio) : 1
        Ca_influx : 1
        ''']
        
        if buffer_enabled:
            buffer_capacity = ca_params.get('buffer_capacity', 200.0)
            buffer_kinetics = ca_params.get('buffer_kinetics', 1.0) * b2.ms
            equations.append(f'''
            buffer_ratio = {buffer_capacity} / (1 + Ca/{ca_rest}) : 1
            ''')
        else:
            equations.append('buffer_ratio = 0 : 1')
        
        # Add calcium sources
        ca_sources = ca_params.get('ca_sources', 'voltage_nmda')
        if 'voltage' in ca_sources or 'vgcc' in ca_sources:
            # Voltage-gated calcium channels
            if ca_params.get('ltype_channels', True):
                ltype_g = ca_params.get('ltype_conductance', 5.0)
                equations.append(f'''
                I_Ca_L = {ltype_g}*nS * m_Ca_L**2 * (50*mV - v) : amp
                dm_Ca_L/dt = (Ca_L_inf - m_Ca_L) / Ca_L_tau : 1
                Ca_L_inf = 1 / (1 + exp(-(v + 20*mV)/(7*mV))) : 1
                Ca_L_tau = 5*ms : second
                ''')
        
        return '\n'.join(equations)
    
    def _initialize_calcium(self, neurons, ca_params):
        """Initialize calcium variables in neurons."""
        ca_rest = ca_params.get('ca_rest', 0.1)
        
        # Initialize calcium concentration
        if hasattr(neurons, 'Ca'):
            neurons.Ca = ca_rest
        if hasattr(neurons, 'Ca_influx'):
            neurons.Ca_influx = 0
    
    def _build_gap_junctions(self, gap_params, neurons):
        """Build gap junctions (electrical synapses) between neurons."""
        if not gap_params.get('enabled', False):
            return None
        
        try:
            # Basic gap junction parameters
            conductance = gap_params.get('conductance', 0.1) * b2.nS
            connection_prob = gap_params.get('connection_probability', 0.1)
            coupling_coeff = gap_params.get('coupling_coefficient', 0.1)
            junction_type = gap_params.get('junction_type', 'symmetric')
            
            # Build gap junction equations
            gj_equations = self._get_gap_junction_equations(gap_params)
            
            # Create gap junction synapses
            gap_junctions = b2.Synapses(neurons, neurons, gj_equations)
            
            # Connect based on spatial organization
            self._connect_gap_junctions(gap_junctions, gap_params, neurons)
            
            # Set gap junction properties
            self._set_gap_junction_properties(gap_junctions, gap_params)
            
            return gap_junctions
            
        except Exception as e:
            print(f"Warning: Gap junction setup failed: {e}")
            return None
    
    def _get_gap_junction_equations(self, gap_params):
        """Get gap junction equations based on configuration."""
        junction_type = gap_params.get('junction_type', 'symmetric')
        voltage_dependent = gap_params.get('voltage_dependence', False)
        
        equations = []
        
        if junction_type == 'symmetric':
            # Symmetric bidirectional gap junction
            equations.append('g_gap : siemens')
            if voltage_dependent:
                equations.append('g_eff = g_gap * gating_factor : siemens')
                equations.append('''
                gating_factor = 1 / (1 + exp(-(v_post - v_pre - V_gate) / slope_gate)) : 1
                V_gate : volt
                slope_gate : volt
                ''')
                current_eq = 'I_gap = g_eff * (v_post - v_pre) : amp'
            else:
                current_eq = 'I_gap = g_gap * (v_post - v_pre) : amp'
                
        elif junction_type == 'asymmetric':
            # Asymmetric gap junction
            equations.append('g_gap : siemens')
            equations.append('asymmetry_factor : 1')
            if voltage_dependent:
                equations.append('g_eff = g_gap * gating_factor : siemens')
                equations.append('''
                gating_factor = 1 / (1 + exp(-(v_post - v_pre - V_gate) / slope_gate)) : 1
                V_gate : volt
                slope_gate : volt
                ''')
                current_eq = 'I_gap = g_eff * asymmetry_factor * (v_post - v_pre) : amp'
            else:
                current_eq = 'I_gap = g_gap * asymmetry_factor * (v_post - v_pre) : amp'
                
        elif junction_type == 'rectifying':
            # Rectifying gap junction (allows current in one direction preferentially)
            equations.append('g_gap : siemens')
            equations.append('rectification_factor : 1')
            current_eq = '''
            I_gap = g_gap * clip((v_post - v_pre) * rectification_factor, 0, inf) : amp
            '''
        
        equations.append(current_eq)
        
        # Add activity-dependent plasticity if enabled
        if gap_params.get('activity_dependent', False):
            equations.extend([
                'activity_pre : Hz',
                'activity_post : Hz',
                'plasticity_factor : 1',
                '''
                dplasticity_factor/dt = (
                    potentiation_rate * int(activity_pre > plasticity_threshold) * 
                    int(activity_post > plasticity_threshold) * (1 - plasticity_factor) -
                    depression_rate * plasticity_factor
                ) : 1/second
                ''',
                'potentiation_rate : Hz',
                'depression_rate : Hz', 
                'plasticity_threshold : Hz'
            ])
        
        # Add noise if enabled
        if gap_params.get('junction_noise', False):
            equations.extend([
                'noise_amplitude : siemens',
                'xi : 1 (linked)',  # Noise variable
                'g_noise = g_gap + noise_amplitude * xi : siemens'
            ])
        
        return '\n'.join(equations)
    
    def _connect_gap_junctions(self, gap_junctions, gap_params, neurons):
        """Connect gap junctions based on spatial organization."""
        spatial_org = gap_params.get('spatial_organization', 'distance_based')
        connection_prob = gap_params.get('connection_probability', 0.1)
        max_distance = gap_params.get('max_distance', 100.0)  # μm
        connection_specificity = gap_params.get('connection_specificity', 'all_to_all')
        
        N = len(neurons)
        
        if spatial_org == 'distance_based':
            # Connect based on distance (simplified as connection probability)
            gap_junctions.connect(condition='i != j', p=connection_prob)
            
        elif spatial_org == 'nearest_neighbor':
            # Connect to nearest neighbors
            for i in range(N):
                # Connect to next few neurons (wrapping around)
                for offset in [1, -1, 2, -2]:
                    j = (i + offset) % N
                    if i != j and np.random.random() < connection_prob:
                        gap_junctions.connect(i=i, j=j)
                        
        elif spatial_org == 'columnar':
            # Columnar organization (simplified)
            cluster_size = gap_params.get('cluster_size', 10)
            for start in range(0, N, cluster_size):
                end = min(start + cluster_size, N)
                for i in range(start, end):
                    for j in range(start, end):
                        if i != j and np.random.random() < connection_prob:
                            gap_junctions.connect(i=i, j=j)
                            
        elif spatial_org == 'radial_clusters':
            # Radial cluster organization
            cluster_size = gap_params.get('cluster_size', 10)
            num_clusters = max(1, N // cluster_size)
            
            for cluster in range(num_clusters):
                start = cluster * cluster_size
                end = min(start + cluster_size, N)
                # Connect all neurons within cluster
                for i in range(start, end):
                    for j in range(start, end):
                        if i != j and np.random.random() < connection_prob:
                            gap_junctions.connect(i=i, j=j)
                            
        else:  # random
            gap_junctions.connect(condition='i != j', p=connection_prob)
        
        # Make connections bidirectional (gap junctions are symmetric)
        if gap_params.get('junction_type', 'symmetric') == 'symmetric':
            # For each connection i->j, ensure j->i exists
            # This is simplified - in practice, we'd check existing connections
            pass  # Brian2 Synapses can handle bidirectional connections
    
    def _set_gap_junction_properties(self, gap_junctions, gap_params):
        """Set gap junction properties and parameters."""
        conductance = gap_params.get('conductance', 0.1) * b2.nS
        
        # Set basic conductance
        if hasattr(gap_junctions, 'g_gap'):
            gap_junctions.g_gap = conductance
        
        # Set voltage-dependent properties
        if gap_params.get('voltage_dependence', False):
            if hasattr(gap_junctions, 'V_gate'):
                gap_junctions.V_gate = gap_params.get('gating_voltage', -40.0) * b2.mV
            if hasattr(gap_junctions, 'slope_gate'):
                gap_junctions.slope_gate = gap_params.get('gating_slope', 10.0) * b2.mV
        
        # Set asymmetry factor
        if gap_params.get('junction_type') == 'asymmetric':
            if hasattr(gap_junctions, 'asymmetry_factor'):
                gap_junctions.asymmetry_factor = gap_params.get('coupling_coefficient', 0.1)
        
        # Set rectification factor
        if gap_params.get('junction_type') == 'rectifying':
            if hasattr(gap_junctions, 'rectification_factor'):
                gap_junctions.rectification_factor = 2.0  # Favor positive direction
        
        # Set activity-dependent plasticity parameters
        if gap_params.get('activity_dependent', False):
            if hasattr(gap_junctions, 'potentiation_rate'):
                gap_junctions.potentiation_rate = gap_params.get('potentiation_rate', 0.01) / b2.second
            if hasattr(gap_junctions, 'depression_rate'):
                gap_junctions.depression_rate = gap_params.get('depression_rate', 0.001) / b2.second
            if hasattr(gap_junctions, 'plasticity_threshold'):
                gap_junctions.plasticity_threshold = gap_params.get('plasticity_threshold', 20.0) * b2.Hz
            if hasattr(gap_junctions, 'plasticity_factor'):
                gap_junctions.plasticity_factor = 1.0
        
        # Set noise parameters
        if gap_params.get('junction_noise', False):
            if hasattr(gap_junctions, 'noise_amplitude'):
                gap_junctions.noise_amplitude = gap_params.get('noise_amplitude', 0.01) * b2.nS
        
        # Set developmental changes
        if gap_params.get('developmental_changes', False):
            initial_g = gap_params.get('initial_conductance', 0.5) * b2.nS
            if hasattr(gap_junctions, 'g_gap'):
                gap_junctions.g_gap = initial_g
            # Developmental changes would be implemented with TimedArray or run_regularly
        
        # Add neuromodulation effects
        if gap_params.get('neuromodulation', False):
            # This would require additional state variables for neuromodulator concentrations
            # Implementation depends on specific neuromodulator systems
            pass
    
    def _setup_homeostatic_plasticity(self, homeo_params, neurons, synapses):
        """Setup homeostatic plasticity mechanisms for network stability."""
        if not homeo_params.get('enabled', False):
            return None
        
        try:
            mechanisms = {}
            
            # Setup activity detection
            if homeo_params.get('activity_detection', 'spike_count') == 'spike_count':
                mechanisms['activity_monitor'] = self._setup_activity_detection(homeo_params, neurons)
            
            # Setup synaptic scaling
            if homeo_params.get('synaptic_scaling', False) and synapses is not None:
                mechanisms['synaptic_scaling'] = self._setup_synaptic_scaling(homeo_params, neurons, synapses)
            
            # Setup intrinsic excitability regulation
            if homeo_params.get('intrinsic_regulation', False):
                mechanisms['intrinsic_regulation'] = self._setup_intrinsic_regulation(homeo_params, neurons)
            
            # Setup threshold adaptation
            if homeo_params.get('threshold_adaptation', False):
                mechanisms['threshold_adaptation'] = self._setup_threshold_adaptation(homeo_params, neurons)
            
            # Setup BCM plasticity
            if homeo_params.get('bcm_plasticity', False):
                mechanisms['bcm_plasticity'] = self._setup_bcm_plasticity(homeo_params, neurons, synapses)
            
            # Setup network-level regulation
            if homeo_params.get('network_regulation', False):
                mechanisms['network_regulation'] = self._setup_network_regulation(homeo_params, neurons, synapses)
            
            return mechanisms
            
        except Exception as e:
            print(f"Warning: Homeostatic plasticity setup failed: {e}")
            return None
    
    def _setup_activity_detection(self, homeo_params, neurons):
        """Setup activity detection for homeostatic regulation."""
        detection_window = homeo_params.get('detection_window', 500.0) * b2.ms
        smoothing_tau = homeo_params.get('smoothing_tau', 2000.0) * b2.ms
        
        # Add activity detection variables to neurons
        neurons.avg_rate = 0.0 / b2.second
        neurons.spike_count = 0
        neurons.last_spike_time = -1000 * b2.ms
        
        # Setup activity tracking
        activity_update = f'''
        # Update average firing rate with exponential decay
        dt_since_spike = (t - last_spike_time)
        avg_rate = avg_rate * exp(-dt/{smoothing_tau}) + spike_count / {detection_window}
        spike_count = 0
        '''
        
        # Run activity detection regularly
        neurons.run_regularly(activity_update, dt=detection_window)
        
        # Track spikes
        neurons.run_regularly('spike_count += 1', when='after_thresholds')
        neurons.run_regularly('last_spike_time = t', when='after_thresholds')
        
        return {'detection_window': detection_window, 'smoothing_tau': smoothing_tau}
    
    def _setup_synaptic_scaling(self, homeo_params, neurons, synapses):
        """Setup synaptic scaling homeostatic mechanism."""
        target_rate = homeo_params.get('target_firing_rate', 5.0) * b2.Hz
        scaling_rate = homeo_params.get('scaling_rate', 0.01) / b2.second
        min_scaling = homeo_params.get('min_weight_scaling', 0.1)
        max_scaling = homeo_params.get('max_weight_scaling', 5.0)
        threshold = homeo_params.get('regulation_threshold', 0.2)
        
        # Add scaling factor to synapses
        if hasattr(synapses, 'w'):
            synapses.scaling_factor = 1.0
            synapses.w_base = synapses.w  # Store original weights
        
        # Synaptic scaling update rule
        scaling_update = f'''
        # Get postsynaptic neuron's activity
        post_rate = avg_rate_post
        rate_error = (post_rate - {target_rate}) / {target_rate}
        
        # Apply scaling if error exceeds threshold
        if abs(rate_error) > {threshold}:
            if rate_error > 0:  # Too much activity - scale down
                scaling_factor = scaling_factor * (1 - {scaling_rate} * dt)
            else:  # Too little activity - scale up
                scaling_factor = scaling_factor * (1 + {scaling_rate} * dt)
            
            # Clip scaling factor
            scaling_factor = clip(scaling_factor, {min_scaling}, {max_scaling})
            
            # Update weights
            w = w_base * scaling_factor
        '''
        
        # Apply scaling regularly
        synapses.run_regularly(scaling_update, dt=1000*b2.ms)
        
        return {
            'target_rate': target_rate,
            'scaling_rate': scaling_rate,
            'min_scaling': min_scaling,
            'max_scaling': max_scaling
        }
    
    def _setup_intrinsic_regulation(self, homeo_params, neurons):
        """Setup intrinsic excitability regulation."""
        target_rate = homeo_params.get('target_firing_rate', 5.0) * b2.Hz
        regulation_type = homeo_params.get('excitability_target', 'firing_rate')
        
        if regulation_type == 'firing_rate':
            # Add intrinsic excitability scaling
            neurons.excitability_factor = 1.0
            
            intrinsic_update = f'''
            rate_error = (avg_rate - {target_rate}) / {target_rate}
            if abs(rate_error) > 0.2:  # threshold
                if rate_error > 0:  # Too active - reduce excitability
                    excitability_factor = excitability_factor * 0.999
                else:  # Too quiet - increase excitability
                    excitability_factor = excitability_factor * 1.001
                
                # Clip excitability factor
                excitability_factor = clip(excitability_factor, 0.1, 3.0)
            '''
            
            neurons.run_regularly(intrinsic_update, dt=1000*b2.ms)
        
        return {'target_rate': target_rate, 'regulation_type': regulation_type}
    
    def _setup_threshold_adaptation(self, homeo_params, neurons):
        """Setup adaptive spike threshold mechanism."""
        target_rate = homeo_params.get('target_firing_rate', 5.0) * b2.Hz
        adaptation_rate = homeo_params.get('threshold_rate', 0.005) / b2.second
        min_threshold = homeo_params.get('min_threshold', -60.0) * b2.mV
        max_threshold = homeo_params.get('max_threshold', -40.0) * b2.mV
        
        # Add adaptive threshold variable
        neurons.v_th_adaptive = neurons.v_th if hasattr(neurons, 'v_th') else -50*b2.mV
        neurons.v_th_base = neurons.v_th_adaptive  # Store original threshold
        
        threshold_update = f'''
        rate_error = (avg_rate - {target_rate}) / {target_rate}
        
        if abs(rate_error) > 0.2:  # threshold for adaptation
            if rate_error > 0:  # Too active - increase threshold
                v_th_adaptive = v_th_adaptive + {adaptation_rate} * dt * mV
            else:  # Too quiet - decrease threshold
                v_th_adaptive = v_th_adaptive - {adaptation_rate} * dt * mV
            
            # Clip threshold
            v_th_adaptive = clip(v_th_adaptive, {min_threshold}, {max_threshold})
        '''
        
        neurons.run_regularly(threshold_update, dt=1000*b2.ms)
        
        return {
            'target_rate': target_rate,
            'adaptation_rate': adaptation_rate,
            'min_threshold': min_threshold,
            'max_threshold': max_threshold
        }
    
    def _setup_bcm_plasticity(self, homeo_params, neurons, synapses):
        """Setup BCM-like plasticity with sliding threshold."""
        bcm_tau = homeo_params.get('bcm_tau', 10000.0) * b2.ms
        bcm_power = homeo_params.get('bcm_power', 2.0)
        
        # Add BCM threshold variable
        if synapses is not None:
            synapses.theta_bcm = 1.0 * b2.Hz  # Sliding threshold
            
            bcm_update = f'''
            # Update sliding threshold based on postsynaptic activity
            dtheta_bcm/dt = (avg_rate_post**{bcm_power} - theta_bcm) / {bcm_tau} : Hz
            
            # BCM learning rule (simplified)
            bcm_factor = avg_rate_post * (avg_rate_post - theta_bcm)
            '''
            
            synapses.run_regularly(bcm_update, dt=100*b2.ms)
        
        return {'bcm_tau': bcm_tau, 'bcm_power': bcm_power}
    
    def _setup_network_regulation(self, homeo_params, neurons, synapses):
        """Setup network-level homeostatic regulation."""
        network_target = homeo_params.get('network_target_rate', 15.0) * b2.Hz
        global_scaling = homeo_params.get('global_scaling', False)
        inhibitory_control = homeo_params.get('inhibitory_gain_control', True)
        
        # Network-level variables
        network_rate = 0.0 * b2.Hz
        global_scaling_factor = 1.0
        
        if global_scaling and synapses is not None:
            synapses.global_scale = 1.0
            
            network_update = f'''
            # Calculate population firing rate
            network_rate = mean(avg_rate)
            rate_error = (network_rate - {network_target}) / {network_target}
            
            if abs(rate_error) > 0.1:  # Network threshold
                if rate_error > 0:  # Network too active
                    global_scale = global_scale * 0.999
                else:  # Network too quiet
                    global_scale = global_scale * 1.001
                    
                # Apply global scaling
                w = w * global_scale
            '''
            
            synapses.run_regularly(network_update, dt=2000*b2.ms)
        
        return {
            'network_target': network_target,
            'global_scaling': global_scaling,
            'inhibitory_control': inhibitory_control
        }
    
    def _setup_neuromodulation(self, neuromod_params, neurons, synapses):
        """Setup neuromodulation systems (dopamine, acetylcholine, etc.)."""
        if not neuromod_params.get('enabled', False):
            return None
        
        try:
            systems = {}
            
            # Setup dopamine system
            if neuromod_params.get('dopamine_system', False):
                systems['dopamine'] = self._setup_dopamine_system(neuromod_params, neurons, synapses)
            
            # Setup acetylcholine system
            if neuromod_params.get('acetylcholine_system', False):
                systems['acetylcholine'] = self._setup_acetylcholine_system(neuromod_params, neurons, synapses)
            
            # Setup serotonin system
            if neuromod_params.get('serotonin_system', False):
                systems['serotonin'] = self._setup_serotonin_system(neuromod_params, neurons, synapses)
            
            # Setup noradrenaline system
            if neuromod_params.get('noradrenaline_system', False):
                systems['noradrenaline'] = self._setup_noradrenaline_system(neuromod_params, neurons, synapses)
            
            # Setup release patterns
            self._setup_neuromodulator_release(neuromod_params, systems, neurons)
            
            # Setup pharmacological interventions
            if neuromod_params.get('pharmacology', False):
                systems['pharmacology'] = self._setup_pharmacology(neuromod_params, systems, neurons)
            
            return systems
            
        except Exception as e:
            print(f"Warning: Neuromodulation setup failed: {e}")
            return None
    
    def _setup_dopamine_system(self, neuromod_params, neurons, synapses):
        """Setup dopaminergic neuromodulation system."""
        baseline = neuromod_params.get('dopamine_baseline', 0.1)  # μM
        clearance_tau = neuromod_params.get('dopamine_clearance_tau', 1000.0) * b2.ms
        d1_effect = neuromod_params.get('dopamine_d1_effect', 0.2)
        d2_effect = neuromod_params.get('dopamine_d2_effect', -0.15)
        
        # Add dopamine concentration variable to neurons
        neurons.DA_conc = baseline  # Dopamine concentration
        neurons.DA_d1_activation = 0.0  # D1 receptor activation
        neurons.DA_d2_activation = 0.0  # D2 receptor activation
        
        # Dopamine dynamics equations
        dopamine_dynamics = f'''
        # Dopamine clearance
        dDA_conc/dt = -DA_conc / {clearance_tau} : 1
        
        # Receptor activation (simplified Hill equation)
        DA_d1_activation = DA_conc / (DA_conc + 0.1) : 1
        DA_d2_activation = DA_conc / (DA_conc + 0.2) : 1
        '''
        
        neurons.run_regularly(dopamine_dynamics, dt=10*b2.ms)
        
        # Apply dopamine effects on neural properties
        if neuromod_params.get('affect_excitability', True):
            excitability_modulation = f'''
            # D1 increases excitability, D2 decreases it
            DA_excitability_effect = {d1_effect} * DA_d1_activation + {d2_effect} * DA_d2_activation
            '''
            neurons.run_regularly(excitability_modulation, dt=100*b2.ms)
        
        # Apply dopamine effects on synaptic transmission
        if neuromod_params.get('affect_synaptic_transmission', True) and synapses is not None:
            synaptic_modulation = f'''
            # Dopamine modulates synaptic strength
            DA_synaptic_effect = 1 + ({d1_effect} * DA_d1_activation_post + {d2_effect} * DA_d2_activation_post)
            '''
            synapses.run_regularly(synaptic_modulation, dt=100*b2.ms)
        
        return {
            'baseline': baseline,
            'clearance_tau': clearance_tau,
            'd1_effect': d1_effect,
            'd2_effect': d2_effect
        }
    
    def _setup_acetylcholine_system(self, neuromod_params, neurons, synapses):
        """Setup cholinergic neuromodulation system."""
        baseline = neuromod_params.get('acetylcholine_baseline', 0.05)  # μM
        clearance_tau = neuromod_params.get('acetylcholine_clearance_tau', 200.0) * b2.ms
        nicotinic_effect = neuromod_params.get('nicotinic_effect', 0.3)
        muscarinic_effect = neuromod_params.get('muscarinic_effect', 0.15)
        
        # Add acetylcholine concentration variable to neurons
        neurons.ACh_conc = baseline
        neurons.ACh_nicotinic_activation = 0.0
        neurons.ACh_muscarinic_activation = 0.0
        
        # Acetylcholine dynamics
        ach_dynamics = f'''
        # ACh clearance (faster than dopamine)
        dACh_conc/dt = -ACh_conc / {clearance_tau} : 1
        
        # Receptor activation
        ACh_nicotinic_activation = ACh_conc / (ACh_conc + 0.02) : 1
        ACh_muscarinic_activation = ACh_conc / (ACh_conc + 0.05) : 1
        '''
        
        neurons.run_regularly(ach_dynamics, dt=5*b2.ms)
        
        # Acetylcholine effects on attention and plasticity
        if neuromod_params.get('affect_excitability', True):
            ach_excitability = f'''
            # ACh generally increases excitability and attention
            ACh_excitability_effect = {nicotinic_effect} * ACh_nicotinic_activation + {muscarinic_effect} * ACh_muscarinic_activation
            '''
            neurons.run_regularly(ach_excitability, dt=100*b2.ms)
        
        # ACh effects on synaptic plasticity
        if neuromod_params.get('affect_plasticity', True) and synapses is not None:
            ach_plasticity = f'''
            # ACh facilitates synaptic plasticity
            ACh_plasticity_effect = 1 + {nicotinic_effect} * ACh_nicotinic_activation_post
            '''
            synapses.run_regularly(ach_plasticity, dt=100*b2.ms)
        
        return {
            'baseline': baseline,
            'clearance_tau': clearance_tau,
            'nicotinic_effect': nicotinic_effect,
            'muscarinic_effect': muscarinic_effect
        }
    
    def _setup_serotonin_system(self, neuromod_params, neurons, synapses):
        """Setup serotonergic neuromodulation system."""
        baseline = neuromod_params.get('serotonin_baseline', 0.02)  # μM
        clearance_tau = neuromod_params.get('serotonin_clearance_tau', 500.0) * b2.ms
        ht1a_effect = neuromod_params.get('5ht1a_effect', -0.1)
        ht2a_effect = neuromod_params.get('5ht2a_effect', 0.15)
        
        # Add serotonin concentration variable to neurons
        neurons.Serotonin_conc = baseline
        neurons.Serotonin_5ht1a_activation = 0.0
        neurons.Serotonin_5ht2a_activation = 0.0
        
        # Serotonin dynamics
        serotonin_dynamics = f'''
        # Serotonin clearance
        dSerotonin_conc/dt = -Serotonin_conc / {clearance_tau} : 1
        
        # Receptor activation (different affinities)
        Serotonin_5ht1a_activation = Serotonin_conc / (Serotonin_conc + 0.01) : 1
        Serotonin_5ht2a_activation = Serotonin_conc / (Serotonin_conc + 0.03) : 1
        '''
        
        neurons.run_regularly(serotonin_dynamics, dt=10*b2.ms)
        
        # Serotonin effects on mood and arousal
        if neuromod_params.get('affect_excitability', True):
            serotonin_excitability = f'''
            # 5-HT1A typically inhibitory, 5-HT2A excitatory
            Serotonin_excitability_effect = {ht1a_effect} * Serotonin_5ht1a_activation + {ht2a_effect} * Serotonin_5ht2a_activation
            '''
            neurons.run_regularly(serotonin_excitability, dt=100*b2.ms)
        
        return {
            'baseline': baseline,
            'clearance_tau': clearance_tau,
            '5ht1a_effect': ht1a_effect,
            '5ht2a_effect': ht2a_effect
        }
    
    def _setup_noradrenaline_system(self, neuromod_params, neurons, synapses):
        """Setup noradrenergic neuromodulation system."""
        baseline = neuromod_params.get('noradrenaline_baseline', 0.03)  # μM
        clearance_tau = neuromod_params.get('noradrenaline_clearance_tau', 800.0) * b2.ms
        alpha1_effect = neuromod_params.get('alpha1_effect', 0.2)
        alpha2_effect = neuromod_params.get('alpha2_effect', -0.1)
        beta_effect = neuromod_params.get('beta_effect', 0.15)
        
        # Add noradrenaline concentration variable to neurons
        neurons.NA_conc = baseline
        neurons.NA_alpha1_activation = 0.0
        neurons.NA_alpha2_activation = 0.0
        neurons.NA_beta_activation = 0.0
        
        # Noradrenaline dynamics
        na_dynamics = f'''
        # Noradrenaline clearance
        dNA_conc/dt = -NA_conc / {clearance_tau} : 1
        
        # Receptor activation
        NA_alpha1_activation = NA_conc / (NA_conc + 0.02) : 1
        NA_alpha2_activation = NA_conc / (NA_conc + 0.05) : 1
        NA_beta_activation = NA_conc / (NA_conc + 0.03) : 1
        '''
        
        neurons.run_regularly(na_dynamics, dt=10*b2.ms)
        
        # Noradrenaline effects on attention and arousal
        if neuromod_params.get('affect_excitability', True):
            na_excitability = f'''
            # Complex noradrenergic effects
            NA_excitability_effect = ({alpha1_effect} * NA_alpha1_activation + 
                                    {alpha2_effect} * NA_alpha2_activation + 
                                    {beta_effect} * NA_beta_activation)
            '''
            neurons.run_regularly(na_excitability, dt=100*b2.ms)
        
        return {
            'baseline': baseline,
            'clearance_tau': clearance_tau,
            'alpha1_effect': alpha1_effect,
            'alpha2_effect': alpha2_effect,
            'beta_effect': beta_effect
        }
    
    def _setup_neuromodulator_release(self, neuromod_params, systems, neurons):
        """Setup neuromodulator release patterns."""
        release_trigger = neuromod_params.get('release_triggers', 'manual')
        activity_threshold = neuromod_params.get('activity_threshold', 20.0) * b2.Hz
        release_duration = neuromod_params.get('release_duration', 2000.0) * b2.ms
        release_interval = neuromod_params.get('release_interval', 10000.0) * b2.ms
        
        if release_trigger == 'activity_dependent':
            # Release based on network activity
            release_code = f'''
            # Check if average activity exceeds threshold
            if mean(avg_rate) > {activity_threshold}:
                # Trigger release for all active systems
                if 'dopamine' in systems:
                    DA_conc = DA_conc + {neuromod_params.get("dopamine_release_rate", 0.01)}
                if 'acetylcholine' in systems:
                    ACh_conc = ACh_conc + {neuromod_params.get("acetylcholine_release_rate", 0.005)}
                if 'serotonin' in systems:
                    Serotonin_conc = Serotonin_conc + {neuromod_params.get("serotonin_release_rate", 0.002)}
                if 'noradrenaline' in systems:
                    NA_conc = NA_conc + {neuromod_params.get("noradrenaline_release_rate", 0.003)}
            '''
            
            neurons.run_regularly(release_code, dt=1000*b2.ms)
            
        elif release_trigger == 'temporal_pattern':
            # Periodic release
            release_times = []
            current_time = release_interval
            sim_time = 100000.0 * b2.ms  # Estimate sim time
            
            while current_time < sim_time:
                release_times.append(current_time)
                current_time += release_interval
            
            # Would implement with TimedArray in full implementation
            
        return {
            'release_trigger': release_trigger,
            'activity_threshold': activity_threshold,
            'release_duration': release_duration,
            'release_interval': release_interval
        }
    
    def _setup_pharmacology(self, neuromod_params, systems, neurons):
        """Setup pharmacological interventions."""
        drug_type = neuromod_params.get('drug_type', 'dopamine_agonist')
        drug_concentration = neuromod_params.get('drug_concentration', 0.1)
        onset_time = neuromod_params.get('drug_onset_time', 10000.0) * b2.ms
        duration = neuromod_params.get('drug_duration', 30000.0) * b2.ms
        
        # Implement drug effects based on type
        if 'dopamine' in drug_type:
            if 'agonist' in drug_type:
                # Increase dopamine effects
                drug_effect = f'''
                if t > {onset_time} and t < {onset_time + duration}:
                    DA_conc = DA_conc + {drug_concentration} * 0.001  # Gradual increase
                '''
            else:  # antagonist
                # Block dopamine receptors
                drug_effect = f'''
                if t > {onset_time} and t < {onset_time + duration}:
                    DA_d1_activation = DA_d1_activation * 0.1  # Block receptors
                    DA_d2_activation = DA_d2_activation * 0.1
                '''
            
            neurons.run_regularly(drug_effect, dt=100*b2.ms)
        
        # Similar implementations for other drug types...
        
        return {
            'drug_type': drug_type,
            'drug_concentration': drug_concentration,
            'onset_time': onset_time,
            'duration': duration
        }
