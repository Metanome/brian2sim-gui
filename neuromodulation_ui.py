# neuromodulation_ui.py
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QGridLayout, QLabel
from ui_forms import BaseFormGenerator
from neuromodulation_config import NEUROMODULATION_CONFIG

def create_neuromodulation_group(main_window):
    neuromodulation_group = QGroupBox("Neuromodulation")
    neuromodulation_group.setToolTip("Configure dopamine, serotonin, norepinephrine, and acetylcholine systems.")
    main_window.neuromodulation_form_generator = NeuromodulationFormGenerator(NEUROMODULATION_CONFIG)
    form_widget = main_window.neuromodulation_form_generator.get_form_widget()
    if form_widget:
        neuromodulation_group.setLayout(form_widget.layout())
        param_widgets = main_window.neuromodulation_form_generator.get_param_widgets()
        main_window.neuromodulation_enabled = param_widgets.get("enabled")
        for param_key, widget in param_widgets.items():
            if param_key != "enabled":
                if hasattr(widget, 'valueChanged'):
                    widget.valueChanged.connect(main_window.neuromodulation_manager.on_param_changed)
                elif hasattr(widget, 'currentIndexChanged'):
                    widget.currentIndexChanged.connect(main_window.neuromodulation_manager.on_param_changed)
    return neuromodulation_group

class NeuromodulationFormGenerator(BaseFormGenerator):
    def _create_forms(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        params_container = QWidget()
        params_layout = QGridLayout(params_container)
        params_layout.setSpacing(8)
        param_widgets = {}
        self.param_labels["main"] = {}
        self.cell_widgets["main"] = {}
        row, col = 0, 0
        num_cols = 3
        for param_key, param_config in self.config.items():
            input_widget = self._create_widget_for_param(param_key, param_config)
            if input_widget:
                cell_widget = QWidget()
                cell_layout = QVBoxLayout(cell_widget)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.setSpacing(2)
                label_text = param_config.get("label", param_key.replace("_", " ").title())
                label = QLabel(label_text)
                label.setWordWrap(True)
                cell_layout.addWidget(label)
                cell_layout.addWidget(input_widget)
                params_layout.addWidget(cell_widget, row, col)
                param_widgets[param_key] = input_widget
                self.param_labels["main"][param_key] = label
                self.cell_widgets["main"][param_key] = cell_widget
                col += 1
                if col >= num_cols:
                    col = 0
                    row += 1
        main_layout.addWidget(params_container)
        main_layout.addStretch()
        self.param_widgets["main"] = param_widgets
        self.forms["main"] = main_widget
