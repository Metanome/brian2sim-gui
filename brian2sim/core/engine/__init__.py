"""
Simulation engine subpackage with modular builders.

This package provides focused builder classes for constructing different
components of a Brian2 neural network simulation.
"""

from brian2sim.core.engine.input_builder import InputBuilder
from brian2sim.core.engine.monitor_builder import MonitorBuilder
from brian2sim.core.engine.neuron_builder import NeuronBuilder
from brian2sim.core.engine.plasticity_builder import PlasticityBuilder
from brian2sim.core.engine.synapse_builder import SynapseBuilder

__all__ = [
    "NeuronBuilder",
    "InputBuilder",
    "SynapseBuilder",
    "PlasticityBuilder",
    "MonitorBuilder",
]
