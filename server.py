from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_env import MetaFlaskEnv
from werkzeug.utils import secure_filename

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.crud import *
from database.datamodel import *
from authentication.form import LoginForm, CreateAccountForm, AddUser, PaySlip, SubmitLeaveForm, LeaveForm
from datetime import datetime, timedelta
from functools import wraps

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
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['UPLOAD_FOLDER'] = app.config['TMP_PATH']
csrf = CSRFProtect(app)
login = LoginManager(app)

mysql_string = app.config['SQLALCHEMY_DATABASE_URI']
engine = create_engine(mysql_string, pool_pre_ping=True, echo=False,
                       pool_size=app.config['POOL_SIZE'], pool_recycle=app.config['POOL_RECYCLE'])
sessionFactory = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

s3 = boto3.client('s3',
                  aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                  aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
                  )

def last_day_of_month(any_day):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - timedelta(days=next_month.day)

@login.user_loader
def user_loader(username):
    session = sessionFactory()
    user = session.query(UserAuthentication).filter_by(username=username).first()
    session.close()
    if user.deleted is True:
        return None
    else:
        return user

def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('menu'))
        return func(*args, **kwargs)
    return wrapper

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
        session.rollback()
        session.close()
        flash("Could not sign up for new user", "error")
        return render_template('login.html', loginform=loginform, sigupform=sigupform)

@app.route("/editprofile", methods=['POST'])
@login_required
def editprofile():
    form = AddUser()
    session = sessionFactory()
    try:
        if 'edit' in request.args:
            u = get_user_by_id(session, request.args.get('edit'))
            profile = u['image']
            resume = u['resume']
            certificate = u['certificate']
            if form.phone.data == '':
                form.phone.data = None
            pr = request.files.get('edit_profile')
            if pr.filename != '':
                filename = secure_filename(pr.filename)
                pr.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                s3.upload_file(
                    Filename=app.config['TMP_PATH'] + '/' + filename,
                    Bucket=app.config['AWS_BUCKET'],
                    Key='profile-{}'.format(form.firstname.data),
                )
                profile = 'profile-{}'.format(form.firstname.data)
                os.remove(app.config['TMP_PATH'] + '/' + filename)
                # url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': app.config['AWS_BUCKET'],'Key': filename})

            re = request.files.get('edit_resume')
            if re.filename != '':
                filename = secure_filename(re.filename)
                re.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                s3.upload_file(
                    Filename=app.config['TMP_PATH'] + '/' + filename,
                    Bucket=app.config['AWS_BUCKET'],
                    Key='resume-{}'.format(form.firstname.data),
                )
                resume = 'resume-{}'.format(form.firstname.data)
                os.remove(app.config['TMP_PATH'] + '/' + filename)

            ce = request.files.get('edit_certificate')
            if ce.filename != '':
                filename = secure_filename(ce.filename)
                ce.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                s3.upload_file(
                    Filename=app.config['TMP_PATH'] + '/' + filename,
                    Bucket=app.config['AWS_BUCKET'],
                    Key='certificate-{}'.format(form.firstname.data),
                )
                certificate = 'certificate-{}'.format(form.firstname.data)
                os.remove(app.config['TMP_PATH'] + '/' + filename)
                # url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': app.config['AWS_BUCKET'],'Key': filename})
            user = session.query(User).filter(User.userid == request.args.get('edit')).update(
                {'firstname': form.firstname.data, 'lastname': form.lastname.data,
                 'age': form.age.data, 'phone': form.phone.data, 'image': profile, 'certificate': certificate, 'resume': resume, 'self_intro': request.form.get('self_intro'),
                 'email': form.email.data, 'jobtitle': form.position.data, 'primaryskills': form.skills.data, 'department': form.department.data, 'location': form.location.data})
            session.commit()
            session.query(Payroll).filter(Payroll.userid==request.args.get('edit')).update({'firstname': form.firstname.data, 'lastname': form.lastname.data})
            session.commit()
            session.close()
            flash('Updated user information successful', "info")
            return redirect(url_for('employee'))
        else:
            flash('Bad request', "error")
            return redirect(url_for('employee'))
    except Exception as e:
        session.rollback()
        session.close()
        flash("Exception occurred - Cannot edit user", "error")
        return redirect(url_for('employee'))


