"""
VisualizationGenerator class for EDA Panel Application.
Creates matplotlib/seaborn visualizations for data analysis.
"""

from typing import Optional, Dict, List, Any, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

from utils.logger import LoggerMixin


class VisualizationGenerator(LoggerMixin):
    """
    Generates various visualizations for EDA analysis.
    """
    
    # Color palette
    COLORS = {
        'primary': '#3498db',
        'secondary': '#2ecc71',
        'accent': '#e74c3c',
        'warning': '#f39c12',
        'dark': '#2c3e50',
        'light': '#ecf0f1',
        'outlier': '#e74c3c',
        'normal': '#3498db',
        'mean': '#e74c3c',
        'median': '#2ecc71',
        'mode': '#9b59b6',
        'kde': '#f39c12',
        'missing': '#e74c3c',
        'complete': '#2ecc71'
    }
    
    def __init__(self, style: str = 'dark'):
        """
        Initialize VisualizationGenerator.
        
        Args:
            style: Plot style ('dark' or 'light')
        """
        self.style = style
        self._setup_style()
        self.log_info("VisualizationGenerator initialized")
    
    def _setup_style(self):
        """Set up matplotlib style."""
        if self.style == 'dark':
            plt.style.use('dark_background')
            self.bg_color = '#1a1a2e'
            self.text_color = '#ffffff'
            self.grid_color = '#3a3a5e'
        else:
            plt.style.use('seaborn-v0_8-whitegrid')
            self.bg_color = '#ffffff'
            self.text_color = '#2c3e50'
            self.grid_color = '#bdc3c7'
    
    def create_figure(self, figsize: Tuple[int, int] = (8, 6)) -> Figure:
        """Create a new figure with proper styling."""
        fig = Figure(figsize=figsize, facecolor=self.bg_color)
        return fig
    
    # ==================== DISTRIBUTION PLOTS ====================
    
    def plot_histogram_kde(
        self, 
        series: pd.Series, 
        stats: Dict[str, Any] = None,
        show_mean: bool = True,
        show_median: bool = True,
        show_mode: bool = True,
        show_rug: bool = True,
        figsize: Tuple[int, int] = (10, 6)
    ) -> Figure:
        """
        Create histogram with KDE, rug plot, and statistical lines.
        
        Args:
            series: Data series
            stats: Optional statistics dictionary
            show_mean/median/mode: Show vertical lines
            show_rug: Show rug plot at bottom
            figsize: Figure size
            
        Returns:
            Matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        clean_data = series.dropna()
        
        if len(clean_data) == 0:
            ax.text(0.5, 0.5, 'Sin datos disponibles', ha='center', va='center',
                   transform=ax.transAxes, fontsize=14, color=self.text_color)
            return fig
        
        # Histogram with KDE
        try:
            sns.histplot(clean_data, kde=True, ax=ax, color=self.COLORS['primary'],
                        edgecolor=self.COLORS['dark'], alpha=0.7, stat='density')
        except Exception:
            ax.hist(clean_data, bins='auto', density=True, color=self.COLORS['primary'],
                   edgecolor=self.COLORS['dark'], alpha=0.7)
        
        # Rug plot
        if show_rug and len(clean_data) < 1000:
            ax.plot(clean_data, np.zeros_like(clean_data) - 0.02, '|', 
                   color=self.COLORS['primary'], alpha=0.5, markersize=10)
        
        # Statistical lines
        legend_handles = []
        
        if show_mean and stats and stats.get('mean') is not None:
            mean_line = ax.axvline(stats['mean'], color=self.COLORS['mean'], 
                                   linestyle='--', linewidth=2, label=f"Media: {stats['mean']:.2f}")
            legend_handles.append(mean_line)
        
        if show_median and stats and stats.get('median') is not None:
            median_line = ax.axvline(stats['median'], color=self.COLORS['median'], 
                                     linestyle='-', linewidth=2, label=f"Mediana: {stats['median']:.2f}")
            legend_handles.append(median_line)
        
        if show_mode and stats and stats.get('mode') is not None:
            try:
                mode_val = float(stats['mode'])
                mode_line = ax.axvline(mode_val, color=self.COLORS['mode'], 
                                       linestyle=':', linewidth=2, label=f"Moda: {mode_val:.2f}")
                legend_handles.append(mode_line)
            except (ValueError, TypeError):
                pass
        
        # Styling
        ax.set_xlabel(series.name or 'Valor', fontsize=11, color=self.text_color)
        ax.set_ylabel('Densidad', fontsize=11, color=self.text_color)
        ax.set_title(f'Distribución de {series.name or "Variable"}', 
                    fontsize=13, fontweight='bold', color=self.text_color)
        ax.tick_params(colors=self.text_color)
        ax.set_facecolor(self.bg_color)
        
        if legend_handles:
            ax.legend(handles=legend_handles, loc='upper right', facecolor=self.bg_color,
                     edgecolor=self.grid_color, labelcolor=self.text_color)
        
        fig.tight_layout()
        return fig
    
    # ==================== BOXPLOT ====================
    
    def plot_boxplot(
        self,
        series: pd.Series,
        outlier_info: Dict[str, Any] = None,
        show_outliers: bool = True,
        show_limits: bool = True,
        figsize: Tuple[int, int] = (10, 6)
    ) -> Figure:
        """
        Create enhanced boxplot with outlier markers.
        
        Args:
            series: Data series
            outlier_info: Dictionary with outlier detection results
            show_outliers: Whether to show outliers
            show_limits: Whether to show IQR limits
            figsize: Figure size
            
        Returns:
            Matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        clean_data = series.dropna()
        
        if len(clean_data) == 0:
            ax.text(0.5, 0.5, 'Sin datos disponibles', ha='center', va='center',
                   transform=ax.transAxes, fontsize=14, color=self.text_color)
            return fig
        
        # Create boxplot
        bp = ax.boxplot(clean_data, vert=False, patch_artist=True,
                       showfliers=show_outliers,
                       flierprops={'marker': 'o', 'markerfacecolor': self.COLORS['outlier'],
                                  'markeredgecolor': self.COLORS['outlier'], 'markersize': 8})
        
        # Style the boxplot
        for patch in bp['boxes']:
            patch.set_facecolor(self.COLORS['primary'])
            patch.set_alpha(0.7)
        
        for whisker in bp['whiskers']:
            whisker.set_color(self.text_color)
            whisker.set_linewidth(1.5)
        
        for cap in bp['caps']:
            cap.set_color(self.text_color)
            cap.set_linewidth(1.5)
        
        for median in bp['medians']:
            median.set_color(self.COLORS['median'])
            median.set_linewidth(2)
        
        # Show IQR limits if outlier info provided
        if show_limits and outlier_info:
            lower = outlier_info.get('lower_bound')
            upper = outlier_info.get('upper_bound')
            
            if lower is not None:
                ax.axvline(lower, color=self.COLORS['warning'], linestyle='--', 
                          linewidth=1.5, alpha=0.7, label=f'Límite inferior: {lower:.2f}')
            if upper is not None:
                ax.axvline(upper, color=self.COLORS['warning'], linestyle='--', 
                          linewidth=1.5, alpha=0.7, label=f'Límite superior: {upper:.2f}')
            
            ax.legend(loc='upper right', facecolor=self.bg_color,
                     edgecolor=self.grid_color, labelcolor=self.text_color)
        
        # Add outlier count annotation
        if outlier_info and outlier_info.get('outlier_count', 0) > 0:
            count = outlier_info['outlier_count']
            pct = outlier_info.get('outlier_pct', 0)
            ax.annotate(f'Outliers: {count} ({pct:.1f}%)', 
                       xy=(0.02, 0.95), xycoords='axes fraction',
                       fontsize=10, color=self.COLORS['outlier'],
                       fontweight='bold')
        
        # Styling
        ax.set_xlabel(series.name or 'Valor', fontsize=11, color=self.text_color)
        ax.set_title(f'Boxplot de {series.name or "Variable"}', 
                    fontsize=13, fontweight='bold', color=self.text_color)
        ax.tick_params(colors=self.text_color)
        ax.set_facecolor(self.bg_color)
        ax.set_yticklabels([])
        
        fig.tight_layout()
        return fig
    
    # ==================== VIOLIN PLOT ====================
    
    def plot_violin(
        self,
        series: pd.Series,
        show_boxplot: bool = True,
        figsize: Tuple[int, int] = (10, 6)
    ) -> Figure:
        """
        Create violin plot with optional boxplot overlay.
        
        Args:
            series: Data series
            show_boxplot: Whether to overlay boxplot
            figsize: Figure size
            
        Returns:
            Matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        clean_data = series.dropna()
        
        if len(clean_data) == 0:
            ax.text(0.5, 0.5, 'Sin datos disponibles', ha='center', va='center',
                   transform=ax.transAxes, fontsize=14, color=self.text_color)
            return fig
        
        # Create violin plot
        parts = ax.violinplot(clean_data, positions=[1], vert=False, showmeans=True,
                             showmedians=True, showextrema=True)
        
        # Style violin
        for pc in parts['bodies']:
            pc.set_facecolor(self.COLORS['primary'])
            pc.set_alpha(0.7)
        
        parts['cmeans'].set_color(self.COLORS['mean'])
        parts['cmedians'].set_color(self.COLORS['median'])
        parts['cbars'].set_color(self.text_color)
        parts['cmaxes'].set_color(self.text_color)
        parts['cmins'].set_color(self.text_color)
        
        # Overlay boxplot
        if show_boxplot:
            bp = ax.boxplot(clean_data, positions=[1], vert=False, widths=0.1,
                           patch_artist=True, showfliers=True,
                           flierprops={'marker': 'o', 'markerfacecolor': self.COLORS['outlier'],
                                      'markersize': 6})
            for patch in bp['boxes']:
                patch.set_facecolor(self.COLORS['secondary'])
                patch.set_alpha(0.8)
        
        # Styling
        ax.set_xlabel(series.name or 'Valor', fontsize=11, color=self.text_color)
        ax.set_title(f'Diagrama de Violín - {series.name or "Variable"}', 
                    fontsize=13, fontweight='bold', color=self.text_color)
        ax.tick_params(colors=self.text_color)
        ax.set_facecolor(self.bg_color)
        ax.set_yticklabels([])
        
        # Legend
        handles = [
            mpatches.Patch(color=self.COLORS['mean'], label='Media'),
            mpatches.Patch(color=self.COLORS['median'], label='Mediana')
        ]
        ax.legend(handles=handles, loc='upper right', facecolor=self.bg_color,
                 edgecolor=self.grid_color, labelcolor=self.text_color)
        
        fig.tight_layout()
        return fig
    
    # ==================== MISSING DATA PLOTS ====================
    
    def plot_missing_bar(
        self,
        df: pd.DataFrame,
        max_columns: int = 20,
        figsize: Tuple[int, int] = (12, 6)
    ) -> Figure:
        """
        Create bar chart of missing values per column.
        
        Args:
            df: DataFrame to analyze
            max_columns: Maximum columns to show
            figsize: Figure size
            
        Returns:
            Matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        # Calculate missing percentages
        missing_pct = (df.isna().sum() / len(df)) * 100
        missing_pct = missing_pct.sort_values(ascending=False)
        
        # Limit columns
        if len(missing_pct) > max_columns:
            missing_pct = missing_pct.head(max_columns)
        
        # Create bars with color gradient
        colors = [self.COLORS['missing'] if p > 20 else 
                 self.COLORS['warning'] if p > 5 else 
                 self.COLORS['complete'] for p in missing_pct.values]
        
        bars = ax.barh(range(len(missing_pct)), missing_pct.values, color=colors, alpha=0.8)
        
        # Add percentage labels
        for i, (bar, pct) in enumerate(zip(bars, missing_pct.values)):
            if pct > 0:
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                       f'{pct:.1f}%', va='center', fontsize=9, color=self.text_color)
        
        # Styling
        ax.set_yticks(range(len(missing_pct)))
        ax.set_yticklabels(missing_pct.index, fontsize=9)
        ax.set_xlabel('Porcentaje de valores faltantes', fontsize=11, color=self.text_color)
        ax.set_title('Valores Faltantes por Columna', 
                    fontsize=13, fontweight='bold', color=self.text_color)
        ax.tick_params(colors=self.text_color)
        ax.set_facecolor(self.bg_color)
        ax.set_xlim(0, max(missing_pct.values) * 1.15 if missing_pct.max() > 0 else 100)
        ax.invert_yaxis()
        
        # Add legend
        legend_elements = [
            mpatches.Patch(color=self.COLORS['complete'], label='< 5%'),
            mpatches.Patch(color=self.COLORS['warning'], label='5-20%'),
            mpatches.Patch(color=self.COLORS['missing'], label='> 20%')
        ]
        ax.legend(handles=legend_elements, loc='lower right', facecolor=self.bg_color,
                 edgecolor=self.grid_color, labelcolor=self.text_color, title='Severidad')
        
        fig.tight_layout()
        return fig
    
    def plot_missing_heatmap(
        self,
        df: pd.DataFrame,
        max_rows: int = 100,
        max_columns: int = 30,
        figsize: Tuple[int, int] = (12, 8)
    ) -> Figure:
        """
        Create heatmap of missing values pattern.
        
        Args:
            df: DataFrame to analyze
            max_rows: Maximum rows to show
            max_columns: Maximum columns to show
            figsize: Figure size
            
        Returns:
            Matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        # Sample data if too large
        sample_df = df
        if len(df) > max_rows:
            sample_df = df.sample(n=max_rows, random_state=42).sort_index()
        
        if len(df.columns) > max_columns:
            # Keep columns with most missing values
            missing_counts = df.isna().sum().sort_values(ascending=False)
            keep_cols = missing_counts.head(max_columns).index.tolist()
            sample_df = sample_df[keep_cols]
        
        # Create missing mask
        missing_mask = sample_df.isna().astype(int)
        
        # Create heatmap
        cmap = plt.cm.colors.ListedColormap([self.COLORS['complete'], self.COLORS['missing']])
        im = ax.imshow(missing_mask.values, aspect='auto', cmap=cmap, interpolation='nearest')
        
        # Styling
        ax.set_xlabel('Columnas', fontsize=11, color=self.text_color)
        ax.set_ylabel('Filas (muestra)', fontsize=11, color=self.text_color)
        ax.set_title('Patrón de Valores Faltantes', 
                    fontsize=13, fontweight='bold', color=self.text_color)
        
        # X-axis labels
        ax.set_xticks(range(len(sample_df.columns)))
        ax.set_xticklabels(sample_df.columns, rotation=45, ha='right', fontsize=8)
        ax.tick_params(colors=self.text_color)
        ax.set_facecolor(self.bg_color)
        
        # Legend
        legend_elements = [
            mpatches.Patch(color=self.COLORS['complete'], label='Presente'),
            mpatches.Patch(color=self.COLORS['missing'], label='Faltante')
        ]
        ax.legend(handles=legend_elements, loc='upper right', facecolor=self.bg_color,
                 edgecolor=self.grid_color, labelcolor=self.text_color)
        
        fig.tight_layout()
        return fig
    
    # ==================== OUTLIER SCATTER PLOT ====================
    
    def plot_outlier_scatter(
        self,
        series: pd.Series,
        outlier_info: Dict[str, Any],
        figsize: Tuple[int, int] = (10, 6)
    ) -> Figure:
        """
        Create scatter plot highlighting outliers.
        
        Args:
            series: Data series
            outlier_info: Dictionary with outlier detection results
            figsize: Figure size
            
        Returns:
            Matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        clean_data = series.dropna()
        
        if len(clean_data) == 0:
            ax.text(0.5, 0.5, 'Sin datos disponibles', ha='center', va='center',
                   transform=ax.transAxes, fontsize=14, color=self.text_color)
            return fig
        
        # Get outlier bounds
        lower_bound = outlier_info.get('lower_bound', clean_data.min())
        upper_bound = outlier_info.get('upper_bound', clean_data.max())
        
        # Separate normal and outlier points
        is_outlier = (clean_data < lower_bound) | (clean_data > upper_bound)
        normal_data = clean_data[~is_outlier]
        outlier_data = clean_data[is_outlier]
        
        # Plot normal points
        ax.scatter(range(len(normal_data)), normal_data.values, 
                  c=self.COLORS['normal'], alpha=0.6, s=30, label='Normal')
        
        # Plot outliers
        if len(outlier_data) > 0:
            outlier_indices = [i for i, (idx, val) in enumerate(clean_data.items()) 
                             if idx in outlier_data.index]
            ax.scatter(outlier_indices, outlier_data.values,
                      c=self.COLORS['outlier'], alpha=0.9, s=60, 
                      edgecolors='white', linewidths=1, label='Outlier', marker='D')
        
        # Add horizontal lines for bounds
        ax.axhline(lower_bound, color=self.COLORS['warning'], linestyle='--', 
                  alpha=0.7, label=f'Límite inferior: {lower_bound:.2f}')
        ax.axhline(upper_bound, color=self.COLORS['warning'], linestyle='--', 
                  alpha=0.7, label=f'Límite superior: {upper_bound:.2f}')
        
        # Shade outlier regions
        ax.axhspan(clean_data.min() - abs(clean_data.min())*0.1, lower_bound, 
                  alpha=0.1, color=self.COLORS['outlier'])
        ax.axhspan(upper_bound, clean_data.max() + abs(clean_data.max())*0.1, 
                  alpha=0.1, color=self.COLORS['outlier'])
        
        # Styling
        ax.set_xlabel('Índice', fontsize=11, color=self.text_color)
        ax.set_ylabel(series.name or 'Valor', fontsize=11, color=self.text_color)
        ax.set_title(f'Detección de Outliers - {series.name or "Variable"}', 
                    fontsize=13, fontweight='bold', color=self.text_color)
        ax.tick_params(colors=self.text_color)
        ax.set_facecolor(self.bg_color)
        ax.legend(loc='upper right', facecolor=self.bg_color,
                 edgecolor=self.grid_color, labelcolor=self.text_color)
        
        fig.tight_layout()
        return fig
    
    # ==================== TIME SERIES PLOT ====================
    
    def plot_time_series(
        self,
        series: pd.Series,
        outlier_info: Dict[str, Any] = None,
        show_trend: bool = True,
        figsize: Tuple[int, int] = (12, 6)
    ) -> Figure:
        """
        Create time series plot with optional outlier detection.
        
        Args:
            series: Time-indexed data series
            outlier_info: Optional outlier detection results
            show_trend: Whether to show rolling average trend
            figsize: Figure size
            
        Returns:
            Matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        clean_data = series.dropna()
        
        if len(clean_data) == 0:
            ax.text(0.5, 0.5, 'Sin datos disponibles', ha='center', va='center',
                   transform=ax.transAxes, fontsize=14, color=self.text_color)
            return fig
        
        # Plot main series
        ax.plot(clean_data.index, clean_data.values, color=self.COLORS['primary'],
               alpha=0.7, linewidth=1, label='Serie original')
        
        # Add trend line
        if show_trend and len(clean_data) > 10:
            window = max(5, len(clean_data) // 20)
            trend = clean_data.rolling(window=window, center=True).mean()
            ax.plot(trend.index, trend.values, color=self.COLORS['secondary'],
                   linewidth=2, label=f'Media móvil ({window})')
        
        # Highlight outliers if provided
        if outlier_info and outlier_info.get('outlier_indices'):
            outlier_indices = outlier_info['outlier_indices']
            outlier_values = clean_data.loc[clean_data.index.isin(outlier_indices) | 
                                           (clean_data.index.get_indexer(outlier_indices) >= 0)]
            if len(outlier_values) > 0:
                ax.scatter(outlier_values.index, outlier_values.values,
                          c=self.COLORS['outlier'], s=50, zorder=5,
                          label='Outliers', edgecolors='white')
        
        # Styling
        ax.set_xlabel('Tiempo/Índice', fontsize=11, color=self.text_color)
        ax.set_ylabel(series.name or 'Valor', fontsize=11, color=self.text_color)
        ax.set_title(f'Serie Temporal - {series.name or "Variable"}', 
                    fontsize=13, fontweight='bold', color=self.text_color)
        ax.tick_params(colors=self.text_color)
        ax.set_facecolor(self.bg_color)
        ax.legend(loc='upper right', facecolor=self.bg_color,
                 edgecolor=self.grid_color, labelcolor=self.text_color)
        
        # Rotate x labels if needed
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        fig.tight_layout()
        return fig
