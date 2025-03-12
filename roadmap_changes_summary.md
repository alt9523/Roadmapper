# Roadmap Manager Changes Summary

## Overview

This document summarizes the changes made to the Roadmap Manager application, focusing on the backend modifications that need to be reflected in the frontend. The changes primarily involve standardizing header alignment, adding "Float on roadmap" functionality, adding "Additional Details" text boxes, and updating funding dropdown options across multiple tabs.

## 1. Standardized Header Alignment

Headers have been standardized across all tabs (Design Tools, Documentation, Special NDT, Part Acceptance) to ensure consistent alignment and user experience.

### Implementation Details:
- Consistent column widths defined for all tabs
- Headers aligned with their respective input fields
- Headers use the same font styling (`("TkDefaultFont", 9, "bold")`)
- Standard header layout: Name/Title, Start Date, End Date, Status, Funding, Float

## 2. "Float on roadmap" Functionality

A "Float on roadmap" checkbox has been added to all roadmap entries across tabs to allow tasks to maintain their relative position to other tasks even if they are delayed.

### Implementation Details:
- Added a checkbox column labeled "Float" to all tabs
- Added logic to adjust task dates based on time elapsed since the last save
- Tasks marked to float will maintain their relative position to other tasks
- The floating functionality uses the last save date to calculate the elapsed time
- Each entry stores a hidden `float_date` variable to track when floating was enabled

### Floating Logic:
```python
# If this is a floating task, adjust the dates based on time elapsed since last save
if float_on_roadmap and float_date and start_date:
    try:
        # Calculate days elapsed since float date
        float_dt = datetime.datetime.strptime(float_date, "%Y-%m-%d")
        today = datetime.datetime.now()
        days_elapsed = (today - float_dt).days
        
        if days_elapsed > 0 and start_date:
            # Adjust start date
            start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            start_dt = start_dt + datetime.timedelta(days=days_elapsed)
            start_date = start_dt.strftime("%Y-%m-%d")
            
            # Adjust end date if it exists
            if end_date:
                end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                end_dt = end_dt + datetime.timedelta(days=days_elapsed)
                end_date = end_dt.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error adjusting floating dates: {str(e)}")
```

## 3. "Additional Details" Text Box

An "Additional Details" text box has been added to all roadmap entries across tabs to allow users to provide more detailed information about each item.

### Implementation Details:
- Added a text box labeled "Additional Details" below each entry
- The text box spans the full width of the entry row
- The text box has a height of 3 lines and uses word wrapping
- The text box content is stored in the data model as `additionalDetails`

### Text Box Implementation:
```python
# Additional Details section
details_frame = ttk.Frame(entry_frame)
details_frame.grid(row=1, column=0, columnspan=7, sticky=tk.W+tk.E, padx=5, pady=(2, 5))

ttk.Label(details_frame, text="Additional Details:", font=("TkDefaultFont", 8, "bold")).pack(anchor=tk.W, pady=(5, 2))

# Text box for additional details
details_text = tk.Text(details_frame, height=3, width=80, wrap=tk.WORD)
details_text.pack(fill=tk.X, expand=True)
if additional_details:
    details_text.insert("1.0", additional_details)
```

## 4. Updated Funding Dropdown Options

The funding dropdown options have been standardized across all tabs to provide consistent funding categories.

### Implementation Details:
- Updated funding dropdown options to include:
  - "Unfunded"
  - "Division IRAD"
  - "Sector IRAD"
  - "CRAD"
  - "Program Funded"
  - "External Task"
- Applied these options consistently across all tabs

### Funding Dropdown Implementation:
```python
# Funding dropdown
funding_var = tk.StringVar(value=funding)
funding_options = ["Unfunded", "Division IRAD", "Sector IRAD", "CRAD", "Program Funded", "External Task"]
funding_dropdown = ttk.Combobox(frame, textvariable=funding_var, values=funding_options, width=15)
```

## 5. Tab-Specific Changes

### 5.1 Design Tools Tab
- Added "Float on roadmap" checkbox
- Added "Additional Details" text box
- Updated funding dropdown options
- Standardized header alignment
- Added floating functionality

