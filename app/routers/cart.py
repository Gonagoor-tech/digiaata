"""
Cart Router - COMPLETE IMPLEMENTATION
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CartItemResponse])
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's cart"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    return cart_items

@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock_quantity < item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item.product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    cart_item = CartItem(
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.put("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if product.stock_quantity < item_update.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    cart_item.quantity = item_update.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    return None

@router.get("/total")
async def get_cart_total(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate cart total"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    total = 0
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            total += product.price * item.quantity
    
    return {"total": total, "item_count": len(cart_items)}
