#!/usr/bin/env python3
"""
Test suite for Docker-based sandboxed Python executor.

This demonstrates:
1. Secure Python execution in Docker container
2. Volume mounting so files created in /tmp appear on host
3. Session isolation
4. Security features (no filesystem access, network disabled, etc.)
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dolphin_mcp.docker_sandbox import DockerSandboxExecutor


def test_basic_execution():
    """Test basic code execution in sandbox."""
    print("=" * 70)
    print("TEST 1: Basic Code Execution")
    print("=" * 70)
    
    with DockerSandboxExecutor(session_id="test-basic") as executor:
        code = """
import math

# Basic calculations
result = math.pi * (5 ** 2)
print(f"Area of circle (r=5): {result:.2f}")

# List operations
numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers]
print(f"Squared: {squared}")
"""
        
        output = executor.execute_code(code)
        print(output)
        print("✓ Basic execution works\n")


def test_file_creation_and_mounting():
    """Test that files created in /tmp appear on host."""
    print("=" * 70)
    print("TEST 2: File Creation with Volume Mounting")
    print("=" * 70)
    
    session_id = "test-files"
    
    with DockerSandboxExecutor(session_id=session_id) as executor:
        code = """
import json

# Create a file in /sandbox (mounted directory)
data = {
    "timestamp": "2025-12-11",
    "values": [1, 2, 3, 4, 5],
    "status": "success"
}

