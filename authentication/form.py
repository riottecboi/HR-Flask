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

class AddUser(FlaskForm):
    firstname = StringField('Firstname', id='firstname')
    lastname = StringField('Lastname', id='lastname')
    age = IntegerField('Age', id='age')
    phone = StringField('Phone', id='phone')
    email = EmailField('Email',
                       id='email',
                       validators=[DataRequired(), Email()])
    position = StringField('Position', id='position')
    department = StringField('Department', id='department')
    location = StringField('Location', id='location')
    skills = StringField('Skills', id='skill')
    username = StringField('Username',
                         id='username',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='password',
                             validators=[DataRequired()])
    confirm = PasswordField('Confirm Password',
                            id='confirm',
                            validators=[DataRequired()])

class PaySlip(FlaskForm):
    salary = FloatField('Basic salary', id='salary')
    tax = FloatField('Tax', id='tax')
    deduction = FloatField('Deduction', id='deduction')
    overtime = FloatField('Overtime', id='overtime')
    payrate = FloatField('Pay rate', id='payrate')

class SubmitLeaveForm(FlaskForm):
    type = SelectField('Leave Type', id='types', choices=[('Annual Leave', 'Annual Leave'), ('Emergency Leave', 'Emergency Leave'),
                                                          ('Sick Leave', 'Sick Leave'), ('Maternity Leave', 'Maternity Leave')])
    description = StringField('Description', id='description', widget=TextArea())


class LeaveForm(FlaskForm):
    firstname = StringField('Firstname', id='firstname')
    lastname = StringField('Lastname', id='lastname')
    description = StringField('Description', id='description')
    startdate = StringField('Start Date', id='sdate')
    enddate = StringField('End Date', id='edate')
    status = SelectField('Status', id='status', choices=[('pending', 'Pending'), ('approve', 'Approve'), ('decline', 'Decline')])
