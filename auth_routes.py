from fastapi import APIRouter, Depends, status
from database import session,engine
from fastapi_jwt_auth import AuthJWT
from fastapi.exceptions import HTTPException
from schemas import SignUpModel, LoginForm
from models import Client
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import or_
import datetime

auth_router = APIRouter(
    prefix="/auth"
)

session = session(bind=engine)

@auth_router.get("/")
async def welcome(Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid Token"
        )
    return {
        "message": "This is a main page of authorization"
    }

@auth_router.post("/signup")
async def signup(user: SignUpModel):
    db_email = session.query(Client).filter(Client.email == user.email).first()
    if db_email is not None:
        return HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "User with that email already exists"
        )
    
    db_username = session.query(Client).filter(Client.username == user.username).first()
    if db_username is not None:
        return HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "User with that username already exists"
        )
    new_user = Client(
        username = user.username,
        email = user.email,
        password = generate_password_hash(user.password),
        is_staff = user.is_staff,
        is_active = user.is_active
    )
    session.add(new_user)
    session.commit()
    data = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "is_staff": new_user.is_staff
    }
    response = {
        "success": True,
        "status": status.HTTP_201_CREATED,
        "message": "User has been created successfully",
        "data": data
    }
    return response


@auth_router.post("/login")
async def login(data:LoginForm,Authorize: AuthJWT=Depends()):
    access_lifetime = datetime.timedelta(hours=96)
    refresh_lifetime = datetime.timedelta(days=90)
    db_user = session.query(Client).filter(
        or_(
            Client.username == data.username_or_email,
            Client.email == data.username_or_email
        )
    ).first()
    if db_user and check_password_hash(db_user.password, data.password):
        access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username,expires_time=refresh_lifetime)
        response = {
            "success": True,
            "access": access_token,
            "refresh": refresh_token,
            "data": "You have logged in successfully"
        }
        return response
    raise HTTPException(
        status_code = status.HTTP_400_BAD_REQUEST,
        detail = "Wrong credentials"
    )


@auth_router.post("/login/refresh")
async def refresh(Authorize: AuthJWT=Depends()):
    access_lifetime = datetime.timedelta(hours=96)
    try:
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()
        
        db_user = session.query(Client).filter(
            Client.username == current_user
        ).first()
        if db_user is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        new_access_token = Authorize.create_access_token(subject=db_user.username,expires_time=access_lifetime)
        data = {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "New access token is created",
            "data": {
                "access": new_access_token
            }
        }
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Invalid refresh token"
        )
    
        


