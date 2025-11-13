from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


SECRET_KEY = "testeapi"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


usuario_teste = {
    "username": "admin",
    "password": "1234"
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def autenticar_usuario(username: str, password: str):
    if username == usuario_teste["username"] and password == usuario_teste["password"]:
        return True
    return False


def criar_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
