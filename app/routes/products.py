from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import or_
from app import db
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.schemas.product_schema import ProductSchema, ProductCreateSchema, ProductUpdateSchema
from app.utils.decorators import role_required
from app.utils.pagination import paginate_query
from app.services.image_service import upload_image, delete_image

class ProductListAPI(Resource):
    """
    Product List and Create
    ---
    tags:
      - Products
    """
    
    def get(self):
        """
        Get Products with Pagination and Filtering
        ---
        parameters:
          - in: query
            name: page
            type: integer
            default: 1
          - in: query
            name: per_page
            type: integer
            default: 12
          - in: query
            name: search
            type: string
          - in: query
            name: category
            type: string
          - in: query
            name: min_price
            type: number
          - in: query
            name: max_price
            type: number
          - in: query
            name: sort
            type: string
            enum: [price_asc, price_desc, name_asc, name_desc, newest]
        responses:
          200:
            description: List of products
        """
        
        query = Product.query.filter_by(is_active=True)
        
        # Search filter
        search = request.args.get('search')
        if search:
            query = query.filter(
                or_(
                    Product.title.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%')
                )
            )
        
        # Category filter
        category = request.args.get('category')
        if category:
            query = query.join(Product.categories).filter(Category.name == category)
        
        # Price filters
        min_price = request.args.get('min_price', type=float)
        if min_price:
            query = query.filter(Product.price >= min_price)
        
        max_price = request.args.get('max_price', type=float)
        if max_price:
            query = query.filter(Product.price <= max_price)
        
        # Sorting
        sort = request.args.get('sort', 'newest')
        if sort == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif sort == 'name_asc':
            query = query.order_by(Product.title.asc())
        elif sort == 'name_desc':
            query = query.order_by(Product.title.desc())
        else:  # newest
            query = query.order_by(Product.created_at.desc())
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 12, type=int), 100)
        
        pagination_result = paginate_query(query, page, per_page)
        
        schema = ProductSchema(many=True)
        return {
            'products': schema.dump(pagination_result['items']),
            'pagination': {
                'page': pagination_result['page'],
                'pages': pagination_result['pages'],
                'per_page': pagination_result['per_page'],
                'total': pagination_result['total']
            }
        }, 200
    
    @jwt_required()
    @role_required(['seller', 'admin'])
    def post(self):
        """
        Create New Product
        ---
        security:
          - Bearer: []
        parameters:
          - in: body
            name: body
            schema:
              type: object
              required:
                - title
                - price
                - sku
              properties:
                title:
                  type: string
                description:
                  type: string
                price:
                  type: number
                inventory_count:
                  type: integer
                sku:
                  type: string
        responses:
          201:
            description: Product created successfully
          400:
            description: Validation error
          403:
            description: Insufficient permissions
        """
        
        schema = ProductCreateSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        # Check if SKU already exists
        if Product.query.filter_by(sku=data['sku']).first():
            return {'message': 'SKU already exists'}, 400
        
        user_id = get_jwt_identity()
        
        product = Product(
            title=data['title'],
            description=data.get('description'),
            price=data['price'],
            inventory_count=data.get('inventory_count', 0),
            sku=data['sku'],
            weight=data.get('weight'),
            material=data.get('material'),
            gemstone=data.get('gemstone'),
            size=data.get('size'),
            is_featured=data.get('is_featured', False),
            seller_id=user_id
        )
        
        # Add categories
        category_ids = data.get('category_ids', [])
        for category_id in category_ids:
            category = Category.query.get(category_id)
            if category:
                product.categories.append(category)
        
        db.session.add(product)
        db.session.commit()
        
        product_schema = ProductSchema()
        return {
            'message': 'Product created successfully',
            'product': product_schema.dump(product)
        }, 201

class ProductDetailAPI(Resource):
    """
    Product Detail Operations
    ---
    tags:
      - Products
    """
    
    def get(self, product_id):
        """
        Get Product Details
        ---
        parameters:
          - in: path
            name: product_id
            type: integer
            required: true
        responses:
          200:
            description: Product details
          404:
            description: Product not found
        """
        
        product = Product.query.filter_by(id=product_id, is_active=True).first()
        if not product:
            return {'message': 'Product not found'}, 404
        
        schema = ProductSchema()
        return {'product': schema.dump(product)}, 200
    
    @jwt_required()
    @role_required(['seller', 'admin'])
    def put(self, product_id):
        """
        Update Product
        ---
        security:
          - Bearer: []
        parameters:
          - in: path
            name: product_id
            type: integer
            required: true
        responses:
          200:
            description: Product updated successfully
          404:
            description: Product not found
          403:
            description: Insufficient permissions
        """
        
        product = Product.query.get(product_id)
        if not product:
            return {'message': 'Product not found'}, 404
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user owns the product or is admin
        if product.seller_id != user_id and not user.is_admin():
            return {'message': 'Insufficient permissions'}, 403
        
        schema = ProductUpdateSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        # Update fields
        for field, value in data.items():
            if field == 'category_ids':
                product.categories.clear()
                for category_id in value:
                    category = Category.query.get(category_id)
                    if category:
                        product.categories.append(category)
            else:
                setattr(product, field, value)
        
        db.session.commit()
        
        product_schema = ProductSchema()
        return {
            'message': 'Product updated successfully',
            'product': product_schema.dump(product)
        }, 200
    
    @jwt_required()
    @role_required(['seller', 'admin'])
    def delete(self, product_id):
        """
        Delete Product
        ---
        security:
          - Bearer: []
        parameters:
          - in: path
            name: product_id
            type: integer
            required: true
        responses:
          200:
            description: Product deleted successfully
          404:
            description: Product not found
          403:
            description: Insufficient permissions
        """
        
        product = Product.query.get(product_id)
        if not product:
            return {'message': 'Product not found'}, 404
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user owns the product or is admin
        if product.seller_id != user_id and not user.is_admin():
            return {'message': 'Insufficient permissions'}, 403
        
        # Soft delete
        product.is_active = False
        db.session.commit()
        
        return {'message': 'Product deleted successfully'}, 200