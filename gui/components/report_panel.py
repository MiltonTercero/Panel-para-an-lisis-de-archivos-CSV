"""
Report Panel for EDA Panel Application.
Handles PDF report generation and clipboard operations.
"""

import os
import customtkinter as ctk
from tkinter import filedialog
from typing import Optional
from datetime import datetime
import threading

from core.data_manager import DataManager
from core.statistics_engine import StatisticsEngine
from core.visualization_generator import VisualizationGenerator
from gui.dialogs import show_success, show_error, show_info
from utils.logger import LoggerMixin
from utils.helpers import format_memory_size

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.platypus.flowables import HRFlowable
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ReportPanel(ctk.CTkFrame, LoggerMixin):
    """
    Panel for generating EDA reports.
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
        self._generating = False
        
        self._setup_ui()
        self.log_info("ReportPanel initialized")
    
    def _setup_ui(self):
        """Set up the UI components."""
        self.configure(fg_color=("#e8e8e8", "#2b2b2b"), corner_radius=10)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📄 Reporte EDA",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        title_label.pack(side="left")
        
        # Buttons container
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=10)
        
        # Generate PDF button
        self.generate_btn = ctk.CTkButton(
            buttons_frame,
            text="📑 Generar Reporte PDF",
            command=self._on_generate_click,
            font=ctk.CTkFont(size=12),
            height=40,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.generate_btn.pack(fill="x", pady=5)
        
        # Copy to clipboard button
        self.copy_btn = ctk.CTkButton(
            buttons_frame,
            text="📋 Copiar Estadísticas",
            command=self._on_copy_click,
            font=ctk.CTkFont(size=12),
            height=40,
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        )
        self.copy_btn.pack(fill="x", pady=5)
        
        # Progress bar (hidden)
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Generando reporte...",
            font=ctk.CTkFont(size=11)
        )
        self.progress_label.pack(fill="x", padx=15)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", padx=15, pady=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Listo para generar reporte",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        self.status_label.pack(fill="x", padx=15, pady=(5, 15))
    
    def _on_generate_click(self):
        """Handle generate report button click."""
        if self._generating:
            return
        
        if not self.data_manager.is_loaded:
            show_error(self.winfo_toplevel(), "Error", "No hay dataset cargado")
            return
        
        if not REPORTLAB_AVAILABLE:
            show_error(
                self.winfo_toplevel(), 
                "Error", 
                "ReportLab no está instalado.\nInstálalo con: pip install reportlab"
            )
            return
        
        # Ask for save location
        default_name = f"eda_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = filedialog.asksaveasfilename(
            title="Guardar reporte",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=default_name,
            initialdir=os.path.expanduser("~")
        )
        
        if not filepath:
            return
        
        self._start_generation(filepath)
    
    def _start_generation(self, filepath: str):
        """Start report generation."""
        self._generating = True
        self.generate_btn.configure(state="disabled")
        self.copy_btn.configure(state="disabled")
        self.progress_frame.pack(fill="x", pady=10)
        self.progress_bar.start()
        self.status_label.configure(text="Generando reporte...")
        
        # Generate in background
        thread = threading.Thread(target=self._generate_report, args=(filepath,), daemon=True)
        thread.start()
    
    def _generate_report(self, filepath: str):
        """Generate the PDF report."""
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=20,
                textColor=colors.HexColor('#3498db')
            )
            story.append(Paragraph("Reporte de Análisis Exploratorio de Datos", title_style))
            story.append(Spacer(1, 10))
            
            # Date
            date_style = ParagraphStyle('Date', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
            story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
            story.append(Spacer(1, 20))
            
            # Dataset summary
            summary = self.data_manager.get_dataset_summary()
            
            section_style = ParagraphStyle(
                'Section',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=10,
                textColor=colors.HexColor('#2c3e50')
            )
            story.append(Paragraph("1. Resumen del Dataset", section_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
            story.append(Spacer(1, 10))
            
            # Summary table
            summary_data = [
                ["Métrica", "Valor"],
                ["Nombre de archivo", summary.get('file_name', 'N/A')],
                ["Filas", f"{summary['n_rows']:,}"],
                ["Columnas", str(summary['n_columns'])],
                ["Uso de memoria", summary['memory_size']],
                ["Datos completos", f"{summary['completeness']:.1f}%"],
                ["Datos faltantes", f"{100 - summary['completeness']:.1f}%"]
            ]
            
            table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Data types breakdown
            story.append(Paragraph("2. Tipos de Datos", section_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
            story.append(Spacer(1, 10))
            
            dtype_counts = summary.get('dtype_counts', {})
            dtype_data = [
                ["Tipo", "Cantidad"],
                ["Numéricas", str(dtype_counts.get('numeric', 0))],
                ["Categóricas", str(dtype_counts.get('categorical', 0))],
                ["Fecha/Hora", str(dtype_counts.get('datetime', 0))],
                ["Booleanas", str(dtype_counts.get('boolean', 0))],
                ["Otras", str(dtype_counts.get('other', 0))]
            ]
            
            dtype_table = Table(dtype_data, colWidths=[2.5*inch, 2*inch])
            dtype_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            story.append(dtype_table)
            story.append(Spacer(1, 20))
            
            # Missing data analysis
            story.append(Paragraph("3. Análisis de Datos Faltantes", section_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
            story.append(Spacer(1, 10))
            
            missing_analysis = self.stats_engine.analyze_missing_data(self.data_manager.dataframe)
            
            missing_text = f"""
            <b>Total de celdas:</b> {missing_analysis['total_cells']:,}<br/>
            <b>Celdas faltantes:</b> {missing_analysis['total_missing']:,} ({missing_analysis['total_missing_pct']:.2f}%)<br/>
            <b>Columnas con faltantes:</b> {missing_analysis['columns_with_missing']} de {missing_analysis['total_columns']}<br/>
            <b>Filas completas:</b> {missing_analysis['complete_rows']:,} ({missing_analysis['complete_rows_pct']:.1f}%)
            """
            story.append(Paragraph(missing_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Column details
            story.append(Paragraph("4. Detalle por Columna", section_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
            story.append(Spacer(1, 10))
            
            column_info = self.data_manager.get_column_info()
            col_data = [["Columna", "Tipo", "Completos", "Faltantes"]]
            
            for col in column_info[:30]:  # Limit to 30 columns
                col_data.append([
                    col['name'][:25],
                    col['category'],
                    f"{col['completeness']:.1f}%",
                    str(col['null_count'])
                ])
            
            col_table = Table(col_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1*inch])
            col_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ]))
            story.append(col_table)
            
            # Build PDF
            doc.build(story)
            
            # Update UI on main thread
            self.after(0, lambda: self._on_generation_complete(True, filepath))
            
        except Exception as e:
            self.log_exception(f"Error generating report: {e}")
            self.after(0, lambda: self._on_generation_complete(False, str(e)))
    
    def _on_generation_complete(self, success: bool, result: str):
        """Handle generation completion."""
        self._generating = False
        self.generate_btn.configure(state="normal")
        self.copy_btn.configure(state="normal")
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
        
        if success:
            self.status_label.configure(text=f"✓ Reporte guardado", text_color="#2ecc71")
            show_success(
                self.winfo_toplevel(),
                "Reporte Generado",
                f"El reporte EDA se ha guardado en:\n{result}"
            )
        else:
            self.status_label.configure(text="✕ Error al generar", text_color="#e74c3c")
            show_error(self.winfo_toplevel(), "Error", f"Error al generar el reporte:\n{result}")
    
    def _on_copy_click(self):
        """Copy statistics to clipboard."""
        if not self.data_manager.is_loaded:
            show_error(self.winfo_toplevel(), "Error", "No hay dataset cargado")
            return
        
        try:
            summary = self.data_manager.get_dataset_summary()
            missing = self.stats_engine.analyze_missing_data(self.data_manager.dataframe)
            
            text = f"""RESUMEN DEL DATASET
==================
Archivo: {summary.get('file_name', 'N/A')}
Filas: {summary['n_rows']:,}
Columnas: {summary['n_columns']}
Memoria: {summary['memory_size']}
Completitud: {summary['completeness']:.2f}%

DATOS FALTANTES
===============
Total celdas faltantes: {missing['total_missing']:,}
Porcentaje faltantes: {missing['total_missing_pct']:.2f}%
Columnas con faltantes: {missing['columns_with_missing']}
Filas completas: {missing['complete_rows']:,}

TIPOS DE DATOS
==============
"""
            for dtype, count in summary.get('dtype_counts', {}).items():
                text += f"{dtype.capitalize()}: {count}\n"
            
            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(text)
            
            self.status_label.configure(text="✓ Copiado al portapapeles", text_color="#2ecc71")
            show_info(self.winfo_toplevel(), "Copiado", "Estadísticas copiadas al portapapeles")
            
        except Exception as e:
            self.log_error(f"Error copying to clipboard: {e}")
            show_error(self.winfo_toplevel(), "Error", f"Error al copiar:\n{str(e)}")
    
    def reset(self):
        """Reset the panel."""
        self.status_label.configure(text="Listo para generar reporte", text_color="#888888")
