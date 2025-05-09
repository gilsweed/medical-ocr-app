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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessManager:
    def __init__(self):
        self.server_process = None
        self.pid_file = Path("server.pid")
        self.port_file = Path("port.txt")
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
        atexit.register(self.cleanup)

    def handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}")
        self.cleanup()
        sys.exit(0)

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

            # Start Gunicorn server
            cmd = [
                "gunicorn",
                "--config", "gunicorn.conf.py",
                f"--bind", f"0.0.0.0:{port}",
                "app:app"
            ]

            self.server_process = multiprocessing.Process(
                target=self._run_server,
                args=(cmd,),
                daemon=True
            )
            self.server_process.start()

            # Save PID to file
            with open(self.pid_file, 'w') as f:
                f.write(str(self.server_process.pid))

            logger.info(f"Started server with PID {self.server_process.pid}")
            return self.server_process

        except Exception as e:
            logger.error(f"Error starting server: {e}")
            self.cleanup()
            raise

    def _run_server(self, cmd):
        try:
            os.execvp(cmd[0], cmd)
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)

    def cleanup(self):
        logger.info("Starting cleanup process...")
        try:
            # Terminate server process
            if self.server_process and self.server_process.is_alive():
                logger.info(f"Terminating server process (PID: {self.server_process.pid})...")
                self.server_process.terminate()
                self.server_process.join(timeout=5)
                if self.server_process.is_alive():
                    self.server_process.kill()

            # Remove PID file
            if self.pid_file.exists():
                self.pid_file.unlink()

            # Remove port file
            if self.port_file.exists():
                self.port_file.unlink()

            # Clean up any remaining Gunicorn processes
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