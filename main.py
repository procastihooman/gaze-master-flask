from flask import *  
import sqlite3
import cv2
import numpy as np
from numpy.lib.function_base import insert
from gaze_tracking import GazeTracker
from expression.src.predict import predict_emotion
import os
from datetime import datetime
from datetime import date
import time, threading  
  
app = Flask(__name__) 
app.secret_key = "Secret key"  
 
@app.route("/")  
def index():  
    return render_template("index.html");  
 
 
@app.route("/newacc",methods = ["POST","GET"])  
def newacc():  
    msg = ""  
    if request.method == "POST":  
        try:  
            name = request.form["name"]  
            email = request.form["email"]  
            password = request.form["password"]  
            with sqlite3.connect("user.db") as con:  
                cur = con.cursor()  
                cur.execute("INSERT into Users (name, email, password) values (?,?,?)",(name,email,password))  
                con.commit()  
                msg = "Hey! Your account is created successfully"  
        except:  
            con.rollback()  
            msg = "Oops! User already exists"  
        finally:  
            return render_template("index.html",msg = msg)  
            con.close()
    return render_template('index.html')
 
 
nameList = []
@app.route("/login",methods = ["POST","GET"])  
def login():
    if nameList:
        nameList.pop(0)

    msg = "" 
    if request.method == "POST":  
        email = request.form["email"]  
        password = request.form["password"]  
        with sqlite3.connect("user.db") as con:
            con.row_factory = sqlite3.Row   
            cur = con.cursor()  
            cur.execute("SELECT * FROM Users WHERE email = ? AND password = ?",(email, password)) 
            info = cur.fetchall() 
            cur.execute("SELECT name FROM Users WHERE email = ? AND password = ?",(email, password))
            row = cur.fetchone()
        if info:
            session['loggedin'] = True
            session['email'] = email
            name = str(row[0])
            nameList.append(name)
            return render_template('home.html',info=info)
        else:
            msg = 'Incorrect email or password!'
    return render_template('login.html', msg = msg) 

@app.route("/camera",methods = ["POST","GET"])  
def camera():
    name = nameList[0]
    os.environ['KMP_DUPLICATE_LIB_OK']='True'


    # Object creation for gaze tracking.
    gaze = GazeTracker()

    # Initializing the videoCapture object to infer the webcam stream.
    webcam = cv2.VideoCapture(0)
    moving_average = np.array([1])
    window = np.array([])


    # Defining constant that affect the way gaze tracking is done. 
    attention = 100.00
    count = 0
    SLIDER = 30
    THRESHOLD = 0.1


    happiness = np.array([1])
    while True:

        # Exctracting frame from the VideoCapture object.
        _, frame = webcam.read()
        count+= 1
        emotion, happy_score, face_found = predict_emotion(frame)
        # The frame to infer is sent to the infer function here. 
        gaze.infer(frame)
        
        window = np.append(window, int(gaze.is_center()))
        if face_found:
            happiness = np.append(happiness, happy_score) 

        # Here the moving average is calculated.
        if count%SLIDER == 0:
            moving_average = np.append(moving_average, int(np.mean(window[-SLIDER:])>THRESHOLD))
            attention = np.mean(moving_average)*100
            window = np.array([])

        # Displaying the attention metric and infered frame to the screen.    
        text = f'Average attention : {attention:.2f} % '
        if face_found:
            text2 = f'Emotion : {emotion}'
        else:
            text2 = 'No face found'
        text3 = f'Average happiness : {happiness.mean()*100:.2f} % '
        text4 = name
        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (147, 58, 31), 2)
        cv2.putText(frame, text2, (90, 120), cv2.FONT_HERSHEY_DUPLEX, 1, (147, 58, 31), 2)
        cv2.putText(frame, text3, (90, 180), cv2.FONT_HERSHEY_DUPLEX, 1, (147, 58, 31), 2)
        cv2.putText(frame, text4, (90, 220), cv2.FONT_HERSHEY_DUPLEX, 1, (147, 58, 31), 2)
        cv2.imshow("Demo", frame)
        if cv2.waitKey(1) == 27:
            break

        WAIT_TIME_SECONDS = 5

        #Check this tomorrow ek baar
        
        def func():
            cur = con.cursor() 
            cur.execute("INSERT INTO GazeData (name, time, date, average_attention, emotion, average_happiness) values (?,?,?,?,?,?)",(name, timenow,datenow,round(attention,2), emotion, round(happiness.mean()*100,2)))
            con.commit()

        with sqlite3.connect("gazemaster.db") as con: 
            timenow = datetime.now().strftime("%H:%M:%S")
            datenow = date.today()
            func()

    return render_template('home.html')


@app.route("/graph",methods = ["POST","GET"]) 
def graph():
    name = nameList[0]
    dateList = []
    con = sqlite3.connect('gazemaster.db')
    cur = con.cursor()
    cur.execute("SELECT COUNT(emotion) FROM GazeData WHERE name = ? GROUP BY emotion",[name])
    values = []
    for row in cur.fetchall():
        values.append(row[0])
        print(values)
    
    cur.execute("SELECT date,average_happiness,time FROM GazeData WHERE name = ?",[name])
    happiness = []
    date = []
    time = []
    for row in cur.fetchall():
        happiness.append(row[1])
        date.append(row[0])
        time.append(row[2])
    
    cur.execute("SELECT DISTINCT date FROM GazeData WHERE name=?",[name])
    for row in cur.fetchall():
        dateList.append(row[0])



    return render_template("graph.html", values = values, happiness = happiness, date= date,dateList = dateList)

@app.route("/dategraph",methods = ["POST","GET"]) 
def dategraph():
    if request.method == "POST":  
        date = request.form["date"]  
    con = sqlite3.connect('gazemaster.db')
    cur = con.cursor()
    
    cur.execute("SELECT average_happiness,time FROM GazeData WHERE date = ?",[date])
    happiness = []
    time = []
    for row in cur.fetchall():
        happiness.append(row[0])
        time.append(row[1])
    



    return render_template("dategraph.html", happiness = happiness, date= date,time=time)


  
 
  
if __name__ == "__main__":  
    app.run(debug = True)
    TEMPLATES_AUTO_RELOAD = True  