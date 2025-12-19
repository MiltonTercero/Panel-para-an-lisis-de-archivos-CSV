"""
Main GUI Application for EDA Panel.
Integrates all components into a unified interface.
"""

import customtkinter as ctk
from typing import Optional

from core.data_manager import DataManager
from core.statistics_engine import StatisticsEngine
from core.visualization_generator import VisualizationGenerator
from gui.components.data_loader import DataLoaderPanel
from gui.components.dataset_info import DatasetInfoPanel
from gui.components.variable_selector import VariableSelectorPanel
from gui.components.statistics_panel import StatisticsPanel
from gui.components.visualization_panel import VisualizationPanel
from gui.components.report_panel import ReportPanel
from utils.logger import setup_logger, LoggerMixin


class GUIApplication(ctk.CTk, LoggerMixin):
    """
    Main GUI application for EDA Panel.
    """
    
    APP_NAME = "EDA Panel - Análisis Exploratorio de Datos"
    MIN_WIDTH = 1400
    MIN_HEIGHT = 800
    
    def __init__(self):
        super().__init__()
        
        # Set up logging
        setup_logger(log_level=10)  # DEBUG level
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure window
        self.title(self.APP_NAME)
        self.geometry(f"{self.MIN_WIDTH}x{self.MIN_HEIGHT}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        
        # Initialize core components
        self.data_manager = DataManager()
        self.stats_engine = StatisticsEngine()
        self.viz_generator = VisualizationGenerator(style='dark')
        
        # Current selected column
        self._current_column: Optional[str] = None
        
        # Build UI
        self._setup_ui()
        
        self.log_info("EDA Panel Application started")
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        # Configure grid weights for responsive layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Left sidebar
        self.grid_columnconfigure(1, weight=1)  # Main content
        self.grid_columnconfigure(2, weight=0)  # Right sidebar
        
        # ========== LEFT SIDEBAR ==========
        left_sidebar = ctk.CTkFrame(self, width=300, fg_color=("#d4d4d4", "#242424"))
        left_sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_sidebar.grid_propagate(False)
        
        # App title
        title_frame = ctk.CTkFrame(left_sidebar, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        app_title = ctk.CTkLabel(
            title_frame,
            text="📊 EDA Panel",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#3498db"
        )
        app_title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Análisis Exploratorio de Datos",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        subtitle.pack()
        
        # Separator
        sep = ctk.CTkFrame(left_sidebar, height=2, fg_color="#3498db")
        sep.pack(fill="x", padx=15, pady=10)
        
        # Data Loader Panel
        self.data_loader = DataLoaderPanel(
            left_sidebar,
            self.data_manager,
            on_data_loaded=self._on_data_loaded
        )
        self.data_loader.pack(fill="x", padx=15, pady=10)
        
        # Dataset Info Panel
        self.dataset_info = DatasetInfoPanel(
            left_sidebar,
            self.data_manager,
            self.stats_engine,
            corner_radius=10
        )
        self.dataset_info.pack(fill="x", padx=15, pady=10)
        
        # Report Panel
        self.report_panel = ReportPanel(
            left_sidebar,
            self.data_manager,
            self.stats_engine,
            self.viz_generator
        )
        self.report_panel.pack(fill="x", padx=15, pady=10)
        
        # ========== CENTER CONTENT ==========
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        center_frame.grid_rowconfigure(0, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)
        
        # Visualization Panel (takes most space)
        self.viz_panel = VisualizationPanel(
            center_frame,
            self.data_manager,
            self.stats_engine,
            self.viz_generator
        )
        self.viz_panel.pack(fill="both", expand=True)
        
        # ========== RIGHT SIDEBAR ==========
        right_sidebar = ctk.CTkFrame(self, width=320, fg_color=("#d4d4d4", "#242424"))
        right_sidebar.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        right_sidebar.grid_propagate(False)
        right_sidebar.grid_rowconfigure(0, weight=1)
        right_sidebar.grid_rowconfigure(1, weight=1)
        
        # Variable Selector Panel
        self.variable_selector = VariableSelectorPanel(
            right_sidebar,
            self.data_manager,
            on_variable_selected=self._on_variable_selected
        )
        self.variable_selector.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        # Statistics Panel
        self.stats_panel = StatisticsPanel(
            right_sidebar,
            self.data_manager,
            self.stats_engine
        )
        self.stats_panel.pack(fill="both", expand=True, padx=10, pady=(5, 10))
    
    def _on_data_loaded(self):
        """Handle data loaded event."""
        self.log_info("Data loaded, updating all panels")
        
        # Update all panels
        self.dataset_info.update_info()
        self.variable_selector.update_variables()
        self.viz_panel.update_missing_overview()
        
        # Reset statistics and select first numeric column if available
        self.stats_panel.reset()
        
        numeric_cols = self.data_manager.get_numeric_columns()
        if numeric_cols:
            self._on_variable_selected(numeric_cols[0])
    
    def _on_variable_selected(self, column_name: str):
        """Handle variable selection event."""
        self._current_column = column_name
        self.log_info(f"Variable selected: {column_name}")
        
        # Update statistics and visualizations
        self.stats_panel.update_statistics(column_name)
        self.viz_panel.update_visualizations(column_name)
    
    def run(self):
        """Run the application."""
        self.mainloop()


def main():
    """Application entry point."""
    app = GUIApplication()
    app.run()


if __name__ == "__main__":
    main()
