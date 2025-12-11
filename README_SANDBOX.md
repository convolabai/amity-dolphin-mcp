# Docker Sandbox for Secure Python Execution

This directory contains a Docker-based sandboxed Python executor that provides secure code execution with controlled filesystem access.

## Overview

The Docker sandbox provides:
- **Filesystem Isolation**: Code cannot access the host filesystem
- **Volume Mounting**: Files created in `/sandbox` inside the container appear at `/tmp/sandboxes/<session_id>` on the host
- **Session Management**: Each session gets its own isolated directory
- **Resource Limits**: CPU and memory constraints
- **Network Isolation**: Network disabled by default
- **Security**: Runs as non-root user with dropped capabilities

## Quick Start

### 1. Build the Docker Image

```bash
docker build -f Dockerfile.sandbox -t dolphin-python-sandbox .
```

### 2. Run the Example

```bash
python3 example_docker_sandbox.py
```

### 3. Run Tests

```bash
python3 test_docker_sandbox.py
```

## Usage

### Basic Usage

```python
from dolphin_mcp.docker_sandbox import DockerSandboxExecutor

# Create a sandbox with a session ID
with DockerSandboxExecutor(session_id="my-session") as sandbox:
    code = """
import json

# Do some computation
data = {"result": 42, "status": "success"}

# Write to /sandbox (appears on host at /tmp/sandboxes/my-session/)
with open('/sandbox/output.json', 'w') as f:
    json.dump(data, f, indent=2)

print("File created!")
"""
    
    output = sandbox.execute_code(code)
    print(output)
```

The file will appear on your host at `/tmp/sandboxes/my-session/output.json`.

### Integration with Reasoning System

The sandbox automatically integrates with the reasoning system when you set the environment variable:

```bash
export DOLPHIN_USE_DOCKER_SANDBOX=1
```

Then the reasoning system will automatically use Docker for Python execution:

```python
from dolphin_mcp.client import run_interaction
from dolphin_mcp.reasoning import ReasoningConfig

config = ReasoningConfig(enable_code_execution=True)

# This will use Docker sandbox if DOLPHIN_USE_DOCKER_SANDBOX=1
result = await run_interaction(
    user_query="Calculate fibonacci numbers and save to a file",
    reasoning_config=config,
    use_reasoning=True
)
```

### Configuration Options

```python
sandbox = DockerSandboxExecutor(
    session_id="my-session",           # Unique session identifier
    sandbox_base_dir="/tmp/sandboxes", # Base directory for volumes
    image_name="dolphin-python-sandbox", # Docker image to use
    memory_limit="512m",               # Memory limit
    cpu_quota=100000,                  # CPU quota (100000 = 1 CPU)
    enable_network=False,              # Enable/disable network
    timeout=30                         # Execution timeout in seconds
)
```

## How It Works

1. **Container Creation**: Each code execution creates a temporary Docker container
2. **Volume Mounting**: The host directory `/tmp/sandboxes/<session_id>` is mounted to `/sandbox` in the container
3. **Code Execution**: Python code runs inside the container with limited resources
4. **Output Capture**: stdout/stderr are captured and returned
5. **File Persistence**: Any files written to `/sandbox` persist on the host after container removal
6. **Cleanup**: Container is automatically removed after execution

## Directory Structure

```
Host:                           Container:
/tmp/sandboxes/                 
├── session-1/          ←→      /sandbox/
│   ├── output.json             
│   └── results.txt             
├── session-2/          ←→      /sandbox/
│   └── data.csv                
```

## Security Features

### Filesystem Isolation
- Cannot read/write host filesystem except mounted `/sandbox`
- Cannot access `/etc`, `/root`, `/home`, etc.
- No access to other sessions' directories

### Resource Limits
- Memory: 512MB default (configurable)
- CPU: 1 CPU default (configurable)
- Disk: 100MB for /tmp

### Network Isolation
- Network disabled by default
- Can be enabled if needed with `enable_network=True`

### Process Isolation
- Runs as non-root user `sandbox`
- All Linux capabilities dropped
- No new privileges can be acquired

### Example Security Test

```python
# This code will be blocked by the sandbox
code = """
import os

# Try to access host filesystem
try:
    with open('/etc/passwd', 'r') as f:
        print(f.read())
except Exception as e:
    print(f"Blocked: {e}")

# Try to list root directory
try:
    files = os.listdir('/home')
    print(files)
except Exception as e:
    print(f"Blocked: {e}")
"""

output = sandbox.execute_code(code)
# Will show errors - cannot access these paths
```

## Practical Examples

### Example 1: Data Analysis with File Output

```python
code = """
import json
import statistics

# Analyze data
data = [12, 15, 13, 18, 14, 16, 11, 19]
report = {
    'count': len(data),
    'mean': statistics.mean(data),
    'median': statistics.median(data),
    'stdev': statistics.stdev(data)
}

# Save report
with open('/sandbox/analysis.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f"Analysis complete: {report}")
"""

output = sandbox.execute_code(code)
# Report available at /tmp/sandboxes/<session_id>/analysis.json
```

### Example 2: Multi-step Computation

```python
# Step 1: Initialize
code1 = """
data = [1, 2, 3, 4, 5]
print(f"Initialized data: {data}")
"""
sandbox.execute_code(code1)

# Step 2: Process (variables persist)
code2 = """
result = sum(x**2 for x in data)
print(f"Sum of squares: {result}")

# Save to file
with open('/sandbox/result.txt', 'w') as f:
    f.write(f"Result: {result}\\n")
"""
sandbox.execute_code(code2)
```

## Available Libraries

The sandbox image includes:
- **numpy**: Numerical computing
- **pandas**: Data analysis
- **matplotlib**: Plotting (can save to files)
- **scipy**: Scientific computing
- **scikit-learn**: Machine learning

All standard library modules that don't require system access are also available.

## Troubleshooting

### Docker not found
```
RuntimeError: Docker is not available
```
**Solution**: Install Docker and ensure it's running.

### Image not found
```
RuntimeError: Docker image 'dolphin-python-sandbox' not found
```
**Solution**: Build the image with `docker build -f Dockerfile.sandbox -t dolphin-python-sandbox .`

### Permission denied on /tmp/sandboxes
```
PermissionError: [Errno 13] Permission denied: '/tmp/sandboxes'
```
**Solution**: Ensure the directory is writable:
```bash
mkdir -p /tmp/sandboxes
chmod 755 /tmp/sandboxes
```

## Cleanup

To clean up session directories:

```bash
# Remove all sandbox sessions
rm -rf /tmp/sandboxes/*

# Remove specific session
rm -rf /tmp/sandboxes/my-session
```

To clean up Docker resources:

```bash
# Remove stopped containers
docker container prune -f

# Remove the sandbox image
docker rmi dolphin-python-sandbox
```

## Comparison: Docker vs. In-Process Sandbox

| Feature | Docker Sandbox | In-Process Sandbox |
|---------|---------------|-------------------|
| Isolation | Strong (kernel-level) | Weak (Python-level) |
| Filesystem Access | Completely isolated | Can be bypassed |
| Resource Limits | Enforced by kernel | Best-effort only |
| Performance | Slower (container overhead) | Fast (direct execution) |
| Setup | Requires Docker | No dependencies |
| Security | Production-ready | Development only |

**Recommendation**: Use Docker sandbox for any untrusted code or production environments.
