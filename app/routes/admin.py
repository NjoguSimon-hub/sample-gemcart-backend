from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.review import Review
from app.schemas.user_schema import UserSchema
from app.utils.decorators import role_required
from app.utils.pagination import paginate_query

class AdminDashboard(Resource):
    """
    Admin Dashboard
    ---
    tags:
      - Admin
    """
    
    @jwt_required()
    @role_required(['admin'])
    def get(self):
        """
        Get Dashboard Statistics
        ---
        security:
          - Bearer: []
        responses:
          200:
            description: Dashboard statistics
          403:
            description: Insufficient permissions
        """
        
        # Get statistics
        total_users = User.query.count()
        total_products = Product.query.filter_by(is_active=True).count()
        total_orders = Order.query.count()
        total_reviews = Review.query.count()
        
        # Revenue statistics
        total_revenue = db.session.query(func.sum(Order.total_amount)).filter_by(status='delivered').scalar() or 0
        pending_orders = Order.query.filter_by(status='pending').count()
        
        # Recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        
        # Top products by sales
        top_products = db.session.query(
            Product.id,
            Product.title,
            func.sum(Order.total_amount).label('revenue')
        ).join(Order).group_by(Product.id).order_by(func.sum(Order.total_amount).desc()).limit(5).all()
        
        return {
            'statistics': {
                'total_users': total_users,
                'total_products': total_products,
                'total_orders': total_orders,
                'total_reviews': total_reviews,
                'total_revenue': float(total_revenue),
                'pending_orders': pending_orders
            },
            'recent_orders': [
                {
                    'id': order.id,
                    'order_number': order.order_number,
                    'total_amount': float(order.total_amount),
                    'status': order.status,
                    'created_at': order.created_at.isoformat()
                } for order in recent_orders
            ],
            'top_products': [
                {
                    'id': product.id,
                    'title': product.title,
                    'revenue': float(product.revenue)
                } for product in top_products
            ]
        }, 200

class AdminUsers(Resource):
    """
    Admin User Management
    ---
    tags:
      - Admin
    """
    
    @jwt_required()
    @role_required(['admin'])
    def get(self):
        """
        Get All Users
        ---
        security:
          - Bearer: []
        parameters:
          - in: query
            name: page
            type: integer
            default: 1
          - in: query
            name: per_page
            type: integer
            default: 20
          - in: query
            name: role
            type: string
        responses:
          200:
            description: List of users
          403:
            description: Insufficient permissions
        """
        
        query = User.query
        
        # Filter by role
        role = request.args.get('role')
        if role:
            query = query.filter_by(role=role)
        
        query = query.order_by(User.created_at.desc())
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        pagination_result = paginate_query(query, page, per_page)
        
        schema = UserSchema(many=True)
        return {
            'users': schema.dump(pagination_result['items']),
            'pagination': {
                'page': pagination_result['page'],
                'pages': pagination_result['pages'],
                'per_page': pagination_result['per_page'],
                'total': pagination_result['total']
            }
        }, 200