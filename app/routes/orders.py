from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app import db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order_schema import OrderSchema, OrderCreateSchema
from app.utils.pagination import paginate_query
import uuid

class OrderListAPI(Resource):
    """
    Order List and Create
    ---
    tags:
      - Orders
    """
    
    @jwt_required()
    def get(self):
        """
        Get User Orders
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
            default: 10
        responses:
          200:
            description: List of user orders
        """
        
        user_id = get_jwt_identity()
        query = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc())
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        
        pagination_result = paginate_query(query, page, per_page)
        
        schema = OrderSchema(many=True)
        return {
            'orders': schema.dump(pagination_result['items']),
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
        Create New Order
        ---
        security:
          - Bearer: []
        parameters:
          - in: body
            name: body
            schema:
              type: object
              required:
                - items
                - shipping_first_name
                - shipping_last_name
                - shipping_address_line1
                - shipping_city
                - shipping_state
                - shipping_postal_code
                - shipping_country
        responses:
          201:
            description: Order created successfully
          400:
            description: Validation error
        """
        
        schema = OrderCreateSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        user_id = get_jwt_identity()
        
        # Calculate totals
        subtotal = 0
        order_items = []
        
        for item_data in data['items']:
            product = Product.query.get(item_data['product_id'])
            if not product or not product.is_active:
                return {'message': f'Product {item_data["product_id"]} not found'}, 400
            
            quantity = item_data['quantity']
            if product.inventory_count < quantity:
                return {'message': f'Insufficient inventory for {product.title}'}, 400
            
            unit_price = product.price
            total_price = unit_price * quantity
            subtotal += total_price
            
            order_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price
            })
        
        # Create order
        order = Order(
            order_number=f'GC-{uuid.uuid4().hex[:8].upper()}',
            customer_id=user_id,
            subtotal=subtotal,
            total_amount=subtotal,  # Add tax/shipping calculation here
            shipping_first_name=data['shipping_first_name'],
            shipping_last_name=data['shipping_last_name'],
            shipping_address_line1=data['shipping_address_line1'],
            shipping_address_line2=data.get('shipping_address_line2'),
            shipping_city=data['shipping_city'],
            shipping_state=data['shipping_state'],
            shipping_postal_code=data['shipping_postal_code'],
            shipping_country=data['shipping_country'],
            payment_method=data.get('payment_method', 'stripe')
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items and update inventory
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price'],
                product_title=item_data['product'].title,
                product_sku=item_data['product'].sku
            )
            db.session.add(order_item)
            
            # Update inventory
            item_data['product'].inventory_count -= item_data['quantity']
        
        db.session.commit()
        
        order_schema = OrderSchema()
        return {
            'message': 'Order created successfully',
            'order': order_schema.dump(order)
        }, 201

class OrderDetailAPI(Resource):
    """
    Order Detail Operations
    ---
    tags:
      - Orders
    """
    
    @jwt_required()
    def get(self, order_id):
        """
        Get Order Details
        ---
        security:
          - Bearer: []
        parameters:
          - in: path
            name: order_id
            type: integer
            required: true
        responses:
          200:
            description: Order details
          404:
            description: Order not found
        """
        
        user_id = get_jwt_identity()
        order = Order.query.filter_by(id=order_id, customer_id=user_id).first()
        
        if not order:
            return {'message': 'Order not found'}, 404
        
        schema = OrderSchema()
        return {'order': schema.dump(order)}, 200