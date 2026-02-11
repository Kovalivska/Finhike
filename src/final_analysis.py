#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final validation and report generation for Finhike Risk Analysis
"""

from xml_processor import XMLCreditDataProcessor
import pandas as pd
import json

def run_final_analysis():
    """Run final analysis with comprehensive reporting"""
    print("=== FINHIKE RISK ANALYSIS - FINAL RUN ===")
    
    # Initialize processor
    processor = XMLCreditDataProcessor()
    
    # Check data folder
    if not processor.data_folder == "Data" and os.path.exists("Data"):
        processor.data_folder = "Data"
    
    # Process all XML files
    print("1. Processing XML files...")
    processor.process_all_xml_files()
    
    # Export results
    print("2. Calculating metrics and exporting results...")
    metrics_df = processor.export_results()
    
    # Print summary with validation
    processor.print_summary()
    
    # Generate final report
    print("\n3. Generating final report...")
    generate_final_report(processor, metrics_df)
    
    return processor, metrics_df

def generate_final_report(processor, metrics_df):
    """Generate comprehensive final report"""
    
    # Load detailed data
    detailed_df = pd.read_csv("detailed_credit_data.csv")
    
    report = {
        'analysis_summary': {
            'total_clients': len(processor.clients_data),
            'total_deals': sum(len(client['deals']) for client in processor.clients_data),
            'total_historical_records': len(detailed_df),
            'unique_deals': detailed_df['deal_id'].nunique(),
            'analysis_date': '2026-02-11'
        },
        'client_metrics': metrics_df.to_dict('records'),
        'portfolio_summary': {
            'average_loans_per_client': metrics_df['total_loans_count'].mean(),
            'overall_closure_rate': metrics_df['closed_loans_ratio'].mean(),
            'total_expired_debt': metrics_df['expired_30_plus_amount'].sum(),
            'clients_with_expired_debt': (metrics_df['expired_30_plus_amount'] > 0).sum()
        },
        'data_quality': {
            'records_processed': len(detailed_df),
            'unique_clients': detailed_df['client_id'].nunique(),
            'date_range': {
                'earliest_period': f"{detailed_df['period_year'].min()}-{detailed_df['period_month'].min():02d}",
                'latest_period': f"{detailed_df['period_year'].max()}-{detailed_df['period_month'].max():02d}"
            }
        }
    }
    
    # Save comprehensive report
    with open('final_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print("✅ Final report saved to: final_analysis_report.json")
    
    # Print key findings
    print("\n=== KEY FINDINGS ===")
    print(f"📊 Portfolio size: {report['analysis_summary']['total_deals']} deals across {report['analysis_summary']['total_clients']} clients")
    print(f"📈 Average closure rate: {report['portfolio_summary']['overall_closure_rate']:.1%}")
    print(f"🚨 Total risk exposure (30+ days): {report['portfolio_summary']['total_expired_debt']:,.2f} UAH")
    print(f"⚠️  High-risk clients: {report['portfolio_summary']['clients_with_expired_debt']}/{report['analysis_summary']['total_clients']}")
    
    # Top risk clients
    top_risk = metrics_df.nlargest(3, 'expired_30_plus_amount')
    if not top_risk[top_risk['expired_30_plus_amount'] > 0].empty:
        print("\n📋 Top risk clients:")
        for _, row in top_risk[top_risk['expired_30_plus_amount'] > 0].iterrows():
            risk_ratio = row['expired_30_plus_amount'] / report['portfolio_summary']['total_expired_debt'] * 100
            print(f"   • Client {row['client_id']}: {row['expired_30_plus_amount']:,.2f} UAH ({risk_ratio:.1f}% of total risk)")

if __name__ == "__main__":
    import os
    processor, metrics = run_final_analysis()
    print("\n🎉 Analysis complete! All files ready for submission.")
