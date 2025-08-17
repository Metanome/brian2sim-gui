# gap_junctions_config.py
# Configuration for gap junctions (electrical synapses) in Brian2Sim GUI
# Gap junctions provide electrical coupling between neurons for synchronized activity

GAP_JUNCTIONS_CONFIG = {
    'enabled': {
        'type': 'checkbox',
        'default': False,
        'label': 'Enable Gap Junctions',
        'tooltip': 'Enable electrical coupling between neurons via gap junctions'
    },
    
    # Basic gap junction parameters
    'conductance': {
        'type': 'spinbox',
        'default': 0.1,  # nS
        'min': 0.0,
        'max': 10.0,
        'decimals': 3,
        'suffix': ' nS',
        'label': 'Gap Junction Conductance',
        'tooltip': 'Electrical conductance of gap junctions (0.01-2 nS typical range)'
    },
    
    'connection_probability': {
        'type': 'spinbox',
        'default': 0.1,
        'min': 0.0,
        'max': 1.0,
        'decimals': 3,
        'label': 'Connection Probability',
        'tooltip': 'Probability of gap junction connection between neuron pairs (0-1)'
    },
    
    'max_distance': {
        'type': 'spinbox',
        'default': 100.0,  # μm
        'min': 0.0,
        'max': 1000.0,
        'decimals': 1,
        'suffix': ' μm',
        'label': 'Maximum Connection Distance',
        'tooltip': 'Maximum distance for gap junction connections (μm)'
    },
    
    # Gap junction types and properties
    'junction_type': {
        'type': 'combo',
        'default': 'symmetric',
        'options': ['symmetric', 'asymmetric', 'rectifying'],
        'label': 'Junction Type',
        'tooltip': 'Type of electrical coupling: symmetric (bidirectional), asymmetric, or rectifying'
    },
    
    'coupling_coefficient': {
        'type': 'spinbox',
        'default': 0.1,
        'min': 0.0,
        'max': 1.0,
        'decimals': 3,
        'label': 'Coupling Coefficient',
        'tooltip': 'Strength of electrical coupling (0-1, where 1 = perfect coupling)'
    },
    
    # Voltage-dependent properties
    'voltage_dependence': {
        'type': 'checkbox',
        'default': False,
        'label': 'Voltage-Dependent Gating',
        'tooltip': 'Enable voltage-dependent gap junction gating'
    },
    
    'gating_voltage': {
        'type': 'spinbox',
        'default': -40.0,  # mV
        'min': -100.0,
        'max': 50.0,
        'decimals': 1,
        'suffix': ' mV',
        'label': 'Gating Voltage',
        'tooltip': 'Voltage threshold for gap junction gating (mV)'
    },
    
    'gating_slope': {
        'type': 'spinbox',
        'default': 10.0,  # mV
        'min': 1.0,
        'max': 50.0,
        'decimals': 1,
        'suffix': ' mV',
        'label': 'Gating Slope',
        'tooltip': 'Voltage sensitivity of gap junction gating (mV)'
    },
    
    # Cell-type specific connections
    'connection_specificity': {
        'type': 'combo',
        'default': 'all_to_all',
        'options': [
            'all_to_all',
            'same_type_only',
            'excitatory_only',
            'inhibitory_only',
            'interneuron_network'
        ],
        'label': 'Connection Specificity',
        'tooltip': 'Which cell types can form gap junctions'
    },
    
    # Spatial organization
    'spatial_organization': {
        'type': 'combo',
        'default': 'distance_based',
        'options': [
            'distance_based',
            'nearest_neighbor',
            'columnar',
            'radial_clusters',
            'random'
        ],
        'label': 'Spatial Organization',
        'tooltip': 'Spatial pattern of gap junction connections'
    },
    
    'cluster_size': {
        'type': 'spinbox',
        'default': 10,
        'min': 2,
        'max': 100,
        'label': 'Cluster Size',
        'tooltip': 'Number of neurons in each electrically coupled cluster'
    },
    
    # Developmental and plasticity
    'developmental_changes': {
        'type': 'checkbox',
        'default': False,
        'label': 'Developmental Changes',
        'tooltip': 'Enable time-dependent changes in gap junction properties'
    },
    
    'initial_conductance': {
        'type': 'spinbox',
        'default': 0.5,  # nS
        'min': 0.0,
        'max': 5.0,
        'decimals': 3,
        'suffix': ' nS',
        'label': 'Initial Conductance',
        'tooltip': 'Initial gap junction conductance for developmental changes'
    },
    
    'final_conductance': {
        'type': 'spinbox',
        'default': 0.1,  # nS
        'min': 0.0,
        'max': 5.0,
        'decimals': 3,
        'suffix': ' nS',
        'label': 'Final Conductance',
        'tooltip': 'Final gap junction conductance after development'
    },
    
    'development_time_constant': {
        'type': 'spinbox',
        'default': 1000.0,  # ms
        'min': 10.0,
        'max': 10000.0,
        'decimals': 1,
        'suffix': ' ms',
        'label': 'Development Time Constant',
        'tooltip': 'Time constant for developmental changes in conductance'
    },
    
    # Activity-dependent plasticity
    'activity_dependent': {
        'type': 'checkbox',
        'default': False,
        'label': 'Activity-Dependent Plasticity',
        'tooltip': 'Enable activity-dependent changes in gap junction strength'
    },
    
    'plasticity_threshold': {
        'type': 'spinbox',
        'default': 20.0,  # Hz
        'min': 0.1,
        'max': 100.0,
        'decimals': 1,
        'suffix': ' Hz',
        'label': 'Plasticity Threshold',
        'tooltip': 'Activity threshold for gap junction plasticity (Hz)'
    },
    
    'potentiation_rate': {
        'type': 'spinbox',
        'default': 0.01,
        'min': 0.0,
        'max': 0.1,
        'decimals': 4,
        'suffix': ' /s',
        'label': 'Potentiation Rate',
        'tooltip': 'Rate of gap junction strengthening with high activity'
    },
    
    'depression_rate': {
        'type': 'spinbox',
        'default': 0.001,
        'min': 0.0,
        'max': 0.01,
        'decimals': 5,
        'suffix': ' /s',
        'label': 'Depression Rate',
        'tooltip': 'Rate of gap junction weakening with low activity'
    },
    
    # Modulation by neurotransmitters
    'neuromodulation': {
        'type': 'checkbox',
        'default': False,
        'label': 'Neuromodulation',
        'tooltip': 'Enable modulation of gap junctions by neurotransmitters'
    },
    
    'dopamine_modulation': {
        'type': 'spinbox',
        'default': 0.0,
        'min': -1.0,
        'max': 1.0,
        'decimals': 3,
        'label': 'Dopamine Modulation',
        'tooltip': 'Dopamine effect on gap junction conductance (-1 to 1)'
    },
    
    'noradrenaline_modulation': {
        'type': 'spinbox',
        'default': 0.0,
        'min': -1.0,
        'max': 1.0,
        'decimals': 3,
        'label': 'Noradrenaline Modulation',
        'tooltip': 'Noradrenaline effect on gap junction conductance (-1 to 1)'
    },
    
    # Recording and analysis
    'record_currents': {
        'type': 'checkbox',
        'default': False,
        'label': 'Record Gap Junction Currents',
        'tooltip': 'Record electrical currents through gap junctions'
    },
    
    'record_conductances': {
        'type': 'checkbox',
        'default': False,
        'label': 'Record Conductances',
        'tooltip': 'Record gap junction conductance values over time'
    },
    
    'record_coupling_strength': {
        'type': 'checkbox',
        'default': False,
        'label': 'Record Coupling Strength',
        'tooltip': 'Record effective coupling strength between neurons'
    },
    
    # Advanced properties
    'junction_noise': {
        'type': 'checkbox',
        'default': False,
        'label': 'Junction Noise',
        'tooltip': 'Add noise to gap junction conductance'
    },
    
    'noise_amplitude': {
        'type': 'spinbox',
        'default': 0.01,  # nS
        'min': 0.0,
        'max': 0.1,
        'decimals': 4,
        'suffix': ' nS',
        'label': 'Noise Amplitude',
        'tooltip': 'Standard deviation of conductance noise (nS)'
    },
    
    'correlation_time': {
        'type': 'spinbox',
        'default': 10.0,  # ms
        'min': 0.1,
        'max': 100.0,
        'decimals': 1,
        'suffix': ' ms',
        'label': 'Noise Correlation Time',
        'tooltip': 'Temporal correlation of gap junction noise (ms)'
    },
    
    # Pathological conditions
    'pathological_conditions': {
        'type': 'checkbox',
        'default': False,
        'label': 'Pathological Conditions',
        'tooltip': 'Simulate pathological changes in gap junctions'
    },
    
    'pathology_type': {
        'type': 'combo',
        'default': 'epilepsy',
        'options': [
            'epilepsy',
            'ischemia',
            'inflammation',
            'aging',
            'neurodegenerative'
        ],
        'label': 'Pathology Type',
        'tooltip': 'Type of pathological condition affecting gap junctions'
    },
    
    'pathology_severity': {
        'type': 'spinbox',
        'default': 0.5,
        'min': 0.0,
        'max': 1.0,
        'decimals': 2,
        'label': 'Pathology Severity',
        'tooltip': 'Severity of pathological changes (0-1)'
    }
}

