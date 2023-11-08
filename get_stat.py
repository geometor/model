import os
import glob

# Initialize statistics
total_files = 0
total_lines = 0

# Walk through all directories and subdirectories starting at the current directory
for root, dirs, files in os.walk('src'):
    # Filter for module directories by your definition (e.g., contains __init__.py)
    if '__init__.py' in files:
        module_files = glob.glob(os.path.join(root, '*.py'))  # Get all .py files in this module directory
        module_lines = 0
        for file_path in module_files:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                line_count = len(lines)
                module_lines += line_count
                print(f'{file_path}: {line_count} lines')
        
        print(f'Module {root}: {len(module_files)} files, {module_lines} total lines')
        total_files += len(module_files)
        total_lines += module_lines

average_lines_per_file = total_lines / total_files if total_files else 0

print(f'Total .py files: {total_files}')
print(f'Total lines across all .py files: {total_lines}')
print(f'Average lines per .py file: {average_lines_per_file:.2f}')

