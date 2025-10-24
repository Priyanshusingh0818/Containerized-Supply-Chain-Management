from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models import db, Item, Transaction, Audit
from utils.security import admin_required, viewer_or_admin_required
from utils.audit import log_audit
import json

items_bp = Blueprint('items', __name__)

@items_bp.route('/items', methods=['GET'])
@jwt_required()
@viewer_or_admin_required
def get_items():
    """Get all items with optional filtering"""
    category = request.args.get('category')
    low_stock = request.args.get('low_stock', 'false').lower() == 'true'
    
    query = Item.query
    
    if category:
        query = query.filter_by(category=category)
    
    if low_stock:
        query = query.filter(Item.quantity <= Item.reorder_level)
    
    items = query.all()
    return jsonify([item.to_dict() for item in items]), 200

@items_bp.route('/items/<int:item_id>', methods=['GET'])
@jwt_required()
@viewer_or_admin_required
def get_item(item_id):
    """Get single item by ID"""
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict()), 200

@items_bp.route('/items', methods=['POST'])
@jwt_required()
@admin_required
def create_item():
    """Create new item"""
    data = request.get_json()
    
    # Validate required fields
    required = ['name', 'sku', 'category', 'quantity', 'price']
    if not all(field in data for field in required):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if SKU already exists
    if Item.query.filter_by(sku=data['sku']).first():
        return jsonify({'message': 'SKU already exists'}), 400
    
    item = Item(
        name=data['name'],
        sku=data['sku'],
        category=data['category'],
        quantity=data['quantity'],
        price=data['price'],
        reorder_level=data.get('reorder_level', 10),
        description=data.get('description', '')
    )
    
    db.session.add(item)
    db.session.commit()
    # Audit log
    try:
        user = get_jwt_identity()
        user_obj = None
        # Try to resolve user id
        from models import User
        user_obj = User.query.filter_by(username=user).first()
        user_id = user_obj.id if user_obj else None
        log_audit('CREATE', 'Item', item.id, user_id, changes=item.to_dict())
    except Exception:
        pass

    return jsonify(item.to_dict()), 201

@items_bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_item(item_id):
    """Update existing item"""
    item = Item.query.get_or_404(item_id)
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        item.name = data['name']
    if 'category' in data:
        item.category = data['category']
    if 'quantity' in data:
        item.quantity = data['quantity']
    if 'price' in data:
        item.price = data['price']
    if 'reorder_level' in data:
        item.reorder_level = data['reorder_level']
    if 'description' in data:
        item.description = data['description']
    
    db.session.commit()
    # Audit log
    try:
        user = get_jwt_identity()
        from models import User
        user_obj = User.query.filter_by(username=user).first()
        user_id = user_obj.id if user_obj else None
        # Determine diff (simple approach)
        changes = {k: getattr(item, k) for k in ['name','category','quantity','price','reorder_level','description']}
        log_audit('UPDATE', 'Item', item.id, user_id, changes=changes)
    except Exception:
        pass

    return jsonify(item.to_dict()), 200

@items_bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_item(item_id):
    """Delete item"""
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    # Audit log
    try:
        user = get_jwt_identity()
        from models import User
        user_obj = User.query.filter_by(username=user).first()
        user_id = user_obj.id if user_obj else None
        log_audit('DELETE', 'Item', item.id, user_id, changes=None)
    except Exception:
        pass

    return jsonify({'message': 'Item deleted successfully'}), 200

@items_bp.route('/categories', methods=['GET'])
@jwt_required()
@viewer_or_admin_required
def get_categories():
    """Get all unique categories"""
    categories = db.session.query(Item.category).distinct().all()
    return jsonify([cat[0] for cat in categories]), 200