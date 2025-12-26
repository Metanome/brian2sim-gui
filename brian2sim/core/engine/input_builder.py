"""
Input Builder for Brian2 simulations.
Handles input currents, noise, and external input patterns.
"""

try:
    import brian2 as b2

    BRIAN2_AVAILABLE = True
except ImportError:
    BRIAN2_AVAILABLE = False


class InputBuilder:
    """Builder class for constructing input stimuli."""

    def __init__(self):
        self.input_current = None
        self.noise_source = None
        self.input_patterns = None

    def setup_input_current(self, sim_params, neurons):
        """Setup input current stimulus."""
        if not BRIAN2_AVAILABLE:
            return None

        current_amplitude = sim_params.get("input_current", 0.5) * b2.nA
        current_start = sim_params.get("current_start", 10) * b2.ms
        current_duration = sim_params.get("current_duration", 50) * b2.ms

        total_sim_time = sim_params.get("sim_time", 100) * b2.ms
        dt_step = 0.1 * b2.ms

        current_values = []
        current_time = 0 * b2.ms

        while current_time <= total_sim_time:
            if current_start <= current_time < (current_start + current_duration):
                current_values.append(float(current_amplitude / b2.amp))
            else:
                current_values.append(0.0)
            current_time += dt_step

        input_current = b2.TimedArray(current_values * b2.amp, dt=dt_step)
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
            neurons.run_regularly(f"I += {intensity} * randn()", dt=0.1 * b2.ms)
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
