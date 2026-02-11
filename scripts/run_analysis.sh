#!/bin/bash

# Finhike Risk Analysis - Quick Start Script
# This script sets up the environment and runs the analysis

echo "=== Finhike Risk Data Analysis ==="
echo "Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install pandas lxml

# Run the analysis
echo "Running XML data analysis..."
python xml_processor.py

echo "=== Analysis Complete ==="
echo "Results files generated:"
echo "- client_metrics_results.csv"
echo "- detailed_credit_data.csv" 
echo "- analysis_report.md"

echo ""
echo "Please check the files for your results."
echo "Send client_metrics_results.csv and xml_processor.py to a.jersovs@finhike.com"
