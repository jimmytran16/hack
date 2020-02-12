from flask import Flask, render_template, redirect, url_for, session, request, logging
# sha256_crpyt for verifying encrypted passswords
from passlib.hash import sha256_crypt
# mysql db module
from flask_mysqldb import MySQL
from datetime import date
# for encoding and decoding images
import base64
from student_pkg.Student import Student

# init flask
app = Flask(__name__)
app.secret_key = '1232131G/21321312sw11'

# set up MySQL crudentials
app.config['MYSQL_HOST'] = 'wftuqljwesiffol6.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'ghgsii8c22l1c8lv'
app.config['MYSQL_PASSWORD'] = 'pd1bp88tw2japxpn'
app.config['MYSQL_DB'] = 'wgrehtsdcu9l1f5z'
# init a mysql object
mysql = MySQL(app)
# -----------------------------------
# Mapping for URLS
@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/dashboard')
def dashboard():
    if not autho_login():
        return redirect(url_for("denied"))
    activity_log = getActivityLogList()  # get activity log from db
    list = []
    for i in activity_log:
        list.append(i)
    list.reverse()
    print(activity_log)
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
        row = getStudentGrades(student_id)
        if row == None:
            return render_template('general.html', error = 'Student does not exist!')
        # will pass in the student data and teacher to the getHours() function to determine study hour requirements
        st_teacher = getTeacher(row[1])
        priority_list = Student.getStudentHours(row,st_teacher)
        print(row)
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
    cur = mysql.connection.cursor()
    query = 'SELECT * FROM uploads;'
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
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
        print(doc_list)
        return render_template('form_component.html', images=doc_list)
    return render_template('form_component.html')

# student records - grades
@app.route('/records')
def students():
    if not autho_login():
        return redirect('accessDenied')
    cur = mysql.connection.cursor()
    query = 'SELECT * from student'
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    student_list = []
    # populate the student_info dictionary with the student's information
    # store student_info into the student_list
    for rows in data:
        student_info = {}
        print(rows)
        student_info['student_teacher_id'] = rows[1]
        student_info['student_name'] = rows[0]
        student_info['student_teacher'] = getTeacher(rows[1])
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
        student_grades = getStudentGrades(student_id)
        student_info = getStudentInfo(student_id)
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
    updateActivityLog('2', 'blank')
    date_today = date.today()
    file = request.files['filetoupload']
    FILENAME = file.filename
    BLOB = base64.b64encode(file.read())
    cur = mysql.connection.cursor()
    DATE_TO_STORE = date_today.strftime("%b-%d-%Y")
    cur.execute('INSERT INTO uploads(filename,upload,date,type) values(%s,%s,%s,%s)',
                (FILENAME, (BLOB,), DATE_TO_STORE, '1'))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('forms'))

# gets the data from form, and updates it into MySQL
@app.route('/student/update/grades', methods=['POST'])
def updateGrade():
    cur = mysql.connection.cursor()
    student_id = request.form.get('student_id')
    math = request.form.get('math-class')
    eng = request.form.get('eng-class')
    ss = request.form.get('ss-class')
    sci = request.form.get('sci-class')
    student_class = request.form.get('class')
    student_fullname = getStudentName(student_id)
    updateActivityLog('1', student_fullname)
    query = f'UPDATE student SET english={eng},math={math},science={sci},history={ss} WHERE id_number = {student_id}'
    cur.execute(query)
    mysql.connection.commit()
    cur.close()
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
    # get cursor object for sql connection
    cur = mysql.connection.cursor()
    query = 'SELECT * FROM user;'
    cur.execute(query)
    # fetch all of user data from the DBget
    data = cur.fetchall()
    cur.close()
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

# function to determine if there is a user logged in
def autho_login():
    # session variable 'fullname' is not assigned when user first runs the app
    if not session.get('fullname'):
        return False
    elif session['fullname'] != None:
        return True
    else:
        return False

# func to get a specific student's grades, passing in id as reference
def getStudentGrades(st_id):
    cur = mysql.connection.cursor()
    query = f'SELECT * from student where id_number ={st_id};'
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    if not data: # if the data is empty (meaning that the student doesn't exist, then return None)
        return None
    return data[0]
# func to get student_info
def getStudentInfo(st_id):
    cur = mysql.connection.cursor()
    query = f'SELECT * from student_info WHERE id_number ={st_id};'
    cur.execute(query)
    data = cur.fetchall()
    return data[0]
# func to get specfic student's full name
def getStudentName(st_id):
    cur = mysql.connection.cursor()
    query = f'SELECT * from student where id_number = {st_id};'
    cur.execute(query)
    data = cur.fetchall()
    return data[0][0]
# func to get teacher's name using teacher id foreign key as reference
def getTeacher(teacher_id):
    cur = mysql.connection.cursor()
    query = f'SELECT * from staff where staffID = {teacher_id};'
    cur.execute(query)
    data = cur.fetchall()
    return data[0][0]
# func to create a log of user's activity
def updateActivityLog(type, student):
    cur = mysql.connection.cursor()
    current_day = date.today()
    if type == '1':
        des = f'Grade has been updated for {student}'
    elif type == '2':
        des = f'A disciplinary/incident form has been submitted. Please take notice! by-{session["fullname"]}'
    query = f"INSERT into log(teacher,activity_description,date,type) values('{session['id']}','{des}','{current_day}','{type}');"
    cur.execute(query)
    mysql.connection.commit()
    cur.close()
# func to return a list of the activity logdesc
def getActivityLogList():
    cur = mysql.connection.cursor()
    query = 'SELECT * from log'
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data


# condition to run the app.py
if __name__ == '__main__':
    app.run(debug=True)
