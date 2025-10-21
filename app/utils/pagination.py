import math

def paginate_query(query, page=1, per_page=20):
    """
    Paginate a SQLAlchemy query
    """
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': math.ceil(total / per_page) if total > 0 else 1,
        'has_prev': page > 1,
        'has_next': page < math.ceil(total / per_page) if total > 0 else False
    }