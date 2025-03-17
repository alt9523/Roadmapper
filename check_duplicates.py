import re

# Read the file
with open('roadmap_manager.py', 'r') as f:
    content = f.read()

# Find all method definitions
methods = re.findall(r'def\s+(\w+)\s*\(', content)

# Count occurrences of each method name
from collections import Counter
method_counts = Counter(methods)

# Find duplicates, excluding expected duplicates (nested methods with same names)
expected_duplicates = [
    'save_program', 'save_supplier', 'save_material', 'save_opp',
    'add_material_checkbox', 'add_task_entry', 'add_milestone_entry',
    '__init__', 'remove_entry', 'remove_task', 'remove_milestone',
    'remove_field', 'delete_program', 'delete_product', 'delete_material',
    'delete_supplier', 'delete_opp'
]

duplicates = [method for method, count in method_counts.items() 
              if count > 1 and method not in expected_duplicates]

print('Duplicate methods:', duplicates) 