# Gap junction-specific research references and validation ranges (2025 standards)
GAP_JUNCTION_RESEARCH_INFO = {
    'description': 'Gap junctions are electrical synapses that allow direct ionic communication between neurons, crucial for network synchronization and oscillations.',
    
    'physiological_ranges': {
        'conductance': {
            'range': '0.01-2.0 nS',
            'typical': '0.1-0.5 nS',
            'notes': 'Varies by cell type and developmental stage'
        },
        'coupling_coefficient': {
            'range': '0.01-0.8',
            'typical': '0.1-0.3',
            'notes': 'Higher in interneuron networks'
        },
        'connection_probability': {
            'range': '0.01-0.5',
            'typical': '0.05-0.2',
            'notes': 'Depends on cell type and brain region'
        }
    },
    
    'research_references': [
        'Bennett & Zukin (2004) Electrical coupling and neuronal synchronization in the mammalian brain. Neuron 41:495-511',
        'Connors & Long (2004) Electrical synapses in the mammalian brain. Annu Rev Neurosci 27:393-418',
        'Pereda (2014) Electrical synapses and their functional interactions with chemical synapses. Nat Rev Neurosci 15:250-263',
        'Belousov & Fontes (2013) Neuronal gap junctions: making and breaking connections during development and injury. Trends Neurosci 36:227-236',
        'Rash et al. (2013) Molecular and functional asymmetry at vertebrate electrical synapses. Front Cell Neurosci 7:151'
    ],
    
    'implementation_notes': {
        'brian2_syntax': 'Use Synapses with bidirectional connections and voltage-dependent current',
        'computational_efficiency': 'Gap junctions require careful timestep selection for stability',
        'network_effects': 'Strong gap junction coupling can lead to network oscillations and synchrony',
        'validation_tests': 'Test coupling coefficient, synchronization index, and oscillation frequency'
    }
}
