from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os

app = Flask(__name__)

app.secret_key = "student_management_secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
 
load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(200))


# Home Page
@app.route('/')
def index():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    students = Student.query.filter(
        Student.name.contains(search)
    ).paginate(
        page=page,
        per_page=5,
        error_out=False
    )

    return render_template(
        'index.html',
        students=students,
        search=search
    )


# Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session['admin'] = True

            flash(
                'Login Successful!',
                'success'
            )

            return redirect(url_for('index'))

        flash(
            'Invalid Username or Password',
            'danger'
        )

    return render_template('login.html')


# Logout
@app.route('/logout')
def logout():

    session.pop('admin', None)

    flash(
        'Logged Out Successfully!',
        'warning'
    )

    return redirect(url_for('index'))


# Add Student
@app.route('/add', methods=['GET', 'POST'])
def add_student():

    if 'admin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        name = request.form['name']
        age = request.form['age']
        course = request.form['course']

        photo = request.files['photo']

        filename = ""

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

        student = Student(
            name=name,
            age=age,
            course=course,
            photo=filename
        )

        db.session.add(student)
        db.session.commit()

        flash(
            'Student Added Successfully!',
            'success'
        )

        return redirect(url_for('index'))

    return render_template('add.html')


# Edit Student
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    if 'admin' not in session:
        return redirect(url_for('login'))

    student = Student.query.get_or_404(id)

    if request.method == 'POST':

        student.name = request.form['name']
        student.age = request.form['age']
        student.course = request.form['course']

        photo = request.files['photo']

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            student.photo = filename

        db.session.commit()

        flash(
            'Student Updated Successfully!',
            'info'
        )

        return redirect(url_for('index'))

    return render_template(
        'edit.html',
        student=student
    )


# Delete Student
@app.route('/delete/<int:id>')
def delete_student(id):

    if 'admin' not in session:
        return redirect(url_for('login'))

    student = Student.query.get_or_404(id)

    db.session.delete(student)
    db.session.commit()

    flash(
        'Student Deleted Successfully!',
        'danger'
    )

    return redirect(url_for('index'))


# Main
if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    os.makedirs(
        app.config['UPLOAD_FOLDER'],
        exist_ok=True
    )

    app.run(debug=True)