@app.route("/employee", methods=['GET', 'POST'])
@login_required
@admin_only
def employee():
    url = '/static/images/default.jpg'
    form = AddUser()
    session = sessionFactory()
    if current_user.is_admin is False:
        uInfo = get_user_by_id(session, current_user.id)
        if uInfo['image'] is not None:
            url = s3.generate_presigned_url(ClientMethod='get_object',
                                        Params={'Bucket': app.config['AWS_BUCKET'], 'Key': uInfo['image']})
    try:
        users = get_all_user(session)
        if request.method == 'POST':
            profile = None
            resume = None
            certificate = None
            password = form.password.data
            confirm =form.confirm.data
            if password != confirm:
                session.close()
                flash("Password not match", "error")
                return render_template('employee.html', users=users, username=current_user.username, form=form, profile=url)

            authentication = UserAuthentication(username=form.username.data)
            if form.phone.data == '':
                form.phone.data = None
            pr = request.files.get('profile')
            if pr.filename != '':
                filename = secure_filename(pr.filename)
                pr.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                s3.upload_file(
                    Filename=app.config['TMP_PATH'] + '/' + filename,
                    Bucket=app.config['AWS_BUCKET'],
                    Key='profile-{}'.format(form.username.data),
                )
                profile = 'profile-{}'.format(form.username.data)
                os.remove(app.config['TMP_PATH'] + '/' + filename)
                # url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': app.config['AWS_BUCKET'],'Key': filename})

            re = request.files.get('resume')
            if re.filename != '':
                filename = secure_filename(re.filename)
                re.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                s3.upload_file(
                    Filename=app.config['TMP_PATH'] + '/' + filename,
                    Bucket=app.config['AWS_BUCKET'],
                    Key='resume-{}'.format(form.username.data),
                )
                resume = 'resume-{}'.format(form.username.data)
                os.remove(app.config['TMP_PATH'] + '/' + filename)

            ce = request.files.get('certificate')
            if ce.filename != '':
                filename = secure_filename(ce.filename)
                ce.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                s3.upload_file(
                    Filename=app.config['TMP_PATH'] + '/' + filename,
                    Bucket=app.config['AWS_BUCKET'],
                    Key='certificate-{}'.format(form.username.data),
                )
                certificate = 'certificate-{}'.format(form.username.data)
                os.remove(app.config['TMP_PATH'] + '/' + filename)

            user = User(email=form.email.data, firstname=form.firstname.data, image=profile, certificate=certificate, resume=resume, self_intro=request.form.get('self_intro'),
                        lastname=form.lastname.data, age=form.age.data, phone=form.phone.data,
                        jobtitle=form.position.data,
                        department=form.department.data, location=form.location.data, primaryskills=form.skills.data)


            payroll = Payroll(firstname=user.firstname, lastname=user.lastname)

            authentication.change_password(form.password.data)
            session.add(authentication)
            session.commit()

            user.userid = authentication.id
            session.add(user)
            session.commit()

            payroll.userid = authentication.id
            session.add(payroll)
            session.commit()

            session.close()
            flash("Adding user successful", "info")
            return redirect(url_for('employee'))
        for user in users:

            if user['certificate'] is not None and user['certificate'] != '':
                user['certificate'] = s3.generate_presigned_url(ClientMethod='get_object',
                                                          Params={'Bucket': app.config['AWS_BUCKET'],
                                                                  'Key': user['certificate']})
            else:
                user['certificate'] = 'None'

            if user['resume'] is not None and user['resume'] !='':
                user['resume'] = s3.generate_presigned_url(ClientMethod='get_object',
                                                          Params={'Bucket': app.config['AWS_BUCKET'],
                                                                  'Key': user['resume']})
            else:
                user['resume'] = 'None'
        session.close()
        return render_template('employee.html', admin=current_user.is_admin, users=users, username=current_user.username, form=form, profile=url)
    except Exception as e:
        session.rollback()
        session.close()
        flash("Exception occurred - Cannot add new user", "error")
        return redirect(url_for('employee'))


