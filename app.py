from flask import Flask

# mysql db module
from flask_mysqldb import MySQL
import os

import config #comment OUT when deploying ----------------------------------------------------------------------------------!!
from db import calls
# init flask
app = Flask(__name__)
# app.secret_key = config.SEC_KEY
app.secret_key = os.environ.get('SEC_KEY')


# HEROKU DATABASE CONFIGS -- get the enviroment variables from the heroku server
app.config['MYSQL_HOST'] = os.environ.get('HOST_NAME')
app.config['MYSQL_USER'] = os.environ.get('DB_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASS')
app.config['MYSQL_DB'] = os.environ.get('DB_NAME')

# set up MySQL crudentials
# LOCAL DATABASE CONFIGS
# app.config['MYSQL_HOST'] = config.R_HOST_NAME
# app.config['MYSQL_USER'] = config.R_DB_USER
# app.config['MYSQL_PASSWORD'] = config.R_DB_PASS
# app.config['MYSQL_DB'] = config.R_DB_NAME

# init a mysql object
mysql = MySQL(app)
# -----------------------------------
from routes.views import * #import the app's views
from routes.views_api import * #import all the api views

# condition to run the app.py
if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=False)
