"""
Cart and Order Pydantic Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    shipping_address_id: int
    payment_method: str

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int
    order_number: str
    total_amount: float
    status: str
    payment_status: str
    created_at: datetime
    order_items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True
