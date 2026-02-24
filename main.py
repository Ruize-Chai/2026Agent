import hashlib
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from Front.login import verify_login
from Front.register import read_user_table, write_user_table

#####PATHS########
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONT_DIR = os.path.join(PROJECT_DIR, "Front")
REGISTER_HTML_PATH = os.path.join(FRONT_DIR, "register.html")
LOGIN_HTML_PATH = os.path.join(FRONT_DIR, "login.html")
#####PATHS########

#####PAYLOADS######
class RegisterPayload(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class LoginPayload(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)
#####PAYLOADS######

#####HASH FUNC######
def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
#####HASH FUNC######

######FAST API CREATE FUNC#######
def create_app() -> FastAPI:
    app = FastAPI()
    
	#GET主页面 （暂时为注册页)
    @app.get("/")
    async def register_page() -> FileResponse:
        return FileResponse(REGISTER_HTML_PATH)
    
	#GET登录页面 
    @app.get("/login")
    async def login_page() -> FileResponse:
        return FileResponse(LOGIN_HTML_PATH)
    
	#GET HEALTH
    @app.get("/health")
    async def health_check() -> dict[str, bool]:
        return {"ok": True}
    
	#POST 注册 RegisterPayload
    @app.post("/register")
    async def register_user(payload: RegisterPayload) -> dict[str, bool]:
        rows = await read_user_table()
        username_hash = hash_value(payload.username.strip().lower())

        for row in rows:
            if row.get("username_hash") == username_hash:
                raise HTTPException(status_code=409, detail="username already exists")

        rows.append(
            {
                "username": payload.username,
                "password_hash": hash_value(payload.password),
                "username_hash": username_hash,
            }
        )

        await write_user_table(rows)
        return {"ok": True}
    
	#POST 登录 LoginPayload
    @app.post("/login")
    async def login_user(payload: LoginPayload) -> dict[str, bool]:
        is_valid = await verify_login(payload.username, payload.password)
        if not is_valid:
            raise HTTPException(status_code=401, detail="invalid username or password")
        return {"ok": True}

    return app
######FAST API CREATE FUNC#######

####main:app####
app = create_app()
####main:app####
