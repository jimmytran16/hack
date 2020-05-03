from app import app
from db import calls
from datetime import date
from student_pkg import Student
import base64 # for encoding and decoding images
from flask import render_template, redirect, url_for, session, request, logging, jsonify
# sha256_crpyt for verifying encrypted passswords
from passlib.hash import sha256_crypt
from uuid import uuid4 #generating API keys

# Mapping for URLS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if not autho_login():
        return redirect(url_for("denied"))
    activity_log = calls.getActivityLogList()  # get activity log from db
    list = []
    for i in activity_log:
        list.append(i)
    list.reverse() # use the reverse function to get the list to descending order
    return render_template('dashboard.html', login=True, name=session['fullname'], activity_log=list)

# student behavoir chart
@app.route('/behavior')
def general():
    if not autho_login():
        return redirect('/')
    return render_template('general.html',searched = False)
# get student information for the graph
@app.route('/fetchGrades')
def fetchgrades():
    if not autho_login():
        return redirect('/')
    else:
        student_id = request.args.get('student_id')
        row = calls.getStudentGrades(student_id)
        if row == None:
            return render_template('general.html', error = 'Student does not exist!')
        # will pass in the student data and teacher to the getHours() function to determine study hour requirements
        st_teacher = calls.getTeacher(row[1])
        priority_list = Student.getStudentHours(row,st_teacher)
        info_hash = {
            "Name":row[0],
            "English":[row[2],Student.checkGradeType(row[2])],
            "Math":[row[3],Student.checkGradeType(row[3])],
            "Science":[row[4],Student.checkGradeType(row[4])],
            "History": [row[5],Student.checkGradeType(row[5])]
            }
        return render_template('general.html', info_hash = info_hash, hour_list = priority_list, searched = True)

# student forms - incident / disciplinary
@app.route('/forms')
def forms():
    if not autho_login():
        return redirect("accessDenied")
    data = calls.getUploads()
    # check if there are any forms in the DB
    if data == None:
        return render_template('forms_component.html')
    # if not then iterate through the data by rows
    else:
        # get the BLOB data from rows
        # convert from binary to string representation
        # get the filename, then store in local folder
        doc_list = []
        for row in data:
            ext_to_save = 'static/docs/'+row[0]
            filename = row[0]
            file_blob = row[1]
            imgdata = base64.b64decode(file_blob)
            with open(ext_to_save, 'wb') as f:
                f.write(imgdata)
            doc_list.append(filename)
        return render_template('form_component.html', images=doc_list)
    return render_template('form_component.html')

# student records - grades
@app.route('/records')
def students():
    if not autho_login():
        return redirect('accessDenied')
    data = calls.getStudents()
    student_list = []
    # populate the student_info dictionary with the student's information
    # store student_info into the student_list
    for rows in data:
        student_info = {}
        print(rows)
        student_info['student_teacher_id'] = rows[1]
        student_info['student_name'] = rows[0]
        student_info['student_teacher'] = calls.getTeacher(rows[1])
        student_info['student_english'] = rows[2]
        student_info['student_math'] = rows[3]
        student_info['student_science'] = rows[4]
        student_info['student_history'] = rows[5]
        student_info['student_id'] = rows[6]
        student_list.append(student_info)
    # return to table template, and pass in list
    return render_template('basic_table.html', list=student_list)
# student info page where their grades can be modified by teacher
@app.route('/student/information', methods=['GET'])
def studentForm():
    if not autho_login():
        return redirect(url_for('denied'))
    else:
        student_name = request.args.get('student_name')
        teacher_id = request.args.get('autho_id')
        student_id = request.args.get('student_id')
        student_grades = calls.getStudentGrades(student_id)
        student_info = calls.getStudentInfo(student_id)
        return render_template('studentinfo.html', student=student_name, grades=student_grades, student_info=student_info, teacher_id=teacher_id)
# ACTIONS------------------------------------------------------------------
# upload form submissions
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    # init date object, get date, get filename
    # convert the file to blob
    # execute query to upload image into DB
    # commit the execution
    # update activity log
    calls.updateActivityLog('2', 'blank',session['id'],session['fullname'])
    date_today = date.today()
    file = request.files['filetoupload']
    FILENAME = file.filename
    BLOB = base64.b64encode(file.read())
    DATE_TO_STORE = date_today.strftime("%b-%d-%Y")
    calls.submitForm(FILENAME,BLOB,DATE_TO_STORE)
    return redirect(url_for('forms'))

# gets the data from form, and updates it into MySQL
@app.route('/student/update/grades', methods=['POST'])
def updateGrade():
    student_id = request.form.get('student_id')
    math = request.form.get('math-class')
    eng = request.form.get('eng-class')
    ss = request.form.get('ss-class')
    sci = request.form.get('sci-class')
    student_class = request.form.get('class')
    student_fullname = calls.getStudentName(student_id)
    calls.updateActivityLog('1', student_fullname) #updates the activity log to the DB when the student's grade is being modified
    calls.submitStudentGrade(eng,math,sci,ss,student_id)
    return redirect(url_for('students'))
# map to expand the forms from form_component
@app.route('/docs/form', methods=['GET'])
def renderDoc():
    image_url = request.args.get('imageUrl')
    return render_template('showdoc.html', image_url=image_url)
# AUTHORIZATIONS-------------------------------------------------------------------
# block any type of unauthorized bypass and then redirecting to log in page
@app.route('/accessDenied')
def denied():
    return render_template('index.html', error=True, message="Please log in!")

@app.route('/login', methods=['POST'])
def login():
    data = calls.getUserData() # get all the user data from the database
    print(data)
    err_msg = "Invalid username or password!"
    # get user and password from the web page form
    username = request.form['username']
    password = request.form['password']
    # iterate through the rows
    # check if username exist, if yes, verify the pass
    # if fail then return to main, with error message
    for row in data:
        if row[2] == username:
            if sha256_crypt.verify(password, row[3]):
                full_name = row[0]+' '+row[1]
                session['fullname'] = full_name  # save user's name in session
                session['id'] = row[4]
                return redirect('dashboard')
            else:
                return render_template('index.html', error=True, message=err_msg)
    return render_template('index.html', error=True, message=err_msg)

@app.route('/logout')
def logout():
    session['fullname'] = None
    session['id'] = None
    return redirect('/')

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
