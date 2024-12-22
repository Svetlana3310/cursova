from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, Course, Enrollment, Assignment, Grade
from api.auth import role_required

routes = Blueprint('routes', __name__)


@routes.route('/courses', methods=['POST'], endpoint="create_course")
@jwt_required()
@role_required('instructor')
def create_course_instructor():
    """
    Create a new course. Endpoint: POST /courses (Instructor only)
    Expects JSON:
    {
        "name": "Course Name",
        "description": "Course Description"
    }
    """
    data = request.json
    if not data or 'name' not in data or 'description' not in data:
        return jsonify({"message": "Invalid data provided"}), 400

    instructor_id = get_jwt_identity().get('id')
    course = Course(
        name=data['name'], description=data['description'], instructor_id=instructor_id)
    db.session.add(course)
    db.session.commit()
    return jsonify({"message": "Course created successfully!"}), 201


@routes.route('/courses', methods=['GET'], endpoint="get_course")
@jwt_required()
def get_courses_all():
    """
    Get all courses. Endpoint: GET /courses
    Response: List of courses with fields:
    [
        {"id": int, "name": str, "description": str}
    ]
    """
    courses = Course.query.all()
    return jsonify([{"id": c.id, "name": c.name, "description": c.description} for c in courses]), 200


@routes.route('/enrollments', methods=['POST'], endpoint="create_enrollments")
@jwt_required()
@role_required('student')
def enroll_in_course_student():
    """
    Enroll a student in a course. Endpoint: POST /enrollments (Student only)
    Expects JSON:
    {
        "course_id": int
    }
    """
    data = request.json
    if not data or 'course_id' not in data:
        return jsonify({"message": "Invalid data provided"}), 400

    student_id = get_jwt_identity().get('id')
    enrollment = Enrollment(student_id=student_id, course_id=data['course_id'])
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({"message": "Enrolled successfully!"}), 201


@routes.route('/enrollments', methods=['GET'], endpoint="get_enrollments")
@jwt_required()
@role_required('student')
def get_student_enrollments():
    """
    Get a student's enrollments. Endpoint: GET /enrollments (Student only)
    Response: List of enrollments with fields:
    [
        {"course_id": int, "enrolled_date": str}
    ]
    """
    student_id = get_jwt_identity().get('id')
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    return jsonify([{"course_id": e.course_id, "enrolled_date": e.enrolled_date.isoformat() if e.enrolled_date else None} for e in enrollments]), 200


@routes.route('/assignments', methods=['POST'], endpoint="create_assignments")
@jwt_required()
@role_required('instructor')
def create_assignment_instructor():
    """
    Create a new assignment. Endpoint: POST /assignments (Instructor only)
    Expects JSON:
    {
        "title": "Assignment Title",
        "description": "Assignment Description",
        "due_date": "YYYY-MM-DD",
        "course_id": int
    }
    """
    data = request.json
    if not data or 'title' not in data or 'description' not in data or 'due_date' not in data or 'course_id' not in data:
        return jsonify({"message": "Invalid data provided"}), 400

    assignment = Assignment(title=data['title'], description=data['description'],
                            due_date=data['due_date'], course_id=data['course_id'])
    db.session.add(assignment)
    db.session.commit()
    return jsonify({"message": "Assignment created successfully!"}), 201


@routes.route('/assignments/<int:course_id>', methods=['GET'], endpoint="get_assignments")
@jwt_required()
def get_course_assignments(course_id):
    """
    Get assignments for a specific course. Endpoint: GET /assignments/<course_id>
    Response: List of assignments with fields:
    [
        {"id": int, "title": str, "description": str, "due_date": str}
    ]
    """
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    return jsonify([{"id": a.id, "title": a.title, "description": a.description, "due_date": a.due_date.isoformat() if a.due_date else None} for a in assignments]), 200


@routes.route('/grades', methods=['POST'], endpoint="create_grades")
@jwt_required()
@role_required('instructor')
def assign_grade_instructor():
    """
    Assign a grade to a student. Endpoint: POST /grades (Instructor only)
    Expects JSON:
    {
        "assignment_id": int,
        "student_id": int,
        "grade": str
    }
    """
    data = request.json
    if not data or 'assignment_id' not in data or 'student_id' not in data or 'grade' not in data:
        return jsonify({"message": "Invalid data provided"}), 400

    grade = Grade(assignment_id=data['assignment_id'],
                  student_id=data['student_id'], grade=data['grade'])
    db.session.add(grade)
    db.session.commit()
    return jsonify({"message": "Grade assigned successfully!"}), 201


@routes.route('/student/history', methods=['GET'], endpoint="student_history")
@jwt_required()
@role_required('student')
def get_student_course_history():
    """
    Get a student's course history. Endpoint: GET /student/history (Student only)
    Response: List of course history with fields:
    [
        {"course_name": str, "enrolled_date": str, "grade": str}
    ]
    """
    try:
        identity = get_jwt_identity()
        if not identity or 'id' not in identity:
            return jsonify({"message": "Invalid token or missing identity"}), 403

        student_id = identity['id']
        query = db.session.query(
            Course.name.label("course_name"),
            Enrollment.enrolled_date,
            Grade.grade
        ).join(
            Enrollment, Enrollment.course_id == Course.id
        ).outerjoin(
            Grade, (Grade.student_id == Enrollment.student_id) &
                   (Grade.assignment_id.in_(
                       db.session.query(Assignment.id).filter(
                           Assignment.course_id == Course.id)
                   ))
        ).filter(
            Enrollment.student_id == student_id
        )

        result = query.all()
        history = [
            {
                "course_name": record.course_name,
                "enrolled_date": record.enrolled_date.isoformat() if record.enrolled_date else None,
                "grade": record.grade
            }
            for record in result
        ]
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"message": "Error fetching history", "error": str(e)}), 500
