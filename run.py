#!/usr/bin/env python3
"""
Instrument Catalog development server
-------------------------------------

This is a convenience module for starting up the server locally.
See README.md for how it should be started in production.

By default, the server runs on port 8000.
However, a different port may be specified when starting the server:
    $ PORT=5000 python3 run.py
"""
import os
from instrument_catalog import app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', '8000'))
