"""
Categories Router - COMPLETE IMPLEMENTATION
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.product import Category, Product
from app.schemas.product import CategoryResponse, CategoryCreate, ProductResponse
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get single category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.get("/{category_id}/products", response_model=List[ProductResponse])
async def get_category_products(category_id: int, db: Session = Depends(get_db)):
    """Get all products in a category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    products = db.query(Product).filter(
        Product.category_id == category_id,
        Product.is_active == True
    ).all()
    return products

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create category (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_category = Category(**category.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category
