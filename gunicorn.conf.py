bind = '0.0.0.0:8000'  # This should match the port specified in your Dockerfile CMD
workers = 3  # Number of worker processes
threads = 3  # Number of worker threads per worker process
timeout = 60  # Timeout for worker processes
