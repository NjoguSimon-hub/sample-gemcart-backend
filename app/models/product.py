from datetime import datetime
from app import db

product_categories = db.Table('product_categories',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False, index=True)
    inventory_count = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Images
    image_url = db.Column(db.String(500))
    image_public_id = db.Column(db.String(200))  # Cloudinary public ID
    
    # Product details
    weight = db.Column(db.Numeric(8, 2))  # in grams
    material = db.Column(db.String(100))
    gemstone = db.Column(db.String(100))
    size = db.Column(db.String(50))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Foreign keys
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = db.relationship('Category', secondary=product_categories, 
                               backref=db.backref('products', lazy='dynamic'))
    reviews = db.relationship('Review', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)
    
    @property
    def review_count(self):
        return self.reviews.count()
    
    def __repr__(self):
        return f'<Product {self.title}>'