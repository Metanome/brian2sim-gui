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
        calcium_dynamics_params=None,
        neurons=None,
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
        # Check for STDP in advanced params
        stdp_params = advanced_params.get("stdp", {}) if advanced_params else {}
        use_stdp = stdp_params.get("enabled", False)

        if use_receptors or use_stp or use_stdp:
            self.synapses = self._build_advanced_synapses(
                network_params,
                advanced_params,
                synaptic_receptors_params,
                short_term_plasticity_params,
                calcium_dynamics_params,
                neurons,
            )
        else:
            self.synapses = self._build_simple_synapses(network_params, advanced_params, neurons)

        # Apply Calcium Plasticity if enabled (works for both simple and advanced)
        if calcium_dynamics_params and calcium_dynamics_params.get("enabled", False):
             self._setup_calcium_plasticity(self.synapses, calcium_dynamics_params)

        return self.synapses

    def _build_simple_synapses(self, network_params, advanced_params, neurons):
        """Build simple synapses."""
        # Support both old key names and new config key names
        weight = network_params.get("synaptic_weight", network_params.get("weight", 0.5)) * b2.nS
        topology_type = network_params.get("network_topology", "random")

        if topology_type == "coba_benchmark":
            # Special logic for Vogels & Abbott Benchmark
            # E (0-3200) -> ge (+6nS), I (3200-4000) -> gi (+67nS)
            # Connectivity p=0.02
            
            # Using int(i<3200) to select Excitatory impact vs Inhibitory
            # This implementation assumes standard 4000 neuron scaling
            # For robustness, we could use N*0.8
            
            model = "w : siemens"
            on_pre = """
            ge_post += 6*nS * int(i < 3200)
            gi_post += 67*nS * int(i >= 3200)
            """
            
            synapses = b2.Synapses(neurons, neurons, model=model, on_pre=on_pre)
            
            # Use probability from params or fallback to 0.02 (2%)
            prob = network_params.get("syn_prob", 0.02)
            synapses.connect(p=prob)
            return synapses

        # Determine if we need to support Reversal Potentials (Conductance Logic)
        use_reversals = advanced_params and ("exc_reversal" in advanced_params or "inh_reversal" in advanced_params)
        
        if use_reversals:
            # Conductance-based model with per-synapse reversal potential
            # v_post change is scaled by normalized driving force
            v_norm = advanced_params.get("driving_force_norm", 70.0) * b2.mV
            
            model = """
            w : siemens
            E_rev : volt
            v_norm : volt # Normalization constant for driving force
            """
            on_pre = "v_post += (w/nS) * ((E_rev - v_post) / v_norm) * mV"
            synapses = b2.Synapses(neurons, neurons, model=model, on_pre=on_pre)
            synapses.v_norm = v_norm
            
            # Default initialization
            synapses.E_rev = 0 * b2.mV # Default to Excitatory if not specified
        else:
            # Standard Current-based Kick
            synapses = b2.Synapses(neurons, neurons, "w : siemens", on_pre="v_post += w / nS * mV")
        
        # Support both old and new key names for topology
        topology = network_params.get("network_topology", network_params.get("topology", "random"))
        
        # Build topology_params from network_config flat structure
        topology_params = self._extract_topology_params(network_params, advanced_params)
        self._connect_by_topology(synapses, topology, topology_params, neurons)
        
        # Set weights AFTER connect() - Brian2 requirement
        if len(synapses) > 0:
            synapses.w = weight

        if advanced_params:
            self._apply_advanced_network_features(synapses, advanced_params, neurons)

        return synapses

    def _extract_topology_params(self, network_params, advanced_params=None):
        """Extract topology parameters from flat network_config structure."""
        return {
            # Random topology
            "connection_probability": network_params.get("syn_prob", network_params.get("connection_probability", 0.1)),
            "allow_self_connections": network_params.get("allow_self_connections", False),
            # Small-world topology
            "nearest_neighbors": network_params.get("topology_k", network_params.get("nearest_neighbors", 4)),
            "rewiring_probability": network_params.get("topology_p_rewire", network_params.get("rewiring_probability", 0.1)),
            # Scale-free topology
            "new_connections": network_params.get("topology_m", network_params.get("new_connections", 3)),
            # Regular topology
            "k": network_params.get("topology_k_reg", network_params.get("k", 4)),
            # Modular topology
            "num_modules": network_params.get("topology_n_modules", network_params.get("num_modules", 4)),
            "p_within": network_params.get("topology_p_intra", network_params.get("p_within", 0.15)),
            "p_between": network_params.get("topology_p_inter", network_params.get("p_between", 0.01)),
            # Distance-dependent topology (from advanced params usually)
            "space_scale": advanced_params.get("space_scale", 200.0) * b2.um if advanced_params else 200.0 * b2.um,
            "base_probability": advanced_params.get("base_probability", 1.0) if advanced_params else 1.0,
        }

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
            
        elif topology == "distance_dependent":
             if hasattr(neurons, "x") and hasattr(neurons, "y"):
                 # Distance-based probability
                 # p = C * exp(-distance / scale)
                 # p = C * exp(-distance / scale)
                 
                 # Add constants to namespace for evaluation
                 synapses.namespace["space_scale"] = topology_params["space_scale"]
                 synapses.namespace["base_prob"] = topology_params["base_probability"]
                 
                 # 2D Euclidean distance
                 dist_expr = "sqrt((x_pre - x_post)**2 + (y_pre - y_post)**2)"
                 prob_expr = "base_prob * exp(-" + dist_expr + " / space_scale)"
                 
                 synapses.connect(p=prob_expr)
             else:
                 # Fallback to random if no positions
                 print("Warning: Distance-dependent topology requested but neurons lack spatial coordinates.")
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
        calcium_dynamics_params,
        neurons,
    ):
        """Build synapses with multiple receptors and/or short-term plasticity."""
        receptor_params = self._get_receptor_params(synaptic_receptors_params)
        stp_enabled = short_term_plasticity_params and short_term_plasticity_params.get(
            "enabled", False
        )
        # Check for STDP
        stdp_params = advanced_params.get("stdp", {}) if advanced_params else {}
        stdp_enabled = stdp_params.get("enabled", False)

        # Build model equations
        model, on_pre, on_post_receptor, namespace = self._build_receptor_model(
            receptor_params, synaptic_receptors_params
        )

        # Add STP if enabled
        if stp_enabled:
            stp_model, stp_on_pre, stp_namespace = self._get_stp_model(short_term_plasticity_params)
            model += stp_model
            on_pre = stp_on_pre + on_pre
            namespace.update(stp_namespace)

        # Add STDP if enabled
        on_post = ""
        if stdp_enabled:
            stdp_model, stdp_on_pre, stdp_on_post, stdp_namespace = self._get_stdp_model(stdp_params)
            model += stdp_model
            on_pre = stdp_on_pre + on_pre
            on_post = stdp_on_post
            namespace.update(stdp_namespace)
            
        # Add receptor on_post (rare, but for custom models)
        if on_post_receptor:
            on_post += on_post_receptor
            
        # Add NMDA Calcium summation if needed
        # We need to detect if neurons have I_nmda_total
        if hasattr(neurons, "I_nmda_total") and "I_nmda" in model:
             model += "\nI_nmda_total_post = I_nmda : amp (summed)"

        synapses = b2.Synapses(neurons, neurons, model=model, on_pre=on_pre, on_post=on_post, namespace=namespace)

        # Support both old and new key names for topology
        topology = network_params.get("network_topology", network_params.get("topology", "random"))
        topology_params = self._extract_topology_params(network_params, advanced_params)
        self._connect_by_topology(synapses, topology, topology_params, neurons)


        self._initialize_weights(synapses, network_params, synaptic_receptors_params, stp_enabled)

        if advanced_params:
            self._apply_advanced_network_features(synapses, advanced_params, neurons)

        return synapses

    def _get_receptor_params(self, synaptic_receptors_params):
        """Extract receptor parameters from config."""
        if not synaptic_receptors_params or not synaptic_receptors_params.get("enabled", False):
            return {}
            
        receptors = {}
        
        # AMPA - fast excitatory (single exponential)
        if synaptic_receptors_params.get("ampa_enabled", False):
            receptors["ampa"] = {
                "tau_decay": synaptic_receptors_params.get("ampa_tau_decay", 2.0),
                "E_rev": synaptic_receptors_params.get("ampa_reversal", 0.0),
                "weight_ratio": synaptic_receptors_params.get("ampa_weight_ratio", 1.0),
            }
        
        # NMDA - slow excitatory with Mg2+ block (dual exponential)
        if synaptic_receptors_params.get("nmda_enabled", False):
            receptors["nmda"] = {
                "tau_rise": synaptic_receptors_params.get("nmda_tau_rise", 2.0),
                "tau_decay": synaptic_receptors_params.get("nmda_tau_decay", 100.0),
                "E_rev": synaptic_receptors_params.get("nmda_reversal", 0.0),
                "mg_conc": synaptic_receptors_params.get("nmda_mg_concentration", 1.0),
                "weight_ratio": synaptic_receptors_params.get("nmda_weight_ratio", 0.5),
            }
        
        # GABA_A - fast inhibitory (single exponential)
        if synaptic_receptors_params.get("gaba_a_enabled", False):
            receptors["gaba_a"] = {
                "tau_rise": synaptic_receptors_params.get("gaba_a_tau_rise", 0.5),
                "tau_decay": synaptic_receptors_params.get("gaba_a_tau_decay", 6.0),
                "E_rev": synaptic_receptors_params.get("gaba_a_reversal", -70.0),
                "weight_ratio": synaptic_receptors_params.get("gaba_a_weight_ratio", 1.5),
            }
        
        # GABA_B - slow inhibitory via K+ channels (dual exponential)
        if synaptic_receptors_params.get("gaba_b_enabled", False):
            receptors["gaba_b"] = {
                "tau_rise": synaptic_receptors_params.get("gaba_b_tau_rise", 50.0),
                "tau_decay": synaptic_receptors_params.get("gaba_b_tau_decay", 200.0),
                "E_rev": synaptic_receptors_params.get("gaba_b_reversal", -90.0),
                "weight_ratio": synaptic_receptors_params.get("gaba_b_weight_ratio", 0.5),
            }
        
        return receptors

    def _build_receptor_model(self, receptor_params, synaptic_receptors_params):
        """Build scientifically accurate receptor equations with conductance-based currents.
        
        Implements:
        - AMPA: Fast excitatory with single exponential decay
        - NMDA: Slow excitatory with dual exponential kinetics and Mg2+ voltage-dependent block
        - GABA_A: Fast inhibitory with alpha-function kinetics
        - GABA_B: Slow inhibitory (K+ channel mediated) with dual exponential
        
        The synaptic current is computed as: I = g * (E_rev - v_post)
        This is summed into the postsynaptic neuron's I variable.
        """
        if synaptic_receptors_params.get("custom_synapse_enabled", False):
            # Use custom user-defined model
            model = synaptic_receptors_params.get("custom_synapse_eqs", "w : siemens")
            on_pre = synaptic_receptors_params.get("custom_on_pre", "g += w")
            on_post = synaptic_receptors_params.get("custom_on_post", "")
            return model, on_pre, on_post, {}

        model_parts = ["w : siemens  # Base synaptic weight"]
        on_pre_parts = []
        namespace = {}
        on_post = ""
        
        # --- AMPA: Single exponential conductance ---
        if "ampa" in receptor_params:
            p = receptor_params["ampa"]
            model_parts.append("""
            dg_ampa/dt = -g_ampa / tau_ampa : siemens
            I_ampa = g_ampa * (E_ampa - v_post) : amp
            """)
            on_pre_parts.append("g_ampa += w * w_ampa")
            namespace["tau_ampa"] = p["tau_decay"] * b2.ms
            namespace["E_ampa"] = p["E_rev"] * b2.mV
            namespace["w_ampa"] = p["weight_ratio"]
        
        # --- NMDA: Dual exponential with Mg2+ block ---
        if "nmda" in receptor_params:
            p = receptor_params["nmda"]
            # Using the Jahr & Stevens (1990) Mg2+ block formulation
            # B(V) = 1 / (1 + [Mg2+]/3.57 * exp(-0.062 * V))
            model_parts.append("""
            dg_nmda/dt = (s_nmda - g_nmda) / tau_nmda_decay : siemens
            ds_nmda/dt = -s_nmda / tau_nmda_rise : siemens
            B_mg = 1.0 / (1.0 + (mg_conc/3.57) * exp(-0.062 * v_post/mV)) : 1
            I_nmda = g_nmda * B_mg * (E_nmda - v_post) : amp
            """)
            on_pre_parts.append("s_nmda += w * w_nmda")
            namespace["tau_nmda_rise"] = p["tau_rise"] * b2.ms
            namespace["tau_nmda_decay"] = p["tau_decay"] * b2.ms
            namespace["E_nmda"] = p["E_rev"] * b2.mV
            namespace["mg_conc"] = p["mg_conc"]  # mM
            namespace["w_nmda"] = p["weight_ratio"]
        
        # --- GABA_A: Fast inhibitory with dual exponential ---
        if "gaba_a" in receptor_params:
            p = receptor_params["gaba_a"]
            model_parts.append("""
            dg_gaba_a/dt = (s_gaba_a - g_gaba_a) / tau_gaba_a_decay : siemens
            ds_gaba_a/dt = -s_gaba_a / tau_gaba_a_rise : siemens
            I_gaba_a = g_gaba_a * (E_gaba_a - v_post) : amp
            """)
            on_pre_parts.append("s_gaba_a += w * w_gaba_a")
            namespace["tau_gaba_a_rise"] = p["tau_rise"] * b2.ms
            namespace["tau_gaba_a_decay"] = p["tau_decay"] * b2.ms
            namespace["E_gaba_a"] = p["E_rev"] * b2.mV
            namespace["w_gaba_a"] = p["weight_ratio"]
        
        # --- GABA_B: Slow inhibitory (G-protein coupled, K+ channel) ---
        if "gaba_b" in receptor_params:
            p = receptor_params["gaba_b"]
            model_parts.append("""
            dg_gaba_b/dt = (s_gaba_b - g_gaba_b) / tau_gaba_b_decay : siemens
            ds_gaba_b/dt = -s_gaba_b / tau_gaba_b_rise : siemens
            I_gaba_b = g_gaba_b * (E_gaba_b - v_post) : amp
            """)
            on_pre_parts.append("s_gaba_b += w * w_gaba_b")
            namespace["tau_gaba_b_rise"] = p["tau_rise"] * b2.ms
            namespace["tau_gaba_b_decay"] = p["tau_decay"] * b2.ms
            namespace["E_gaba_b"] = p["E_rev"] * b2.mV
            namespace["w_gaba_b"] = p["weight_ratio"]
        
        # Combine model parts
        if len(receptor_params) > 0:
            # Sum all receptor currents into the postsynaptic input current 'I'
            # Assuming neuron has 'I : amp'
            
            # Identify current variables defined in parts
            current_vars = []
            if "ampa" in receptor_params: current_vars.append("I_ampa")
            if "nmda" in receptor_params: current_vars.append("I_nmda")
            if "gaba_a" in receptor_params: current_vars.append("I_gaba_a")
            if "gaba_b" in receptor_params: current_vars.append("I_gaba_b")
            
            if current_vars:
                # Total synaptic current
                model_parts.append(f"I_syn = {' + '.join(current_vars)} : amp")
                model_parts.append("I_post = I_syn : amp (summed)")
                
                # Special handling for NMDA calcium current
                if "nmda" in receptor_params:
                     # Check if neuron has I_nmda_total
                     pass

            model = "\n".join(model_parts)
            on_pre = "; ".join(on_pre_parts)
        else:
            # Fallback to simple current-based synapse
            model = "w : siemens"
            on_pre = "v_post += w / nS * mV"
        
            # Fallback to simple current-based synapse
            model = "w : siemens"
            on_pre = "v_post += w / nS * mV"
        
        return model, on_pre, on_post, namespace


    def _get_stp_model(self, stp_params):
        """Get short-term plasticity equations using Tsodyks-Markram model.
        
        Implements the Tsodyks-Markram (1997) model:
        - x: fraction of available resources (depression)
        - u: release probability (facilitation)
        - U: baseline release probability
        - tau_d: recovery time from depression
        - tau_f: decay time of facilitation
        
        Release: r = u * x, then x decreases and u increases
        """
        plasticity_type = stp_params.get("plasticity_type", "tsodyks_markram")
        namespace = {}
        
        if plasticity_type == "tsodyks_markram":
            # Full Tsodyks-Markram model with facilitation and depression
            U = stp_params.get("tm_U", 0.5)
            tau_d = stp_params.get("tm_tau_d", 800.0)
            tau_f = stp_params.get("tm_tau_f", 50.0)
            
            model = """
            dx/dt = (1 - x) / tau_d : 1 (event-driven)
            du/dt = (U_stp - u) / tau_f : 1 (event-driven)
            r : 1  # Release probability (set in on_pre)
            """
            # Order matters: first update u (facilitation), then compute release, then decrease x
            on_pre = "u += U_stp * (1 - u); r = u * x; x -= r; "
            
            namespace["tau_d"] = tau_d * b2.ms
            namespace["tau_f"] = tau_f * b2.ms
            namespace["U_stp"] = U
        
        elif plasticity_type == "simple_depression":
            # Simple depression only
            tau_d = stp_params.get("dep_tau", 500.0)
            dep_factor = stp_params.get("dep_factor", 0.8)
            dep_min = stp_params.get("dep_min", 0.1)
            
            model = """
            dx/dt = (1 - x) / tau_d : 1 (event-driven)
            """
            on_pre = f"x = clip(x * {dep_factor}, {dep_min}, 1.0); "
            
            namespace["tau_d"] = tau_d * b2.ms
        
        elif plasticity_type == "simple_facilitation":
            # Simple facilitation only
            tau_f = stp_params.get("fac_tau", 100.0)
            fac_increment = stp_params.get("fac_increment", 0.1)
            fac_max = stp_params.get("fac_max", 3.0)
            
            model = """
            du/dt = (1 - u) / tau_f : 1 (event-driven)
            """
            on_pre = f"u = clip(u + {fac_increment}, 1.0, {fac_max}); "
            
            namespace["tau_f"] = tau_f * b2.ms
        
        else:
            # No STP
            model = ""
            on_pre = ""
        
        return model, on_pre, namespace


    def _get_stdp_model(self, stdp_params):
        """Get STDP equations and namespace."""
        # STDP Parameters
        tau_pre = stdp_params.get("tau_pre", 20.0)
        tau_post = stdp_params.get("tau_post", 20.0)
        A_plus = stdp_params.get("A_plus", 0.01)
        A_minus = stdp_params.get("A_minus", 0.0105)
        w_max = stdp_params.get("w_max", 1.0)
        w_min = stdp_params.get("w_min", 0.0)
        
        stdp_type = stdp_params.get("stdp_type", "additive")
        
        namespace = {
            "tau_pre": tau_pre * b2.ms,
            "tau_post": tau_post * b2.ms,
            "A_plus": A_plus * b2.nS,
            "A_minus": A_minus * b2.nS,
            "w_max": w_max * b2.nS,
            "w_min": w_min * b2.nS,
        }
        
        model = """
        dapre/dt = -apre / tau_pre : 1 (event-driven)
        dapost/dt = -apost / tau_post : 1 (event-driven)
        """
        
        # Standard Additive STDP logic
        # on_pre: w increases (LTP) if post spike was recent (apost > 0). Plus update trace for future post spikes.
        # on_post: w decreases (LTD) if pre spike was recent (apre > 0). Plus update trace for future pre spikes.
        
        on_pre = "apre += A_plus; w = clip(w + apost, w_min, w_max); "
        on_post = "apost -= A_minus; w = clip(w + apre, w_min, w_max); "
        
        if stdp_type == "multiplicative":
            # Multiplicative weight dependence
            # Multiplicative weight dependence (clip(w + apost * w, ...))
            pass
            pass

        return model, on_pre, on_post, namespace



    def _initialize_weights(self, synapses, network_params, synaptic_receptors_params, stp_enabled):
        """Initialize synaptic weights."""
        base_weight = network_params.get("weight", 0.5) * b2.nS
        synapses.w = base_weight

        if stp_enabled:
            # Tsodyks-Markram: x starts at 1 (full resources), u starts at U (baseline)
            if hasattr(synapses, "x"):
                synapses.x = 1.0
            if hasattr(synapses, "u"):
                synapses.u = 0.2  # Will be overwritten in first spike anyway
            if hasattr(synapses, "r"):
                synapses.r = 0.0  # Release probability starts at 0

    def _apply_advanced_network_features(self, synapses, advanced_params, neurons):
        """Apply advanced network features."""
        # 1. Dale's Principle
        dales_config = advanced_params.get("dales_principle", {})
        # Handle possibly nested config structure
        
        use_dales = advanced_params.get("dales_principle", {}).get("enabled", False) if isinstance(advanced_params.get("dales_principle"), dict) else advanced_params.get("dales_principle", False)
        
        if use_dales:
            # Retrieve params from nested dict if present, else flat
            dp_params = advanced_params.get("dales_principle", {}) if isinstance(advanced_params.get("dales_principle"), dict) else advanced_params
            
            exc_fraction = dp_params.get("excitatory_ratio", dp_params.get("exc_fraction", 0.8))
            n = len(neurons)
            n_exc = int(n * exc_fraction)

            exc_weight = dp_params.get("exc_weight", 1.0) * b2.nS
            inh_weight = dp_params.get("inh_weight", -4.0) * b2.nS
            
            # Reversal Potentials logic
            exc_rev = advanced_params.get("exc_reversal", 0.0) * b2.mV
            inh_rev = advanced_params.get("inh_reversal", -80.0) * b2.mV
            
            has_erev = hasattr(synapses, "E_rev")

            # Apply weights based on neuron index (0..n_exc are excitatory)
            # This assumes neurons are sorted or grouped.
            if n_exc > 0 and n_exc < n:
                synapses.w["i < n_exc"] = exc_weight
                synapses.w["i >= n_exc"] = inh_weight
                if has_erev:
                    synapses.E_rev["i < n_exc"] = exc_rev
                    synapses.E_rev["i >= n_exc"] = inh_rev
                    
            elif n_exc == n:
                synapses.w = exc_weight
                if has_erev:
                    synapses.E_rev = exc_rev
            elif n_exc == 0:
                synapses.w = inh_weight
                if has_erev:
                    synapses.E_rev = inh_rev

        # 2. Synaptic Delays
        delay_config = advanced_params.get("synaptic_delays", {})
        use_delays = delay_config.get("enabled", False)
        
        if use_delays:
            min_delay = delay_config.get("min_delay", 0.5) * b2.ms
            max_delay = delay_config.get("max_delay", 5.0) * b2.ms
            delay_type = delay_config.get("delay_type", "uniform")
            
            if delay_type == "uniform":
                 synapses.delay = "min_delay + rand() * (max_delay - min_delay)"
            elif delay_type == "distance_dependent":
                 # requires spatial positions
                 if hasattr(neurons, "x") and hasattr(neurons, "y"):
                     velocity = advanced_params.get("conduction_velocity", 0.5) * b2.meter/b2.second
                     synapses.namespace["c_velocity"] = velocity
                     synapses.delay = "sqrt((x_pre-x_post)**2 + (y_pre-y_post)**2) / c_velocity"
                 else:
                     print("Warning: Distance-dependent delays requested but neurons lack spatial coordinates. Using uniform.")
                     synapses.delay = "min_delay + rand() * (max_delay - min_delay)"
            elif delay_type == "normal":
                 mean_delay = delay_config.get("mean_delay", 1.0) * b2.ms
                 std_delay = delay_config.get("delay_std", 0.3) * b2.ms
                 # Use clip to ensure positive delays
                 synapses.delay = f"clip({mean_delay} + {std_delay} * randn(), {min_delay}, {max_delay})"
            else:
                 # Fallback to uniform
                 synapses.delay = "min_delay + rand() * (max_delay - min_delay)"



    def _setup_calcium_plasticity(self, synapses, ca_params):
        """Setup calcium-dependent plasticity (threshold based)."""
        if not ca_params.get("ca_plasticity_enabled", False):
            return

        # Thresholds (uM -> mM for Brian2)
        ltp_thres = ca_params.get("ca_ltp_threshold", 1.0) * b2.umolar
        ltd_thres = ca_params.get("ca_ltd_threshold", 0.3) * b2.umolar
        
        ltp_rate = ca_params.get("ca_ltp_rate", 0.01)
        ltd_rate = ca_params.get("ca_ltd_rate", 0.005)
        
        # We need w_max/w_min for clipping, usually from STDP or generic
        w_max = ca_params.get("w_max", ca_params.get("max_weight", 10.0)) * b2.nS
        w_min = ca_params.get("w_min", ca_params.get("min_weight", 0.0)) * b2.nS
        
        synapses.namespace.update({
            "Ca_LTP_thres": ltp_thres,
            "Ca_LTD_thres": ltd_thres,
            "eta_LTP": ltp_rate,
            "eta_LTD": ltd_rate,
            "w_max_ca": w_max,
            "w_min_ca": w_min
        })
        
        # Run regularly to update weights based on postsynaptic Calcium
        # Note: Ca_post must exist in neuron group
        synapses.run_regularly(
            """
            # Calculate weight change direction
            # Potentiation if Ca > LTP
            # Depression if LTD < Ca < LTP
            
            is_pot = int(Ca_post > Ca_LTP_thres)
            is_dep = int(Ca_post > Ca_LTD_thres) * int(Ca_post < Ca_LTP_thres)
            
            delta_w = (eta_LTP * is_pot - eta_LTD * is_dep) * dt
            
            # Apply change (only if plastic)
            w = clip(w + delta_w * nS / ms, w_min_ca, w_max_ca)
            """,
            dt=ca_params.get("update_dt", 10.0) * b2.ms
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
        # Config uses 'junction_type' and separate 'voltage_dependence' flag
        gj_type = gap_params.get("junction_type", "symmetric")
        voltage_dep = gap_params.get("voltage_dependence", False)

        # Base conductance (g_gap) is defined. 
        # We need to define I_gap_post.

        eqs = ["g_gap : siemens"]
        g_effective_expr = "g_gap"

        # 1. Handle Voltage Dependence (Gating)
        if voltage_dep:
            Vhalf = gap_params.get("gating_voltage", -40.0)
            k = gap_params.get("gating_slope", 10.0)
            eqs.append(f"g_open = 1 / (1 + exp(-(v_pre - v_post - {Vhalf}*mV) / ({k}*mV))) : 1")
            g_effective_expr += " * g_open"

        # 2. Handle Rectification (Asymmetric)
        if gj_type == "rectifying":
            # Rectifying allows current only one way (e.g., pre > post)
            # Or usually implemented as asymmetric conductance
            eqs.append("ratio = int(v_pre > v_post) : 1")
            g_effective_expr += " * ratio"
        
        # 3. Handle Activity Dependence (Plasticity) - basic scaffold
        if gap_params.get("activity_dependent", False):
            # If complex plasticity is needed, it might require differential equations for g_gap
            pass 

        eqs.append(f"g_effective = {g_effective_expr} : siemens")
        eqs.append("I_gap_post = g_effective * (v_pre - v_post) : amp (summed)")


        return "\n".join(eqs)


    def _connect_gap_junctions(self, gap_junctions, gap_params, neurons):
        """Connect gap junctions based on spatial organization."""
        pattern = gap_params.get("spatial_organization", "random")
        n = len(neurons)

        if pattern == "random":
            probability = gap_params.get("connection_probability", 0.05)
            gap_junctions.connect(condition="i < j", p=probability)
            # Bidirectional
            gap_junctions.connect(condition="i > j", p=probability)

        elif pattern == "nearest_neighbor":
            # Interpret 'cluster_size' or 'num_neighbors' as k
            k = gap_params.get("cluster_size", gap_params.get("num_neighbors", 2))
            for i in range(n):
                for j in range(1, k + 1):
                    if i + j < n:
                        gap_junctions.connect(i=i, j=i + j)
                        gap_junctions.connect(i=i + j, j=i)

        elif pattern == "distance_based" or pattern == "distance_dependent":
            # Distance based connection
            max_dist = gap_params.get("max_distance", 100.0)  # um
            sigma = max_dist / 3.0  # approximate sigma if not provided

            # Generate random 3D positions if not already present in neurons
            # In a real sim, neurons should have positions. We'll simulate them here if missing.
            if hasattr(neurons, "x") and hasattr(neurons, "y"):
                # Use actual positions
                pass # Brian2 handles distance check automatically if we use correct syntax
                # But here we loop manually for probability
                # Simplified: assume we need to calculate dist manually for probability
                pass
            
            # Use synthetic positions for connectivity generation
            positions = np.random.uniform(0, max_dist * 3, (n, 3))
            
            for i in range(n):
                for j in range(i + 1, n):
                    dist = np.sqrt(np.sum((positions[i] - positions[j]) ** 2))
                    if dist < max_dist:
                        prob = np.exp(-(dist**2) / (2 * sigma**2))
                        if np.random.random() < prob:
                            gap_junctions.connect(i=i, j=j)
                            gap_junctions.connect(i=j, j=i)

        elif pattern in ["columnar", "radial_clusters"]:
            # Cluster based connectivity
            cluster_size = gap_params.get("cluster_size", 10)
            num_clusters = n // cluster_size
            
            for c in range(num_clusters):
                start_idx = c * cluster_size
                end_idx = min((c + 1) * cluster_size, n)
                # All-to-all within cluster
                for i in range(start_idx, end_idx):
                    for j in range(i + 1, end_idx):
                         gap_junctions.connect(i=i, j=j)
                         gap_junctions.connect(i=j, j=i)

        else:  # Fallback
            gap_junctions.connect(condition="i != j", p=0.01)

    def _set_gap_junction_properties(self, gap_junctions, gap_params):
        """Set gap junction properties and parameters."""
        conductance = gap_params.get("conductance", 0.1) * b2.nS
        
        # Determine noise properties
        # Config: junction_noise (bool), noise_amplitude (nS)
        use_noise = gap_params.get("junction_noise", False)
        noise_amp = gap_params.get("noise_amplitude", 0.01) * b2.nS
        
        if use_noise and noise_amp > 0 * b2.nS:
            # Apply static noise to conductance
            # g_gap = conductance + noise * randn()
            gap_junctions.g_gap = f"clip({conductance} + {noise_amp} * randn(), 0*nS, 10*nS)"
        else:
            gap_junctions.g_gap = conductance

        # Handle voltage dependence parameters if enabled
        if gap_params.get("voltage_dependence", False):
            # These are constants in the equations, usually don't need setting per synapse unless heterogeneous
            # But if we wanted heterogeneity, we could set them here.
            pass


