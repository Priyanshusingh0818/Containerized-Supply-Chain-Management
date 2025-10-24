from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Item, Transaction
from utils.security import admin_required, viewer_or_admin_required

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions', methods=['GET'])
@jwt_required()
@viewer_or_admin_required
def get_transactions():
    """Get all transactions with optional filtering"""
    item_id = request.args.get('item_id', type=int)
    transaction_type = request.args.get('type')
    limit = request.args.get('limit', 100, type=int)
    
    query = Transaction.query
    
    if item_id:
        query = query.filter_by(item_id=item_id)
    
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    transactions = query.order_by(Transaction.created_at.desc()).limit(limit).all()
    return jsonify([t.to_dict() for t in transactions]), 200

@transactions_bp.route('/transactions/<int:transaction_id>', methods=['GET'])
@jwt_required()
@viewer_or_admin_required
def get_transaction(transaction_id):
    """Get single transaction by ID"""
    transaction = Transaction.query.get_or_404(transaction_id)
    return jsonify(transaction.to_dict()), 200

@transactions_bp.route('/transactions', methods=['POST'])
@jwt_required()
@admin_required
def create_transaction():
    """Create new transaction (IN or OUT)"""
    data = request.get_json()
    current_user = get_jwt_identity()
    
    # Validate required fields
    required = ['item_id', 'transaction_type', 'quantity']
    if not all(field in data for field in required):
        return jsonify({'message': 'Missing required fields'}), 400
    
    if data['transaction_type'] not in ['IN', 'OUT']:
        return jsonify({'message': 'Invalid transaction type. Use IN or OUT'}), 400
    
    # Get item
    item = Item.query.get_or_404(data['item_id'])
    
    # Check if sufficient stock for OUT transaction
    if data['transaction_type'] == 'OUT' and item.quantity < data['quantity']:
        return jsonify({'message': 'Insufficient stock'}), 400
    
    # Create transaction
    transaction = Transaction(
        item_id=data['item_id'],
        transaction_type=data['transaction_type'],
        quantity=data['quantity'],
        notes=data.get('notes', ''),
        created_by=current_user
    )
    
    # Update item quantity
    if data['transaction_type'] == 'IN':
        item.quantity += data['quantity']
    else:
        item.quantity -= data['quantity']
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 201

@transactions_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_transaction(transaction_id):
    """Delete transaction (admin only)"""
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transaction deleted successfully'}), 200