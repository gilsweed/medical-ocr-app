import os
import sys
import signal
import logging
import atexit
import multiprocessing
from pathlib import Path
import psutil
import socket
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessManager:
    def __init__(self):
        self.process = None
        self.port = None
        self.pid_file = None
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        atexit.register(self.cleanup)

    def _handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}")
        self.cleanup()
        sys.exit(0)

    def find_free_port(self, start_port=8080, max_port=8090):
        for port in range(start_port, max_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("No free ports available")

    def start_server(self):
        try:
            self.port = self.find_free_port()
            logger.info(f"Using port {self.port}")

            # Create PID file
            self.pid_file = Path(f"server_{self.port}.pid")
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))

            # Start Gunicorn
            cmd = [
                'gunicorn',
                '--config', 'gunicorn.conf.py',
                '--bind', f'0.0.0.0:{self.port}',
                'app:app'
            ]

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )

            logger.info(f"Started server with PID {self.process.pid}")
            return True

        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            self.cleanup()
            return False

    def cleanup(self):
        try:
            logger.info("Starting cleanup process...")

            # Kill the server process
            if self.process:
                logger.info(f"Terminating server process (PID: {self.process.pid})...")
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                    self.process.wait(timeout=5)
                except ProcessLookupError:
                    logger.error("Process already terminated")
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)

            # Remove PID file
            if self.pid_file and self.pid_file.exists():
                self.pid_file.unlink()

            # Clean up any remaining processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'gunicorn' in ' '.join(proc.info['cmdline'] or []):
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            logger.info("Cleanup completed successfully")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def main():
    manager = ProcessManager()
    if manager.start_server():
        try:
            manager.process.wait()
        except KeyboardInterrupt:
            pass
        finally:
            manager.cleanup()

if __name__ == '__main__':
    main() 