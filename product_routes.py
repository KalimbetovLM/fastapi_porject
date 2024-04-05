from fastapi import APIRouter,status,Depends
from database import session, engine
from schemas import ProductForm
from fastapi_jwt_auth import AuthJWT
from fastapi.exceptions import HTTPException
from models import Client, Product
from fastapi.encoders import jsonable_encoder

product_router = APIRouter(
    prefix="/product"
)

session = session(bind=engine)

@product_router.post("/create_product",status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductForm, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Enter a valid access token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user).first()
    if db_user.is_staff:
        new_product = Product(
            name = data.name,
            price = data.price
        )
        session.add(new_product)
        session.commit()
        data = {
            "id": new_product.id,
            "name": new_product.name,
            "price": new_product.price,
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email
            }
        }
        response = {
            "success": True,
            "status": status.HTTP_201_CREATED,
            "message": "The Product has been registered",
            "data": data
        }   
        return jsonable_encoder(response)
    elif not db_user.is_staff:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff users can register a new product"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something gone wrong,please try again"
        )


@product_router.get("/list",status_code=status.HTTP_200_OK)
async def list_all_products(Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Enter a valid token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user)
    
    if db_user.is_staff:
        products = session.query(Product).filter(Product.id > 0)
        if products:
            data = [
                {
                "id": product.id,
                "name": product.name,
                "price": product.price
                }
                for product in products
            ]
            response = {
                "success": True,
                "status": status.HTTP_200_OK,
                "results": products.count(),
                "data": data
            }
            return jsonable_encoder(response)
        else:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "No products found"
            )
    elif not db_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superuser can see the list of all products"
        )
    else:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Something gone wrong, please try again"
        )


@product_router.get("/{id}")
async def get_product_by_id(id: int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Enter a valid access token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user).first()
    if db_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            response = {
                "success": True,
                "status": status.HTTP_200_OK,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price
                }
            }
            return jsonable_encoder(response)
        else:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product id {id} not found"
            )
    elif not db_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can et product by id"
        )

product_router.delete("/{id}/delete")
async def delete_product(id: int, Authorize: AuthJWT=Depends()):
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
        product = session.query(Product).filter(Product.id == id).first()
        session.delete(product)
        session.commit()
        response = {
            "success": True,
            "status": status.HTTP_102_PROCESSING,
            "message": "Produt has been deleted successfully"
        }
        return jsonable_encoder(response)
    elif not db_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can delete product"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Something gone wrong, please try again later"
        )
    

product_router.patch("/{int}/patch")
async def update_product(id: int, data: ProductForm, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Enter a valid access token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(Client).filter(Client.username == current_user).first()
    if db_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        for key,value in data.dict(exclude_unset=True).items():
            setattr(product,key,value)
        session.commit()
        data = {
            "succes": True,
            "status": status.HTTP_202_ACCEPTED,
            "message": "Product has been updated successfully",
            "product": {
                "id": product.id,
                "name": product.name,
                "price": product.price
            }
        }
        return jsonable_encoder(data)
    elif not db_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Only superusers can update info of products"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )   