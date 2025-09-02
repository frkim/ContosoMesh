# ContosoMesh - Multi-Agent Supply Management Demo

ContosoMesh is a comprehensive demo application showcasing a multi-agent supply management system for smart home devices. Built with Azure AI Agent Services, Azure AI Foundry, Azure AI Search, and Semantic Kernel in Python.

## 🏠 About ContosoMesh

ContosoMesh is a fictional company that builds cutting-edge electronic devices for smart homes, including sensors, connected door locks, smart switches, intelligent lights, and security cameras. The demo simulates a supply management solution for resellers ordering ContosoMesh products.

## 🤖 Multi-Agent Architecture

The system employs six specialized AI agents:

### 1. Order Agent (Orchestrator) 
- **Color**: Blue (`#2563eb`)
- **Role**: Main orchestrator agent that manages the complete order workflow
- **Capabilities**: 
  - Accept orders with product items and quantities
  - Coordinate with other agents
  - Track order status throughout the process
  - Handle order cancellations

### 2. Stocks Agent
- **Color**: Green (`#16a34a`) 
- **Role**: Manages inventory and availability checking
- **Capabilities**:
  - Check product availability for each order item
  - Provide next availability dates for out-of-stock items
  - Reserve stock for confirmed orders
  - Update stock levels for replenishment

### 3. Price Agent
- **Color**: Red (`#dc2626`)
- **Role**: Handles pricing calculations and discount strategies
- **Capabilities**:
  - Calculate item prices with quantity discounts
  - Apply category-based discounts for bulk orders
  - Generate pricing quotes without creating orders
  - Support custom pricing for special customers

### 4. Delivery Agent (Reasoning Model)
- **Color**: Purple (`#7c3aed`)
- **Role**: Advanced reasoning agent for optimal delivery planning
- **Capabilities**:
  - Use reasoning to create optimal delivery parcels
  - Split orders based on availability (items delayed >3 days)
  - Weight-based parcel optimization
  - Select optimal shipping methods (express/standard/economy)
  - Calculate delivery timelines

### 5. Datawarehouse Agent
- **Color**: Orange (`#ea580c`)
- **Role**: Interfaces with logistics platform for order preparation
- **Capabilities**:
  - Generate pick lists for warehouse workers
  - Assign items to warehouse zones by category
  - Create packing instructions based on product types
  - Generate shipping labels and tracking numbers
  - Update warehouse capacity and utilization

### 6. Quality Agent (Advanced Reasoning)
- **Color**: Emerald (`#059669`)
- **Role**: Advanced reasoning agent for comprehensive quality control
- **Capabilities**:
  - Analyze product compatibility within orders
  - Perform multi-dimensional risk assessment
  - Predict customer satisfaction
  - Evaluate setup complexity for customers
  - Generate quality scores and recommendations

## 📦 Product Catalog

The demo includes 12 ContosoMesh smart home products inspired by SwitchBot devices:

| Product ID | Name | Category | Price | Stock |
|------------|------|----------|-------|-------|
| SW-001 | SwitchBot Hub Mini | Smart Home Hub | $49.99 | 150 |
| SW-002 | SwitchBot Bot | Smart Switch | $29.99 | 85 |
| SW-003 | SwitchBot Curtain | Smart Curtain | $89.99 | 12 |
| SW-004 | SwitchBot Contact Sensor | Security Sensor | $19.99 | 200 |
| SW-005 | SwitchBot Motion Sensor | Security Sensor | $24.99 | 75 |
| SW-006 | SwitchBot Lock Pro | Smart Lock | $199.99 | 3 |
| SW-007 | SwitchBot Meter | Environmental Sensor | $15.99 | 120 |
| SW-008 | SwitchBot Outdoor Meter | Environmental Sensor | $19.99 | 45 |
| SW-009 | SwitchBot Color Bulb | Smart Lighting | $12.99 | 95 |
| SW-010 | SwitchBot Indoor Cam | Security Camera | $39.99 | 0 |
| SW-011 | SwitchBot Blind Tilt | Smart Blinds | $69.99 | 25 |
| SW-012 | SwitchBot Plug Mini | Smart Plug | $14.99 | 180 |

## 🔄 Order Processing Workflow