### 5.2 Documentation Tab
- Added "Float on roadmap" checkbox
- Added "Additional Details" text box
- Updated funding dropdown options
- Standardized header alignment
- Added floating functionality

### 5.3 Special NDT Tab
- Added "Float on roadmap" checkbox
- Added "Additional Details" text box
- Updated funding dropdown options
- Standardized header alignment
- Added floating functionality

### 5.4 Part Acceptance Tab
- Added "Float on roadmap" checkbox
- Added "Additional Details" text box
- Updated funding dropdown options
- Standardized header alignment
- Added floating functionality

### 5.5 Business Case Tab
- Maintained original checkbox-based format
- Organized into three categories:
  1. Business
  2. Unconventional Design
  3. Agility throughout program
- Each category contains specific checkboxes for business case drivers

## 6. Data Model Changes

The data model has been updated to store the new fields for each entry type:

### 6.1 Design Tools Entry
```json
{
  "name": "Tool Name",
  "start": "YYYY-MM-DD",
  "end": "YYYY-MM-DD",
  "status": "Status",
  "funding": "Funding Type",
  "float": true/false,
  "floatDate": "YYYY-MM-DD",
  "additionalDetails": "Text content"
}
```

### 6.2 Documentation Entry
```json
{
  "name": "Document Name",
  "start": "YYYY-MM-DD",
  "end": "YYYY-MM-DD",
  "status": "Status",
  "funding": "Funding Type",
  "float": true/false,
  "floatDate": "YYYY-MM-DD",
  "additionalDetails": "Text content"
}
```

### 6.3 Special NDT Entry
```json
{
  "name": "NDT Name",
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "status": "Status",
  "funding": "Funding Type",
  "float": true/false,
  "floatDate": "YYYY-MM-DD",
  "additionalDetails": "Text content"
}
```

### 6.4 Part Acceptance Entry
```json
{
  "name": "Acceptance Criteria",
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "status": "Status",
  "funding": "Funding Type",
  "float": true/false,
  "floatDate": "YYYY-MM-DD",
  "additionalDetails": "Text content"
}
```

### 6.5 Business Case
```json
{
  "Save schedule": true/false,
  "Save hardware costs": true/false,
  "Relieve supply chain constraints": true/false,
  "Increase Pwin by hitting PTW": true/false,
  "Reduce specialty training": true/false,
  "Save weight": true/false,
  "Increase performance": true/false,
  "Unify parts": true/false,
  "Quickly iterate design/EMs": true/false,
  "Agility in Design and AI&T": true/false,
  "Digital Spares": true/false
}
```

## 7. Frontend Implementation Requirements

To update the frontend to match these backend changes, the following should be implemented:

### 7.1 General UI Updates
- Ensure consistent header alignment across all tabs
- Add "Float" column to all roadmap entry tables
- Add "Additional Details" expandable section for each entry
- Update funding dropdown options in all forms

### 7.2 Floating Functionality
- Implement date adjustment logic for floating tasks
- Store and track float dates
- Provide visual indication of floating tasks

### 7.3 Data Handling
- Update data models to include new fields
- Ensure proper serialization/deserialization of the updated data structure
- Handle backward compatibility with older data formats

### 7.4 Visual Design
- Maintain consistent styling across all tabs
- Ensure proper alignment of all form elements
- Provide clear visual hierarchy

## 8. Testing Considerations

When implementing these changes in the frontend, consider testing the following scenarios:

1. Creating new entries with all the new fields
2. Editing existing entries to use the new fields
3. Testing the floating functionality with different date ranges
4. Verifying that the "Additional Details" text is properly saved and loaded
5. Checking that the funding dropdown options are consistent
6. Ensuring backward compatibility with existing data

## 9. Conclusion

These changes enhance the Roadmap Manager application by providing more consistent UI, additional functionality for tracking tasks, and more detailed information capture. The frontend implementation should focus on maintaining this consistency while providing an intuitive user experience for the new features. 