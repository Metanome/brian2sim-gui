import json

from PyQt6.QtWidgets import QMessageBox


class ConfigManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def validate_all_parameters(self):
        """
        Validate all current parameters in the GUI.

        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        # Get all current configuration from the GUI
        config_data = self._get_current_config()

        # Use the existing validate_parameters method
        return self.validate_parameters(config_data)

    def _get_current_config(self):
        """Get current configuration from all GUI components."""
        config_data = {}

        # Get neuron model settings
        if hasattr(self.main_window, "neuron_models_manager"):
            config_data["neuron_model"] = (
                self.main_window.neuron_models_manager.get_neuron_model_config()
            )

        # Get simulation parameters
        if hasattr(self.main_window, "sim_params_manager"):
            config_data["simulation"] = self.main_window.sim_params_manager.get_sim_params_config()

        # Get noise options
        if hasattr(self.main_window, "noise_manager"):
            config_data["noise"] = self.main_window.noise_manager.get_config()

        # Get network options
        if hasattr(self.main_window, "network_manager"):
            config_data["network"] = (
                self.main_window.network_manager.get_config()
            )

        # Get advanced network options
        if hasattr(self.main_window, "advanced_network_manager"):
            config_data["advanced_network"] = (
                self.main_window.advanced_network_manager.get_advanced_network_config()
            )

        # Get gap junctions configuration
        if hasattr(self.main_window, "gap_junctions_ui"):
            config_data["gap_junctions"] = self.main_window.gap_junctions_ui.get_params_for_save()

        # Get synaptic receptors configuration
        if hasattr(self.main_window, "synaptic_receptors_ui"):
            config_data["synaptic_receptors"] = (
                self.main_window.synaptic_receptors_ui.get_params_for_save()
            )

        # Get calcium dynamics configuration
        if hasattr(self.main_window, "calcium_dynamics_ui"):
            config_data["calcium_dynamics"] = (
                self.main_window.calcium_dynamics_ui.get_params_for_save()
            )

        # Get homeostatic plasticity configuration
        if hasattr(self.main_window, "homeostatic_plasticity_ui"):
            config_data["homeostatic_plasticity"] = (
                self.main_window.homeostatic_plasticity_ui.get_params_for_save()
            )

        # Get neuromodulation configuration
        if hasattr(self.main_window, "neuromodulation_ui"):
            config_data["neuromodulation"] = (
                self.main_window.neuromodulation_ui.get_params_for_save()
            )

        # Get multicompartment configuration
        if hasattr(self.main_window, "multicompartment_ui"):
            config_data["multicompartment"] = (
                self.main_window.multicompartment_ui.get_params_for_save()
            )

        # Get short-term plasticity configuration
        if hasattr(self.main_window, "short_term_plasticity_ui"):
            config_data["short_term_plasticity"] = (
                self.main_window.short_term_plasticity_ui.get_params_for_save()
            )

        return config_data

    def save_config_to_file(self, file_path):
        """
        Convenience method to gather current config from GUI and save to file.
        
        Args:
            file_path (str): The path to save the configuration to
        """
        config_data = self._get_current_config()
        self.save_config(config_data, file_path)

    def save_config(self, config_data, file_path):
        """
        Save configuration data to a JSON file.

        Args:
            config_data (dict): The configuration data to save
            file_path (str): The path to save the file to
        """
        # Validate parameters before saving
        is_valid, error_msg = self.validate_parameters(config_data)
        if not is_valid:
            QMessageBox.warning(
                self.main_window,
                "Invalid Configuration",
                f"Configuration contains invalid parameters:\n{error_msg}",
            )
            return

        try:
            with open(file_path, "w") as f:
                json.dump(config_data, f, indent=4)
            QMessageBox.information(
                self.main_window, "Success", "Configuration saved successfully."
            )
        except Exception as e:
            QMessageBox.critical(
                self.main_window, "Error", f"An unexpected error occurred during save: {e}"
            )

    def load_config(self, file_path):
        """
        Load configuration data from a JSON file.

        Args:
            file_path (str): The path to load the configuration from

        Returns:
            dict: The loaded configuration data, or None if loading failed
        """
        try:
            with open(file_path, "r") as f:
                config_data = json.load(f)

            # Validate parameters before loading
            is_valid, error_msg = self.validate_parameters(config_data)
            if not is_valid:
                QMessageBox.warning(
                    self.main_window,
                    "Invalid Configuration",
                    f"Configuration contains invalid parameters:\n{error_msg}",
                )
                return None

            return config_data

        except json.JSONDecodeError:
            QMessageBox.warning(
                self.main_window, "Error", "Invalid JSON file. Could not load configuration."
            )
            return None
        except Exception as e:
            QMessageBox.critical(
                self.main_window, "Error", f"An unexpected error occurred during load: {e}"
            )
            return None

    def validate_parameters(self, config_data):
        """
        Validate configuration parameters.

        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        # Base validation
        if not isinstance(config_data, dict):
            return False, "Configuration data must be a dictionary"
            # Check for required sections
        required_sections = ["neuron_model", "simulation"]
        missing_sections = [s for s in required_sections if s not in config_data]
        if missing_sections:
            return False, f"Missing required sections: {', '.join(missing_sections)}"

        # Validate simulation parameters
        sim_params = config_data["simulation"]
        if not isinstance(sim_params, dict):
            return False, "Simulation parameters must be a dictionary"

        # Validate sim_time
        sim_time = sim_params.get("sim_time", 0)
        if not (1 <= sim_time <= 100000):  # 1ms to 100s
            return False, "Simulation time must be between 1 and 100000 ms"

        # Validate input_current
        input_current = sim_params.get("input_current", 0)
        if not (-1000 <= input_current <= 1000):  # -1000 to 1000 pA
            return False, "Input current must be between -1000 and 1000 pA"

        # Validate num_neurons
        num_neurons = sim_params.get("num_neurons", 0)
        if not isinstance(num_neurons, int) or not (1 <= num_neurons <= 100000):
            return False, "Number of neurons must be an integer between 1 and 100000"

        # Validate current_start
        current_start = sim_params.get("current_start", 0)
        if not isinstance(current_start, (int, float)) or not (0 <= current_start <= sim_time):
            return False, f"Current start must be between 0 and {sim_time} ms"

        # Validate current_duration
        current_duration = sim_params.get("current_duration", 0)
        if not isinstance(current_duration, (int, float)) or not (
            0 <= current_duration <= sim_time
        ):
            return False, f"Current duration must be between 0 and {sim_time} ms"

        # Validate that current injection doesn't exceed simulation time
        if current_start + current_duration > sim_time:
            return (
                False,
                f"Current injection (start + duration = {current_start + current_duration}ms) exceeds simulation time ({sim_time}ms)",
            )

        # Neuron model settings validation
        neuron_settings = config_data["neuron_model"]
        if not isinstance(neuron_settings, dict):
            return False, "Neuron model settings must be a dictionary"

        if "model_key" not in neuron_settings:
            return False, "Missing model_key in neuron model settings"

        # Validate LIF-specific simulation parameters if LIF model is selected
        model_key = neuron_settings["model_key"]
        if model_key == "lif":
            # Validate LIF threshold and reset simulation parameters
            if "lif_threshold" in sim_params:
                lif_threshold = sim_params.get("lif_threshold")
                if not isinstance(lif_threshold, (int, float)) or not (-80 <= lif_threshold <= -30):
                    return False, "LIF threshold must be between -80 and -30 mV"

            if "lif_reset" in sim_params:
                lif_reset = sim_params.get("lif_reset")
                if not isinstance(lif_reset, (int, float)) or not (-90 <= lif_reset <= -60):
                    return False, "LIF reset must be between -90 and -60 mV"

                # Validate threshold > reset relationship if both are present
                if "lif_threshold" in sim_params:
                    lif_threshold = sim_params.get("lif_threshold")
                    if lif_reset >= lif_threshold:
                        return (
                            False,
                            f"LIF reset ({lif_reset} mV) must be less than threshold ({lif_threshold} mV)",
                        )

        # Model-specific validation
        model_key = neuron_settings["model_key"]
        if model_key == "lif":
            is_valid, error_msg = self._validate_lif_parameters(neuron_settings)
            if not is_valid:
                return False, error_msg
        elif model_key == "izhikevich":
            is_valid, error_msg = self._validate_izhikevich_parameters(neuron_settings)
            if not is_valid:
                return False, error_msg
        elif model_key == "adex":
            is_valid, error_msg = self._validate_adex_parameters(neuron_settings)
            if not is_valid:
                return False, error_msg

        # Validate noise options
        if "noise" in config_data:
            is_valid, error_msg = self._validate_noise(config_data["noise"])
            if not is_valid:
                return False, f"Noise options error: {error_msg}"

        # Validate network options
        if "network" in config_data:
            is_valid, error_msg = self._validate_network(config_data["network"])
            if not is_valid:
                return False, f"Network options error: {error_msg}"

        # Validate advanced network features
        if "advanced_network" in config_data:
            is_valid, error_msg = self._validate_advanced_network(config_data["advanced_network"])
            if not is_valid:
                return False, f"Advanced network error: {error_msg}"

        return True, ""

    def _validate_lif_parameters(self, neuron_settings):
        """Validates LIF model parameters"""
        params = neuron_settings.get("parameters", {})

        # Validate membrane time constant (tau)
        if "tau_m" in params:
            tau = params["tau_m"]
            if not isinstance(tau, (int, float)) or tau <= 0:
                return False, "Membrane time constant (tau_m) must be a positive number"

        # Validate resting potential (v_rest)
        if "v_rest" in params:
            v_rest = params["v_rest"]
            if not isinstance(v_rest, (int, float)):
                return False, "Resting potential must be a number"

        # Validate resistance (R)
        if "resistance" in params:
            resistance = params["resistance"]
            if not isinstance(resistance, (int, float)) or resistance <= 0:
                return False, "Resistance must be a positive number"

        return True, ""

    def _validate_izhikevich_parameters(self, neuron_settings):
        """Validates Izhikevich model parameters"""
        params = neuron_settings.get("parameters", {})

        required_params = ["a", "b", "c", "d"]
        missing_params = [p for p in required_params if p not in params]
        if missing_params:
            return False, f"Missing required Izhikevich parameters: {', '.join(missing_params)}"

        try:
            a = float(params["a"])
            b = float(params["b"])
            c = float(params["c"])
            d = float(params["d"])

            if not (0.001 <= a <= 0.2):
                return False, "Parameter 'a' must be between 0.001 and 0.2 ms⁻¹"
            if not (0 <= b <= 0.3):
                return False, "Parameter 'b' must be between 0 and 0.3"
            if not (-75.0 <= c <= -40.0):
                return False, "Parameter 'c' must be between -75.0 and -40.0 mV"
            if not (0 <= d <= 10.0):
                return False, "Parameter 'd' must be between 0 and 10.0 mV/ms"
        except (TypeError, ValueError):
            return False, "All Izhikevich parameters must be numeric values"

        return True, ""

    def _validate_adex_parameters(self, neuron_settings):
        """Validates AdEx model parameters - ALL 8 parameters with correct field names"""
        params = neuron_settings.get("parameters", {})

        # All 8 AdEx parameters as exported by the actual system
        required_params = ["C", "gL", "EL", "VT", "delT", "a", "tauw", "b"]
        missing_params = [p for p in required_params if p not in params]
        if missing_params:
            return False, f"Missing required AdEx parameters: {', '.join(missing_params)}"

        try:
            C = float(params["C"])  # Membrane capacitance (pF)
            gL = float(params["gL"])  # Leak conductance (nS)
            EL = float(params["EL"])  # Leak reversal potential (mV)
            VT = float(params["VT"])  # Spike threshold (mV)
            delT = float(params["delT"])  # Slope factor (mV)
            a = float(params["a"])  # Subthreshold adaptation (nS)
            tauw = float(params["tauw"])  # Adaptation time constant (ms)
            b = float(params["b"])  # Spike-triggered adaptation (pA)

            # Validate parameter ranges based on neuron_models_config.py
            if not (50.0 <= C <= 500.0):
                return False, "Parameter 'C' (membrane capacitance) must be between 50 and 500 pF"
            if not (1.0 <= gL <= 30.0):
                return False, "Parameter 'gL' (leak conductance) must be between 1 and 30 nS"
            if not (-80.0 <= EL <= -50.0):
                return (
                    False,
                    "Parameter 'EL' (leak reversal potential) must be between -80 and -50 mV",
                )
            if not (-60.0 <= VT <= -40.0):
                return False, "Parameter 'VT' (spike threshold) must be between -60 and -40 mV"
            if not (0.1 <= delT <= 5.0):
                return False, "Parameter 'delT' (slope factor) must be between 0.1 and 5 mV"
            if not (0.0 <= a <= 10.0):
                return False, "Parameter 'a' (subthreshold adaptation) must be between 0 and 10 nS"
            if not (1.0 <= tauw <= 500.0):
                return (
                    False,
                    "Parameter 'tauw' (adaptation time constant) must be between 1 and 500 ms",
                )
            if not (0.0 <= b <= 500.0):
                return (
                    False,
                    "Parameter 'b' (spike-triggered adaptation) must be between 0 and 500 pA",
                )
        except (TypeError, ValueError):
            return False, "All AdEx parameters must be numeric values"

        return True, ""

    def _validate_noise(self, noise_config):
        """Validates noise configuration parameters"""
        if not isinstance(noise_config, dict):
            return False, "Noise config must be a dictionary"

        # Validate noise enabled flag
        if "enabled" in noise_config:
            if not isinstance(noise_config["enabled"], bool):
                return False, "Noise 'enabled' must be a boolean value"

        # Validate noise intensity (always validate if present)
        if "intensity" in noise_config:
            intensity = noise_config["intensity"]
            if not isinstance(intensity, (int, float)):
                return False, "Noise intensity must be a numeric value"
            if not (0.0 <= intensity <= 5.0):
                return False, "Noise intensity must be between 0.0 and 5.0 nA"

        # Validate noise method (always validate if present)
        if "method" in noise_config:
            method = noise_config["method"]
            valid_methods = ["Gaussian White Noise", "Ornstein-Uhlenbeck Process"]
            if method not in valid_methods:
                return False, f"Noise method must be one of: {', '.join(valid_methods)}"

        return True, ""

    def _validate_network(self, network_config):
        """Validates network configuration parameters"""
        if not isinstance(network_config, dict):
            return False, "Network config must be a dictionary"

        # Validate synaptic connections enabled flag
        if "enabled" in network_config:
            if not isinstance(network_config["enabled"], bool):
                return False, "Network 'enabled' must be a boolean value"

        # Validate synaptic weight (always validate if present)
        if "synaptic_weight" in network_config:
            weight = network_config["synaptic_weight"]
            if not isinstance(weight, (int, float)):
                return False, "Synaptic weight must be a numeric value"
            if not (0.0 <= weight <= 100.0):
                return False, "Synaptic weight must be between 0.0 and 100.0"

        # Validate network topology (always validate if present)
        if "network_topology" in network_config:
            topology = network_config["network_topology"]
            valid_topologies = ["random", "small_world", "scale_free", "regular", "modular", "coba_benchmark"]
            if topology not in valid_topologies:
                return False, f"Network topology must be one of: {', '.join(valid_topologies)}"

        # If network is enabled, validate topology-specific parameters
        if network_config.get("enabled", False):

            # Validate topology-specific parameters
            if "syn_prob" in network_config:
                prob = network_config["syn_prob"]
                if not isinstance(prob, (int, float)):
                    return False, "Connection probability must be a numeric value"
                if not (0.0 <= prob <= 1.0):
                    return False, "Connection probability must be between 0.0 and 1.0"

            if "topology_k" in network_config:
                neighbors = network_config["topology_k"]
                if not isinstance(neighbors, int):
                    return False, "Small-world nearest neighbors must be an integer"
                if not (2 <= neighbors <= 20):
                    return False, "Small-world nearest neighbors must be between 2 and 20"

            if "topology_p_rewire" in network_config:
                rewiring_prob = network_config["topology_p_rewire"]
                if not isinstance(rewiring_prob, (int, float)):
                    return False, "Small-world rewiring probability must be a numeric value"
                if not (0.0 <= rewiring_prob <= 1.0):
                    return False, "Small-world rewiring probability must be between 0.0 and 1.0"

            if "topology_m" in network_config:
                m = network_config["topology_m"]
                if not isinstance(m, int):
                    return False, "Scale-free m parameter must be an integer"
                if not (1 <= m <= 10):
                    return False, "Scale-free m parameter must be between 1 and 10"

            if "topology_k_reg" in network_config:
                k_reg = network_config["topology_k_reg"]
                if not isinstance(k_reg, int):
                    return False, "Regular lattice k parameter must be an integer"
                if not (2 <= k_reg <= 20):
                    return False, "Regular lattice k parameter must be between 2 and 20"

            if "topology_n_modules" in network_config:
                n_modules = network_config["topology_n_modules"]
                if not isinstance(n_modules, int):
                    return False, "Number of modules must be an integer"
                if not (2 <= n_modules <= 10):
                    return False, "Number of modules must be between 2 and 10"

            if "topology_p_intra" in network_config:
                p_intra = network_config["topology_p_intra"]
                if not isinstance(p_intra, (int, float)):
                    return False, "Intra-module probability must be a numeric value"
                if not (0.0 <= p_intra <= 1.0):
                    return False, "Intra-module probability must be between 0.0 and 1.0"

            if "topology_p_inter" in network_config:
                p_inter = network_config["topology_p_inter"]
                if not isinstance(p_inter, (int, float)):
                    return False, "Inter-module probability must be a numeric value"
                if not (0.0 <= p_inter <= 1.0):
                    return False, "Inter-module probability must be between 0.0 and 1.0"

        return True, ""

    def _validate_advanced_network(self, advanced_config):
        """Validates advanced network feature parameters"""
        if not isinstance(advanced_config, dict):
            return False, "Advanced network options must be a dictionary"

        # Validate Dale's Principle - ALL 5 parameters (always validate if present)
        if "dales_principle" in advanced_config:
            dales = advanced_config["dales_principle"]
            if not isinstance(dales, dict):
                return False, "Dale's principle must be a dictionary"

            if "enabled" in dales and not isinstance(dales["enabled"], bool):
                return False, "Dale's principle 'enabled' must be a boolean"

            # Always validate Dale's principle parameters if present
            if "excitatory_ratio" in dales:
                ratio = dales["excitatory_ratio"]
                if not isinstance(ratio, (int, float)) or not (0.1 <= ratio <= 0.9):
                    return False, "Excitatory ratio must be between 0.1 and 0.9"

            if "exc_weight" in dales:
                exc_weight = dales["exc_weight"]
                if not isinstance(exc_weight, (int, float)) or not (0.01 <= exc_weight <= 10.0):
                    return False, "Excitatory weight must be between 0.01 and 10.0 nS"

            if "inh_weight" in dales:
                inh_weight = dales["inh_weight"]
                if not isinstance(inh_weight, (int, float)) or not (-20.0 <= inh_weight <= -0.1):
                    return False, "Inhibitory weight must be between -20.0 and -0.1 nS"

            if "exc_reversal" in dales:
                exc_reversal = dales["exc_reversal"]
                if not isinstance(exc_reversal, (int, float)) or not (
                    -20.0 <= exc_reversal <= 20.0
                ):
                    return False, "Excitatory reversal potential must be between -20 and 20 mV"

            if "inh_reversal" in dales:
                inh_reversal = dales["inh_reversal"]
                if not isinstance(inh_reversal, (int, float)) or not (
                    -100.0 <= inh_reversal <= -50.0
                ):
                    return False, "Inhibitory reversal potential must be between -100 and -50 mV"

        # Validate Synaptic Delays - ALL 4 delay types + ALL parameters (always validate if present)
        if "synaptic_delays" in advanced_config:
            delays = advanced_config["synaptic_delays"]
            if not isinstance(delays, dict):
                return False, "Synaptic delays must be a dictionary"

            if "enabled" in delays and not isinstance(delays["enabled"], bool):
                return False, "Synaptic delays 'enabled' must be a boolean"

            # Always validate delay parameters if present
            if "delay_type" in delays:
                delay_type = delays["delay_type"]
                valid_types = ["uniform", "normal", "exponential", "distance_dependent"]
                if delay_type not in valid_types:
                    return False, f"Delay type must be one of: {', '.join(valid_types)}"

            if "min_delay" in delays:
                min_delay = delays["min_delay"]
                if not isinstance(min_delay, (int, float)) or not (0.1 <= min_delay <= 10.0):
                    return False, "Minimum delay must be between 0.1 and 10.0 ms"

            if "max_delay" in delays:
                max_delay = delays["max_delay"]
                if not isinstance(max_delay, (int, float)) or not (0.5 <= max_delay <= 50.0):
                    return False, "Maximum delay must be between 0.5 and 50.0 ms"

            if "mean_delay" in delays:
                mean_delay = delays["mean_delay"]
                if not isinstance(mean_delay, (int, float)) or not (0.1 <= mean_delay <= 20.0):
                    return False, "Mean delay must be between 0.1 and 20.0 ms"

            if "delay_std" in delays:
                delay_std = delays["delay_std"]
                if not isinstance(delay_std, (int, float)) or not (0.1 <= delay_std <= 5.0):
                    return False, "Delay standard deviation must be between 0.1 and 5.0 ms"

            if "conduction_velocity" in delays:
                velocity = delays["conduction_velocity"]
                if not isinstance(velocity, (int, float)) or velocity <= 0:
                    return False, "Conduction velocity must be a positive number"

        # Validate STDP - ALL 8 parameters (always validate if present)
        if "stdp" in advanced_config:
            stdp = advanced_config["stdp"]
            if not isinstance(stdp, dict):
                return False, "STDP must be a dictionary"

            if "enabled" in stdp and not isinstance(stdp["enabled"], bool):
                return False, "STDP 'enabled' must be a boolean"

            # Always validate STDP parameters if present
            if "stdp_type" in stdp:
                stdp_type = stdp["stdp_type"]
                valid_types = ["additive", "multiplicative", "nearest_spike", "all_to_all"]
                if stdp_type not in valid_types:
                    return False, f"STDP type must be one of: {', '.join(valid_types)}"

            # Validate all STDP parameters from advanced_network_config.py
            if "tau_pre" in stdp:
                tau_pre = stdp["tau_pre"]
                if not isinstance(tau_pre, (int, float)) or not (1.0 <= tau_pre <= 100.0):
                    return False, "STDP tau_pre must be between 1.0 and 100.0 ms"

            if "tau_post" in stdp:
                tau_post = stdp["tau_post"]
                if not isinstance(tau_post, (int, float)) or not (1.0 <= tau_post <= 100.0):
                    return False, "STDP tau_post must be between 1.0 and 100.0 ms"

            if "A_plus" in stdp:
                A_plus = stdp["A_plus"]
                if not isinstance(A_plus, (int, float)) or not (0.001 <= A_plus <= 0.1):
                    return False, "STDP A_plus must be between 0.001 and 0.1"

            if "A_minus" in stdp:
                A_minus = stdp["A_minus"]
                if not isinstance(A_minus, (int, float)) or not (0.001 <= A_minus <= 0.1):
                    return False, "STDP A_minus must be between 0.001 and 0.1"

            if "w_min" in stdp:
                w_min = stdp["w_min"]
                if not isinstance(w_min, (int, float)) or not (-10.0 <= w_min <= 0.0):
                    return False, "STDP w_min must be between -10.0 and 0.0"

            if "w_max" in stdp:
                w_max = stdp["w_max"]
                if not isinstance(w_max, (int, float)) or not (1.0 <= w_max <= 20.0):
                    return False, "STDP w_max must be between 1.0 and 20.0"

        # Validate Distance-Dependent Connectivity - ALL 8 parameters (always validate if present)
        if "distance_connectivity" in advanced_config:
            distance = advanced_config["distance_connectivity"]
            if not isinstance(distance, dict):
                return False, "Distance connectivity must be a dictionary"

            if "enabled" in distance and not isinstance(distance["enabled"], bool):
                return False, "Distance connectivity 'enabled' must be a boolean"

            # Always validate distance connectivity parameters if present
            if "spatial_layout" in distance:
                layout = distance["spatial_layout"]
                valid_layouts = ["1d_line", "2d_grid", "2d_random", "3d_cube", "3d_random"]
                if layout not in valid_layouts:
                    return False, f"Spatial layout must be one of: {', '.join(valid_layouts)}"

            if "space_scale" in distance:
                scale = distance["space_scale"]
                if not isinstance(scale, (int, float)) or not (10.0 <= scale <= 10000.0):
                    return False, "Space scale must be between 10.0 and 10000.0 μm"

            if "connection_function" in distance:
                func = distance["connection_function"]
                valid_functions = ["exponential", "gaussian", "power_law", "step", "linear"]
                if func not in valid_functions:
                    return (
                        False,
                        f"Connection function must be one of: {', '.join(valid_functions)}",
                    )

            if "connection_length" in distance:
                length = distance["connection_length"]
                if not isinstance(length, (int, float)) or not (1.0 <= length <= 1000.0):
                    return False, "Connection length must be between 1.0 and 1000.0 μm"

            if "max_distance" in distance:
                max_dist = distance["max_distance"]
                if not isinstance(max_dist, (int, float)) or not (10.0 <= max_dist <= 5000.0):
                    return False, "Maximum distance must be between 10.0 and 5000.0 μm"

            if "base_probability" in distance:
                base_prob = distance["base_probability"]
                if not isinstance(base_prob, (int, float)) or not (0.001 <= base_prob <= 1.0):
                    return False, "Base probability must be between 0.001 and 1.0"

            if "power_exponent" in distance:
                exponent = distance["power_exponent"]
                if not isinstance(exponent, (int, float)) or not (0.5 <= exponent <= 5.0):
                    return False, "Power exponent must be between 0.5 and 5.0"

        return True, ""
