from models import db, Audit
from flask import current_app
from flask_socketio import emit
import json

def log_audit(action, resource_type, resource_id, user_id, changes=None):
    """
    Log an audit entry and emit a socket event
    
    Args:
        action (str): The action performed (CREATE, UPDATE, DELETE)
        resource_type (str): The type of resource (Item, Transaction, etc.)
        resource_id (int): The ID of the resource
        user_id (int): The ID of the user performing the action
        changes (dict, optional): Dictionary of changes made
    """
    audit = Audit(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        changes=json.dumps(changes) if changes else None
    )
    
    db.session.add(audit)
    db.session.commit()
    
    # Emit socket event with audit information
    socket_data = {
        'type': f'{resource_type.lower()}_changed',
        'action': action,
        'resource_id': resource_id,
        'audit': audit.to_dict()
    }
    
    current_app.socketio.emit('inventory_update', socket_data, broadcast=True)