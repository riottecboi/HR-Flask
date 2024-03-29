from database.datamodel import *
from datetime import datetime
def user_is_admin(session, userid):
    user = session.query(UserAuthentication.is_admin).filter(UserAuthentication.id==userid).one()
    if user is not None:
        return user[0]
    else:
        return False

def get_user_by_id(session, id):
    user = session.query(User).filter(User.userid==id).one()
    if user is not None:
        userInfo = {'firstname': user.firstname, 'lastname': user.lastname, 'self_intro': user.self_intro,'image': user.image, 'email': user.email, 'resume': user.resume, 'certificate': user.certificate}
    else:
        userInfo = {'firstname': '', 'lastname': '', 'image': '' , 'self_intro': '', 'resume': '', 'certificate': ''}
    return userInfo

def get_all_user(session):
    user_list = []
    users = session.query(User).all()
    if users is not None and len(users)!=0:
        for user in users:
            admin = user_is_admin(session, user.userid)
            if not admin:
                try:
                    annualLeaveDays = session.query(AnnualLeaveDays).filter(
                        AnnualLeaveDays.userid == user.userid).one()
                    user_list.append({'id': user.userid, 'firstname': user.firstname, 'lastname': user.lastname, 'image': user.image, 'resume': user.resume, 'certificate': user.certificate, 'self_intro': user.self_intro,
                                  'age': user.age, 'phone': user.phone, 'email': user.email, 'position': user.jobtitle, 'skill': user.primaryskills, 'annual': annualLeaveDays.annualleave, 'sick': annualLeaveDays.sickleave,
                                  'department': user.department, 'location': user.location})
                except:
                    continue
    return user_list

def get_user_payroll(session):
    payroll_list = []

    payrolls = session.query(Payroll).all()
    if payrolls is not None and len(payrolls) != 0:
        for payroll in payrolls:
            admin = user_is_admin(session, payroll.userid)
            if not admin:
                payroll_list.append({'id': payroll.id, 'firstname': payroll.firstname, 'lastname': payroll.lastname,
                              'basicSalary': payroll.basicSalary, 'tax': payroll.tax, 'deduction': payroll.deduction, 'overTime': payroll.overTime,
                              'totalPayRate': payroll.totalPayRate, 'payDate': payroll.payDate})
    return payroll_list


def get_user_leave(session):
    leave_list = []

    leaves = session.query(Leave).all()
    if leaves is not None and len(leaves) != 0:
        for leave in leaves:
            leave_list.append({'id': leave.id, 'firstname': leave.firstname, 'lastname': leave.lastname, 'userid': leave.userid, 'leavetype': leave.leavetype,
                                 'description': leave.description, 'startDate': leave.startDate, 'endDate': leave.endDate, 'status': leave.status
                              })
    return leave_list


def get_payroll_by_user(session, id):
    payroll_list = []
    payroll = session.query(Payroll).filter(Payroll.userid==id).one()
    if payroll is not None:
        payroll_list.append({'id': payroll.id, 'firstname': payroll.firstname, 'lastname': payroll.lastname,
                             'basicSalary': payroll.basicSalary, 'tax': payroll.tax, 'deduction': payroll.deduction,
                             'overTime': payroll.overTime,
                             'totalPayRate': payroll.totalPayRate, 'payDate': payroll.payDate})
    return payroll_list

def get_leave_form_history_by_user(session, id):

    forms = []
    leave_form = session.query(Leave).filter(Leave.userid==id).all()
    if leave_form is not None and len(leave_form)!=0:
        for leave in leave_form:
            forms.append({'leave': leave.leavetype, 'description': leave.description, 'sdate': leave.startDate,
                          'edate': leave.endDate, 'status': leave.status})
    return forms

def get_day_leave_left(session, userid, year):
    day = session.query(TotalAnnualLeave).filter(TotalAnnualLeave.year==year).filter(TotalAnnualLeave.userid==userid).one()
    annualDays = day.annualleaveday
    sickDays = day.sickleaveday
    unpaidDays = day.unpaidleaveday
    return annualDays, sickDays, unpaidDays

def get_all_leave(session, year):
    annualDays = 0
    sickDays = 0
    try:
        check = session.query(TotalAnnualLeave).filter(TotalAnnualLeave.year==year).all()
        if check is not None and len(check)!=0:
            for day in check:
                annualDays = annualDays + day.annualleaveday
                sickDays = sickDays + day.sickleaveday
    except Exception:
        pass
    return annualDays, sickDays

def get_latest_payroll_by_userid(session, id):
    userPayroll = {'id': '', 'firstname': '', 'lastname': '', 'basicSalary': '', 'tax': '', 'deduction': '',
                   'overTime': '', 'totalPayRate': '', 'payDate': ''}
    payroll = session.query(Payroll).filter(Payroll.userid==id).order_by(Payroll.payDate.desc()).limit(1).one()
    if payroll is not None:
        userPayroll = {'id': payroll.id, 'firstname': payroll.firstname, 'lastname': payroll.lastname,
                             'basicSalary': payroll.basicSalary, 'tax': payroll.tax, 'deduction': payroll.deduction,
                             'overTime': payroll.overTime,
                             'totalPayRate': payroll.totalPayRate, 'payDate': payroll.payDate}
    return userPayroll
