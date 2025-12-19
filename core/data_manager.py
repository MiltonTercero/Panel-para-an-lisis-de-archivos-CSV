"""
DataManager class for EDA Panel Application.
Handles data loading, validation, and basic data manipulation.
"""

import os
import json
import threading
from typing import Optional, Callable, Dict, List, Tuple, Any
from io import StringIO

import pandas as pd
import numpy as np
import chardet

from utils.logger import LoggerMixin
from utils.helpers import format_memory_size, get_dtype_category, validate_file_extension


class DataManager(LoggerMixin):
    """
    Manages dataset loading, validation, and basic data operations.
    Supports CSV, Excel, and JSON file formats with automatic encoding detection.
    """
    
    SUPPORTED_EXTENSIONS = ['csv', 'xlsx', 'xls', 'json']
    
    def __init__(self):
        """Initialize DataManager."""
        self._dataframe: Optional[pd.DataFrame] = None
        self._file_path: Optional[str] = None
        self._loading_progress: float = 0.0
        self._is_loading: bool = False
        self._load_error: Optional[str] = None
        
        self.log_info("DataManager initialized")
    
    @property
    def dataframe(self) -> Optional[pd.DataFrame]:
        """Get the current dataframe."""
        return self._dataframe
    
    @property
    def is_loaded(self) -> bool:
        """Check if data is loaded."""
        return self._dataframe is not None
    
    @property
    def file_path(self) -> Optional[str]:
        """Get the current file path."""
        return self._file_path
    
    @property
    def loading_progress(self) -> float:
        """Get loading progress (0-100)."""
        return self._loading_progress
    
    @property
    def is_loading(self) -> bool:
        """Check if currently loading."""
        return self._is_loading
    
    def detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding using chardet.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding string
        """
        self.log_debug(f"Detecting encoding for: {file_path}")
        
        # Read a sample of the file for detection
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB
        
        result = chardet.detect(raw_data)
        encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0)
        
        self.log_info(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
        
        # Default to utf-8 if detection fails or low confidence
        if encoding is None or confidence < 0.5:
            encoding = 'utf-8'
        
        return encoding
    
    def load_csv(self, file_path: str, encoding: Optional[str] = None) -> pd.DataFrame:
        """
        Load a CSV file.
        
        Args:
            file_path: Path to CSV file
            encoding: Optional encoding, auto-detected if not provided
            
        Returns:
            Loaded DataFrame
        """
        if encoding is None:
            encoding = self.detect_encoding(file_path)
        
        self._loading_progress = 30
        
        # Try loading with detected encoding
        try:
            df = pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            # Fallback encodings
            for fallback in ['latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    self.log_warning(f"Encoding {encoding} failed, trying {fallback}")
                    df = pd.read_csv(file_path, encoding=fallback)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"No se pudo determinar la codificación del archivo")
        
        self._loading_progress = 70
        return df
    
    def load_excel(self, file_path: str) -> pd.DataFrame:
        """
        Load an Excel file.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Loaded DataFrame
        """
        self._loading_progress = 30
        
        # Load Excel file (first sheet by default)
        df = pd.read_excel(file_path, engine='openpyxl')
        
        self._loading_progress = 70
        return df
    
    def load_json(self, file_path: str, encoding: Optional[str] = None) -> pd.DataFrame:
        """
        Load a JSON file.
        
        Args:
            file_path: Path to JSON file
            encoding: Optional encoding
            
        Returns:
            Loaded DataFrame
        """
        if encoding is None:
            encoding = self.detect_encoding(file_path)
        
        self._loading_progress = 30
        
        with open(file_path, 'r', encoding=encoding) as f:
            data = json.load(f)
        
        self._loading_progress = 50
        
        # Handle different JSON structures
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Try to find a list of records
            if 'data' in data:
                df = pd.DataFrame(data['data'])
            elif 'records' in data:
                df = pd.DataFrame(data['records'])
            else:
                # Try to interpret as records
                df = pd.DataFrame([data])
        else:
            raise ValueError("Formato JSON no compatible")
        
        self._loading_progress = 70
        return df
    
    def load_file(
        self, 
        file_path: str, 
        progress_callback: Optional[Callable[[float], None]] = None,
        completion_callback: Optional[Callable[[bool, str], None]] = None
    ) -> None:
        """
        Load a data file asynchronously.
        
        Args:
            file_path: Path to the file
            progress_callback: Callback for progress updates (0-100)
            completion_callback: Callback when loading completes (success, message)
        """
        def _load_thread():
            self._is_loading = True
            self._load_error = None
            self._loading_progress = 0
            
            try:
                # Validate file
                is_valid, message = validate_file_extension(file_path, self.SUPPORTED_EXTENSIONS)
                if not is_valid:
                    raise ValueError(message)
                
                self._loading_progress = 10
                if progress_callback:
                    progress_callback(self._loading_progress)
                
                # Get file extension
                _, ext = os.path.splitext(file_path)
                ext = ext.lower().lstrip('.')
                
                self.log_info(f"Loading file: {file_path} (type: {ext})")
                
                # Load based on extension
                if ext == 'csv':
                    df = self.load_csv(file_path)
                elif ext in ['xlsx', 'xls']:
                    df = self.load_excel(file_path)
                elif ext == 'json':
                    df = self.load_json(file_path)
                else:
                    raise ValueError(f"Extensión no soportada: {ext}")
                
                if progress_callback:
                    progress_callback(self._loading_progress)
                
                # Validate DataFrame
                if df.empty:
                    raise ValueError("El archivo está vacío")
                
                self._loading_progress = 90
                if progress_callback:
                    progress_callback(self._loading_progress)
                
                # Store results
                self._dataframe = df
                self._file_path = file_path
                
                self._loading_progress = 100
                if progress_callback:
                    progress_callback(100)
                
                # Create success message
                summary = self.get_dataset_summary()
                success_msg = (
                    f"Dataset cargado exitosamente:\n"
                    f"• Filas: {summary['n_rows']:,}\n"
                    f"• Columnas: {summary['n_columns']}\n"
                    f"• Memoria: {summary['memory_size']}"
                )
                
                self.log_info(f"File loaded successfully: {summary['n_rows']} rows, {summary['n_columns']} columns")
                
                if completion_callback:
                    completion_callback(True, success_msg)
                    
            except Exception as e:
                self._load_error = str(e)
                self.log_error(f"Error loading file: {e}")
                
                if completion_callback:
                    completion_callback(False, f"Error al cargar el archivo:\n{str(e)}")
                    
            finally:
                self._is_loading = False
        
        # Start loading in background thread
        thread = threading.Thread(target=_load_thread, daemon=True)
        thread.start()
    
    def load_file_sync(self, file_path: str) -> Tuple[bool, str]:
        """
        Load a file synchronously.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            is_valid, message = validate_file_extension(file_path, self.SUPPORTED_EXTENSIONS)
            if not is_valid:
                return False, message
            
            _, ext = os.path.splitext(file_path)
            ext = ext.lower().lstrip('.')
            
            if ext == 'csv':
                df = self.load_csv(file_path)
            elif ext in ['xlsx', 'xls']:
                df = self.load_excel(file_path)
            elif ext == 'json':
                df = self.load_json(file_path)
            else:
                return False, f"Extensión no soportada: {ext}"
            
            if df.empty:
                return False, "El archivo está vacío"
            
            self._dataframe = df
            self._file_path = file_path
            
            summary = self.get_dataset_summary()
            return True, f"Cargado: {summary['n_rows']:,} filas, {summary['n_columns']} columnas"
            
        except Exception as e:
            return False, str(e)
    
    def get_dataset_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the loaded dataset.
        
        Returns:
            Dictionary with dataset summary information
        """
        if not self.is_loaded:
            return {}
        
        df = self._dataframe
        
        # Calculate memory usage
        memory_bytes = df.memory_usage(deep=True).sum()
        
        # Count data types
        dtype_counts = {'numeric': 0, 'categorical': 0, 'datetime': 0, 'boolean': 0, 'other': 0}
        for dtype in df.dtypes:
            category = get_dtype_category(str(dtype))
            dtype_counts[category] = dtype_counts.get(category, 0) + 1
        
        # Calculate missing data
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100 if total_cells > 0 else 0
        
        return {
            'n_rows': len(df),
            'n_columns': len(df.columns),
            'memory_bytes': memory_bytes,
            'memory_size': format_memory_size(memory_bytes),
            'dtype_counts': dtype_counts,
            'total_cells': total_cells,
            'missing_cells': int(missing_cells),
            'completeness': completeness,
            'file_name': os.path.basename(self._file_path) if self._file_path else None
        }
    
    def get_column_info(self) -> List[Dict[str, Any]]:
        """
        Get detailed information about each column.
        
        Returns:
            List of dictionaries with column information
        """
        if not self.is_loaded:
            return []
        
        df = self._dataframe
        columns_info = []
        
        for col in df.columns:
            series = df[col]
            non_null_count = series.notna().sum()
            total_count = len(series)
            
            columns_info.append({
                'name': col,
                'dtype': str(series.dtype),
                'category': get_dtype_category(str(series.dtype)),
                'non_null_count': non_null_count,
                'null_count': total_count - non_null_count,
                'completeness': (non_null_count / total_count) * 100 if total_count > 0 else 0,
                'unique_count': series.nunique()
            })
        
        return columns_info
    
    def get_numeric_columns(self) -> List[str]:
        """Get list of numeric column names."""
        if not self.is_loaded:
            return []
        return self._dataframe.select_dtypes(include=[np.number]).columns.tolist()
    
    def get_categorical_columns(self) -> List[str]:
        """Get list of categorical/object column names."""
        if not self.is_loaded:
            return []
        return self._dataframe.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def get_datetime_columns(self) -> List[str]:
        """Get list of datetime column names."""
        if not self.is_loaded:
            return []
        return self._dataframe.select_dtypes(include=['datetime64', 'timedelta64']).columns.tolist()
    
    def get_column_data(self, column_name: str) -> Optional[pd.Series]:
        """
        Get data for a specific column.
        
        Args:
            column_name: Name of the column
            
        Returns:
            Series with column data or None if not found
        """
        if not self.is_loaded or column_name not in self._dataframe.columns:
            return None
        return self._dataframe[column_name]
    
    def clear_data(self) -> None:
        """Clear the loaded data."""
        self._dataframe = None
        self._file_path = None
        self._loading_progress = 0
        self.log_info("Data cleared")
