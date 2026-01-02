"""
Input Builder for Brian2 simulations.
Handles input currents, noise, and external input patterns.
"""


try:
    import brian2 as b2
    import numpy as np
    import os

    BRIAN2_AVAILABLE = True
except ImportError:
    BRIAN2_AVAILABLE = False


class InputBuilder:
    """Builder class for constructing input stimuli."""

    def __init__(self):
        self.input_current = None
        self.noise_source = None
        self.input_patterns = None

    def setup_input_current(self, sim_params, neurons, model_type="lif"):
        """
        Setup input current stimulus.
        
        Args:
            sim_params: Simulation parameters including input_current, current_start, etc.
            neurons: The NeuronGroup to apply input to
            model_type: The neuron model type (lif, izhikevich, adex, hodgkin_huxley)
        """
        if not BRIAN2_AVAILABLE:
            return None

        current_amplitude = sim_params.get("input_current", 0.5)
        current_start = sim_params.get("current_start", 10) * b2.ms
        current_duration = sim_params.get("current_duration", 50) * b2.ms

        total_sim_time = sim_params.get("sim_time", 100) * b2.ms
        dt_step = 0.1 * b2.ms

        # Determine if model uses dimensionless I or amp-based I
        is_dimensionless = model_type in ["izhikevich"]

        current_values = []
        current_time = 0 * b2.ms

        while current_time <= total_sim_time:
            if current_start <= current_time < (current_start + current_duration):
                current_values.append(float(current_amplitude))
            else:
                current_values.append(0.0)
            current_time += dt_step

        if is_dimensionless:
            # For Izhikevich: I is dimensionless, directly use the value
            input_current = b2.TimedArray(current_values, dt=dt_step)
        else:
            # For LIF, AdEx, HH: I is in amps
            input_current = b2.TimedArray(current_values * b2.nA, dt=dt_step)

        neurons.run_regularly("I = input_current(t)", dt=dt_step)
        neurons.namespace["input_current"] = input_current

        self.input_current = input_current
        return input_current

    def setup_noise(self, noise_params, neurons):
        """Setup noise input if enabled."""
        if not noise_params.get("enabled", False):
            return None

        intensity = noise_params.get("intensity", 0.1) * b2.nA
        method = noise_params.get("method", "Gaussian")

        if method == "Gaussian":
            # Extract scalar value for use in string equation
            intensity_val = float(intensity / b2.nA)
            neurons.run_regularly(f"I += {intensity_val}*nA * randn()", dt=0.1 * b2.ms)
        elif method == "Ornstein-Uhlenbeck":
            tau_noise = noise_params.get("correlation_time", 5) * b2.ms
            neurons.equations += b2.Equations(
                f"""
                dI_noise/dt = -I_noise/tau_noise + sigma*sqrt(2/tau_noise)*xi : amp
                """,
                tau_noise=tau_noise,
                sigma=intensity,
            )
            neurons.run_regularly("I += I_noise", dt=0.1 * b2.ms)

        self.noise_source = True
        return True

    def setup_input_patterns(self, input_params, neurons):
        """Setup external input patterns (Poisson, rhythmic, burst, step)."""
        if not input_params.get("enabled", False):
            return None

        pattern_type = input_params.get("pattern_type", "poisson")

        if pattern_type == "poisson":
            return self._setup_poisson_pattern(input_params, neurons)
        elif pattern_type == "rhythmic":
            return self._setup_rhythmic_pattern(input_params, neurons)
        elif pattern_type == "burst":
            return self._setup_burst_pattern(input_params, neurons)
        elif pattern_type == "step":
            return self._setup_step_pattern(input_params, neurons)
        elif pattern_type == "spike_generator":
            return self._setup_spike_generator(input_params, neurons)
        elif pattern_type == "timed_array":
            return self._setup_timed_array(input_params, neurons)

        return None

    def _setup_poisson_pattern(self, input_params, neurons):
        """Setup Poisson spike train inputs."""
        rate = input_params.get("poisson_rate", 10.0) * b2.Hz
        weight = input_params.get("poisson_weight", 0.5) * b2.nS
        num_sources = input_params.get("poisson_num_sources", 50)

        poisson_input = b2.PoissonGroup(num_sources, rate)
        input_synapses = b2.Synapses(
            poisson_input, neurons, "w : siemens", on_pre="I += w * (0*mV - v)"
        )
        input_synapses.connect(p=0.1)
        input_synapses.w = weight

        return {"poisson_group": poisson_input, "input_synapses": input_synapses}

    def _setup_rhythmic_pattern(self, input_params, neurons):
        """Setup rhythmic oscillatory input."""
        frequency = input_params.get("rhythmic_frequency", 10.0) * b2.Hz
        amplitude = input_params.get("rhythmic_amplitude", 0.2) * b2.nA
        phase = input_params.get("rhythmic_phase", 0.0) * b2.degree

        neurons.run_regularly(
            f"I += {amplitude} * sin(2*pi*{frequency}*t + {phase})", dt=0.1 * b2.ms
        )

        return {"type": "rhythmic", "frequency": frequency, "amplitude": amplitude}

    def _setup_burst_pattern(self, input_params, neurons):
        """Setup burst stimulation pattern."""
        burst_freq = input_params.get("burst_frequency", 100.0) * b2.Hz

        burst_input = b2.PoissonGroup(10, burst_freq)
        burst_synapses = b2.Synapses(burst_input, neurons, "w : siemens", on_pre="I += w * 1*nA")
        burst_synapses.connect(p=0.2)
        burst_synapses.w = 0.5 * b2.nS

        return {"burst_group": burst_input, "burst_synapses": burst_synapses}

    def _setup_step_pattern(self, input_params, neurons):
        """Setup step current protocol."""
        try:
            levels_str = input_params.get("step_levels", "0.0, 0.5, 1.0, 0.0")
            durations_str = input_params.get("step_durations", "100, 200, 200, 100")

            levels = [float(x.strip()) for x in levels_str.split(",")]
            durations = [float(x.strip()) for x in durations_str.split(",")]

            if len(levels) != len(durations):
                return None

            dt_step = 0.1 * b2.ms
            currents = []

            for level, duration in zip(levels, durations):
                duration_ms = duration * b2.ms
                steps_in_duration = int(duration_ms / dt_step)
                for _ in range(steps_in_duration):
                    currents.append(level * b2.nA)

            step_current = b2.TimedArray(currents, dt=dt_step)
            neurons.run_regularly("I += step_current(t)", dt=dt_step)
            neurons.namespace["step_current"] = step_current

            return {"type": "step", "levels": levels, "durations": durations}

        except (ValueError, AttributeError):
            return None

    def _setup_spike_generator(self, input_params, neurons):
        """Setup precise spike timing input using SpikeGeneratorGroup."""
        try:
            # Check for file input first
            file_path = input_params.get("spike_file_path", "")
            indices = []
            times = []
            
            if file_path and os.path.exists(file_path):
                try:
                    if file_path.endswith('.npy'):
                        data = np.load(file_path, allow_pickle=True)
                        if isinstance(data, dict) or (isinstance(data, np.ndarray) and data.dtype.names):
                            # Assume dict or struct array
                            indices = data['indices'] if 'indices' in data else data['index']
                            times = data['times'] if 'times' in data else data['time']
                        else:
                             # Assume 2D array [index, time]
                            indices = data[:, 0].astype(int)
                            times = data[:, 1]
                    elif file_path.endswith('.csv') or file_path.endswith('.txt'):
                        # Assume CSV without header or with header skipped? 
                        # Simple loadtxt
                        data = np.loadtxt(file_path, delimiter=',', skiprows=1 if file_path.endswith('.csv') else 0)
                        indices = data[:, 0].astype(int)
                        times = data[:, 1]
                except Exception as e:
                    print(f"Error loading spike file: {e}")
                    return None
            else:
                # Text input fallback
                indices_str = input_params.get("spike_indices", "0, 0, 1, 2")
                times_str = input_params.get("spike_times", "10, 20, 15, 30")

                indices = [int(x.strip()) for x in indices_str.split(",")]
                times = [float(x.strip()) for x in times_str.split(",")]

            if len(indices) != len(times):
                print("Error: Spike indices and times must have the same length.")
                return None

            # Convert times to b2.ms
            # Ensure times are unitless first if numpy loaded them
            times = np.array(times)
            times_units = times * b2.ms

            # Determine number of sources (max index + 1 or user specified?)
            num_sources = max(indices) + 1 if len(indices) > 0 else 1

            spike_input = b2.SpikeGeneratorGroup(num_sources, indices, times_units)
            
            # Connect via synapses
            weight = input_params.get("poisson_weight", 0.5) * b2.nS
            
            input_synapses = b2.Synapses(
                spike_input, neurons, "w : siemens", on_pre="I += w * (0*mV - v)"
            )
            input_synapses.connect(p=0.5)
            input_synapses.w = weight

            return {"spike_group": spike_input, "input_synapses": input_synapses}

        except (ValueError, AttributeError, IndexError) as e:
            print(f"Error setup_spike_generator: {e}")
            return None

    def _setup_timed_array(self, input_params, neurons):
        """Setup time-varying current input using TimedArray."""
        try:
            dt_val = input_params.get("timed_dt", 1.0)
            file_path = input_params.get("timed_array_file_path", "")
            values = []
            
            if file_path and os.path.exists(file_path):
                try:
                    if file_path.endswith('.npy'):
                        values = np.load(file_path)
                    elif file_path.endswith('.csv') or file_path.endswith('.txt'):
                        values = np.loadtxt(file_path, delimiter=',')
                except Exception as e:
                    print(f"Error loading timed array file: {e}")
                    return None
            else:
                # Text input
                values_str = input_params.get("timed_values", "0, 0.2, 0.5, 0.2, 0")
                values = [float(x.strip()) for x in values_str.split(",")]
            
            # Ensure numpy array
            values = np.array(values)
            
            # Create TimedArray
            timed_input = b2.TimedArray(values * b2.nA, dt=dt_val * b2.ms)
            
            expression = "I = timed_input(t, i)" if values.ndim > 1 else "I = timed_input(t)"
            
            return {
                "timed_array": timed_input, 
                "run_reg": neurons.run_regularly(expression, dt=dt_val*b2.ms)
            }
            # Note: `run_reg` is a Runner object.
             
        except Exception as e:
            print(f"Error setup_timed_array: {e}")
            return None
