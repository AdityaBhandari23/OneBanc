import csv
import re
import os
from datetime import datetime
from dateutil import parser as date_parser

def clean_amount(amount_str):
    """
    Cleans amount strings by removing currency symbols, commas, and handling credits
    Returns a float value (negative for credits)
    """
    if not amount_str or amount_str.strip() == '':
        return 0.0
    
    # Handle 'cr' suffix for credits
    is_credit = False
    if 'cr' in amount_str.lower():
        is_credit = True
        amount_str = amount_str.lower().replace('cr', '').strip()
    
    # Remove currency symbols and commas
    amount_str = re.sub(r'[₹$€£,]', '', amount_str.strip())
    
    # Handle any additional text that might appear
    amount_str = re.sub(r'[^\d.]', '', amount_str.strip())
    
    try:
        amount = float(amount_str)
        return amount if is_credit else amount  # Return positive for credits now
    except ValueError:
        return 0.0

def parse_date(date_str):
    """
    Parses dates in various formats using dateutil parser
    Returns a standardized DD-MM-YYYY format string
    """
    try:
        # Handle the MM-DD-YYYY format specifically
        if re.match(r'\d{2}-\d{2}-\d{4}', date_str):
            parts = date_str.split('-')
            
            # Check if likely MM-DD-YYYY format (American style)
            if int(parts[0]) <= 12 and int(parts[1]) <= 31:
                # Swap month and day for non-US format
                date_str = f"{parts[1]}-{parts[0]}-{parts[2]}"
        
        parsed_date = date_parser.parse(date_str)
        return parsed_date.strftime('%d-%m-%Y')  # Changed to DD-MM-YYYY format
    except (ValueError, TypeError):
        # Return empty string for invalid dates
        return ''

def extract_location(description):
    """
    Extracts location from transaction description
    """
    # Common city names in India and internationally
    common_cities = [
        'delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad', 
        'pune', 'ahmedabad', 'jaipur', 'gurgaon', 'noida', 'gurugram', 
        'newyork', 'california', 'berlin', 'katunayake', 'dusseldor'
    ]
    
    # Extract anything after the last space as potential location
    words = description.strip().split()
    if len(words) > 1:
        # Check the last word first, if it's a common city
        last_word = words[-1].lower()
        for city in common_cities:
            if city in last_word:
                return city
        
        # If the last word is not a city, try the whole description
        desc_lower = description.lower()
        for city in common_cities:
            if city in desc_lower:
                return city
                
        # Default to the last word if no cities found
        location = last_word
        # Clean up location - remove any non-alphanumeric characters
        location = re.sub(r'[^a-zA-Z0-9]', '', location)
        return location
    return ""

def detect_transaction_type(description, currency):
    """
    Determines if transaction is domestic or international based on description and currency
    """
    if currency not in ['INR', '']:
        return 'International'
    
    international_keywords = ['international', 'foreign', 'overseas', 'euro', 'usd', 'eur', 'dollar', 'pound']
    for keyword in international_keywords:
        if keyword.lower() in description.lower():
            return 'International'
    
    return 'Domestic'

def extract_currency_from_description(description, amount_str):
    """
    Extract currency information from description and amount
    """
    # Default currency
    currency = 'INR'
    
    # Check for currency in amount string
    if 'EUR' in amount_str:
        currency = 'EUR'
    elif 'USD' in amount_str:
        currency = 'USD'
    elif 'POUND' in amount_str or '£' in amount_str:
        currency = 'POUND'
    
    # Check in description if not found in amount
    elif 'EUR' in description or 'EURO' in description:
        currency = 'EUR'
    elif 'USD' in description or 'DOLLAR' in description:
        currency = 'USD'
    elif 'POUND' in description or '£' in description:
        currency = 'POUND'
    
    return currency

def is_name_row(line):
    """
    Checks if a CSV row contains just a name
    """
    # Names we're looking for
    names = ['Rahul', 'Ritu', 'Raj', 'Rajat']
    
    # Check if the row has just one column with a name
    if line and len(line) >= 1:
        # For single-cell name entries
        if len(line) == 1 and line[0].strip() in names:
            return True, line[0].strip()
        
        # For names that might be in a specific cell pattern (like in IDFC format)
        for i, cell in enumerate(line):
            if cell.strip() in names and (i <= 2):  # Look in first 3 columns
                # Check if other cells in the row are mostly empty
                other_cells_empty = True
                for j, other_cell in enumerate(line):
                    if j != i and other_cell.strip() and not other_cell.strip() in ['Domestic Transactions', 'International Transactions', 'Domestic Transaction', 'International Transaction']:
                        other_cells_empty = False
                        break
                if other_cells_empty:
                    return True, cell.strip()
    
    return False, None

