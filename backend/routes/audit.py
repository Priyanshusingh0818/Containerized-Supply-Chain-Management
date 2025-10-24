from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Audit
from utils.security import admin_required

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit', methods=['GET'])
@jwt_required()
@admin_required
def get_audit_logs():
    """Get audit logs with optional filtering"""
    logs = Audit.query.order_by(Audit.timestamp.desc()).limit(100).all()
    return jsonify([log.to_dict() for log in logs]), 200

@audit_bp.route('/audit/resource/<string:resource_type>/<int:resource_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_resource_audit_logs(resource_type, resource_id):
    """Get audit logs for a specific resource"""
    logs = Audit.query.filter_by(
        resource_type=resource_type,
        resource_id=resource_id
    ).order_by(Audit.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs]), 200