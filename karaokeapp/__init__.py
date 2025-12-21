from flask import Flask
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
# cấu hình sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/labdb?charset=utf8mb4'


db=SQLAlchemy(app=app)