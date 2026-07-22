from diff_parser import parse_diff, get_changed_functions

def test_parse_diff():
    with open("sample.diff", "r") as f:
        diff_text = f.read()
    file_path, changed_lines = parse_diff(diff_text)
    assert file_path == "sample_repo/calc.py"
    assert changed_lines == [11]

def test_get_changed_functions():
    file_path = "sample_repo/calc.py"
    changed_lines = [11]
    changed_functions = get_changed_functions(file_path, changed_lines)
    assert changed_functions == ["divide"]