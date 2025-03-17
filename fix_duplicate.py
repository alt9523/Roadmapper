# Script to fix duplicate save_data method in roadmap_manager.py
with open('roadmap_manager.py', 'r') as f:
    content = f.read()

# Replace the duplicate save_data method at the end of the file
fixed_content = content.replace('''    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            
            self.status_var.set(f"Data saved to {self.data_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

if''', 'if')

# Write the fixed content back to the file
with open('roadmap_manager.py', 'w') as f:
    f.write(fixed_content)

print("Fixed duplicate save_data method in roadmap_manager.py") 