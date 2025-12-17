# Import Restrictions

## Overview

The Dolphin MCP now enforces strict import restrictions on Python code executed within the sandbox environment. This security measure ensures that only approved libraries can be imported and used during code execution.

## Allowed Libraries

### Standard Python Library Modules

The following standard library modules are allowed:
- **System & OS**: `sys`, `os`, `pathlib`, `glob`, `fnmatch`, `tempfile`, `shutil`, `subprocess`, `socket`, `ssl`
- **Data Types & Math**: `math`, `random`, `decimal`, `fractions`, `statistics`, `array`
- **Date & Time**: `datetime`, `time`
- **Data Formats**: `json`, `csv`, `pickle`, `shelve`, `configparser`, `base64`, `binascii`
- **Text Processing**: `re`, `string`, `textwrap`, `unicodedata`
- **Compression**: `gzip`, `bz2`, `lzma`, `zipfile`, `tarfile`
- **Security**: `hashlib`, `hmac`, `secrets`, `uuid`
- **Collections & Iteration**: `collections`, `itertools`, `functools`, `operator`, `heapq`, `bisect`, `queue`
- **I/O**: `io`, `struct`, `codecs`
- **Concurrency**: `threading`, `multiprocessing`
- **Logging & Debugging**: `logging`, `warnings`, `traceback`, `argparse`, `pprint`
- **Type System**: `typing`, `enum`, `abc`, `dataclasses`, `copy`, `contextlib`
- **Database**: `sqlite3`
- **Network**: `urllib`, `http`, `html`, `email`, `webbrowser`
- **XML**: `xml`

### Third-Party Libraries

The following third-party libraries are allowed:

1. **numpy** - Numerical computing
   ```python
   import numpy
   import numpy as np
   ```

2. **pandas** - Data manipulation and analysis
   ```python
   import pandas
   import pandas as pd
   ```

3. **matplotlib** - Data visualization
   ```python
   import matplotlib
   import matplotlib.pyplot as plt
   ```

4. **scipy** - Scientific computing
   ```python
   import scipy
   from scipy import stats
   ```

5. **scikit-learn** - Machine learning
   ```python
   import sklearn
   from sklearn.model_selection import train_test_split
   ```

6. **pdfplumber** - PDF text extraction
   ```python
   import pdfplumber
   ```

7. **pymupdf** - PDF manipulation (imports as `fitz`)
   ```python
   import fitz  # PyMuPDF
   ```

8. **python-docx** - Microsoft Word documents (imports as `docx`)
   ```python
   import docx
   from docx import Document
   ```

9. **python-pptx** - Microsoft PowerPoint (imports as `pptx`)
   ```python
   import pptx
   from pptx import Presentation
   ```

10. **openpyxl** - Excel file handling
    ```python
    import openpyxl
    ```

11. **chardet** - Character encoding detection
    ```python
    import chardet
    ```

12. **python-magic** - File type identification (imports as `magic`)
    ```python
    import magic
    ```

## How It Works

The import restriction is enforced through AST (Abstract Syntax Tree) parsing:

1. Before any code execution, the code is parsed into an AST
2. All `import` and `from ... import` statements are extracted
3. The top-level module name is checked against the allowed list
4. If any disallowed imports are found, execution is blocked with a clear error message

## Error Messages

If you attempt to import a disallowed library, you will receive an error message like:

```
IMPORT RESTRICTION ERROR:
Import restriction violation: The following imports are not allowed: requests, flask

Allowed libraries:
- Standard Python library modules
- numpy
- pandas
- matplotlib
- scipy
- scikit-learn (import as sklearn)
- pdfplumber
- pymupdf (import as fitz)
- python-docx (import as docx)
- python-pptx (import as pptx)
- openpyxl
- chardet
- python-magic (import as magic)
```

## Examples

### ✅ Allowed Code

```python
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import json
from pathlib import Path

data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
print(data)
```

### ❌ Disallowed Code

```python
import requests  # NOT ALLOWED
import flask     # NOT ALLOWED
import torch     # NOT ALLOWED

response = requests.get('https://example.com')  # Will be blocked
```

## Testing

To test the import restrictions, run:

```bash
python test_import_restrictions.py
```

This will verify that:
- All allowed libraries can be imported
- Disallowed libraries are properly blocked
- Complex code with mixed imports is correctly validated

## Modifying Allowed Libraries

To modify the allowed libraries list, edit the `ALLOWED_LIBRARIES` constant in:
- `/src/dolphin_mcp/docker_sandbox.py` - For the main validation logic

After modifying, ensure you:
1. Update the system prompt in `/src/dolphin_mcp/reasoning.py`
2. Run the test suite to verify everything works
3. Rebuild the Docker image if using Docker sandbox: `docker build -f Dockerfile.sandbox -t dolphin-python-sandbox:latest .`

## Security Considerations

This import restriction provides defense-in-depth security:

1. **AST-based validation** - Checks imports before execution
2. **Docker isolation** - Code runs in isolated containers (when Docker sandbox is enabled)
3. **Non-root execution** - Containers run as unprivileged user
4. **Network isolation** - Network access can be disabled
5. **Resource limits** - CPU and memory are constrained

Even with these restrictions, be cautious about:
- Running untrusted code
- Allowing file system access
- Processing sensitive data
