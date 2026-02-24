import hashlib

from Front.register import read_user_table

#####HASH VALUE#####
def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
#####HASH VALUE#####

#检测更新消息
async def verify_login(username: str, password: str) -> bool:
    rows = await read_user_table()
    username_hash = hash_value(username.strip().lower())
    password_hash = hash_value(password)

    for row in rows:
        if row.get("username_hash") == username_hash:
            return row.get("password_hash") == password_hash

    return False
