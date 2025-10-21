from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.order import Order, OrderItem

class OrderItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OrderItem
        load_instance = True
    
    id = fields.Int(dump_only=True)
    product = fields.Nested('ProductSchema', only=['id', 'title', 'image_url'], dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class OrderSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
    
    id = fields.Int(dump_only=True)
    items = fields.Nested(OrderItemSchema, many=True, dump_only=True)
    customer = fields.Nested('UserSchema', only=['id', 'username', 'email'], dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class OrderCreateSchema(Schema):
    items = fields.List(fields.Dict(), required=True)
    shipping_first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    shipping_last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    shipping_address_line1 = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    shipping_address_line2 = fields.Str(validate=validate.Length(max=200))
    shipping_city = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    shipping_state = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    shipping_postal_code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    shipping_country = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    payment_method = fields.Str(validate=validate.OneOf(['stripe', 'paypal']))