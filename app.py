from flask import Flask, render_template, request, redirect, url_for, jsonify
import pymysql
pymysql.install_as_MySQLdb()
from flask_sqlalchemy import SQLAlchemy
import json
import random
#import openai

# Initialize Flask application
app = Flask(__name__)

# Configure SQLAlchemy to use MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://myfirstsql:password@localhost/students'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications for better performance
db = SQLAlchemy(app)

# Define SQLAlchemy models
class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'))
    registration_date = db.Column(db.TIMESTAMP, server_default=db.func.now())

class Course(db.Model):
    __tablename__ = 'courses'
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100))
    description = db.Column(db.Text)

class Grade(db.Model):
    __tablename__ = 'grades'
    grade_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    grade = db.Column(db.DECIMAL(5, 2))
    student = db.relationship('Student', backref='grades')
    course = db.relationship('Course', backref='grades')

# Load JSON data into database
def load_data():
    with open('data.json') as f:
        data = json.load(f)

    with app.app_context():
        for table_name, table_data in data.items():
            if table_name == 'students':
                for row in table_data:
                    student = Student(**row)
                    db.session.add(student)
            elif table_name == 'courses':
                for row in table_data:
                    course = Course(**row)
                    db.session.add(course)
            elif table_name == 'grades':
                for row in table_data:
                    grade = Grade(**row)
                    db.session.add(grade)

        db.session.commit()

# Dummy user database (for login)
users = {
    "user1": "password1",
    "user2": "password2"
}

# Responses for different types of questions
greetings = ["Hello! Enter your College Name to continue:", "Hi there! Enter your College Name to continue:", "Hey! How can I help you? Enter your College Name to continue:"]
questions_about_school = ["What's your question about the college?", "How can I assist you with college-related inquiries?"]
questions_about_courses = ["What specific course are you interested in?", "Tell me which course you want to know about."]
questions_about_grades = ["Do you want to know about your grades?", "Are you inquiring about your academic performance?"]

# OpenAI API key
#openai.api_key = 'sk-proj-cMwPwxdtWpAhreAKpkNFT3BlbkFJSenAcXWTelxB1RSyie0a'

# Function to get grade information for a student
def get_grade_info(student_id):
    student = Student.query.get(student_id)
    if student:
        grades_info = "\n".join(["{}: {}".format(grade.course.course_name, grade.grade) for grade in student.grades])
        return grades_info if grades_info else "Sorry, I couldn't find any grades for that student."
    else:
        return "Sorry, I couldn't find any student with that ID."

# Function to generate response based on user input
def generate_response(user_input):
    if any(greeting in user_input for greeting in ["hello", "hi", "hey"]):
        return random.choice(greetings)
    elif "bvrit" in user_input:
        return random.choice(questions_about_school)
    elif "course" in user_input:
        return "CSE,IT,ECE,EEE,AIML,AI&DS"
    elif "grade" in user_input:
        return "O,A+,A,B+,B,C"
    elif "cse" in user_input:
        return "Computer Science and Engineering"
    elif "it" in user_input:
        return "Information and Technology"
    elif "ece" in user_input:
        return "Electrical Communication and Engineering"
    elif "eee" in user_input:
        return "Electrical and Electronics Engineering"
    elif "aiml" in user_input:
        return "Artificial Intelligence and Machine Learning"
    elif "ai&ds" in user_input:
        return "Artificial Intelligence and Data Science"
    elif "student details" in user_input:
        return "Enter Student name(Ram,Shyam,Sethu):"
    elif "ram" in user_input:
        return "Ram is studying at BVRIT in CSE with Grade 'O' "
    elif "shyam" in user_input:
        return "Shyam is studying at BVRIT in ECE with Grade 'A' "
    elif "sethu" in user_input:
        return "Sethu is studying at BVRIT in AI&ML with Grade 'B+' "
    elif "bye" in user_input:
        return "Goodbye! Have a nice day."
    else:
        return "I'm sorry, I didn't understand. Can you please rephrase?"

# Route for index page (login form)
@app.route('/')
def index():
    return render_template("login.html")

# Route for handling login form submission
@app.route('/form_login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            # Authentication successful, redirect to chatbot page
            return redirect(url_for('chatbot'))
        else:
            error = 'Invalid credentials. Please try again.'
    return render_template('login.html', error=error)

# Route for chatbot page
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# Route for suggestions page
@app.route('/suggestions')
def suggestions():
    return render_template('suggestions.html')

# Route for about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for handling user input and generating response
@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input'].lower()
    response = generate_response(user_input)
    return jsonify({'response': response})  # Return JSON response for AJAX handling

# Route for loading data into the database (used for testing)
@app.route('/load_data')
def route_load_data():
    load_data()
    return "Data loaded successfully!"

# Route for handling suggestion submissions
@app.route('/submit_suggestion', methods=['POST'])
def submit_suggestion():
    suggestion = request.form['suggestion']
    # Handle the suggestion submission (e.g., save to database or send via email)
    print(f"Received suggestion: {suggestion}")
    return redirect(url_for('chatbot'))

# Route for logout
@app.route('/logout')
def logout():
    # Assuming session handling logic here
    return redirect(url_for('index'))

# Optional route to use OpenAI for generating responses
@app.route('/openai_response', methods=['POST'])
def openai_response():
    user_input = request.form['user_input']
    openai_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_input,
        max_tokens=150
    )
    response_text = openai_response.choices[0].text.strip()
    return jsonify({'response': response_text})

if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(debug=True)