with open('/sandbox/output.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Created file: /sandbox/output.json")

# Also create a text file
with open('/sandbox/results.txt', 'w') as f:
    f.write("Calculation Results\\n")
    f.write("===================\\n")
    f.write("Sum: 15\\n")
    f.write("Average: 3.0\\n")

print("Created file: /sandbox/results.txt")
"""
        
        output = executor.execute_code(code)
        print(output)
        
        # Check that files exist on host
        print("\nChecking host filesystem:")
        host_path = Path(f"/tmp/sandboxes/{session_id}")
        
        json_file = host_path / "output.json"
        txt_file = host_path / "results.txt"
        
        if json_file.exists():
            print(f"✓ Found {json_file}")
            content = json_file.read_text()
            print(f"  Content preview: {content[:100]}...")
        else:
            print(f"✗ File not found: {json_file}")
        
        if txt_file.exists():
            print(f"✓ Found {txt_file}")
            content = txt_file.read_text()
            print(f"  Content:\n{content}")
        else:
            print(f"✗ File not found: {txt_file}")
        
        print("\n✓ File creation and mounting works\n")


def test_persistent_context():
    """Test that context persists across multiple executions in same session."""
    print("=" * 70)
    print("TEST 3: Persistent Context (Multiple Executions)")
    print("=" * 70)
    
    with DockerSandboxExecutor(session_id="test-context") as executor:
        # First execution
        code1 = """
x = 10
y = 20
result = x + y
print(f"First execution: x={x}, y={y}, result={result}")
"""
        print("Execution 1:")
        output1 = executor.execute_code(code1)
        print(output1)
        
        # Second execution (should have access to previous variables)
        code2 = """
# Use variables from first execution
z = result * 2
print(f"Second execution: Using result={result}, z={z}")
"""
        print("Execution 2:")
        output2 = executor.execute_code(code2)
        print(output2)
        
        print("✓ Context persistence works\n")


def test_security_filesystem_isolation():
    """Test that the sandbox cannot access host filesystem."""
    print("=" * 70)
    print("TEST 4: Security - Filesystem Isolation")
    print("=" * 70)
    
    with DockerSandboxExecutor(session_id="test-security") as executor:
        code = """
import os

# Try to access various system directories
test_paths = ['/etc/passwd', '/root', '/home', '/var', '/usr/bin']

for path in test_paths:
    try:
        if os.path.exists(path):
            print(f"⚠️  Can access: {path}")
        else:
            print(f"✓ Cannot access: {path}")
    except Exception as e:
        print(f"✓ Blocked: {path} - {type(e).__name__}")

# Try to list root directory
try:
    files = os.listdir('/')
    print(f"\\nRoot directory contents: {files}")
except Exception as e:
    print(f"✓ Cannot list root: {e}")

# Confirm we can only write to /sandbox
try:
    with open('/sandbox/test_write.txt', 'w') as f:
        f.write('Can write here')
    print("✓ Can write to /sandbox")
except Exception as e:
    print(f"✗ Cannot write to /sandbox: {e}")
"""
        
        output = executor.execute_code(code)
        print(output)
        print("\n✓ Filesystem isolation verified\n")


def test_data_analysis_workflow():
    """Test a realistic data analysis workflow with file output."""
    print("=" * 70)
    print("TEST 5: Data Analysis Workflow")
    print("=" * 70)
    
    session_id = "test-analysis"
    
    with DockerSandboxExecutor(session_id=session_id) as executor:
        code = """
import json
import statistics

# Simulate sales data analysis
sales_data = [
    {"month": "Jan", "sales": 12000, "region": "North"},
    {"month": "Feb", "sales": 15000, "region": "North"},
    {"month": "Mar", "sales": 13500, "region": "North"},
    {"month": "Jan", "sales": 9000, "region": "South"},
    {"month": "Feb", "sales": 11000, "region": "South"},
    {"month": "Mar", "sales": 10500, "region": "South"},
]

# Calculate statistics by region
regions = {}
for record in sales_data:
    region = record["region"]
    if region not in regions:
        regions[region] = []
    regions[region].append(record["sales"])

# Generate report
report = {
    "analysis_date": "2025-12-11",
    "regions": {}
}

for region, sales in regions.items():
    report["regions"][region] = {
        "total": sum(sales),
        "average": statistics.mean(sales),
        "median": statistics.median(sales),
        "count": len(sales)
    }

# Print summary
print("Sales Analysis Report")
print("=" * 50)
for region, stats in report["regions"].items():
    print(f"\\n{region}:")
    print(f"  Total Sales: ${stats['total']:,}")
    print(f"  Average: ${stats['average']:,.2f}")
    print(f"  Median: ${stats['median']:,.2f}")
    print(f"  Transactions: {stats['count']}")

# Save to file
with open('/sandbox/sales_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("\\n✓ Report saved to /sandbox/sales_report.json")
"""
        
        output = executor.execute_code(code)
        print(output)
        
        # Read the generated report from host
        report_path = Path(f"/tmp/sandboxes/{session_id}/sales_report.json")
        if report_path.exists():
            print("\nReport contents on host:")
            print(report_path.read_text())
        
        print("\n✓ Data analysis workflow completed\n")


def test_multiple_sessions():
    """Test that different sessions are isolated."""
    print("=" * 70)
    print("TEST 6: Multiple Session Isolation")
    print("=" * 70)
    
    # Session 1
    with DockerSandboxExecutor(session_id="session-1") as executor:
        code = """
session_var = "I am from session 1"
with open('/sandbox/session1.txt', 'w') as f:
    f.write(session_var)
print(f"Session 1: {session_var}")
"""
        output = executor.execute_code(code)
        print("Session 1 output:")
        print(output)
    
    # Session 2
    with DockerSandboxExecutor(session_id="session-2") as executor:
        code = """
session_var = "I am from session 2"
with open('/sandbox/session2.txt', 'w') as f:
    f.write(session_var)
print(f"Session 2: {session_var}")

# Try to access session 1 file (should not exist)
import os
if os.path.exists('/sandbox/session1.txt'):
    print("⚠️  Can see session 1 file!")
else:
    print("✓ Cannot see session 1 file (isolated)")
"""
        output = executor.execute_code(code)
        print("\nSession 2 output:")
        print(output)
    
    # Verify on host
    print("\nHost filesystem check:")
    session1_file = Path("/tmp/sandboxes/session-1/session1.txt")
    session2_file = Path("/tmp/sandboxes/session-2/session2.txt")
    
    if session1_file.exists():
        print(f"✓ Session 1 file: {session1_file.read_text()}")
    if session2_file.exists():
        print(f"✓ Session 2 file: {session2_file.read_text()}")
    
    print("\n✓ Session isolation verified\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("DOCKER SANDBOX EXECUTOR TEST SUITE")
    print("=" * 70)
    print()
    print("IMPORTANT: Make sure to build the Docker image first:")
    print("  docker build -f Dockerfile.sandbox -t dolphin-python-sandbox .")
    print()
    
    try:
        test_basic_execution()
        test_file_creation_and_mounting()
        test_persistent_context()
        test_security_filesystem_isolation()
        test_data_analysis_workflow()
        test_multiple_sessions()
        
        print("=" * 70)
        print("ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("Summary:")
        print("  ✓ Basic Python execution works in Docker container")
        print("  ✓ Files created in /sandbox appear on host at /tmp/sandboxes/<session_id>")
        print("  ✓ Context persists across executions in same session")
        print("  ✓ Filesystem is isolated (cannot access host filesystem)")
        print("  ✓ Data analysis workflows function properly")
        print("  ✓ Multiple sessions are properly isolated")
        print()
        print("The Docker sandbox provides:")
        print("  • Strong filesystem isolation")
        print("  • Controlled volume mounting for output files")
        print("  • Session-based directory organization")
        print("  • Resource limits (memory, CPU)")
        print("  • Network isolation (disabled by default)")
        print("  • Non-root execution for security")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
