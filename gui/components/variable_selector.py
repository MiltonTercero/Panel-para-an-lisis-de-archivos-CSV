"""
Variable Selector Panel for EDA Panel Application.
Provides tabbed variable selection with search and filtering.
"""

import customtkinter as ctk
from typing import Optional, Callable, List, Dict, Any

from core.data_manager import DataManager
from utils.helpers import format_percentage
from utils.logger import LoggerMixin


class VariableItem(ctk.CTkFrame):
    """Single variable item in the list."""
    
    def __init__(
        self,
        parent,
        column_info: Dict[str, Any],
        on_analyze: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.column_info = column_info
        self.on_analyze = on_analyze
        
        self.configure(fg_color=("#d4d4d4", "#3a3a3a"), corner_radius=6)
        
        # Main row
        main_row = ctk.CTkFrame(self, fg_color="transparent")
        main_row.pack(fill="x", padx=10, pady=8)
        
        # Column name
        name_label = ctk.CTkLabel(
            main_row,
            text=column_info['name'],
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        # Data type badge
        dtype_colors = {
            'numeric': '#3498db',
            'categorical': '#9b59b6',
            'datetime': '#e67e22',
            'boolean': '#1abc9c',
            'other': '#95a5a6'
        }
        dtype_color = dtype_colors.get(column_info['category'], '#95a5a6')
        
        dtype_label = ctk.CTkLabel(
            main_row,
            text=column_info['category'].upper()[:3],
            font=ctk.CTkFont(size=9),
            fg_color=dtype_color,
            corner_radius=4,
            width=35,
            height=18
        )
        dtype_label.pack(side="left", padx=5)
        
        # Analyze button
        analyze_btn = ctk.CTkButton(
            main_row,
            text="Analizar",
            command=self._on_analyze_click,
            width=70,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        analyze_btn.pack(side="right")
        
        # Completeness bar row
        bar_row = ctk.CTkFrame(self, fg_color="transparent")
        bar_row.pack(fill="x", padx=10, pady=(0, 8))
        
        completeness = column_info.get('completeness', 100)
        
        # Progress bar background
        bar_bg = ctk.CTkFrame(bar_row, fg_color="#555555", height=6, corner_radius=3)
        bar_bg.pack(side="left", fill="x", expand=True)
        
        # Progress bar fill
        bar_width = max(0.02, completeness / 100)  # Minimum 2% for visibility
        bar_color = "#2ecc71" if completeness >= 95 else "#f39c12" if completeness >= 80 else "#e74c3c"
        
        bar_fill = ctk.CTkFrame(bar_bg, fg_color=bar_color, height=6, corner_radius=3)
        bar_fill.place(relx=0, rely=0, relwidth=bar_width, relheight=1)
        
        # Percentage label
        pct_label = ctk.CTkLabel(
            bar_row,
            text=f"{completeness:.0f}%",
            font=ctk.CTkFont(size=10),
            width=40,
            text_color=bar_color
        )
        pct_label.pack(side="right", padx=(5, 0))
    
    def _on_analyze_click(self):
        if self.on_analyze:
            self.on_analyze(self.column_info['name'])


class VariableSelectorPanel(ctk.CTkFrame, LoggerMixin):
    """
    Panel for selecting and filtering variables with tabs.
    """
    
    def __init__(
        self,
        parent,
        data_manager: DataManager,
        on_variable_selected: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.data_manager = data_manager
        self.on_variable_selected = on_variable_selected
        self._column_info: List[Dict] = []
        self._filtered_items: List[VariableItem] = []
        
        self._setup_ui()
        self.log_info("VariableSelectorPanel initialized")
    
    def _setup_ui(self):
        """Set up the UI components."""
        self.configure(fg_color="transparent")
        
        # Header with search
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📋 Variables",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        title_label.pack(side="left")
        
        # Search entry
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        
        search_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="🔍 Buscar variable...",
            textvariable=self.search_var,
            width=150,
            height=30
        )
        search_entry.pack(side="right")
        
        # Tabview
        self.tabview = ctk.CTkTabview(self, height=400)
        self.tabview.pack(fill="both", expand=True)
        
        # Create tabs
        self.tabs = {
            'all': self.tabview.add("Todas"),
            'numeric': self.tabview.add("Numéricas"),
            'categorical': self.tabview.add("Categóricas")
        }
        
        # Scrollable frames for each tab
        self.scroll_frames = {}
        for tab_name, tab in self.tabs.items():
            scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
            scroll.pack(fill="both", expand=True)
            self.scroll_frames[tab_name] = scroll
            
            # Placeholder
            placeholder = ctk.CTkLabel(
                scroll,
                text="Carga un dataset para ver las variables",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            placeholder.pack(expand=True, pady=50)
    
    def _on_search_change(self, *args):
        """Handle search input change."""
        self._update_variable_list()
    
    def _clear_tab(self, tab_name: str):
        """Clear all widgets in a tab."""
        for widget in self.scroll_frames[tab_name].winfo_children():
            widget.destroy()
    
    def _add_variable_to_tab(self, tab_name: str, column_info: Dict):
        """Add a variable item to a specific tab."""
        item = VariableItem(
            self.scroll_frames[tab_name],
            column_info,
            on_analyze=self._on_analyze_variable
        )
        item.pack(fill="x", pady=3)
        return item
    
    def _on_analyze_variable(self, column_name: str):
        """Handle variable analyze click."""
        self.log_info(f"Variable selected for analysis: {column_name}")
        if self.on_variable_selected:
            self.on_variable_selected(column_name)
    
    def _update_variable_list(self):
        """Update the variable list based on current data and search filter."""
        search_text = self.search_var.get().lower().strip()
        
        # Clear all tabs
        for tab_name in self.tabs:
            self._clear_tab(tab_name)
        
        if not self.data_manager.is_loaded:
            for tab_name in self.tabs:
                placeholder = ctk.CTkLabel(
                    self.scroll_frames[tab_name],
                    text="Carga un dataset para ver las variables",
                    font=ctk.CTkFont(size=12),
                    text_color="#888888"
                )
                placeholder.pack(expand=True, pady=50)
            return
        
        # Get column info
        column_info = self.data_manager.get_column_info()
        
        # Filter by search
        if search_text:
            column_info = [c for c in column_info if search_text in c['name'].lower()]
        
        # Populate tabs
        for col in column_info:
            # Add to "All" tab
            self._add_variable_to_tab('all', col)
            
            # Add to category-specific tab
            if col['category'] == 'numeric':
                self._add_variable_to_tab('numeric', col)
            elif col['category'] in ['categorical', 'other']:
                self._add_variable_to_tab('categorical', col)
        
        # Add empty message if no results
        for tab_name in self.tabs:
            if not self.scroll_frames[tab_name].winfo_children():
                no_results = ctk.CTkLabel(
                    self.scroll_frames[tab_name],
                    text="No se encontraron variables",
                    font=ctk.CTkFont(size=12),
                    text_color="#888888"
                )
                no_results.pack(expand=True, pady=50)
        
        self.log_info(f"Variable list updated: {len(column_info)} variables shown")
    
    def update_variables(self):
        """Refresh the variable list."""
        self._update_variable_list()
    
    def reset(self):
        """Reset the panel."""
        self.search_var.set("")
        self._update_variable_list()
