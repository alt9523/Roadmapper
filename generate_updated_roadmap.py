import json
import random
import datetime
from copy import deepcopy

# Load the existing roadmap data
with open('roadmap.json', 'r') as f:
    data = json.load(f)

# Make a deep copy to avoid modifying the original data
updated_data = deepcopy(data)

# Define funding options
FUNDING_OPTIONS = ["Unfunded", "Division IRAD", "Sector IRAD", "CRAD", "Program Funded", "External Task"]

# Define status options
STATUS_OPTIONS = ["Not Started", "In Progress", "Complete", "On Hold", "Delayed"]

# Function to generate random dates
def random_date(start_year=2025, end_year=2026):
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"

# Function to generate random additional details
def random_details():
    details = [
        "This task involves collaboration with multiple teams.",
        "Critical path item that requires careful monitoring.",
        "Dependent on successful completion of previous tasks.",
        "May require additional resources if scope expands.",
        "Includes regular progress reviews with stakeholders.",
        "Requires specialized expertise from external consultants.",
        "Budget constraints may impact timeline.",
        "Technical challenges anticipated during implementation.",
        "Opportunity for process improvement and optimization.",
        "Strategic importance for future program development."
    ]
    return random.choice(details)

# Function to update design tools entries
def update_design_tools(tools_list):
    updated_tools = []
    
    # If tools_list is a list of strings, convert to the new format
    if tools_list and isinstance(tools_list[0], str):
        for tool in tools_list:
            updated_tools.append({
                "name": tool,
                "start": random_date(),
                "end": random_date(),
                "status": random.choice(STATUS_OPTIONS),
                "funding": random.choice(FUNDING_OPTIONS),
                "float": random.choice([True, False]),
                "floatDate": random_date() if random.choice([True, False]) else "",
                "additionalDetails": random_details()
            })
    else:
        # If already in object format, ensure all required fields are present
        for tool in tools_list:
            if isinstance(tool, dict):
                # Ensure the tool has all required fields
                updated_tool = {
                    "name": tool.get("name", ""),
                    "start": tool.get("start", random_date()),
                    "end": tool.get("end", random_date()),
                    "status": tool.get("status", random.choice(STATUS_OPTIONS)),
                    "funding": tool.get("funding", random.choice(FUNDING_OPTIONS)),
                    "float": tool.get("float", random.choice([True, False])),
                    "floatDate": tool.get("floatDate", random_date() if random.choice([True, False]) else ""),
                    "additionalDetails": tool.get("additionalDetails", random_details())
                }
                updated_tools.append(updated_tool)
            else:
                # If not a dict, create a new entry
                updated_tools.append({
                    "name": str(tool),
                    "start": random_date(),
                    "end": random_date(),
                    "status": random.choice(STATUS_OPTIONS),
                    "funding": random.choice(FUNDING_OPTIONS),
                    "float": random.choice([True, False]),
                    "floatDate": random_date() if random.choice([True, False]) else "",
                    "additionalDetails": random_details()
                })
    
    return updated_tools

# Function to update documentation entries
def update_documentation(docs_list):
    updated_docs = []
    
    # If docs_list is a list of strings, convert to the new format
    if docs_list and isinstance(docs_list[0], str):
        for doc in docs_list:
            updated_docs.append({
                "name": doc,
                "start": random_date(),
                "end": random_date(),
                "status": random.choice(STATUS_OPTIONS),
                "funding": random.choice(FUNDING_OPTIONS),
                "float": random.choice([True, False]),
                "floatDate": random_date() if random.choice([True, False]) else "",
                "additionalDetails": random_details()
            })
    else:
        # If already in object format, ensure all required fields are present
        for doc in docs_list:
            if isinstance(doc, dict):
                # Ensure the doc has all required fields
                updated_doc = {
                    "name": doc.get("name", ""),
                    "start": doc.get("start", random_date()),
                    "end": doc.get("end", random_date()),
                    "status": doc.get("status", random.choice(STATUS_OPTIONS)),
                    "funding": doc.get("funding", random.choice(FUNDING_OPTIONS)),
                    "float": doc.get("float", random.choice([True, False])),
                    "floatDate": doc.get("floatDate", random_date() if random.choice([True, False]) else ""),
                    "additionalDetails": doc.get("additionalDetails", random_details())
                }
                updated_docs.append(updated_doc)
            else:
                # If not a dict, create a new entry
                updated_docs.append({
                    "name": str(doc),
                    "start": random_date(),
                    "end": random_date(),
                    "status": random.choice(STATUS_OPTIONS),
                    "funding": random.choice(FUNDING_OPTIONS),
                    "float": random.choice([True, False]),
                    "floatDate": random_date() if random.choice([True, False]) else "",
                    "additionalDetails": random_details()
                })
    
    return updated_docs

