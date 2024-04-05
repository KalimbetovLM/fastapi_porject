from fastapi import APIRouter,status,Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.exceptions import HTTPException
from models import Client, Product, Order
from schemas import OrderForm, OrderStatusForm
from database import session,engine
from fastapi.encoders import jsonable_encoder


order_router = APIRouter(
    prefix = "/order"
)

session=session(bind=engine)

@order_router.get("/")
async def order():
    return {
        "message": "This is order's main page"
    }

@order_router.post("/make",status_code=status.HTTP_201_CREATED)
async def make_order(data: OrderForm, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Enter a valid access token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user).first()
    product = session.query(Product).filter(Product.id == data.product_id).first()
    new_order = Order(
        quantity = data.quantity,
        product_id = product.id
    )
    new_order.client = db_user
    session.add(new_order)
    session.commit()
    response = {
        "success": True,
        "status": status.HTTP_200_OK,
        "id": new_order.id,
        "quantity": new_order.quantity,
        "user": new_order.client.id,
        "total_price": new_order.quantity * new_order.product.price,
        "order_status": new_order.order_status.value,
        "products": {
            "id": new_order.product.id,
            "name": new_order.product.name,
            "price": new_order.product.price
        }
    }
    return jsonable_encoder(response)


@order_router.get("/list",status_code=status.HTTP_200_OK)
async def get_list_orders(Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Enter a valid access token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user).first()
    if db_user.is_staff:
        orders = session.query(Order).all()
        data = (
            {
                "id": order.id,
                "quantity": order.quantity,
                "status": order.order_status,
                "user_id": order.client_id,
                "product_id": order.product_id
            }
            for order in orders
        )
        response = {
            "status": status.HTTP_200_OK,
            "success": True,
            "results": len(orders),
            "data": data
        }
        return jsonable_encoder(response)
    elif not db_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can get a list of all orders"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something gone wrong, please try again"
        )
    

@order_router.get("/{id}")
async def get_order_by_id(id:int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Enter a valid access token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user).first()
    if db_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        if order:
            response = {
                "order_id": order.id,
                "order_quantity": order.quantity,
                "order_status": order.order_status,
                "user": {
                    "user_id": order.client_id,
                    "user_username": order.client.username,
                    "user_email": order.client.email
                },
                "product": {
                    "product_id": order.product_id,
                    "product_name": order.product.name,
                    "product_price": order.product.price
                }

            }
            return jsonable_encoder(response)
        else:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="Order not found"
            )
    elif not db_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can get order by id"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something gone wrong, please try again"
        )


@order_router.get("/my/{id}")
async def get_users_order_by_id(id:int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enter a valid access token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user).first()
    if db_user:
        order = session.query(Order).filter(Order.id == id).first()
        if order:
            response = {
                "order_id": order.id,
                "order_quantity": order.quantity,
                "order_status": order.order_status,
                "order_product": {
                    "product_id": order.product.id,
                    "product_name": order.product.name,
                    "product_price": order.product.price
                }
            }
            return jsonable_encoder(response)
        else:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail = "Order not found"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something gone wrong, please try again"
        )
    

@order_router.put("/update/{id}")
async def update_order_details(id:int, data:OrderForm, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Enter a valid access token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user).first()
    order = session.query(Order).filter(Order.id == id).first()
    if order:
        if order.client == db_user:
            for key, value in data.dict(exclude_unset=True).items():
                setattr(order,key,value)
            session.commit()
            response = {
                "order_id": order.id,
                "order_quantity": order.quantity,
                "order_status": order.order_status,
                "product": {
                    "product_id": order.product.id,
                    "product_name": order.product.name,
                    "product_price": order.product.price
                }
            }
            return jsonable_encoder(response)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Your order is not found"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found, id is wrong"
        )


@order_router.patch("/update-status",status_code=status.HTTP_202_ACCEPTED)
async def update_order_status(data: OrderStatusForm, Authorize: AuthJWT=Depends()):
    try: 
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Enter a valid access token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user).first()
    if db_user.is_staff:
        order = session.query(Order).filter(Order.id == data.order_id).first()
        if order:
            order.order_status = data.order_status
            session.commit()
            response = {
                "success": True,
                "code": status.HTTP_202_ACCEPTED,
                "message": "Order status has been updated successfully",
                "order": {
                    "id":order.id,
                    'order_status': order.order_status
                }
            }
            return jsonable_encoder(response)
        else:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="Order is not found"
            )
    elif not db_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= "Only superusers can update order's status"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something is gone  wrong, please try again"
        )


@order_router.delete("/delete/{id}")
async def delete_order(id:int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Enter a valid access token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user).first()
    order = session.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    if not db_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can not delete this order"
        )
    if db_user != order.client:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't your order,so you can't cancel it"
        )
    
    if order.order_status != "PENDING" and not db_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can cancel the order while it's pending"
        )
    session.delete(order)
    session.commit()
    response = {
        "success": True,
        "message": "Order has been cancelled successfully",
        "status": status.HTTP_200_OK,
    }
    return jsonable_encoder(response)











