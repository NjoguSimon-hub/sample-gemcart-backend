from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.category import Category

class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True
    
    id = fields.Int(dump_only=True)
    product_count = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    children = fields.Nested('self', many=True, dump_only=True)
    parent = fields.Nested('self', only=['id', 'name'], dump_only=True)

class CategoryCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    description = fields.Str()
    slug = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    parent_id = fields.Int()
    sort_order = fields.Int(missing=0)
    is_active = fields.Bool(missing=True)