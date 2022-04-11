"""
Thrilld.
Created by Matan Yosef
Version 1.0
Copyright ©2019
config.py
- This file is is here to provide all the configurations required by the site.
"""

#---------------------------IMPORTS + VARIABLE(S)-------------------------------
import os
basedir = os.path.abspath(os.path.dirname(__file__)) #creates a new path of where the file exits and stores it in the variable basedir.
#-------------------------------------------------------------------------------


class Config(object):
	SECRET_KEY = '93a4b8854409a2e668ae476f6a63a8a5' #allows Flask to encrypt the site edit access
	SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "thrilld-site.db")# The SQL path w.r.t root of the app (hence 'basedir').
	SQLALCHEMY_TRACK_MODIFICATIONS = False #Turns off unused warning notifcations about a disspearing item in the package.
