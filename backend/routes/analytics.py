from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func, desc, case
from models import db, Item, Transaction
from utils.security import viewer_or_admin_required
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/low-stock', methods=['GET'])
@jwt_required()
@viewer_or_admin_required
def low_stock_items():
    """Get items with stock below reorder level"""
    items = Item.query.filter(Item.quantity <= Item.reorder_level).all()
    
    result = [{
        'id': item.id,
        'name': item.name,
        'sku': item.sku,
        'category': item.category,
        'current_stock': item.quantity,
        'reorder_level': item.reorder_level,
        'shortage': item.reorder_level - item.quantity
    } for item in items]
    
    return jsonify(result), 200

@analytics_bp.route('/analytics/category-summary', methods=['GET'])
@jwt_required()
@viewer_or_admin_required
def category_summary():
    """Get summary statistics by category"""
    summary = db.session.query(
        Item.category,
        func.count(Item.id).label('total_items'),
        func.sum(Item.quantity).label('total_quantity'),
        func.sum(Item.quantity * Item.price).label('total_value')
    ).group_by(Item.category).all()
    
    result = [{
        'category': row.category,
        'total_items': row.total_items,
        'total_quantity': row.total_quantity or 0,
        'total_value': float(row.total_value or 0)
    } for row in summary]
    
    return jsonify(result), 200

@analytics_bp.route('/analytics/stock-trends', methods=['GET'])
@jwt_required()
@viewer_or_admin_required
def stock_trends():
    """Get stock movement trends (last 30 days)"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Get daily transaction summary
    trends = db.session.query(
        func.date(Transaction.created_at).label('date'),
        func.sum(case((Transaction.transaction_type == 'IN', Transaction.quantity), else_=0)).label('stock_in'),
        func.sum(case((Transaction.transaction_type == 'OUT', Transaction.quantity), else_=0)).label('stock_out')
    ).filter(
        Transaction.created_at >= thirty_days_ago
    ).group_by(
        func.date(Transaction.created_at)
    ).order_by('date').all()
    
    result = [{
        'date': str(row.date),
        'stock_in': int(row.stock_in or 0),
        'stock_out': int(row.stock_out or 0),
        'net_change': int((row.stock_in or 0) - (row.stock_out or 0))
    } for row in trends]
    
    return jsonify(result), 200

@analytics_bp.route('/analytics/top-items', methods=['GET'])
@jwt_required()
@viewer_or_admin_required
def top_items():
    """Get top items by value"""
    items = Item.query.order_by(desc(Item.quantity * Item.price)).limit(10).all()
    
    result = [{
        'id': item.id,
        'name': item.name,
        'category': item.category,
        'quantity': item.quantity,
        'price': item.price,
        'total_value': item.quantity * item.price
    } for item in items]
    
    return jsonify(result), 200

@analytics_bp.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
@viewer_or_admin_required
def dashboard_stats():
    """Get overall dashboard statistics"""
    total_items = Item.query.count()
    total_categories = db.session.query(func.count(func.distinct(Item.category))).scalar()
    total_value = db.session.query(func.sum(Item.quantity * Item.price)).scalar() or 0
    low_stock_count = Item.query.filter(Item.quantity <= Item.reorder_level).count()
    
    # Recent transactions
    recent_transactions = Transaction.query.order_by(
        Transaction.created_at.desc()
    ).limit(5).all()
    
    return jsonify({
        'total_items': total_items,
        'total_categories': total_categories,
        'total_inventory_value': float(total_value),
        'low_stock_alerts': low_stock_count,
        'recent_transactions': [t.to_dict() for t in recent_transactions]
    }), 200