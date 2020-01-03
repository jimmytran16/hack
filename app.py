from flask import Flask, render_template, flash, redirect, url_for, session, request, logging

#init flask
app = Flask(__name__)

#Mapping for URLS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

#student behavoir
@app.route('/behavior')
def general():
    return render_template('general.html')

#student forms - incident / behavior
@app.route('/forms')
def forms():
    return render_template('form_component.html')

#student records - grades 
@app.route('/students')
def students():
    return render_template('basic_table.html')

@app.route('/logout')
def logout():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)


