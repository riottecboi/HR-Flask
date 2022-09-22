from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, EmailField, IntegerField, SelectField, FloatField, TextAreaField
from wtforms.validators import Email, DataRequired
from wtforms.widgets import TextArea

# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])
class PasswordAuth(FlaskForm):
    username = StringField('Username',
                           id='username',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             id='password',
                             validators=[DataRequired()])
    confirm = PasswordField('Confirm Password',
                            id='confirm',
                            validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = EmailField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    confirm = PasswordField('Confirm Password',
                             id='pwd_confirm',
                             validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])

class AddUser(PasswordAuth):
    firstname = StringField('Firstname', id='firstname')
    lastname = StringField('Lastname', id='lastname')
    self_intro = StringField('Self Information', id='selfinfo', widget=TextArea())
    age = IntegerField('Age', id='age')
    phone = StringField('Phone', id='phone')
    email = EmailField('Email',
                       id='email',
                       validators=[DataRequired(), Email()])
    position = StringField('Position', id='position')
    department = StringField('Department', id='department')
    location = StringField('Location', id='location')
    skills = StringField('Skills', id='skill')
    annualleave = IntegerField('Annual Leave', id='annualleave', default=0)
    sickleave = IntegerField('Sick Leave', id='sickleave', default=0)

class EditUser(FlaskForm):
    editfirstname = StringField('Firstname', id='firstname', description="First Name")
    editlastname = StringField('Lastname', id='lastname')
    editself_intro = StringField('Self Information', id='selfinfo', widget=TextArea())
    editage = IntegerField('Age', id='age')
    editphone = StringField('Phone', id='phone')
    editemail = EmailField('Email',
                       id='email',
                       validators=[DataRequired(), Email()])
    editposition = StringField('Position', id='position')
    editdepartment = StringField('Department', id='department')
    editlocation = StringField('Location', id='location')
    editskills = StringField('Skills', id='skill')
    editannualleave = IntegerField('Annual Leave', id='annualleave', default=0)
    editsickleave = IntegerField('Sick Leave', id='sickleave', default=0)


class PaySlip(FlaskForm):
    salary = FloatField('Basic salary', id='salary')
    tax = FloatField('Tax', id='tax')
    deduction = FloatField('Deduction', id='deduction')
    overtime = FloatField('Overtime', id='overtime')
    payrate = FloatField('Pay rate', id='payrate')

class SubmitLeaveForm(FlaskForm):
    type = SelectField('Leave Type', id='types', choices=[('Annual Leave', 'Annual Leave'),
                                                          ('Sick Leave', 'Sick Leave'),  ('Unpaid Leave', 'Unpaid Leave')])
    description = StringField('Description', id='description', widget=TextArea())


class LeaveForm(FlaskForm):
    firstname = StringField('Firstname', id='firstname')
    lastname = StringField('Lastname', id='lastname')
    description = StringField('Description', id='description')
    startdate = StringField('Start Date', id='sdate')
    enddate = StringField('End Date', id='edate')
    status = SelectField('Status', id='status', choices=[('pending', 'Pending'), ('approve', 'Approve'), ('decline', 'Decline')])
