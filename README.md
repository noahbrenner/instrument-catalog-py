Musical Instrument Catalog Server
=================================

Running the server locally
--------------------------

```bash
# Here's the most simple option
python3 run.py
# You can also specify a port (assuming a UNIX-style shell)
PORT=5000 python3 run.py

# To run more similarly to production:
heroku local web # This requires you to have the heroku CLI installed

# Do the same without requiring external dependencies
gunicorn instrument_catalog:app
# You can also specify a host and port,
# which may be needed to avoid other OS configuration steps
gunicorn --bind 0.0.0.0:8000 instrument_catalog:app
```
