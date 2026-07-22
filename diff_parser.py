from code_graph import find_enclosing_function

def parse_diff(diff_text):
    changed_lines = []
    counter = 0
    file_path = None
    for line in diff_text.splitlines():
        if line.startswith('+++ b/'):
            file_path = line[6:]  # Extract the file path after '+++ b/'
        elif line.startswith('@@'):
            # Extract the line numbers from the hunk header
            hunk_header = line.split(' ')
            new_file_hunk_info = hunk_header[2]  # e.g., '+10,5'
            start_line = int(new_file_hunk_info.split(',')[0][1:])  # Remove the '+' and convert to int
            counter = start_line  # Set counter 
        elif line.startswith('+') and not line.startswith('+++'):
            changed_lines.append(counter)
            counter += 1
        elif line.startswith(' '):
            counter += 1
    return file_path, changed_lines

def get_changed_functions(file_path, changed_lines):
    changed_functions = set()
    for line_number in changed_lines:
        function_name = find_enclosing_function(file_path, line_number)
        if function_name:
            changed_functions.add(function_name)
    return list(changed_functions)

if __name__ == "__main__":
    with open("sample.diff", "r") as f:
        diff_text = f.read()
    file_path, changed_lines = parse_diff(diff_text)
    changed_functions = get_changed_functions(file_path, changed_lines)
    print(f"Changed file: {file_path}")
    print(f"Changed lines: {changed_lines}")
    print(f"Changed functions: {changed_functions}")