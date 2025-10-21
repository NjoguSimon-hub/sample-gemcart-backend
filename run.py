import os
from app import create_app, db
from app.models import User, Product, Category, Order, Review
from flask_migrate import upgrade

def deploy():
    """Run deployment tasks."""
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create sample data if none exists
        if not User.query.first():
            create_sample_data()

def create_sample_data():
    """Create sample data for development"""
    # Create admin user
    admin = User(
        username='admin',
        email='admin@gemcart.com',
        first_name='Admin',
        last_name='User',
        role='admin',
        is_active=True,
        is_verified=True
    )
    admin.set_password('admin123')
    
    # Create seller user
    seller = User(
        username='jeweler',
        email='seller@gemcart.com',
        first_name='Master',
        last_name='Jeweler',
        role='seller',
        is_active=True,
        is_verified=True
    )
    seller.set_password('seller123')
    
    # Create customer user
    customer = User(
        username='customer',
        email='customer@gemcart.com',
        first_name='John',
        last_name='Doe',
        role='customer',
        is_active=True,
        is_verified=True
    )
    customer.set_password('customer123')
    
    db.session.add_all([admin, seller, customer])
    db.session.commit()
    
    # Create categories
    categories_data = [
        {'name': 'Rings', 'slug': 'rings', 'description': 'Engagement rings, wedding bands, and fashion rings'},
        {'name': 'Necklaces', 'slug': 'necklaces', 'description': 'Pendants, chains, and statement necklaces'},
        {'name': 'Earrings', 'slug': 'earrings', 'description': 'Studs, hoops, and drop earrings'},
        {'name': 'Bracelets', 'slug': 'bracelets', 'description': 'Tennis bracelets, bangles, and charm bracelets'},
        {'name': 'Watches', 'slug': 'watches', 'description': 'Luxury timepieces and smart watches'},
        {'name': 'Chains', 'slug': 'chains', 'description': 'Gold chains, silver chains, and necklace chains'}
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data)
        categories.append(category)
        db.session.add(category)
    
    db.session.commit()
    
    print("Sample data created successfully!")

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    with app.app_context():
        if not User.query.first():
            create_sample_data()
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)