"""
Synapse Builder for Brian2 simulations.
Handles network topology, synapse construction, gap junctions, and plasticity.
"""

try:
    import brian2 as b2
    import numpy as np

    BRIAN2_AVAILABLE = True
except ImportError:
    BRIAN2_AVAILABLE = False
    import numpy as np


class SynapseBuilder:
    """Builder class for constructing synapses and network connections."""

    def __init__(self):
        self.synapses = None
        self.gap_junctions = None

    def build_network(
        self,
        network_params,
        advanced_params,
        synaptic_receptors_params,
        short_term_plasticity_params,
        neurons,
    ):
        """Build synaptic connections between neurons."""
        if not network_params.get("enabled", False):
            return None

        # Check if advanced features are needed
        use_receptors = synaptic_receptors_params and synaptic_receptors_params.get(
            "enabled", False
        )
        use_stp = short_term_plasticity_params and short_term_plasticity_params.get(
            "enabled", False
        )

        if use_receptors or use_stp:
            self.synapses = self._build_advanced_synapses(
                network_params,
                advanced_params,
                synaptic_receptors_params,
                short_term_plasticity_params,
                neurons,
            )
        else:
            self.synapses = self._build_simple_synapses(network_params, advanced_params, neurons)

        return self.synapses

    def _build_simple_synapses(self, network_params, advanced_params, neurons):
        """Build simple synapses."""
        weight = network_params.get("weight", 0.5) * b2.nS

        synapses = b2.Synapses(neurons, neurons, "w : siemens", on_pre="v_post += w / nS * mV")

        topology = network_params.get("topology", "all_to_all")
        topology_params = network_params.get("topology_params", {})
        self._connect_by_topology(synapses, topology, topology_params, neurons)

        synapses.w = weight

        if advanced_params:
            self._apply_advanced_network_features(synapses, advanced_params, neurons)

        return synapses

    def _connect_by_topology(self, synapses, topology, topology_params, neurons):
        """Connect synapses based on network topology."""
        n = len(neurons)

        if topology == "all_to_all":
            allow_self = topology_params.get("allow_self_connections", False)
            if allow_self:
                synapses.connect()
            else:
                synapses.connect(condition="i != j")

        elif topology == "random":
            prob = topology_params.get("connection_probability", 0.1)
            synapses.connect(p=prob)

        elif topology == "one_to_one":
            synapses.connect(j="i")

        elif topology == "small_world":
            k = topology_params.get("nearest_neighbors", 4)
            p_rewire = topology_params.get("rewiring_probability", 0.1)

            # Create small-world network
            sources = []
            targets = []

            for i in range(n):
                for j in range(1, k // 2 + 1):
                    target = (i + j) % n
                    if np.random.random() < p_rewire:
                        target = np.random.randint(n)
                    sources.append(i)
                    targets.append(target)

                    target = (i - j) % n
                    if np.random.random() < p_rewire:
                        target = np.random.randint(n)
                    sources.append(i)
                    targets.append(target)

            synapses.connect(i=sources, j=targets)

        elif topology == "scale_free":
            m = topology_params.get("new_connections", 2)
            sources, targets = self._generate_scale_free(n, m)
            synapses.connect(i=sources, j=targets)

        elif topology == "regular":
            degree = topology_params.get("degree", 4)
            sources = []
            targets = []
            for i in range(n):
                for j in range(1, degree // 2 + 1):
                    sources.extend([i, i])
                    targets.extend([(i + j) % n, (i - j) % n])
            synapses.connect(i=sources, j=targets)

        elif topology == "modular":
            num_modules = topology_params.get("num_modules", 4)
            p_within = topology_params.get("p_within", 0.8)
            p_between = topology_params.get("p_between", 0.1)

            module_size = n // num_modules
            for i in range(n):
                module_i = i // module_size
                for j in range(n):
                    if i == j:
                        continue
                    module_j = j // module_size
                    p = p_within if module_i == module_j else p_between
                    if np.random.random() < p:
                        synapses.connect(i=i, j=j)

    def _generate_scale_free(self, n, m):
        """Generate scale-free network using preferential attachment."""
        sources = []
        targets = []
        degrees = [m] * m  # Initial clique

        # Initial connections (clique)
        for i in range(m):
            for j in range(i + 1, m):
                sources.extend([i, j])
                targets.extend([j, i])

        # Preferential attachment for remaining nodes
        for new_node in range(m, n):
            total_degree = sum(degrees)
            probs = [d / total_degree for d in degrees]

            chosen = np.random.choice(
                len(degrees), size=min(m, len(degrees)), replace=False, p=probs
            )

            for target in chosen:
                sources.extend([new_node, target])
                targets.extend([target, new_node])
                degrees[target] += 1

            degrees.append(m)

        return sources, targets

    def _build_advanced_synapses(
        self,
        network_params,
        advanced_params,
        synaptic_receptors_params,
        short_term_plasticity_params,
        neurons,
    ):
        """Build synapses with multiple receptors and/or short-term plasticity."""
        receptor_params = self._get_receptor_params(synaptic_receptors_params)
        stp_enabled = short_term_plasticity_params and short_term_plasticity_params.get(
            "enabled", False
        )

        # Build model equations
        model, on_pre, namespace = self._build_receptor_model(
            receptor_params, synaptic_receptors_params
        )

        # Add STP if enabled
        if stp_enabled:
            stp_model, stp_on_pre = self._get_stp_model(short_term_plasticity_params)
            model += stp_model
            on_pre = stp_on_pre + on_pre

        synapses = b2.Synapses(neurons, neurons, model=model, on_pre=on_pre, namespace=namespace)

        topology = network_params.get("topology", "all_to_all")
        topology_params = network_params.get("topology_params", {})
        self._connect_by_topology(synapses, topology, topology_params, neurons)

        self._initialize_weights(synapses, network_params, synaptic_receptors_params, stp_enabled)

        if advanced_params:
            self._apply_advanced_network_features(synapses, advanced_params, neurons)

        return synapses

    def _get_receptor_params(self, synaptic_receptors_params):
        """Extract receptor parameters."""
        receptors = {}
        for receptor in ["AMPA", "NMDA", "GABA_A", "GABA_B"]:
            if synaptic_receptors_params.get(f"{receptor}_enabled", False):
                receptors[receptor] = {
                    "g": synaptic_receptors_params.get(f"{receptor}_g", 1.0),
                    "tau": synaptic_receptors_params.get(f"{receptor}_tau", 5.0),
                    "E": synaptic_receptors_params.get(f"{receptor}_E", 0.0),
                }
        return receptors

    def _build_receptor_model(self, receptor_params, synaptic_receptors_params):
        """Build receptor equations, on_pre, and namespace."""
        model = "w : siemens\n"
        on_pre = ""
        namespace = {}

        for receptor, params in receptor_params.items():
            model += f"""
            d{receptor}/dt = -{receptor}/tau_{receptor} : siemens (event-driven)
            """
            on_pre += f"{receptor} += w * g_{receptor}; "
            namespace[f"tau_{receptor}"] = params["tau"] * b2.ms
            namespace[f"g_{receptor}"] = params["g"]
            namespace[f"E_{receptor}"] = params["E"] * b2.mV

        if not receptor_params:
            model = "w : siemens"
            on_pre = "v_post += w / nS * mV"

        return model, on_pre, namespace

    def _get_stp_model(self, stp_params):
        """Get short-term plasticity equations."""
        stp_type = stp_params.get("type", "depression")
        stp_params.get("tau_d", 200.0)
        stp_params.get("tau_f", 50.0)
        stp_params.get("U", 0.2)

        if stp_type == "depression":
            model = f"""
            dx/dt = (1 - x) / tau_d : 1 (event-driven)
            """
            on_pre = "x *= (1 - U); "

        elif stp_type == "facilitation":
            model = f"""
            du/dt = (U0 - u) / tau_f : 1 (event-driven)
            """
            on_pre = "u += U0 * (1 - u); "

        else:  # combined
            model = f"""
            dx/dt = (1 - x) / tau_d : 1 (event-driven)
            du/dt = (U0 - u) / tau_f : 1 (event-driven)
            """
            on_pre = "u += U0 * (1 - u); x *= (1 - u); "

        return model, on_pre

    def _initialize_weights(self, synapses, network_params, synaptic_receptors_params, stp_enabled):
        """Initialize synaptic weights."""
        base_weight = network_params.get("weight", 0.5) * b2.nS
        synapses.w = base_weight

        if stp_enabled:
            if hasattr(synapses, "x"):
                synapses.x = 1.0
            if hasattr(synapses, "u"):
                synapses.u = 0.2

    def _apply_advanced_network_features(self, synapses, advanced_params, neurons):
        """Apply advanced network features."""
        # Dale's principle
        if advanced_params.get("dales_principle", False):
            exc_fraction = advanced_params.get("exc_fraction", 0.8)
            n = len(neurons)
            int(n * exc_fraction)

            exc_weight = advanced_params.get("exc_weight", 1.0) * b2.nS
            inh_weight = advanced_params.get("inh_weight", -4.0) * b2.nS

            synapses.w["i < n_exc"] = exc_weight
            synapses.w["i >= n_exc"] = inh_weight

        # Synaptic delays
        if advanced_params.get("delays_enabled", False):
            advanced_params.get("min_delay", 0.5) * b2.ms
            advanced_params.get("max_delay", 5.0) * b2.ms
            synapses.delay = "min_delay + rand() * (max_delay - min_delay)"

        # STDP
        if advanced_params.get("stdp_enabled", False):
            self._setup_stdp(synapses, advanced_params)

    def _setup_stdp(self, synapses, advanced_params):
        """Setup STDP plasticity."""
        advanced_params.get("tau_pre", 20.0) * b2.ms
        advanced_params.get("tau_post", 20.0) * b2.ms
        advanced_params.get("A_pre", 0.01)
        advanced_params.get("A_post", -0.01)
        w_max = advanced_params.get("w_max", 10.0) * b2.nS

        # Note: Full STDP requires modifying synapse model during creation
        # This is a simplified post-hoc setup
        synapses.run_regularly(
            f"""
            w = clip(w, 0*nS, {w_max})
            """,
            dt=10 * b2.ms,
        )

    def build_gap_junctions(self, gap_params, neurons):
        """Build gap junctions (electrical synapses) between neurons."""
        if not gap_params or not gap_params.get("enabled", False):
            return None

        model = self._get_gap_junction_equations(gap_params)

        gap_junctions = b2.Synapses(neurons, neurons, model=model, method="euler")

        self._connect_gap_junctions(gap_junctions, gap_params, neurons)
        self._set_gap_junction_properties(gap_junctions, gap_params)

        self.gap_junctions = gap_junctions
        return gap_junctions

    def _get_gap_junction_equations(self, gap_params):
        """Get gap junction equations based on configuration."""
        gj_type = gap_params.get("type", "linear")

        if gj_type == "linear":
            return """
            g_gap : siemens
            I_gap_post = g_gap * (v_pre - v_post) : amp (summed)
            """

        elif gj_type == "rectifying":
            return """
            g_gap : siemens
            g_effective = g_gap * int(v_pre > v_post) : siemens
            I_gap_post = g_effective * (v_pre - v_post) : amp (summed)
            """

        elif gj_type == "voltage_dependent":
            Vhalf = gap_params.get("Vhalf", -40.0)
            k = gap_params.get("k", 10.0)
            return f"""
            g_gap : siemens
            g_open = 1 / (1 + exp(-(v_pre - v_post - {Vhalf}*mV) / ({k}*mV))) : 1
            g_effective = g_gap * g_open : siemens
            I_gap_post = g_effective * (v_pre - v_post) : amp (summed)
            """

        elif gj_type == "calcium_dependent":
            Ca_half = gap_params.get("Ca_half", 500e-9)
            n_hill = gap_params.get("n_hill", 2)
            return f"""
            g_gap : siemens
            g_modulated = g_gap / (1 + (Ca_post / ({Ca_half}*molar))**{n_hill}) : siemens
            I_gap_post = g_modulated * (v_pre - v_post) : amp (summed)
            """

        elif gj_type == "subcellular":
            return """
            g_gap : siemens
            compartment_pre : integer (constant)
            compartment_post : integer (constant)
            I_gap_post = g_gap * (v_pre - v_post) : amp (summed)
            """

        else:
            return """
            g_gap : siemens
            I_gap_post = g_gap * (v_pre - v_post) : amp (summed)
            """

    def _connect_gap_junctions(self, gap_junctions, gap_params, neurons):
        """Connect gap junctions based on spatial organization."""
        pattern = gap_params.get("connection_pattern", "random")
        n = len(neurons)

        if pattern == "random":
            probability = gap_params.get("probability", 0.05)
            gap_junctions.connect(condition="i < j", p=probability)
            # Bidirectional
            gap_junctions.connect(condition="i > j", p=probability)

        elif pattern == "nearest_neighbor":
            k = gap_params.get("num_neighbors", 2)
            for i in range(n):
                for j in range(1, k + 1):
                    if i + j < n:
                        gap_junctions.connect(i=i, j=i + j)
                        gap_junctions.connect(i=i + j, j=i)

        elif pattern == "distance_dependent":
            sigma = gap_params.get("sigma", 50.0)  # um
            max_dist = gap_params.get("max_distance", 100.0)  # um

            # Generate positions
            positions = np.random.uniform(0, max_dist * 3, (n, 3))

            for i in range(n):
                for j in range(i + 1, n):
                    dist = np.sqrt(np.sum((positions[i] - positions[j]) ** 2))
                    prob = np.exp(-(dist**2) / (2 * sigma**2))
                    if np.random.random() < prob:
                        gap_junctions.connect(i=i, j=j)
                        gap_junctions.connect(i=j, j=i)

        elif pattern == "interneuron_specific":
            interneuron_fraction = gap_params.get("interneuron_fraction", 0.2)
            n_inter = int(n * interneuron_fraction)
            p_inter = gap_params.get("p_interneuron", 0.3)

            # Connect interneurons with higher probability
            for i in range(n_inter):
                for j in range(i + 1, n_inter):
                    if np.random.random() < p_inter:
                        gap_junctions.connect(i=i, j=j)
                        gap_junctions.connect(i=j, j=i)

        elif pattern == "layer_specific":
            num_layers = gap_params.get("num_layers", 3)
            p_within = gap_params.get("p_within_layer", 0.1)
            p_between = gap_params.get("p_between_layer", 0.01)

            layer_size = n // num_layers
            for i in range(n):
                layer_i = i // layer_size
                for j in range(i + 1, n):
                    layer_j = j // layer_size
                    p = p_within if layer_i == layer_j else p_between
                    if np.random.random() < p:
                        gap_junctions.connect(i=i, j=j)
                        gap_junctions.connect(i=j, j=i)

        else:  # 'all'
            gap_junctions.connect(condition="i != j")

    def _set_gap_junction_properties(self, gap_junctions, gap_params):
        """Set gap junction properties and parameters."""
        conductance = gap_params.get("conductance", 0.5) * b2.nS
        variability = gap_params.get("variability", 0.1)

        # Set base conductance with variability
        if variability > 0:
            gap_junctions.g_gap = f"{conductance} * (1 + {variability} * randn())"
        else:
            gap_junctions.g_gap = conductance

        # Clip to valid range
        g_min = gap_params.get("g_min", 0.01) * b2.nS
        g_max = gap_params.get("g_max", 2.0) * b2.nS
        gap_junctions.g_gap = f"clip(g_gap, {g_min}, {g_max})"

        # Subcellular localization
        if gap_params.get("type") == "subcellular":
            compartment_dist = gap_params.get("compartment_distribution", "dendrite")
            if compartment_dist == "dendrite":
                gap_junctions.compartment_pre = "randint(1, 5)"
                gap_junctions.compartment_post = "randint(1, 5)"
            elif compartment_dist == "soma":
                gap_junctions.compartment_pre = 0
                gap_junctions.compartment_post = 0
            elif compartment_dist == "axon":
                gap_junctions.compartment_pre = "randint(5, 10)"
                gap_junctions.compartment_post = "randint(5, 10)"
