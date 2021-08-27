import sqlite3  
  
con = sqlite3.connect("gazemaster.db")  
print("Database opened successfully")  
  
con.execute("create table GazeData (name TEXT NOT NULL, time TEXT NOT NULL, date TEXT NOT NULL, average_attention TEXT NOT NULL, emotion TEXT NOT NULL, average_happiness TEXT NOT NULL)")  
  
print("Table created successfully")  
  
con.close() 