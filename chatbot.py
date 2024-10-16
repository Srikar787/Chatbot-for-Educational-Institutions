from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import random

# Establish connection to the database
db_connection = mysql.connector.connect(
    host="localhost",
    user="myfirstsql",
    password="password",
    database="student"
)

# Create a cursor object to execute SQL queries
cursor = db_connection.cursor()

# Responses for different types of questions
greetings = ["Hello!", "Hi there!", "Hey! How can I help you?"]
questions_about_school = ["What's your question about the school?", "How can I assist you with school-related inquiries?"]
questions_about_courses = ["What specific course are you interested in?", "Tell me which course you want to know about."]
questions_about_grades = ["Do you want to know about your grades?", "Are you inquiring about your academic performance?"]

# Responses for different types of inquiries
school_info = "Our school offers a wide range of programs and extracurricular activities to support students' holistic development."
course_info = "The {} course covers topics such as {}, {}, and {}. It's designed to provide students with a comprehensive understanding of {}."
grade_info = "Please provide your student ID, and I can check your grades for you."

def get_course_info(course_name):
    # Query the database for course information
    query = "SELECT description FROM courses WHERE course_name = %s"
    cursor.execute(query, (course_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return "Sorry, I couldn't find information about that course."

def get_grade_info(student_id):
    # Query the database for grade information
    query = "SELECT course_name, grade FROM grades INNER JOIN courses ON grades.course_id = courses.course_id WHERE student_id = %s"
    cursor.execute(query, (student_id,))
    results = cursor.fetchall()
    if results:
        return "\n".join(["{}: {}".format(course[0], course[1]) for course in results])
    else:
        return "Sorry, I couldn't find any grades for that student."

def chatbot():
    print("Welcome to the Education Chatbot!")
    while True:
        user_input = input("You: ").lower()
        
        # Greetings
        if user_input in ["hello", "hi", "hey"]:
            print(random.choice(greetings))
        # Inquiries about the school
        elif "school" in user_input:
            print(random.choice(questions_about_school))
            print(school_info)
        # Inquiries about courses
        elif "course" in user_input:
            print(random.choice(questions_about_courses))
            course_name = input("You: ").capitalize()
            print(get_course_info(course_name))
        # Inquiries about grades
        elif "grade" in user_input:
            print(random.choice(questions_about_grades))
            student_id = input("Please enter your student ID: ")
            print(get_grade_info(student_id))
        # Ending the conversation
        elif user_input in ["bye", "goodbye"]:
            print("Goodbye! Have a great day!")
            break
        else:
            print("I'm sorry, I didn't understand. Can you please rephrase?")

# Close the cursor and the database connection when done
cursor.close()
db_connection.close()

chatbot()
