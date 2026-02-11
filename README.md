# Finhike Risk Data Analysis 🏦

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-success.svg)](https://github.com/Kovalivska/Finhike)

> **Comprehensive XML-based credit risk analysis solution for financial institutions**

## 📋 Project Overview

This project processes XML files containing credit deal information and calculates client-level risk metrics. Built as a technical assessment for Finhike, it demonstrates advanced data processing, validation, and reporting capabilities.

### 🎯 Key Results
- **Processed:** 5 client XML files (634 deals, 1,967 records)
- **Portfolio closure rate:** 69.5% average
- **Risk exposure:** 88,968.67 UAH in 30+ day overdue debt
- **High-risk clients:** 2 out of 5 identified

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Kovalivska/Finhike.git
cd Finhike

# Run with sample data
chmod +x scripts/run_analysis.sh
./scripts/run_analysis.sh

# Or run the Python script directly
python src/xml_processor.py
```

## 📊 Calculated Metrics

For each client, the system calculates:

1. **Total loans count** - Number of unique credit deals
2. **Closed loans ratio** - Percentage of deals with actual end dates
3. **Expired 30+ days amount** - Sum of overdue debt exceeding 30 days

## 🏗️ Project Structure

```
Finhike/
├── src/
│   ├── xml_processor.py      # Main processing engine
│   ├── validation.py         # Data validation module
│   ├── final_analysis.py     # Comprehensive analysis
│   └── sql_solution.sql      # Alternative SQL solution
├── scripts/
│   ├── run_analysis.sh       # Quick start script
│   └── run_full_validation.sh # Complete validation
├── sample_data/              # Demo XML files
├── submission_files/         # Ready-to-submit outputs
└── reports/                  # Analysis documentation
```

## 💻 Technical Implementation

### Python Solution Features
- ✅ **XML Parsing** - Robust ElementTree-based processing
- ✅ **Data Validation** - Comprehensive error checking
- ✅ **Pandas Integration** - Efficient tabular operations  
- ✅ **CSV Export** - Standard format outputs
- ✅ **JSON Reports** - Structured analysis results

### SQL Alternative
- PostgreSQL/Snowflake compatible queries
- Optimized with CTEs and window functions
- Production-ready for database environments

## 📈 Sample Results

| Client ID | Total Loans | Closed Ratio | 30+ Days Overdue |
|-----------|-------------|--------------|------------------|
| 2333123   | 416         | 95.67%       | 0.00 UAH        |
| 2402782   | 23          | 39.13%       | 0.00 UAH        |
| 2426982   | 20          | 35.00%       | 0.00 UAH        |
| 2441859   | 116         | 92.24%       | 16,585.21 UAH   |
| 2444357   | 55          | 85.45%       | 72,383.46 UAH   |

## 🔧 Requirements

```bash
pip install pandas lxml
```

## 📁 Output Files

- `client_metrics_results.csv` - Final client metrics
- `detailed_credit_data.csv` - Complete tabular dataset
- `final_analysis_report.json` - Comprehensive JSON report
- `validation_report.json` - Data quality assessment

## 🧪 Testing

The project includes sample XML data for testing:

```bash
# Test with demo data
python -c "
from src.xml_processor import XMLCreditDataProcessor
processor = XMLCreditDataProcessor('sample_data')
processor.process_all_xml_files()
processor.print_summary()
"
```

## 🛡️ Data Validation

- **XML Structure Validation** - Ensures proper parsing
- **Metric Calculation Verification** - Cross-validates results
- **Data Quality Checks** - Identifies inconsistencies
- **Business Logic Validation** - Confirms calculation accuracy

## 📧 Contact

**Project:** Finhike Risk Analysis  
**Developer:** [Your Name]  
**Submission:** Ready for a.jersovs@finhike.com

---

⭐ **Star this repository if it helped you!**