# Function to update special NDT entries
def update_special_ndt(ndt_list):
    updated_ndt = []
    
    # If ndt_list is a list of strings, convert to the new format
    if ndt_list and isinstance(ndt_list[0], str):
        for ndt in ndt_list:
            updated_ndt.append({
                "name": ndt,
                "startDate": random_date(),
                "endDate": random_date(),
                "status": random.choice(STATUS_OPTIONS),
                "funding": random.choice(FUNDING_OPTIONS),
                "float": random.choice([True, False]),
                "floatDate": random_date() if random.choice([True, False]) else "",
                "additionalDetails": random_details()
            })
    else:
        # If already in object format, ensure all required fields are present
        for ndt in ndt_list:
            if isinstance(ndt, dict):
                # Ensure the ndt has all required fields
                updated_ndt_item = {
                    "name": ndt.get("name", ""),
                    "startDate": ndt.get("startDate", random_date()),
                    "endDate": ndt.get("endDate", random_date()),
                    "status": ndt.get("status", random.choice(STATUS_OPTIONS)),
                    "funding": ndt.get("funding", random.choice(FUNDING_OPTIONS)),
                    "float": ndt.get("float", random.choice([True, False])),
                    "floatDate": ndt.get("floatDate", random_date() if random.choice([True, False]) else ""),
                    "additionalDetails": ndt.get("additionalDetails", random_details())
                }
                updated_ndt.append(updated_ndt_item)
            else:
                # If not a dict, create a new entry
                updated_ndt.append({
                    "name": str(ndt),
                    "startDate": random_date(),
                    "endDate": random_date(),
                    "status": random.choice(STATUS_OPTIONS),
                    "funding": random.choice(FUNDING_OPTIONS),
                    "float": random.choice([True, False]),
                    "floatDate": random_date() if random.choice([True, False]) else "",
                    "additionalDetails": random_details()
                })
    
    return updated_ndt

# Function to update part acceptance entries
def update_part_acceptance(acceptance_list):
    updated_acceptance = []
    
    # If acceptance_list is a list of strings, convert to the new format
    if acceptance_list and isinstance(acceptance_list[0], str):
        for acceptance in acceptance_list:
            updated_acceptance.append({
                "name": acceptance,
                "startDate": random_date(),
                "endDate": random_date(),
                "status": random.choice(STATUS_OPTIONS),
                "funding": random.choice(FUNDING_OPTIONS),
                "float": random.choice([True, False]),
                "floatDate": random_date() if random.choice([True, False]) else "",
                "additionalDetails": random_details()
            })
    else:
        # If already in object format, ensure all required fields are present
        for acceptance in acceptance_list:
            if isinstance(acceptance, dict):
                # Ensure the acceptance has all required fields
                updated_acceptance_item = {
                    "name": acceptance.get("name", ""),
                    "startDate": acceptance.get("startDate", random_date()),
                    "endDate": acceptance.get("endDate", random_date()),
                    "status": acceptance.get("status", random.choice(STATUS_OPTIONS)),
                    "funding": acceptance.get("funding", random.choice(FUNDING_OPTIONS)),
                    "float": acceptance.get("float", random.choice([True, False])),
                    "floatDate": acceptance.get("floatDate", random_date() if random.choice([True, False]) else ""),
                    "additionalDetails": acceptance.get("additionalDetails", random_details())
                }
                updated_acceptance.append(updated_acceptance_item)
            else:
                # If not a dict, create a new entry
                updated_acceptance.append({
                    "name": str(acceptance),
                    "startDate": random_date(),
                    "endDate": random_date(),
                    "status": random.choice(STATUS_OPTIONS),
                    "funding": random.choice(FUNDING_OPTIONS),
                    "float": random.choice([True, False]),
                    "floatDate": random_date() if random.choice([True, False]) else "",
                    "additionalDetails": random_details()
                })
    
    return updated_acceptance

# Function to update business case
def update_business_case(business_case):
    # If business case is already in the checkbox format, return it
    if isinstance(business_case, dict) and "Save schedule" in business_case:
        return business_case
    
    # Create a new business case with checkbox format
    new_business_case = {
        # Business category
        "Save schedule": random.choice([True, False]),
        "Save hardware costs": random.choice([True, False]),
        "Relieve supply chain constraints": random.choice([True, False]),
        "Increase Pwin by hitting PTW": random.choice([True, False]),
        
        # Unconventional Design category
        "Reduce specialty training": random.choice([True, False]),
        "Save weight": random.choice([True, False]),
        "Increase performance": random.choice([True, False]),
        "Unify parts": random.choice([True, False]),
        
        # Agility throughout program category
        "Quickly iterate design/EMs": random.choice([True, False]),
        "Agility in Design and AI&T": random.choice([True, False]),
        "Digital Spares": random.choice([True, False])
    }
    
    return new_business_case

# Update each product in the data
for product in updated_data["products"]:
    # Update designTools
    if "designTools" in product:
        product["designTools"] = update_design_tools(product["designTools"])
    
    # Update documentation
    if "documentation" in product:
        product["documentation"] = update_documentation(product["documentation"])
    
    # Update specialNDT
    if "specialNDT" in product:
        product["specialNDT"] = update_special_ndt(product["specialNDT"])
    
    # Update partAcceptance
    if "partAcceptance" in product:
        product["partAcceptance"] = update_part_acceptance(product["partAcceptance"])
    
    # Update businessCase
    if "businessCase" in product:
        product["businessCase"] = update_business_case(product["businessCase"])
    
    # Add lastSaveDate if not present
    if "lastSaveDate" not in product:
        product["lastSaveDate"] = datetime.datetime.now().strftime("%Y-%m-%d")

# Write the updated data to a new file
with open('updated_roadmap.json', 'w') as f:
    json.dump(updated_data, f, indent=4)

print("Updated roadmap data has been written to updated_roadmap.json") 