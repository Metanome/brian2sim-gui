# Brian2Sim GUI - Test Suite

Comprehensive test suite for the Brian2Sim neural network simulator GUI application.

## Test Coverage Overview

**Total Tests: ~320** with full pass rate
- Complete coverage of all builders, managers, and orchestration components
- Integration tests for end-to-end workflows
- Comprehensive parameter validation and error handling
- Property-based testing for edge cases

## Test Structure

### Core Builder Tests (~65 tests)

#### test_neuron_builder.py (~23 tests)
- LIF, Izhikevich, AdEx neurons
- **Hodgkin-Huxley neurons** (gating variables, conductance)
- Calcium dynamics integration
- Multicompartment neuron support
- Edge cases and error handling

#### test_synapse_builder.py (~25 tests)
- Random, all-to-all, small-world, scale-free topologies
- STDP (Spike-Timing-Dependent Plasticity)
- Short-term plasticity (STP)
- **AMPA, NMDA, GABA_A, GABA_B receptors**
- Gap junctions
- **Distance-dependent connectivity**

#### test_plasticity_builder.py (~27 tests)
- Neuromodulation (dopamine, **serotonin**, acetylcholine, **noradrenaline**)
- **Pharmacology** (agonists, antagonists, blockers)
- **Neuromodulator release patterns** (tonic, phasic)
- Homeostatic plasticity, **BCM**, **Metaplasticity**
- **Threshold adaptation**

#### test_input_builder.py (11 tests)
- Input current (LIF, Izhikevich, AdEx, HH models)
- Gaussian/Ornstein-Uhlenbeck noise
- Poisson spike train inputs
- Burst and rhythmic stimulation

#### test_monitor_builder.py (12 tests)
- Spike, state, and weight monitors
- Results collection and formatting
- Custom variable monitoring

### Integration Tests (18 tests)

#### test_simulation_integration.py
- Complete simulation pipelines
- Complex network configurations
- Multi-feature integration
- Error propagation and handling

### Manager & Orchestration Tests (~75 tests)

#### test_simulation_manager.py (13 tests)
- SimulationManager orchestration and lifecycle

#### test_config_manager_full.py (14 tests)
- Configuration save/load and validation

#### test_results_manager_full.py (17 tests)
- Plot generation, statistics, export

#### test_feature_managers.py (28 tests)
- All 13+ UI managers

### NEW: Validation Tests (~89 tests)

#### test_cross_tab_dependencies.py (17 tests)
- CrossTabDependencyManager coupling rules
- NMDA→Calcium, Calcium→Plasticity, Receptor→STP coupling
- Configuration validation and warnings

#### test_parameter_validation.py (27 tests)
- ValidationResult class
- ParameterValidator range rules (voltage, tau, probability)
- Cross-parameter rules (NMDA, calcium, network consistency)
- ValidationManager integration

#### test_validation_integration.py (13 tests)
- Full validation chain (CrossTab → Validator → Manager)
- Neuroscientific validation rules
- Signal emission and error handling

#### test_parameter_combinations.py (49 tests)
- **Property-based testing** with hypothesis
- Boundary condition fuzzing
- Random parameter combinations
- Model + feature matrix testing

### NEW: Config & UI Tests (~90 tests)

#### test_config_models.py (35 tests)
- All 14 config files (neuron, network, calcium, neuromodulation, etc.)
- Parameter schema validation
- Preset value validation

#### test_ui_components.py (19 tests)
- BaseFormGenerator, SimParamsFormGenerator
- TabFactory, FilePickerWidget
- MainWindow, MenuBar imports

### Core Utilities Tests (17 tests)

#### test_managers.py (8 tests)
#### test_core_utilities.py (9 tests)

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_neuron_builder.py -v

# Run tests by pattern
pytest tests/ -k "validation" -v

# Run with coverage report
pytest tests/ --cov=brian2sim --cov-report=html

# Run property-based tests only
pytest tests/test_parameter_combinations.py -v
```

## Test Fixtures (conftest.py)

Shared fixtures:
- `default_sim_params`, `default_neuron_params`
- `izh_neuron_params`, `network_params`
- `stdp_params`, `neuromodulation_params`
- `homeostatic_params`, `calcium_params`

## Features Tested

**Neuron Models**: LIF, Izhikevich, AdEx, Hodgkin-Huxley, Calcium dynamics, Multicompartment
**Network Topologies**: Random, All-to-all, Small-world, Scale-free, Distance-dependent
**Receptors**: AMPA, NMDA, GABA_A, GABA_B
**Plasticity**: STDP, STP, BCM, Metaplasticity, Neuromodulation (4 transmitters), Homeostatic
**Validation**: Range rules, cross-parameter rules, neuroscientific consistency
**Input Patterns**: Current injection, noise, Poisson, burst, rhythmic
**Monitoring**: Spikes, voltage, synaptic weights
**UI**: All managers, form generators, config models

## Dependencies

- pytest 9.0.2
- pytest-qt 4.5.0
- pytest-cov 7.0.0
- **hypothesis 6.148.8** (property-based testing)
- Brian2 2.5+
- PyQt6 6.10.1
- Python 3.13.11

## Contributing

1. Follow existing test structure and naming conventions
2. Add reusable fixtures to conftest.py
3. Document complex test logic with docstrings
4. Use mocks for UI dependencies
5. Test both success and failure paths
6. Run full test suite before committing
