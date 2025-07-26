import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

load_dotenv()
app = FastAPI()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

class Item(BaseModel):
    ItemType: str
    Description: str | None = None
    Status: bool

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