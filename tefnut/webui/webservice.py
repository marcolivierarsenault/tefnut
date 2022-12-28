import atexit
import json
import logging

import git
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_apscheduler import APScheduler
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

import tefnut.control.control as control
from tefnut.utils.logging import configure_logger
from tefnut.utils.setting import settings

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
app.secret_key = "super secret key"

scheduler = APScheduler()

persist = True
BACKGROUND_THREAD_TIMER = 10

sha = ""
version = ""

tefnut_controller = None


def close_tefnut():
    app.logger.info("Stopping tefnut")
    tefnut_controller.goodbye()


def load_application():
    global tefnut_controller

    scheduler.init_app(app)
    scheduler.start()

    atexit.register(close_tefnut)

    configure_logger(logging.getLogger("main"))
    configure_logger(app.logger)
    app.logger.info("Application loaded")

    f = open("VERSION")
    version = f.read()
    f.close()
    app.logger.info("Tefnut version: %s", version)

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    app.logger.info("Starting code on git sha: %s", sha)

    tefnut_controller = control.TefnutController()


@scheduler.task(
    "interval",
    id="tefnut_update",
    seconds=BACKGROUND_THREAD_TIMER,
    misfire_grace_time=900,
)
def background_job():
    app.logger.info("Starting tefnut update")
    tefnut_controller.controler_loop()
    app.logger.debug("finished tefnut update")


@app.context_processor
def inject_git_info():
    return dict(sha=sha[0:6], version=version)


@login_manager.user_loader
def load_user(user_id):
    return User()


@app.route("/version")
@login_required
def version():
    out = {"version": version, "sha": sha}
    return out


@app.route("/")
@login_required
def index():
    app.logger.info("Accessing main page")
    return render_template("index.html")


@app.route("/login")
def login():
    app.logger.info("Accessing Login page")
    return render_template("login.html")


@app.route("/state", methods=["POST"])
@login_required
def get_state():
    if request.get_data().decode("utf-8") == "":
        app.logger.debug("Updating webUI with no incoming data")
        return tefnut_controller.state

    try:
        new_data = json.loads(request.get_data())
    except Exception as e:
        app.logger.error(request.get_data())
        app.logger.error("Error opening json", exc_info=e)
        return tefnut_controller.state

    if "mode" in new_data:
        if new_data["mode"] not in ["AUTO", "MANUAL", "OFF"]:
            app.logger.error("Error incoming data, mode invalid: %s", new_data["mode"])
            return tefnut_controller.state

        app.logger.info("Chaning Humidifier mode: %s", new_data["mode"])
        settings.set("GENERAL.mode", new_data["mode"], persist=persist)
        tefnut_controller.humidifier_controller()
        return tefnut_controller.state

    if "manual_target" in new_data:
        if not type(new_data["manual_target"]) == int:
            app.logger.error(
                "Error incoming data, manual_target invalid: %s",
                new_data["manual_target"],
            )
            return tefnut_controller.state

        if new_data["manual_target"] < 10 or new_data["manual_target"] > 50:
            app.logger.error(
                "Error incoming data, manual_target is out of range: %s",
                new_data["manual_target"],
            )
            return tefnut_controller.state

        app.logger.info(
            "Chaning Humidifier manual_target: %d", new_data["manual_target"]
        )
        settings.set(
            "GENERAL.manual_target", new_data["manual_target"], persist=persist
        )
        tefnut_controller.humidifier_controller()
        return tefnut_controller.state

    if "auto_delta" in new_data:
        if not type(new_data["auto_delta"]) == int:
            app.logger.error(
                "Error incoming data, auto_delta invalid: %s", new_data["auto_delta"]
            )
            return tefnut_controller.state

        if new_data["auto_delta"] < -20 or new_data["auto_delta"] > 20:
            app.logger.error(
                "Error incoming data, auto_delta is out of range: %s",
                new_data["auto_delta"],
            )
            return tefnut_controller.state

        app.logger.info("Chaning Humidifier auto_delta: %d", new_data["auto_delta"])
        settings.set("GENERAL.auto_delta", new_data["auto_delta"], persist=persist)
        tefnut_controller.humidifier_controller()
        return tefnut_controller.state

    app.logger.error("Error incoming data, invalid data: %s", new_data)
    return tefnut_controller.state


@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User()

    if username == settings.get("WEBUI.username") and password == settings.get(
        "WEBUI.password"
    ):
        app.logger.info("User Logging in")
        login_user(user, remember=True)
        return redirect(url_for("index"))

    app.logger.info("User FAILED Logging to loggin")
    flash("Please check your login details and try again.")
    return redirect(url_for("login"))


@login_manager.request_loader
def load_user_from_header(request):
    auth = request.authorization
    if not auth:
        return None

    username = auth.username
    password = auth.password
    user = User()

    if username == settings.get("WEBUI.username") and password == settings.get(
        "WEBUI.password"
    ):
        app.logger.info("User Logging in from HTTP AUTH")
        return user

    app.logger.info("User FAILED Logging from HTTP AUTH")


@app.route("/logout")
@login_required
def logout():
    app.logger.info("User Logging out")
    logout_user()
    return redirect(url_for("login"))


@app.errorhandler(Exception)
@app.errorhandler(500)
def handle_exception(e):
    app.logger.error("WebUI ERROR", exc_info=e)
    return (
        render_template("error.html", title="Server Error", subtitle="check logs"),
        500,
    )


@app.errorhandler(404)
def page_not_found(e):
    app.logger.info(f"404 - Wrong URL {e}")
    return (
        render_template(
            "error.html", title="Invalid page", subtitle="take me home, west virginia"
        ),
        404,
    )


class User(UserMixin):
    """
    Dummy User class for the Login,
    Nothing crazy here, there is only 1 user that we get from config files
    """

    id = "secretID"
