import os
import socket
import logging
import atexit
import signal
import psutil
import time
import multiprocessing
from pathlib import Path

# Get the absolute path of the backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PORT_FILE = os.path.join(BACKEND_DIR, 'port.txt')

logger = logging.getLogger(__name__)

def cleanup_resources():
    """Clean up resources when the server shuts down."""
    try:
        # Remove port file
        port_file = Path(PORT_FILE)
        if port_file.exists():
            port_file.unlink()
            logger.info("Removed port file")

        # Kill any orphaned Python processes
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Skip the current process
                if proc.pid == current_pid:
                    continue

                # Check if it's a Python process running our script
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('main.py' in cmd for cmd in cmdline if cmd):
                        logger.info(f"Terminating orphaned process {proc.pid}")
                        # Try graceful termination first
                        proc.terminate()
                        try:
                            proc.wait(timeout=1)
                        except psutil.TimeoutExpired:
                            # Force kill if graceful termination fails
                            proc.kill()
                            proc.wait(timeout=1)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
            except Exception as e:
                logger.error(f"Error cleaning up process {proc.pid}: {e}")

        # Clean up multiprocessing resources
        try:
            # Get all active multiprocessing contexts
            contexts = [multiprocessing.get_context(method) for method in ['spawn', 'fork', 'forkserver']]
            for ctx in contexts:
                try:
                    # Close any pools
                    if hasattr(ctx, 'Pool'):
                        ctx.Pool().close()
                    # Clean up any remaining resources
                    if hasattr(ctx, 'cleanup'):
                        ctx.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up multiprocessing context: {e}")
        except Exception as e:
            logger.error(f"Error cleaning up multiprocessing resources: {e}")

        # Wait a moment for processes to clean up
        time.sleep(0.5)
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def find_available_port(start_port=8080, max_attempts=10):
    """
    Find an available port starting from start_port.
    Will try up to max_attempts different ports.
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

# Server Configuration
HOST = '0.0.0.0'
DEFAULT_PORT = 8080
PORT = find_available_port(DEFAULT_PORT)

# Logging Configuration
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# OCR Configuration
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png']
SUPPORTED_PDF_FORMATS = ['.pdf']
SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS + SUPPORTED_PDF_FORMATS

def save_port_to_file():
    """Save the current port to a file for the frontend to read."""
    try:
        # Ensure the backend directory exists
        os.makedirs(BACKEND_DIR, exist_ok=True)
        
        # Write the port to the file
        with open(PORT_FILE, 'w') as f:
            f.write(str(PORT))
        logger.info(f"Port {PORT} saved to {PORT_FILE}")
    except Exception as e:
        logger.error(f"Failed to save port to file: {e}")
        raise

# Register cleanup function
atexit.register(cleanup_resources)

# Register signal handlers
def signal_handler(signum, frame):
    """Handle termination signals."""
    logger.info(f"Received signal {signum}")
    cleanup_resources()
    os._exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler) 