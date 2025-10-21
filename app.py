from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gemcart.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret'
    
    CORS(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    from routes.auth import bp as auth_bp
    from routes.products import bp as products_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        # Create sample jewelry data
        from models import User, Product, Category
        if not Product.query.first():
            # Create seller
            seller = User(username='jeweler', email='seller@gemcart.com', is_seller=True)
            seller.set_password('password')
            db.session.add(seller)
            db.session.commit()
            
            # Create categories
            rings = Category(name='Rings')
            necklaces = Category(name='Necklaces')
            db.session.add_all([rings, necklaces])
            db.session.commit()
            
            # Create categories
            watches = Category(name='⌚ Watches')
            chains = Category(name='🔗 Chains')
            gems = Category(name='💎 Gems')
            db.session.add_all([rings, necklaces, watches, chains, gems])
            db.session.commit()
            
            # Create sample products with jewelry images
            products = [
                Product(
                    title="💙 Ocean's Embrace Sapphire Necklace",
                    description="✨ A stunning 18K white gold pendant featuring a deep blue, round-cut sapphire surrounded by a halo of brilliant-cut diamonds. Perfect for special occasions.",
                    price=1250.00,
                    sku="SAPPHIRE-PND-001",
                    inventory_count=50,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&h=500&fit=crop"
                ),
                Product(
                    title="💍 Vintage Diamond Engagement Ring",
                    description="👑 Elegant vintage-style diamond engagement ring with intricate Art Deco detailing and premium clarity stones.",
                    price=2800.00,
                    sku="DIAMOND-RING-002",
                    inventory_count=25,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&h=500&fit=crop"
                ),
                Product(
                    title="🌟 Luxury Swiss Chronograph Watch",
                    description="⌚ Premium Swiss-made chronograph with sapphire crystal, water resistance 200m, and genuine leather strap.",
                    price=3500.00,
                    sku="SWISS-WATCH-004",
                    inventory_count=15,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500&h=500&fit=crop"
                ),
                Product(
                    title="🔗 Cuban Link Gold Chain",
                    description="⚡ Heavy 14K solid gold Cuban link chain, 20 inches, perfect for layering or wearing solo.",
                    price=1800.00,
                    sku="GOLD-CHAIN-005",
                    inventory_count=30,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=500&h=500&fit=crop"
                ),
                Product(
                    title="💎 Natural Emerald Gemstone",
                    description="🌿 Rare Colombian emerald, 2.5 carats, AAA grade with certificate of authenticity. Perfect for custom jewelry.",
                    price=4200.00,
                    sku="EMERALD-GEM-006",
                    inventory_count=8,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500&h=500&fit=crop"
                ),
                Product(
                    title="✨ Rose Gold Tennis Bracelet",
                    description="🌹 Delicate rose gold tennis bracelet with 50 brilliant-cut diamonds, perfect for everyday elegance.",
                    price=2200.00,
                    sku="TENNIS-BRAC-007",
                    inventory_count=40,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=500&h=500&fit=crop"
                ),
                Product(
                    title="👂 Pearl Drop Earrings",
                    description="🦪 Elegant freshwater pearl earrings with 18K gold settings, perfect for formal occasions.",
                    price=680.00,
                    sku="PEARL-DROP-008",
                    inventory_count=60,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&h=500&fit=crop"
                ),
                Product(
                    title="👑 Diamond Tiara",
                    description="🎆 Exquisite bridal tiara with over 200 diamonds, handcrafted for your special day.",
                    price=8500.00,
                    sku="DIAMOND-TIARA-009",
                    inventory_count=5,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&h=500&fit=crop"
                ),
                Product(
                    title="🎭 Men's Gold Cufflinks",
                    description="🔥 Classic 14K gold cufflinks with engraved monogram option, perfect for business attire.",
                    price=420.00,
                    sku="GOLD-CUFF-010",
                    inventory_count=35,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=500&h=500&fit=crop"
                ),
                Product(
                    title="💫 Silver Anklet",
                    description="🌊 Delicate sterling silver anklet with charm details, perfect for summer styling.",
                    price=180.00,
                    sku="SILVER-ANKLET-011",
                    inventory_count=80,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&h=500&fit=crop"
                ),
                Product(
                    title="💍 Ruby Engagement Ring",
                    description="🔥 Stunning 2-carat ruby with diamond halo in platinum setting.",
                    price=3200.00,
                    sku="RUBY-RING-012",
                    inventory_count=12,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&h=500&fit=crop"
                ),
                Product(
                    title="📿 Tahitian Pearl Necklace",
                    description="🌊 Exotic black Tahitian pearls with 18K white gold clasp.",
                    price=2800.00,
                    sku="TAHITIAN-NECK-013",
                    inventory_count=18,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&h=500&fit=crop"
                ),
                Product(
                    title="⌚ Rolex Submariner Watch",
                    description="🌊 Iconic diving watch with ceramic bezel and automatic movement.",
                    price=12500.00,
                    sku="ROLEX-SUB-014",
                    inventory_count=3,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500&h=500&fit=crop"
                ),
                Product(
                    title="👂 Diamond Stud Earrings",
                    description="✨ Classic 1-carat total weight diamond studs in 14K white gold.",
                    price=1800.00,
                    sku="DIAMOND-STUD-015",
                    inventory_count=45,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&h=500&fit=crop"
                ),
                Product(
                    title="🔗 Platinum Chain Necklace",
                    description="🧿 Heavy platinum curb chain, 22 inches, perfect for pendants.",
                    price=2400.00,
                    sku="PLAT-CHAIN-016",
                    inventory_count=20,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=500&h=500&fit=crop"
                ),
                Product(
                    title="💍 Fashion Crystal Ring Set",
                    description="✨ Elegant crystal ring set with adjustable size, perfect for daily wear and special occasions.",
                    price=45.00,
                    sku="CRYSTAL-SET-017",
                    inventory_count=150,
                    seller_id=seller.id,
                    image_url="https://img.kilimall.com/c/public/store/5603/goods/image/101499303.jpg"
                ),
                Product(
                    title="👂 Stainless Steel Hoop Earrings",
                    description="🔥 Durable stainless steel hoops, hypoallergenic, available in gold and silver finish.",
                    price=25.00,
                    sku="STEEL-HOOP-018",
                    inventory_count=200,
                    seller_id=seller.id,
                    image_url="https://image.kilimall.com/kenya/shop/store/goods/7564/2021/08/7564_06827854776024927.jpg"
                ),
                Product(
                    title="💝 Charm Bracelet Collection",
                    description="🎆 Beautiful charm bracelet with multiple pendants, adjustable length 16-20cm.",
                    price=35.00,
                    sku="CHARM-BRAC-019",
                    inventory_count=120,
                    seller_id=seller.id,
                    image_url="https://i.ebayimg.com/images/g/5qIAAeSwSYxoROK9/s-l1600.webp"
                ),
                Product(
                    title="⌚ Digital Smart Watch",
                    description="📱 Multi-function smart watch with fitness tracking, waterproof, 7-day battery life.",
                    price=85.00,
                    sku="SMART-WATCH-020",
                    inventory_count=75,
                    seller_id=seller.id,
                    image_url="https://i.ebayimg.com/images/g/ZeIAAOSw0fxlTQxG/s-l1600.webp"
                ),
                Product(
                    title="🔗 Layered Chain Necklace Set",
                    description="🌟 Trendy multi-layer necklace set, 3 pieces, gold-plated, perfect for layering.",
                    price=28.00,
                    sku="LAYER-NECK-021",
                    inventory_count=180,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&h=500&fit=crop"
                ),
                Product(
                    title="💒 Bridal Jewelry Set",
                    description="👑 Complete bridal set: necklace, earrings, bracelet, ring. Crystal and pearl design.",
                    price=120.00,
                    sku="BRIDAL-SET-022",
                    inventory_count=45,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&h=500&fit=crop"
                ),
                Product(
                    title="🎭 Luxury Cufflink Set",
                    description="🔥 Premium cufflinks with gift box, perfect for business and formal events.",
                    price=65.00,
                    sku="LUX-CUFF-023",
                    inventory_count=60,
                    seller_id=seller.id,
                    image_url="https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=500&h=500&fit=crop"
                )
            ]
            
            # Create additional categories
            earrings = Category(name='👂 Earrings')
            bracelets = Category(name='💝 Bracelets')
            accessories = Category(name='🎭 Accessories')
            db.session.add_all([earrings, bracelets, accessories])
            db.session.commit()
            
            for product in products:
                if "Necklace" in product.title:
                    product.categories.append(necklaces)
                elif "Ring" in product.title:
                    product.categories.append(rings)
                elif "Watch" in product.title:
                    product.categories.append(watches)
                elif "Chain" in product.title:
                    product.categories.append(chains)
                elif "Gemstone" in product.title or "Emerald" in product.title:
                    product.categories.append(gems)
                elif "Earrings" in product.title:
                    product.categories.append(earrings)
                elif "Bracelet" in product.title or "Anklet" in product.title:
                    product.categories.append(bracelets)
                elif "Tiara" in product.title or "Cufflinks" in product.title:
                    product.categories.append(accessories)
                else:
                    product.categories.append(rings)  # Default category
                db.session.add(product)
            
            db.session.commit()
            print("Sample jewelry data created!")
    
    app.run(debug=True)