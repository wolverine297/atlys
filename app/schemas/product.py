# Modify Product schema to ensure JSON serializability
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

class Product(BaseModel):
    product_title: str
    product_price: float
    path_to_image: Optional[str] = None

    class Config:
        json_encoders = {
            Decimal: float
        }