from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi_users import FastAPIUsers, schemas
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse
import uuid

from models import User, Item
from auth import auth_backend, get_user_manager
from db import get_db

app = FastAPI(title="Bookingsystem API")

# Jinja2 setup
current_dir = os.path.dirname(os.path.abspath(__file__))
main_templates_dir = os.path.join(current_dir, '..', 'templates')
jinja_env = Environment(
    loader=FileSystemLoader([main_templates_dir])
)

# FastAPIUsers setup
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass

# Legg til rutene for autentisering
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# Legg til rutene for registrering
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# API endpoints
current_active_user = fastapi_users.current_user(active=True)

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

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
