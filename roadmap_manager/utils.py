import json
import os
from datetime import datetime

def load_json_data(file_path, default_data=None):
    """Load JSON data from a file, with fallback to default data"""
    if default_data is None:
        default_data = {
            "programs": [], 
            "products": [], 
            "materialSystems": [], 
            "printingSuppliers": [],
            "postProcessingSuppliers": [],
            "fundingOpps": []
        }
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Ensure all required sections exist
            for key in default_data.keys():
                if key not in data:
                    data[key] = default_data[key]
            
            return data, None
        else:
            return default_data, "File not found, using default data"
    except Exception as e:
        return default_data, f"Error loading data: {str(e)}"

def save_json_data(file_path, data):
    """Save JSON data to a file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True, None
    except Exception as e:
        return False, f"Error saving data: {str(e)}"

def format_date(date_obj):
    """Format a date object as YYYY-MM-DD"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%Y-%m-%d")
    return date_obj

def parse_date(date_str):
    """Parse a date string into a datetime object"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return datetime.now()

def parse_comma_separated_list(text):
    """Parse a comma-separated list into a list of strings"""
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()] 