def extract_name_from_file(file_path):
    """
    Extracts all names from the file content for better name detection
    """
    name_positions = {}
    names = ['Rahul', 'Ritu', 'Raj', 'Rajat']
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        content = file.read()
        
        for name in names:
            # Find all occurrences of this name using word boundaries
            matches = list(re.finditer(r'\b' + name + r'\b', content))
            for match in matches:
                name_positions[match.start()] = name
    
    return name_positions

def preprocess_file(file_path):
    """
    Pre-reads the file to identify sections and their names
    Returns a mapping of line numbers to section names and types
    """
    section_map = {}
    current_name = "Unknown"
    current_type = "Domestic"
    
    # Pre-extract names from file content
    name_positions = extract_name_from_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        file_content = file.read()
        lines = file_content.split('\n')
        
        # Reset file pointer for CSV reader
        file.seek(0)
        reader = csv.reader(file)
        
        # Process each line
        line_start_positions = [0]  # Start position of each line in the file
        for i in range(len(lines) - 1):
            line_start_positions.append(line_start_positions[-1] + len(lines[i]) + 1)
        
        for line_num, line in enumerate(reader):
            # Find names that appear in this line
            line_pos = line_start_positions[line_num]
            
            # Check for name rows directly in CSV cells
            name_result, name_value = is_name_row(line)
            if name_result:
                current_name = name_value if name_value else line[0].strip()
                section_map[line_num] = {"name": current_name, "type": current_type}
                continue
            
            # Otherwise, check if any of our known names occur in this line range
            for pos, name in name_positions.items():
                if line_pos <= pos < (line_pos + len(lines[line_num])):
                    current_name = name
                    section_map[line_num] = {"name": current_name, "type": current_type}
                    break
            
            # Check for transaction type headers
            transaction_line = ''.join(line).lower()
            if 'international' in transaction_line:
                current_type = "International"
                section_map[line_num] = {"name": current_name, "type": current_type}
            elif 'domestic' in transaction_line:
                current_type = "Domestic"
                section_map[line_num] = {"name": current_name, "type": current_type}
    
    return section_map

def detect_bank_format(file_path):
    """
    Detects which bank format the CSV file follows based on its content
    Returns a string identifier: 'hdfc', 'icici', 'axis', or 'idfc'
    """
    filename = os.path.basename(file_path).lower()
    
    if 'hdfc' in filename:
        return 'hdfc'
    elif 'icici' in filename:
        return 'icici'
    elif 'axis' in filename:
        return 'axis'
    elif 'idfc' in filename:
        return 'idfc'
    
    # If filename doesn't give it away, check the content
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        content = file.read(1000)  # Read first 1000 chars for a sample
        
        if 'HDFC' in content:
            return 'hdfc'
        elif 'ICICI' in content:
            return 'icici'
        elif 'AXIS' in content:
            return 'axis'
        elif 'IDFC' in content:
            return 'idfc'
    
    # Default to generic format if can't detect
    return 'generic'

def find_current_section(line_number, section_map):
    """
    Finds the current section name and type based on line number
    """
    current_name = "Unknown"
    current_type = "Domestic"
    
    # Find the most recent section before this line
    relevant_sections = {l: s for l, s in section_map.items() if l <= line_number}
    if relevant_sections:
        latest_section_line = max(relevant_sections.keys())
        current_name = section_map[latest_section_line]["name"]
        current_type = section_map[latest_section_line]["type"]
    
    return current_name, current_type

