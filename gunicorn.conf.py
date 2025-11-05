import os
import multiprocessing

# Bind to the PORT environment variable (required by Render)
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Worker configuration
workers = 1
threads = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'felix-hub'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (не используется на Render, но для будущего)
keyfile = None
certfile = None
