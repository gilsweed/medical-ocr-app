import os
import sys
import signal
import atexit
import socket
import time
import tempfile
import shutil
from pathlib import Path
import psutil

print(f"[DEBUG] Supervisor PID: {os.getpid()} CMD: {' '.join(sys.argv)}")

def get_python_executable():
    # If running as a PyInstaller bundle, use 'python3' from PATH
    if getattr(sys, 'frozen', False):
        return 'python3'
    else:
        return sys.executable

class ProcessManager:
    def __init__(self):
        self.server_process = None
        self.port = None
        self.temp_dir = None
        self.is_running = True

    def handle_signal(self, signum, frame):
        """Handle termination signals."""
        print(f"Received signal {signum}")
        self.is_running = False
        self.cleanup()
        sys.exit(0)

    def cleanup_old_processes(self):
        """Clean up any existing Python processes."""
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.pid == current_pid:
                    continue
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('main.py' in cmd for cmd in cmdline if cmd):
                        print(f"Terminating old process {proc.pid}")
                        proc.terminate()
                        try:
                            proc.wait(timeout=1)
                        except psutil.TimeoutExpired:
                            proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def find_free_port(self, start_port=8080, max_attempts=10):
        """Find an available port."""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

    def start_server(self):
        """Start the Flask development server."""
        try:
            # Find a free port
            self.port = self.find_free_port()
            print(f"Using port {self.port}")

            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()

            # Set environment variables
            env = os.environ.copy()
            env['FLASK_APP'] = 'main.py'
            env['FLASK_ENV'] = 'development'
            env['PYTHONUNBUFFERED'] = '1'

            # Start the server
            self.server_process = psutil.Popen(
                [get_python_executable(), '-m', 'flask', 'run', 
                 '--host=0.0.0.0', f'--port={self.port}',
                 '--no-debugger', '--no-reload'],
                env=env,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            print(f"Started server with PID {self.server_process.pid}")
            print(f"[DEBUG] Child CMD: {self.server_process.args}")

        except Exception as e:
            print(f"Error starting server: {e}")
            self.cleanup()
            sys.exit(1)

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.server_process:
                print(f"Terminating server process (PID: {self.server_process.pid})...")
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    self.server_process.kill()
                    self.server_process.wait()

            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

        except Exception as e:
            print(f"Error during cleanup: {e}")

def main():
    # Create process manager
    manager = ProcessManager()

    # Register signal handlers
    signal.signal(signal.SIGTERM, manager.handle_signal)
    signal.signal(signal.SIGINT, manager.handle_signal)

    # Register cleanup function
    atexit.register(manager.cleanup)

    # Clean up any existing processes
    manager.cleanup_old_processes()

    # Start the server
    manager.start_server()

    print('Entering main loop...')
    # Keep the main process running
    while manager.is_running:
        time.sleep(1)
    print('Exited main loop.')

if __name__ == '__main__':
    main() 