"""
Neuron Builder for Brian2 simulations.
Handles construction of point neurons and multi-compartment neuron models.
"""

try:
    import brian2 as b2

    BRIAN2_AVAILABLE = True
except ImportError:
    BRIAN2_AVAILABLE = False


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
        model_type = neuron_params.get("model_type", "lif")

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
            self.neurons = self._build_adex_neurons(num_neurons, neuron_params)
        elif model_type == "hodgkin_huxley":
            self.neurons = self._build_hh_neurons(num_neurons, neuron_params)
        else:
            self.neurons = self._build_default_neurons(num_neurons)

        return self.neurons

    def _build_lif_neurons(
        self, num_neurons, sim_params, neuron_params, ca_enabled, calcium_params
    ):
        """Build Leaky Integrate-and-Fire neurons."""
        tau = neuron_params.get("tau", 10.0) * b2.ms
        v_rest = neuron_params.get("v_rest", -70.0) * b2.mV
        v_threshold = neuron_params.get("v_threshold", -50.0) * b2.mV
        v_reset = neuron_params.get("v_reset", -70.0) * b2.mV

        eqs = """
        dv/dt = (v_rest - v + I*R) / tau : volt
        I : amp
        R : ohm
        """

        if ca_enabled and calcium_params:
            ca_eqs = self._get_calcium_equations(calcium_params)
            eqs = eqs + ca_eqs

        neurons = b2.NeuronGroup(
            num_neurons,
            eqs,
            threshold="v > v_threshold",
            reset="v = v_reset",
            method="euler",
            namespace={
                "tau": tau,
                "v_rest": v_rest,
                "v_threshold": v_threshold,
                "v_reset": v_reset,
            },
        )

        neurons.v = v_rest
        neurons.R = 100 * b2.Mohm

        if ca_enabled and calcium_params:
            self._initialize_calcium(neurons, calcium_params)

        return neurons

    def _build_izhikevich_neurons(self, num_neurons, neuron_params):
        """Build Izhikevich neurons."""
        a = neuron_params.get("a", 0.02)
        b_param = neuron_params.get("b", 0.2)
        c = neuron_params.get("c", -65.0)
        d = neuron_params.get("d", 8.0)

        eqs = """
        dv/dt = (0.04*v**2/mV + 5*v + 140*mV - u + I*Mohm) / ms : volt
        du/dt = a * (b * v - u) / ms : volt
        I : amp
        """

        neurons = b2.NeuronGroup(
            num_neurons,
            eqs,
            threshold="v > 30*mV",
            reset="v = c*mV; u += d*mV",
            method="euler",
            namespace={"a": a, "b": b_param, "c": c, "d": d},
        )

        neurons.v = c * b2.mV
        neurons.u = b_param * c * b2.mV

        return neurons

    def _build_adex_neurons(self, num_neurons, neuron_params):
        """Build Adaptive Exponential Integrate-and-Fire neurons."""
        C = neuron_params.get("C", 281.0) * b2.pF
        gL = neuron_params.get("gL", 30.0) * b2.nS
        EL = neuron_params.get("EL", -70.6) * b2.mV
        VT = neuron_params.get("VT", -50.4) * b2.mV
        DeltaT = neuron_params.get("DeltaT", 2.0) * b2.mV
        Vcut = neuron_params.get("Vcut", -40.0) * b2.mV
        tauw = neuron_params.get("tauw", 144.0) * b2.ms
        a = neuron_params.get("a", 4.0) * b2.nS
        b_param = neuron_params.get("b", 0.0805) * b2.nA
        Vreset = neuron_params.get("Vreset", -70.6) * b2.mV

        eqs = """
        dv/dt = (gL*(EL - v) + gL*DeltaT*exp((v - VT)/DeltaT) + I - w) / C : volt
        dw/dt = (a*(v - EL) - w) / tauw : amp
        I : amp
        """

        neurons = b2.NeuronGroup(
            num_neurons,
            eqs,
            threshold="v > Vcut",
            reset="v = Vreset; w += b",
            method="euler",
            namespace={
                "C": C,
                "gL": gL,
                "EL": EL,
                "VT": VT,
                "DeltaT": DeltaT,
                "Vcut": Vcut,
                "tauw": tauw,
                "a": a,
                "b": b_param,
                "Vreset": Vreset,
            },
        )

        neurons.v = EL
        neurons.w = 0 * b2.pA

        return neurons

    def _build_hh_neurons(self, num_neurons, neuron_params):
        """Build Hodgkin-Huxley neurons."""
        Cm = neuron_params.get("Cm", 1.0) * b2.uF
        gNa = neuron_params.get("gNa", 120.0) * b2.mS
        gK = neuron_params.get("gK", 36.0) * b2.mS
        gL = neuron_params.get("gL", 0.3) * b2.mS
        ENa = neuron_params.get("ENa", 50.0) * b2.mV
        EK = neuron_params.get("EK", -77.0) * b2.mV
        EL = neuron_params.get("EL", -54.4) * b2.mV

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
            namespace={"Cm": Cm, "gNa": gNa, "gK": gK, "gL": gL, "ENa": ENa, "EK": EK, "EL": EL},
        )

        neurons.v = -65 * b2.mV
        neurons.m = 0.05
        neurons.h = 0.6
        neurons.n = 0.32

        return neurons

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
        dendrite_length = params.get("dendrite_length", 200.0) * b2.um
        dendrite_diameter = params.get("dendrite_diameter", 2.0) * b2.um
        dendrite_compartments = params.get("dendrite_compartments", 10)

        # Axon parameters
        axon_enabled = params.get("axon_enabled", True)
        axon_length = params.get("axon_length", 500.0) * b2.um
        axon_diameter = params.get("axon_diameter", 1.0) * b2.um
        axon_compartments = params.get("axon_compartments", 20)

        # Build morphology
        morphology = Section(n=1, length=soma_length, diameter=soma_diameter)

        # Add dendrites
        for i in range(num_dendrites):
            dendrite = Section(
                n=dendrite_compartments, length=dendrite_length, diameter=dendrite_diameter
            )
            morphology.append(dendrite)

        # Add axon
        if axon_enabled:
            axon = Section(n=axon_compartments, length=axon_length, diameter=axon_diameter)
            morphology.append(axon)

        return morphology

    def _get_ion_channel_equations(self, params):
        """Get ion channel equations for multi-compartment model."""
        channel_type = params.get("channel_type", "passive")

        if channel_type == "passive":
            return """
            dv/dt = (gL * (EL - v) + I) / Cm : volt
            I : amp/meter**2
            gL : siemens/meter**2
            EL : volt
            """

        elif channel_type == "hh":
            return """
            dv/dt = (gNa*m**3*h*(ENa-v) + gK*n**4*(EK-v) + gL*(EL-v) + I) / Cm : volt
            dm/dt = alpham*(1-m) - betam*m : 1
            dn/dt = alphan*(1-n) - betan*n : 1
            dh/dt = alphah*(1-h) - betah*h : 1
            alpham = 0.1*(v/mV+40)/(1-exp(-(v/mV+40)/10))/ms : Hz
            betam = 4*exp(-(v/mV+65)/18)/ms : Hz
            alphah = 0.07*exp(-(v/mV+65)/20)/ms : Hz
            betah = 1/(1+exp(-(v/mV+35)/10))/ms : Hz
            alphan = 0.01*(v/mV+55)/(1-exp(-(v/mV+55)/10))/ms : Hz
            betan = 0.125*exp(-(v/mV+65)/80)/ms : Hz
            I : amp/meter**2
            gNa : siemens/meter**2
            gK : siemens/meter**2
            gL : siemens/meter**2
            ENa : volt
            EK : volt
            EL : volt
            """

        elif channel_type == "hh_with_a":
            # HH with A-type potassium current
            return """
            dv/dt = (gNa*m**3*h*(ENa-v) + gK*n**4*(EK-v) + gA*a**4*b*(EK-v) + gL*(EL-v) + I) / Cm : volt
            dm/dt = alpham*(1-m) - betam*m : 1
            dn/dt = alphan*(1-n) - betan*n : 1
            dh/dt = alphah*(1-h) - betah*h : 1
            da/dt = (a_inf - a) / tau_a : 1
            db/dt = (b_inf - b) / tau_b : 1
            alpham = 0.1*(v/mV+40)/(1-exp(-(v/mV+40)/10))/ms : Hz
            betam = 4*exp(-(v/mV+65)/18)/ms : Hz
            alphah = 0.07*exp(-(v/mV+65)/20)/ms : Hz
            betah = 1/(1+exp(-(v/mV+35)/10))/ms : Hz
            alphan = 0.01*(v/mV+55)/(1-exp(-(v/mV+55)/10))/ms : Hz
            betan = 0.125*exp(-(v/mV+65)/80)/ms : Hz
            a_inf = 1/(1+exp(-(v/mV+30)/8.5)) : 1
            b_inf = 1/(1+exp((v/mV+80)/6)) : 1
            tau_a = 5*ms : second
            tau_b = 50*ms : second
            I : amp/meter**2
            gNa : siemens/meter**2
            gK : siemens/meter**2
            gA : siemens/meter**2
            gL : siemens/meter**2
            ENa : volt
            EK : volt
            EL : volt
            """

        else:
            # Default passive
            return """
            dv/dt = (gL * (EL - v) + I) / Cm : volt
            I : amp/meter**2
            gL : siemens/meter**2
            EL : volt
            """

    def _set_compartment_properties(self, neurons, params):
        """Set membrane properties for different compartments."""
        # Default channel densities
        gL_soma = params.get("gL_soma", 0.03) * b2.mS / b2.cm**2
        gL_dend = params.get("gL_dend", 0.02) * b2.mS / b2.cm**2
        gL_axon = params.get("gL_axon", 0.05) * b2.mS / b2.cm**2

        EL = params.get("EL", -70.0) * b2.mV

        # Set leak conductance based on compartment type
        try:
            # Soma (first section)
            neurons.gL[0] = gL_soma
            neurons.EL[0] = EL

            # Dendrites and axon
            num_dendrites = params.get("num_dendrites", 4)
            dendrite_compartments = params.get("dendrite_compartments", 10)

            for i in range(1, 1 + num_dendrites * dendrite_compartments):
                if i < len(neurons.gL):
                    neurons.gL[i] = gL_dend
                    neurons.EL[i] = EL

            # Axon (remaining compartments)
            axon_start = 1 + num_dendrites * dendrite_compartments
            for i in range(axon_start, len(neurons.gL)):
                neurons.gL[i] = gL_axon
                neurons.EL[i] = EL

            # If HH channels, set Na/K conductances
            if params.get("channel_type") in ["hh", "hh_with_a"]:
                # Higher Na density in axon initial segment
                gNa_soma = params.get("gNa_soma", 120.0) * b2.mS / b2.cm**2
                gNa_axon = params.get("gNa_axon", 500.0) * b2.mS / b2.cm**2  # AIS
                gK_soma = params.get("gK_soma", 36.0) * b2.mS / b2.cm**2
                gK_axon = params.get("gK_axon", 100.0) * b2.mS / b2.cm**2

                neurons.gNa[0] = gNa_soma
                neurons.gK[0] = gK_soma
                neurons.ENa = params.get("ENa", 50.0) * b2.mV
                neurons.EK = params.get("EK", -77.0) * b2.mV

                for i in range(axon_start, min(axon_start + 5, len(neurons.gNa))):
                    neurons.gNa[i] = gNa_axon
                    neurons.gK[i] = gK_axon

        except (AttributeError, IndexError) as e:
            print(f"Note: Could not set all compartment properties: {e}")

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
                    "Cm": 1 * b2.uF,
                    "gNa": 120 * b2.mS,
                    "gK": 36 * b2.mS,
                    "gL": 0.3 * b2.mS,
                    "ENa": 50 * b2.mV,
                    "EK": -77 * b2.mV,
                    "EL": -54.4 * b2.mV,
                },
            )
            neurons.v = -65 * b2.mV
            neurons.m = 0.05
            neurons.h = 0.6
            neurons.n = 0.32

        self.neurons = neurons
        return neurons

    def _get_calcium_equations(self, ca_params):
        """Get calcium dynamics equations."""
        ca_model = ca_params.get("model", "single_pool")

        if ca_model == "single_pool":
            return """
            dCa/dt = (-ICa / (2*F*vol) - (Ca - Ca_rest) / tau_Ca) : molar
            ICa = gCa * (v - ECa) : amp
            """
        elif ca_model == "detailed":
            return """
            dCa/dt = (-ICa / (2*F*vol) - (Ca - Ca_rest) / tau_Ca + J_IP3) : molar
            dCa_ER/dt = (-J_IP3 + J_leak) / vol_ER : molar 
            ICa = gCa * (v - ECa) : amp
            J_IP3 : molar/second
            J_leak : molar/second
            """
        else:
            return """
            dCa/dt = (- (Ca - Ca_rest) / tau_Ca) : molar
            """

    def _initialize_calcium(self, neurons, ca_params):
        """Initialize calcium variables."""
        Ca_rest = ca_params.get("Ca_rest", 100e-9)  # 100 nM
        neurons.Ca = Ca_rest * b2.molar

        if hasattr(neurons, "Ca_ER"):
            neurons.Ca_ER = ca_params.get("Ca_ER_rest", 400e-6) * b2.molar
