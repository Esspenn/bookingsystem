import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

app = FastAPI()

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWORD
    )

    if conn.is_connected():
        print("Connected to MySQL database")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users")
        result = cursor.fetchall()
        for row in result:
            print(row)

except Error as e:
    print(f"Error: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()


@app.get("/")
async def root():
    return {"message": "Velkommen til mitt FastAPI-reservasjonssystem!"}


@app.get("/users/") # Merk: slutt-slash er standard for å unngå omdirigering
async def get_users():
    conn = None # Initialiser conn til None
    cursor = None # Initialiser cursor til None
    try:
        conn = get_db_connection() # Hent en fersk kobling for denne forespørselen
        cursor = conn.cursor(dictionary=True) # dictionary=True er veldig nyttig her!
        cursor.execute("SELECT UserID, EmailAddress, CreationDate FROM Users")
        users = cursor.fetchall()
        return {"users": users} # Returner som ordbok for bedre JSON-format
    except HTTPException: # Fanger feil som kommer fra get_db_connection()
        raise
    except Error as e: # Fanger andre databasefeil
        print(f"Feil ved henting av brukere: {e}")
        raise HTTPException(status_code=500, detail="Error fetching users from database")
    finally:
        # Viktig: Lukk cursor og connection her!
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("MySQL-tilkoblingen er lukket for denne forespørselen.")