1. **Order Creation**: Customer submits order with multiple products
2. **Stock Check**: Stocks Agent verifies availability and provides alternatives
3. **Pricing**: Price Agent calculates total with applicable discounts
4. **Delivery Planning**: Delivery Agent uses reasoning to optimize parcels
5. **Warehouse Notification**: Datawarehouse Agent prepares logistics
6. **Quality Check**: Quality Agent performs comprehensive assessment

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or later
- Windows (PowerShell scripts provided)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/frkim/ContosoMesh.git
   cd ContosoMesh
   ```

2. **Run setup script**
   ```powershell
   .\scripts\setup.ps1
   ```

3. **Start the application**
   ```powershell
   .\scripts\run.ps1
   ```

4. **Access the application**
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

### Generate Demo Data

```powershell
.\scripts\demo-data.ps1
```

## 🌐 Web Interface Features

### Product Catalog
- Browse all ContosoMesh products
- Search by name, description, or category
- Filter by category and stock availability
- Add products to shopping cart

### Order Management
- View all orders with status tracking
- Create new orders with multiple products
- Real-time order status updates
- Order cancellation capability

### Warehouse Dashboard
- View warehouse zone utilization
- Monitor capacity and current load
- Track zone specializations and status

### Real-time Agent Activity
- Collapsible panel showing agent activity
- Color-coded agent identification
- Live agent action logging
- Activity statistics and metrics

## 🔧 API Endpoints

### Products
- `GET /api/products` - Get all products
- `GET /api/products/{id}` - Get specific product
- `GET /api/products/search` - Search products

### Orders
- `POST /api/orders` - Create new order (triggers full workflow)
- `GET /api/orders` - Get all orders
- `GET /api/orders/{id}` - Get comprehensive order status
- `DELETE /api/orders/{id}` - Cancel order

### Pricing
- `POST /api/quote` - Get pricing quote without creating order

### Warehouse
- `GET /api/warehouse/status` - Get warehouse status
- `PUT /api/stocks` - Update stock levels

### Agent Activity
- `GET /api/agents/logs` - Get agent activity logs
- `GET /api/agents/statistics` - Get agent statistics
- `DELETE /api/agents/logs` - Clear agent logs

### Real-time Updates
- `WS /ws/agent-logs` - WebSocket for real-time agent activity

## 🎨 Intelligent Features

### Delivery Agent Reasoning
The Delivery Agent uses advanced reasoning to:
- Analyze delivery requirements and constraints
- Decide when to split orders into multiple parcels
- Optimize parcel weight distribution
- Consider customer satisfaction vs. cost factors
- Select optimal shipping methods

### Quality Agent Analysis
The Quality Agent performs:
- Product compatibility analysis
- Multi-factor risk assessment
- Customer satisfaction prediction
- Setup complexity evaluation
- Packaging optimization

### Pricing Intelligence
- Quantity-based discount tiers (5% to 20%)
- Category-specific bulk discounts
- Custom pricing for premium customers
- Real-time pricing calculations

## 📊 Demo Scenarios

### Scenario 1: Standard Order
- Customer orders hub + accessories
- All items in stock
- Single shipment with standard pricing

### Scenario 2: Complex Order with Delays
- Large reseller order with mix of products
- Some items out of stock (delayed delivery)
- Agent reasoning splits into multiple parcels
- Quality agent identifies potential issues

### Scenario 3: High-Value Premium Order
- Premium customer with expensive items
- Enhanced packaging and handling
- Quality agent flags for special attention
- Express shipping recommended

## 🛠️ Technology Stack

- **Backend**: FastAPI with Python 3.11+
- **Database**: SQLite with custom ORM
- **Search**: Azure AI Search (with mock fallback)
- **AI Agents**: Semantic Kernel framework
- **Frontend**: HTML5 with Alpine.js and Tailwind CSS
- **Real-time**: WebSockets for live updates
- **Deployment**: Uvicorn ASGI server

## 🔒 Environment Configuration

Create a `.env` file with Azure credentials (optional):

```env
# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-search-key

# Azure OpenAI (for advanced reasoning)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Database
DATABASE_PATH=contoso_mesh.db
```

The demo works fully with mock services if Azure credentials are not provided.

## 📈 Monitoring and Logging

- Real-time agent activity monitoring
- Color-coded agent identification
- Activity statistics and metrics
- Comprehensive order tracking
- Warehouse utilization monitoring

## 🎯 Business Value Demonstration

This demo showcases:
- **Multi-agent coordination** for complex business processes
- **Intelligent reasoning** for operational optimization
- **Real-time monitoring** of automated systems
- **Scalable architecture** for enterprise scenarios
- **User-friendly interfaces** for business users

## 🤝 Contributing

This is a demonstration project. For improvements or suggestions, please create issues or pull requests.

## 📄 License

MIT License - see LICENSE file for details.

---

*ContosoMesh - Demonstrating the future of intelligent supply chain management with Azure AI Agent Services.*