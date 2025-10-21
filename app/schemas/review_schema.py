from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.review import Review

class ReviewSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Review
        load_instance = True
    
    id = fields.Int(dump_only=True)
    author = fields.Nested('UserSchema', only=['id', 'username'], dump_only=True)
    product = fields.Nested('ProductSchema', only=['id', 'title'], dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ReviewCreateSchema(Schema):
    product_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    title = fields.Str(validate=validate.Length(max=200))
    body = fields.Str()