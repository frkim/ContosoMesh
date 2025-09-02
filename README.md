# ContosoMesh - Multi-Agent Supply Management Demo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com)
[![Azure AI](https://img.shields.io/badge/Azure_AI-0078D4?logo=microsoftazure)](https://azure.microsoft.com/en-us/products/ai-services)

A comprehensive demonstration of multi-agent supply management using Azure AI Agent Services, Azure AI Foundry, Azure AI Search, and Semantic Kernel in Python.

## 🏠 About ContosoMesh

ContosoMesh is a fictional company that builds cutting-edge smart home devices with appealing design and advanced functionality. This demo simulates a realistic supply management solution for resellers ordering ContosoMesh products through an intelligent multi-agent system.

### Featured Products
- **Smart Home Hubs** - Central control for all devices
- **Security Sensors** - Motion, contact, and environmental monitoring  
- **Smart Locks** - Keyless entry with multiple unlock methods
- **Intelligent Lighting** - RGB bulbs with automation features
- **Connected Switches** - Transform any appliance into a smart device
- **Environmental Sensors** - Temperature, humidity, and air quality monitoring

## 🤖 Multi-Agent System

### Six Specialized AI Agents

| Agent | Role | Reasoning Type | Key Capabilities |
|-------|------|----------------|------------------|
| **Order Agent** | Orchestrator | Workflow | Order management, agent coordination |
| **Stocks Agent** | Inventory | Data-driven | Availability checking, stock management |
| **Price Agent** | Pricing | Business logic | Dynamic pricing, discount strategies |
| **Delivery Agent** | Logistics | Advanced reasoning | Parcel optimization, shipping strategy |
| **Datawarehouse Agent** | Operations | Integration | Warehouse management, logistics |
| **Quality Agent** | Quality Control | Advanced reasoning | Risk assessment, satisfaction prediction |

### Real-time Collaboration
- **Orchestrated Workflows**: Seamless coordination between agents
- **Intelligent Decision Making**: Advanced reasoning for optimal outcomes
- **Live Activity Monitoring**: Real-time visibility into agent operations
- **Color-coded Identification**: Visual agent activity tracking

## ✨ Key Features

### 🛒 Order Management
- **Multi-product Orders**: Support for complex orders with multiple items
- **Real-time Processing**: Live order status updates through the workflow
- **Intelligent Orchestration**: Agents collaborate automatically
- **Order Tracking**: Complete visibility from creation to fulfillment

### 🧠 Advanced Reasoning
- **Delivery Optimization**: Smart parcel creation based on availability and constraints
- **Quality Assessment**: Multi-dimensional analysis of order quality and risk
- **Customer Satisfaction Prediction**: Proactive satisfaction forecasting
- **Cost-Benefit Analysis**: Economic reasoning for optimal decisions

### 📊 Business Intelligence
- **Dynamic Pricing**: Quantity and category-based discount strategies
- **Inventory Management**: Real-time stock tracking and availability
- **Warehouse Optimization**: Zone-based storage and pick optimization
- **Risk Management**: Comprehensive risk assessment and mitigation

### 🌐 Modern Web Interface
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Live agent activity and order status
- **Interactive Catalog**: Product browsing with search and filtering
- **Dashboard Analytics**: Warehouse status and performance metrics

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Windows** - PowerShell scripts provided (Linux/Mac coming soon)
- **Git** - For cloning the repository

### 1. Clone and Setup
```powershell
# Clone the repository
git clone https://github.com/frkim/ContosoMesh.git
cd ContosoMesh

# Run the automated setup
.\scripts\setup.ps1
```

### 2. Start the Application
```powershell
# Start the server
.\scripts\run.ps1
```

### 3. Access the Demo
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/api/health

### 4. Generate Demo Data
```powershell
# Create sample orders (run in another terminal)
.\scripts\demo-data.ps1
```

## 🎯 Demo Scenarios

### Scenario 1: Simple Smart Home Setup
**Customer**: Home enthusiast  
**Order**: Hub + sensors + smart bulbs  
**Outcome**: Single shipment, standard pricing, high satisfaction

### Scenario 2: Complex Reseller Order  
**Customer**: Technology reseller  
**Order**: Multiple hubs, security equipment, bulk quantities  
**Outcome**: Split shipment, bulk discounts, quality assessment

### Scenario 3: Premium Security System
**Customer**: Premium customer  
**Order**: High-value security devices with delayed items  
**Outcome**: Reasoning-based delivery planning, enhanced packaging

### Scenario 4: Out-of-Stock Challenge
**Customer**: Large order with unavailable items  
**Outcome**: Smart parcel splitting, alternative recommendations

## 📱 User Interface

### Product Catalog
- **Search and Filter**: Find products by name, category, or features
- **Stock Visibility**: Real-time inventory levels
- **Smart Cart**: Easy product selection with quantity management

### Order Dashboard  
- **Status Tracking**: Visual order progression through agent workflow
- **Order History**: Complete order management and cancellation
- **Real-time Updates**: Live status changes and notifications

### Agent Activity Panel
- **Live Monitoring**: Real-time agent activity with color coding
- **Activity Logs**: Detailed action history and decision rationale
- **Performance Metrics**: Agent statistics and system health

### Warehouse Management
- **Zone Utilization**: Visual warehouse capacity monitoring
- **Performance Tracking**: Efficiency metrics and optimization opportunities

## 🔧 Technical Architecture

### Backend Services
- **FastAPI**: High-performance Python web framework
- **SQLite**: Embedded database for demo data
- **WebSockets**: Real-time communication for live updates
- **Semantic Kernel**: Agent framework and coordination

### Agent Framework
- **Modular Design**: Independent agents with clear responsibilities  
- **Message Passing**: Structured communication between agents
- **Error Handling**: Graceful degradation and error recovery
- **Extensibility**: Easy addition of new agents and capabilities

### Azure Integration
- **Azure AI Search**: Product indexing and intelligent search (with mock fallback)
- **Azure AI Foundry**: Agent development and deployment platform
- **Azure OpenAI**: Advanced reasoning capabilities for intelligent agents

### Frontend Technology
- **Alpine.js**: Reactive user interface framework
- **Tailwind CSS**: Utility-first styling for responsive design
- **Real-time Updates**: WebSocket integration for live data

## 📚 Documentation

- **[Architecture Guide](documentation/ARCHITECTURE.md)** - Detailed technical architecture
- **[Complete Documentation](documentation/README.md)** - Comprehensive feature guide
- **[API Reference](http://localhost:8000/docs)** - Interactive API documentation (when running)

## 🛠️ Configuration

### Environment Variables (Optional)
```env
# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-search-key

# Azure OpenAI (for advanced reasoning)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

*Note: The demo works fully with mock services if Azure credentials are not provided.*

## 🎨 Screenshots

### Product Catalog
![Product Catalog](https://via.placeholder.com/800x400/2563eb/ffffff?text=Product+Catalog+with+Smart+Search)

### Order Processing
![Order Processing](https://via.placeholder.com/800x400/16a34a/ffffff?text=Real-time+Agent+Orchestration)

### Agent Activity
![Agent Activity](https://via.placeholder.com/800x400/7c3aed/ffffff?text=Live+Agent+Activity+Monitoring)

## 🔄 API Endpoints

### Core Operations
```http
POST /api/orders          # Create order (triggers full workflow)
GET  /api/orders          # List all orders
GET  /api/orders/{id}     # Get comprehensive order status
DELETE /api/orders/{id}   # Cancel order

GET  /api/products        # Browse product catalog
GET  /api/products/search # Intelligent product search
POST /api/quote          # Get pricing quote

WS   /ws/agent-logs      # Real-time agent activity stream
```

## 🎯 Business Value

This demo showcases:
- **Intelligent Automation**: Multi-agent coordination for complex processes
- **Advanced Reasoning**: AI-powered decision making and optimization  
- **Real-time Visibility**: Complete transparency into automated operations
- **Scalable Architecture**: Enterprise-ready design patterns
- **User Experience**: Intuitive interfaces for business users

## 🤝 Contributing

This is a demonstration project. Contributions, suggestions, and feedback are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by SwitchBot's innovative smart home devices
- Built with Azure AI Agent Services and Semantic Kernel
- Designed for the Azure AI Foundry platform

---

**ContosoMesh** - *Demonstrating the future of intelligent supply chain management with Azure AI Agent Services.*

[🏠 Live Demo](http://localhost:8000) | [📖 Documentation](documentation/) | [🤖 Agent Architecture](documentation/ARCHITECTURE.md)
