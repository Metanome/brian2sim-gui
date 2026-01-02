"""
Neuron Builder for Brian2 simulations.
Handles construction of point neurons and multi-compartment neuron models.
"""

try:
    import brian2 as b2

    BRIAN2_AVAILABLE = True
except ImportError:
    BRIAN2_AVAILABLE = False

import os
import numpy as np


class NeuronBuilder:
    """Builder class for constructing neuron models."""

    def __init__(self):
        self.neurons = None

    def build_neurons(
        self, sim_params, neuron_params, calcium_dynamics_params=None, multicompartment_params=None
    ):
        """Build the neuron group based on model parameters."""
        if not BRIAN2_AVAILABLE:
            return None

        num_neurons = sim_params.get("num_neurons", 10)
        model_type = neuron_params.get("model_key", "lif")

        # Check if multi-compartment is enabled
        multicomp_enabled = multicompartment_params and multicompartment_params.get(
            "enabled", False
        )

        if multicomp_enabled:
            return self._build_multicompartment_neurons(
                num_neurons, multicompartment_params, neuron_params, calcium_dynamics_params
            )

        # Calcium dynamics check
        ca_enabled = calcium_dynamics_params and calcium_dynamics_params.get("enabled", False)

        # Build based on model type
        if model_type == "lif":
            self.neurons = self._build_lif_neurons(
                num_neurons, sim_params, neuron_params, ca_enabled, calcium_dynamics_params
            )
        elif model_type == "izhikevich":
            self.neurons = self._build_izhikevich_neurons(num_neurons, neuron_params)
        elif model_type == "adex":
            self.neurons = self._build_adex_neurons(num_neurons, sim_params, neuron_params)
        elif model_type == "hodgkin_huxley":
            self.neurons = self._build_hh_neurons(num_neurons, neuron_params)
        elif model_type == "custom":
            self.neurons = self._build_custom_neurons(num_neurons, sim_params, neuron_params)
        else:
            self.neurons = self._build_default_neurons(num_neurons)

        return self.neurons

    def _build_lif_neurons(
        self, num_neurons, sim_params, neuron_params, ca_enabled, calcium_params
    ):
        """Build Leaky Integrate-and-Fire neurons."""
        # Get neuron parameters from nested 'parameters' dict (from config)
        params = neuron_params.get("parameters", neuron_params)
        
        # Config keys: tau_m, v_rest, resistance, refractory
        tau = params.get("tau_m", 20.0) * b2.ms
        v_rest = params.get("v_rest", -70.0) * b2.mV
        R = params.get("resistance", 100.0) * b2.Mohm
        refractory = params.get("refractory", 2.0) * b2.ms
        
        # Threshold and reset come from sim_params
        vt_val = sim_params.get("v_threshold", -55.0)
        vr_val = sim_params.get("v_reset", -70.0)
        
        v_threshold = vt_val * b2.mV
        v_reset = vr_val * b2.mV

        eqs = """
        dv/dt = (v_rest - v + (I + I_gap)*R) / tau : volt
        I : amp              # External/synaptic input current
        I_gap : amp          # Gap junction current (summed from electrical synapses)
        R : ohm
        activity : Hz        # Firing rate trace for plasticity
        v_th : volt          # Threshold voltage (can be modulated)
        """
        
        if ca_enabled and calcium_params:
            ca_eqs = self._get_calcium_equations(calcium_params)
            eqs = eqs + ca_eqs


        neurons = b2.NeuronGroup(
            num_neurons,
            eqs,
            threshold="v > v_th",
            reset="v = v_reset; activity += 1*Hz",
            refractory=refractory,
            method="euler",
            namespace={
                "tau": params.get("tau", 10.0) * b2.ms,
                "v_rest": params.get("v_rest", -70.0) * b2.mV,
                "v_reset": v_reset,
            },
        )

        neurons.v = v_rest
        neurons.R = R
        neurons.v_th = v_threshold

        if ca_enabled and calcium_params:
            self._initialize_calcium(neurons, calcium_params)

        return neurons


    def _build_izhikevich_neurons(self, num_neurons, neuron_params):
        """
        Build Izhikevich neurons.
        
        Parameters (from UI):
        - a: Time scale of recovery variable u (typical: 0.02)
        - b: Sensitivity of u to subthreshold v (typical: 0.2)
        - c: After-spike reset value of v (typical: -65)
        - d: After-spike increment of u (typical: 8)
        
        """
        params = neuron_params.get("parameters", neuron_params)
        
        # Get parameters from UI
        a = params.get("a", 0.02)
        b_val = params.get("b", 0.2)
        c = params.get("c", -65.0)
        d = params.get("d", 8.0)

        # Izhikevich model: dimensionless equations
        # v is membrane potential (dimensionless, represents mV in original paper)
        # u is recovery variable (dimensionless)
        # I is external input (dimensionless)
        # I_gap is gap junction input (dimensionless) - note: gap junctions generally
        # shouldn't be used with Izhikevich as it requires biophysical current
        eqs = """
        dv/dt = (0.04*v**2 + 5*v + 140 - u + I + I_gap)/ms : 1
        du/dt = (a*(b*v - u))/ms : 1
        I : 1        # External input (dimensionless)
        I_gap : 1    # Gap junction input (dimensionless) - use with caution
        a : 1
        b : 1
        c : 1
        d : 1
        """


        neurons = b2.NeuronGroup(
            num_neurons,
            eqs,
            threshold="v >= 30",
            reset="v = c; u += d",
            method="euler",
        )

        # Initialize state
        neurons.v = c
        neurons.u = b_val * c
        neurons.a = a
        neurons.b = b_val
        neurons.c = c
        neurons.d = d
        neurons.I = 0  # Will be set by input_builder

        return neurons

    def _build_adex_neurons(self, num_neurons, sim_params, neuron_params):
        """Build AdEx neurons using UI parameters (C, gL, EL, VT, delT, a, tauw, b)."""
        # Get parameters from UI, with nested 'parameters' dict support
        params = neuron_params.get("parameters", neuron_params)
        
        # Parameters from UI - note UI uses 'delT' not 'DeltaT'
        c_m = params.get("C", 200.0) * b2.pF
        g_l = params.get("gL", 10.0) * b2.nS
        e_l = params.get("EL", -70.0) * b2.mV
        v_t = params.get("VT", -50.0) * b2.mV
        d_t = params.get("delT", 2.0) * b2.mV  # UI uses 'delT'
        tau_w = params.get("tauw", 30.0) * b2.ms
        a = params.get("a", 2.0) * b2.nS
        b_param = params.get("b", 60.0) * b2.pA  # UI default is 60 pA
        
        # Get v_reset from sim_params (global) or local params, fallback to EL
        v_r_val = sim_params.get("v_reset", params.get("v_reset"))
                    
        if v_r_val is not None:
            v_r = v_r_val * b2.mV
        else:
            v_r = e_l  # Default to leak potential
        
        # AdEx equations - using v (not vm) for monitor compatibility
        # I_gap added for gap junction coupling
        eqs = """
        dv/dt = (g_l*(e_l - v) + g_l*d_t*exp((v-v_t)/d_t) + I + I_gap - w)/c_m : volt
        dw/dt = (a*(v - e_l) - w)/tau_w : amp
        I : amp              # External/synaptic input current
        I_gap : amp          # Gap junction current (summed from electrical synapses)
        activity : Hz        # Firing rate trace
        v_th : volt          # Threshold voltage (can be modulated)
        """


        neurons = b2.NeuronGroup(
            num_neurons,
            eqs,
            threshold="v > v_th",
            reset="v = v_r; w += b; activity += 1*Hz",
            method="euler",
            namespace={
                "c_m": c_m,
                "g_l": g_l,
                "e_l": e_l,
                "v_t": v_t,
                "d_t": d_t,
                "tau_w": tau_w,
                "a": a,
                "b": b_param,
                "v_r": v_r,
            },
        )

        neurons.v = e_l
        neurons.w = 0 * b2.pA
        neurons.v_th = 0 * b2.mV  # AdEx uses spike detection above 0 mV


        return neurons

    def _build_hh_neurons(self, num_neurons, neuron_params):
        """
        Build Hodgkin-Huxley neurons.
        
        Parameters (from UI):
        - C: Membrane capacitance (μF/cm²)
        - gNa_max: Max sodium conductance (mS/cm²)
        - gK_max: Max potassium conductance (mS/cm²)
        - gL: Leak conductance (mS/cm²)
        - ENa: Sodium reversal potential (mV)
        - EK: Potassium reversal potential (mV)
        - EL: Leak reversal potential (mV)
        - membrane_area: Membrane area (μm²) - used to scale conductances
        """
        params = neuron_params.get("parameters", neuron_params)
        
        # Get area and convert to cm² (1 μm² = 1e-8 cm²)
        membrane_area_um2 = params.get("membrane_area", 1000.0)
        area_cm2 = membrane_area_um2 * 1e-8  # Convert μm² to cm²
        
        # Scale conductances by area (conductance density × area = total conductance)
        Cm = params.get("C", 1.0) * b2.uF / b2.cm**2 * area_cm2 * b2.cm**2  # = uF
        gl = params.get("gL", 0.3) * b2.mS / b2.cm**2 * area_cm2 * b2.cm**2  # = mS
        g_na = params.get("gNa_max", 120.0) * b2.mS / b2.cm**2 * area_cm2 * b2.cm**2
        g_kd = params.get("gK_max", 36.0) * b2.mS / b2.cm**2 * area_cm2 * b2.cm**2
        
        El = params.get("EL", -54.4) * b2.mV
        ENa = params.get("ENa", 50.0) * b2.mV
        EK = params.get("EK", -77.0) * b2.mV
        refractory = params.get("refractory", 3.0) * b2.ms

        # Standard Hodgkin-Huxley equations
        # I_gap added for gap junction coupling
        eqs = """
        dv/dt = (gl*(El-v) - g_na*(m**3)*h*(v-ENa) - g_kd*(n**4)*(v-EK) + I + I_gap)/Cm : volt
        dm/dt = alpha_m*(1-m) - beta_m*m : 1
        dn/dt = alpha_n*(1-n) - beta_n*n : 1
        dh/dt = alpha_h*(1-h) - beta_h*h : 1
        alpha_m = 0.1*(v/mV+40)/(1-exp(-(v/mV+40)/10))/ms : Hz
        beta_m = 4*exp(-(v/mV+65)/18)/ms : Hz
        alpha_n = 0.01*(v/mV+55)/(1-exp(-(v/mV+55)/10))/ms : Hz
        beta_n = 0.125*exp(-(v/mV+65)/80)/ms : Hz
        alpha_h = 0.07*exp(-(v/mV+65)/20)/ms : Hz
        beta_h = 1/(1+exp(-(v/mV+35)/10))/ms : Hz
        I : amp              # External/synaptic input current
        I_gap : amp          # Gap junction current (summed from electrical synapses)
        activity : Hz        # Firing rate trace for plasticity
        """


        neurons = b2.NeuronGroup(
            num_neurons,
            eqs,
            threshold="v > -20*mV",
            reset="activity += 1*Hz", # Update activity trace on spike
            refractory=refractory,

            method="exponential_euler",
            namespace={
                "Cm": Cm,
                "gl": gl,
                "g_na": g_na,
                "g_kd": g_kd,
                "El": El,
                "ENa": ENa,
                "EK": EK,
            },
        )

        # Initialize gating variables to near steady-state at resting potential
        neurons.v = El
        neurons.m = 0.05
        neurons.n = 0.32
        neurons.h = 0.6

        return neurons

    def _build_custom_neurons(self, num_neurons, sim_params, neuron_params):
        """Build neurons from custom user definitions."""
        params = neuron_params.get("parameters", neuron_params)
        
        eqs = params.get("custom_eqs", "dv/dt = (I-v)/(10*ms) : 1\nI : 1")
        threshold = params.get("custom_threshold", "v > 1")
        reset = params.get("custom_reset", "v = 0")
        
        method = sim_params.get("integration_method", "euler")
        # Map 'auto' to 'exact' or 'euler' if needed, but Brian2 handles method names string.
        
        try:
            neurons = b2.NeuronGroup(
                num_neurons,
                eqs,
                threshold=threshold,
                reset=reset,
                method=method,
                name="custom_neurons"
            )
            
            # Custom models complicate initialization. We leave it to Brian2 default (0).
            
            return neurons
        except Exception as e:
            print(f"Error building custom neurons: {e}")
            # Fallback to default
            return self._build_default_neurons(num_neurons)

    def _build_default_neurons(self, num_neurons):
        """Build simple default LIF neurons."""
        eqs = """
        dv/dt = (I - v) / (10*ms) : 1
        I : 1
        """

        neurons = b2.NeuronGroup(num_neurons, eqs, threshold="v > 1", reset="v = 0", method="euler")

        return neurons

    def _build_multicompartment_neurons(
        self, num_neurons, multicomp_params, neuron_params, calcium_params=None
    ):
        """Build multi-compartment neuron models using Brian2's spatial extension."""
        try:
            from brian2 import Section, SpatialNeuron

            # Create morphology
            morph_file = multicomp_params.get("morphology_file", "")
            if morph_file and os.path.exists(morph_file):
                try:
                    morphology = b2.Morphology.from_file(morph_file)
                except Exception as e:
                    print(f"Error loading morphology from {morph_file}: {e}. Falling back to generated geometry.")
                    morphology = self._create_morphology_with_spatial(multicomp_params, Section)
            else:
                morphology = self._create_morphology_with_spatial(multicomp_params, Section)

            # Get ion channel equations
            eqs = self._get_ion_channel_equations(multicomp_params)

            # Add calcium dynamics if enabled
            if calcium_params and calcium_params.get("enabled", False):
                eqs += self._get_calcium_equations(calcium_params)

            # Create spatial neuron
            neurons = SpatialNeuron(
                morphology=morphology,
                model=eqs,
                Cm=multicomp_params.get("Cm", 1.0) * b2.uF / b2.cm**2,
                Ri=multicomp_params.get("Ri", 150.0) * b2.ohm * b2.cm,
                threshold="v > -20*mV",
                refractory=2 * b2.ms,
                method="exponential_euler",
            )

            # Set compartment-specific properties
            self._set_compartment_properties(neurons, multicomp_params)

            # Set Calcium properties if enabled
            if calcium_params and calcium_params.get("enabled", False):
                self._set_calcium_properties(neurons, calcium_params)

            # Initialize membrane potential
            neurons.v = multicomp_params.get("v_init", -70.0) * b2.mV

            self.neurons = neurons
            return neurons

        except (ImportError, AttributeError) as e:
            print(f"Multi-compartment not available: {e}. Using point neuron fallback.")
            return self._build_point_neuron_fallback(num_neurons, multicomp_params, neuron_params)

    def _create_morphology_with_spatial(self, params, Section):
        """Create morphology for multi-compartment neuron using Section class."""
        # Soma parameters
        soma_length = params.get("soma_length", 30.0) * b2.um
        soma_diameter = params.get("soma_diameter", 30.0) * b2.um

        # Dendrite parameters
        num_dendrites = params.get("num_dendrites", 4)
        dendrite_length = params.get("dendrite_length", params.get("dendrite_length_total", 200.0)) * b2.um
        # Support tapering
        diam_prox = params.get("dendrite_diameter_proximal", params.get("dendrite_diameter", 2.0))
        diam_dist = params.get("dendrite_diameter_distal", 0.5)
        use_taper = params.get("dendrite_taper", True)
        
        # Use average for now to be safe, or prox if no taper.
        dendrite_diameter = (diam_prox + diam_dist)/2.0 * b2.um if use_taper else diam_prox * b2.um

        dendrite_compartments = params.get("dendrite_compartments", params.get("dendrite_segments", 10))

        # Axon parameters
        axon_enabled = params.get("axon_enabled", params.get("include_axon", True))
        axon_length = params.get("axon_length", 500.0) * b2.um
        axon_diameter = params.get("axon_diameter", 1.0) * b2.um
        axon_compartments = params.get("axon_compartments", params.get("axon_segments", 20))

        # Build morphology - Soma is a cylinder (2 points)
        # Note: Brian2 requires explicit diameter array for robustness in some contexts or if n=1 implies 2 points.
        # Build morphology - Soma is a cylinder (2 points)
        # Note: Brian2 requires explicit diameter array for robustness in some contexts or if n=1 implies 2 points.
        # Also appears to require explicit length array for n=1 in some versions.
        morphology = Section(n=1, length=np.array([soma_length/b2.um])*b2.um, diameter=np.array([soma_diameter/b2.um, soma_diameter/b2.um])*b2.um)

        # Add dendrites
        for i in range(num_dendrites):
            if use_taper:
                # Linear taper
                # Calculate dimensionless, then multiply by unit to avoid Quantity array issues or list issues
                d_prox_m = diam_prox / b2.um
                d_dist_m = diam_dist / b2.um
                diams_m = [d_prox_m + (d_dist_m - d_prox_m) * (k / dendrite_compartments) for k in range(dendrite_compartments + 1)]
                dend_diam_arg = np.array(diams_m) * b2.um
            else:
                dend_diam_arg = dendrite_diameter # Scalar should work if constant? Or use list to be safe.
                # If scalar failed for Soma, likely fails here.
                # But dendrite_compartments might be > 1.
                # If scalar fails, we use [dendrite_diameter]*(n+1).
                dend_diam_arg = np.array([dendrite_diameter/b2.um] * (dendrite_compartments + 1)) * b2.um

            # Array lengths for strict Brian2 compliance
            dend_len_seg = dendrite_length / dendrite_compartments
            dend_len_arg = np.array([dend_len_seg/b2.um] * dendrite_compartments) * b2.um

            # Use parent attribute assignment
            dendrite = Section(
                n=dendrite_compartments, length=dend_len_arg, diameter=dend_diam_arg
            )
            dendrite.parent = morphology
            # No append needed

        # Add axon
        if axon_enabled:
            # Axon usually constant diameter
            axon_diam_arg = np.array([axon_diameter/b2.um] * (axon_compartments + 1)) * b2.um
            axon_len_seg = axon_length / axon_compartments
            axon_len_arg = np.array([axon_len_seg/b2.um] * axon_compartments) * b2.um
            
            # Use parent attribute assignment
            axon = Section(n=axon_compartments, length=axon_len_arg, diameter=axon_diam_arg)
            axon.parent = morphology
            # No append needed


        return morphology

    def _get_ion_channel_equations(self, params):
        """Get ion channel equations for multi-compartment model."""
        channel_type = params.get("channel_type", "passive")

        if channel_type == "passive":
            return """
            Im = gL * (v - EL) - I : amp/meter**2
            I : amp/meter**2
            gL : siemens/meter**2
            EL : volt
            """

        elif channel_type == "hh":
            return """
            Im = gNa*m**3*h*(v-ENa) + gK*n**4*(v-EK) + gH*r*(v-Eh) + gL*(v-EL) - I : amp/meter**2
            dm/dt = alpham*(1-m) - betam*m : 1
            dn/dt = alphan*(1-n) - betan*n : 1
            dh/dt = alphah*(1-h) - betah*h : 1
            dr/dt = (r_inf - r) / tau_r : 1
            alpham = 0.1*(v/mV+40)/(1-exp(-(v/mV+40)/10))/ms : Hz
            betam = 4*exp(-(v/mV+65)/18)/ms : Hz
            alphah = 0.07*exp(-(v/mV+65)/20)/ms : Hz
            betah = 1/(1+exp(-(v/mV+35)/10))/ms : Hz
            alphan = 0.01*(v/mV+55)/(1-exp(-(v/mV+55)/10))/ms : Hz
            betan = 0.125*exp(-(v/mV+65)/80)/ms : Hz
            r_inf = 1/(1+exp((v/mV + 80)/10)) : 1
            tau_r = 100*ms : second
            I : amp/meter**2
            gNa : siemens/meter**2
            gK : siemens/meter**2
            gH : siemens/meter**2
            gL : siemens/meter**2
            ENa : volt
            EK : volt
            Eh : volt
            EL : volt
            """

        elif channel_type == "hh_with_a":
            # HH with A-type potassium current
            return """
            Im = gNa*m**3*h*(v-ENa) + gK*n**4*(v-EK) + gA*a**4*b*(v-EK) + gH*r*(v-Eh) + gL*(v-EL) - I : amp/meter**2
            dm/dt = alpham*(1-m) - betam*m : 1
            dn/dt = alphan*(1-n) - betan*n : 1
            dh/dt = alphah*(1-h) - betah*h : 1
            da/dt = (a_inf - a) / tau_a : 1
            db/dt = (b_inf - b) / tau_b : 1
            dr/dt = (r_inf - r) / tau_r : 1
            alpham = 0.1*(v/mV+40)/(1-exp(-(v/mV+40)/10))/ms : Hz
            betam = 4*exp(-(v/mV+65)/18)/ms : Hz
            alphah = 0.07*exp(-(v/mV+65)/20)/ms : Hz
            betah = 1/(1+exp(-(v/mV+35)/10))/ms : Hz
            alphan = 0.01*(v/mV+55)/(1-exp(-(v/mV+55)/10))/ms : Hz
            betan = 0.125*exp(-(v/mV+65)/80)/ms : Hz
            a_inf = 1/(1+exp(-(v/mV+30)/8.5)) : 1
            b_inf = 1/(1+exp((v/mV+80)/6)) : 1
            r_inf = 1/(1+exp((v/mV + 80)/10)) : 1
            tau_a = 5*ms : second
            tau_b = 50*ms : second
            tau_r = 100*ms : second
            I : amp/meter**2
            gNa : siemens/meter**2
            gK : siemens/meter**2
            gA : siemens/meter**2
            gH : siemens/meter**2
            gL : siemens/meter**2
            ENa : volt
            EK : volt
            Eh : volt
            EL : volt
            """

        else:
            # Default passive
            return """
            Im = gL * (v - EL) - I : amp/meter**2
            I : amp/meter**2
            gL : siemens/meter**2
            EL : volt
            """

    def _set_compartment_properties(self, neurons, params):
        """Set membrane properties for different compartments."""
        # Default channel densities (conductances)
        # Try to derive from Rm if available, otherwise use defaults
        
        # SOMA
        if "gL_soma" in params:
             gL_soma = params["gL_soma"] * b2.mS / b2.cm**2
        elif "soma_rm" in params:
             # Rm is in Ohm*cm^2 -> gL = 1/Rm (S/cm^2)
             gL_soma = (1.0 / (params["soma_rm"] * b2.ohm * b2.cm**2))
        else:
             gL_soma = 0.03 * b2.mS / b2.cm**2

        # DENDRITE
        if "gL_dend" in params:
             gL_dend = params["gL_dend"] * b2.mS / b2.cm**2
        elif "dendrite_rm" in params:
             gL_dend = (1.0 / (params["dendrite_rm"] * b2.ohm * b2.cm**2))
        else:
             gL_dend = 0.02 * b2.mS / b2.cm**2

        # AXON
        if "gL_axon" in params:
             gL_axon = params["gL_axon"] * b2.mS / b2.cm**2
        elif "axon_rm" in params:
             gL_axon = (1.0 / (params["axon_rm"] * b2.ohm * b2.cm**2))
        else:
             gL_axon = 0.05 * b2.mS / b2.cm**2

        EL = params.get("EL", -70.0) * b2.mV
        
        # Capacitance
        soma_cm = params.get("soma_cm", 1.0) * b2.uF / b2.cm**2
        dend_cm = params.get("dendrite_cm", 1.0) * b2.uF / b2.cm**2
        axon_cm = params.get("axon_cm", 1.0) * b2.uF / b2.cm**2
        
        # Axial Resistance
        soma_ra = params.get("soma_ra", 150.0) * b2.ohm * b2.cm
        dend_ra = params.get("dendrite_ra", 150.0) * b2.ohm * b2.cm
        axon_ra = params.get("axon_ra", 150.0) * b2.ohm * b2.cm

        # Set leak conductance based on compartment type
        try:
            # Soma (first section)
            neurons.gL[0] = gL_soma
            neurons.EL[0] = EL
            neurons.Cm[0] = soma_cm
            neurons.Ri[0] = soma_ra

            # Dendrites and axon
            num_dendrites = params.get("num_dendrites", 4)
            dendrite_compartments = params.get("dendrite_compartments", 10)

            for i in range(1, 1 + num_dendrites * dendrite_compartments):
                if i < len(neurons.gL):
                    neurons.gL[i] = gL_dend
                    neurons.EL[i] = EL
                    neurons.Cm[i] = dend_cm
                    neurons.Ri[i] = dend_ra

            # Axon (remaining compartments)
            axon_start = 1 + num_dendrites * dendrite_compartments
            for i in range(axon_start, len(neurons.gL)):
                neurons.gL[i] = gL_axon
                neurons.EL[i] = EL
                neurons.Cm[i] = axon_cm
                neurons.Ri[i] = axon_ra

            # If HH channels, set Na/K conductances
            if params.get("channel_type") in ["hh", "hh_with_a"]:
                # Higher Na density in axon initial segment
                gNa_soma = params.get("soma_nav_density", params.get("gNa_soma", 120.0)) * b2.mS / b2.cm**2
                gNa_dend = params.get("dendrite_nav_density", 10.0) * b2.mS / b2.cm**2
                gNa_axon = params.get("ais_nav_density", params.get("gNa_axon", 500.0)) * b2.mS / b2.cm**2  # AIS
                
                gK_soma = params.get("soma_kv_density", params.get("gK_soma", 36.0)) * b2.mS / b2.cm**2
                gK_dend = params.get("dendrite_kv_density", 5.0) * b2.mS / b2.cm**2
                gK_axon = params.get("ais_kv_density", params.get("gK_axon", 100.0)) * b2.mS / b2.cm**2
                
                gH_dend = params.get("dendrite_h_density", 0.1) * b2.mS / b2.cm**2
                gCa_dend = params.get("dendrite_ca_density", 0.5) * b2.mS / b2.cm**2

                neurons.gNa[0] = gNa_soma
                neurons.gK[0] = gK_soma
                neurons.gH[0] = 0 * b2.mS / b2.cm**2  # No Ih in soma by default
                neurons.ENa = params.get("ENa", 50.0) * b2.mV
                neurons.EK = params.get("EK", -77.0) * b2.mV
                neurons.Eh = -43.0 * b2.mV

                # Set Dendrites
                num_dendrites = params.get("num_dendrites", 4)
                dendrite_compartments = params.get("dendrite_compartments", 10)
                dend_end = 1 + num_dendrites * dendrite_compartments
                
                for i in range(1, dend_end):
                     if i < len(neurons.gNa):
                         neurons.gNa[i] = gNa_dend
                         neurons.gK[i] = gK_dend
                         neurons.gH[i] = gH_dend
                         if hasattr(neurons, "g_Ca_L"):
                             neurons.g_Ca_L[i] = gCa_dend

                for i in range(axon_start, min(axon_start + 5, len(neurons.gNa))):
                    neurons.gNa[i] = gNa_axon
                    neurons.gK[i] = gK_axon
                    neurons.gH[i] = 0 * b2.nsiemens / b2.cm**2

        except (AttributeError, IndexError) as e:
            import traceback
            traceback.print_exc()
            print(f"Note: Could not set all compartment properties: {e}")

    def _set_calcium_properties(self, neurons, params):
        """Initialize calcium state variables."""
        try:
            if hasattr(neurons, "Ca_rest"):
                neurons.Ca_rest = params.get("ca_rest", 0.0001) * b2.mM
                neurons.Ca = neurons.Ca_rest
                
            if hasattr(neurons, "tau_Ca"):
                 rate = params.get("ca_extrusion_rate", 0.1) # /ms
                 if rate > 0:
                     neurons.tau_Ca = (1.0 / rate) * b2.ms
                 else:
                     neurons.tau_Ca = 1000 * b2.ms

            if hasattr(neurons, "kappa"):
                 neurons.kappa = params.get("buffer_capacity", 20.0)

            if hasattr(neurons, "diff_rate"):
                 neurons.diff_rate = params.get("diffusion_constant", 0.0) * b2.Hz

            if hasattr(neurons, "Ca_scaling"):
                 # Conversion from current to concentration change
                 # Depends on Shell depth. Placeholder constant for stability.
                 neurons.Ca_scaling = 5000.0 * b2.mM / b2.amp 

            if hasattr(neurons, "E_Ca"):
                 neurons.E_Ca = 120 * b2.mV

            # Buffer Kinetics initialization
            if hasattr(neurons, "Ca_bound"):
                 neurons.B_total = params.get("buffer_total", 0.5) * b2.mM
                 neurons.k_on = params.get("buffer_k_on", 100.0) / (b2.mM * b2.ms) # Fast binding
                 neurons.k_off = params.get("buffer_k_off", 1.0) / b2.ms
                 # Steady state approximation for initial bound freq
                 # Kd = k_off / k_on. Bound = B_total * Ca / (Ca + Kd)
                 Kd = neurons.k_off / neurons.k_on
                 neurons.Ca_bound = neurons.B_total * neurons.Ca / (neurons.Ca + Kd)
                 
        except Exception as e:
            print(f"Note: Error setting calcium properties: {e}")


    def _build_point_neuron_fallback(self, num_neurons, multicomp_params, neuron_params):
        """Fallback to point neuron if spatial extension not available."""
        channel_type = multicomp_params.get("channel_type", "passive")

        if channel_type == "passive":
            eqs = """
            dv/dt = (gL*(EL - v) + I) / Cm : volt
            I : amp
            """
            neurons = b2.NeuronGroup(
                num_neurons,
                eqs,
                threshold="v > -50*mV",
                reset="v = -70*mV",
                method="euler",
                namespace={"Cm": 100 * b2.pF, "gL": 10 * b2.nS, "EL": -70 * b2.mV},
            )
        else:
            # HH fallback
            eqs = """
            dv/dt = (I - gNa*m**3*h*(v-ENa) - gK*n**4*(v-EK) - gL*(v-EL)) / Cm : volt
            dm/dt = alpham*(1-m) - betam*m : 1
            dn/dt = alphan*(1-n) - betan*n : 1
            dh/dt = alphah*(1-h) - betah*h : 1
            alpham = 0.1*(v/mV+40)/(1-exp(-(v/mV+40)/10))/ms : Hz
            betam = 4*exp(-(v/mV+65)/18)/ms : Hz
            alphah = 0.07*exp(-(v/mV+65)/20)/ms : Hz
            betah = 1/(1+exp(-(v/mV+35)/10))/ms : Hz
            alphan = 0.01*(v/mV+55)/(1-exp(-(v/mV+55)/10))/ms : Hz
            betan = 0.125*exp(-(v/mV+65)/80)/ms : Hz
            I : amp
            """
            neurons = b2.NeuronGroup(
                num_neurons,
                eqs,
                threshold="v > -20*mV",
                refractory=3 * b2.ms,
                method="exponential_euler",
                namespace={
                    "Cm": params.get("Cm", 1.0) * b2.uF,
                    "gNa": params.get("gNa", 120.0) * b2.mS,
                    "gK": params.get("gK", 36.0) * b2.mS,
                    "gL": params.get("gL", 0.3) * b2.mS,
                    "ENa": params.get("ENa", 50.0) * b2.mV,
                    "EK": params.get("EK", -77.0) * b2.mV,
                    "EL": params.get("EL", -54.4) * b2.mV,
                },
            )
            neurons.v = params.get("v_init", -65.0) * b2.mV
            neurons.m = 0.05
            neurons.h = 0.6
            neurons.n = 0.32

        self.neurons = neurons
        return neurons

    def _get_calcium_equations(self, ca_params):
        """Get calcium dynamics equations based on config parameters.
        
        Implements intracellular calcium dynamics with:
        - Voltage-gated calcium channels (L-type, N-type)
        - NMDA-mediated calcium influx
        - Calcium buffering
        - Calcium extrusion (pumps)
        
        Parameters from config:
        - ca_sources: voltage_only, nmda_only, voltage_nmda, vgcc_nmda
        - ca_rest: Resting calcium concentration (μM)
        - ca_extrusion_rate: Extrusion time constant (/ms)
        - buffer_capacity: Buffering capacity (dimensionless)
        - ltype_conductance, ntype_conductance: Channel conductances (nS)
        """
        ca_source = ca_params.get("ca_sources", "voltage_only")
        use_ltype = ca_params.get("ltype_channels", False) or "voltage" in ca_source or "vgcc" in ca_source
        use_ntype = ca_params.get("ntype_channels", False) or "voltage" in ca_source or "vgcc" in ca_source
        use_diff = ca_params.get("ca_diffusion", False)
        
        # Base calcium equation with extrusion and optional diffusion
        # dCa/dt = influx - extrusion + diffusion
        # Diffusion modeled as simplified radial loss/gain to bulk: + diff_rate * (Ca_rest - Ca)
        # Allows controlling "leakiness" via diffusion constant.
        
        diff_term = "+ diff_rate * (Ca_rest - Ca)" if use_diff else ""
        
        # Check buffer mode (default 'instant' if not specified)
        buffer_mode = ca_params.get("buffer_mode", "instant")
        use_kinetics = (buffer_mode == "kinetic") or ca_params.get("buffer_kinetics", False) is True
        
        if use_kinetics:
            # Explicit buffer kinetics
            # dCa/dt = ... + (k_off * Ca_bound - k_on * Ca * (B_total - Ca_bound))
            # dCa_bound/dt = k_on * Ca * (B_total - Ca_bound) - k_off * Ca_bound
            buff_term = "+ (k_off * Ca_bound - k_on * Ca * (B_total - Ca_bound))"
            
            eqs = f"""
            dCa/dt = (I_Ca_total * Ca_scaling - (Ca - Ca_rest) / tau_Ca {diff_term} {buff_term}) : mmolar
            dCa_bound/dt = k_on * Ca * (B_total - Ca_bound) - k_off * Ca_bound : mmolar
            Ca_scaling : mmolar/amp
            tau_Ca : second
            Ca_rest : mmolar
            diff_rate : Hz
            k_on : 1/mmolar/second
            k_off : Hz
            B_total : mmolar
            """
        else:
            # Fast buffering approximation (kappa)
            eqs = f"""
            dCa/dt = (I_Ca_total * Ca_scaling - (Ca - Ca_rest) / tau_Ca {diff_term}) / kappa : mmolar
            Ca_scaling : mmolar/amp
            tau_Ca : second
            Ca_rest : mmolar
            kappa : 1
            diff_rate : Hz
            """
        
        # Add calcium current sources
        if use_ltype or use_ntype:
            eqs += """
            I_Ca_vgcc = I_Ca_L + I_Ca_N : amp
            E_Ca : volt
            """
            
            if use_ltype:
                eqs += """
                I_Ca_L = g_Ca_L * m_Ca_L_inf * (v - E_Ca) : amp
                m_Ca_L_inf = 1.0 / (1.0 + exp(-(v/mV + 20.0) / 10.0)) : 1
                g_Ca_L : siemens
                """
            else:
                eqs += "I_Ca_L = 0*amp : amp\n"

            if use_ntype:
                eqs += """
                I_Ca_N = g_Ca_N * m_Ca_N_inf * h_Ca_N_inf * (v - E_Ca) : amp
                m_Ca_N_inf = 1.0 / (1.0 + exp(-(v/mV + 20.0) / 10.0)) : 1
                h_Ca_N_inf = 1.0 / (1.0 + exp((v/mV + 40.0) / 5.0)) : 1
                g_Ca_N : siemens
                """
            else:
                eqs += "I_Ca_N = 0*amp : amp\n"
        else:
            eqs += """
            I_Ca_vgcc = 0*amp : amp
            """
            
        if "nmda" in ca_source or "nmda" in ca_params.get("ca_sources", ""):
            # NMDA-mediated calcium influx
            # I_Ca_nmda = fraction * I_nmda_total
            # I_nmda_total must be summed from synapses
            eqs += """
            I_Ca_nmda = nmda_ca_fraction * I_nmda_total : amp
            I_nmda_total : amp  # Summed from NMDA synapses
            nmda_ca_fraction : 1
            """
        else:
            eqs += """
            I_Ca_nmda = 0*amp : amp
            """
        
        # Total calcium current
        eqs += """
        I_Ca_total = I_Ca_vgcc + I_Ca_nmda : amp
        """
        
        return eqs

    def _initialize_calcium(self, neurons, ca_params):
        """Initialize calcium variables from config parameters."""
        # Resting calcium concentration: config is in μM, Brian2 uses mmolar (= mM)
        # 0.1 μM = 0.0001 mM = 100 nM
        ca_rest_um = ca_params.get("ca_rest", 0.1)  # μM
        ca_rest_mm = ca_rest_um * 1e-3  # Convert to mM
        
        # Extrusion rate to time constant
        extrusion_rate = ca_params.get("ca_extrusion_rate", 0.1)  # /ms
        tau_ca = (1.0 / extrusion_rate) * b2.ms if extrusion_rate > 0 else 100 * b2.ms
        
        # Buffer capacity
        kappa = ca_params.get("buffer_capacity", 200.0) if ca_params.get("ca_buffer_enabled", True) else 1.0
        
        # Calcium current to concentration scaling
        # This is a simplified scaling factor - in detailed models this would 
        # depend on cell volume and Faraday's constant
        # For a typical cell: ~1 pA for 1 ms raises [Ca] by ~0.01 μM
        ca_scaling = 0.01 * b2.mmolar / b2.pA  # Simplified
        
        # Set neuron variables
        neurons.Ca = ca_rest_mm * b2.mmolar
        neurons.Ca_rest = ca_rest_mm * b2.mmolar
        neurons.tau_Ca = tau_ca
        if hasattr(neurons, "kappa"):
            neurons.kappa = kappa
        neurons.Ca_scaling = ca_scaling
        
        # Set voltage-gated calcium channel parameters if present
        ca_source = ca_params.get("ca_sources", "voltage_only")
        if ca_source in ["voltage_only", "voltage_nmda", "vgcc_nmda"]:
            e_ca = ca_params.get("e_ca", 120.0) * b2.mV
            if hasattr(neurons, "E_Ca"):
                neurons.E_Ca = e_ca
                
            if hasattr(neurons, "g_Ca_L"):
                g_ca_l = ca_params.get("ltype_conductance", 5.0) * b2.nS
                neurons.g_Ca_L = g_ca_l
                
            if hasattr(neurons, "g_Ca_N"):
                g_ca_n = ca_params.get("ntype_conductance", 2.0) * b2.nS
                neurons.g_Ca_N = g_ca_n
        
        # NMDA calcium current
        if hasattr(neurons, "nmda_ca_fraction"):
            neurons.nmda_ca_fraction = ca_params.get("nmda_ca_fraction", 0.1)
            neurons.I_nmda_total = 0 * b2.amp # Initialize logic
        elif hasattr(neurons, "I_Ca_nmda"):
             neurons.I_Ca_nmda = 0 * b2.amp
