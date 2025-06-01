import multiprocessing
import os
import tempfile
import atexit
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes
workers = 1  # Single worker for development
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Process naming
proc_name = "ocr_app"

# Server mechanics
daemon = False
pidfile = None  # Don't use pidfile
umask = 0
user = None
group = None
tmp_upload_dir = tempfile.mkdtemp(prefix="ocr_app_")

# SSL
keyfile = None
certfile = None

# Server hooks
def on_starting(server):
    """Log when server starts."""
    logger.info("Starting OCR server")

def on_exit(server):
    """Log when server exits."""
    logger.info("OCR server shutting down")
    try:
        # Clean up temp directory
        if tmp_upload_dir and os.path.exists(tmp_upload_dir):
            import shutil
            shutil.rmtree(tmp_upload_dir, ignore_errors=True)
    except Exception as e:
        logger.error(f"Error cleaning up temp directory: {e}")

def worker_int(worker):
    """Log when worker receives SIGINT or SIGQUIT."""
    logger.info("Worker received SIGINT or SIGQUIT")

def worker_abort(worker):
    """Log when worker receives SIGABRT."""
    logger.info("Worker received SIGABRT")

# Gunicorn config variables
preload_app = True
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30

# Resource management
max_worker_lifetime = 3600  # Restart workers after 1 hour
max_worker_lifetime_jitter = 60  # Add some randomness to worker restarts
worker_tmp_dir = tempfile.gettempdir()  # Use system temp directory

# Register cleanup handler
atexit.register(on_exit)

# Application
wsgi_app = "app:app" 