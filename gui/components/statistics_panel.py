"""
Statistics Panel for EDA Panel Application.
Displays descriptive statistics in organized tabs.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any
import pandas as pd

from core.data_manager import DataManager
from core.statistics_engine import StatisticsEngine
from utils.logger import LoggerMixin


class StatRow(ctk.CTkFrame):
    """Single statistic row display."""
    
    def __init__(self, parent, label: str, value: str, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        label_widget = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            anchor="w",
            width=140
        )
        label_widget.pack(side="left")
        
        self.value_widget = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="e"
        )
        self.value_widget.pack(side="right", fill="x", expand=True)
    
    def set_value(self, value: str, color: str = None):
        """Update the displayed value."""
        self.value_widget.configure(text=value)
        if color:
            self.value_widget.configure(text_color=color)


class StatisticsPanel(ctk.CTkFrame, LoggerMixin):
    """
    Panel displaying descriptive statistics with tabs.
    """
    
    def __init__(
        self,
        parent,
        data_manager: DataManager,
        stats_engine: StatisticsEngine,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.data_manager = data_manager
        self.stats_engine = stats_engine
        self._current_column: Optional[str] = None
        
        self._setup_ui()
        self.log_info("StatisticsPanel initialized")
    
    def _setup_ui(self):
        """Set up the UI components."""
        self.configure(fg_color="transparent")
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="📈 Estadísticas",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.title_label.pack(side="left")
        
        self.column_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.column_label.pack(side="right")
        
        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)
        
        # Create tabs
        self.tab_basic = self.tabview.add("Resumen")
        self.tab_dist = self.tabview.add("Distribución")
        self.tab_quality = self.tabview.add("Calidad")
        
        # Setup each tab
        self._setup_basic_tab()
        self._setup_distribution_tab()
        self._setup_quality_tab()
        
        # Show placeholder initially
        self._show_placeholder()
    
    def _setup_basic_tab(self):
        """Setup the basic statistics tab."""
        scroll = ctk.CTkScrollableFrame(self.tab_basic, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        self.basic_stats = {
            'count': StatRow(scroll, "Conteo válido:", "-"),
            'mean': StatRow(scroll, "Media:", "-"),
            'median': StatRow(scroll, "Mediana:", "-"),
            'mode': StatRow(scroll, "Moda:", "-"),
            'std': StatRow(scroll, "Desviación Std:", "-"),
            'variance': StatRow(scroll, "Varianza:", "-"),
            'min': StatRow(scroll, "Mínimo:", "-"),
            'max': StatRow(scroll, "Máximo:", "-"),
            'range': StatRow(scroll, "Rango:", "-"),
            'unique': StatRow(scroll, "Valores únicos:", "-")
        }
        
        for stat_row in self.basic_stats.values():
            stat_row.pack(fill="x", pady=2)
    
    def _setup_distribution_tab(self):
        """Setup the distribution statistics tab."""
        scroll = ctk.CTkScrollableFrame(self.tab_dist, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        # Percentiles section
        section_label = ctk.CTkLabel(
            scroll,
            text="PERCENTILES",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#3498db"
        )
        section_label.pack(fill="x", pady=(5, 5))
        
        self.dist_stats = {
            'p25': StatRow(scroll, "Percentil 25:", "-"),
            'p50': StatRow(scroll, "Percentil 50:", "-"),
            'p75': StatRow(scroll, "Percentil 75:", "-"),
            'p90': StatRow(scroll, "Percentil 90:", "-"),
            'iqr': StatRow(scroll, "Rango Intercuartil:", "-")
        }
        
        for key in ['p25', 'p50', 'p75', 'p90', 'iqr']:
            self.dist_stats[key].pack(fill="x", pady=2)
        
        # Shape section
        section_label2 = ctk.CTkLabel(
            scroll,
            text="FORMA DE DISTRIBUCIÓN",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#3498db"
        )
        section_label2.pack(fill="x", pady=(15, 5))
        
        self.dist_stats.update({
            'skewness': StatRow(scroll, "Asimetría (Skewness):", "-"),
            'kurtosis': StatRow(scroll, "Curtosis:", "-"),
            'skew_interp': StatRow(scroll, "Interpretación:", "-"),
            'kurt_interp': StatRow(scroll, "Interpretación:", "-")
        })
        
        for key in ['skewness', 'skew_interp', 'kurtosis', 'kurt_interp']:
            self.dist_stats[key].pack(fill="x", pady=2)
        
        # Normality section
        section_label3 = ctk.CTkLabel(
            scroll,
            text="PRUEBA DE NORMALIDAD",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#3498db"
        )
        section_label3.pack(fill="x", pady=(15, 5))
        
        self.dist_stats.update({
            'shapiro_stat': StatRow(scroll, "Estadístico Shapiro-Wilk:", "-"),
            'shapiro_p': StatRow(scroll, "P-valor:", "-"),
            'is_normal': StatRow(scroll, "¿Es normal?:", "-")
        })
        
        for key in ['shapiro_stat', 'shapiro_p', 'is_normal']:
            self.dist_stats[key].pack(fill="x", pady=2)
    
    def _setup_quality_tab(self):
        """Setup the quality/missing data tab."""
        scroll = ctk.CTkScrollableFrame(self.tab_quality, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        # Missing data section
        section_label = ctk.CTkLabel(
            scroll,
            text="DATOS FALTANTES",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#e74c3c"
        )
        section_label.pack(fill="x", pady=(5, 5))
        
        self.quality_stats = {
            'missing_count': StatRow(scroll, "Valores faltantes:", "-"),
            'missing_pct': StatRow(scroll, "Porcentaje faltante:", "-"),
            'complete_count': StatRow(scroll, "Valores completos:", "-"),
            'pattern': StatRow(scroll, "Patrón:", "-")
        }
        
        for key in ['missing_count', 'missing_pct', 'complete_count', 'pattern']:
            self.quality_stats[key].pack(fill="x", pady=2)
        
        # Outliers section
        section_label2 = ctk.CTkLabel(
            scroll,
            text="OUTLIERS (IQR)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#e74c3c"
        )
        section_label2.pack(fill="x", pady=(15, 5))
        
        self.quality_stats.update({
            'outlier_count': StatRow(scroll, "Cantidad de outliers:", "-"),
            'outlier_pct': StatRow(scroll, "Porcentaje outliers:", "-"),
            'lower_bound': StatRow(scroll, "Límite inferior:", "-"),
            'upper_bound': StatRow(scroll, "Límite superior:", "-")
        })
        
        for key in ['outlier_count', 'outlier_pct', 'lower_bound', 'upper_bound']:
            self.quality_stats[key].pack(fill="x", pady=2)
        
        # Recommendations
        section_label3 = ctk.CTkLabel(
            scroll,
            text="RECOMENDACIONES",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#2ecc71"
        )
        section_label3.pack(fill="x", pady=(15, 5))
        
        self.recommendations_label = ctk.CTkLabel(
            scroll,
            text="",
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w",
            wraplength=250
        )
        self.recommendations_label.pack(fill="x", pady=5)
    
    def _show_placeholder(self):
        """Show placeholder message."""
        self.column_label.configure(text="Selecciona una variable")
    
    def _format_value(self, value, decimals: int = 4) -> str:
        """Format a numeric value for display."""
        if value is None:
            return "-"
        if isinstance(value, (int, float)):
            if abs(value) < 0.0001 and value != 0:
                return f"{value:.2e}"
            return f"{value:,.{decimals}f}" if decimals > 0 else f"{value:,.0f}"
        return str(value)
    
    def update_statistics(self, column_name: str):
        """Update statistics for the selected column."""
        if not self.data_manager.is_loaded:
            return
        
        series = self.data_manager.get_column_data(column_name)
        if series is None:
            return
        
        self._current_column = column_name
        self.column_label.configure(text=f"Variable: {column_name}")
        
        # Calculate statistics
        basic_stats = self.stats_engine.calculate_basic_stats(series)
        dist_stats = self.stats_engine.calculate_distribution_stats(series)
        missing_stats = self.stats_engine.analyze_column_missing(series)
        outlier_stats = self.stats_engine.detect_outliers_iqr(series)
        
        # Update basic tab
        self.basic_stats['count'].set_value(self._format_value(basic_stats['count'], 0))
        self.basic_stats['mean'].set_value(self._format_value(basic_stats['mean']))
        self.basic_stats['median'].set_value(self._format_value(basic_stats['median']))
        self.basic_stats['mode'].set_value(self._format_value(basic_stats['mode']))
        self.basic_stats['std'].set_value(self._format_value(basic_stats['std']))
        self.basic_stats['variance'].set_value(self._format_value(basic_stats['variance']))
        self.basic_stats['min'].set_value(self._format_value(basic_stats['min']))
        self.basic_stats['max'].set_value(self._format_value(basic_stats['max']))
        self.basic_stats['range'].set_value(self._format_value(basic_stats['range']))
        self.basic_stats['unique'].set_value(self._format_value(basic_stats['unique'], 0))
        
        # Update distribution tab
        if dist_stats['percentiles']:
            self.dist_stats['p25'].set_value(self._format_value(dist_stats['percentiles']['p25']))
            self.dist_stats['p50'].set_value(self._format_value(dist_stats['percentiles']['p50']))
            self.dist_stats['p75'].set_value(self._format_value(dist_stats['percentiles']['p75']))
            self.dist_stats['p90'].set_value(self._format_value(dist_stats['percentiles']['p90']))
        
        self.dist_stats['iqr'].set_value(self._format_value(dist_stats.get('iqr')))
        self.dist_stats['skewness'].set_value(self._format_value(dist_stats['skewness']))
        self.dist_stats['kurtosis'].set_value(self._format_value(dist_stats['kurtosis']))
        self.dist_stats['skew_interp'].set_value(dist_stats.get('skew_interpretation', '-'))
        self.dist_stats['kurt_interp'].set_value(dist_stats.get('kurt_interpretation', '-'))
        
        # Normality
        self.dist_stats['shapiro_stat'].set_value(self._format_value(dist_stats.get('shapiro_stat')))
        self.dist_stats['shapiro_p'].set_value(self._format_value(dist_stats.get('shapiro_p_value')))
        
        is_normal = dist_stats.get('is_normal')
        if is_normal is True:
            self.dist_stats['is_normal'].set_value("Sí (p > 0.05)", "#2ecc71")
        elif is_normal is False:
            self.dist_stats['is_normal'].set_value("No (p ≤ 0.05)", "#e74c3c")
        else:
            self.dist_stats['is_normal'].set_value("-")
        
        # Update quality tab
        self.quality_stats['missing_count'].set_value(
            self._format_value(missing_stats['missing'], 0),
            "#e74c3c" if missing_stats['missing'] > 0 else "#2ecc71"
        )
        self.quality_stats['missing_pct'].set_value(f"{missing_stats['missing_pct']:.2f}%")
        self.quality_stats['complete_count'].set_value(self._format_value(missing_stats['complete'], 0))
        self.quality_stats['pattern'].set_value(missing_stats['pattern'])
        
        self.quality_stats['outlier_count'].set_value(
            self._format_value(outlier_stats['outlier_count'], 0),
            "#e74c3c" if outlier_stats['outlier_count'] > 0 else "#2ecc71"
        )
        self.quality_stats['outlier_pct'].set_value(f"{outlier_stats['outlier_pct']:.2f}%")
        self.quality_stats['lower_bound'].set_value(self._format_value(outlier_stats.get('lower_bound')))
        self.quality_stats['upper_bound'].set_value(self._format_value(outlier_stats.get('upper_bound')))
        
        # Recommendations
        all_recs = missing_stats.get('recommendations', [])
        outlier_summary = self.stats_engine.get_outlier_summary(series)
        all_recs.extend(outlier_summary.get('recommendations', []))
        self.recommendations_label.configure(text="\n".join(all_recs))
        
        self.log_info(f"Statistics updated for column: {column_name}")
    
    def reset(self):
        """Reset the panel."""
        self._current_column = None
        self._show_placeholder()
        
        # Reset all values
        for stat_row in self.basic_stats.values():
            stat_row.set_value("-")
        for stat_row in self.dist_stats.values():
            stat_row.set_value("-")
        for stat_row in self.quality_stats.values():
            stat_row.set_value("-")
        self.recommendations_label.configure(text="")
