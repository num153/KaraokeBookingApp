from flask import Flask
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
# cấu hình sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/karadb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'CNPM_KARAOKE'
db=SQLAlchemy(app=app)