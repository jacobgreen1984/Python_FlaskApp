# -*- coding: utf-8 -*-
# https://stackoverflow.com/questions/19260067/sqlalchemy-engine-absolute-path-url-in-windows

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Markup, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import flask_whooshalchemy as wa 
import pymysql
import sqlite3
import markdown
import datetime
import os


#==============================================================================
# app configure
#==============================================================================
# set datetime
datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# sqlite config
DATABASE = 'C:/Users/jacob/Documents/myproject/db/database.db'
#DATABASE = '/home/jacobgreen1984/deploy/db/database.db'

pymysql.install_as_MySQLdb()
UPLOAD_FOLDER = "C:/Users/jacob/Documents/myproject/images"

app = Flask(__name__,template_folder="C:/Users/jacob/Documents/myproject/templates")

app.secret_key = 'some_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://jacobgreen:hyjod1001@localhost/dataset"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['WHOOSH_BASE'] = 'whoosh'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
#==============================================================================


#==============================================================================
# sqlite3
#==============================================================================
def connect_db():
    return sqlite3.connect(DATABASE)

def createTable(g):
    try: 
        sql = "CREATE TABLE if not exists posts(date TEXT, name TEXT, content TEXT)"
        g.db.execute(sql)
        g.db.commit()
    except Exception as err:
        print('error:', err)

@app.before_request
def before_request(): 
    g.db = connect_db()
    createTable(g)
    print("before request")

@app.teardown_request
def teardown_request(exception):
    g.db.close()
    print("end request")
#==============================================================================


#==============================================================================
# slqalchemy
#==============================================================================
class Post(db.Model):
    __searchable__ = ["title","content"]
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(20000))

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)

    def __init__(self):
        self.count = 0

wa.whoosh_index(app,Post)
#==============================================================================


#==============================================================================
# home(index)
#==============================================================================
def sidebar_data():
    recent=Post.query.order_by(
            Post.id.desc()
            ).limit(5).all()
    return recent

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    v = Visit.query.first()
    if not v:
        v = Visit()
        v.count += 1
        db.session.add(v)
    v.count +=1
    db.session.commit()
    
    pagination = Post.query.order_by(desc('id')).paginate(page, 5, False)
    posts = pagination.items
    recent = sidebar_data()
    return render_template('index.html',posts=posts,pagination=pagination,counter=v.count,recent=recent)
 

@app.route('/post/<id>')
def view(id):
    post = Post.query.filter_by(id=id).first()
    content = Markup(markdown.markdown(post.content))
    return render_template('view.html',post=post,content=content)

@app.route("/search")
def search(page=1):
    v = Visit.query.first()
    if not v:
        v = Visit()
        v.count += 1
        db.session.add(v)
    v.count +=1
    db.session.commit()
    
    pagination = Post.query.order_by(desc('id')).paginate(page, 5, False)
    posts = Post.query.whoosh_search(request.args.get("query")).all()
    recent = sidebar_data()
    return render_template("index.html",posts=posts,pagination=pagination,counter=v.count,recent=recent)

@app.route("/add",methods=["GET","POST"])
def add():
    if request.method == "POST":
        post=Post(title=request.form["title"],content=request.form["content"])
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template('add.html')

@app.route('/delete',methods = ['POST'])
def delete():
       Post.query.filter(Post.title == request.form['delete_title']).delete()
       db.session.commit()
       return redirect(url_for("index"))

@app.route('/add/<filename>')
def added_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
#==============================================================================


#==============================================================================
# about me 
#==============================================================================
@app.route("/about")
def aboutme():
    
    myetc = [
             u"2017 신한데이터시스템 인공지능 강사"
            ,u"2017 교보생명 머신러닝 강사"
            ,u"2017 웹케시 인공신경망 강사"
            ,u"2016 투이컨설팅 워너비 데이터 분석 강사"
            ,u"2017 국민대 빅데이터경영MBA 빅데이터프로젝트 멘토"
            ,u"2016 국민대 빅데이터경영MBA 빅데이터프로젝트 멘토"
            ]
    
    myproject = [
             u"2017 고객 세그먼테이션 소프트웨어 개발"
            ,u"2016 빅데이터 보험 레퍼런스 모델 (*고객 이탈예측 모형 개발, 고객 맞춤형 금융상품추천엔진 개발)"
            ,u"2016 맞춤형 기상기후 빅데이터 서비스 기반구축 (*살오징어 단위노력당 어획량 예측모형 고도화)"
            ,u"2016 데이터 기반 고객여정 분석 (*마케팅 전략수립을 위한 고객 군집화)"
            ,u"2015 맞춤형 기상기후 빅데이터 서비스 기반구축 (*살오징어 어획량 예측모형 개발)"
            ,u"2015 스마트 MICE 플랫폼 구축 (*전시회 부스추천엔진 개발)"
            ,u"2015 국가 특허전략 청사진 수립 (*특허평가모형 개발)"
            ,u"2014 NIA 미래전략컨설팅 (*농작물 단수 예측모형 개발)"
            ]
    
    return render_template('about.html', myproject = myproject, myetc=myetc)
#==============================================================================
 

#==============================================================================
# messages 
#==============================================================================
@app.route('/message',methods = ['POST', 'GET'])
def message():
   # GET
   if request.method=="GET":
       cur = g.db.execute("SELECT * FROM posts ORDER BY date DESC")
       fdata = cur.fetchall() 
       rows = [dict(date=date
                    ,name=name
                    ,content=content) for date,name,content in fdata]
       return render_template("message.html", rows = rows)
   # POST 
   else: 
       date = int(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
       name = request.form['name']
       content = request.form['content']
       sql  = "INSERT INTO posts (date,name,content) VALUES (?,?,?)"
       data = (date,name,content)
       g.db.execute(sql,data)
       g.db.commit()
       return redirect(url_for("message"))


@app.route('/delete2',methods = ['POST'])
def delete_date():
       g.db.execute("DELETE FROM posts WHERE date = ?",[request.form['date_to_delete']])
       g.db.commit()
       return redirect(url_for("message"))
#==============================================================================


#==============================================================================
# document
#==============================================================================
@app.route('/document')
def document():
    return render_template('document.html')
#==============================================================================


#==============================================================================
# project
#==============================================================================
@app.route("/project/kaggle")
def kaggle():
    return render_template('kaggle.html')

@app.route("/project/crawl")
def crawl():
    return render_template('crawl.html')

@app.route("/project/stock")
def stock():
    return render_template('stock.html')

@app.route("/project/book")
def book():
    return render_template('book.html')
#==============================================================================


#==============================================================================
# gallery
#==============================================================================
@app.route("/photo")
def photo():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload():
    target = UPLOAD_FOLDER
    print(target)
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))
        print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("Accept incoming file:", filename)
        print ("Save it to:", destination)
        upload.save(destination)

    # return send_from_directory("images", filename, as_attachment=True)
    return render_template("complete.html", image_name=filename)

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

@app.route('/gallery')
def get_gallery():
    image_names = sorted(os.listdir('./images'),reverse=True)
    print(image_names)
    return render_template("gallery.html", image_names=image_names)
#==============================================================================


if __name__=="__main__":
    app.run()














