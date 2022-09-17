from database.datamodel import *

def get_all_user(session):
    user_list = []
    users = session.query(User).all()
    if users is not None and len(users)!=0:
        for user in users:
            user_list.append({'id': user.id, 'firstname': user.firstname, 'lastname': user.lastname,
                              'age': user.age, 'phone': user.phone, 'email': user.email, 'position': user.jobtitle,
                              'department': user.department, 'location': user.location})
    return user_list