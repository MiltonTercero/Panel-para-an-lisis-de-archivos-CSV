#!/usr/bin/env python3
"""
EDA Panel - Advanced Exploratory Data Analysis Application
Main entry point for the application.

Features:
- Load CSV, Excel, JSON datasets with auto-encoding detection
- Dataset summary with quality indicators
- Variable selection with filtering
- Comprehensive statistics (basic, distribution, quality)
- Advanced visualizations (histograms, boxplots, outliers, missing data)
- PDF report generation
- Dark theme interface

Usage:
    python main.py

Requirements:
    pip install -r requirements.txt
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import main


if __name__ == "__main__":
    main()
