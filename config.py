import os
from decouple import config
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
#require('dotenv').config()
# Enable debug mode.
DEBUG = True

# Connect to the database
SECRET_KEY2 = config("SECRET_KEY")
SECRET_USER = config("SECRET_USER")
SQLALCHEMY_DATABASE_URI = 'postgres://' + SECRET_USER + ':' + SECRET_KEY2 +'@localhost:5432/fyyur'
