import multiprocessing
import os
import tempfile
import atexit

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "access.log"
errorlog = "error.log"
loglevel = "info"

# Process naming
proc_name = "ocr_app"

# Server mechanics
daemon = False
pidfile = "server.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Server hooks
def on_starting(server):
    """Log when server starts."""
    server.log.info("Starting OCR server")

def on_exit(server):
    """Log when server exits."""
    server.log.info("OCR server shutting down")
    # Clean up any remaining semaphores
    if hasattr(multiprocessing, 'resource_tracker'):
        try:
            multiprocessing.resource_tracker._resource_tracker._stop = True
            multiprocessing.resource_tracker._resource_tracker.join()
        except Exception as e:
            server.log.error(f"Error cleaning up resources: {e}")

def worker_int(worker):
    """Log when worker receives SIGINT or SIGQUIT."""
    worker.log.info("Worker received SIGINT or SIGQUIT")

def worker_abort(worker):
    """Log when worker receives SIGABRT."""
    worker.log.info("Worker received SIGABRT")

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