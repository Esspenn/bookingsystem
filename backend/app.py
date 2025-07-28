from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, sessionmaker
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

load_dotenv()
app = FastAPI(title="Bookingsystem API")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"
    
    id = mapped_column(default=uuid.uuid4, primary_key=True)
    email = mapped_column(String, unique=True, index=True)
    hashed_password = mapped_column(String)
    is_active = mapped_column(Boolean, default=True)
    is_superuser = mapped_column(Boolean, default=False)
    is_verified = mapped_column(Boolean, default=False)
    
    reservations = relationship("Reservation", back_populates="user")

class Item(Base):
    __tablename__ = "items"
    
    id = mapped_column(primary_key=True)
    name = mapped_column(String)
    description = mapped_column(Text, nullable=True)
    available = mapped_column(Boolean, default=True)
    
    reservations = relationship("Reservation", back_populates="item")

class Reservation(Base):
    __tablename__ = "reservations"
    
    id = mapped_column(primary_key=True)
    start_time = mapped_column(DateTime)
    end_time = mapped_column(DateTime)
    is_active = mapped_column(Boolean, default=True)
    created_at = mapped_column(DateTime, server_default=func.now())
    
    user_id = mapped_column(ForeignKey("user.id"))
    item_id = mapped_column(ForeignKey("items.id"))
    
    user = relationship("User", back_populates="reservations")
    item = relationship("Item", back_populates="reservations")

# Database dependency
async def get_db():
    async with async_session_maker() as session:
        yield session

# API endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Bookingsystem API!"}

@app.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()

@app.get("/items/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
