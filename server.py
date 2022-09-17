from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_env import MetaFlaskEnv
from werkzeug.utils import secure_filename

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.crud import *
from database.datamodel import *
from authentication.form import LoginForm, CreateAccountForm, AddUser

import boto3
import os

class Configuration(metaclass=MetaFlaskEnv):
    SECRET_KEY = "supersecretkey"
    AWS_BUCKET = 'hr-fiver-test'
    AWS_ACCESS_KEY_ID = 'XXXX'
    AWS_SECRET_ACCESS_KEY = 'XXXX'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://localhost:3306/fiver?user=root&password=root'
    POOL_SIZE = 1
    POOL_RECYCLE = 60
    TMP_PATH = '/tmp'

app = Flask(__name__)
try:
    app.config.from_pyfile('settings.cfg')

except FileNotFoundError:
    # Load environment variables - docker/kubernetes integration
    app.config.from_object(Configuration)

app.config['SESSION_COOKIE_SECURE']=True
app.config['UPLOAD_FOLDER'] = app.config['TMP_PATH']
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
    user = session.query(UserAuthentication).filter_by(username=username).first()
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    loginform = LoginForm()
    sigupform = CreateAccountForm()
    session = sessionFactory()
    if loginform.validate_on_submit():
        user = session.query(UserAuthentication).filter_by(username=loginform.username.data).first()
        if user:
            if user.check_password(loginform.password.data) and user.deleted is False:
                user.set_authenticated(session, True)
                login_user(user)
                session.close()
                return redirect(url_for('menu'))
        session.close()
        flash("Incorrect username/password", "error")
        return render_template('login.html', loginform=loginform, sigupform=sigupform)
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
            return redirect(url_for('menu'))
    except Exception as e:
        flash("Could not sign up for new user", "error")
        return render_template('login.html', loginform=loginform, sigupform=sigupform)

@app.route("/employee", methods=['GET', 'POST'])
@login_required
def employee():
    form = AddUser()
    session = sessionFactory()
    try:
        users = get_all_user(session)
        if request.method == 'POST':
            filename = None
            s3 = boto3.client('s3',
                              aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                              aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
                              )
            password = form.password.data
            confirm =form.confirm.data
            if password != confirm:
                session.close()
                flash("Password not match", "error")
                return render_template('employee.html', users=users, username=current_user.username, form=form)

            authentication = UserAuthentication(username=form.username.data)
            if form.phone.data == '':
                form.phone.data = None

            file = request.files.get('profile')
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                s3.upload_file(
                    Filename=app.config['TMP_PATH']+'/'+filename,
                    Bucket=app.config['AWS_BUCKET'],
                    Key=filename,
                )
                # url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': app.config['AWS_BUCKET'],'Key': filename})

            user = User(userid=authentication.id, email=form.email.data, firstname=form.firstname.data, image=filename,
                        lastname=form.lastname.data, age=form.age.data, phone=form.phone.data, jobtitle=form.position.data,
                        department=form.department.data, location=form.location.data, primaryskills=form.skills.data)
            session.add(user)
            session.commit()

            authentication.change_password(form.password.data)
            session.add(authentication)
            session.commit()

            session.close()
            flash("Adding user successful", "info")
            return redirect(url_for('employee'))
        session.close()
        return render_template('employee.html', users=users, username=current_user.username, form=form)
    except Exception as e:
        session.close()
        flash("Exception occurred - Cannot add new user", "error")
        return redirect(url_for('employee'))


@app.route("/menu", methods=["GET", "POST"])
@login_required
def menu():
    admin = current_user.is_admin
    userType = 'User'
    if admin is True:
        userType = 'Administrator'
    return render_template('dashboard.html', user=current_user.username, userType=userType)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('menu'))

if __name__ == '__main__':
    app.run()
