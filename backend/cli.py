#!/usr/bin/env python3
import typer
import os
import requests
from typing import Optional
from dotenv import load_dotenv
from utils.backup import create_backup, restore_backup

# Load environment variables
load_dotenv()

app = typer.Typer(help="InvGuard CLI - Inventory Management Command Line Interface")

# Configuration
API_URL = os.getenv('API_URL', 'http://localhost:5000/api')
DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/inventory.db')
BACKUP_PATH = os.getenv('BACKUP_PATH', '/app/backups')
GPG_PASSPHRASE = os.getenv('GPG_PASSPHRASE', 'default_passphrase')

# Global token storage (in production, use secure storage)
TOKEN_FILE = '/tmp/invguard_token'

def get_headers():
    """Get authorization headers with JWT token"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            token = f.read().strip()
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    return {'Content-Type': 'application/json'}

def save_token(token):
    """Save JWT token to file"""
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)
    os.chmod(TOKEN_FILE, 0o600)

@app.command()
def login(username: str, password: str):
    """Login to InvGuard system"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={'username': username, 'password': password}
        )
        
        if response.status_code == 200:
            data = response.json()
            save_token(data['access_token'])
            typer.echo(f"✓ Login successful! Welcome {data['user']['username']} ({data['user']['role']})")
        else:
            typer.echo(f"✗ Login failed: {response.json().get('message', 'Unknown error')}", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

@app.command()
def add_item(
    name: str,
    sku: str,
    category: str,
    quantity: int,
    price: float,
    reorder_level: int = 10,
    description: str = ""
):
    """Add a new item to inventory"""
    try:
        response = requests.post(
            f"{API_URL}/items",
            headers=get_headers(),
            json={
                'name': name,
                'sku': sku,
                'category': category,
                'quantity': quantity,
                'price': price,
                'reorder_level': reorder_level,
                'description': description
            }
        )
        
        if response.status_code == 201:
            item = response.json()
            typer.echo(f"✓ Item added successfully! ID: {item['id']}, SKU: {item['sku']}")
        else:
            typer.echo(f"✗ Failed to add item: {response.json().get('message', 'Unknown error')}", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

@app.command()
def update_item(
    item_id: int,
    name: Optional[str] = None,
    category: Optional[str] = None,
    quantity: Optional[int] = None,
    price: Optional[float] = None,
    reorder_level: Optional[int] = None,
    description: Optional[str] = None
):
    """Update an existing item"""
    try:
        data = {}
        if name: data['name'] = name
        if category: data['category'] = category
        if quantity is not None: data['quantity'] = quantity
        if price is not None: data['price'] = price
        if reorder_level is not None: data['reorder_level'] = reorder_level
        if description is not None: data['description'] = description
        
        response = requests.put(
            f"{API_URL}/items/{item_id}",
            headers=get_headers(),
            json=data
        )
        
        if response.status_code == 200:
            item = response.json()
            typer.echo(f"✓ Item updated successfully! {item['name']} (ID: {item['id']})")
        else:
            typer.echo(f"✗ Failed to update item: {response.json().get('message', 'Unknown error')}", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

@app.command()
def delete_item(item_id: int):
    """Delete an item from inventory"""
    try:
        confirm = typer.confirm(f"Are you sure you want to delete item ID {item_id}?")
        if not confirm:
            typer.echo("Operation cancelled")
            return
        
        response = requests.delete(
            f"{API_URL}/items/{item_id}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            typer.echo(f"✓ Item deleted successfully!")
        else:
            typer.echo(f"✗ Failed to delete item: {response.json().get('message', 'Unknown error')}", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

@app.command()
def view_item(item_id: Optional[int] = None):
    """View item details or list all items"""
    try:
        if item_id:
            response = requests.get(
                f"{API_URL}/items/{item_id}",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                item = response.json()
                typer.echo("\n" + "="*60)
                typer.echo(f"ID: {item['id']}")
                typer.echo(f"Name: {item['name']}")
                typer.echo(f"SKU: {item['sku']}")
                typer.echo(f"Category: {item['category']}")
                typer.echo(f"Quantity: {item['quantity']}")
                typer.echo(f"Price: ${item['price']:.2f}")
                typer.echo(f"Reorder Level: {item['reorder_level']}")
                typer.echo(f"Description: {item['description']}")
                typer.echo("="*60 + "\n")
            else:
                typer.echo(f"✗ Failed to get item: {response.json().get('message', 'Unknown error')}", err=True)
        else:
            response = requests.get(
                f"{API_URL}/items",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                items = response.json()
                typer.echo(f"\n{'ID':<5} {'SKU':<12} {'Name':<30} {'Category':<15} {'Qty':<6} {'Price':<10}")
                typer.echo("="*85)
                for item in items:
                    typer.echo(
                        f"{item['id']:<5} {item['sku']:<12} {item['name']:<30} "
                        f"{item['category']:<15} {item['quantity']:<6} ${item['price']:<9.2f}"
                    )
                typer.echo(f"\nTotal items: {len(items)}\n")
            else:
                typer.echo(f"✗ Failed to get items: {response.json().get('message', 'Unknown error')}", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

@app.command()
def log_transaction(
    item_id: int,
    transaction_type: str,
    quantity: int,
    notes: str = ""
):
    """Log a stock transaction (IN or OUT)"""
    try:
        if transaction_type.upper() not in ['IN', 'OUT']:
            typer.echo("✗ Transaction type must be IN or OUT", err=True)
            return
        
        response = requests.post(
            f"{API_URL}/transactions",
            headers=get_headers(),
            json={
                'item_id': item_id,
                'transaction_type': transaction_type.upper(),
                'quantity': quantity,
                'notes': notes
            }
        )
        
        if response.status_code == 201:
            transaction = response.json()
            typer.echo(f"✓ Transaction logged successfully! ID: {transaction['id']}")
            typer.echo(f"  Item: {transaction['item_name']}")
            typer.echo(f"  Type: {transaction['transaction_type']}")
            typer.echo(f"  Quantity: {transaction['quantity']}")
        else:
            typer.echo(f"✗ Failed to log transaction: {response.json().get('message', 'Unknown error')}", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

@app.command()
def view_transactions(limit: int = 20):
    """View recent transactions"""
    try:
        response = requests.get(
            f"{API_URL}/transactions?limit={limit}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            transactions = response.json()
            typer.echo(f"\n{'ID':<5} {'Item':<30} {'Type':<6} {'Qty':<6} {'Date':<20} {'User':<15}")
            typer.echo("="*90)
            for t in transactions:
                typer.echo(
                    f"{t['id']:<5} {t['item_name']:<30} {t['transaction_type']:<6} "
                    f"{t['quantity']:<6} {t['created_at']:<20} {t['created_by'] or 'N/A':<15}"
                )
            typer.echo(f"\nTotal transactions: {len(transactions)}\n")
        else:
            typer.echo(f"✗ Failed to get transactions: {response.json().get('message', 'Unknown error')}", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

@app.command()
def backup_db(encrypt: bool = True):
    """Create encrypted backup of database"""
    try:
        backup_file = create_backup(
            DATABASE_PATH,
            BACKUP_PATH,
            encrypt=encrypt,
            passphrase=GPG_PASSPHRASE if encrypt else None
        )
        
        if backup_file:
            typer.echo(f"✓ Backup created successfully: {backup_file}")
        else:
            typer.echo("✗ Backup failed", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

@app.command()
def restore_db(backup_file: str):
    """Restore database from backup"""
    try:
        confirm = typer.confirm("This will overwrite the current database. Continue?")
        if not confirm:
            typer.echo("Operation cancelled")
            return
        
        success = restore_backup(
            backup_file,
            DATABASE_PATH,
            passphrase=GPG_PASSPHRASE if backup_file.endswith('.gpg') else None
        )
        
        if success:
            typer.echo("✓ Database restored successfully")
        else:
            typer.echo("✗ Restore failed", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

@app.command()
def low_stock():
    """Show items with low stock"""
    try:
        response = requests.get(
            f"{API_URL}/analytics/low-stock",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            items = response.json()
            if items:
                typer.echo(f"\n{'Name':<30} {'SKU':<12} {'Current':<10} {'Reorder':<10} {'Shortage':<10}")
                typer.echo("="*75)
                for item in items:
                    typer.echo(
                        f"{item['name']:<30} {item['sku']:<12} {item['current_stock']:<10} "
                        f"{item['reorder_level']:<10} {item['shortage']:<10}"
                    )
                typer.echo(f"\n⚠ Total low stock items: {len(items)}\n")
            else:
                typer.echo("✓ No low stock items found")
        else:
            typer.echo(f"✗ Failed to get low stock items: {response.json().get('message', 'Unknown error')}", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

@app.command()
def dashboard():
    """Show dashboard statistics"""
    try:
        response = requests.get(
            f"{API_URL}/analytics/dashboard",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            stats = response.json()
            typer.echo("\n" + "="*60)
            typer.echo("INVGUARD DASHBOARD")
            typer.echo("="*60)
            typer.echo(f"Total Items: {stats['total_items']}")
            typer.echo(f"Total Categories: {stats['total_categories']}")
            typer.echo(f"Total Inventory Value: ${stats['total_inventory_value']:.2f}")
            typer.echo(f"Low Stock Alerts: {stats['low_stock_alerts']}")
            typer.echo("="*60 + "\n")
        else:
            typer.echo(f"✗ Failed to get dashboard stats: {response.json().get('message', 'Unknown error')}", err=True)
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)

if __name__ == "__main__":
    app()