@app.route("/payroll", methods=["GET", "POST"])
@login_required
def payroll():
    url = '/static/images/default.jpg'
    session = sessionFactory()
    if current_user.is_admin is False:
        uInfo = get_user_by_id(session, current_user.id)
        if uInfo['image'] is not None:
            url = s3.generate_presigned_url(ClientMethod='get_object',
                                        Params={'Bucket': app.config['AWS_BUCKET'], 'Key': uInfo['image']})
    form = PaySlip()
    try:
        if request.method == 'POST':
            if 'edit' in request.args:
                # date = request.form.get('date')
                # datedb = datetime.strptime(date, '%Y-%m-%d')
                salary = 0
                overtime = 0
                payrate = 0
                if 'salary' in request.form:
                    if request.form.get('salary') != '':
                        salary = round(float(request.form.get('salary')), 2)
                if 'overtime' in request.form:
                    if request.form.get('overtime') != '':
                        overtime = round(float(request.form.get('overtime')), 2)
                tax = float(salary*0.12)
                deduction = float((salary)/21)
                session.query(Payroll).filter(Payroll.id==request.args.get('edit')).update({'basicSalary': salary, 'tax': round(tax, 2),
                                                                                                      'deduction': round(deduction, 2), 'overTime': overtime,
                                                                                                      'totalPayRate': round(salary-(tax + deduction)), 'payDate': last_day_of_month(datetime.now())})

                session.commit()
                session.close()
                flash('Edited successful', "info")
            else:
                flash('Could not edit pay slip', 'info')
                return redirect(url_for('payroll'))
        if current_user.is_admin:
            payrolls = get_user_payroll(session)
        else:
            payrolls = get_payroll_by_user(session, current_user.id)
        for pay in payrolls:
            if pay['basicSalary'] is not None:
                pay['payDate'] = last_day_of_month(datetime.now())
                session.query(Payroll).filter(Payroll.id==pay['id']).update({'payDate': last_day_of_month(datetime.now())})
        session.commit()
        session.close()
        return render_template('payroll.html', admin=current_user.is_admin,  payrolls=payrolls, form=form, profile=url)
    except Exception as e:
        session.rollback()
        session.close()
        return redirect(url_for('menu'))

@app.route('/submitform', methods=['POST'])
def submitform():
    now = datetime.now()
    session = sessionFactory()
    try:
        submitform = SubmitLeaveForm()
        sdate = request.form.get('sdate')
        sdatedb = datetime.strptime(sdate, '%Y-%m-%d')
        edate = request.form.get('edate')
        edatedb = datetime.strptime(edate, '%Y-%m-%d')
        leavetype = submitform.type.data
        description = submitform.description.data
        userInfo = get_user_by_id(session, current_user.id)
        leaveform = Leave(userid=current_user.id, firstname=userInfo['firstname'], lastname=userInfo['lastname'],
                          leavetype=leavetype, description=description, startDate=sdatedb, endDate=edatedb, status='pending')
        session.add(leaveform)
        session.commit()

        if leavetype == 'Annual Leave' or leavetype == 'Sick Leave':
            try:
                getDays = get_day_leave_left(session, current_user.id, now.strftime("%Y"))
                # session.query(TotalAnnualLeave).filter(TotalAnnualLeave.userid == current_user.id).update(
                #     {'days': getDays + 1, 'year': now.strftime("%Y")})
            except:
                annualLeave = TotalAnnualLeave(userid=current_user.id, days=0, year=now.strftime("%Y"))
                session.add(annualLeave)

            session.commit()

        session.close()
        flash('Added leave form successful', 'info')
        return redirect(url_for('leave'))
    except Exception as e:
        session.rollback()
        session.close()
        flash('Could not add leave form', 'error')
        return redirect(url_for('leave'))


@app.route("/leave", methods=['GET'])
@login_required
def leave():
    url = '/static/images/default.jpg'
    session = sessionFactory()
    uInfo = get_user_by_id(session, current_user.id)
    if uInfo['image'] is not None:
        url = s3.generate_presigned_url(ClientMethod='get_object',
                                        Params={'Bucket': app.config['AWS_BUCKET'], 'Key': uInfo['image']})
    try:
        if current_user.is_admin is False:
            submitform = SubmitLeaveForm()
            history = get_leave_form_history_by_user(session, current_user.id)
            return render_template('leave.html', form=submitform, records=history, profile=url)
        else:
            return redirect(url_for('leaves'))
    except Exception as e:
        session.rollback()
        session.close()
        flash('Could not retrieve page', 'error')
        return redirect(url_for('menu'))

