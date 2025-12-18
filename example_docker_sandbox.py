#!/usr/bin/env python3
"""
Simple example demonstrating Docker sandbox with volume mounting.

This shows how files created in the sandbox appear on the host filesystem.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dolphin_mcp.docker_sandbox import DockerSandboxExecutor


def main():
    print("Docker Sandbox Example")
    print("=" * 60)
    
    # Create a sandbox with a specific session ID
    session_id = "example-session"
    print(f"Session ID: {session_id}")
    print(f"Host directory: /tmp/sandboxes/{session_id}")
    print()
    
    with DockerSandboxExecutor(session_id=session_id) as sandbox:
        # Example 1: Simple calculation
        print("Example 1: Simple calculation")
        print("-" * 60)
        code1 = """
import math

radius = 10
area = math.pi * radius ** 2
circumference = 2 * math.pi * radius

print(f"Circle with radius {radius}:")
print(f"  Area: {area:.2f}")
print(f"  Circumference: {circumference:.2f}")
"""
        output1 = sandbox.execute_code(code1)
        print(output1)
        
        # Example 2: Create a data file
        print("\nExample 2: Create a data file")
        print("-" * 60)
        code2 = """
import json

# Generate some data
data = {
    "experiment": "sandbox-test",
    "results": [
        {"trial": 1, "value": 42.5},
        {"trial": 2, "value": 43.1},
        {"trial": 3, "value": 41.8}
    ],
    "summary": {
        "mean": 42.47,
        "success": True
    }
}

# Write to file in /sandbox (which is mounted to host)
with open('/sandbox/experiment_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✓ Created file: /sandbox/experiment_data.json")
"""
        output2 = sandbox.execute_code(code2)
        print(output2)
        
        # Example 3: Create a CSV file
        print("\nExample 3: Create a CSV file")
        print("-" * 60)
        code3 = """
# Write CSV data
csv_content = '''timestamp,temperature,humidity
2025-12-11 10:00,22.5,65
2025-12-11 11:00,23.1,63
2025-12-11 12:00,24.0,61
2025-12-11 13:00,24.5,60
'''

with open('/sandbox/sensor_data.csv', 'w') as f:
    f.write(csv_content)

print("✓ Created file: /sandbox/sensor_data.csv")
print(f"\\nContent:\\n{csv_content}")
"""
        output3 = sandbox.execute_code(code3)
        print(output3)
    
    # Show that files exist on host
    print("\n" + "=" * 60)
    print("Checking host filesystem...")
    print("=" * 60)
    
    host_dir = Path(f"/tmp/sandboxes/{session_id}")
    
    if host_dir.exists():
        print(f"\n✓ Session directory exists: {host_dir}\n")
        
        for file_path in host_dir.iterdir():
            if file_path.is_file() and not file_path.name.startswith('script_'):
                print(f"📄 {file_path.name}")
                print(f"   Size: {file_path.stat().st_size} bytes")
                
                # Show preview of content
                content = file_path.read_text()
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"   Preview:\n{preview}\n")
    else:
        print(f"✗ Session directory not found: {host_dir}")
    
    print("=" * 60)
    print("\nKey Points:")
    print("  • Python code runs in isolated Docker container")
    print("  • Files written to /sandbox in container appear on host")
    print(f"  • Host location: /tmp/sandboxes/{session_id}/")
    print("  • Each session gets its own directory")
    print("  • No access to host filesystem outside mounted volume")
    print("  • Safe for untrusted code execution")


if __name__ == "__main__":
    main()
