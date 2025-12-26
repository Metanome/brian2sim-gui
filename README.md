# Brian2Sim GUI

A graphical user interface for the [Brian2](https://brian2.readthedocs.io/) spiking neural network simulator. This application provides an intuitive way to configure, run, and analyze neural network simulations without writing code.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![Brian2](https://img.shields.io/badge/Brian2-2.5+-orange.svg)

## Features

### Neuron Models
- **Leaky Integrate-and-Fire (LIF)** - Simple threshold-based spiking
- **Izhikevich** - Rich dynamics with different firing patterns
- **Adaptive Exponential (AdEx)** - Brette & Gerstner model with adaptation
- **Hodgkin-Huxley** - Biophysically detailed conductance-based model
- **Custom Equations** - Define your own differential equations

### Network Features
- Multiple topology types: All-to-all, random, small-world, scale-free, modular
- Synaptic plasticity (STDP)
- Dale's principle (excitatory/inhibitory separation)
- Configurable synaptic delays
- Gap junctions (electrical synapses)

### Advanced Features
- **Multi-receptor synapses**: AMPA, NMDA, GABA_A, GABA_B
- **Short-term plasticity**: Facilitation and depression
- **Calcium dynamics**: Multiple calcium models
- **Homeostatic plasticity**: Synaptic scaling, threshold adaptation
- **Neuromodulation**: Dopamine, acetylcholine, serotonin, noradrenaline
- **Multi-compartment neurons**: Soma, dendrites, axon with ion channels

### Input Patterns
- Constant current injection with timing control
- Gaussian and Ornstein-Uhlenbeck noise
- Poisson spike trains
- Rhythmic oscillatory inputs
- Burst stimulation
- Step current protocols

### User Interface
- **Tiered user levels**: Beginner, Intermediate, Advanced
- Real-time simulation progress
- Voltage traces and raster plots
- Configuration save/load (JSON format)
- Python code generation for reproducibility

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/brian2sim-gui.git
cd brian2sim-gui

# Install in development mode
pip install -e .
```

### Install dependencies only

```bash
pip install -r requirements.txt
```

## Usage

### Run the application

```bash
# Using the package entry point
python -m brian2sim

# Or after pip install -e .
brian2sim
```

### Quick Start

1. **Select a neuron model** from the Core tab
2. **Set simulation parameters**: number of neurons, simulation time, input current
3. **Switch to Simulation tab** and click "Run Simulation"
4. **View results**: Raster plots show spike times, voltage traces show membrane potential

### User Levels

Change user level via `User Level` menu:

- **Beginner**: Core and Simulation tabs only
- **Intermediate**: Adds Network and Synapses tabs
- **Advanced**: All features including Plasticity, Neuromodulation, Multi-Compartment

### Saving/Loading Configurations

- **Save**: Click "Save Configuration" to export settings as JSON
- **Load**: Click "Load Configuration" to restore a saved configuration
- **Export Code**: Generate standalone Python script for your simulation

## Project Structure

```
brian2sim-gui/
├── brian2sim/                    # Main package
│   ├── core/                     # Simulation engine
│   │   ├── engine/               # Modular builders
│   │   │   ├── neuron_builder.py
│   │   │   ├── input_builder.py
│   │   │   ├── synapse_builder.py
│   │   │   ├── plasticity_builder.py
│   │   │   └── monitor_builder.py
│   │   ├── simulation_engine.py
│   │   ├── simulation_manager.py
│   │   ├── code_generator.py
│   │   ├── config_manager.py
│   │   └── results_manager.py
│   ├── managers/                 # Business logic
│   ├── models/                   # Configuration definitions
│   └── ui/                       # User interface
│       ├── main_window.py
│       ├── menu_bar.py
│       └── tabs/                 # Tab-specific UI
├── tests/                        # Test directory
├── requirements.txt
├── setup.py
└── README.md
```

## Dependencies

| Package    | Version  | Purpose                  |
| ---------- | -------- | ------------------------ |
| PyQt6      | ≥ 6.4.0  | GUI framework            |
| brian2     | ≥ 2.5.0  | Neural network simulator |
| numpy      | ≥ 1.20.0 | Numerical computations   |
| matplotlib | ≥ 3.5.0  | Plotting                 |

## Development

### Running tests

```bash
# When tests are implemented
pytest tests/
```

### Code structure

The application follows a manager pattern:
- **Managers** (`*_manager.py`): Handle business logic and state
- **UI modules** (`*_ui.py`): Create UI components
- **Config modules** (`*_config.py`): Define parameter configurations

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Acknowledgments

- [Brian2](https://brian2.readthedocs.io/) - The simulator that powers this application
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework