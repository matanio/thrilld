"""
Thrilld.
Created by Matan Yosef
Version 1.0
Copyright ©2019
__init__.py
- This file 'executes and defines' what parts of the package gets exposed.
"""

#---------------------------------ALL IMPORTS-----------------------------------
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy #imports the database handling module
from flask_bcrypt import Bcrypt #imports a hashing module flask has built in for passwords.
from flask_login import LoginManager #imports Flasks login system
#-------------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'fail'

from app import routes, models

#for live, delete this line
app.run(port=8080, debug=True)
