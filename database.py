import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",   # XAMPP mein default password khaali hota hai
    database="mobile_shop"
)
cursor = db.cursor()