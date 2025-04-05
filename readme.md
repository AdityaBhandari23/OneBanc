# Credit Card Statement Normalizer

A simple Django application that standardizes credit card statements from various banks into a unified format.

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

## Installation

1. Clone the repository or download the source code

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: 
   ```
   venv\Scripts\activate
   ```
   - Linux/Mac: 
   ```
   source venv/bin/activate
   ```

4. Install the required packages:
```bash
pip install -r requirements.txt
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

7. Access the application at http://127.0.0.1:8000/

## How to Use

1. Navigate to the web interface at http://127.0.0.1:8000/
2. Click "Choose File" or drag and drop a CSV file
3. Click "Standardize Statement"
4. Download the standardized CSV file
5. Import into your financial tools

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

- Make sure your CSV file is properly formatted
- Ensure your virtual environment is activated before running commands
- Check Django logs for detailed error messages