"""
Docker-based sandboxed Python executor for Dolphin MCP.

This module provides a secure Python execution environment using Docker containers
with controlled volume mounting. Files created in the mounted directory inside the 
sandbox are mapped to a directory on the host (default: /tmp/sandboxes/<session_id>).
"""

import docker
import uuid
import os
import tempfile
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DockerSandboxExecutor:
    """
    Docker-based Python sandbox executor with volume mounting.
    
    Features:
    - Isolated Python execution environment
    - No access to host filesystem except mounted volumes
    - Files created in container mount path appear on host at <sandbox_base_dir>/<session_id>
    - Resource limits (CPU, memory, network)
    - Non-root user execution for additional security
    """
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        sandbox_base_dir: str = "/tmp/sandboxes",
        container_mount_path: str = "/sandbox",
        image_name: str = "dolphin-python-sandbox",
        image_tag: str = "latest",
        memory_limit: str = "512m",
        cpu_quota: int = 100000,  # 100% of one CPU
        enable_network: bool = False,
        timeout: int = 30
    ):
        """
        Initialize the Docker sandbox executor.
        
        Args:
            session_id: Unique session identifier (generated if not provided)
            sandbox_base_dir: Base directory on host for sandbox volumes
            container_mount_path: Path inside container where host directory is mounted (default: /sandbox)
            image_name: Docker image name to use
            image_tag: Docker image tag/version (default: "latest")
            memory_limit: Memory limit (e.g., "512m", "1g")
            cpu_quota: CPU quota in microseconds (100000 = 1 CPU)
            enable_network: Whether to enable network access
            timeout: Execution timeout in seconds
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.sandbox_base_dir = Path(sandbox_base_dir)
        self.container_mount_path = container_mount_path
        self.image_name = image_name
        self.image_tag = image_tag
        self.full_image_name = f"{image_name}:{image_tag}"
        self.memory_limit = memory_limit
        self.cpu_quota = cpu_quota
        self.enable_network = enable_network
        self.timeout = timeout
        
        # Create session-specific directory
        self.session_dir = self.sandbox_base_dir / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Docker client
        try:
            # On macOS, Docker Desktop uses a different socket location
            # Try common socket locations
            docker_client = None
            socket_locations = [
                os.path.expanduser("~/.docker/run/docker.sock"),  # macOS Docker Desktop
                "/var/run/docker.sock",  # Linux/standard location
            ]
            
            # Try to connect using environment variables first
            try:
                docker_client = docker.from_env()
                docker_client.ping()
            except:
                # If from_env() fails, try explicit socket locations
                for socket_path in socket_locations:
                    if os.path.exists(socket_path):
                        try:
                            docker_client = docker.DockerClient(base_url=f"unix://{socket_path}")
                            docker_client.ping()
                            break
                        except:
                            continue
            
            if docker_client is None:
                raise RuntimeError("Could not connect to Docker daemon")
            
            self.docker_client = docker_client
            logger.info(f"Docker client initialized for session {self.session_id}")
            
        except docker.errors.DockerException as e:
            logger.error(f"Failed to connect to Docker daemon: {e}")
            raise RuntimeError(
                f"Docker daemon is not available. Please ensure Docker Desktop is running.\n"
                f"Error: {e}\n"
                f"On macOS, start Docker Desktop from Applications or run: open -a Docker"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise RuntimeError(f"Docker is not available: {e}")
        
        # Ensure the sandbox image exists
        self._ensure_image_exists()
    
    def _ensure_image_exists(self):
        """Check if the sandbox image exists, build if not."""
        try:
            self.docker_client.images.get(self.full_image_name)
            logger.info(f"Using existing Docker image: {self.full_image_name}")
        except docker.errors.ImageNotFound:
            logger.warning(f"Image {self.full_image_name} not found. Please build it first.")
            logger.info(f"Run: docker build -f Dockerfile.sandbox -t {self.full_image_name} .")

            raise RuntimeError(
                f"Docker image '{self.full_image_name}' not found. "
                f"Build it with: docker build -f Dockerfile.sandbox -t {self.full_image_name} ."
            )
    
    def execute_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute Python code in a sandboxed Docker container.
        
        Args:
            code: Python code to execute
            context: Optional context dictionary (serialized and passed to container)
            
        Returns:
            String output from the code execution
        """
        # Create a temporary Python script
        script_path = self.session_dir / f"script_{uuid.uuid4().hex[:8]}.py"
        
        try:
            # Prepare the full script with context loading
            full_script = self._prepare_script(code, context)
            
            # Write script to host
            script_path.write_text(full_script)
            
            # Setup volume mounts
            volumes = {
                str(self.session_dir): {
                    'bind': self.container_mount_path,
                    'mode': 'rw'
                }
            }
            
            # Configure network
            network_mode = 'none' if not self.enable_network else 'bridge'
            
            # Run the container
            logger.info(f"Executing code in Docker container (session: {self.session_id})")
            
            # Create and start container with timeout handling
            container = self.docker_client.containers.create(
                image=self.full_image_name,
                command=["python3", f"{self.container_mount_path}/{script_path.name}"],
                volumes=volumes,
                network_mode=network_mode,
                mem_limit=self.memory_limit,
                cpu_quota=self.cpu_quota,
                user="sandbox",  # Run as non-root user
                security_opt=["no-new-privileges"],  # Additional security
                cap_drop=["ALL"],  # Drop all capabilities
                read_only=False,  # Allow writes to mounted volumes
                tmpfs={'/tmp': 'size=100M,mode=1777'},  # Writable /tmp with size limit
            )
            
            try:
                container.start()
                exit_status = container.wait(timeout=self.timeout)
                
                # Get logs (output)
                result = container.logs(stdout=True, stderr=True)
                
            finally:
                # Always remove the container
                try:
                    container.remove(force=True)
                except:
                    pass
            
            # Decode output
            output = result.decode('utf-8')
            logger.info(f"Code executed successfully in session {self.session_id}")
            
            return output
            
        except docker.errors.ContainerError as e:
            error_msg = f"Container execution error:\n{e.stderr.decode('utf-8')}"
            logger.error(error_msg)
            return f"EXECUTION ERROR:\n{error_msg}"
            
        except Exception as e:
            error_msg = f"Unexpected error:\n{traceback.format_exc()}"
            logger.error(error_msg)
            return f"ERROR:\n{error_msg}"
            
        finally:
            # Optionally clean up script file
            if script_path.exists():
                try:
                    script_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to cleanup script file: {e}")
    
    def _prepare_script(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Prepare the Python script with context loading.
        
        Args:
            code: User's Python code
            context: Optional context dictionary
            
        Returns:
            Complete Python script to execute
        """
        script_parts = [
            "#!/usr/bin/env python3",
            "# Sandboxed Python execution",
            "import sys",
            "import json",
            "import traceback",
            ""
        ]
        
        # Load context if provided
        if context:
            script_parts.extend([
                "# Load context",
                "import pickle",
                "context = " + repr(context),
                "# Inject context into globals",
                "globals().update(context)",
                ""
            ])
        
        # Add user code
        script_parts.extend([
            "# User code",
            "try:",
            "    # Execute user code",
        ])
        
        # Indent user code
        for line in code.split('\n'):
            script_parts.append("    " + line)
        
        script_parts.extend([
            "",
            "except Exception as e:",
            "    print('EXECUTION ERROR:', file=sys.stderr)",
            "    traceback.print_exc()",
            "    sys.exit(1)"
        ])
        
        return '\n'.join(script_parts)
    
    def get_session_files(self) -> list:
        """
        Get list of files created in the session directory.
        
        Returns:
            List of file paths relative to session directory
        """
        if not self.session_dir.exists():
            return []
        
        files = []
        for item in self.session_dir.rglob('*'):
            if item.is_file() and not item.name.startswith('script_'):
                files.append(str(item.relative_to(self.session_dir)))
        
        return files
    
    def read_session_file(self, filename: str) -> str:
        """
        Read a file from the session directory.
        
        Args:
            filename: Filename relative to session directory
            
        Returns:
            File contents as string
        """
        file_path = self.session_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        
        if not file_path.is_relative_to(self.session_dir):
            raise ValueError("Path traversal attempt detected")
        
        return file_path.read_text()
    
    def cleanup(self):
        """
        Clean up session directory and resources.
        """
        try:
            if self.session_dir.exists():
                import shutil
                shutil.rmtree(self.session_dir)
                logger.info(f"Cleaned up session directory: {self.session_id}")
        except Exception as e:
            logger.error(f"Failed to cleanup session {self.session_id}: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        # Optionally cleanup on exit
        # self.cleanup()
        pass


def sandboxed_python_interpreter(
    code: str, 
    context: Dict[str, Any], 
    session_id: Optional[str] = None,
    image_name: str = "dolphin-python-sandbox",
    image_tag: str = "latest"
) -> str:
    """
    Execute Python code in a Docker sandbox with volume mounting.
    
    This is a drop-in replacement for the original python_interpreter function
    but with Docker-based isolation.
    
    Args:
        code: Python code to execute
        context: Persistent execution context (dictionary of variables)
        session_id: Optional session ID for volume mounting
        image_name: Docker image name to use (default: "dolphin-python-sandbox")
        image_tag: Docker image tag/version (default: "latest")
        
    Returns:
        String output from the code execution
    """
    # Use or create session_id
    if session_id is None:
        # Try to get session_id from context if it exists
        session_id = context.get('__sandbox_session_id__')
        if session_id is None:
            session_id = str(uuid.uuid4())
            context['__sandbox_session_id__'] = session_id
    
    try:
        executor = DockerSandboxExecutor(session_id=session_id, image_name=image_name, image_tag=image_tag)
        output = executor.execute_code(code, context)
        return output
    except Exception as e:
        return f"SANDBOX ERROR:\n{traceback.format_exc()}"


# Export main classes and functions
__all__ = [
    'DockerSandboxExecutor',
    'sandboxed_python_interpreter'
]
