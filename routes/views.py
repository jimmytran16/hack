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
