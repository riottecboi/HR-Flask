from database.datamodel import *

def user_is_admin(session, userid):
    user = session.query(UserAuthentication.is_admin).filter(UserAuthentication.id==userid).one()
    if user is not None:
        return user[0]
    else:
        return False

def get_all_user(session):
    user_list = []
    users = session.query(User).all()
    if users is not None and len(users)!=0:
        for user in users:
            admin = user_is_admin(session, user.userid)
            if not admin:
                user_list.append({'id': user.id, 'firstname': user.firstname, 'lastname': user.lastname,
                              'age': user.age, 'phone': user.phone, 'email': user.email, 'position': user.jobtitle, 'skill': user.primaryskills,
                              'department': user.department, 'location': user.location})
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
            leave_list.append({'id': leave.id, 'firstname': leave.firstname, 'lastname': leave.lastname,
                                 'description': leave.description, 'startDate': leave.startDate, 'endDate': leave.endDate,
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
