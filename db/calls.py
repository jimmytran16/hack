import app

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
# func to create a log of user's activity
def updateActivityLog(type, student):
    cur = app.mysql.connection.cursor()
    current_day = date.today()
    if type == '1':
        des = f'Grade has been updated for {student}'
    elif type == '2':
        des = f'A disciplinary/incident form has been submitted. Please take notice! by-{session["fullname"]}'
    query = f"INSERT into log(teacher,activity_description,date,type) values('{session['id']}','{des}','{current_day}','{type}');"
    cur.execute(query)
    app.mysql.connection.commit()
    cur.close()
