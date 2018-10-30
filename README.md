Musical Instrument Catalog (web app)
====================================

Check out this app running live: https://instrument-catalog-py.herokuapp.com/

The sample server is running on a free Heroku dyno, so it may take a minute to boot up when you first visit the site, but then it should be nice and snappy!

The app also has a JSON API. You can find the documentation for it on the site itself or [here in this repo][API].

Installation
------------

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

Before you can run the server, you'll need to set a few environment variables.

In development on your local machine, you can set these variables in a file named `.env` in the project's root directory (useful if you don't want to type them out each time you restart your shell). The `.env` file is listed in `.gitignore`, so it won't be accidentally committed. In production, you should just set configuration variables in your server environment without using a `.env` file.


For running in a **development** environment you only need the following 3 environment variables ([see below](#oauth-credentials) for how to get your Google OAuth credentials):

```bash
# Google OAuth credentials (see below for details)
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>

# Don't require https (without this, you can't easily test login functionality locally)
OAUTHLIB_INSECURE_TRANSPORT=true
```

In **production**, you'll need to set all 4 of these:

```bash
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
SECRET_KEY=<your_very_secure_secret_key>
DATABASE_URL=postgres://<your_postgres_url>
```

### OAuth credentials

To get Google OAuth credentials, you'll need to register a web application at <https://console.developers.google.com/>.

If you're registering an application for local development, choose "Internal" as your application type. This will allow you to set `localhost` addresses as authorized redirect URIs. For a non-`localhost` address (in production), you'll need to chose "Public" instead.

Google will ask you for some specific "**Authorized redirect URIs**" that Google can send users to after they authorize the app to access their Google account. Assuming your server will run at `localhost:8000`, enter each of these URIs in that section:

<!--
TODO Authorized JavaScript origins:

* http://localhost:8000
-->

* `http://localhost:8000/auth/google/`
* `http://localhost:8000/auth/google/authorized`

Once you've registered your application, Google will assign you a Client ID and a Client secret. Remember to set both of these as environment variables [as described above](#server-configuration).

<details>
<summary>Click for more detailed instructions</summary>

1. Visit https://console.developers.google.com/ and log in if needed.
2. Click on the drop-down menu at the top left, right next to "Google APIs".
3. Click on "NEW PROJECT" at the top right of the modal that pops up.
4. Optionally name the project, then click the "CREATE" button.
5. Check the text shown on the drop down menu next to "Google APIs" at the top left (the same one as step 2). If that text isn't the name of the project you just crated, click on it and select the correct project.
6. Click on "Credentials" in the left sidebar.
7. Click on "OAuth consent screen" in the top navigation bar of the main page section.
8. If you only need credentials for local development, select "Internal" in the **Application type** section. You can also enter an application name, perhaps something like "Instrument Catalog (dev)". Then, click on the "Save" button at the bottom of the page. This should take you back to the "Credentials" tab.
9. Click the "Create credentials" button in the main window and select "OAuth client ID".
10. Select "Web application".
11. In the **Authorized redirect URIs** section, enter all the URIs listed above (a new input field will appear after you've entered an address in one of them).
12. You will now be shown your client ID and client secret (you can come back to this page any time to find them again). Copy each of these and paste them into a file named `.env` that you create in the root directory of the Instrument Catalog repo, as described in the [Server configuration](#server-configuration) section.

</details>

Running the server
------------------

First, activate the Pipenv environment subshell:

```bash
$ pipenv shell
```

### Initialize/update the database

Instrument Catalog uses [Flask-Migrate][] to handle updates to the database schema. Flask-Migrate conveniently integrates itself into the `flask` command line interface. You will need to run the following Flask-Migrate command before your first time running the server in a new environment:

```bash
$ flask db upgrade
```

If you make a change to the database schema, you'll need to update Flask-Migrate's record of database schema changes by running `$ flask db migrate`. Be sure to commit the file generated by this command in `git` after you've done so.

Any time the schema has changed since the last time you ran the server (whether from running the `migrate` command or checking out a different commit), you'll need to update the database itself by running `$ flask db upgrade` again. Since there's no harm in running this command even when there *aren't* changes to be made, it may be simpler to run it whenever you [start the server](#start-the-server), for example:

```bash
$ flask db upgrade && flask run
```

### Start the server

You can use any of these options to start up the server (optionally preceded by `$ flask db upgrade` as described above):

```bash
# Start the server on port 8000 (ONLY FOR DEVELOPMENT)
$ flask run

# You can also specify a different port
$ flask run --port 5000


# To run more similarly to a production environment:

# If you to have the Heroku CLI installed, you can use this option
$ heroku local web

# Otherwise run this, which is exactly what you'd run in production
$ gunicorn instrument_catalog:app

# You can also specify a host and port, which may be needed when running
# locally to avoid other OS configuration steps (likely needed if you're
# running the server on a virtual machine).
$ gunicorn --bind 0.0.0.0:8000 instrument_catalog:app
```

Then, open up the app in your browser! http://localhost:8000

[API]: instrument_catalog/doc/api.md
[Flask-Migrate]: https://flask-migrate.readthedocs.io/en/latest/
[Python]: https://www.python.org/downloads.
[Pipenv]: https://pipenv.readthedocs.io/en/latest/
