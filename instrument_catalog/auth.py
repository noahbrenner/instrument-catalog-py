"""
instrument_catalog.auth
~~~~~~~~~~~~~~~~~~~~~~~

Defines routes for logging in and out using OAuth.
"""
from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, session, url_for)
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.contrib.google import make_google_blueprint, google
from .models import db, User


bp = Blueprint('auth', __name__)


google_bp = make_google_blueprint(
    scope='https://www.googleapis.com/auth/userinfo.profile'
)


@oauth_error.connect
def login_failed(*args, **kwargs):
    flash('You did not log in. Please try again.')
    return redirect(url_for('auth.login'))


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

            db.session.add(user)
            db.session.commit()

    session['user'] = user.id
    flash('Successfully logged in with {oauth_provider}!'
          .format(oauth_provider=user.oauth_provider.capitalize()))

    return redirect(url_for('my_instruments'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Display the login page."""
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        if current_app.env == 'development':
            # Log in as the first user in the database (only for development)
            session['user'] = User.query.order_by(User.id).first().id
            return redirect(url_for('index'))
        else:
            # This route only accepts POST requests while in development
            return abort(501)  # Not Implemented


@bp.route('/logout')
def logout():
    """Log the user out and redirect to the home page."""
    if hasattr(g, 'user'):
        del g.user
    return redirect(url_for('index'))
