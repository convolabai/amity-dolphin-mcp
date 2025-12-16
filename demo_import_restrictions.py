#!/usr/bin/env python3
"""
Demo script showing import restrictions in action.
"""
import ast
from typing import Set

# Copy of the validation logic
ALLOWED_LIBRARIES = {
    # Standard library modules
    'sys', 'os', 'math', 'random', 'datetime', 'time', 'json', 'csv', 'io', 'collections',
    'itertools', 'functools', 'operator', 're', 'string', 'textwrap', 'unicodedata',
    'struct', 'codecs', 'base64', 'binascii', 'hashlib', 'hmac', 'secrets',
    'pathlib', 'glob', 'fnmatch', 'tempfile', 'shutil', 'pickle', 'shelve',
    'sqlite3', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile',
    'configparser', 'argparse', 'logging', 'warnings', 'traceback',
    'decimal', 'fractions', 'statistics', 'enum', 'typing', 'copy', 'pprint',
    'heapq', 'bisect', 'array', 'queue', 'threading', 'multiprocessing',
    'subprocess', 'socket', 'ssl', 'email', 'urllib', 'http', 'html',
    'xml', 'webbrowser', 'uuid', 'contextlib', 'abc', 'dataclasses',
    # Third-party allowed libraries
    'numpy', 'np', 'pandas', 'pd', 'matplotlib', 'plt', 'scipy',
    'sklearn', 'scikit-learn', 'pdfplumber', 'fitz', 'pymupdf',
    'docx', 'python-docx', 'pptx', 'python-pptx', 'openpyxl',
    'chardet', 'magic', 'python-magic',
}

def validate_imports(code: str) -> tuple[bool, str]:
    """Validate that all imports in the code are from allowed libraries."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax error in code: {e}"
    
    disallowed_imports = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split('.')[0]
                if module_name not in ALLOWED_LIBRARIES:
                    disallowed_imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split('.')[0]
                if module_name not in ALLOWED_LIBRARIES:
                    disallowed_imports.add(node.module)
    
    if disallowed_imports:
        return False, (
            f"Import restriction violation: The following imports are not allowed: {', '.join(sorted(disallowed_imports))}\\n\\n"
            f"Allowed libraries:\\n"
            f"- Standard Python library modules\\n"
            f"- numpy, pandas, matplotlib, scipy, scikit-learn\\n"
            f"- pdfplumber, pymupdf, python-docx, python-pptx\\n"
            f"- openpyxl, chardet, python-magic"
        )
    
    return True, ""

def demo_validation():
    """Demonstrate import validation."""
    print("=" * 70)
    print("DEMO: Import Restriction Validation")
    print("=" * 70)
    print()
    
    # Example 1: Valid code
    print("Example 1: Valid code with allowed imports")
    print("-" * 70)
    valid_code = """
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# Create some data
data = pd.DataFrame({
    'x': np.linspace(0, 10, 100),
    'y': np.sin(np.linspace(0, 10, 100))
})

print(f"Created dataset with {len(data)} rows")
"""
    print("Code:")
    print(valid_code)
    
    is_valid, error_msg = validate_imports(valid_code)
    print(f"\nValidation result: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    if error_msg:
        print(f"Error: {error_msg}")
    print()
    
    # Example 2: Invalid code
    print("Example 2: Code with disallowed imports")
    print("-" * 70)
    invalid_code = """
import numpy as np
import requests  # NOT ALLOWED!
import flask     # NOT ALLOWED!

response = requests.get('https://api.example.com/data')
print(response.json())
"""
    print("Code:")
    print(invalid_code)
    
    is_valid, error_msg = validate_imports(invalid_code)
    print(f"\nValidation result: {'✓ PASSED' if is_valid else '✗ BLOCKED (as expected)'}")
    if error_msg:
        print(f"\nError message shown to user:")
        print(error_msg)
    print()
    
    # Example 3: Mixed valid/invalid
    print("Example 3: Mixed imports (some allowed, some not)")
    print("-" * 70)
    mixed_code = """
import pandas as pd      # ALLOWED
import scikit-learn     # NOT IN ALLOWED LIST (should use 'sklearn')
import torch            # NOT ALLOWED
import json             # ALLOWED (standard library)

data = pd.read_csv('data.csv')
"""
    print("Code:")
    print(mixed_code)
    
    is_valid, error_msg = validate_imports(mixed_code)
    print(f"\nValidation result: {'✓ PASSED' if is_valid else '✗ BLOCKED (as expected)'}")
    if error_msg:
        print(f"\nError message:")
        print(error_msg)
    print()
    
    # Example 4: Submodule imports
    print("Example 4: Submodule imports")
    print("-" * 70)
    submodule_code = """
from scipy.stats import norm
from matplotlib.pyplot import plot, show
import openpyxl.workbook

print("All imports are from allowed top-level modules")
"""
    print("Code:")
    print(submodule_code)
    
    is_valid, error_msg = validate_imports(submodule_code)
    print(f"\nValidation result: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    if error_msg:
        print(f"Error: {error_msg}")
    print()
    
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("1. Only imports from the allowed list are permitted")
    print("2. Validation happens before any code execution")
    print("3. Clear error messages indicate which imports are not allowed")
    print("4. Submodule imports are checked based on their top-level module")
    print()


if __name__ == "__main__":
    demo_validation()