def parse_hdfc_statement(file_path):
    """
    Parse HDFC bank statement CSV format
    """
    rows = []
    # Preprocess to get section mapping
    section_map = preprocess_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        
        # Skip initial non-transaction rows until we find the header
        header_found = False
        for header_line_num, line in enumerate(reader):
            # Look for the header line that has "Date" in first column
            if line and len(line) >= 3 and 'Date' in line[0]:
                header_found = True
                break
        
        # Process transactions
        for line_num, line in enumerate(reader, start=header_line_num+1):
            # Skip empty rows or header rows
            if not line or len(line) < 3 or not line[0].strip() or 'Date' in line[0]:
                continue
            
            # Check for name or section markers
            name_result, name = is_name_row(line)
            if name_result or any('Transactions' in cell for cell in line):
                continue
                
            # Check if we have date, description, and amount
            if len(line) >= 3 and line[0].strip() and line[1].strip():
                # Get current section info
                current_name, current_type = find_current_section(line_num, section_map)
                
                date = parse_date(line[0].strip())
                description = line[1].strip()
                
                # Extract currency if included with amount
                amount_str = line[2].strip() if len(line) > 2 else ""
                
                # Get the currency combining amount string and description
                currency = extract_currency_from_description(description, amount_str)
                
                # Clean the amount string by removing the currency
                if currency != 'INR':
                    amount_str = amount_str.replace(currency, '').strip()
                
                # Determine if it's a credit or debit
                is_credit = 'cr' in amount_str.lower()
                amount = clean_amount(amount_str)
                
                debit = 0
                credit = 0
                
                if is_credit:
                    credit = amount
                else:
                    debit = amount
                
                # Extract location from description
                location = extract_location(description)
                
                if date:  # Only add rows with valid dates
                    rows.append({
                        'Date': date,
                        'Transaction Description': description,
                        'Debit': debit,
                        'Credit': credit,
                        'Currency': currency,
                        'CardName': current_name,
                        'Transaction': current_type,
                        'Location': location
                    })
    
    return rows

def parse_icici_statement(file_path):
    """
    Parse ICICI bank statement CSV format
    """
    rows = []
    # Preprocess to get section mapping
    section_map = preprocess_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        
        # Skip initial non-transaction rows
        header_found = False
        for header_line_num, line in enumerate(reader):
            if line and len(line) >= 4 and 'Date' in line[0] and ('Transaction' in ''.join(line)):
                header_found = True
                break
        
        # Start processing transactions
        for line_num, line in enumerate(reader, start=header_line_num+1):
            # Skip empty rows or section headers
            if not line or len(line) < 3 or not line[0].strip():
                continue
            
            # Check for name or section markers
            name_result, name = is_name_row(line)
            if name_result or any('Transactions' in cell for cell in line):
                continue
                
            # Check if we have date and description
            if len(line) >= 3 and line[0].strip():
                # Get current section info
                current_name, current_type = find_current_section(line_num, section_map)
                
                date = parse_date(line[0].strip())
                description = line[1].strip() if len(line) > 1 and line[1].strip() else "Unknown Transaction"
                
                # ICICI has separate debit and credit columns
                debit_str = line[2].strip() if len(line) > 2 else ''
                credit_str = line[3].strip() if len(line) > 3 else ''
                
                # Parse amounts
                debit = clean_amount(debit_str) if debit_str else 0
                credit = clean_amount(credit_str) if credit_str else 0
                
                # Extract currency combining description 
                currency = extract_currency_from_description(description, debit_str + credit_str)
                
                # Extract location from description
                location = extract_location(description)
                
                if date:  # Only add rows with valid dates
                    rows.append({
                        'Date': date,
                        'Transaction Description': description,
                        'Debit': debit,
                        'Credit': credit,
                        'Currency': currency,
                        'CardName': current_name,
                        'Transaction': current_type,
                        'Location': location
                    })
    
    return rows

