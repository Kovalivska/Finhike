# Finhike Risk Analysis - Submission Package

## Assignment Completion

✅ **Task 1:** XML files reviewed and processed (5 clients, 634 deals)
✅ **Task 2:** Data transformed to tabular format (1,967 records)
✅ **Task 3:** Client metrics calculated for all clients

## Key Results

| Client ID | Total Loans | Closed Ratio | Expired 30+ Days |
|-----------|-------------|--------------|------------------|
| 2333123   | 416         | 95.67%       | 0.00 UAH        |
| 2402782   | 23          | 39.13%       | 0.00 UAH        |
| 2426982   | 20          | 35.00%       | 0.00 UAH        |
| 2441859   | 116         | 92.24%       | 16,585.21 UAH   |
| 2444357   | 55          | 85.45%       | 72,383.46 UAH   |

**Portfolio Summary:**
- Total risk exposure (30+ days): 88,968.67 UAH
- Average closure rate: 69.5%
- High-risk clients: 2 out of 5

## Files Included

### Required Files:
1. **results_report.md** - Detailed analysis results and methodology
2. **xml_processor.py** - Python code for data processing and calculations
3. **sql_solution.sql** - Alternative SQL solution

### Supporting Files:
- **client_metrics_results.csv** - Final calculated metrics
- **detailed_credit_data.csv** - Complete tabular dataset
- **validation.py** - Validation code ensuring result accuracy
- **README.md** - Technical documentation
- **final_analysis_report.json** - Machine-readable analysis results

## Solution Reproducibility

The solution is fully reproducible:
1. Install requirements: `pip install pandas lxml`
2. Place XML files in `Data/` folder
3. Run: `python xml_processor.py`

## Validation Status

✅ All validations passed
✅ Calculations verified through cross-validation
✅ Data quality checks completed
✅ Results are accurate and consistent

---
*Analysis completed: February 11, 2026*
*Ready for submission to: a.jersovs@finhike.com*
