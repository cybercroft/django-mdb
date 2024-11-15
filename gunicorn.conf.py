# gunicorn.conf.py
# Non logging stuff
bind = "0.0.0.0:8000"
workers = 3
# Whether to send Django output to the error log 
capture_output = True
# How verbose the Gunicorn error logs should be 
loglevel = "debug"