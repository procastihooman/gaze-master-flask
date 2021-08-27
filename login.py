from flask import *  
import sqlite3  
  
app = Flask(__name__) 
app.secret_key = "Secret key"  
 
@app.route("/")  
def index():  
    return render_template("login.html");  
 
 
@app.route("/login",methods = ["POST","GET"])  
def login():  
    msg = "msg"  
    if request.method == "POST":  
        email = request.form["email"]  
        password = request.form["password"]  
        with sqlite3.connect("user.db") as con:  
            cur = con.cursor()  
            cur.execute("SELECT * FROM Users WHERE email = ? AND password = ?",(email, password)) 
            info = cur.fetchall()     
        if info:
            session['loggedin'] = True
            session['email'] = email
            session['name'] = info[2]
            return render_template('home.html')
        else:
            msg = 'Incorrect email / password !'
    return render_template('login.html', msg = msg) 
           