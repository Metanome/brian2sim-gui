from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTabWidget,
    QTextBrowser,
    QDialogButtonBox,
    QWidget
)
from PyQt6.QtCore import Qt

class HelpDialog(QDialog):
    """A professional documentation dialog for the application."""
    
    def __init__(self, parent=None, start_tab_index=0):
        super().__init__(parent)
        self.setWindowTitle("Brian2Sim Documentation")
        self.resize(700, 500)
        self.start_tab_index = start_tab_index
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Tab widget for different documentation sections
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_resources_tab(), "Online Resources")
        self.tabs.addTab(self.create_about_app_tab(), "About Brian2Sim")
        self.tabs.addTab(self.create_about_brian_tab(), "About Brian2")
        
        if 0 <= self.start_tab_index < self.tabs.count():
            self.tabs.setCurrentIndex(self.start_tab_index)
            
        layout.addWidget(self.tabs)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def create_resources_tab(self):
        """Create the Online Resources tab content."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
            <h2 style="color: #2c3e50;">Online Resources</h2>
            <p>For detailed documentation, tutorials, and issues, please visit our online repositories.</p>
            
            <h3 style="color: #2980b9;">Brian2Sim on GitHub</h3>
            <ul>
                <li><a href="https://github.com/Metanome/brian2sim-gui">User Guide & Wiki</a></li>
                <li><a href="https://github.com/Metanome/brian2sim-gui/issues">Report Issues</a></li>
                <li><a href="https://github.com/Metanome/brian2sim-gui/releases">Latest Updates</a></li>
            </ul>
            
            <h3 style="color: #2980b9;">Brian2 Simulator</h3>
            <ul>
                <li><a href="https://brian2.readthedocs.io">Brian2 Documentation</a></li>
                <li><a href="https://brian.discourse.group/">Brian Discourse Forum</a></li>
            </ul>
        """)
        return browser

    def create_about_app_tab(self):
        """Create the About Brian2Sim tab content."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
            <div style="text-align: center;">
                <h1 style="color: #2c3e50; margin-bottom: 5px;">Brian2Sim GUI</h1>
                <p style="font-size: 1.2em; color: #7f8c8d; margin-top: 0;">Version 1.0.0</p>
            </div>
            
            <hr style="border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0));">
            
            <p><b>Brian2Sim</b> is a comprehensive graphical interface for designing, running, and analyzing spiking neural network simulations using the Brian2 simulator.</p>
            
            <h3 style="color: #2980b9;">Key Features</h3>
            <ul>
                <li><b>Visual Design:</b> Intuitive configuration of neurons, synapses, and plasticity.</li>
                <li><b>Advanced Models:</b> Support for multicompartment models, gap junctions, and complex receptors.</li>
                <li><b>Validation:</b> Real-time parameter checking to prevent simulation errors.</li>
                <li><b>Code Generation:</b> Export valid Python/Brian2 scripts for standalone execution.</li>
            </ul>
            
            <p style="margin-top: 20px;">
                <i>Built with PyQt6 and Brian2. Released under Open Source License.</i><br>
                <a href="https://github.com/Metanome/brian2sim-gui">https://github.com/Metanome/brian2sim-gui</a>
            </p>
        """)
        return browser
        
    def create_about_brian_tab(self):
        """Create the About Brian2 tab content."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
            <h2 style="color: #2c3e50;">About Brian2</h2>
            <p><b>Brian2</b> is a clock-driven simulator for spiking neural networks.</p>
            
            <p>It is designed to be easy to learn and use, highly flexible, and easily consistent.</p>
            
            <h3 style="color: #2980b9;">Resources</h3>
            <ul>
                <li><a href="https://brian2.readthedocs.io">Official Documentation</a></li>
                <li><a href="https://brian2.readthedocs.io/en/stable/examples/index.html">Example Gallery</a></li>
                <li><a href="https://brian.discourse.group/">Community Forum</a></li>
            </ul>
            
            <p style="font-size: 0.9em; color: #7f8c8d;">Brian2Sim connects to your local Brian2 installation to run simulations.</p>
        """)
        return browser
