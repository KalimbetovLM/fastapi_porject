from database import engine,Base
from models import Client, Order, Product

Base.metadata.create_all(bind=engine)
