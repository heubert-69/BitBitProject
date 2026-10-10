
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.db.session import DbSession
from src.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from src.services.auth_service import (
    EmailOrUsernameTaken,
    InvalidCredentials,
    authenticate_user,
    register_user,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegister,
    db: DbSession,
):
    try:
        return await register_user(db, data)
    except EmailOrUsernameTaken:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username is already registered",
        ) from None


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    db: DbSession,
):
    try:
        token = await authenticate_user(
            db,
            data.email,
            data.password,
        )
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    return TokenResponse(access_token=token)
