import app
from datetime import date
#APIIIII REQUESTS-------------------
# get the admins from the db
def getAdminUser(user_name):
    cur = app.mysql.connection.cursor()
    query = f'SELECT * from admin where username = "{user_name}";'
    cur.execute(query)
    try:
        data = cur.fetchall()[0]
    except IndexError:
        return 'error'
    return data
def getStudentDataRequest(id):
    cur = app.mysql.connection.cursor()
    query = f'SELECT * from student where id_number = {id};'
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data
def getTeacherDataRequest(id):
    cur = app.mysql.connection.cursor()
    query = f'SELECT * from staff where staffID = {id};'
    cur.execute(query)
    data = cur.fetchall()
    return data
#func to get all teachers
def getAllTeachers():
    cur = app.mysql.connection.cursor()
    cur.execute("SELECT * from staff;")
    data = cur.fetchall()
    cur.close()
    return data
def getAllStudents(): #func to get all students
    cur = app.mysql.connection.cursor()
    cur.execute("SELECT * from student;")
    data = cur.fetchall()
    cur.close()
    return data
def getApiKey(key): # get the api key from the database that is passed in by the user
    cur = app.mysql.connection.cursor()
    cur.execute(f"SELECT * from api_user where api_key = '{key}';")
    data = cur.fetchall()
    cur.close()
    if data: # if db returns data then return true, if not (no api key by the given was found) return false
        return True
    else:
        return False
def saveApiKey(username,key):
    cur = app.mysql.connection.cursor()
    cur.execute(f"INSERT into api_user(username,api_key) VALUES('{username}','{key}');")
    app.mysql.connection.commit()
    cur.close()

# API END -----------------------------------------
# get user data from the DATABASE
def getUserData():
    # get cursor object for sql connection
    cur = app.mysql.connection.cursor()
    query = 'SELECT * FROM user;'
    cur.execute(query)
    # fetch all of user data from the DBget
    data = cur.fetchall()
    cur.close()
    return data

def submitStudentGrade(eng,math,sci,ss,student_id): #update the student's grade
    cur = app.mysql.connection.cursor()
    query = f'UPDATE student SET english={eng},math={math},science={sci},history={ss} WHERE id_number = {student_id}'
    cur.execute(query)
    app.mysql.connection.commit()
    cur.close()
#commit an upload for form submitted
def submitForm(FILENAME,BLOB,DATE_TO_STORE):
    cur = app.mysql.connection.cursor()
    cur.execute('INSERT INTO uploads(filename,upload,date,type) values(%s,%s,%s,%s)',
                (FILENAME, (BLOB,), DATE_TO_STORE, '1'))
    app.mysql.connection.commit()
    cur.close()

# get all of the students
def getStudents():
    cur = app.mysql.connection.cursor()
    query = 'SELECT * from student'
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data
# get all the of the form uploads from db
def getUploads():
    cur = app.mysql.connection.cursor()
    query = 'SELECT * FROM uploads;'
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

# func to return a list of the activity logdesc
def getActivityLogList():
    cur = app.mysql.connection.cursor()
    query = 'SELECT * from log'
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data
# func to get a specific student's grades, passing in id as reference
def getStudentGrades(st_id):
    cur = app.mysql.connection.cursor()
    query = f'SELECT * from student where id_number ={st_id};'
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    if not data: # if the data is empty (meaning that the student doesn't exist, then return None)
        return None
    return data[0]
# func to get student_info
def getStudentInfo(st_id):
    cur = app.mysql.connection.cursor()
    query = f'SELECT * from student_info WHERE id_number ={st_id};'
    cur.execute(query)
    data = cur.fetchall()
    return data[0]
# func to get specfic student's full name
def getStudentName(st_id):
    cur = app.mysql.connection.cursor()
    query = f'SELECT * from student where id_number = {st_id};'
    cur.execute(query)
    data = cur.fetchall()
    return data[0][0]
# func to get teacher's name using teacher id foreign key as reference
def getTeacher(teacher_id):
    cur = app.mysql.connection.cursor()
    query = f'SELECT * from staff where staffID = {teacher_id};'
    cur.execute(query)
    data = cur.fetchall()
    return data[0][0]
# func to create a log of user's activity, passing in the type, student, and the session [id] of the user
def updateActivityLog(type, student,teacher_id = '',teacher_name = ''):
    cur = app.mysql.connection.cursor()
    current_day = date.today()
    if type == '1':
        des = f'Grade has been updated for {student}'
    elif type == '2':
        des = f'A disciplinary/incident form has been submitted. Please take notice! by-{teacher_name}'
    query = f"INSERT into log(teacher,activity_description,date,type) values('{teacher_id}','{des}','{current_day}','{type}');"
    cur.execute(query)
    app.mysql.connection.commit()
    cur.close()
