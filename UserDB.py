import sqlite3  
  
con = sqlite3.connect("user.db")  
print("Database opened successfully")  
  
con.execute("create table Users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")  
  
print("Table created successfully")  
  
con.close()  