"""
Visualization Panel for EDA Panel Application.
Displays matplotlib charts in tabbed interface.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from core.data_manager import DataManager
from core.statistics_engine import StatisticsEngine
from core.visualization_generator import VisualizationGenerator
from utils.logger import LoggerMixin


class VisualizationPanel(ctk.CTkFrame, LoggerMixin):
    """
    Panel displaying visualizations in tabs.
    """
    
    def __init__(
        self,
        parent,
        data_manager: DataManager,
        stats_engine: StatisticsEngine,
        viz_generator: VisualizationGenerator,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.data_manager = data_manager
        self.stats_engine = stats_engine
        self.viz_generator = viz_generator
        self._current_column: Optional[str] = None
        self._canvases: Dict[str, FigureCanvasTkAgg] = {}
        
        self._setup_ui()
        self.log_info("VisualizationPanel initialized")
    
    def _setup_ui(self):
        """Set up the UI components."""
        self.configure(fg_color="transparent")
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Visualizaciones",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        title_label.pack(side="left")
        
        self.column_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.column_label.pack(side="right")
        
        # Controls frame
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.controls_frame.pack(fill="x", pady=(0, 5))
        
        # Outlier display toggle
        self.show_outliers_var = ctk.BooleanVar(value=True)
        outlier_check = ctk.CTkCheckBox(
            self.controls_frame,
            text="Mostrar outliers",
            variable=self.show_outliers_var,
            command=self._refresh_current_viz,
            font=ctk.CTkFont(size=11)
        )
        outlier_check.pack(side="left", padx=5)
        
        # Stats lines toggle
        self.show_stats_var = ctk.BooleanVar(value=True)
        stats_check = ctk.CTkCheckBox(
            self.controls_frame,
            text="Mostrar estadísticas",
            variable=self.show_stats_var,
            command=self._refresh_current_viz,
            font=ctk.CTkFont(size=11)
        )
        stats_check.pack(side="left", padx=5)
        
        # Tabview for visualizations
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)
        
        # Create tabs
        self.tabs = {
            'dist': self.tabview.add("Distribución"),
            'boxplot': self.tabview.add("Boxplot"),
            'outliers': self.tabview.add("Outliers"),
            'missing': self.tabview.add("Faltantes"),
            'timeseries': self.tabview.add("Serie Temporal")
        }
        
        # Create chart containers for each tab
        self.chart_frames = {}
        for tab_name, tab in self.tabs.items():
            frame = ctk.CTkFrame(tab, fg_color=("#2b2b2b", "#1a1a2e"))
            frame.pack(fill="both", expand=True, padx=5, pady=5)
            self.chart_frames[tab_name] = frame
            
            # Placeholder
            placeholder = ctk.CTkLabel(
                frame,
                text="Selecciona una variable para visualizar",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            placeholder.pack(expand=True)
    
    def _clear_chart(self, tab_name: str):
        """Clear a chart container."""
        if tab_name in self._canvases:
            self._canvases[tab_name].get_tk_widget().destroy()
            del self._canvases[tab_name]
        
        for widget in self.chart_frames[tab_name].winfo_children():
            widget.destroy()
    
    def _embed_figure(self, tab_name: str, figure: Figure):
        """Embed a matplotlib figure in a tab."""
        self._clear_chart(tab_name)
        
        canvas = FigureCanvasTkAgg(figure, master=self.chart_frames[tab_name])
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self._canvases[tab_name] = canvas
    
    def _refresh_current_viz(self):
        """Refresh the current visualization with updated settings."""
        if self._current_column:
            self.update_visualizations(self._current_column)
    
    def update_visualizations(self, column_name: str):
        """Update all visualizations for the selected column."""
        if not self.data_manager.is_loaded:
            return
        
        series = self.data_manager.get_column_data(column_name)
        if series is None:
            return
        
        self._current_column = column_name
        self.column_label.configure(text=f"Variable: {column_name}")
        
        # Get statistics
        basic_stats = self.stats_engine.calculate_basic_stats(series)
        outlier_info = self.stats_engine.detect_outliers_iqr(series)
        
        show_stats = self.show_stats_var.get()
        show_outliers = self.show_outliers_var.get()
        
        # 1. Distribution histogram
        try:
            fig_dist = self.viz_generator.plot_histogram_kde(
                series,
                stats=basic_stats if show_stats else None,
                show_mean=show_stats,
                show_median=show_stats,
                show_mode=show_stats,
                show_rug=len(series.dropna()) < 500,
                figsize=(8, 5)
            )
            self._embed_figure('dist', fig_dist)
        except Exception as e:
            self.log_error(f"Error creating distribution plot: {e}")
            self._show_error_in_tab('dist', str(e))
        
        # 2. Boxplot
        try:
            fig_box = self.viz_generator.plot_boxplot(
                series,
                outlier_info=outlier_info if show_stats else None,
                show_outliers=show_outliers,
                show_limits=show_stats,
                figsize=(8, 5)
            )
            self._embed_figure('boxplot', fig_box)
        except Exception as e:
            self.log_error(f"Error creating boxplot: {e}")
            self._show_error_in_tab('boxplot', str(e))
        
        # 3. Outlier scatter
        try:
            fig_outlier = self.viz_generator.plot_outlier_scatter(
                series,
                outlier_info,
                figsize=(8, 5)
            )
            self._embed_figure('outliers', fig_outlier)
        except Exception as e:
            self.log_error(f"Error creating outlier plot: {e}")
            self._show_error_in_tab('outliers', str(e))
        
        # 4. Missing data (dataset level)
        try:
            df = self.data_manager.dataframe
            fig_missing = self.viz_generator.plot_missing_bar(df, figsize=(8, 5))
            self._embed_figure('missing', fig_missing)
        except Exception as e:
            self.log_error(f"Error creating missing data plot: {e}")
            self._show_error_in_tab('missing', str(e))
        
        # 5. Time series (if applicable)
        try:
            # Check if data could be a time series
            if len(series.dropna()) >= 10:
                fig_ts = self.viz_generator.plot_time_series(
                    series,
                    outlier_info=outlier_info if show_outliers else None,
                    figsize=(8, 5)
                )
                self._embed_figure('timeseries', fig_ts)
            else:
                self._clear_chart('timeseries')
                msg = ctk.CTkLabel(
                    self.chart_frames['timeseries'],
                    text="Datos insuficientes para serie temporal\n(mínimo 10 valores)",
                    font=ctk.CTkFont(size=12),
                    text_color="#888888"
                )
                msg.pack(expand=True)
        except Exception as e:
            self.log_error(f"Error creating time series plot: {e}")
            self._show_error_in_tab('timeseries', str(e))
        
        self.log_info(f"Visualizations updated for column: {column_name}")
    
    def _show_error_in_tab(self, tab_name: str, error_msg: str):
        """Show error message in a tab."""
        self._clear_chart(tab_name)
        
        error_label = ctk.CTkLabel(
            self.chart_frames[tab_name],
            text=f"Error al generar gráfico:\n{error_msg}",
            font=ctk.CTkFont(size=12),
            text_color="#e74c3c",
            wraplength=300
        )
        error_label.pack(expand=True)
    
    def update_missing_overview(self):
        """Update missing data visualization for entire dataset."""
        if not self.data_manager.is_loaded:
            return
        
        try:
            df = self.data_manager.dataframe
            
            # Bar chart
            fig_bar = self.viz_generator.plot_missing_bar(df, figsize=(8, 5))
            self._embed_figure('missing', fig_bar)
            
        except Exception as e:
            self.log_error(f"Error updating missing overview: {e}")
    
    def reset(self):
        """Reset the panel."""
        self._current_column = None
        self.column_label.configure(text="")
        
        for tab_name in self.tabs:
            self._clear_chart(tab_name)
            placeholder = ctk.CTkLabel(
                self.chart_frames[tab_name],
                text="Selecciona una variable para visualizar",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            placeholder.pack(expand=True)
