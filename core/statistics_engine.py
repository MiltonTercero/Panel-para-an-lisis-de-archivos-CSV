"""
StatisticsEngine class for EDA Panel Application.
Provides statistical analysis, outlier detection, and data quality assessment.
"""

from typing import Optional, Dict, List, Any, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import shapiro, skew, kurtosis

from utils.logger import LoggerMixin
from utils.helpers import safe_divide, create_quality_label


class StatisticsEngine(LoggerMixin):
    """
    Engine for statistical calculations, outlier detection, and data quality analysis.
    """
    
    def __init__(self):
        """Initialize StatisticsEngine."""
        self.log_info("StatisticsEngine initialized")
    
    # ==================== BASIC STATISTICS ====================
    
    def calculate_basic_stats(self, series: pd.Series) -> Dict[str, Any]:
        """
        Calculate basic descriptive statistics.
        
        Args:
            series: Pandas Series with data
            
        Returns:
            Dictionary with basic statistics
        """
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return self._empty_basic_stats()
        
        # Calculate mode (handle multimodal)
        mode_result = clean_series.mode()
        mode_value = mode_result.iloc[0] if len(mode_result) > 0 else None
        mode_count = len(mode_result)
        
        stats_dict = {
            'count': len(clean_series),
            'count_total': len(series),
            'missing': len(series) - len(clean_series),
            'missing_pct': safe_divide(len(series) - len(clean_series), len(series)) * 100,
            'mean': float(clean_series.mean()) if np.issubdtype(clean_series.dtype, np.number) else None,
            'median': float(clean_series.median()) if np.issubdtype(clean_series.dtype, np.number) else None,
            'mode': mode_value,
            'mode_count': mode_count,
            'std': float(clean_series.std()) if np.issubdtype(clean_series.dtype, np.number) else None,
            'variance': float(clean_series.var()) if np.issubdtype(clean_series.dtype, np.number) else None,
            'min': float(clean_series.min()) if np.issubdtype(clean_series.dtype, np.number) else clean_series.min(),
            'max': float(clean_series.max()) if np.issubdtype(clean_series.dtype, np.number) else clean_series.max(),
            'range': None,
            'unique': clean_series.nunique()
        }
        
        # Calculate range for numeric data
        if stats_dict['min'] is not None and stats_dict['max'] is not None:
            if np.issubdtype(clean_series.dtype, np.number):
                stats_dict['range'] = stats_dict['max'] - stats_dict['min']
        
        return stats_dict
    
    def _empty_basic_stats(self) -> Dict[str, Any]:
        """Return empty statistics structure."""
        return {
            'count': 0, 'count_total': 0, 'missing': 0, 'missing_pct': 0,
            'mean': None, 'median': None, 'mode': None, 'mode_count': 0,
            'std': None, 'variance': None, 'min': None, 'max': None,
            'range': None, 'unique': 0
        }
    
    # ==================== DISTRIBUTION STATISTICS ====================
    
    def calculate_distribution_stats(self, series: pd.Series) -> Dict[str, Any]:
        """
        Calculate distribution statistics.
        
        Args:
            series: Pandas Series with numeric data
            
        Returns:
            Dictionary with distribution statistics
        """
        clean_series = series.dropna()
        
        if len(clean_series) < 3 or not np.issubdtype(clean_series.dtype, np.number):
            return self._empty_distribution_stats()
        
        values = clean_series.values.astype(float)
        
        # Percentiles
        percentiles = {
            'p10': float(np.percentile(values, 10)),
            'p25': float(np.percentile(values, 25)),
            'p50': float(np.percentile(values, 50)),
            'p75': float(np.percentile(values, 75)),
            'p90': float(np.percentile(values, 90)),
            'p95': float(np.percentile(values, 95)),
            'p99': float(np.percentile(values, 99))
        }
        
        # Skewness and Kurtosis
        skewness = float(skew(values))
        kurt = float(kurtosis(values))
        
        # Normality test (Shapiro-Wilk) - limit sample size
        sample_size = min(len(values), 5000)
        if sample_size >= 3:
            sample = np.random.choice(values, size=sample_size, replace=False) if len(values) > sample_size else values
            try:
                shapiro_stat, shapiro_p = shapiro(sample)
                is_normal = shapiro_p > 0.05
            except Exception:
                shapiro_stat, shapiro_p = None, None
                is_normal = None
        else:
            shapiro_stat, shapiro_p = None, None
            is_normal = None
        
        # Interpret skewness
        if abs(skewness) < 0.5:
            skew_interpretation = "Simétrica"
        elif skewness > 0:
            skew_interpretation = "Asimetría positiva (cola derecha)"
        else:
            skew_interpretation = "Asimetría negativa (cola izquierda)"
        
        # Interpret kurtosis
        if abs(kurt) < 0.5:
            kurt_interpretation = "Mesocúrtica (normal)"
        elif kurt > 0:
            kurt_interpretation = "Leptocúrtica (colas pesadas)"
        else:
            kurt_interpretation = "Platicúrtica (colas ligeras)"
        
        return {
            'percentiles': percentiles,
            'skewness': skewness,
            'skew_interpretation': skew_interpretation,
            'kurtosis': kurt,
            'kurt_interpretation': kurt_interpretation,
            'shapiro_stat': float(shapiro_stat) if shapiro_stat else None,
            'shapiro_p_value': float(shapiro_p) if shapiro_p else None,
            'is_normal': is_normal,
            'iqr': percentiles['p75'] - percentiles['p25']
        }
    
    def _empty_distribution_stats(self) -> Dict[str, Any]:
        """Return empty distribution statistics structure."""
        return {
            'percentiles': {k: None for k in ['p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'p99']},
            'skewness': None, 'skew_interpretation': None,
            'kurtosis': None, 'kurt_interpretation': None,
            'shapiro_stat': None, 'shapiro_p_value': None,
            'is_normal': None, 'iqr': None
        }
    
    # ==================== MISSING DATA ANALYSIS ====================
    
    def analyze_missing_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze missing data across the entire dataset.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with missing data analysis
        """
        total_cells = df.size
        missing_matrix = df.isna()
        total_missing = missing_matrix.sum().sum()
        
        # Per-column analysis
        column_missing = []
        for col in df.columns:
            missing_count = df[col].isna().sum()
            total_count = len(df)
            column_missing.append({
                'column': col,
                'missing_count': int(missing_count),
                'missing_pct': safe_divide(missing_count, total_count) * 100,
                'complete_pct': safe_divide(total_count - missing_count, total_count) * 100
            })
        
        # Sort by missing percentage
        column_missing.sort(key=lambda x: x['missing_pct'], reverse=True)
        
        # Rows with any missing
        rows_with_missing = missing_matrix.any(axis=1).sum()
        
        # Complete rows
        complete_rows = len(df) - rows_with_missing
        
        return {
            'total_cells': total_cells,
            'total_missing': int(total_missing),
            'total_missing_pct': safe_divide(total_missing, total_cells) * 100,
            'columns_with_missing': sum(1 for c in column_missing if c['missing_count'] > 0),
            'total_columns': len(df.columns),
            'rows_with_missing': int(rows_with_missing),
            'complete_rows': int(complete_rows),
            'complete_rows_pct': safe_divide(complete_rows, len(df)) * 100,
            'column_details': column_missing
        }
    
    def analyze_column_missing(self, series: pd.Series) -> Dict[str, Any]:
        """
        Analyze missing data for a single column.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Dictionary with column missing data analysis
        """
        total = len(series)
        missing = series.isna().sum()
        
        # Detect pattern (simple heuristic)
        if missing == 0:
            pattern = "Sin valores faltantes"
            pattern_type = "none"
        elif missing == total:
            pattern = "Todos los valores faltantes"
            pattern_type = "complete"
        else:
            # Check for consecutive missing values
            missing_mask = series.isna()
            consecutive_groups = (missing_mask != missing_mask.shift()).cumsum()
            group_sizes = missing_mask.groupby(consecutive_groups).sum()
            max_consecutive = group_sizes.max() if len(group_sizes) > 0 else 0
            
            if max_consecutive > total * 0.1:
                pattern = "Patrón sistemático (valores consecutivos)"
                pattern_type = "systematic"
            else:
                pattern = "Patrón aleatorio"
                pattern_type = "random"
        
        # Recommendations
        recommendations = []
        missing_pct = safe_divide(missing, total) * 100
        
        if missing_pct == 0:
            recommendations.append("✓ No se requiere acción")
        elif missing_pct < 5:
            recommendations.append("• Eliminar filas con valores faltantes")
            recommendations.append("• Imputar con media/mediana (numéricos)")
            recommendations.append("• Imputar con moda (categóricos)")
        elif missing_pct < 20:
            recommendations.append("• Imputación múltiple recomendada")
            recommendations.append("• Imputar con KNN o modelo predictivo")
            recommendations.append("• Evitar eliminar filas")
        elif missing_pct < 50:
            recommendations.append("⚠ Alto porcentaje de faltantes")
            recommendations.append("• Considerar eliminar la columna")
            recommendations.append("• Crear variable indicadora de faltante")
        else:
            recommendations.append("❌ Mayoría de valores faltantes")
            recommendations.append("• Eliminar columna recomendado")
            recommendations.append("• No usar para análisis críticos")
        
        return {
            'total': total,
            'missing': int(missing),
            'missing_pct': missing_pct,
            'complete': total - missing,
            'complete_pct': safe_divide(total - missing, total) * 100,
            'pattern': pattern,
            'pattern_type': pattern_type,
            'recommendations': recommendations
        }
    
    # ==================== OUTLIER DETECTION ====================
    
    def detect_outliers_iqr(self, series: pd.Series, k: float = 1.5) -> Dict[str, Any]:
        """
        Detect outliers using IQR method.
        
        Args:
            series: Pandas Series with numeric data
            k: IQR multiplier (default 1.5)
            
        Returns:
            Dictionary with outlier detection results
        """
        clean_series = series.dropna()
        
        if len(clean_series) == 0 or not np.issubdtype(clean_series.dtype, np.number):
            return self._empty_outlier_result()
        
        q1 = clean_series.quantile(0.25)
        q3 = clean_series.quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr
        
        # Identify outliers
        outlier_mask = (clean_series < lower_bound) | (clean_series > upper_bound)
        outlier_indices = clean_series[outlier_mask].index.tolist()
        outlier_values = clean_series[outlier_mask].values.tolist()
        
        # Separate lower and upper outliers
        lower_outliers = clean_series[clean_series < lower_bound]
        upper_outliers = clean_series[clean_series > upper_bound]
        
        return {
            'method': 'IQR',
            'q1': float(q1),
            'q3': float(q3),
            'iqr': float(iqr),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outlier_count': len(outlier_indices),
            'outlier_pct': safe_divide(len(outlier_indices), len(clean_series)) * 100,
            'lower_outlier_count': len(lower_outliers),
            'upper_outlier_count': len(upper_outliers),
            'outlier_indices': outlier_indices[:100],  # Limit to 100
            'outlier_values': outlier_values[:100],
            'normal_min': float(clean_series[~outlier_mask].min()) if (~outlier_mask).any() else None,
            'normal_max': float(clean_series[~outlier_mask].max()) if (~outlier_mask).any() else None
        }
    
    def detect_outliers_zscore(self, series: pd.Series, threshold: float = 3.0) -> Dict[str, Any]:
        """
        Detect outliers using Z-score method.
        
        Args:
            series: Pandas Series with numeric data
            threshold: Z-score threshold (default 3.0)
            
        Returns:
            Dictionary with outlier detection results
        """
        clean_series = series.dropna()
        
        if len(clean_series) == 0 or not np.issubdtype(clean_series.dtype, np.number):
            return self._empty_outlier_result()
        
        mean = clean_series.mean()
        std = clean_series.std()
        
        if std == 0:
            return self._empty_outlier_result()
        
        z_scores = (clean_series - mean) / std
        
        # Identify outliers
        outlier_mask = np.abs(z_scores) > threshold
        outlier_indices = clean_series[outlier_mask].index.tolist()
        outlier_values = clean_series[outlier_mask].values.tolist()
        outlier_zscores = z_scores[outlier_mask].values.tolist()
        
        lower_bound = mean - threshold * std
        upper_bound = mean + threshold * std
        
        return {
            'method': 'Z-Score',
            'mean': float(mean),
            'std': float(std),
            'threshold': threshold,
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outlier_count': len(outlier_indices),
            'outlier_pct': safe_divide(len(outlier_indices), len(clean_series)) * 100,
            'outlier_indices': outlier_indices[:100],
            'outlier_values': outlier_values[:100],
            'outlier_zscores': outlier_zscores[:100],
            'normal_min': float(clean_series[~outlier_mask].min()) if (~outlier_mask).any() else None,
            'normal_max': float(clean_series[~outlier_mask].max()) if (~outlier_mask).any() else None
        }
    
    def _empty_outlier_result(self) -> Dict[str, Any]:
        """Return empty outlier detection result."""
        return {
            'method': None,
            'outlier_count': 0,
            'outlier_pct': 0,
            'outlier_indices': [],
            'outlier_values': [],
            'lower_bound': None,
            'upper_bound': None
        }
    
    def get_outlier_summary(self, series: pd.Series) -> Dict[str, Any]:
        """
        Get combined outlier summary using both methods.
        
        Args:
            series: Pandas Series with numeric data
            
        Returns:
            Dictionary with combined outlier analysis
        """
        iqr_result = self.detect_outliers_iqr(series)
        zscore_result = self.detect_outliers_zscore(series)
        
        # Recommendations based on outlier analysis
        recommendations = []
        
        iqr_pct = iqr_result.get('outlier_pct', 0)
        zscore_pct = zscore_result.get('outlier_pct', 0)
        
        if iqr_pct == 0 and zscore_pct == 0:
            recommendations.append("✓ No se detectaron outliers")
        elif iqr_pct < 5:
            recommendations.append("• Outliers moderados - revisar individualmente")
            recommendations.append("• Considerar winsorización")
            recommendations.append("• Usar estadísticos robustos (mediana)")
        else:
            recommendations.append("⚠ Alto número de outliers")
            recommendations.append("• Verificar errores de entrada")
            recommendations.append("• Considerar transformación logarítmica")
            recommendations.append("• Aplicar técnicas de truncamiento")
        
        return {
            'iqr': iqr_result,
            'zscore': zscore_result,
            'recommendations': recommendations
        }
    
    # ==================== DATA QUALITY SUMMARY ====================
    
    def get_quality_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get overall data quality summary.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with quality summary
        """
        missing_analysis = self.analyze_missing_data(df)
        
        # Calculate overall quality score
        completeness = 100 - missing_analysis['total_missing_pct']
        
        # Analyze outliers in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        total_outliers = 0
        outlier_columns = 0
        
        for col in numeric_cols:
            iqr_result = self.detect_outliers_iqr(df[col])
            if iqr_result['outlier_count'] > 0:
                total_outliers += iqr_result['outlier_count']
                outlier_columns += 1
        
        # Quality label
        quality_label, quality_color = create_quality_label(completeness)
        
        # Issues list
        issues = []
        if missing_analysis['total_missing_pct'] > 5:
            issues.append(f"Datos faltantes: {missing_analysis['total_missing_pct']:.1f}%")
        if outlier_columns > 0:
            issues.append(f"Columnas con outliers: {outlier_columns}")
        
        return {
            'completeness': completeness,
            'quality_label': quality_label,
            'quality_color': quality_color,
            'missing_analysis': missing_analysis,
            'total_outliers': total_outliers,
            'outlier_columns': outlier_columns,
            'issues': issues,
            'has_issues': len(issues) > 0
        }
