import os
import requests
import json

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://jxzosipnydmabf:902838b9e9d4bba2bab657bd563fa688b5e8ca54169194aa4b879cb31378370a@ec2-50-17-21-170.compute-1.amazonaws.com:5432/ddvff1uqkmtiop")

db = scoped_session(sessionmaker(bind=engine))


@app.route("/index", methods=["GET","POST"])
def index():
    username = session.get("username")
    msg=" "
    session["books"]=[]
    if  request.method=="POST":
        msg=("")
        book = request.form.get("book")
        data = db.execute("SELECT * FROM books WHERE title iLIKE '%"+book+"%'  OR author iLIKE '%"+book+"%' OR year iLIKE '%"+book+"%' OR isbn iLIKE '%"+book+"%'").fetchall() 

        for i in data:
            session["books"].append(i)
        if len(session["books"])==0:
            msg="Sorry! Book not found"
    return render_template("index.html",data=session["books"],msg=msg, username=username)




@app .route("/", methods = ["GET", "POST"])
def login():
    log_in_message=" "
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        usernamelogin=request.form.get("usernamelogin")
        passwordlogin=request.form.get("passwordlogin")
        if usernamelogin == None:
            data = db.execute("SELECT username From login").fetchall()
            for i in range(len(data)):
                if data[i]["username"]==username:
                    log_in_message="Sorry. Username already exists!"
                    return render_template("login.html",log_in_message=log_in_message)
            db.execute("INSERT INTO login(username,password)VALUES(:username , :password)",{"username":username, "password":password})
            db.commit()
            log_in_message="SUCESS. You can log in" 
        else:
            data=db.execute("SELECT * FROM login WHERE username = :uname",{"uname":usernamelogin}).fetchone()
            if data !=None:
                if data.username == usernamelogin and data.password == passwordlogin:
                    session["username"]=usernamelogin
                    return redirect(url_for("index"))
                else:
                    log_in_message="Invalid username or password"
            else:
                log_in_message="Invalid username or password"
    return render_template("login.html",log_in_message=log_in_message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/open/<string:isbn>" , methods=["GET","POST"])
def open(isbn):
    username = session.get("username")
    session["review"]=[]
    mesg=""

    data=db.execute("SELECT * FROM books WHERE isbn=:x",{"x":isbn}).fetchone()
    url="https://www.goodreads.com/book/review_counts.json"
    params=dict(key='0Qkweiga4tKpCLWeCHm1MA',isbns=isbn)
    resp = requests.get(url=url,params=params)
    average_rating = resp.json()['books'][0]['average_rating']
    work_ratings_count = resp.json()['books'][0]['work_ratings_count']

    reviews = db.execute("SELECT * FROM review WHERE isbn=:y",{"y":isbn}).fetchall()
    for z in reviews:
        session['review'].append(z)
    another_review = db.execute("SELECT * FROM review WHERE isbn = :isbn AND username = :username", { "isbn": isbn, "username": username}).fetchone()
    if request.method == "POST" and another_review==None:
       Review = request.form.get("review")
       rating = request.form.get("Rate")
       data=db.execute("INSERT INTO review (isbn, username, rating, review) VALUES (:a,:b,:c,:d)",{"a":isbn,"b":username,"c":rating,"d":Review}) 
       db.commit()
    if request.method == "POST" and another_review!=None:
        mesg="You already gave a review"
    return render_template("open.html",data=data,  review=session["review"], average_rating=average_rating, work_ratings_count=work_ratings_count, username=username, mesg=mesg)


@app.route("/api/<string:isbn>")
def get_api(isbn):
    data=db.execute("SELECT * FROM books WHERE isbn=:x",{"x":isbn}).fetchone()
    url="https://www.goodreads.com/book/review_counts.json"
    params=dict(key='0Qkweiga4tKpCLWeCHm1MA',isbns=isbn)
    resp = requests.get(url=url,params=params)
    average_rating = resp.json()['books'][0]['average_rating']
    work_ratings_count = resp.json()['books'][0]['work_ratings_count']

    i = {
        "title": data.title,
        "author": data.author,
        "year": data.year,
        "isbn": isbn,
        "review_count": work_ratings_count,
        "average_score": average_rating
    }

    apibook = json.dumps(i)
    return render_template("api.json",api=apibook)
   

