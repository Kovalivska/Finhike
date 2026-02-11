#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML Data Processor for Finhike Risk Analysis Task
Objective: Transform XML credit data into tabular format and calculate client metrics
"""

import xml.etree.ElementTree as ET
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Tuple
import glob

class XMLCreditDataProcessor:
    """Process XML credit data files and calculate client-level metrics"""
    
    def __init__(self, data_folder: str = "Data"):
        self.data_folder = data_folder
        self.clients_data = []
        self.results_df = None
        
    def parse_xml_file(self, xml_file_path: str) -> Dict:
        """
        Parse a single XML file (one client) and extract credit deal information
        
        Args:
            xml_file_path (str): Path to XML file
            
        Returns:
            Dict: Parsed client data with deals and their history
        """
        client_data = {
            'client_file': os.path.basename(xml_file_path),
            'client_id': os.path.splitext(os.path.basename(xml_file_path))[0],
            'deals': []
        }
        
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # Parse each credit deal (crdeal block)
            for crdeal in root.findall('.//crdeal'):
                deal_info = self._parse_deal_info(crdeal)
                
                # Parse deal history (deallife blocks)
                deal_history = []
                for deallife in crdeal.findall('.//deallife'):
                    history_record = self._parse_deal_history(deallife)
                    deal_history.append(history_record)
                
                deal_info['history'] = deal_history
                client_data['deals'].append(deal_info)
                
        except ET.ParseError as e:
            print(f"Error parsing {xml_file_path}: {e}")
        except Exception as e:
            print(f"Unexpected error processing {xml_file_path}: {e}")
            
        return client_data
    
    def _parse_deal_info(self, crdeal_element) -> Dict:
        """Parse basic deal information from crdeal element"""
        deal_info = {}
        
        # Key deal fields from attributes
        attributes_to_extract = [
            'dlref',      # Transaction ID
            'lng',        # Part presentation
            'dlcelcred',  # Transaction type
            'dlvidobes',  # Type of collateral
            'dlporpog',   # Redemption plan
            'dlcurr',     # Transaction currency
            'dlamt',      # Transaction amount (initial)
            'dldonor',    # Information provider
            'dldonornum', # Unique number of creditor
            'primarydebt', # CHS type under main agreement
            'dlrolesub',  # Subject's role
            'dlamtobes',  # Collateral value in base currency
            'bdate',      # Birth date (additional field)
            'dlcelcredref', # Transaction type reference
            'dlcurrref',  # Currency reference
            'dlporpogref', # Redemption plan reference
            'dlrolesubref', # Subject's role reference
            'dlvidobesref', # Collateral type reference
            'lngref'      # Language reference
        ]
        
        for field in attributes_to_extract:
            deal_info[field] = crdeal_element.get(field)
                
        return deal_info
    
    def _parse_deal_history(self, deallife_element) -> Dict:
        """Parse deal history from deallife element"""
        history_record = {}
        
        # Key history fields from attributes
        attributes_to_extract = [
            'dlref',        # Transaction ID
            'dlmonth',      # Data period (month)
            'dlyear',       # Data period (year)
            'dlds',         # Transaction commencement date
            'dldpf',        # Transaction closing date under contract
            'dldff',        # Actual transaction end date
            'dlflstat',     # Transaction status in current period
            'dlflstatref',  # Transaction status reference
            'dlamtlim',     # Current transaction limit
            'dlamtpaym',    # Planned compulsory payment amount
            'dlamtcur',     # Current debt amount
            'dlamtexp',     # Current debt overdue amount
            'dldayexp',     # Current number of days overdue
            'dlflpay',      # Indication of payment made
            'dlflpayref',   # Payment made reference
            'dlflbrk',      # Indication of arrears present
            'dlflbrkref',   # Arrears present reference
            'dlfluse',      # Indication of credit tranche made
            'dlfluseref',   # Credit tranche reference
            'dldateclc'     # Calculation date
        ]
        
        for field in attributes_to_extract:
            history_record[field] = deallife_element.get(field)
                
        return history_record
    
    def process_all_xml_files(self) -> List[Dict]:
        """Process all XML files in the data folder"""
        xml_files = glob.glob(os.path.join(self.data_folder, "*.xml"))
        
        if not xml_files:
            print(f"No XML files found in {self.data_folder} folder")
            return []
        
        print(f"Found {len(xml_files)} XML files to process")
        
        for xml_file in xml_files:
            print(f"Processing: {xml_file}")
            client_data = self.parse_xml_file(xml_file)
            self.clients_data.append(client_data)
            
        return self.clients_data
    
    def create_tabular_format(self) -> pd.DataFrame:
        """Convert parsed XML data to tabular format"""
        tabular_data = []
        
        for client in self.clients_data:
            client_id = client['client_id']
            
            for deal in client['deals']:
                deal_id = deal.get('dlref', 'Unknown')
                
                # Basic deal info
                base_record = {
                    'client_id': client_id,
                    'client_file': client['client_file'],
                    'deal_id': deal_id,
                    'transaction_amount': self._safe_float(deal.get('dlamt')),
                    'transaction_type': deal.get('dlcelcred'),
                    'currency': deal.get('dlcurr'),
                    'collateral_type': deal.get('dlvidobes'),
                    'subject_role': deal.get('dlrolesub'),
                    'collateral_value': self._safe_float(deal.get('dlamtobes'))
                }
                
                # Add history records
                for history in deal.get('history', []):
                    record = base_record.copy()
                    record.update({
                        'period_month': self._safe_int(history.get('dlmonth')),
                        'period_year': self._safe_int(history.get('dlyear')),
                        'start_date': history.get('dlds'),
                        'planned_end_date': history.get('dldpf'),
                        'actual_end_date': history.get('dldff'),
                        'deal_status': self._safe_int(history.get('dlflstat')),
                        'current_limit': self._safe_float(history.get('dlamtlim')),
                        'planned_payment': self._safe_float(history.get('dlamtpaym')),
                        'current_debt': self._safe_float(history.get('dlamtcur')),
                        'overdue_debt': self._safe_float(history.get('dlamtexp')),
                        'days_overdue': self._safe_int(history.get('dldayexp')),
                        'payment_made': self._safe_int(history.get('dlflpay')),
                        'arrears_present': self._safe_int(history.get('dlflbrk')),
                        'calculation_date': history.get('dldateclc')
                    })
                    tabular_data.append(record)
        
        df = pd.DataFrame(tabular_data)
        
        # Remove duplicates based on key fields
        df = df.drop_duplicates(subset=['client_id', 'deal_id', 'period_month', 'period_year'], keep='last')
        
        return df
    
    def _safe_float(self, value):
        """Safely convert value to float"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value):
        """Safely convert value to int"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def calculate_client_metrics(self) -> pd.DataFrame:
        """Calculate required metrics for each client"""
        if self.results_df is None:
            self.results_df = self.create_tabular_format()
        
        if self.results_df.empty:
            print("No data available for metrics calculation")
            return pd.DataFrame()
        
        # Group by client and deal to get unique deals per client
        deal_summary = self.results_df.groupby(['client_id', 'deal_id']).agg({
            'deal_status': 'last',  # Take last status for each deal
            'actual_end_date': 'last',
            'overdue_debt': 'last',
            'days_overdue': 'last'
        }).reset_index()
        
        # Calculate metrics for each client
        client_metrics = []
        
        for client_id in deal_summary['client_id'].unique():
            client_deals = deal_summary[deal_summary['client_id'] == client_id]
            
            # 1. Total count of loans
            total_loans = len(client_deals)
            
            # 2. Ratio of closed loans count over total loans count
            # A loan is closed if it has actual_end_date filled (not empty string)
            closed_loans = client_deals[
                (client_deals['actual_end_date'].notna()) & 
                (client_deals['actual_end_date'] != '') & 
                (client_deals['actual_end_date'] != 'nan')
            ].shape[0]
            closed_ratio = closed_loans / total_loans if total_loans > 0 else 0
            
            # 3. Sum of currently expired deals amount over 30+ days
            expired_30_plus = client_deals[
                (client_deals['days_overdue'] > 30) & 
                (client_deals['overdue_debt'].notna()) &
                (client_deals['overdue_debt'] > 0)
            ]['overdue_debt'].sum()
            
            client_metrics.append({
                'client_id': client_id,
                'total_loans_count': total_loans,
                'closed_loans_count': closed_loans,
                'closed_loans_ratio': round(closed_ratio, 4),
                'expired_30_plus_amount': round(expired_30_plus, 2) if pd.notna(expired_30_plus) else 0
            })
        
        return pd.DataFrame(client_metrics)
    
    def export_results(self, output_file: str = "client_metrics_results.csv"):
        """Export calculated metrics to CSV file"""
        metrics_df = self.calculate_client_metrics()
        
        if not metrics_df.empty:
            metrics_df.to_csv(output_file, index=False)
            print(f"Results exported to {output_file}")
            
            # Also save detailed tabular data
            detailed_file = "detailed_credit_data.csv"
            if self.results_df is not None and not self.results_df.empty:
                self.results_df.to_csv(detailed_file, index=False)
                print(f"Detailed data exported to {detailed_file}")
            
            return metrics_df
        else:
            print("No metrics calculated - no data available")
            return pd.DataFrame()
    
    def validate_results(self) -> Dict:
        """Validate the calculated results"""
        validation_results = {'status': 'PASSED', 'issues': []}
        
        if self.results_df is None or self.results_df.empty:
            validation_results['status'] = 'FAILED'
            validation_results['issues'].append("No tabular data available for validation")
            return validation_results
        
        metrics_df = self.calculate_client_metrics()
        if metrics_df.empty:
            validation_results['status'] = 'FAILED'
            validation_results['issues'].append("No metrics calculated for validation")
            return validation_results
        
        # Validate each client's metrics
        for _, row in metrics_df.iterrows():
            client_id = row['client_id']
            client_data = self.results_df[self.results_df['client_id'] == client_id]
            
            # 1. Check total loans count
            unique_deals = client_data['deal_id'].nunique()
            if unique_deals != row['total_loans_count']:
                validation_results['issues'].append(
                    f"Client {client_id}: Deal count mismatch - expected {unique_deals}, got {row['total_loans_count']}"
                )
            
            # 2. Check closed loans ratio is within valid range
            if not 0 <= row['closed_loans_ratio'] <= 1:
                validation_results['issues'].append(
                    f"Client {client_id}: Invalid closed ratio {row['closed_loans_ratio']} (should be 0-1)"
                )
            
            # 3. Check expired amount is not negative
            if row['expired_30_plus_amount'] < 0:
                validation_results['issues'].append(
                    f"Client {client_id}: Negative expired amount {row['expired_30_plus_amount']}"
                )
            
            # 4. Check data consistency
            latest_status = client_data.groupby('deal_id').agg({
                'actual_end_date': 'last',
                'overdue_debt': 'last',
                'days_overdue': 'last'
            }).reset_index()
            
            # Validate expired debt calculation
            manual_expired = latest_status[
                (latest_status['days_overdue'] > 30) & 
                (latest_status['overdue_debt'].notna())
            ]['overdue_debt'].sum()
            
            if abs(manual_expired - row['expired_30_plus_amount']) > 0.01:
                validation_results['issues'].append(
                    f"Client {client_id}: Expired amount calculation error - expected {manual_expired:.2f}, got {row['expired_30_plus_amount']}"
                )
        
        if validation_results['issues']:
            validation_results['status'] = 'FAILED'
        
        return validation_results

    def print_summary(self):
        """Print summary of processed data"""
        if not self.clients_data:
            print("No data processed yet. Run process_all_xml_files() first.")
            return
        
        print(f"\n=== DATA PROCESSING SUMMARY ===")
        print(f"Total clients processed: {len(self.clients_data)}")
        
        total_deals = sum(len(client['deals']) for client in self.clients_data)
        print(f"Total deals processed: {total_deals}")
        
        if self.results_df is not None:
            print(f"Total records in tabular format: {len(self.results_df)}")
        
        # Calculate and display metrics
        metrics_df = self.calculate_client_metrics()
        if not metrics_df.empty:
            print(f"\n=== CLIENT METRICS ===")
            print(metrics_df.to_string(index=False))
        
        # Run validation
        print(f"\n=== VALIDATION RESULTS ===")
        validation = self.validate_results()
        if validation['status'] == 'PASSED':
            print("✅ All validations PASSED")
        else:
            print("❌ Validation FAILED:")
            for issue in validation['issues']:
                print(f"  - {issue}")
        
        print(f"\n=== FILES GENERATED ===")
        print("- client_metrics_results.csv (final metrics)")
        print("- detailed_credit_data.csv (detailed tabular data)")

def main():
    """Main execution function"""
    processor = XMLCreditDataProcessor()
    
    # Check if Data folder exists, if not try sample_data
    if not os.path.exists(processor.data_folder):
        if os.path.exists("sample_data"):
            print(f"{processor.data_folder} folder not found, using sample_data for demonstration...")
            processor.data_folder = "sample_data"
        else:
            print(f"Error: {processor.data_folder} folder not found!")
            print("Please ensure the Data folder with XML files is in the current directory.")
            return
    
    # Process all XML files
    processor.process_all_xml_files()
    
    # Export results
    results_df = processor.export_results()
    
    # Print summary
    processor.print_summary()
    
    return processor, results_df

if __name__ == "__main__":
    processor, results = main()
