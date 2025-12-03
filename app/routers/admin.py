"""
Admin Router - COMPLETE IMPLEMENTATION
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.cart import Order
from app.routers.auth import get_current_user
from app.schemas.cart import OrderResponse

router = APIRouter()

def check_admin(current_user: User = Depends(get_current_user)):
    """Check if user is admin"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/orders", response_model=List[OrderResponse])
async def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Get all orders (admin only)"""
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders

@router.get("/stats")
async def get_stats(
    current_user: User = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics (admin only)"""
    from app.models.product import Product
    from sqlalchemy import func
    
    total_users = db.query(func.count(User.id)).scalar()
    total_products = db.query(func.count(Product.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == "completed"
    ).scalar() or 0
    
    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue)
    }
