import json
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_required, login_user, UserMixin, logout_user
from tefnut.utils.setting import settings
import tefnut.control.control as control


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
app.secret_key = 'super secret key'

persist = True

sha = ""
version = ""


@app.context_processor
def inject_git_info():
    return dict(sha=sha[0:6], version=version)


@login_manager.user_loader
def load_user(user_id):
    return User()


@app.route("/version")
def version():
    out = {
                "version": version,
                "sha": sha
            }
    return out


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
    if request.get_data().decode("utf-8") == "":
        app.logger.debug("Updating webUI with no incoming data")
        return control.state

    try:
        new_data = json.loads(request.get_data())
    except Exception as e:
        app.logger.error(request.get_data())
        app.logger.error("Error opening json", exc_info=e)
        return control.state

    if "mode" in new_data:
        if new_data["mode"] not in ["AUTO", "MANUAL", "OFF"]:
            app.logger.error("Error incoming data, mode invalid: %s", new_data["mode"])
            return control.state

        app.logger.info("Chaning Humidifier mode: %s", new_data["mode"])
        settings.set("GENERAL.mode", new_data["mode"], persist=persist)
        control.humidifier_controller()
        return control.state

    if "manual_target" in new_data:
        if not type(new_data["manual_target"]) == int:
            app.logger.error("Error incoming data, manual_target invalid: %s", new_data["manual_target"])
            return control.state

        if new_data["manual_target"] < 10 or new_data["manual_target"] > 50:
            app.logger.error("Error incoming data, manual_target is out of range: %s", new_data["manual_target"])
            return control.state

        app.logger.info("Chaning Humidifier manual_target: %d", new_data["manual_target"])
        settings.set("GENERAL.manual_target", new_data["manual_target"], persist=persist)
        control.humidifier_controller()
        return control.state

    app.logger.error("Error incoming data, invalid data: %s", new_data)
    return control.state


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


@login_manager.request_loader
def load_user_from_header(request):
    auth = request.authorization
    if not auth:
        return None

    username = auth.username
    password = auth.password
    user = User()

    if username == settings.get("WEBUI.username") and password == settings.get("WEBUI.password"):
        app.logger.info("User Logging in from HTTP AUTH")
        return user

    app.logger.info("User FAILED Logging from HTTP AUTH")
    abort(401)


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
    app.logger.info("404 - Wrong URL", exc_info=e)
    return render_template('error.html', title="Invalid page", subtitle="take me home, west virginia"), 404


class User(UserMixin):
    """
    Dummy User class for the Login,
    Nothing crazy here, there is only 1 user that we get from config files
    """
    id = "secretID"
