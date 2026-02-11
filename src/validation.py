#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation Module for Finhike Risk Analysis Results
Objective: Validate the correctness of XML processing and metric calculations
"""

import pandas as pd
import xml.etree.ElementTree as ET
import os
import glob
from typing import Dict, List, Tuple
from xml_processor import XMLCreditDataProcessor

class ResultsValidator:
    """Validate XML processing results and calculated metrics"""
    
    def __init__(self, data_folder: str = "Data"):
        self.data_folder = data_folder
        self.validation_results = {}
        self.errors = []
        self.warnings = []
        
    def validate_all(self) -> Dict:
        """Run all validation checks"""
        print("=== STARTING VALIDATION ===")
        
        # 1. Validate XML file processing
        self.validate_xml_processing()
        
        # 2. Validate data transformation
        self.validate_data_transformation()
        
        # 3. Validate metric calculations
        self.validate_metric_calculations()
        
        # 4. Validate data quality
        self.validate_data_quality()
        
        # 5. Cross-validation with manual calculation
        self.cross_validate_metrics()
        
        # Generate validation report
        self.generate_validation_report()
        
        return self.validation_results
    
    def validate_xml_processing(self):
        """Validate that XML files are processed correctly"""
        print("1. Validating XML processing...")
        
        xml_files = glob.glob(os.path.join(self.data_folder, "*.xml"))
        
        if not xml_files:
            self.errors.append("No XML files found for validation")
            return
        
        processor = XMLCreditDataProcessor(self.data_folder)
        processor.process_all_xml_files()
        
        # Check that all XML files were processed
        processed_clients = len(processor.clients_data)
        expected_clients = len(xml_files)
        
        if processed_clients != expected_clients:
            self.errors.append(f"Expected {expected_clients} clients, but processed {processed_clients}")
        else:
            print(f"✅ All {processed_clients} XML files processed successfully")
        
        # Validate each client has deals
        clients_without_deals = []
        total_deals = 0
        
        for client in processor.clients_data:
            if not client['deals']:
                clients_without_deals.append(client['client_id'])
            else:
                total_deals += len(client['deals'])
        
        if clients_without_deals:
            self.warnings.append(f"Clients without deals: {clients_without_deals}")
        
        self.validation_results['xml_processing'] = {
            'total_files': len(xml_files),
            'processed_clients': processed_clients,
            'total_deals': total_deals,
            'clients_without_deals': len(clients_without_deals)
        }
        
        print(f"✅ Total deals extracted: {total_deals}")
        
    def validate_data_transformation(self):
        """Validate tabular data transformation"""
        print("\n2. Validating data transformation...")
        
        if not os.path.exists("detailed_credit_data.csv"):
            self.errors.append("Detailed credit data CSV not found")
            return
        
        df = pd.read_csv("detailed_credit_data.csv")
        
        # Check required columns
        required_columns = [
            'client_id', 'deal_id', 'transaction_amount', 'actual_end_date',
            'overdue_debt', 'days_overdue', 'deal_status'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.errors.append(f"Missing required columns: {missing_columns}")
        
        # Check data types and ranges
        if 'transaction_amount' in df.columns:
            negative_amounts = (df['transaction_amount'] < 0).sum()
            if negative_amounts > 0:
                self.warnings.append(f"Found {negative_amounts} negative transaction amounts")
        
        if 'days_overdue' in df.columns:
            invalid_overdue = (df['days_overdue'] < 0).sum()
            if invalid_overdue > 0:
                self.errors.append(f"Found {invalid_overdue} negative overdue days")
        
        # Check for duplicates
        if 'client_id' in df.columns and 'deal_id' in df.columns:
            duplicates = df.duplicated(['client_id', 'deal_id', 'period_month', 'period_year']).sum()
            if duplicates > 0:
                self.errors.append(f"Found {duplicates} duplicate records")
        
        self.validation_results['data_transformation'] = {
            'total_records': len(df),
            'unique_clients': df['client_id'].nunique() if 'client_id' in df.columns else 0,
            'unique_deals': df['deal_id'].nunique() if 'deal_id' in df.columns else 0,
            'missing_columns': len(missing_columns),
            'duplicate_records': duplicates if 'client_id' in df.columns else 0
        }
        
        print(f"✅ Tabular data: {len(df)} records, {df['client_id'].nunique()} clients")
        
    def validate_metric_calculations(self):
        """Validate calculated metrics"""
        print("\n3. Validating metric calculations...")
        
        if not os.path.exists("client_metrics_results.csv"):
            self.errors.append("Client metrics CSV not found")
            return
        
        metrics_df = pd.read_csv("client_metrics_results.csv")
        detailed_df = pd.read_csv("detailed_credit_data.csv")
        
        # Validate each client's metrics
        validation_errors = []
        
        for _, row in metrics_df.iterrows():
            client_id = row['client_id']
            client_data = detailed_df[detailed_df['client_id'] == client_id]
            
            # 1. Validate total loans count
            unique_deals = client_data['deal_id'].nunique()
            if unique_deals != row['total_loans_count']:
                validation_errors.append(
                    f"Client {client_id}: Expected {unique_deals} loans, got {row['total_loans_count']}"
                )
            
            # 2. Validate closed loans count
            latest_status = client_data.groupby('deal_id')['actual_end_date'].last()
            closed_count = ((latest_status.notna()) & 
                           (latest_status != '') & 
                           (latest_status != 'nan')).sum()
            if closed_count != row['closed_loans_count']:
                validation_errors.append(
                    f"Client {client_id}: Expected {closed_count} closed loans, got {row['closed_loans_count']}"
                )
            
            # 3. Validate closed loans ratio
            expected_ratio = closed_count / unique_deals if unique_deals > 0 else 0
            if abs(expected_ratio - row['closed_loans_ratio']) > 0.0001:
                validation_errors.append(
                    f"Client {client_id}: Expected ratio {expected_ratio:.4f}, got {row['closed_loans_ratio']}"
                )
            
            # 4. Validate expired 30+ amount
            latest_overdue = client_data.groupby('deal_id').agg({
                'overdue_debt': 'last',
                'days_overdue': 'last'
            }).reset_index()
            
            expired_30_plus = latest_overdue[
                (latest_overdue['days_overdue'] > 30) & 
                (latest_overdue['overdue_debt'].notna())
            ]['overdue_debt'].sum()
            
            if abs(expired_30_plus - row['expired_30_plus_amount']) > 0.01:
                validation_errors.append(
                    f"Client {client_id}: Expected expired amount {expired_30_plus:.2f}, got {row['expired_30_plus_amount']}"
                )
        
        if validation_errors:
            self.errors.extend(validation_errors)
        else:
            print("✅ All metric calculations are correct")
        
        self.validation_results['metric_calculations'] = {
            'total_clients': len(metrics_df),
            'calculation_errors': len(validation_errors)
        }
    
    def validate_data_quality(self):
        """Validate data quality and consistency"""
        print("\n4. Validating data quality...")
        
        detailed_df = pd.read_csv("detailed_credit_data.csv")
        
        quality_issues = []
        
        # Check for missing critical values
        critical_fields = ['client_id', 'deal_id', 'transaction_amount']
        for field in critical_fields:
            if field in detailed_df.columns:
                missing_count = detailed_df[field].isna().sum()
                if missing_count > 0:
                    quality_issues.append(f"Missing {field}: {missing_count} records")
        
        # Check date consistency
        if 'start_date' in detailed_df.columns and 'planned_end_date' in detailed_df.columns:
            date_issues = 0
            for _, row in detailed_df.iterrows():
                if pd.notna(row['start_date']) and pd.notna(row['planned_end_date']):
                    try:
                        start = pd.to_datetime(row['start_date'])
                        end = pd.to_datetime(row['planned_end_date'])
                        if start >= end:
                            date_issues += 1
                    except:
                        pass
            
            if date_issues > 0:
                quality_issues.append(f"Date consistency issues: {date_issues} records")
        
        # Check amount consistency
        if 'current_debt' in detailed_df.columns and 'overdue_debt' in detailed_df.columns:
            amount_issues = ((detailed_df['overdue_debt'] > detailed_df['current_debt']) & 
                           (detailed_df['overdue_debt'].notna()) & 
                           (detailed_df['current_debt'].notna())).sum()
            
            if amount_issues > 0:
                quality_issues.append(f"Overdue > Current debt: {amount_issues} records")
        
        if quality_issues:
            self.warnings.extend(quality_issues)
        else:
            print("✅ Data quality checks passed")
        
        self.validation_results['data_quality'] = {
            'quality_issues': len(quality_issues),
            'total_records_checked': len(detailed_df)
        }
    
    def cross_validate_metrics(self):
        """Cross-validate metrics with manual calculation"""
        print("\n5. Cross-validating with manual calculation...")
        
        # Manual calculation using direct XML parsing
        manual_metrics = self._manual_metric_calculation()
        
        if not os.path.exists("client_metrics_results.csv"):
            self.errors.append("Cannot cross-validate: metrics file missing")
            return
        
        calculated_metrics = pd.read_csv("client_metrics_results.csv")
        
        cross_validation_errors = []
        
        for client_id in manual_metrics:
            # Convert client_id to string to match CSV format
            calc_row = calculated_metrics[calculated_metrics['client_id'] == str(client_id)]
            if calc_row.empty:
                cross_validation_errors.append(f"Client {client_id} missing from calculated metrics")
                continue
            
            calc_row = calc_row.iloc[0]
            manual = manual_metrics[client_id]
            
            # Compare each metric
            if calc_row['total_loans_count'] != manual['total_loans']:
                cross_validation_errors.append(
                    f"Client {client_id} total loans mismatch: calc={calc_row['total_loans_count']}, manual={manual['total_loans']}"
                )
            
            if abs(calc_row['expired_30_plus_amount'] - manual['expired_30_plus']) > 0.01:
                cross_validation_errors.append(
                    f"Client {client_id} expired amount mismatch: calc={calc_row['expired_30_plus_amount']}, manual={manual['expired_30_plus']}"
                )
        
        if cross_validation_errors:
            self.errors.extend(cross_validation_errors)
        else:
            print("✅ Cross-validation passed")
        
        self.validation_results['cross_validation'] = {
            'validation_errors': len(cross_validation_errors),
            'clients_validated': len(manual_metrics)
        }
    
    def _manual_metric_calculation(self) -> Dict:
        """Manually calculate metrics for cross-validation"""
        manual_results = {}
        
        xml_files = glob.glob(os.path.join(self.data_folder, "*.xml"))
        
        for xml_file in xml_files:
            client_id = os.path.splitext(os.path.basename(xml_file))[0]
            
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                deals = root.findall('.//crdeal')
                total_loans = len(deals)
                
                expired_30_plus = 0
                
                for deal in deals:
                    # Get latest deallife for this deal
                    deal_histories = deal.findall('.//deallife')
                    if deal_histories:
                        # Find latest history by year/month
                        latest_history = max(deal_histories, 
                                           key=lambda x: (int(x.get('dlyear', '0')), int(x.get('dlmonth', '0'))))
                        
                        days_overdue = int(latest_history.get('dldayexp', '0'))
                        overdue_debt = float(latest_history.get('dlamtexp', '0') or '0')
                        
                        if days_overdue > 30:
                            expired_30_plus += overdue_debt
                
                manual_results[client_id] = {
                    'total_loans': total_loans,
                    'expired_30_plus': expired_30_plus
                }
                
            except Exception as e:
                self.warnings.append(f"Error in manual calculation for {client_id}: {e}")
        
        return manual_results
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "="*50)
        print("VALIDATION REPORT")
        print("="*50)
        
        if not self.errors and not self.warnings:
            print("🎉 ALL VALIDATIONS PASSED!")
        else:
            if self.errors:
                print(f"❌ ERRORS FOUND: {len(self.errors)}")
                for i, error in enumerate(self.errors, 1):
                    print(f"   {i}. {error}")
            
            if self.warnings:
                print(f"⚠️  WARNINGS: {len(self.warnings)}")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"   {i}. {warning}")
        
        print("\nVALIDATION SUMMARY:")
        for category, results in self.validation_results.items():
            print(f"- {category.replace('_', ' ').title()}:")
            for key, value in results.items():
                print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        # Save validation results
        validation_summary = {
            'validation_status': 'PASSED' if not self.errors else 'FAILED',
            'errors_count': len(self.errors),
            'warnings_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings,
            'detailed_results': {k: {k2: int(v2) if isinstance(v2, (pd.Int64Dtype, type(pd.NA))) else v2 
                                    for k2, v2 in v.items()} for k, v in self.validation_results.items()}
        }
        
        import json
        with open('validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(validation_summary, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Detailed validation report saved to: validation_report.json")
    
    def quick_validate(self) -> bool:
        """Quick validation for basic checks"""
        print("Running quick validation...")
        
        # Check if required files exist
        required_files = ["client_metrics_results.csv", "detailed_credit_data.csv"]
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ Missing required file: {file}")
                return False
        
        # Check if metrics make sense
        metrics_df = pd.read_csv("client_metrics_results.csv")
        
        # Basic sanity checks
        if (metrics_df['closed_loans_ratio'] > 1).any():
            print("❌ Invalid closed loans ratio (>1)")
            return False
        
        if (metrics_df['expired_30_plus_amount'] < 0).any():
            print("❌ Negative expired amounts found")
            return False
        
        if (metrics_df['total_loans_count'] <= 0).any():
            print("❌ Invalid total loans count")
            return False
        
        print("✅ Quick validation passed")
        return True

def main():
    """Run validation"""
    validator = ResultsValidator()
    
    # First run quick validation
    if not validator.quick_validate():
        print("❌ Quick validation failed. Please check the results first.")
        return False
    
    # Run full validation
    validator.validate_all()
    
    return len(validator.errors) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
