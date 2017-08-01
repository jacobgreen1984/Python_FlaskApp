# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 15:33:28 2017

@author: jacob
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://jacobgreen:hyjod1001@localhost/dataset"
db = SQLAlchemy(app)


class post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(20000))

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return '<post %r>' % self.title
    
    
class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)

    def __init__(self, count):
        self.count = count

    def __repr__(self):
        return '<visit %r>' % self.count
    
    
    
    




    