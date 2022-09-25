from sqlalchemy import Column, TIMESTAMP, Integer, String, Boolean, Float, BigInteger, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from os import urandom
from binascii import hexlify
from hashlib import sha512, sha224, sha256

Base = declarative_base()
class UserAuthentication(Base):
    __tablename__ = 'authentication'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    password_salt = Column(String(255))
    authenticated = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    view_clean = Column(Boolean, default=False)


    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    def set_authenticated(self, session, value):
        self.authenticated = value
        session.add(self)
        session.commit()

    def generate_salt(self):
        self.password_salt = hexlify(urandom(32)).decode('utf-8').upper()
        return self.password_salt

    def change_password(self, password):
        self.generate_salt()
        self.password = self.generate_password_hash(password, self.password_salt)
        return

    def generate_password_hash(self, password, salt):
        return sha512(salt.encode('utf-8') + password.encode('utf-8')).hexdigest().upper()

    def check_password(self, password):
        hash = self.generate_password_hash(password, self.password_salt)
        if hash == self.password:
            return True
        return False

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    userid = Column(Integer, index=True)
    firstname = Column(String(255))
    lastname = Column(String(255))
    age = Column(Integer)
    phone = Column(BigInteger, unique=True, index=True)
    email = Column(String(128), unique=True, index=True)
    jobtitle = Column(String(64))
    self_intro = Column(String(255))
    department = Column(String(128))
    primaryskills = Column(Text)
    location = Column(String(255))
    image = Column(String(255), index=True)
    resume = Column(String(255), index=True)
    certificate = Column(String(255), index=True)

class Leave(Base):
    __tablename__ = 'leave'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    userid = Column(Integer, index=True)
    firstname = Column(String(255))
    lastname = Column(String(255))
    leavetype = Column(String(32))
    description = Column(Text)
    startDate = Column(DateTime)
    endDate = Column(DateTime)
    status = Column(String(64))

class Payroll(Base):
    __tablename__ = 'payroll'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    userid = Column(Integer, index=True)
    firstname = Column(String(255))
    lastname = Column(String(255))
    basicSalary = Column(Float, default=0)
    tax = Column(Float, default=0)
    deduction = Column(Float, default=0)
    overTime = Column(Float, default=0)
    totalPayRate = Column(Float)
    payDate = Column(DateTime)

class TotalAnnualLeave(Base):
    __tablename__ = 'annualleave'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    userid = Column(Integer, index=True)
    annualleaveday = Column(Integer, default=0)
    sickleaveday = Column(Integer, default=0)
    unpaidleaveday = Column(Integer, default=0)
    year = Column(Integer)

class AnnualLeaveDays(Base):
    __tablename__ = 'annualleaveday'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    userid = Column(Integer, index=True)
    annualleave = Column(Integer, default=0)
    sickleave = Column(Integer, default=0)