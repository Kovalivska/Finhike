#!/bin/bash

echo "=== FINHIKE RISK ANALYSIS - FULL VALIDATION ==="
echo "Date: $(date)"
echo "================================================"

# Check if virtual environment exists and activate it
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found, using system Python"
fi

# Run the main analysis
echo -e "\n1. Running XML processing and analysis..."
python xml_processor.py

# Check if analysis was successful
if [ $? -eq 0 ]; then
    echo "✅ Analysis completed successfully"
else
    echo "❌ Analysis failed"
    exit 1
fi

# Run comprehensive validation
echo -e "\n2. Running comprehensive validation..."
python validation.py

# Check validation results
if [ $? -eq 0 ]; then
    echo "✅ All validations passed"
else
    echo "❌ Validation failed - please check the errors"
    exit 1
fi

# Generate summary statistics
echo -e "\n3. Generating summary statistics..."
python -c "
import pandas as pd
import json

# Load results
try:
    metrics = pd.read_csv('client_metrics_results.csv')
    detailed = pd.read_csv('detailed_credit_data.csv')
    
    print('\\n=== FINAL SUMMARY STATISTICS ===')
    print(f'Total clients analyzed: {len(metrics)}')
    print(f'Total credit deals: {detailed[\"deal_id\"].nunique()}')
    print(f'Total historical records: {len(detailed)}')
    print(f'Average loans per client: {metrics[\"total_loans_count\"].mean():.1f}')
    print(f'Overall closure rate: {metrics[\"closed_loans_ratio\"].mean():.1%}')
    print(f'Total expired debt (30+ days): {metrics[\"expired_30_plus_amount\"].sum():,.2f} UAH')
    
    # Top risk clients
    top_risk = metrics.nlargest(3, 'expired_30_plus_amount')
    if not top_risk.empty:
        print('\\nTop 3 risk clients by expired debt:')
        for _, row in top_risk.iterrows():
            print(f'  • Client {row[\"client_id\"]}: {row[\"expired_30_plus_amount\"]:,.2f} UAH')
    
    print('\\n✅ Summary statistics generated successfully')
    
except Exception as e:
    print(f'❌ Error generating statistics: {e}')
    exit(1)
"

# List all generated files
echo -e "\n4. Generated files:"
ls -la *.csv *.json *.md | grep -E '\.(csv|json|md)$' | awk '{print "  • " $9 " (" $5 " bytes)"}'

echo -e "\n=== VALIDATION COMPLETE ==="
echo "All files are ready for submission to a.jersovs@finhike.com"
