"""
Database Initialization Script
Run this to create tables and populate initial data
Usage: python init_db.py
"""
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.product import Product, Category
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")

def create_admin_user(db: Session):
    """Create default admin user"""
    print("Creating admin user...")
    
    admin = db.query(User).filter(User.email == "admin@digiaata.com").first()
    if admin:
        print("✓ Admin user already exists")
        return
    
    admin = User(
        email="admin@digiaata.com",
        password_hash=pwd_context.hash("admin123"),
        full_name="Admin User",
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("✓ Admin user created (email: admin@digiaata.com, password: admin123)")

def populate_categories(db: Session):
    """Populate categories"""
    print("Populating categories...")
    
    categories_data = [
        {"name": "Stacking & Balance Toys", "slug": "stacking-balance", "description": "Toys that develop fine motor skills and spatial reasoning"},
        {"name": "Pull & Push Toys", "slug": "pull-push", "description": "Wooden toys on wheels that encourage walking and coordination"},
        {"name": "Skill Development", "slug": "skill-development", "description": "Educational toys for developing various skills"},
        {"name": "Baby Toys", "slug": "baby-toys", "description": "Safe, smooth wooden toys for infants"},
        {"name": "Spiritual & Décor", "slug": "spiritual-decor", "description": "Handcrafted spiritual idols and decorative items"},
        {"name": "Home Décor", "slug": "home-decor", "description": "Beautiful handcrafted items for your home"}
    ]
    
    count = 0
    for cat_data in categories_data:
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
            count += 1
    
    db.commit()
    print(f"✓ {count} categories added")

def populate_products(db: Session):
    """Populate products"""
    print("Populating products...")
    
    categories = db.query(Category).all()
    category_map = {cat.name: cat.id for cat in categories}
    
    products_data = [
        {
            "name": "Balancing Cat",
            "price": 850,
            "category": "Stacking & Balance Toys",
            "age_group": "3+",
            "description": "Challenge yourself with Balancing Cat! Strategically stack various colorful, uniquely shaped wooden blocks on a smiling cat base.",
            "stock": 25,
            "image_url": "/uploads/products/balancing-cat.jpg",
        },
        {
            "name": "Indian Nesting Dolls",
            "price": 400,
            "category": "Skill Development",
            "age_group": "3+",
            "description": "Set of five handcrafted, colorful wooden nesting dolls showcasing vibrant Indian craftsmanship.",
            "stock": 30,
            "image_url": "/uploads/products/Indian Nesting Dolls.jpg",  # rename file if needed
        },
        {
            "name": "Ladybug Yo-Yo",
            "price": 120,
            "category": "Skill Development",
            "age_group": "6+",
            "description": "Handcrafted wooden yo-yo with adorable ladybug design.",
            "stock": 50,
            "image_url": "/uploads/products/Ladybug.jpg",
        },
        {
            "name": "Giraffe Pull Toy",
            "price": 300,
            "category": "Pull & Push Toys",
            "age_group": "18 months+",
            "description": "Handcrafted giraffe pull toy with vibrant colors and friendly face.",
            "stock": 20,
            "image_url": "/uploads/products/Giraffe.jpg",
        },
        {
            "name": "Handcrafted Container Train",
            "price": 850,
            "category": "Skill Development",
            "age_group": "3+",
            "description": "Handcrafted wooden train painted with intricate Indian folk art.",
            "stock": 15,
            "image_url": "/uploads/products/Container Train.jpg",
        },
        {
            "name": "Peacock Rattle",
            "price": 120,
            "category": "Baby Toys",
            "age_group": "3 months+",
            "description": "Handcrafted peacock rattle painted with vibrant Indian motifs.",
            "stock": 40,
            "image_url": "/uploads/products/Peacock Rattle.jpg",
        },
        {
            "name": "Dinosaur Pull Toy",
            "price": 300,
            "category": "Pull & Push Toys",
            "age_group": "18 months+",
            "description": "Handcrafted vibrant green dinosaur pull toy.",
            "stock": 25,
            "image_url": "/uploads/products/Dinosaur.jpg",
        },
        {
            "name": "Wooden Stacking Rings",
            "price": 250,
            "category": "Stacking & Balance Toys",
            "age_group": "12 months+",
            "description": "Classic handcrafted wooden toy with brightly colored rings.",
            "stock": 35,
            "image_url": "/uploads/products/Stacking Rings.jpg",
        },
        {
            "name": "Wooden Dog Push Toy",
            "price": 300,
            "category": "Pull & Push Toys",
            "age_group": "12 months+",
            "description": "Charming wooden dog push toy with smooth edges.",
            "stock": 30,
            "image_url": "/uploads/products/Dog.jpg",
        },
        {
            "name": "The Chomp-Chomp Croc",
            "price": 350,
            "category": "Pull & Push Toys",
            "age_group": "12 months+",
            "description": "Charming wooden crocodile with smooth-rolling wheels.",
            "stock": 20,
            "image_url": "/uploads/products/Chomp-Chomp Croc.jpg",
        },
        {
            "name": "The Friendly Push-Along Duck",
            "price": 300,
            "category": "Pull & Push Toys",
            "age_group": "12 months+",
            "description": "Charming wooden duck with cheerful design.",
            "stock": 25,
            "image_url": "/uploads/products/Duck.jpg",
        },
        {
            "name": "Speedster GT Push Along",
            "price": 350,
            "category": "Pull & Push Toys",
            "age_group": "12 months+",
            "description": "Classic wooden car with vibrant finish.",
            "stock": 30,
            "image_url": "/uploads/products/Speedster GT.jpg",
        },
        {
            "name": "Wooden Push Toy",
            "price": 300,
            "category": "Baby Toys",
            "age_group": "6 months+",
            "description": "Natural wooden push toy with smooth curves.",
            "stock": 35,
            "image_url": "/uploads/products/Push Toy.jpg",
        },
        {
            "name": "The Rainbow Stacker",
            "price": 400,
            "category": "Stacking & Balance Toys",
            "age_group": "12 months+",
            "description": "Classic stacking rainbow toy with vibrant colors.",
            "stock": 25,
            "image_url": "/uploads/products/Rainbow Stacker.jpg",
        },
        {
            "name": "Tirupati Balaji Wooden Idol Set",
            "price": 800,
            "category": "Spiritual & Décor",
            "age_group": "All ages",
            "description": "Handcrafted wooden idol set featuring Lord Tirupati Balaji.",
            "stock": 15,
            "image_url": "/uploads/products/Balaji.jpg",
        },
        {
            "name": "Rajasthani Style Hand Mirror",
            "price": 250,
            "category": "Home Décor",
            "age_group": "All ages",
            "description": "Handcrafted wooden hand mirror with folk art.",
            "stock": 20,
            "image_url": "/uploads/products/Hand Mirror.jpg",
        },
        {
            "name": "Sacred Reflections Wall Hangings",
            "price": 450,
            "category": "Spiritual & Décor",
            "age_group": "All ages",
            "description": "Heritage Bronze wall hangings with intricate designs.",
            "stock": 12,
            "image_url": "/uploads/products/Wall Hangings.jpg",
        },
        {
            "name": "Woodland Treasures Nesting Trays",
            "price": 1200,
            "category": "Home Décor",
            "age_group": "All ages",
            "description": "Artisan nesting trays set with hand-carved patterns.",
            "stock": 10,
            "image_url": "/uploads/products/Woodland.jpg",
        },
        {
            "name": "Divine Voyager - Ganesha on Peacock",
            "price": 750,
            "category": "Spiritual & Décor",
            "age_group": "All ages",
            "description": "Handcrafted brass idol featuring Lord Ganesha on peacock.",
            "stock": 15,
            "image_url": "/uploads/products/Ganesha on Peacock.jpg",
        },
        {
            "name": "Divine Serenity - Krishna Idol",
            "price": 350,
            "category": "Spiritual & Décor",
            "age_group": "All ages",
            "description": "Handcrafted wooden idol of Lord Krishna.",
            "stock": 20,
            "image_url": "/uploads/products/Krishna Idol.jpg",
        },
        {
            "name": "Organic Glow Bamboo Pendant Light",
            "price": 460,
            "category": "Home Décor",
            "age_group": "All ages",
            "description": "Handcrafted bamboo pendant lights with natural design.",
            "stock": 15,
            "image_url": "/uploads/products/Pendant Light.jpg",
        },
        {
            "name": "Nature's Embrace Table Lamp",
            "price": 260,
            "category": "Home Décor",
            "age_group": "All ages",
            "description": "Handcrafted bamboo table lamp.",
            "stock": 20,
            "image_url": None,
        },
        {
            "name": "Traditional Echoes Musician Idol",
            "price": 300,
            "category": "Spiritual & Décor",
            "age_group": "All ages",
            "description": "Handcrafted wooden idol honoring India's musical heritage.",
            "stock": 18,
            "image_url": None,
        },
        {
            "name": "Organic Hanging Planter",
            "price": 180,
            "category": "Home Décor",
            "age_group": "All ages",
            "description": "Handwoven macrame hanger with coconut shell pot.",
            "stock": 25,
            "image_url": None,
        },
    ]
    
    count = 0
    for prod_data in products_data:
        existing = db.query(Product).filter(Product.name == prod_data["name"]).first()
        if not existing:
            category_id = category_map.get(prod_data["category"])
            if category_id:
                product = Product(
                    name=prod_data["name"],
                    description=prod_data["description"],
                    price=prod_data["price"],
                    category_id=category_id,
                    age_group=prod_data["age_group"],
                    stock_quantity=prod_data["stock"],
                    is_active=True,
                    image_url=prod_data.get("image_url"),
                )
                db.add(product)
                count += 1
    
    db.commit()
    print(f"✓ {count} products added")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("DIGI AATA E-Commerce - Database Initialization")
    print("=" * 60)
    
    create_tables()
    
    db = SessionLocal()
    
    try:
        create_admin_user(db)
        populate_categories(db)
        populate_products(db)
        
        print("\n" + "=" * 60)
        print("✓ Database initialization completed successfully!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Start the backend: uvicorn app.main:app --reload")
        print("2. Visit API docs: http://localhost:8000/docs")
        print("3. Login as admin: admin@digiaata.com / admin123")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
