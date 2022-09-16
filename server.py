from flask import Flask, render_template, request, make_response, redirect, url_for, Response, session, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_env import MetaFlaskEnv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datamodel import *
from authentication.form import LoginForm, CreateAccountForm


class Configuration(metaclass=MetaFlaskEnv):
    SECRET_KEY = "supersecretkey"
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://localhost:3306/fiver?user=root&password=root'
    POOL_SIZE = 1
    POOL_RECYCLE = 60

app = Flask(__name__)
try:
    app.config.from_pyfile('settings.cfg')

except FileNotFoundError:
    # Load environment variables - docker/kubernetes integration
    app.config.from_object(Configuration)

app.config['SESSION_COOKIE_SECURE']=True
csrf = CSRFProtect(app)
login = LoginManager(app)

mysql_string = app.config['SQLALCHEMY_DATABASE_URI']
engine = create_engine(mysql_string, pool_pre_ping=True, echo=False,
                       pool_size=app.config['POOL_SIZE'], pool_recycle=app.config['POOL_RECYCLE'])
sessionFactory = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

@login.user_loader
def user_loader(username):
    session = sessionFactory()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    if user.deleted is True:
        return None
    else:
        return user

@login.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    resp = make_response(render_template('logout.html'))
    session.clear()
    return resp

@app.route('/login', methods=['GET', 'POST'])
def login():
    loginform = LoginForm()
    sigupform = CreateAccountForm()
    session = sessionFactory()
    if loginform.validate_on_submit():
        user = session.query(User).filter_by(username=loginform.username.data).first()
        if user:
            if user.check_password(loginform.password.data) and user.deleted is False:
                user.set_authenticated(session, True)
                login_user(user)
                session.close()
                return redirect('https://google.com')
        session.close()
        flash("Incorrect username/password", "error")
        return render_template('error.html', message="Authentication error", redirect="/")
    session.close()
    return render_template("login.html", loginform=loginform, sigupform=sigupform)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    loginform = LoginForm()
    sigupform = CreateAccountForm()
    session = sessionFactory()
    try:
        if sigupform.validate_on_submit():
            if sigupform.password.data != sigupform.confirm.data:
                session.close()
                flash("Password not match", "error")
                return render_template('login.html', loginform=loginform, sigupform=sigupform)
            authentication = UserAuthentication(username=sigupform.username.data)
            authentication.change_password(sigupform.password.data)
            session.add(authentication)
            session.commit()

            user = User(userid=authentication.id, email=sigupform.email.data)
            session.add(user)
            session.commit()
            session.close()
            flash("Create user successful", "info")
            return redirect('https://google.com')
    except Exception as e:
        flash("Could not sign up for new user", "error")
        return render_template('login.html', loginform=loginform, sigupform=sigupform)

if __name__ == '__main__':
    app.run()