@app.route("/leaves", methods=['GET', 'POST'])
@login_required
@admin_only
def leaves():
    url = '/static/images/default.jpg'
    now = datetime.now()
    form = LeaveForm()
    session = sessionFactory()
    if current_user.is_admin is False:
        uInfo = get_user_by_id(session, current_user.id)
        if uInfo['image'] is not None:
            url = s3.generate_presigned_url(ClientMethod='get_object',
                                            Params={'Bucket': app.config['AWS_BUCKET'], 'Key': uInfo['image']})
    if request.method == 'POST':
        try:
            leaveid = request.form.get('leaveid')
            status = form.status.data
            if request.form.get('status') == 'approve':
                getDays = get_day_leave_left(session, request.form.get('leaveuserid'), now.strftime("%Y"))
                session.query(TotalAnnualLeave).filter(TotalAnnualLeave.userid == request.form.get('leaveuserid')).update(
                    {'days': getDays + 1, 'year': now.strftime("%Y")})
            session.query(Leave).filter(Leave.id==leaveid).update({'status': request.form.get('status')})
            session.commit()
            session.close()
            flash('Updated form successful', "info")
        except Exception as e:
            session.rollback()
            session.close()
            flash('Could not update form', 'error')
        return redirect(url_for('leaves'))
    all_leaves = get_user_leave(session)
    session.close()
    return render_template('leaves.html', admin=current_user.is_admin, form=form, leaves=all_leaves, profile=url, options=['pending', 'approve','decline'])


@app.route("/menu", methods=["GET", "POST"])
@login_required
def menu():
    profile = '/static/images/default.jpg'
    session = sessionFactory()
    if current_user.is_admin is False:
        uInfo = get_user_by_id(session, current_user.id)
        if uInfo['image'] is not None:
            profile = s3.generate_presigned_url(ClientMethod='get_object',
                                        Params={'Bucket': app.config['AWS_BUCKET'], 'Key': uInfo['image']})
        else:
            profile = '/static/images/default.jpg'
    users = get_all_user(session)
    for user in users:

        if user['image'] is not None:
            user['image'] = s3.generate_presigned_url(ClientMethod='get_object',
                                        Params={'Bucket': app.config['AWS_BUCKET'], 'Key': user['image']})
        else:
            user['image'] = '/static/images/default.jpg'

    admin = current_user.is_admin
    userType = 'User'
    if admin is True:
        userType = 'Administrator'
    session.close()
    return render_template('dashboard.html', admin=current_user.is_admin, user=current_user.username, userType=userType, profile=profile, users=users)

@app.route("/statistics", methods=["GET"])
@login_required
def statistics():
    now = datetime.now()
    totalPayroll = 0
    profile = '/static/images/default.jpg'
    session = sessionFactory()
    if current_user.is_admin is False:
        uInfo = get_user_by_id(session, current_user.id)
        if uInfo['image'] is not None:
            profile = s3.generate_presigned_url(ClientMethod='get_object',
                                                Params={'Bucket': app.config['AWS_BUCKET'], 'Key': uInfo['image']})
        else:
            profile = '/static/images/default.jpg'
    users = get_all_user(session)
    payrolls = get_user_payroll(session)
    for pay in payrolls:
        totalPayroll = totalPayroll + pay['basicSalary']
    totalAnnualleaves = len(users)*14
    leaveTaken = get_all_leave(session, now.strftime("%Y"))
    try:
        annualLeaves = round((leaveTaken/totalAnnualleaves)*100, 2)
    except:
        annualLeaves = 0
    return render_template('statistic.html', admin=current_user.is_admin, totalPayroll=totalPayroll, annualLeaves=annualLeaves,   profile=profile, users=len(users))


@app.route("/payrollStatistic", methods=['GET'])
@login_required
def payrollStatistic():
    json_ret = []
    session = sessionFactory()
    payrolls = get_user_payroll(session)
    for pay in payrolls:
        json_ret.append({'firstname': pay['firstname'], 'payroll': pay['basicSalary']})
    session.close()
    return jsonify(json_ret)

@app.route("/annualLeaveStatistic", methods=['GET'])
@login_required
def annualLeaveStatistic():
    now = datetime.now()
    json_ret = []
    session = sessionFactory()
    users = get_all_user(session)
    for user in users:
        try:
            dayUsed = get_day_leave_left(session, user['id'], now.strftime("%Y"))
            if dayUsed>=14:
                dayUsed=14
        except:
            dayUsed = 0
        json_ret.append({'dayused': dayUsed, 'firstname': user['firstname']})
    session.close()
    return jsonify(json_ret)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('menu'))

if __name__ == '__main__':
    app.run()
