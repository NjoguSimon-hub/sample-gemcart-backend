from flask_restful import Resource
from app.models.category import Category
from app.schemas.category_schema import CategorySchema

class CategoryListAPI(Resource):
    """
    Category List
    ---
    tags:
      - Categories
    """
    
    def get(self):
        """
        Get All Categories
        ---
        responses:
          200:
            description: List of categories
        """
        
        categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order, Category.name).all()
        schema = CategorySchema(many=True)
        
        return {'categories': schema.dump(categories)}, 200