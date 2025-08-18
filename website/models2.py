from website import db2
from flask_login import UserMixin
from datetime import datetime

class Business(db2.Model, UserMixin):
    b_id = db2.Column(db2.Integer, primary_key=True, autoincrement=True)
    bname = db2.Column(db2.String(200), unique=True)
    Firstname = db2.Column(db2.String(150))
    email = db2.Column(db2.String(150), unique=True)
    password = db2.Column(db2.String(150))

    employees = db2.relationship("Employee", back_populates="business", cascade="all, delete-orphan")
    holidays = db2.relationship("Holiday", back_populates="business", cascade="all, delete-orphan")

    def get_id(self):
        return str(self.b_id)

class Employee(db2.Model):
    emp_id = db2.Column(db2.Integer, primary_key=True, autoincrement=True)
    emp_name = db2.Column(db2.String(150))
    position = db2.Column(db2.String(100))
    phonenumber = db2.Column(db2.String(15))
    payment_details = db2.Column(db2.String(150))
    join_date = db2.Column(db2.Date, default=datetime.utcnow)
    base_salary = db2.Column(db2.Float)  # Monthly base salary
    b_id = db2.Column(db2.Integer, db2.ForeignKey('business.b_id'))

    business = db2.relationship("Business", back_populates="employees")
    emp_attendance = db2.relationship('EmployeeAttendance', back_populates="employee", cascade="all, delete-orphan")
    salary_info = db2.relationship('Salary', back_populates="employee", cascade="all, delete-orphan")

class EmployeeAttendance(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True,autoincrement =True)
    emp_id = db2.Column(db2.Integer, db2.ForeignKey('employee.emp_id'), index=True)
    date = db2.Column(db2.Date, default=datetime.utcnow)  # Corrected default
    status = db2.Column(db2.String(20))  # 'present', 'absent', 'leave', 'holiday'

    employee = db2.relationship('Employee', back_populates="emp_attendance")

    def __repr__(self):
        return f"<Attendance {self.emp_id} on {self.date}: {self.status}>"
class Holiday(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True)
    b_id = db2.Column(db2.Integer, db2.ForeignKey('business.b_id'))
    date = db2.Column(db2.Date)
    name = db2.Column(db2.String(150))

    business = db2.relationship("Business", back_populates="holidays")


class Salary(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True)
    emp_id = db2.Column(db2.Integer, db2.ForeignKey('employee.emp_id'))
    month = db2.Column(db2.Integer)  # 1-12
    year = db2.Column(db2.Integer)
    base_salary = db2.Column(db2.Float)
    deductions = db2.Column(db2.Float, default=0)
    bonuses = db2.Column(db2.Float, default=0)
    net_salary = db2.Column(db2.Float)
    payment_status = db2.Column(db2.String(20), default='pending')  # 'pending', 'paid'
    payment_date = db2.Column(db2.Date, nullable=True)
    payment_details = db2.Column(db2.String(150))
    employee = db2.relationship('Employee', back_populates="salary_info")