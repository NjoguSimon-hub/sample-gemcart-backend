from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app import db
from app.models.review import Review
from app.models.product import Product
from app.schemas.review_schema import ReviewSchema, ReviewCreateSchema
from app.utils.pagination import paginate_query

class ReviewListAPI(Resource):
    """
    Review List and Create
    ---
    tags:
      - Reviews
    """
    
    def get(self):
        """
        Get Reviews
        ---
        parameters:
          - in: query
            name: product_id
            type: integer
          - in: query
            name: page
            type: integer
            default: 1
          - in: query
            name: per_page
            type: integer
            default: 10
        responses:
          200:
            description: List of reviews
        """
        
        query = Review.query.filter_by(is_approved=True)
        
        product_id = request.args.get('product_id', type=int)
        if product_id:
            query = query.filter_by(product_id=product_id)
        
        query = query.order_by(Review.created_at.desc())
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        
        pagination_result = paginate_query(query, page, per_page)
        
        schema = ReviewSchema(many=True)
        return {
            'reviews': schema.dump(pagination_result['items']),
            'pagination': {
                'page': pagination_result['page'],
                'pages': pagination_result['pages'],
                'per_page': pagination_result['per_page'],
                'total': pagination_result['total']
            }
        }, 200
    
    @jwt_required()
    def post(self):
        """
        Create Review
        ---
        security:
          - Bearer: []
        parameters:
          - in: body
            name: body
            schema:
              type: object
              required:
                - product_id
                - rating
              properties:
                product_id:
                  type: integer
                rating:
                  type: integer
                  minimum: 1
                  maximum: 5
                title:
                  type: string
                body:
                  type: string
        responses:
          201:
            description: Review created successfully
          400:
            description: Validation error
        """
        
        schema = ReviewCreateSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        user_id = get_jwt_identity()
        
        # Check if product exists
        product = Product.query.get(data['product_id'])
        if not product:
            return {'message': 'Product not found'}, 404
        
        # Check if user already reviewed this product
        existing_review = Review.query.filter_by(
            author_id=user_id,
            product_id=data['product_id']
        ).first()
        
        if existing_review:
            return {'message': 'You have already reviewed this product'}, 400
        
        review = Review(
            author_id=user_id,
            product_id=data['product_id'],
            rating=data['rating'],
            title=data.get('title'),
            body=data.get('body')
        )
        
        db.session.add(review)
        db.session.commit()
        
        review_schema = ReviewSchema()
        return {
            'message': 'Review created successfully',
            'review': review_schema.dump(review)
        }, 201