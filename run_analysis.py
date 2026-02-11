#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main runner for Finhike Risk Analysis
Runs from project root directory
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from xml_processor import XMLCreditDataProcessor

def main():
    """Run analysis from project root"""
    print("=== FINHIKE RISK ANALYSIS ===")
    print("Running from project root...")
    
    # Initialize processor with correct data path
    data_folder = "data" if os.path.exists("data") else "Data"
    processor = XMLCreditDataProcessor(data_folder)
    
    # Process files
    processor.process_all_xml_files()
    
    # Export to output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results to output directory
    metrics_df = processor.calculate_client_metrics()
    if not metrics_df.empty:
        metrics_df.to_csv(os.path.join(output_dir, "client_metrics_results.csv"), index=False)
        print(f"✅ Results saved to {output_dir}/client_metrics_results.csv")
        
        # Also save detailed data
        if processor.results_df is not None and not processor.results_df.empty:
            processor.results_df.to_csv(os.path.join(output_dir, "detailed_credit_data.csv"), index=False)
            print(f"✅ Detailed data saved to {output_dir}/detailed_credit_data.csv")
    
    # Print summary
    processor.print_summary()
    
    return processor, metrics_df

if __name__ == "__main__":
    processor, results = main()
