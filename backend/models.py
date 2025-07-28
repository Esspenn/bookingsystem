from datetime import datetime
import uuid
from typing import List
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID

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