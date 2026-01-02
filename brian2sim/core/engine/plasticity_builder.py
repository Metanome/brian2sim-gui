"""
Plasticity Builder for Brian2 simulations.
Handles homeostatic plasticity, neuromodulation, BCM, metaplasticity, and pharmacology.
"""

try:
    import brian2 as b2

    BRIAN2_AVAILABLE = True
except ImportError:
    BRIAN2_AVAILABLE = False


class PlasticityBuilder:
    """Builder class for constructing plasticity and neuromodulation mechanisms."""

    def __init__(self):
        self.homeostatic_mechanisms = None
        self.neuromodulation_systems = None

    def setup_homeostatic_plasticity(self, homeo_params, neurons, synapses):
        """Setup homeostatic plasticity mechanisms for network stability."""
        if not homeo_params.get("enabled", False):
            return None

        mechanisms = {}

        # Activity detection
        if homeo_params.get("activity_detection", True):
            mechanisms["activity"] = self._setup_activity_detection(homeo_params, neurons)

        # Synaptic scaling
        if homeo_params.get("synaptic_scaling", False) and synapses:
            mechanisms["scaling"] = self._setup_synaptic_scaling(homeo_params, neurons, synapses)

        # Intrinsic regulation
        if homeo_params.get("intrinsic_regulation", False):
            mechanisms["intrinsic"] = self._setup_intrinsic_regulation(homeo_params, neurons)

        # Threshold adaptation
        if homeo_params.get("threshold_adaptation", False):
            mechanisms["threshold"] = self._setup_threshold_adaptation(homeo_params, neurons)

        # BCM plasticity
        if homeo_params.get("bcm_plasticity", False) and synapses:
            mechanisms["bcm"] = self._setup_bcm_plasticity(homeo_params, neurons, synapses)

        # Network-level regulation
        if homeo_params.get("network_regulation", False) and synapses:
            mechanisms["network"] = self._setup_network_regulation(homeo_params, neurons, synapses)

        # Metaplasticity
        if homeo_params.get("metaplasticity", False) and synapses:
            mechanisms["metaplasticity"] = self._setup_metaplasticity(
                homeo_params, neurons, synapses
            )

        self.homeostatic_mechanisms = mechanisms
        return mechanisms

    def _setup_activity_detection(self, homeo_params, neurons):
        """Setup activity detection for homeostatic regulation."""
        tau_activity = homeo_params.get("tau_activity", homeo_params.get("target_window", 1000.0)) * b2.ms
        target_rate = homeo_params.get("target_rate", homeo_params.get("target_firing_rate", 5.0)) * b2.Hz

        # Add activity tracking
        neurons.run_regularly(
            """
            activity = activity * exp(-dt/tau_activity)
            activity_error = activity - target_rate
            """,
            dt=10 * b2.ms,
            when="end",
        )

        return {"tau_activity": tau_activity, "target_rate": target_rate}

    def _setup_synaptic_scaling(self, homeo_params, neurons, synapses):
        """Setup synaptic scaling homeostatic mechanism."""
        scaling_rate = homeo_params.get("scaling_rate", 0.001)
        min_weight = homeo_params.get("min_weight", homeo_params.get("min_weight_scaling", 0.1) * 10.0) * b2.nS
        max_weight = homeo_params.get("max_weight", homeo_params.get("max_weight_scaling", 5.0) * 10.0) * b2.nS
        target_rate = homeo_params.get("target_rate", homeo_params.get("target_firing_rate", 5.0)) * b2.Hz

        # Multiplicative scaling
        synapses.run_regularly(
            f"""
            scaling_factor = 1 + {scaling_rate} * (target_rate - activity_post) / Hz
            w = clip(w * scaling_factor, {min_weight}, {max_weight})
            """,
            dt=100 * b2.ms,
        )

        return {"scaling_rate": scaling_rate, "min_weight": min_weight, "max_weight": max_weight}

    def _setup_intrinsic_regulation(self, homeo_params, neurons):
        """Setup intrinsic excitability regulation."""
        tau_intrinsic = homeo_params.get("tau_intrinsic", 5000.0) * b2.ms
        target_rate = homeo_params.get("target_rate", 5.0)

        # Adjust leak conductance based on activity
        neurons.run_regularly(
            f"""
            g_leak_adjustment = 1 - 0.001 * (activity/Hz - {target_rate})
            g_leak = clip(g_leak * g_leak_adjustment, 0.5*nS, 50*nS)
            """,
            dt=1000 * b2.ms,
        )

        return {"tau_intrinsic": tau_intrinsic}

    def _setup_threshold_adaptation(self, homeo_params, neurons):
        """Setup adaptive spike threshold mechanism."""
        tau_threshold = homeo_params.get("tau_threshold", 10000.0) * b2.ms
        threshold_increment = homeo_params.get("threshold_increment", 0.1) * b2.mV
        threshold_min = homeo_params.get("threshold_min", -60.0) * b2.mV
        threshold_max = homeo_params.get("threshold_max", -30.0) * b2.mV
        target_rate = homeo_params.get("target_rate", 5.0)

        neurons.run_regularly(
            f"""
            threshold_adjustment = {threshold_increment} * (activity/Hz - {target_rate})
            v_threshold = clip(v_threshold + threshold_adjustment, {threshold_min}, {threshold_max})
            """,
            dt=1000 * b2.ms,
        )

        return {"tau_threshold": tau_threshold, "threshold_increment": threshold_increment}

    def _setup_bcm_plasticity(self, homeo_params, neurons, synapses):
        """Setup BCM-like plasticity with sliding threshold."""
        tau_theta = homeo_params.get("tau_theta", homeo_params.get("bcm_tau", 10000.0)) * b2.ms
        theta_init = homeo_params.get("theta_init", 1.0)
        eta = homeo_params.get("bcm_learning_rate", 0.01)

        # Add sliding threshold variable
        try:
            p_bcm = homeo_params.get("bcm_power", 2.0)
            synapses.namespace["theta"] = theta_init
            synapses.namespace["tau_theta"] = tau_theta
            synapses.namespace["eta_bcm"] = eta
            synapses.namespace["p_bcm"] = p_bcm

            # BCM rule: dw/dt = eta * post * (post - theta) * pre
            # Theta tracks activity^p
            # Note: We work in dimensionless units for theta to avoid complex unit powers in Brian2
            synapses.run_regularly(
                """
                theta = theta + dt/tau_theta * ((activity_post/Hz)**p_bcm - theta)
                dw = eta_bcm * activity_post/Hz * (activity_post/Hz - theta) * activity_pre/Hz * nS
                w = clip(w + dw, w_min, w_max)
                """,
                dt=homeo_params.get("bcm_dt", 100.0) * b2.ms,
            )
        except Exception as e:
            print(f"Note: BCM plasticity setup error: {e}")

        return {"tau_theta": tau_theta, "theta_init": theta_init, "eta": eta, "p_bcm": p_bcm}

    def _setup_network_regulation(self, homeo_params, neurons, synapses):
        """Setup network-level homeostatic regulation."""
        target_activity = homeo_params.get("target_network_activity", 0.1)  # fraction
        regulation_rate = homeo_params.get("network_regulation_rate", 0.0001)

        try:
            # Global inhibition scaling
            synapses.run_regularly(
                f"""
                network_activity = sum(activity_post) / N_post / Hz
                inhibition_scale = 1 + {regulation_rate} * (network_activity - {target_activity})
                w = w * int(w > 0*nS) + w * inhibition_scale * int(w < 0*nS)
                """,
                dt=homeo_params.get("regulation_dt", 500.0) * b2.ms,
            )
        except Exception as e:
            print(f"Note: Network regulation setup error: {e}")

        return {"target_activity": target_activity, "regulation_rate": regulation_rate}

    def _setup_metaplasticity(self, homeo_params, neurons, synapses):
        """Setup metaplasticity - activity-dependent changes in plasticity rules."""
        tau_meta = homeo_params.get("tau_metaplasticity", 50000.0) * b2.ms
        meta_threshold = homeo_params.get("meta_threshold", homeo_params.get("metaplasticity_threshold", 5.0)) * b2.Hz

        try:
            # Sliding modification threshold for STDP
            synapses.namespace["tau_meta"] = tau_meta
            synapses.namespace["meta_threshold"] = meta_threshold
            
            # Scales for LTP/LTD adjustments
            ltp_scale = homeo_params.get("meta_ltp_scaling", 0.001)
            ltd_scale = homeo_params.get("meta_ltd_scaling", 0.001)
            
            synapses.namespace["ltp_scale"] = ltp_scale
            synapses.namespace["ltd_scale"] = ltd_scale

            synapses.run_regularly(
                """
                # Update metaplasticity state
                avg_activity = (activity_pre + activity_post) / (2*Hz)
               
                # High activity -> increase LTD, decrease LTP
                # Low activity -> decrease LTD, increase LTP
                meta_factor = (avg_activity - meta_threshold/Hz) / (meta_threshold/Hz)
               
                # Apply to STDP parameters if they exist
                # Simple logic: modify A_plus / A_minus (requires them to be variables, not consts!)
                # If they are consts in namespace, this checks fails.
                # Assuming dynamic modification:
                A_plus = A_plus * (1 - ltp_scale * meta_factor)
                A_minus = A_minus * (1 + ltd_scale * meta_factor)
                """,
                dt=homeo_params.get("metaplasticity_dt", 1000.0) * b2.ms,
            )
        except Exception as e:
            print(f"Note: Metaplasticity requires STDP variables: {e}")

        return {"tau_meta": tau_meta, "meta_threshold": meta_threshold}

    def setup_neuromodulation(self, neuromod_params, neurons, synapses):
        """Setup neuromodulation systems (dopamine, acetylcholine, etc.)."""
        if not neuromod_params.get("enabled", False):
            return None

        systems = {}

        if neuromod_params.get("dopamine_enabled", neuromod_params.get("dopamine_system", False)):
            systems["dopamine"] = self._setup_dopamine_system(neuromod_params, neurons, synapses)

        if neuromod_params.get("acetylcholine_enabled", neuromod_params.get("acetylcholine_system", False)):
            systems["acetylcholine"] = self._setup_acetylcholine_system(
                neuromod_params, neurons, synapses
            )

        if neuromod_params.get("serotonin_enabled", neuromod_params.get("serotonin_system", False)):
            systems["serotonin"] = self._setup_serotonin_system(neuromod_params, neurons, synapses)

        if neuromod_params.get("noradrenaline_enabled", neuromod_params.get("noradrenaline_system", False)):
            systems["noradrenaline"] = self._setup_noradrenaline_system(
                neuromod_params, neurons, synapses
            )

        # Setup release patterns
        if systems:
            self._setup_neuromodulator_release(neuromod_params, systems, neurons)

        # Setup pharmacology
        if neuromod_params.get("pharmacology_enabled", False):
            self._setup_pharmacology(neuromod_params, systems, neurons)

        self.neuromodulation_systems = systems
        return systems

    def _setup_dopamine_system(self, neuromod_params, neurons, synapses):
        """Setup dopaminergic neuromodulation system."""
        baseline = neuromod_params.get("dopamine_baseline", 0.5)
        tau_da = neuromod_params.get("dopamine_tau", neuromod_params.get("dopamine_clearance_tau", 200.0)) * b2.ms

        try:
            # Add dopamine dynamics
            neurons.namespace["DA_baseline"] = baseline
            neurons.namespace["tau_DA"] = tau_da

            # Add specific receptor effects to namespace
            neurons.namespace["DA_D1"] = neuromod_params.get("dopamine_d1_effect", 0.2)
            neurons.namespace["DA_D2"] = neuromod_params.get("dopamine_d2_effect", -0.15)
            
            neurons.run_regularly(
                """
                DA = DA + dt * (DA_baseline - DA) / tau_DA
                # Net modulation combines D1 (typically excitatory) and D2 (inhibitory) coefficients
                DA_modulation = 1 + (DA - DA_baseline) * (DA_D1 + DA_D2)
                """,
                dt=1 * b2.ms,
            )

            # Dopamine modulates synaptic plasticity
            if synapses:
                synapses.namespace["DA_D1"] = neuromod_params.get("dopamine_d1_effect", 0.2)
                synapses.namespace["DA_D2"] = neuromod_params.get("dopamine_d2_effect", -0.15)
                synapses.run_regularly(
                    """
                    # Modulation of synaptic weight based on net receptor activation
                    w_mod = (DA_post - 0.5) * (DA_D1 + DA_D2)
                    w = w * (1 + 0.01 * w_mod)
                    """,
                    dt=100 * b2.ms,
                )
        except Exception as e:
            print(f"Note: Dopamine setup error: {e}")

        return {"baseline": baseline, "tau": tau_da, "type": "dopamine"}

    def _setup_acetylcholine_system(self, neuromod_params, neurons, synapses):
        """Setup cholinergic neuromodulation system."""
        baseline = neuromod_params.get("acetylcholine_baseline", 0.5)
        tau_ach = neuromod_params.get("acetylcholine_tau", neuromod_params.get("acetylcholine_clearance_tau", 100.0)) * b2.ms

        try:
            neurons.namespace["ACh_baseline"] = baseline
            neurons.namespace["tau_ACh"] = tau_ach

            # ACh modulates excitability
            neurons.namespace["ACh_Muscarinic"] = neuromod_params.get("muscarinic_effect", 0.15)
            neurons.namespace["ACh_Nicotinic"] = neuromod_params.get("nicotinic_effect", 0.3)

            # ACh modulates excitability
            neurons.run_regularly(
                """
                ACh = ACh + dt * (ACh_baseline - ACh) / tau_ACh
                # Muscarinic effect modulates threshold (excitability)
                v_th = v_th - (ACh - ACh_baseline) * ACh_Muscarinic * 20*mV # 20*mV is max shift at effect=1.0
                """,
                dt=neuromod_params.get("update_dt", 1.0) * b2.ms,
            )
        except Exception as e:
            print(f"Note: Acetylcholine setup error: {e}")

        return {"baseline": baseline, "tau": tau_ach, "type": "acetylcholine"}

    def _setup_serotonin_system(self, neuromod_params, neurons, synapses):
        """Setup serotonergic neuromodulation system."""
        baseline = neuromod_params.get("serotonin_baseline", 0.5)
        tau_5ht = neuromod_params.get("serotonin_tau", neuromod_params.get("serotonin_clearance_tau", 500.0)) * b2.ms

        try:
            neurons.namespace["HT5_baseline"] = baseline
            neurons.namespace["tau_5HT"] = tau_5ht

            # 5-HT modulates inhibition and membrane time constant
            neurons.namespace["HT5_1A"] = neuromod_params.get("5ht1a_effect", -0.1)
            neurons.namespace["HT5_2A"] = neuromod_params.get("5ht2a_effect", 0.15)

            # 5-HT modulates inhibition and membrane time constant
            neurons.run_regularly(
                """
                HT5 = HT5 + dt * (HT5_baseline - HT5) / tau_5HT
                # Net effect on time constant
                tau = tau * (1 + (HT5 - HT5_baseline) * (HT5_1A + HT5_2A))
                """,
                dt=1 * b2.ms,
            )
        except Exception as e:
            print(f"Note: Serotonin setup error: {e}")

        return {"baseline": baseline, "tau": tau_5ht, "type": "serotonin"}

    def _setup_noradrenaline_system(self, neuromod_params, neurons, synapses):
        """Setup noradrenergic neuromodulation system."""
        baseline = neuromod_params.get("noradrenaline_baseline", 0.5)
        tau_ne = neuromod_params.get("noradrenaline_tau", neuromod_params.get("noradrenaline_clearance_tau", 300.0)) * b2.ms

        try:
            neurons.namespace["NE_baseline"] = baseline
            neurons.namespace["tau_NE"] = tau_ne

            # NE modulates gain and signal-to-noise ratio
            neurons.namespace["NE_Alpha1"] = neuromod_params.get("alpha1_effect", 0.2)
            neurons.namespace["NE_Alpha2"] = neuromod_params.get("alpha2_effect", -0.1)
            neurons.namespace["NE_Beta"] = neuromod_params.get("beta_effect", 0.15)

            # NE modulates gain and signal-to-noise ratio
            neurons.run_regularly(
                """
                NE = NE + dt * (NE_baseline - NE) / tau_NE
                # Combined adrenergic effect on gain
                gain_factor = 1 + (NE - NE_baseline) * (NE_Alpha1 + NE_Alpha2 + NE_Beta)
                """,
                dt=1 * b2.ms,
            )
        except Exception as e:
            print(f"Note: Noradrenaline setup error: {e}")

        return {"baseline": baseline, "tau": tau_ne, "type": "noradrenaline"}

    def _setup_neuromodulator_release(self, neuromod_params, systems, neurons):
        """Setup neuromodulator release patterns."""
        # Map release_triggers config to internal pattern logic
        release_pattern = neuromod_params.get("release_triggers", "manual")
        # 'manual' maps to tonic/steady state in this context unless triggered manually
        if release_pattern == "manual": 
             release_pattern = "tonic"
        elif release_pattern == "temporal_pattern":
             release_pattern = "oscillatory"
        elif release_pattern == "activity_dependent":
             release_pattern = "phasic"

        if release_pattern == "tonic":
            # Steady-state release (default behavior)
            pass

        elif release_pattern == "phasic":
            # Event-triggered release bursts
            for nm_name, nm_system in systems.items():
                try:
                    # Calculate burst amplitude from release rate and duration
                    # burst = rate (uM/ms) * duration (ms)
                    release_rate = neuromod_params.get(f"{nm_name}_release_rate", 0.01)
                    duration = neuromod_params.get("release_duration", 100.0)
                    burst_amplitude = release_rate * duration * 0.1 # Scaling factor for simulation stability
                    
                    # Alternatively check for explicit burst amplitude override
                    if f"{nm_name}_burst_amplitude" in neuromod_params:
                        burst_amplitude = neuromod_params[f"{nm_name}_burst_amplitude"]

                    # Triggered by high network activity
                    neurons.run_regularly(
                        f"""
                        {nm_name.upper()}_burst = {burst_amplitude} * int(sum(activity)/N > 10*Hz)
                        {nm_name.upper()} = {nm_name.upper()} + {nm_name.upper()}_burst
                        """,
                        dt=10 * b2.ms,
                    )
                except Exception as e:
                    print(f"Note: Phasic release setup error for {nm_name}: {e}")

        elif release_pattern == "oscillatory":
            # Rhythmic release
            for nm_name, nm_system in systems.items():
                try:
                    osc_frequency = neuromod_params.get(f"{nm_name}_osc_frequency", 0.1) * b2.Hz
                    osc_amplitude = neuromod_params.get(f"{nm_name}_osc_amplitude", 0.1)

                    neurons.run_regularly(
                        f"""
                        {nm_name.upper()}_osc = {osc_amplitude} * sin(2*pi*{osc_frequency}*t)
                        {nm_name.upper()} = {nm_name.upper()} + {nm_name.upper()}_osc
                        """,
                        dt=10 * b2.ms,
                    )
                except Exception as e:
                    print(f"Note: Oscillatory release setup error for {nm_name}: {e}")

        elif release_pattern == "reward_based":
            # Release modulated by reward signal
            try:
                neurons.namespace["reward_signal"] = 0.0

                for nm_name in systems:
                    neurons.run_regularly(
                        f"""
                        {nm_name.upper()}_reward = reward_signal * 0.5
                        {nm_name.upper()} = clip({nm_name.upper()} + {nm_name.upper()}_reward, 0, 1)
                        """,
                        dt=1 * b2.ms,
                    )
            except Exception as e:
                print(f"Note: Reward-based release setup error: {e}")

    def _setup_pharmacology(self, neuromod_params, systems, neurons):
        """Setup pharmacological interventions."""
        interventions = neuromod_params.get("interventions", {})

        for drug_name, drug_params in interventions.items():
            drug_type = drug_params.get("type", "agonist")
            target = drug_params.get("target", "dopamine")
            efficacy = drug_params.get("efficacy", 0.5)
            onset_time = drug_params.get("onset_time", 1000.0) * b2.ms
            duration = drug_params.get("duration", 5000.0) * b2.ms

            try:
                if target in systems:
                    nm_name = target.upper()

                    if drug_type == "agonist":
                        # Increase neuromodulator effect
                        neurons.run_regularly(
                            f"""
                            drug_active = int(t >= {onset_time}) * int(t < {onset_time + duration})
                            {nm_name} = {nm_name} + {efficacy} * drug_active
                            """,
                            dt=10 * b2.ms,
                        )

                    elif drug_type == "antagonist":
                        # Block neuromodulator effect
                        neurons.run_regularly(
                            f"""
                            drug_active = int(t >= {onset_time}) * int(t < {onset_time + duration})
                            {nm_name} = {nm_name} * (1 - {efficacy} * drug_active)
                            """,
                            dt=10 * b2.ms,
                        )

                    elif drug_type == "reuptake_inhibitor":
                        # Slow neuromodulator decay
                        systems[target]["tau"]
                        neurons.run_regularly(
                            f"""
                            drug_active = int(t >= {onset_time}) * int(t < {onset_time + duration})
                            tau_{nm_name}_effective = tau_{nm_name} * (1 + 2*{efficacy}*drug_active)
                            """,
                            dt=10 * b2.ms,
                        )

                    elif drug_type == "release_enhancer":
                        # Increase spontaneous release
                        neurons.run_regularly(
                            f"""
                            drug_active = int(t >= {onset_time}) * int(t < {onset_time + duration})
                            {nm_name} = {nm_name} + 0.01 * {efficacy} * drug_active
                            """,
                            dt=1 * b2.ms,
                        )

            except Exception as e:
                print(f"Note: Pharmacology setup error for {drug_name}: {e}")