def parse_axis_statement(file_path):
    """
    Parse Axis bank statement CSV format
    """
    rows = []
    # Preprocess to get section mapping
    section_map = preprocess_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        
        # Skip initial non-transaction rows
        header_found = False
        for header_line_num, line in enumerate(reader):
            if line and len(line) >= 4 and 'Date' in line[0] and 'Debit' in line[1] and 'Credit' in line[2]:
                header_found = True
                break
        
        if not header_found:
            return rows  # Return empty if format doesn't match
        
        # Start processing transactions
        for line_num, line in enumerate(reader, start=header_line_num+1):
            # Skip empty rows or section headers
            if not line or len(line) < 4 or not line[0].strip():
                continue
            
            # Check for name or section markers
            name_result, name = is_name_row(line)
            if name_result or any('Transactions' in cell for cell in line):
                continue
                
            # Check if we have date and transaction details
            if len(line) >= 4 and line[0].strip() and line[3].strip():
                # Get current section info
                current_name, current_type = find_current_section(line_num, section_map)
                
                date = parse_date(line[0].strip())
                description = line[3].strip()
                
                # Axis has separate debit and credit columns
                debit_str = line[1].strip() if len(line) > 1 else ''
                credit_str = line[2].strip() if len(line) > 2 else ''
                
                # Parse amounts
                debit = clean_amount(debit_str) if debit_str else 0
                credit = clean_amount(credit_str) if credit_str else 0
                
                # Extract currency combining description
                currency = extract_currency_from_description(description, debit_str + credit_str)
                
                # Extract location from description
                location = extract_location(description)
                
                if date:  # Only add rows with valid dates
                    rows.append({
                        'Date': date,
                        'Transaction Description': description,
                        'Debit': debit,
                        'Credit': credit,
                        'Currency': currency,
                        'CardName': current_name,
                        'Transaction': current_type,
                        'Location': location
                    })
    
    return rows

def parse_idfc_statement(file_path):
    """
    Parse IDFC bank statement CSV format
    """
    rows = []
    # Preprocess to get section mapping
    section_map = preprocess_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        
        # Skip initial non-transaction rows
        header_found = False
        for header_line_num, line in enumerate(reader):
            if line and len(line) >= 3 and 'Transaction Details' in line[0] and 'Date' in line[1] and 'Amount' in line[2]:
                header_found = True
                break
        
        # Start processing transactions
        for line_num, line in enumerate(reader, start=header_line_num+1):
            # Skip empty rows or section headers
            if not line or len(line) < 3 or not line[0].strip():
                continue
            
            # Check for name or section markers
            name_result, name = is_name_row(line)
            if name_result or any('Transactions' in cell for cell in line):
                continue
                
            # Check if we have transaction details and date
            if len(line) >= 3 and line[0].strip() and line[1].strip():
                # Get current section info
                current_name, current_type = find_current_section(line_num, section_map)
                
                date = parse_date(line[1].strip())
                description = line[0].strip()
                
                # Extract currency
                amount_str = line[2].strip() if len(line) > 2 else ''
                currency = extract_currency_from_description(description, amount_str)
                
                # Clean amount string by removing currency if needed
                if currency != 'INR':
                    amount_str = amount_str.replace(currency, '').strip()
                
                is_credit = 'cr' in amount_str.lower()
                amount = clean_amount(amount_str)
                
                debit = 0
                credit = 0
                
                if is_credit:
                    credit = amount
                else:
                    debit = amount
                
                # Extract location from description
                location = extract_location(description)
                
                if date:  # Only add rows with valid dates
                    rows.append({
                        'Date': date,
                        'Transaction Description': description,
                        'Debit': debit,
                        'Credit': credit,
                        'Currency': currency,
                        'CardName': current_name,
                        'Transaction': current_type,
                        'Location': location
                    })
    
    return rows

def parse_csv_statement(file_path):
    """
    Main function to parse bank statements
    Detects format and dispatches to appropriate parser
    """
    bank_format = detect_bank_format(file_path)
    
    if bank_format == 'hdfc':
        return parse_hdfc_statement(file_path)
    elif bank_format == 'icici':
        return parse_icici_statement(file_path)
    elif bank_format == 'axis':
        return parse_axis_statement(file_path)
    elif bank_format == 'idfc':
        return parse_idfc_statement(file_path)
    else:
        # Generic fallback
        try:
            return parse_hdfc_statement(file_path)
        except:
            try:
                return parse_icici_statement(file_path)
            except:
                try:
                    return parse_axis_statement(file_path)
                except:
                    try:
                        return parse_idfc_statement(file_path)
                    except:
                        return []  # Return empty if all fail

def standardize_statement(input_file, output_file):
    """
    Reads a raw bank statement CSV file, normalizes it to a standard format,
    and writes the result to a new CSV file.
    """
    rows = parse_csv_statement(input_file)
    
    # Write standardized output to CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Date', 'Transaction Description', 'Debit', 'Credit', 'Currency', 'CardName', 'Transaction', 'Location'])
        writer.writeheader()
        writer.writerows(rows)
    
    return len(rows)  # Return number of rows processed 