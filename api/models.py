from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(255), nullable=False)
    # 'student' or 'instructor'
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    instructor = db.relationship('User', backref='courses', lazy=True)


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey(
        'courses.id'), nullable=False)
    enrolled_date = db.Column(db.Date, default=db.func.current_date())
    student = db.relationship('User', backref='enrollments', lazy=True)
    course = db.relationship('Course', backref='enrollments', lazy=True)


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey(
        'courses.id'), nullable=False)
    course = db.relationship('Course', backref='assignments', lazy=True)


class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey(
        'assignments.id'), nullable=False)
    student_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    graded_date = db.Column(db.Date, default=db.func.current_date())
    assignment = db.relationship('Assignment', backref='grades', lazy=True)
    student = db.relationship('User', backref='grades', lazy=True)
