import os
import sys
import signal
import logging
import atexit
import multiprocessing
from pathlib import Path
import psutil
import socket
import time
import tempfile
import shutil
from main import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessManager:
    def __init__(self):
        self.server_process = None
        self.port_file = Path("port.txt")
        self.temp_dir = tempfile.mkdtemp(prefix="ocr_app_")
        self.setup_signal_handlers()
        self.cleanup_old_processes()

    def setup_signal_handlers(self):
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
        atexit.register(self.cleanup)

    def handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}")
        self.cleanup()
        sys.exit(0)

    def cleanup_old_processes(self):
        """Clean up any existing Python processes from previous runs."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any('main.py' in cmd for cmd in cmdline if cmd):
                            if proc.pid != os.getpid():
                                logger.info(f"Terminating old process {proc.pid}")
                                proc.terminate()
                                proc.wait(timeout=1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.error(f"Error cleaning up old processes: {e}")

    def find_free_port(self, start_port=8080, max_port=9000):
        for port in range(start_port, max_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("No free ports found")

    def start_server(self):
        try:
            # Find a free port
            port = self.find_free_port()
            logger.info(f"Using port {port}")

            # Save port to file
            with open(self.port_file, 'w') as f:
                f.write(str(port))

            # Set up environment variables
            env = os.environ.copy()
            env.update({
                'PYTHONUNBUFFERED': '1',
                'PYTHONPATH': os.getcwd(),
                'TEMP_DIR': self.temp_dir,
                'FLASK_APP': 'main.py',
                'FLASK_ENV': 'development'
            })

            # Start Flask development server
            self.server_process = multiprocessing.Process(
                target=self._run_server,
                args=(port, env),
                daemon=True
            )
            self.server_process.start()

            logger.info(f"Started server with PID {self.server_process.pid}")
            return self.server_process

        except Exception as e:
            logger.error(f"Error starting server: {e}")
            self.cleanup()
            raise

    def _run_server(self, port, env):
        try:
            app.run(
                host='0.0.0.0',
                port=port,
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)

    def cleanup(self):
        logger.info("Starting cleanup process...")
        try:
            # Terminate server process
            if self.server_process and self.server_process.is_alive():
                logger.info(f"Terminating server process (PID: {self.server_process.pid})...")
                try:
                    self.server_process.terminate()
                    self.server_process.join(timeout=5)
                    if self.server_process.is_alive():
                        self.server_process.kill()
                except Exception as e:
                    logger.error(f"Error terminating process: {e}")

            # Remove port file
            if self.port_file.exists():
                try:
                    self.port_file.unlink()
                except Exception as e:
                    logger.error(f"Error removing port file: {e}")

            # Clean up temp directory
            try:
                if os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")

            # Clean up any remaining Python processes
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] and 'python' in proc.info['name'].lower():
                            cmdline = proc.info['cmdline']
                            if cmdline and any('main.py' in cmd for cmd in cmdline if cmd):
                                if proc.pid != os.getpid():
                                    proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except Exception as e:
                logger.error(f"Error cleaning up remaining processes: {e}")

            # Clean up multiprocessing resources
            try:
                if hasattr(multiprocessing, 'resource_tracker'):
                    multiprocessing.resource_tracker._resource_tracker._stop()
            except Exception as e:
                logger.error(f"Error cleaning up multiprocessing resources: {e}")

            logger.info("Cleanup completed successfully")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def main():
    manager = ProcessManager()
    try:
        manager.start_server()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main() 