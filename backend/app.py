import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

class Item(BaseModel):
    ItemType: str
    Description: str | None = None
    Status: bool

class User(BaseModel):
    UserName: str
    Email: str
    Password: str

class Reservation(BaseModel):
    ReservationDate: str
    ReservationTime: str
    ReservationStatus: bool

def get_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_DATABASE,
            user=DB_USER,
            password=DB_PASSWORD
        )
        if conn.is_connected():
            yield conn  
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.get("/items/")
async def get_all_items(conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Items")
        items = cursor.fetchall()
        return {"items": items}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()

@app.get("/items/{item_id}")
async def get_item(item_id: int, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Items WHERE ItemID = %s", (item_id,))
        item = cursor.fetchone()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"item": item}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()

@app.post("/items/")
async def create_item(item: Item, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO Items (ItemType, Description, Status) VALUES (%s, %s, %s)"
        val = (item.ItemType, item.Description, item.Status)
        cursor.execute(sql, val)
        conn.commit()
        
        new_item_id = cursor.lastrowid
        return {"message": "Item created successfully", "item_id": new_item_id}
    except Error as e:
        conn.rollback() 
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()


@app.get("/Users/")
async def get_all_users(conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()
        return {"users": users}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
    
@app.get("/Users/{user_id}")
async def get_user(user_id: int, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE UserID = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user": user}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
    
@app.post("/Users/")
async def create_user(user: User, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO Users (UserName, Email, Password) VALUES (%s, %s, %s)"
        val = (user.UserName, user.Email, user.Password)
        cursor.execute(sql, val)
        conn.commit()
        new_user_id = cursor.lastrowid
        return {"message": "User created successfully", "user_id": new_user_id}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()

@app.get("/Reservations/")
async def get_all_reservations(conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Reservations")
        reservations = cursor.fetchall()
        return {"reservations": reservations}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
    
@app.get("/Reservations/{reservation_id}")
async def get_reservation(reservation_id: int, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Reservations WHERE ReservationID = %s", (reservation_id,))
        reservation = cursor.fetchone()
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return {"reservation": reservation}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
    
@app.post("/Reservations/")
async def create_reservation(reservation: Reservation, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO Reservations (ReservationDate, ReservationTime, ReservationStatus) VALUES (%s, %s, %s)"
        val = (reservation.ReservationDate, reservation.ReservationTime, reservation.ReservationStatus)
        cursor.execute(sql, val)
        conn.commit()
        new_reservation_id = cursor.lastrowid
        return {"message": "Reservation created successfully", "reservation_id": new_reservation_id}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()