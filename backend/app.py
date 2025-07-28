from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, sessionmaker
from sqlalchemy.orm import Mapped
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
from typing import List

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
    
    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    reservations: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="user")

class Item(Base):
    __tablename__ = "items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    
    reservations: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="item")

class Reservation(Base):
    __tablename__ = "reservations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    
    user: Mapped["User"] = relationship("User", back_populates="reservations")
    item: Mapped["Item"] = relationship("Item", back_populates="reservations")

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
