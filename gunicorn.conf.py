import os
import multiprocessing

# Bind to PORT if defined, otherwise default to 8000
port = int(os.environ.get('PORT', '8000'))
bind = f'0.0.0.0:{port}'

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = 'gthread'

# Number of threads per worker
threads = 4

# Timeout
timeout = 120

# Access log - writes to stdout by default
accesslog = '-'

# Error log - writes to stderr by default
errorlog = '-'

# Log level
loglevel = 'info'

# Preload application code before worker processes are forked
preload_app = True

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50 