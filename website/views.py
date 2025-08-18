from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime, date
from flask_login import login_required, current_user
from website.models2 import  Employee, EmployeeAttendance, Salary, Holiday
from website import db2
from website.salarylogic import calculate_salary
import pandas as pd

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/add-employee', methods=['POST'])
@login_required
def add_employee():
    emp_name = request.form.get('emp_name')
    position = request.form.get('position')
    phonenumber = request.form.get('phonenumber')
    payment_details = request.form.get('payment_details')
    join_date_str = request.form.get('join_date')
    base_salary_str = request.form.get('base_salary')

    try:
        join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
        base_salary = float(base_salary_str)
    except (ValueError, TypeError):
        flash('Invalid input for date or salary', 'danger')
        return redirect(url_for('views.home'))

    new_employee = Employee(
        emp_name=emp_name,
        position=position,
        phonenumber=phonenumber,
        payment_details=payment_details,
        join_date=join_date,
        base_salary=base_salary,
        business=current_user
    )

    db2.session.add(new_employee)
    db2.session.commit()
    flash('Employee added successfully!', 'success')
    return redirect(url_for('views.home'))

@views.route('/mark_attendance', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    if request.method == 'POST':
        emp_id = int(request.form.get('emp_id'))
        status = request.form.get('status')
        date_str = request.form.get('date') 
        attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        employee = Employee.query.filter_by(emp_id=emp_id, b_id=current_user.b_id).first()
        if not employee:
            flash('Invalid employee selection', 'danger')
            return redirect(url_for('views.mark_attendance'))

        existing = EmployeeAttendance.query.filter_by(
            emp_id=emp_id,
            date=attendance_date
        ).first()

        if existing:
            flash('Attendance already marked for today', 'danger')
        else:
            new_attendance = EmployeeAttendance(
                emp_id=emp_id,
                date=attendance_date,
                status=status
            )
            db2.session.add(new_attendance)
            db2.session.commit()
            flash('Attendance marked successfully', 'success')

        return redirect(url_for('views.mark_attendance'))

    employees = Employee.query.filter_by(b_id=current_user.b_id).all()
    return render_template('mark_attendance.html', user=current_user, employees=employees)

@views.route('/view_attendance')
@login_required
def view_attendance():
    today = date.today()
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Default to current month if no filter is applied
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        start_date = date(today.year, today.month, 1)
        end_date = today

    employees = Employee.query.filter_by(b_id=current_user.b_id).all()
    holidays = Holiday.query.filter(
        Holiday.b_id == current_user.b_id,
        Holiday.date >= start_date,
        Holiday.date <= end_date
    ).all()
    holiday_dates = {h.date for h in holidays}

    attendance_data = []
    total_present = total_absent = total_leave = 0

    for emp in employees:
        emp_attendance = EmployeeAttendance.query.filter(
            EmployeeAttendance.emp_id == emp.emp_id,
            EmployeeAttendance.date >= start_date,
            EmployeeAttendance.date <= end_date
        ).all()

        # Optional: filter to one record per day if duplicates exist
        unique_attendance = {}
        for record in emp_attendance:
            # Only keep one record per day (latest or first)
            unique_attendance[record.date] = record

        emp_present = emp_absent = emp_leave = 0
        for record in unique_attendance.values():
            if record.status == 'present':
                emp_present += 1
            elif record.status == 'absent':
                emp_absent += 1
            elif record.status == 'leave':
                emp_leave += 1

        total_present += emp_present
        total_absent += emp_absent
        total_leave += emp_leave

        attendance_data.append({
            'employee': emp,
            'attendance': list(unique_attendance.values()),
            'present': emp_present,
            'absent': emp_absent,
            'leave': emp_leave
        })

    holiday = len(holiday_dates)

    return render_template(
        'view_attendance.html',
        user=current_user,
        attendance_data=attendance_data,
        present=total_present,
        absent=total_absent,
        leave=total_leave,
        holiday=holiday
    )

@views.route('/view_salaries')
@login_required
def view_salaries():
    m_name = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
              7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
    # Default to current month/year
    month = int(request.args.get('month', date.today().month))
    year = int(request.args.get('year', date.today().year))

    employees = Employee.query.filter_by(b_id=current_user.b_id).all()

    for emp in employees:
        calculate_salary(emp.emp_id, month, year)

    salaries = db2.session.query(Salary).join(Employee).filter(
        Employee.b_id == current_user.b_id,
        Salary.month == month,
        Salary.year == year
    ).all()

    return render_template(
        'salaries.html',month_name=m_name[month],
        user=current_user,
        salaries=salaries,
        current_month=month,
        current_year=year
    )


@views.route('/salary_filter')
@login_required
def salary_filter():
    m_name = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
              7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
    month = int(request.args.get('month', date.today().month))
    year = int(request.args.get('year', date.today().year))

    salaries = db2.session.query(Salary).join(Employee).filter(
        Employee.b_id == current_user.b_id,
        Salary.month == month,
        Salary.year == year
    ).all()
    return render_template(
        'salaries.html',
        user=current_user,
        salaries=salaries,
        current_month=month,
        month_name=m_name[month],
        current_year=year
    )

#stubs small
import calendar

@views.route('/view_salary/<int:id>', methods=['GET'])
@login_required
def view_salary(id):
    # id here is Salary.id, not Employee.id
    salary_record = Salary.query.get(id)
    if not salary_record:
        flash(f"Salary record not found.", category='error')
        return render_template("view_salary.html", user=current_user, salary=None)

    employee = Employee.query.get(salary_record.emp_id)
    if not employee:
        flash(f"Employee with ID {salary_record.emp_id} not found.", category='error')
        return render_template("view_salary.html", user=current_user, salary=None)

    month = salary_record.month
    year = salary_record.year

    # Recalculate attendance breakdown
    start_date = date(year, month, 1)
    end_date = date(year + (month // 12), (month % 12) + 1, 1)

    attendance_records = EmployeeAttendance.query.filter(
        EmployeeAttendance.emp_id == employee.emp_id,
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
    for day in pd.date_range(start_date, end_date - pd.Timedelta(days=1)):
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

    def generate_upi_link(upi_id, amount, name, note):
        return f"upi://pay?pa={upi_id}&pn={name}&am={amount}&tn={note}"
    
    payment_link = generate_upi_link(employee.payment_details,salary_record.net_salary,employee.emp_name,"Salary")

    return render_template("view_salary.html",
        user=current_user,
        emp_name=employee.emp_name,
        month=calendar.month_name[month],
        year=year,
        base_salary=salary_record.base_salary,
        present_days=present_days,
        leave_days=leave_days,
        absent_days=absent_days,
        deductions=salary_record.deductions,
        net_salary=salary_record.net_salary,
        payment_details = employee.payment_details,
        payment_status=salary_record.payment_status,
        pay = payment_link
    )

@views.route('/mark_paid/<int:id>')
@login_required
def mark_paid(id):
    salary = Salary.query.get(id)
    if salary:
        salary.payment_status = 'paid'
        db2.session.commit()
    return redirect(url_for('views.view_salaries'))


