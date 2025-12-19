"""
Data Loader Panel for EDA Panel Application.
Handles file selection and loading with progress feedback.
"""

import os
import customtkinter as ctk
from tkinter import filedialog
from typing import Optional, Callable

from core.data_manager import DataManager
from gui.dialogs import show_success, show_error
from utils.logger import LoggerMixin


class DataLoaderPanel(ctk.CTkFrame, LoggerMixin):
    """
    Panel for loading data files with progress indication.
    """
    
    FILETYPES = [
        ("Archivos de datos", "*.csv *.xlsx *.xls *.json"),
        ("CSV", "*.csv"),
        ("Excel", "*.xlsx *.xls"),
        ("JSON", "*.json"),
        ("Todos los archivos", "*.*")
    ]
    
    def __init__(
        self,
        parent,
        data_manager: DataManager,
        on_data_loaded: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.data_manager = data_manager
        self.on_data_loaded = on_data_loaded
        self._loading = False
        
        self._setup_ui()
        self.log_info("DataLoaderPanel initialized")
    
    def _setup_ui(self):
        """Set up the UI components."""
        # Main container
        self.configure(fg_color="transparent")
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📂 Cargar Dataset",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(side="left")
        
        # Load button
        self.load_button = ctk.CTkButton(
            self,
            text="Seleccionar Archivo",
            command=self._on_load_click,
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.load_button.pack(fill="x", pady=(0, 10))
        
        # File info label
        self.file_label = ctk.CTkLabel(
            self,
            text="No hay archivo cargado",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        self.file_label.pack(fill="x")
        
        # Progress bar (hidden by default)
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Cargando...",
            font=ctk.CTkFont(size=11)
        )
        self.progress_label.pack(fill="x")
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            mode="determinate",
            height=8
        )
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)
    
    def _on_load_click(self):
        """Handle load button click."""
        if self._loading:
            return
        
        # Open file dialog
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de datos",
            filetypes=self.FILETYPES,
            initialdir=os.path.expanduser("~")
        )
        
        if not filepath:
            return
        
        self._start_loading(filepath)
    
    def _start_loading(self, filepath: str):
        """Start the loading process."""
        self._loading = True
        self.load_button.configure(state="disabled", text="Cargando...")
        self.file_label.configure(text=f"Cargando: {os.path.basename(filepath)}")
        
        # Show progress
        self.progress_frame.pack(fill="x", pady=10)
        self.progress_bar.set(0)
        
        # Start async loading
        self.data_manager.load_file(
            filepath,
            progress_callback=self._on_progress,
            completion_callback=self._on_load_complete
        )
    
    def _on_progress(self, progress: float):
        """Handle progress updates."""
        # Schedule UI update on main thread
        self.after(0, lambda: self._update_progress(progress))
    
    def _update_progress(self, progress: float):
        """Update progress bar."""
        self.progress_bar.set(progress / 100)
        self.progress_label.configure(text=f"Cargando... {progress:.0f}%")
    
    def _on_load_complete(self, success: bool, message: str):
        """Handle load completion."""
        # Schedule UI update on main thread
        self.after(0, lambda: self._handle_load_result(success, message))
    
    def _handle_load_result(self, success: bool, message: str):
        """Handle the loading result in the main thread."""
        self._loading = False
        self.load_button.configure(state="normal", text="Seleccionar Archivo")
        self.progress_frame.pack_forget()
        
        if success:
            # Update file label
            summary = self.data_manager.get_dataset_summary()
            self.file_label.configure(
                text=f"✓ {summary['file_name']} ({summary['n_rows']:,} filas, {summary['n_columns']} cols)",
                text_color="#2ecc71"
            )
            
            # Show success dialog
            show_success(self.winfo_toplevel(), "Dataset Cargado", message)
            
            # Callback
            if self.on_data_loaded:
                self.on_data_loaded()
        else:
            self.file_label.configure(
                text="Error al cargar archivo",
                text_color="#e74c3c"
            )
            show_error(self.winfo_toplevel(), "Error de Carga", message)
    
    def reset(self):
        """Reset the panel to initial state."""
        self.file_label.configure(
            text="No hay archivo cargado",
            text_color="#888888"
        )
        self.progress_frame.pack_forget()
        self.progress_bar.set(0)
