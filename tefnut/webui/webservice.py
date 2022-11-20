from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, UserMixin, logout_user
from tefnut.utils.setting import settings
from tefnut.control.control import state


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
app.secret_key = 'super secret key'


@login_manager.user_loader
def load_user(user_id):
    return User()


@app.route("/")
@login_required
def index():
    app.logger.info("Accessing main page")
    return render_template('index.html')


@app.route('/login')
def login():
    app.logger.info("Accessing Login page")
    return render_template('login.html')


@app.route('/state', methods=['POST'])
@login_required
def get_state():
    return state


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User()

    if username == settings.get("WEBUI.username") and password == settings.get("WEBUI.password"):
        app.logger.info("User Logging in")
        login_user(user, remember=True)
        return redirect(url_for('index'))

    app.logger.info("User FAILED Logging to loggin")
    flash('Please check your login details and try again.')
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    app.logger.info("User Logging out")
    logout_user()
    return redirect(url_for('login'))


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error("WebUI ERROR", exc_info=e)
    return render_template('error.html', title="Server Error", subtitle="check logs"), 500


@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning("404 - Wrong URL", exc_info=e)
    return render_template('error.html', title="Invalid page", subtitle="take me home, west virginia"), 404


class User(UserMixin):
    """
    Dummy User class for the Login,
    Nothing crazy here, there is only 1 user that we get from config files
    """
    id = "secretID"
