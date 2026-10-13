# Authenticatie met JWT

Inloggen met gebruikersnaam en wachtwoord, een JWT als toegangstoken en een `CurrentUser`-dependency voor beveiligde endpoints. De frontend stuurt het token al mee: `frontend/src/services/api.ts` leest `access_token` uit `localStorage`.

## Voorbereiding

Voeg toe aan `backend/requirements.txt` en installeer:

```text
pyjwt>=2.8.0
pwdlib[argon2]>=0.2.0
```

Voeg toe aan `Settings` in `backend/app/core/config.py`, en zet de waarde in `backend/.env`:

```python
SECRET_KEY: str
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
```

Genereer een sleutel met `openssl rand -hex 32`. Geef `SECRET_KEY` geen standaardwaarde in de code: de app hoort niet te starten zonder sleutel.

Het `User`-model heeft minimaal `email` (uniek), `hashed_password` en `is_active` nodig. Sla nooit het wachtwoord zelf op, en neem `hashed_password` niet op in het `Response`-schema.

## Wachtwoorden en tokens

```python
# backend/app/core/security.py
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": subject, "exp": expire}, settings.SECRET_KEY, algorithm=ALGORITHM)
```

## De huidige gebruiker als dependency

```python
# backend/app/api/deps.py (aanvulling)
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.security import ALGORITHM
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ongeldige of verlopen inloggegevens",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise credentials_error

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_error

    user = await db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
```

## Inloggen

```python
# backend/app/api/v1/endpoints/auth.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.deps import DbSession
from app.core.security import create_access_token, verify_password
from app.models.user import User

router = APIRouter()


@router.post("/token")
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Onjuist e-mailadres of wachtwoord")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}
```

Registreer de router in `router.py` met `prefix="/auth"`. Geef bij een mislukte login dezelfde melding voor een onbekend e-mailadres en een fout wachtwoord, zodat niet te achterhalen is welke adressen bestaan.

## Een endpoint beveiligen

```python
@router.get("/me", response_model=UserResponse)
async def read_me(current_user: CurrentUser):
    return current_user
```

Controleer bij records die van een gebruiker zijn ook het eigenaarschap, bijvoorbeeld `todo.user_id == current_user.id`. Ingelogd zijn is niet hetzelfde als dit record mogen zien.
