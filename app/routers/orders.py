"""
Orders Router - COMPLETE IMPLEMENTATION
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.cart import Order, OrderItem, CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import OrderCreate, OrderResponse
from app.routers.auth import get_current_user

router = APIRouter()

def generate_order_number():
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ORD{timestamp}"

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create order from cart"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total_amount = 0
    order_items_data = []
    
    for cart_item in cart_items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {cart_item.product_id} not found")
        
        if product.stock_quantity < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}"
            )
        
        subtotal = product.price * cart_item.quantity
        total_amount += subtotal
        
        order_items_data.append({
            "product_id": product.id,
            "quantity": cart_item.quantity,
            "price_at_purchase": product.price
        })
    
    order = Order(
        user_id=current_user.id,
        order_number=generate_order_number(),
        total_amount=total_amount,
        shipping_address_id=order_data.shipping_address_id,
        payment_method=order_data.payment_method,
        status="pending",
        payment_status="pending"
    )
    
    db.add(order)
    db.flush()
    
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            **item_data
        )
        db.add(order_item)
        
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        product.stock_quantity -= item_data["quantity"]
    
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    
    db.commit()
    db.refresh(order)
    return order

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's orders"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    
    return {"message": "Order status updated", "order_id": order_id, "status": status}
