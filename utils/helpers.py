"""
Helper utilities for EDA Panel Application.
Provides common formatting and validation functions.
"""

import os
from typing import List, Tuple, Optional


def format_memory_size(size_bytes: int) -> str:
    """
    Format byte size to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes < 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.2f} {units[unit_index]}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a decimal value as percentage string.
    
    Args:
        value: Decimal value (0-1 or 0-100)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    # Handle values in 0-1 range
    if 0 <= value <= 1:
        value *= 100
    
    return f"{value:.{decimals}f}%"


def validate_file_extension(filepath: str, allowed_extensions: List[str] = None) -> Tuple[bool, str]:
    """
    Validate if a file has an allowed extension.
    
    Args:
        filepath: Path to the file
        allowed_extensions: List of allowed extensions (without dot)
        
    Returns:
        Tuple of (is_valid, message)
    """
    if allowed_extensions is None:
        allowed_extensions = ['csv', 'xlsx', 'xls', 'json']
    
    if not filepath:
        return False, "No se proporcionó ruta de archivo"
    
    if not os.path.exists(filepath):
        return False, f"El archivo no existe: {filepath}"
    
    _, ext = os.path.splitext(filepath)
    ext = ext.lower().lstrip('.')
    
    if ext not in allowed_extensions:
        allowed = ', '.join(allowed_extensions)
        return False, f"Extensión no válida: .{ext}. Extensiones permitidas: {allowed}"
    
    return True, "Archivo válido"


def get_file_info(filepath: str) -> dict:
    """
    Get basic information about a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dictionary with file information
    """
    if not os.path.exists(filepath):
        return {}
    
    stat = os.stat(filepath)
    return {
        'name': os.path.basename(filepath),
        'path': os.path.abspath(filepath),
        'size': stat.st_size,
        'size_formatted': format_memory_size(stat.st_size),
        'extension': os.path.splitext(filepath)[1].lower().lstrip('.')
    }


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_dtype_category(dtype_str: str) -> str:
    """
    Categorize a pandas dtype into a human-readable category.
    
    Args:
        dtype_str: String representation of dtype
        
    Returns:
        Category name (numeric, categorical, datetime, boolean, other)
    """
    dtype_str = str(dtype_str).lower()
    
    if any(t in dtype_str for t in ['int', 'float', 'complex']):
        return 'numeric'
    elif 'datetime' in dtype_str or 'timedelta' in dtype_str:
        return 'datetime'
    elif 'bool' in dtype_str:
        return 'boolean'
    elif 'object' in dtype_str or 'category' in dtype_str or 'string' in dtype_str:
        return 'categorical'
    else:
        return 'other'


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def create_quality_label(completeness: float) -> Tuple[str, str]:
    """
    Create a quality label based on data completeness.
    
    Args:
        completeness: Percentage of complete data (0-100)
        
    Returns:
        Tuple of (label, color) - color is green/yellow/red
    """
    if completeness >= 95:
        return "Excelente", "#2ecc71"  # Green
    elif completeness >= 80:
        return "Bueno", "#f1c40f"  # Yellow
    elif completeness >= 60:
        return "Regular", "#e67e22"  # Orange
    else:
        return "Crítico", "#e74c3c"  # Red
