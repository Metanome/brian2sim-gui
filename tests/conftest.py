"""
Pytest configuration and fixtures for Brian2Sim tests.
"""
import pytest
import brian2 as b2


@pytest.fixture(scope="session", autouse=True)
def setup_brian2():
    """Configure Brian2 for testing."""
    b2.prefs.codegen.target = 'numpy'  # Fast execution for tests
    yield
    # Cleanup between test sessions
    b2.start_scope()


@pytest.fixture
def default_sim_params():
    """Default simulation parameters for testing."""
    return {
        "dt": 0.1,
        "sim_time": 100,
        "num_neurons": 10,
        "v_threshold": -55.0,
        "v_reset": -70.0,
        "input_current": 0.5
    }


@pytest.fixture
def default_neuron_params():
    """Default LIF neuron parameters."""
    return {
        "model_key": "lif",
        "parameters": {
            "tau_m": 20.0,
            "v_rest": -70.0,
            "resistance": 100.0,
            "refractory": 2.0
        }
    }


@pytest.fixture
def izhikevich_params():
    """Izhikevich neuron parameters (regular spiking)."""
    return {
        "model_key": "izhikevich",
        "parameters": {
            "a": 0.02,
            "b": 0.2,
            "c": -65.0,
            "d": 8.0
        }
    }


@pytest.fixture
def adex_params():
    """AdEx neuron parameters."""
    return {
        "model_key": "adex",
        "parameters": {
            "C": 200.0,
            "gL": 10.0,
            "EL": -70.0,
            "VT": -50.0,
            "delT": 2.0,
            "a": 2.0,
            "tauw": 30.0,
            "b": 60.0
        }
    }


@pytest.fixture
def calcium_params():
    """Calcium dynamics parameters."""
    return {
        "enabled": True,
        "ca_sources": "vgcc_nmda",
        "ltype_conductance": 5.0,
        "ntype_conductance": 3.0,
        "nmda_ca_fraction": 0.15,
        "decay_tau": 20.0,
        "buffer_enabled": True
    }


@pytest.fixture
def network_params():
    """Basic network parameters."""
    return {
        "enabled": True,
        "topology": "random",
        "connection_prob": 0.1,
        "synaptic_weight": 0.5
    }


@pytest.fixture
def stdp_params():
    """STDP parameters."""
    return {
        "stdp": {
            "enabled": True,
            "stdp_type": "additive",
            "taupre": 20.0,
            "taupost": 20.0,
            "Apre": 0.01,
            "Apost": -0.012,
            "w_max": 2.0
        }
    }


@pytest.fixture
def receptor_params():
    """Synaptic receptor parameters."""
    return {
        "enabled": True,
        "ampa_enabled": True,
        "nmda_enabled": True,
        "gaba_a_enabled": False,
        "gaba_b_enabled": False
    }


@pytest.fixture
def neuromodulation_params():
    """Neuromodulation parameters."""
    return {
        "enabled": True,
        "acetylcholine_system": True,
        "acetylcholine_baseline": 0.5,
        "acetylcholine_tau": 100.0,
        "muscarinic_effect": 0.15,
        "nicotinic_effect": 0.3
    }


@pytest.fixture
def homeostatic_params():
    """Homeostatic plasticity parameters."""
    return {
        "enabled": True,
        "bcm_plasticity": True,
        "target_rate": 5.0,
        "learning_rate": 0.0001,
        "tau_avg": 1000.0
    }
