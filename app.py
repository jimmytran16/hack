from flask import Flask, render_template, flash, redirect, url_for, session, request, logging

#init flask
app = Flask(__name__)

#Mapping for URLS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html',dash=True)

#student behavoir
@app.route('/behavior')
def general():
    return render_template('general.html',general=True)

#student forms - incident / behavior
@app.route('/forms')
def forms():
    return render_template('form_component.html',form=True)

#student records - grades 
@app.route('/records')
def students():
    return render_template('basic_table.html',basic=True)

@app.route('/logout')
def logout():
    return render_template('index.html')

@app.route('/login',methods=['POST'])
def login():
    # get the username and password from the field
    # authenticate the username and password 
    # if doesn't exist, return to index and send error message
    fixed_name = 'Jimmy Tran'
    fixed_user = 'jimmytran16'
    fixed_pass = '68016801'
    username = request.form['username']
    password = request.form['password']
    error = "The username or password you've entered doesn't match any account. Please try again!"
    if username == fixed_user:
        if password == fixed_pass:
            return render_template('dashboard.html', error=False, name = fixed_name)
    else:
        return render_template('index.html', error = True, message = error)
    
    return render_template('index.html', error = True, message = error)

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)


