# ContosoMesh Demo Data Generator
# This script populates the system with demo orders for testing

Write-Host "🏠 ContosoMesh Demo Data Generator" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue

# Activate virtual environment
if (Test-Path "venv") {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "❌ Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "📦 Generating demo data..." -ForegroundColor Yellow

# Generate demo orders using Python
python -c "
import requests
import time
import json

# Demo customers and orders
demo_orders = [
    {
        'customer_name': 'Alice Johnson',
        'customer_email': 'alice.johnson@email.com',
        'items': [
            {'product_id': 'SW-001', 'quantity': 1},  # Hub
            {'product_id': 'SW-002', 'quantity': 2},  # Bot
            {'product_id': 'SW-007', 'quantity': 3}   # Meter
        ]
    },
    {
        'customer_name': 'Bob Smith - Premium Customer',
        'customer_email': 'bob.smith@premium.com',
        'items': [
            {'product_id': 'SW-006', 'quantity': 1},  # Lock (out of stock)
            {'product_id': 'SW-004', 'quantity': 5},  # Contact sensors
            {'product_id': 'SW-005', 'quantity': 3}   # Motion sensors
        ]
    },
    {
        'customer_name': 'Carol Williams - Tech Reseller',
        'customer_email': 'carol@smarttech.com',
        'items': [
            {'product_id': 'SW-001', 'quantity': 2},  # Hubs
            {'product_id': 'SW-003', 'quantity': 1},  # Curtain (out of stock)
            {'product_id': 'SW-009', 'quantity': 10}, # Bulbs
            {'product_id': 'SW-012', 'quantity': 15}  # Plugs
        ]
    },
    {
        'customer_name': 'David Chen - Security Focus',
        'customer_email': 'david.chen@security.com',
        'items': [
            {'product_id': 'SW-001', 'quantity': 1},  # Hub
            {'product_id': 'SW-010', 'quantity': 2},  # Camera (out of stock)
            {'product_id': 'SW-006', 'quantity': 1},  # Lock
            {'product_id': 'SW-004', 'quantity': 8},  # Contact sensors
            {'product_id': 'SW-005', 'quantity': 4}   # Motion sensors
        ]
    },
    {
        'customer_name': 'Emma Davis - Smart Home Enthusiast',
        'customer_email': 'emma.davis@gmail.com',
        'items': [
            {'product_id': 'SW-001', 'quantity': 1},  # Hub
            {'product_id': 'SW-002', 'quantity': 4},  # Bots
            {'product_id': 'SW-007', 'quantity': 6},  # Meters
            {'product_id': 'SW-008', 'quantity': 2},  # Outdoor meters
            {'product_id': 'SW-009', 'quantity': 8},  # Bulbs
            {'product_id': 'SW-011', 'quantity': 2},  # Blind tilts
            {'product_id': 'SW-012', 'quantity': 10}  # Plugs
        ]
    }
]

print('Creating demo orders...')
created_orders = []

for i, order in enumerate(demo_orders, 1):
    print(f'Creating order {i}/5: {order[\"customer_name\"]}')
    
    # Simulate the order creation
    try:
        response = requests.post('http://localhost:8000/api/orders', 
                               json=order, 
                               timeout=60)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                created_orders.append(result['order_id'])
                print(f'  ✅ Order created: {result[\"order_id\"]}')
            else:
                print(f'  ❌ Order failed: {result.get(\"message\", \"Unknown error\")}')
        else:
            print(f'  ❌ HTTP Error: {response.status_code}')
    except requests.exceptions.ConnectionError:
        print(f'  ⚠️  Server not running. Please start the server first with run.ps1')
        break
    except Exception as e:
        print(f'  ❌ Error: {e}')
    
    # Wait between orders to see the agent activity
    if i < len(demo_orders):
        print('    Waiting 3 seconds...')
        time.sleep(3)

print(f'\\n✅ Demo data generation complete!')
print(f'   Created {len(created_orders)} orders')
print(f'   Order IDs: {created_orders}')
print(f'\\n🌐 View results at: http://localhost:8000')
"

Write-Host ""
Write-Host "✅ Demo data generation completed!" -ForegroundColor Green
Write-Host "   Open http://localhost:8000 to see the results" -ForegroundColor Yellow