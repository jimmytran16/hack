from app import app
from db import calls
from datetime import date
from student_pkg import Student
import base64 # for encoding and decoding images
from flask import render_template, redirect, url_for, session, request, logging, jsonify
# sha256_crpyt for verifying encrypted passswords
from passlib.hash import sha256_crypt
from uuid import uuid4 #generating API keys

@app.route('/adminLogout',methods=['POST'])
def adminLogout():
    if request.method == 'POST':
        session['admin'] = None #Empty the admin value in session
        return redirect('api')
    else:
        return 'Method not allowed! 405'

@app.route('/api/admin') #route to admin log in page
def adminSignIn():
    if autho_login_admin():
        return redirect(url_for('AdminSucces'));
    else:
        return render_template('api/admin.html')

@app.route('/api') #render the admin page to login for API access
def APIpage():
    return render_template('api/home.html')

@app.route('/unauthorized403')
def unauthorized():
    return render_template('api/403error.html')

@app.route('/successLogin')
def AdminSucces():
    if autho_login_admin():
        return render_template('api/admin_dashboard.html',user=session['admin'])
    else:
        return redirect('unauthorized403',code=302)

@app.route('/adminLogin', methods = ['POST']) # handle the admin login request
def AdminLogin():
    if request.method == 'POST':
        username = request.form['username']
        data =calls.getAdminUser(username)
        if data == 'error': #check if the query returns an empty tuple or if there's a user under that Username
            return render_template('api/admin.html', err='Wrong Crudentials!')
        else:
            if data[0] == request.form['username'] and sha256_crypt.verify(request.form['password'],data[1]):
                session['admin'] = data[0]
                return redirect('successLogin')
            else:
                return render_template('api/admin.html', err='Wrong Crudentials!')
    return redirect('api')

def autho_login_admin(): # func to determine if admin is logged in
    if not session.get('admin'):
        return False
    elif session['admin'] != None:
        return True
    else:
        return False

def autho_login():
    # session variable 'fullname' is not assigned when user first runs the app
    if not session.get('fullname'):
        return False
    elif session['fullname'] != None:
        return True
    else:
        return False

@app.route('/api/signup')
def signUpForApiKey():
    return render_template('api/signup.html')

@app.route('/api/generatingKey', methods =['POST']) # path after user registers for api key
def generateKey():
    USERNAME = request.form.get('emailAddress')
    GENERATED_KEY = str(uuid4())
    calls.saveApiKey(USERNAME,GENERATED_KEY)
    return render_template('api/signup.html',KEY=GENERATED_KEY,signup=True) # will pass back to the signup page that they have successfully signed up and display the api key

@app.route('/api/student/<string:id>') #request handler for student's information
def getStudentJson(id):
    api_key = request.args.get('api_key')
    if api_key == None: # if user did not submit the form with the api key, return an error message
        return jsonify({'Error':'API KEY IS REQUIRED'})
    print(api_key)
    if calls.getApiKey(api_key):
        data = calls.getStudentDataRequest(id)
        print(f'THE DATA-----------{data}')
        if not data:
            return jsonify({'message':'Student cannot be found!','error':400})
        student_information = {
            'First Name':data[0][0].split(' ')[0],
            'Last Name':data[0][0].split(' ')[1],
            'Teacher ID':data[0][1],
            'Grades':{'English':data[0][2],'Math':data[0][3],'Science':data[0][4],'History':data[0][5]}
        }
        print(student_information)
        return jsonify(student_information)
    else:
        return jsonify({'Error':'INVALID API KEY'})
@app.route('/api/teacher/<int:id>') # request handler for teacher's information
def getTeacherJson(id):
    api_key = request.args.get('api_key')
    if api_key == None: # if user did not submit the form with the api key, return an error message
        return jsonify({'Error':'API KEY IS REQUIRED'})
    if calls.getApiKey(api_key):
        data = calls.getTeacherDataRequest(id)
        if not data: # if the tuple that is returned from the database is empty (no teacher matches requested)
            return jsonify({'Message':"No Teacher's found!",'error':400})
        print(data)
        teacher_information = {'Name':data[0][0],'Staff_ID':data[0][1]}
        return jsonify(teacher_information)
    else:
        return jsonify({'Error':'INVALID API KEY'})

@app.route('/api/teacher/all') # request to get list of all of the teachers in the DB
def getAllTeachers():
    api_key = request.args.get('api_key')
    if api_key == None: # if user did not submit the form with the api key, return an error message
        return jsonify({'Error':'API KEY IS REQUIRED'})
    if calls.getApiKey(api_key):
        teacher = {}
        teacher_list = []
        data = calls.getAllTeachers()
        for i in data:
            name = {'Name':i[0],'Id':i[1]}
            teacher_list.append(name)
        teacher['teachers'] = teacher_list
        return jsonify(teacher)
    else:
        return jsonify({'Error':'INVALID API KEY'})

@app.route('/api/student/all') # request to get list of all of the teachers in the DB
def getAllStudents():
    api_key = request.args.get('api_key')
    if api_key == None: # if user did not submit the form with the api key, return an error message
        return jsonify({'Error':'API KEY IS REQUIRED'})
    if calls.getApiKey(api_key):
        students = {}
        students_list = []
        data = calls.getAllStudents()
        for i in data:
            details_dict = {'Name':i[0],'Teacher_id':i[1],'English':i[2],'Math':i[3],'Science':i[4],'History':i[5],'student_id':i[6]}
            students_list.append(details_dict)
        students['students'] = students_list
        return jsonify(students)
    else:
        return jsonify({'Error':'INVALID API KEY'})
