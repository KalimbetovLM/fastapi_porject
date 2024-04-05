from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_router
from product_routes import product_router
from sqlalchemy.sql import base
from fastapi_jwt_auth import AuthJWT
from schemas import Settings,LoginForm

app = FastAPI()
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(product_router)

@AuthJWT.load_config
def get_config():
    return Settings()

@app.get('/')
async def root():
    return {
        "message": "FastApi project ishga tushdi"
    }
