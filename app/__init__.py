from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flasgger import Swagger
import cloudinary
from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # Initialize Cloudinary
    if app.config.get('CLOUDINARY_CLOUD_NAME'):
        cloudinary.config(
            cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=app.config['CLOUDINARY_API_KEY'],
            api_secret=app.config['CLOUDINARY_API_SECRET']
        )
    
    # Initialize Swagger
    swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "GemCart API",
            "description": "Luxury Jewelry E-commerce API",
            "version": "1.0.0"
        }
    })
    
    # Initialize API
    api = Api(app)
    
    # Register routes
    from app.routes.auth import AuthRegister, AuthLogin, AuthProfile
    from app.routes.products import ProductListAPI, ProductDetailAPI
    from app.routes.categories import CategoryListAPI
    from app.routes.orders import OrderListAPI, OrderDetailAPI
    from app.routes.reviews import ReviewListAPI
    from app.routes.admin import AdminDashboard, AdminUsers
    
    # Auth routes
    api.add_resource(AuthRegister, '/api/auth/register')
    api.add_resource(AuthLogin, '/api/auth/login')
    api.add_resource(AuthProfile, '/api/auth/profile')
    
    # Product routes
    api.add_resource(ProductListAPI, '/api/products')
    api.add_resource(ProductDetailAPI, '/api/products/<int:product_id>')
    
    # Category routes
    api.add_resource(CategoryListAPI, '/api/categories')
    
    # Order routes
    api.add_resource(OrderListAPI, '/api/orders')
    api.add_resource(OrderDetailAPI, '/api/orders/<int:order_id>')
    
    # Review routes
    api.add_resource(ReviewListAPI, '/api/reviews')
    
    # Admin routes
    api.add_resource(AdminDashboard, '/api/admin/dashboard')
    api.add_resource(AdminUsers, '/api/admin/users')
    
    return app