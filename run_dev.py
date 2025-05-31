#!/usr/bin/env python3
import subprocess
import sys
import os
import signal
import threading
import queue
import time
from typing import Optional, Tuple, List, Set, Dict, Any
import platform
import shutil
import importlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_node_installation():
    """Check Node.js and npm installation."""
    print("\nChecking Node.js and npm installation...")
    
    # Check Node.js
    node_path = shutil.which("node")
    if node_path:
        try:
            node_version = subprocess.check_output(["node", "--version"], text=True).strip()
            print(f"✓ Node.js found: {node_version} at {node_path}")
            
            # Try to find npm in the same directory as node
            node_dir = os.path.dirname(node_path)
            npm_cmd = os.path.join(node_dir, "npm.cmd" if platform.system() == "Windows" else "npm")
            
            if os.path.exists(npm_cmd):
                print(f"✓ npm found in Node.js directory: {npm_cmd}")
                # Add node directory to PATH temporarily
                os.environ["PATH"] = node_dir + os.pathsep + os.environ["PATH"]
                return npm_cmd
            else:
                print(f"✗ npm not found in Node.js directory: {node_dir}")
        except subprocess.CalledProcessError:
            print("✗ Node.js found but version check failed")
    else:
        print("✗ Node.js not found in PATH")
    
    return None

