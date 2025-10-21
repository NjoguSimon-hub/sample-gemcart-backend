from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Product, Category, User

bp = Blueprint('products', __name__, url_prefix='/api/products')

@bp.route('', methods=['GET'])
def list_products():
    query = Product.query
    
    # Search functionality
    search = request.args.get('search')
    if search:
        query = query.filter(Product.title.ilike(f'%{search}%'))
    
    # Category filter
    category = request.args.get('category')
    if category:
        query = query.join(Product.categories).filter(Category.name.ilike(f'%{category}%'))
    
    # Price range filter
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    if min_price:
        query = query.filter(Product.price >= float(min_price))
    if max_price:
        query = query.filter(Product.price <= float(max_price))
    
    # Sort by price
    sort = request.args.get('sort')
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    
    products = query.all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'description': p.description,
        'price': str(p.price),
        'inventory_count': p.inventory_count,
        'sku': p.sku,
        'image_url': p.image_url,
        'categories': [{'id': c.id, 'name': c.name} for c in p.categories],
        'seller': {'id': p.seller.id, 'username': p.seller.username}
    } for p in products])

@bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_seller and not user.is_admin:
        return jsonify({'error': 'Must be seller to create product'}), 403

    data = request.get_json()
    product = Product(
        title=data['title'],
        description=data.get('description', ''),
        price=data['price'],
        inventory_count=data.get('inventory_count', 0),
        sku=data['sku'],
        seller_id=user_id,
        image_url=data.get('image_url')
    )
    
    for cat_name in data.get('categories', []):
        cat = Category.query.filter_by(name=cat_name).first()
        if not cat:
            cat = Category(name=cat_name)
            db.session.add(cat)
        product.categories.append(cat)

    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created', 'id': product.id}), 201

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'price': str(product.price),
        'inventory_count': product.inventory_count,
        'sku': product.sku,
        'image_url': product.image_url,
        'categories': [{'id': c.id, 'name': c.name} for c in product.categories],
        'seller': {'id': product.seller.id, 'username': product.seller.username}
    })

@bp.route('/<int:product_id>', methods=['PATCH'])
@jwt_required()
def update_product(product_id):
    user_id = get_jwt_identity()
    product = Product.query.get_or_404(product_id)
    if product.seller_id != user_id and not User.query.get(user_id).is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    for k in ['title', 'description', 'price', 'inventory_count', 'sku', 'image_url']:
        if k in data:
            setattr(product, k, data[k])
    
    db.session.commit()
    return jsonify({'message': 'Product updated'})

@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    user_id = get_jwt_identity()
    product = Product.query.get_or_404(product_id)
    if product.seller_id != user_id and not User.query.get(user_id).is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({}), 204