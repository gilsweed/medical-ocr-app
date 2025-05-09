import os
import sys
import time
import signal
import logging
import subprocess
import multiprocessing
import atexit
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Supervisor:
    def __init__(self):
        self.server_process = None
        self.port = None
        self.pid_file = None
        self.port_file = None
        self.shutdown_lock = multiprocessing.Lock()
        self.signal_handlers_restored = False
        self.last_signal_time = 0
        self.signal_count = 0
        self.process_group = None
        # Register cleanup on exit
        atexit.register(self.cleanup)

    def find_available_port(self, start_port=8080, max_port=8090):
        """Find an available port starting from start_port up to max_port."""
        for port in range(start_port, max_port + 1):
            try:
                # Try to bind to the port
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"No available ports between {start_port} and {max_port}")

    def start_server(self):
        """Start the Gunicorn server with the supervisor."""
        try:
            # Find an available port
            self.port = self.find_available_port()
            logger.info(f"Using port {self.port}")

            # Create PID and port files
            self.pid_file = Path(f"server_{self.port}.pid")
            self.port_file = Path(f"server_{self.port}.port")
            
            # Write port to file
            with open(self.port_file, 'w') as f:
                f.write(str(self.port))

            # Get the path to gunicorn in the virtual environment
            venv_path = Path('venv')
            gunicorn_path = venv_path / 'bin' / 'gunicorn'
            config_path = Path(__file__).parent / 'gunicorn.conf.py'

            # Start Gunicorn with the supervisor
            gunicorn_cmd = [
                str(gunicorn_path),
                "--config", str(config_path),
                "--bind", f"0.0.0.0:{self.port}",
                "--pid", str(self.pid_file),
                "main:app"
            ]

            # Start the server process
            self.server_process = subprocess.Popen(
                gunicorn_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            if self.server_process:
                self.process_group = os.getpgid(self.server_process.pid)
                logger.info(f"Started server with PID {self.server_process.pid}")

            # Monitor the server process
            while True:
                if self.server_process.poll() is not None:
                    logger.info(f"Server process ended with return code {self.server_process.returncode}")
                    break

                # Read output
                output = self.server_process.stdout.readline()
                if output:
                    logger.info(f"Server: {output.decode().strip()}")
                
                error = self.server_process.stderr.readline()
                if error:
                    logger.error(f"Server error: {error.decode().strip()}")

                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error starting server: {str(e)}")
            self.cleanup()
            sys.exit(1)

    def cleanup(self):
        """Clean up resources and terminate the server process."""
        with self.shutdown_lock:
            try:
                logger.info("Starting cleanup process...")
                
                # Remove PID and port files
                if self.pid_file and self.pid_file.exists():
                    self.pid_file.unlink()
                if self.port_file and self.port_file.exists():
                    self.port_file.unlink()

                # Terminate the server process
                if self.server_process:
                    logger.info(f"Terminating server process (PID: {self.server_process.pid})...")
                    try:
                        if self.process_group:
                            os.killpg(self.process_group, signal.SIGTERM)
                        else:
                            self.server_process.terminate()
                        self.server_process.wait(timeout=5)
                    except Exception as e:
                        logger.error(f"Error terminating process: {str(e)}")
                        try:
                            if self.process_group:
                                os.killpg(self.process_group, signal.SIGKILL)
                            else:
                                self.server_process.kill()
                        except Exception as e:
                            logger.error(f"Error killing process: {str(e)}")

                # Clean up multiprocessing resources
                logger.info("Cleaning up multiprocessing resources...")
                try:
                    if hasattr(multiprocessing, 'resource_tracker'):
                        multiprocessing.resource_tracker._resource_tracker._stop = True
                        multiprocessing.resource_tracker._resource_tracker.join()
                except Exception as e:
                    logger.error(f"Error during cleanup: {str(e)}")

                logger.info("Cleanup completed successfully")

            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")

    def handle_signal(self, signum, frame):
        """Handle termination signals."""
        current_time = time.time()
        self.signal_count += 1
        
        # Log signal details
        logger.info(f"Received signal {signum}")
        if self.last_signal_time > 0:
            time_since_last = current_time - self.last_signal_time
            logger.info(f"Time since last signal: {time_since_last:.3f}s")
        
        self.last_signal_time = current_time
        
        # Restore original signal handlers if not already done
        if not self.signal_handlers_restored:
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            self.signal_handlers_restored = True
        
        # Perform cleanup
        self.cleanup()
        
        # Exit with appropriate code
        sys.exit(0 if signum == signal.SIGTERM else 1)

def main():
    """Main entry point for the supervisor."""
    supervisor = Supervisor()
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, supervisor.handle_signal)
    signal.signal(signal.SIGINT, supervisor.handle_signal)
    
    try:
        supervisor.start_server()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        supervisor.cleanup()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        supervisor.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main() 