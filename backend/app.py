import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path


load_dotenv()
app = FastAPI()


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

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
    UserID: int
    ItemID: int
    ReservationDate: str
    ReservationTime: str
    ReservationStatus: bool



def get_db():
    """
    Dependency for å håndtere databaseforbindelser.
    Åpner en forbindelse for hver request og lukker den etterpå.
    """
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
        if 'conn' in locals() and conn.is_connected():
            conn.close()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    """
    Hovedsiden som viser en liste over gjenstander fra databasen.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ItemID, ItemType, Description, Status FROM Items")
        items = cursor.fetchall()
        
        return templates.TemplateResponse("index.html", {"request": request, "items": items})
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database eller mal-feil: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()


@app.get("/items/")
async def get_all_items(conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    """Henter alle gjenstander."""
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
    """Henter en spesifikk gjenstand basert på ID."""
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
    """Oppretter en ny gjenstand."""
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


@app.get("/reservations/")
async def get_all_reservations(conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    """Henter alle reservasjoner."""
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

@app.get("/reservations/{reservation_id}")
async def get_reservation(reservation_id: int, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    """Henter en spesifikk reservasjon basert på ID."""
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

@app.post("/reservations/")
async def create_reservation(reservation: Reservation, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    """Oppretter en ny reservasjon."""
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO Reservations (UserID, ItemID, ReservationDate, ReservationTime, ReservationStatus) VALUES (%s, %s, %s, %s, %s)"
        val = (reservation.UserID, reservation.ItemID, reservation.ReservationDate, reservation.ReservationTime, reservation.ReservationStatus)
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

@app.put("/reservations/{reservation_id}")
async def update_reservation(reservation_id: int, reservation: Reservation, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    """Oppdaterer en eksisterende reservasjon."""
    try:
        cursor = conn.cursor()
        sql = """
            UPDATE Reservations 
            SET UserID = %s, ItemID = %s, ReservationDate = %s, ReservationTime = %s, ReservationStatus = %s
            WHERE ReservationID = %s
        """
        val = (reservation.UserID, reservation.ItemID, reservation.ReservationDate, reservation.ReservationTime, reservation.ReservationStatus, reservation_id)
        cursor.execute(sql, val)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reservation not found to update")
        conn.commit()
        return {"message": f"Reservation {reservation_id} updated successfully"}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()

@app.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: int, conn: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    """Sletter en reservasjon."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Reservations WHERE ReservationID = %s", (reservation_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reservation not found to delete")
        conn.commit()
        return {"message": f"Reservation {reservation_id} deleted successfully"}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
