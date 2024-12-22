from app import app
from api.models import db, User, Course, Enrollment, Assignment, Grade
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Seed Data


def seed_data():
    with app.app_context():
        # Clear existing data
        db.session.query(Grade).delete()
        db.session.query(Assignment).delete()
        db.session.query(Enrollment).delete()
        db.session.query(Course).delete()
        db.session.query(User).delete()

        # Create Instructors
        instructors = []
        for _ in range(5):
            instructor = User(
                name=fake.name()[:50],  # Ensure name fits within constraints
                email=fake.unique.email(),
                # Truncate phone to 20 characters
                phone=fake.phone_number()[:20],
                role="instructor",  # Ensure role fits in 'instructor' or 'student'
            )
            instructor.set_password("password123")
            instructors.append(instructor)
            db.session.add(instructor)

        # Create Students
        students = []
        for _ in range(20):
            student = User(
                name=fake.name()[:50],  # Ensure name fits within constraints
                email=fake.unique.email(),
                # Truncate phone to 20 characters
                phone=fake.phone_number()[:20],
                role="student",  # Ensure role fits in 'instructor' or 'student'
            )
            student.set_password("password123")
            students.append(student)
            db.session.add(student)

        db.session.commit()

        # Create Courses
        courses = []
        for i in range(10):
            course = Course(
                name=f"Course {i + 1}",
                description=fake.text(max_nb_chars=200)[
                    :200],  # Ensure description fits
                instructor_id=random.choice(instructors).id,
            )
            courses.append(course)
            db.session.add(course)

        db.session.commit()

        # Create Enrollments
        for student in students:
            enrolled_courses = random.sample(courses, k=random.randint(1, 5))
            for course in enrolled_courses:
                enrollment = Enrollment(
                    student_id=student.id, course_id=course.id)
                db.session.add(enrollment)

        db.session.commit()

        # Create Assignments
        assignments = []
        for course in courses:
            for _ in range(random.randint(2, 5)):
                assignment = Assignment(
                    # Ensure title fits within constraints
                    title=fake.sentence(nb_words=5)[:100],
                    description=fake.text(max_nb_chars=150)[
                        :150],  # Ensure description fits
                    due_date=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                    course_id=course.id,
                )
                assignments.append(assignment)
                db.session.add(assignment)

        db.session.commit()

        # Create Grades
        for assignment in assignments:
            enrolled_students = Enrollment.query.filter_by(
                course_id=assignment.course_id
            ).all()
            for enrollment in enrolled_students:
                grade = Grade(
                    assignment_id=assignment.id,
                    student_id=enrollment.student_id,
                    grade=random.uniform(50.0, 100.0),
                )
                db.session.add(grade)

        db.session.commit()
        print("Seeding complete!")


if __name__ == "__main__":
    seed_data()
