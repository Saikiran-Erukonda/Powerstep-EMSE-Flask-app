import pandas as pd
from datetime import date, timedelta
from website import db2
from website.models2 import Employee, EmployeeAttendance, Holiday, Salary

def calculate_salary(emp_id, month, year):
    employee = Employee.query.get(emp_id)
    if not employee:
        raise ValueError(f"Employee with ID {emp_id} not found.")

    start_date = date(year, month, 1)
    end_date = date(year + (month // 12), (month % 12) + 1, 1)

    attendance_records = EmployeeAttendance.query.filter(
        EmployeeAttendance.emp_id == emp_id,
        EmployeeAttendance.date >= start_date,
        EmployeeAttendance.date < end_date
    ).all()

    holidays = Holiday.query.filter(
        Holiday.b_id == employee.b_id,
        Holiday.date >= start_date,
        Holiday.date < end_date
    ).all()

    holiday_dates = {h.date for h in holidays}
    attendance_map = {a.date: a.status for a in attendance_records}

    data = []
    for day in pd.date_range(start_date, end_date - timedelta(days=1)):
        current_date = day.date()
        if current_date.weekday() >= 5:
            status = 'weekend'
        elif current_date in holiday_dates:
            status = 'holiday'
        else:
            status = attendance_map.get(current_date, 'absent')
        data.append({'date': current_date, 'status': status})

    df = pd.DataFrame(data)

    working_days = df[~df['status'].isin(['weekend', 'holiday'])].shape[0]
    present_days = df[df['status'] == 'present'].shape[0]
    leave_days = df[df['status'] == 'leave'].shape[0]
    absent_days = working_days - present_days - leave_days

    daily_salary = employee.base_salary / working_days if working_days > 0 else 0
    deductions = round(absent_days * daily_salary, 2)
    net_salary = round(employee.base_salary - deductions, 2)

    salary_record = Salary.query.filter_by(
        emp_id=emp_id, month=month, year=year
    ).first()

    if salary_record:
        salary_record.base_salary = employee.base_salary
        salary_record.deductions = deductions
        salary_record.net_salary = net_salary
    else:
        salary_record = Salary(
            emp_id=emp_id,
            month=month,
            year=year,
            base_salary=employee.base_salary,
            deductions=deductions,
            net_salary=net_salary,
            payment_status='pending'
        )
        db2.session.add(salary_record)

    db2.session.commit()
    return salary_record