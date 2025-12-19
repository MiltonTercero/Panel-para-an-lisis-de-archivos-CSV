"""
Dataset Info Panel for EDA Panel Application.
Displays dataset summary and quality indicators.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any

from core.data_manager import DataManager
from core.statistics_engine import StatisticsEngine
from utils.helpers import format_percentage, create_quality_label
from utils.logger import LoggerMixin


class DatasetInfoPanel(ctk.CTkFrame, LoggerMixin):
    """
    Panel displaying dataset summary information and quality indicators.
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
        
        self._setup_ui()
        self.log_info("DatasetInfoPanel initialized")
    
    def _setup_ui(self):
        """Set up the UI components."""
        self.configure(fg_color=("#e8e8e8", "#2b2b2b"))
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Información del Dataset",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        title_label.pack(side="left")
        
        # Quality indicator
        self.quality_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        self.quality_frame.pack(side="right")
        
        self.quality_dot = ctk.CTkLabel(
            self.quality_frame,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color="#888888"
        )
        self.quality_dot.pack(side="left", padx=2)
        
        self.quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="Sin datos",
            font=ctk.CTkFont(size=12)
        )
        self.quality_label.pack(side="left")
        
        # Stats container
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Placeholder message
        self.placeholder = ctk.CTkLabel(
            self.stats_frame,
            text="Carga un dataset para ver la información",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.placeholder.pack(expand=True)
        
        # Stats cards (hidden initially)
        self.cards_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        
        # Row 1: Basic counts
        row1 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        self.rows_card = self._create_stat_card(row1, "Filas", "0", "#3498db")
        self.cols_card = self._create_stat_card(row1, "Columnas", "0", "#9b59b6")
        self.memory_card = self._create_stat_card(row1, "Memoria", "0 B", "#e67e22")
        
        # Row 2: Data types
        row2 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self.numeric_card = self._create_stat_card(row2, "Numéricas", "0", "#2ecc71")
        self.categorical_card = self._create_stat_card(row2, "Categóricas", "0", "#1abc9c")
        self.datetime_card = self._create_stat_card(row2, "Fecha/Hora", "0", "#34495e")
        
        # Row 3: Data quality
        row3 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        self.complete_card = self._create_stat_card(row3, "Datos Completos", "0%", "#2ecc71")
        self.missing_card = self._create_stat_card(row3, "Datos Faltantes", "0%", "#e74c3c")
    
    def _create_stat_card(
        self,
        parent,
        title: str,
        value: str,
        color: str
    ) -> Dict[str, ctk.CTkLabel]:
        """Create a statistics card."""
        card = ctk.CTkFrame(parent, fg_color=("#d4d4d4", "#3a3a3a"), corner_radius=8)
        card.pack(side="left", fill="both", expand=True, padx=3)
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=color
        )
        value_label.pack(pady=(10, 2))
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        title_label.pack(pady=(0, 10))
        
        return {"value": value_label, "title": title_label, "frame": card}
    
    def update_info(self):
        """Update the panel with current dataset information."""
        if not self.data_manager.is_loaded:
            self.reset()
            return
        
        # Hide placeholder, show cards
        self.placeholder.pack_forget()
        self.cards_frame.pack(fill="both", expand=True)
        
        # Get summary data
        summary = self.data_manager.get_dataset_summary()
        dtype_counts = summary.get('dtype_counts', {})
        
        # Update basic stats
        self.rows_card["value"].configure(text=f"{summary['n_rows']:,}")
        self.cols_card["value"].configure(text=str(summary['n_columns']))
        self.memory_card["value"].configure(text=summary['memory_size'])
        
        # Update data types
        self.numeric_card["value"].configure(text=str(dtype_counts.get('numeric', 0)))
        self.categorical_card["value"].configure(text=str(dtype_counts.get('categorical', 0)))
        self.datetime_card["value"].configure(text=str(dtype_counts.get('datetime', 0)))
        
        # Update quality info
        completeness = summary.get('completeness', 0)
        missing_pct = 100 - completeness
        
        self.complete_card["value"].configure(text=f"{completeness:.1f}%")
        self.missing_card["value"].configure(text=f"{missing_pct:.1f}%")
        
        # Update color based on values
        if missing_pct > 20:
            self.missing_card["value"].configure(text_color="#e74c3c")
        elif missing_pct > 5:
            self.missing_card["value"].configure(text_color="#f39c12")
        else:
            self.missing_card["value"].configure(text_color="#2ecc71")
        
        # Update quality indicator
        quality_label, quality_color = create_quality_label(completeness)
        self.quality_dot.configure(text_color=quality_color)
        self.quality_label.configure(text=quality_label)
        
        self.log_info(f"Dataset info updated: {summary['n_rows']} rows, {summary['n_columns']} cols")
    
    def reset(self):
        """Reset the panel to initial state."""
        self.cards_frame.pack_forget()
        self.placeholder.pack(expand=True)
        
        self.quality_dot.configure(text_color="#888888")
        self.quality_label.configure(text="Sin datos")
