from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.product import Product
from .category_schema import CategorySchema

class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True
    
    id = fields.Int(dump_only=True)
    categories = fields.Nested(CategorySchema, many=True, dump_only=True)
    average_rating = fields.Float(dump_only=True)
    review_count = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    seller = fields.Nested('UserSchema', only=['id', 'username'], dump_only=True)

class ProductCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    inventory_count = fields.Int(validate=validate.Range(min=0), missing=0)
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    weight = fields.Decimal(validate=validate.Range(min=0))
    material = fields.Str(validate=validate.Length(max=100))
    gemstone = fields.Str(validate=validate.Length(max=100))
    size = fields.Str(validate=validate.Length(max=50))
    category_ids = fields.List(fields.Int(), missing=[])
    is_featured = fields.Bool(missing=False)

class ProductUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str()
    price = fields.Decimal(validate=validate.Range(min=0))
    inventory_count = fields.Int(validate=validate.Range(min=0))
    weight = fields.Decimal(validate=validate.Range(min=0))
    material = fields.Str(validate=validate.Length(max=100))
    gemstone = fields.Str(validate=validate.Length(max=100))
    size = fields.Str(validate=validate.Length(max=50))
    category_ids = fields.List(fields.Int())
    is_featured = fields.Bool()
    is_active = fields.Bool()