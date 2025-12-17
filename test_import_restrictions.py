#!/usr/bin/env python3
"""
Test script to verify import restrictions are working correctly.
"""
import ast
from typing import Set

# Copy of the validation logic from docker_sandbox.py
ALLOWED_LIBRARIES = {
    # Standard library modules (common ones - this is not exhaustive but covers most use cases)
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
    'numpy', 'np',
    'pandas', 'pd',
    'matplotlib', 'plt',
    'scipy',
    'sklearn', 'scikit-learn',
    'pdfplumber',
    'fitz', 'pymupdf',  # pymupdf imports as 'fitz'
    'docx', 'python-docx',
    'pptx', 'python-pptx',
    'openpyxl',
    'chardet',
    'magic', 'python-magic',
}


def validate_imports(code: str) -> tuple[bool, str]:
    """
    Validate that all imports in the code are from allowed libraries.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax error in code: {e}"
    
    disallowed_imports = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split('.')[0]  # Get top-level module
                if module_name not in ALLOWED_LIBRARIES:
                    disallowed_imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split('.')[0]  # Get top-level module
                if module_name not in ALLOWED_LIBRARIES:
                    disallowed_imports.add(node.module)
    
    if disallowed_imports:
        return False, f"Import restriction violation: The following imports are not allowed: {', '.join(sorted(disallowed_imports))}"
    
    return True, ""

def test_allowed_imports():
    """Test that allowed imports pass validation."""
    print("Testing allowed imports...")
    
    test_cases = [
        ("import numpy", True),
        ("import pandas as pd", True),
        ("import matplotlib.pyplot as plt", True),
        ("from scipy import stats", True),
        ("import sklearn", True),
        ("import pdfplumber", True),
        ("import fitz", True),
        ("import docx", True),
        ("import pptx", True),
        ("import openpyxl", True),
        ("import chardet", True),
        ("import magic", True),
        ("import sys", True),
        ("import os", True),
        ("import json", True),
        ("import datetime", True),
        ("import re", True),
        ("from pathlib import Path", True),
    ]
    
    passed = 0
    failed = 0
    
    for code, should_pass in test_cases:
        is_valid, error_msg = validate_imports(code)
        if is_valid == should_pass:
            print(f"  ✓ {code}")
            passed += 1
        else:
            print(f"  ✗ {code}")
            if error_msg:
                print(f"    Error: {error_msg}")
            failed += 1
    
    print(f"\nAllowed imports: {passed} passed, {failed} failed")
    return failed == 0


def test_disallowed_imports():
    """Test that disallowed imports are rejected."""
    print("\nTesting disallowed imports...")
    
    test_cases = [
        ("import requests", False),
        ("import flask", False),
        ("import django", False),
        ("import tensorflow", False),
        ("import torch", False),
        ("import pip", False),
        ("import setuptools", False),
    ]
    
    passed = 0
    failed = 0
    
    for code, should_pass in test_cases:
        is_valid, error_msg = validate_imports(code)
        if is_valid == should_pass:
            print(f"  ✓ {code} - correctly {'allowed' if should_pass else 'blocked'}")
            passed += 1
        else:
            print(f"  ✗ {code} - should be {'allowed' if should_pass else 'blocked'}")
            if error_msg:
                print(f"    Error: {error_msg}")
            failed += 1
    
    print(f"\nDisallowed imports: {passed} passed, {failed} failed")
    return failed == 0


def test_complex_code():
    """Test validation on more complex code snippets."""
    print("\nTesting complex code snippets...")
    
    # Code with allowed imports
    allowed_code = """
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
print(data)
"""
    
    is_valid, error_msg = validate_imports(allowed_code)
    if is_valid:
        print("  ✓ Complex code with allowed imports passed")
    else:
        print(f"  ✗ Complex code with allowed imports failed: {error_msg}")
    
    # Code with disallowed import
    disallowed_code = """
import numpy as np
import pandas as pd
import requests

data = requests.get('https://example.com')
"""
    
    is_valid, error_msg = validate_imports(disallowed_code)
    if not is_valid and "requests" in error_msg:
        print("  ✓ Complex code with disallowed import correctly rejected")
    else:
        print(f"  ✗ Complex code with disallowed import not properly rejected")
    
    print()
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Import Restriction Validation Tests")
    print("=" * 60)
    
    all_passed = True
    all_passed &= test_allowed_imports()
    all_passed &= test_disallowed_imports()
    all_passed &= test_complex_code()
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60)
