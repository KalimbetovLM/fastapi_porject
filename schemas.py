from pydantic import BaseModel,ValidationError, Field
from typing import Optional


class SignUpModel(BaseModel):
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            "example":{
                "username": "test_user",
                "email": "testmail@gmail.com",
                "password": "password12345",
                "is_staff": False,
                "is_active": True
            }
        }

class Settings(BaseModel):
    authjwt_secret_key: str = '3ffd95bd23505c24bbdeb96d26886992c58849b8413fb3c4e686163703ed3120'

class LoginForm(BaseModel):
    username_or_email: str
    password: str


class ProductForm(BaseModel):
    id: Optional[int]
    name: str
    price: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Pizza",
                "price": 40000
            }
        }
    

class OrderForm(BaseModel):
    quantity: int
    order_status: Optional[str] = "PENDING"
    user_id: Optional[int]
    product_id: int

    class Config:
        orm_mode = True
        schema_ecxtra = {
            "example": {
                "quantity": 2,
                "product_id": 1234
            }
        }
        

class OrderStatusForm(BaseModel):
    order_status: Optional[str] = Field("PENDING")
    order_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "order_status": "PENDING",
                "order_id": 1234
            }
        }
        