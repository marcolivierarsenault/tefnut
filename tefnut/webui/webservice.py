from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, UserMixin, logout_user
from tefnut.utils.setting import settings


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
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User()

    if username == settings.get("WEBUI.username") and password == settings.get("WEBUI.password"):
        login_user(user, remember=True)
        return redirect(url_for('index'))

    flash('Please check your login details and try again.')
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


class User(UserMixin):
    id = "secretID"
