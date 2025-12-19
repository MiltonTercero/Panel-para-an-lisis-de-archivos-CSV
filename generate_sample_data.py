"""
Sample data generator for testing the EDA Panel application.
Creates a CSV file with various data types, missing values, and outliers.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def generate_sample_data(n_rows: int = 500, output_path: str = "sample_data.csv"):
    """
    Generate sample data for testing EDA Panel.
    
    Args:
        n_rows: Number of rows to generate
        output_path: Output file path
    """
    np.random.seed(42)
    
    # Generate base data
    data = {
        # Numeric columns with different distributions
        'edad': np.random.normal(35, 12, n_rows).astype(int).clip(18, 80),
        'salario': np.random.lognormal(10.5, 0.5, n_rows).astype(int),
        'puntuacion': np.random.uniform(0, 100, n_rows).round(2),
        'horas_trabajadas': np.random.poisson(40, n_rows),
        
        # Categorical columns
        'departamento': np.random.choice(
            ['Ventas', 'TI', 'Marketing', 'Recursos Humanos', 'Finanzas', 'Operaciones'],
            n_rows, p=[0.25, 0.20, 0.15, 0.15, 0.15, 0.10]
        ),
        'nivel_educacion': np.random.choice(
            ['Secundaria', 'Universitario', 'Maestría', 'Doctorado'],
            n_rows, p=[0.15, 0.45, 0.30, 0.10]
        ),
        'genero': np.random.choice(['M', 'F', 'Otro'], n_rows, p=[0.48, 0.48, 0.04]),
        'estado_civil': np.random.choice(
            ['Soltero', 'Casado', 'Divorciado', 'Viudo'],
            n_rows, p=[0.35, 0.45, 0.15, 0.05]
        ),
        
        # Boolean column
        'activo': np.random.choice([True, False], n_rows, p=[0.85, 0.15]),
        
        # Date column
        'fecha_contratacion': [
            (datetime.now() - timedelta(days=np.random.randint(1, 3650))).strftime('%Y-%m-%d')
            for _ in range(n_rows)
        ],
        
        # ID column
        'id_empleado': [f'EMP{str(i).zfill(5)}' for i in range(1, n_rows + 1)]
    }
    
    df = pd.DataFrame(data)
    
    # Add outliers to numeric columns
    # Salary outliers (very high)
    outlier_indices = np.random.choice(n_rows, size=int(n_rows * 0.03), replace=False)
    df.loc[outlier_indices, 'salario'] = df.loc[outlier_indices, 'salario'] * 5
    
    # Age outliers (some impossible values)
    age_outliers = np.random.choice(n_rows, size=int(n_rows * 0.02), replace=False)
    df.loc[age_outliers, 'edad'] = np.random.choice([95, 100, 105], size=len(age_outliers))
    
    # Score outliers (some above 100 - data entry errors)
    score_outliers = np.random.choice(n_rows, size=int(n_rows * 0.01), replace=False)
    df.loc[score_outliers, 'puntuacion'] = np.random.uniform(110, 150, len(score_outliers))
    
    # Add missing values
    # Random missing in salary (5%)
    salary_missing = np.random.choice(n_rows, size=int(n_rows * 0.05), replace=False)
    df.loc[salary_missing, 'salario'] = np.nan
    
    # Random missing in score (8%)
    score_missing = np.random.choice(n_rows, size=int(n_rows * 0.08), replace=False)
    df.loc[score_missing, 'puntuacion'] = np.nan
    
    # Random missing in department (3%)
    dept_missing = np.random.choice(n_rows, size=int(n_rows * 0.03), replace=False)
    df.loc[dept_missing, 'departamento'] = np.nan
    
    # Systematic missing in education (for older employees)
    old_employees = df[df['edad'] > 60].index
    edu_missing = np.random.choice(old_employees, size=min(len(old_employees), int(n_rows * 0.03)), replace=False)
    df.loc[edu_missing, 'nivel_educacion'] = np.nan
    
    # Random missing in hours (2%)
    hours_missing = np.random.choice(n_rows, size=int(n_rows * 0.02), replace=False)
    df.loc[hours_missing, 'horas_trabajadas'] = np.nan
    
    # Reorder columns
    df = df[['id_empleado', 'edad', 'genero', 'estado_civil', 'nivel_educacion',
             'departamento', 'salario', 'horas_trabajadas', 'puntuacion', 
             'fecha_contratacion', 'activo']]
    
    # Save to CSV
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Sample data generated: {output_path}")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    print(f"Missing values: {df.isna().sum().sum()}")
    
    return df


if __name__ == "__main__":
    generate_sample_data()
