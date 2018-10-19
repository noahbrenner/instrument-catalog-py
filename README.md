Musical Instrument Catalog Server
=================================

Check out this app running live: https://instrument-catalog-py.herokuapp.com/

Running the server locally
--------------------------

```bash
# Here's the most simple option, which runs on port 8000
flask run
# You can also specify a port (assuming a UNIX-style shell)
flask run --port 5000

# To run more similarly to production:
heroku local web # This requires you to have the Heroku CLI installed

# Do the same without requiring external dependencies
gunicorn instrument_catalog:app
# You can also specify a host and port, which may be needed to avoid other OS
# configuration steps or if you're running the server on a virtual machine.
gunicorn --bind 0.0.0.0:8000 instrument_catalog:app
```
