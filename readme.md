# Credit Card Statement Normalizer

A Django application that converts credit card statements from various banks (HDFC, ICICI, Axis, IDFC) into a standardized format for easier financial tracking and analysis.

## Purpose

The Credit Card Statement Normalizer solves a common problem: different banks use different formats for their credit card statements, making it difficult to consolidate and analyze financial data. This application automatically detects the bank format and standardizes transaction data into a consistent structure with uniform dates, amounts, and categories.

## Live Demo

Access the deployed application: [https://onebanc.onrender.com/](https://onebanc.onrender.com/)

## GitHub Repository

[https://github.com/AdityaBhandari23/OneBanc.git](https://github.com/AdityaBhandari23/OneBanc.git)

## Features

- Supports multiple bank formats (HDFC, ICICI, Axis, IDFC)
- Extracts transaction details automatically
- Detects transaction types (Domestic/International)
- Identifies card owner names
- Extracts location information from descriptions
- Standardizes date formats
- Separates debit and credit amounts
- Detects currency

## Requirements

- Python 3.9+
- Django 4.2.1

## Installation and Setup

1. Clone the repository:
```bash
git clone https://github.com/AdityaBhandari23/OneBanc.git
cd OneBanc
```

2. Create and activate virtual environment:

**Windows:**
```
python -m venv venv
venv\Scripts\activate
```

**PowerShell Activation (if you encounter errors):**
```
cd venv\Scripts
activate
cd ..\..
```

**macOS/Linux:**
```
python -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

6. Access the application at http://127.0.0.1:8000/

## How to Use

1. Upload a CSV statement file from any supported bank (HDFC, ICICI, Axis, IDFC)
2. The system will automatically detect the bank format
3. Click "Standardize Statement" to process the file
4. Download the standardized CSV file
5. Import the standardized file into your financial tools or spreadsheets

## Output Format

The standardized output contains these columns:
- Date (DD-MM-YYYY)
- Transaction Description
- Debit (positive value)
- Credit (positive value)
- Currency (INR, USD, EUR, etc.)
- CardName (card owner name)
- Transaction (Domestic/International)
- Location

## Adding New Bank Formats

To support a new bank format:
1. Add a detection rule in `normalizer/utils/parser.py`
2. Create a parsing function for the new format
3. Add the format to the main parsing function

## Troubleshooting

- Ensure your virtual environment is activated before running commands
- Make sure your CSV file is properly formatted
- Check the Django server logs for detailed error messages