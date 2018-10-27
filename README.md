Musical Instrument Catalog (web app)
====================================

Check out this app running live: https://instrument-catalog-py.herokuapp.com/

The sample server is running on a free Heroku dyno, so it may take a minute to boot up when you first visit the site, but then it should be nice and snappy!

The app also has a JSON API. You can find the documentation for it on the site itself or [here in this repo][API].

Setup
-----

1. Make sure [Python][] is installed. This app requires Python 3.5 at minimum. It will not run on Python 2.
2. Install [Pipenv][] if you don't have it already. You can find simple instructions for installing it here: https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv
3. Clone this repository and change to its directory:
   ```bash
   $ git clone https://github.com/noahbrenner/instrument-catalog-py.git
   $ cd instrument-catalog-py
   ```
4. Initialize Pipenv environment and install app dependencies:
   ```bash
   $ pipenv --python 3

   # The `--ignore-pipfile` option is optional but recommended so that you
   # install the same dependency versions as those used in development.
   $ pipenv install --ignore-pipfile
   ```

Server configuration
--------------------

This app depends on some environment variables for configuration. In development on your local machine, you can set them in a file named `.env` in the project's root directory if you don't want to type them out each time you restart your shell. The `.env` file is included in the `.gitignore` file so it won't be accidentally committed. In production, you should just set the variables without using this file.


For running in a development environment you only need these environment variables:

```bash
# Google OAuth credentials (see below for details)
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
# Don't require https (otherwise you couldn't test login functionality locally)
OAUTHLIB_INSECURE_TRANSPORT=true
```

In production, you'll need to set these:

```bash
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
SECRET_KEY=<your_very_secure_secret_key>
DATABASE_URL=postgres://<your_postgres_url>
```

### OAuth credentials

You'll need to register a web application with Google to get OAuth credentials, which you can do here: https://console.developers.google.com/

For local development, you can choose "Internal" as your application type. This will allow you to use `localhost` addresses. For a non-`localhost` address, you'll need to chose "Public" instead.

You'll need to enter some specific "Authorized redirect URIs" that Google can redirect users to who are trying to connect with your app. Assuming your server will run at `localhost:8000`, enter these URIs in that section:

<!--
TODO Authorized JavaScript origins:

* http://localhost:8000
-->

* `http://localhost:8000/auth/google/`
* `http://localhost:8000/auth/google/authorized`

Running the server
------------------

First, activate the Pipenv environment subshell:

```bash
$ pipenv shell
```

Then start the server using any of these options:

```bash
# Start the server locally on port 8000
flask run

# You can also specify a different port
flask run --port 5000

# To run more similarly to a production environment:

# If you to have the Heroku CLI installed, you can use this option
heroku local web

# Otherwise run this, which is exactly what you'd run in production
gunicorn instrument_catalog:app

# You can also specify a host and port, which may be needed when running
# locally to avoid other OS configuration steps (likely needed if you're
# running the server on a virtual machine).
gunicorn --bind 0.0.0.0:8000 instrument_catalog:app
```

Now, open up the app in your browser!
http://localhost:8000

[API]: instrument_catalog/doc/api.md
[Python]: https://www.python.org/downloads.
[Pipenv]: https://pipenv.readthedocs.io/en/latest/
