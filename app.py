from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from functools import wraps
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


# User database model
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
class Assignment(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    faculty_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    due_date = db.Column(db.Date, nullable=False)
class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)

    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey('assignments.id'),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    content = db.Column(db.Text, nullable=False)

    submitted_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/health')
def health():
    return {"status": "ok"}


# Login
@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):

    if role not in ['admin', 'faculty', 'student']:
        return "Invalid role", 404

    error = None

    if request.method == 'POST':

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(
            email=email,
            role=role
        ).first()

        if user and check_password_hash(user.password, password):

            session['user_id'] = user.id
            session['email'] = user.email
            session['role'] = user.role

            return redirect(url_for(role))

        error = "Invalid email or password"

    return render_template(
        'login.html',
        role=role.capitalize(),
        error=error
    )


# Role authentication
def role_required(required_role):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if session.get('role') != required_role:
                return redirect(url_for('login', role=required_role))

            return function(*args, **kwargs)

        return wrapper

    return decorator


@app.route('/admin')
@role_required('admin')
def admin():
    students = User.query.filter_by(role='student').count()
    faculty_count = User.query.filter_by(role='faculty').count()
    total_users = User.query.count()

    return render_template(
        'admin.html',
        email=session['email'],
        students=students,
        faculty=faculty_count,
        total_users=total_users
    )
@app.route('/admin/users')
@role_required('admin')
def admin_users():
    users = User.query.order_by(User.role, User.email).all()
    return render_template(
        'users.html',
        users=users,
        title='All Users'
    )


@app.route('/admin/users/<role>')
@role_required('admin')
def admin_users_by_role(role):
    if role not in ('student', 'faculty'):
        return "Invalid role", 404

    users = User.query.filter_by(role=role).order_by(User.email).all()

    return render_template(
        'users.html',
        users=users,
        title=f'{role.title()} Accounts'
    )
@app.route('/faculty')
@role_required('faculty')
def faculty():
    return render_template(
        'faculty.html',
        email=session['email']
    )
@app.route('/faculty/students')
@role_required('faculty')
def faculty_students():
    students = User.query.filter_by(role='student').order_by(User.email).all()

    return render_template(
        'users.html',
        users=students,
        title='Student Accounts'
    )
@app.route('/faculty/attendance', methods=['GET', 'POST'])
@role_required('faculty')
def faculty_attendance():
    students = User.query.filter_by(role='student').order_by(User.email).all()

    if request.method == 'POST':
        for student in students:
            attendance_date = date.fromisoformat(
                request.form[f'date_{student.id}']
            )
            status = request.form[f'status_{student.id}']

            if status not in ('Present', 'Absent'):
                return "Invalid attendance status", 400

            record = Attendance.query.filter_by(
                student_id=student.id,
                attendance_date=attendance_date
            ).first()

            if record:
                record.status = status
                record.faculty_id = session['user_id']
            else:
                db.session.add(Attendance(
                    student_id=student.id,
                    faculty_id=session['user_id'],
                    attendance_date=attendance_date,
                    status=status
                ))

        db.session.commit()
        return "Attendance saved successfully! <a href='/faculty'>Back to Dashboard</a>"

    return render_template('attendance.html', students=students)
@app.route('/faculty/assignments', methods=['GET', 'POST'])
@role_required('faculty')
def faculty_assignments():

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        due_date_value = request.form.get('due_date', '')

        if not title or not description or not due_date_value:
            return "All fields are required", 400

        try:
            due_date = date.fromisoformat(due_date_value)
        except ValueError:
            return "Invalid due date", 400

        assignment = Assignment(
            title=title,
            description=description,
            faculty_id=session['user_id'],
            due_date=due_date
        )

        db.session.add(assignment)
        db.session.commit()

    assignments = Assignment.query.filter_by(
        faculty_id=session['user_id']
    ).order_by(Assignment.due_date).all()

    return render_template(
        'assignments.html',
        assignments=assignments
    )
@app.route('/student')
@role_required('student')
def student():
    return render_template(
        'student.html',
        email=session['email']
    )

@app.route('/student/attendance')
@role_required('student')
def student_attendance():
    records = Attendance.query.filter_by(
        student_id=session['user_id']
    ).order_by(Attendance.attendance_date.desc()).all()

    return render_template(
        'student_attendance.html',
        records=records
    )
@app.route('/student/assignments')
@role_required('student')
def student_assignments():

    assignments = Assignment.query.order_by(
        Assignment.due_date
    ).all()

    return render_template(
        'student_assignments.html',
        assignments=assignments
    )
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