class ProcessMonitor:
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.output_queue = queue.Queue()
        self.is_running = True
        self.error_summary: List[str] = []
        self.npm_path = None

    def _find_npm_command(self) -> str:
        """Find the appropriate package manager command."""
        # First check for yarn
        yarn_path = shutil.which("yarn")
        if yarn_path:
            print(f"Using yarn from: {yarn_path}")
            return "yarn"
        
        # Use the npm path we found during installation check
        if self.npm_path:
            print(f"Using npm from: {self.npm_path}")
            return self.npm_path
            
        # Try to find npm in Node.js directory
        node_path = shutil.which("node")
        if node_path:
            node_dir = os.path.dirname(node_path)
            npm_cmd = os.path.join(node_dir, "npm.cmd" if platform.system() == "Windows" else "npm")
            if os.path.exists(npm_cmd):
                print(f"Using npm from Node.js directory: {npm_cmd}")
                return npm_cmd
            
        raise FileNotFoundError(
            "Neither npm nor yarn was found in PATH. "
            "Please install Node.js and npm, or yarn if you prefer."
        )

    def run_backend(self) -> None:
        """Run the backend FastAPI server."""
        try:
            # Check if uvicorn is installed
            try:
                import uvicorn
            except ImportError:
                self.error_summary.append(
                    "uvicorn not found. Please install it with: pip install uvicorn"
                )
                self.is_running = False
                return

            # Use python -m uvicorn for better cross-platform compatibility
            self.backend_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start output monitoring threads
            threading.Thread(target=self._monitor_output, args=(self.backend_process, "BACKEND"), daemon=True).start()
            
        except Exception as e:
            self.error_summary.append(f"Failed to start backend: {str(e)}")
            self.is_running = False

    def run_frontend(self) -> None:
        """Run the frontend Vite development server."""
        try:
            # Change to frontend directory
            frontend_dir = os.path.join(os.getcwd(), "frontend")
            if not os.path.exists(frontend_dir):
                raise FileNotFoundError(
                    f"Frontend directory not found: {frontend_dir}\n"
                    "Please ensure you're running this script from the project root directory."
                )

            # Check for package.json
            package_json = os.path.join(frontend_dir, "package.json")
            if not os.path.exists(package_json):
                raise FileNotFoundError(
                    f"package.json not found in {frontend_dir}\n"
                    "Please ensure the frontend directory is properly initialized."
                )

            # Find npm command
            npm_cmd = self._find_npm_command()

            # Check if node_modules exists
            node_modules = os.path.join(frontend_dir, "node_modules")
            if not os.path.exists(node_modules):
                print("[FRONTEND] Installing dependencies...")
                install_process = subprocess.run(
                    [npm_cmd, "install"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True
                )
                if install_process.returncode != 0:
                    raise RuntimeError(
                        f"Failed to install dependencies:\n{install_process.stderr}"
                    )

            # Start the frontend process
            self.frontend_process = subprocess.Popen(
                [npm_cmd, "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start output monitoring threads
            threading.Thread(target=self._monitor_output, args=(self.frontend_process, "FRONTEND"), daemon=True).start()
            
        except Exception as e:
            self.error_summary.append(f"Failed to start frontend: {str(e)}")
            self.is_running = False

    def _monitor_output(self, process: subprocess.Popen, prefix: str) -> None:
        """Monitor and queue process output."""
        def enqueue_output(pipe, prefix: str):
            for line in iter(pipe.readline, ''):
                if not self.is_running:
                    break
                self.output_queue.put(f"[{prefix}] {line.strip()}")
            pipe.close()

        # Start threads to monitor stdout and stderr
        threading.Thread(target=enqueue_output, args=(process.stdout, prefix), daemon=True).start()
        threading.Thread(target=enqueue_output, args=(process.stderr, prefix), daemon=True).start()

        # Monitor process status
        while self.is_running:
            if process.poll() is not None:
                exit_code = process.poll()
                if exit_code != 0:
                    self.error_summary.append(f"{prefix} process exited with code {exit_code}")
                self.is_running = False
                break
            time.sleep(0.1)

    def print_output(self) -> None:
        """Print queued output from both processes."""
        while self.is_running or not self.output_queue.empty():
            try:
                line = self.output_queue.get_nowait()
                print(line)
            except queue.Empty:
                time.sleep(0.1)

    def cleanup(self) -> None:
        """Clean up processes and print error summary."""
        self.is_running = False

        # Terminate processes
        for process in [self.backend_process, self.frontend_process]:
            if process and process.poll() is None:
                if platform.system() == "Windows":
                    process.terminate()
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if platform.system() == "Windows":
                        process.kill()
                    else:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)

        # Print error summary
        if self.error_summary:
            print("\nError Summary:")
            for error in self.error_summary:
                print(f"- {error}")

def check_node_npm():
    """Check if Node.js and npm are installed."""
    npm_path = check_node_installation()
    if not npm_path:
        logger.error("❌ Node.js or npm not found. Please install them first.")
        return False
    return True

def find_all_python_files(start_dir: str) -> List[str]:
    """Find all Python files in the given directory and its subdirectories."""
    python_files = []
    for root, _, files in os.walk(start_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def check_imports() -> Dict[str, List[str]]:
    """Check all Python files for import errors."""
    errors = {}
    app_dir = os.path.join(os.getcwd(), 'app')
    
    # Get all Python files
    python_files = find_all_python_files(app_dir)
    
    # Try importing each module
    for file_path in python_files:
        # Convert file path to module path
        rel_path = os.path.relpath(file_path, os.getcwd())
        module_path = rel_path.replace(os.sep, '.').replace('.py', '')
        
        try:
            importlib.import_module(module_path)
        except ImportError as e:
            errors[module_path] = str(e)
        except Exception as e:
            errors[module_path] = f"Unexpected error: {str(e)}"
    
    return errors

def main():
    # Print startup message
    print("Starting development servers...")
    print("Press Ctrl+C to stop all servers\n")
    
    # Check Node.js installation first
    if not check_node_npm():
        sys.exit(1)
    
    # Check all imports
    logger.info("Checking all Python imports...")
    import_errors = check_imports()
    
    if import_errors:
        logger.error("\nImport errors found:")
        for module, error in import_errors.items():
            logger.error(f"\n{module}:")
            logger.error(f"  {error}")
        sys.exit(1)
    
    logger.info("✓ All imports checked successfully")
    
    monitor = ProcessMonitor()
    
    # Start both processes
    monitor.run_backend()
    monitor.run_frontend()
    
    # Print output until processes exit
    monitor.print_output()
    
    # Cleanup and exit
    monitor.cleanup()
    sys.exit(1 if monitor.error_summary else 0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0) 