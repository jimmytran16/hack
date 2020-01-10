from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
#sha256_crpyt for verifying encrypted passswords
from passlib.hash import sha256_crypt
#mysql db module
from flask_mysqldb import MySQL

#init flask
app = Flask(__name__)
#set up MySQL crudentials 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'bhcc'
app.config['MYSQL_DB'] = 'HHDB'

mysql = MySQL(app)

@app.route('/login',methods=['POST'])
def login():
    #get cursor object for sql connection
    cur = mysql.connection.cursor()
    query = 'SELECT * FROM user;'
    cur.execute(query)
    #fetch all of user data from the DB
    data = cur.fetchall()
    cur.close()
    err_msg = "The username or password you've entered doesn't match any account. Please try again!"
    #get user/pass from index form
    username = request.form['username']
    password = request.form['password']
    # iterate through the rows 
    # check if username exist, if yes, verify the pass
    # if fail then return to main, with error message
    for row in data:
        if row[2] == username:
            if sha256_crypt.verify(password,row[3]):
                full_name = row[0]+' '+row[1]
                return render_template('dashboard.html',error=False, name = full_name)
            else:
                return render_template('index.html',error = True, message = err_msg)
    return render_template('index.html',error=True, message = err_msg)

#Mapping for URLS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

#student behavoir chart
@app.route('/behavior')
def general():
    return render_template('general.html')

#student forms - incident / behavior
@app.route('/forms')
def forms():
    return render_template('form_component.html')

#student records - grades 

@app.route('/records')
def students():
    cur = mysql.connection.cursor()
    query = 'SELECT * from student'
    cur.execute(query)
    data = cur.fetchall()
    student_list =[]
    #populate the student_info dictionary with the student's information
    #store student_info into the student_list 
    for rows in data:
        student_info ={}
        print(rows)
        student_info['student_name'] = rows[0];
        student_info['student_teacher'] = rows[1];
        student_info['student_english'] = rows[2];
        student_info['student_math'] = rows[3];
        student_info['student_science'] = rows[4];
        student_info['student_history'] = rows[5];
        student_info['student_id'] = rows[6];
        student_list.append(student_info)        
    #return to table template, and pass in list
    cur.close()
    return render_template('basic_table.html', list = student_list)

@app.route('/logout')
def logout():
    return render_template('index.html')


if __name__ == '__main__':
    app.secret_key = '1232131G/21321312sw11'
    app.run(debug=True)
