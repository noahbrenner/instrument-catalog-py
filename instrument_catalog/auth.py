"""
instrument_catalog.auth
~~~~~~~~~~~~~~~~~~~~~~~

Defines routes for logging in and out using OAuth.
"""
from flask import (Blueprint, Markup, abort, current_app, flash, redirect,
                   render_template, request, session, url_for)
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from .models import db, User


bp = Blueprint('auth', __name__)

google_bp = make_google_blueprint(
    scope='https://www.googleapis.com/auth/userinfo.profile'
)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'You need to log in to access that page.'
login_manager.refresh_view
login_manager.session_protection = 'strong'


# flask-login functions

@login_manager.user_loader
def load_user_from_cookie(user_id):
    """Return a user object (or None) from a Unicode user ID."""
    return User.query.get(int(user_id))


@login_manager.request_loader
def load_user_from_header(request):
    """Return a user object (or None) from an API key."""
    auth_header = request.headers.get('Authorization')

    if auth_header and auth_header.startswith('Bearer '):
        api_key = auth_header[len('Bearer '):]
        user_id = User.verify_api_key(api_key)

        if user_id is not None:
            return User.query.get(user_id)

    return None


@login_manager.unauthorized_handler
def require_login():
    """Handle unauthorized page requests.

    This function overrides flask-login's default behavior in order to
    avoid including a `next` query string parameter, since we haven't
    yet implemented safe validation of redirect URLs.
    """
    flash(login_manager.login_message)
    return redirect(url_for('auth.login')), 302  # Found


# flask-dance functions

@oauth_error.connect
def login_failed(*args, **kwargs):
    flash('You did not log in. Please try again.')
    return redirect(url_for('auth.login')), 302  # Found


@oauth_authorized.connect
def login_completed(blueprint, token):
    if blueprint.name == 'google':
        user_data = google.get('/oauth2/v2/userinfo').json()
        # => locale, given_name, link, id, name, family_name, picture, gender

        user = User.query.filter_by(
            oauth_provider=blueprint.name,
            provider_user_id=user_data.get('id')
        ).one_or_none()

        if user is None:
            user = User(name=user_data.get('given_name'),
                        oauth_provider=blueprint.name,
                        provider_user_id=user_data.get('id'))

        user.access_token = token.get('access_token')
        db.session.add(user)
        db.session.commit()

    remember = current_app.env != 'development'  # Only use a cookie in prod
    login_user(user, remember=remember)
    flash('Successfully logged in with {oauth_provider}!'
          .format(oauth_provider=user.oauth_provider.capitalize()))

    return redirect(url_for('my_instruments')), 303  # See Other


# Routes

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Display the login page."""
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        if current_app.env == 'development':
            # Log in as the first user in the database (only for development)
            login_user(User.query.order_by(User.id).first())
            flash('Successfully logged in as dev mode user.')
            return redirect(url_for('my_instruments')), 303  # See Other
        else:
            # This route only accepts POST requests while in development
            return abort(501)  # Not Implemented


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Log the user out and redirect to the home page."""
    # Revoke our access to the user's Google account
    oauth_logout = google.post(
        'https://accounts.google.com/o/oauth2/revoke',
        params={'token': current_user.access_token},
        headers={'Content-Type': 'application/x-www-form-urlencoded'})

    # Remove the user's OAuth access token from our database
    current_user.access_token = None
    db.session.add(current_user)
    db.session.commit()

    # Log out the user in our server environment
    logout_user()

    if oauth_logout.ok:
        flash('You have successfully logged out!')
    else:
        flash(Markup(  # Use Markup() so that the link is rendered correctly
            'You are successfully logged out of Instrument Catalog, but we may'
            ' not have been able to revoke our access to your Google account.'
            ' You can manually revoke our access yourself at'
            ' <a href="https://myaccount.google.com/permissions">'
            'https://myaccount.google.com/permissions</a>.'))

    return redirect(url_for('index')), 303  # See Other
