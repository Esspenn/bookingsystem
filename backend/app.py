from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi_users import FastAPIUsers # Hvis du ikke har denne
from fastapi_users.authentication import AuthenticationBackend # Hvis du ikke har denne
from fastapi_users.router import get_register_router
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTableUUID,
)
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, sessionmaker
from sqlalchemy.orm import Mapped
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
from typing import List
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse

load_dotenv()
app = FastAPI(title="Bookingsystem API")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession)

# Jinja2 setup
current_dir = os.path.dirname(os.path.abspath(__file__))
main_templates_dir = os.path.join(current_dir, '..', 'templates')
jinja_env = Environment(
    loader=FileSystemLoader([main_templates_dir])
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"
    
    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    reservations: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="user")

class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass


class Item(Base):
    __tablename__ = "items"
    
    ItemID: Mapped[int] = mapped_column(primary_key=True)
    ItemType: Mapped[str] = mapped_column(String)
    Description: Mapped[str] = mapped_column(Text, nullable=True)
    Status: Mapped[bool] = mapped_column(Boolean, default=True)
    
    reservations: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="item")

class Reservation(Base):
    __tablename__ = "reservations"
    
    ReservationID: Mapped[int] = mapped_column(primary_key=True)
    StartTime: Mapped[datetime] = mapped_column(DateTime)
    EndTime: Mapped[datetime] = mapped_column(DateTime)
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True)
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    UserID: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    ItemID: Mapped[int] = mapped_column(ForeignKey("items.ItemID"))
    
    user: Mapped["User"] = relationship("User", back_populates="reservations")
    item: Mapped["Item"] = relationship("Item", back_populates="reservations")

# Database dependency
async def get_db():
    async with async_session_maker() as session:
        yield session

# API endpoints
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    template = jinja_env.get_template("index.html")
    html_content = template.render(request=request)
    return html_content 

@app.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()

@app.get("/items/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.ItemID == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item