from database import Base
from sqlalchemy import Column,Integer,Boolean,Text,String, ForeignKey
from sqlalchemy.orm import relationship
import random
from sqlalchemy_utils.types import ChoiceType

def id_generator():
    first_number = random.randint(10,99)
    second_number = random.randint(10,99)
    id = str(first_number) + str(second_number)
    id = int(id)
    return id

class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    password = Column(Text, nullable=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    # orders = relationship("Order",back_populates="client")

    def __repr__(self):
        return self.username
    

class Product(Base):
    __tablename__='product'
    id = Column(Integer,primary_key=True,default=id_generator)
    name = Column(String(100))
    price = Column(Integer)

    def __str__(self):
        return self.name

class Order(Base):
    ORDER_STATUSES = (
        ("PENDING","pending"),
        ("IN_TRANSIT","in_transit"),
        ("DELIVERED","delivered")
    )
    __tablename__="order"
    id = Column(Integer,primary_key=True,default=id_generator)
    quantity = Column(Integer,nullable=False)
    order_status = Column(ChoiceType(choices=ORDER_STATUSES),default="PENDING")
    client_id = Column(Integer,ForeignKey("client.id"))
    client = relationship("Client", backref="orders", overlaps="orders")
    product_id = Column(Integer,ForeignKey("product.id"))
    product = relationship("Product",backref="product")

    def __repr__(self):
        return self.id
    



    
