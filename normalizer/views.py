import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import csv
import io
import os.path
import re

from .utils.parser import standardize_statement, detect_bank_format

def home(request):
    """Home page view with file upload form"""
    return render(request, 'upload.html')

def upload_file(request):
    """Handle file upload and processing"""
    if request.method == 'POST' and request.FILES.get('statement_file'):
        # Get uploaded file
        uploaded_file = request.FILES['statement_file']
        
        # Check if it's a CSV
        if not uploaded_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file')
            return redirect('home')
        
        # Save the uploaded file
        fs = FileSystemStorage()
        input_filename = fs.save(uploaded_file.name, uploaded_file)
        input_file_path = os.path.join(settings.MEDIA_ROOT, input_filename)
        
        # Detect bank format for naming
        bank_format = detect_bank_format(input_file_path).capitalize()
        
        # Generate output filename using <Bank><Name>.csv format
        # Extract the current timestamp to make filename unique
        import time
        timestamp = int(time.time())
        
        # Get a name component from the input filename (either a pattern like "Case1" or just a random string)
        name_match = re.search(r'Case\d+', os.path.splitext(input_filename)[0])
        if name_match:
            name_component = name_match.group(0)
        else:
            # Use last 4 digits of timestamp if no Case pattern found
            name_component = f"Statement{timestamp % 10000}"
            
        output_filename = f"{bank_format}{name_component}.csv"
        output_file_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        
        # Process the file
        try:
            rows_processed = standardize_statement(input_file_path, output_file_path)
            
            # Prepare context for result page
            context = {
                'input_filename': input_filename,
                'output_filename': output_filename,
                'rows_processed': rows_processed
            }
            
            return render(request, 'result.html', context)
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('home')
    
    return redirect('home')

def download_file(request, filename):
    """Download processed file"""
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    
    messages.error(request, 'File not found')
    return redirect('home')
