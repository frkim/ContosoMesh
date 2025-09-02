# ContosoMesh Agent Architecture Guide

This document provides a detailed technical overview of the multi-agent architecture powering the ContosoMesh supply management system.

## Architecture Overview

The ContosoMesh system employs a distributed agent architecture where each agent has specialized responsibilities and capabilities. All agents coordinate through a central Agent Manager that provides orchestration and communication services.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Agent Manager                               │
│                  (Orchestration Layer)                         │
└─────────────────────────────────────────────────────────────────┘
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│Order Agent  │Stocks Agent │Price Agent  │Delivery     │Datawarehouse│Quality Agent│
│(Orchestr.)  │(Inventory)  │(Pricing)    │Agent        │Agent        │(QA)         │
│             │             │             │(Reasoning)  │(Logistics)  │(Reasoning)  │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                   Shared Services Layer                         │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│   │  Database   │  │ Azure AI    │  │  WebSocket  │           │
│   │  (SQLite)   │  │   Search    │  │   Manager   │           │
│   └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Specifications

### 1. Order Agent (Orchestrator)
**File**: `backend/agents/order_agent.py`  
**Color**: Blue (`#2563eb`)  
**Type**: Orchestrator Agent

#### Responsibilities
- Primary entry point for all orders
- Workflow orchestration across all agents
- Order lifecycle management
- Status tracking and updates

#### Key Methods
- `create_order()` - Creates new orders with validation
- `orchestrate_order_processing()` - Coordinates the full workflow
- `get_order_status()` - Retrieves current order status
- `cancel_order()` - Handles order cancellation

#### Workflow Orchestration
```python
# Orchestration sequence
1. Order Creation & Validation
2. Delegate to Stocks Agent → Stock Check
3. Delegate to Price Agent → Pricing Calculation  
4. Delegate to Delivery Agent → Delivery Planning
5. Delegate to Datawarehouse Agent → Logistics Notification
6. Delegate to Quality Agent → Quality Assessment
7. Final Status Update
```

### 2. Stocks Agent
**File**: `backend/agents/stocks_agent.py`  
**Color**: Green (`#16a34a`)  
**Type**: Data Management Agent

#### Responsibilities
- Inventory tracking and management
- Stock availability verification
- Availability date calculations
- Stock reservation and updates

#### Key Methods
- `check_stocks()` - Validates item availability for orders
- `reserve_stock()` - Reserves inventory for confirmed orders
- `get_stock_status()` - Returns current stock levels
- `update_stock_levels()` - Updates inventory (replenishment)

#### Stock Logic
```python
def check_availability(product_id, quantity):
    if stock >= quantity:
        return "available"
    elif next_availability_date:
        return "out_of_stock" 
    else:
        # Calculate estimated restock
        estimated_days = (quantity - stock) // 10  # 10 units/day production
        return "low_stock"
```

### 3. Price Agent
**File**: `backend/agents/price_agent.py`  
**Color**: Red (`#dc2626`)  
**Type**: Business Logic Agent

#### Responsibilities
- Pricing calculations with discounts
- Quote generation
- Promotional pricing
- Cost optimization

#### Discount Strategies
```python
quantity_discounts = {
    10: 0.05,   # 5% for 10+ units
    25: 0.08,   # 8% for 25+ units  
    50: 0.12,   # 12% for 50+ units
    100: 0.15,  # 15% for 100+ units
    200: 0.20   # 20% for 200+ units
}

category_discounts = {
    "Smart Home Hub": 0.03,
    "Security Sensor": 0.05,
    "Smart Lighting": 0.04,
    "Environmental Sensor": 0.06
}
```

#### Key Methods
- `calculate_pricing()` - Full pricing with all discounts
- `calculate_custom_pricing()` - Special customer pricing
- `get_pricing_quote()` - Quote without order creation

### 4. Delivery Agent (Reasoning Model)
**File**: `backend/agents/delivery_agent.py`  
**Color**: Purple (`#7c3aed`)  
**Type**: Advanced Reasoning Agent

#### Responsibilities
- Intelligent delivery planning
- Parcel optimization using reasoning
- Shipping method selection
- Delivery timeline calculation

#### Reasoning Process
```python
def _reason_delivery_strategy(self, analysis):
    # Step 1: Analyze delay impact
    if max_delay > threshold: split_decision = True
    
    # Step 2: Analyze weight distribution  
    if total_weight > limit: split_decision = True
    
    # Step 3: Customer satisfaction reasoning
    satisfaction_benefit = available_items / total_items
    if satisfaction_benefit >= 0.6: split_decision = True
    
    # Step 4: Economic reasoning
    cost_impact = split_cost - single_cost
    if cost_impact > threshold: reconsider_decision()
    
    return strategy
```

#### Parcel Creation Strategies
- **Smart Split (Immediate + Delayed)**: Ship available items immediately
- **Weight-based Split**: Optimize for shipping constraints
- **Single Shipment**: Wait for all items when economical

### 5. Datawarehouse Agent
**File**: `backend/agents/datawarehouse_agent.py`  
**Color**: Orange (`#ea580c`)  
**Type**: Integration Agent

#### Responsibilities
- Warehouse management system integration
- Pick list generation
- Zone assignment and capacity tracking
- Shipping label creation

#### Warehouse Zones
```python
warehouse_zones = {
    "ZONE_A_ELECTRONICS": {
        "capacity": 1000, 
        "specialization": "Electronic devices"
    },
    "ZONE_B_SENSORS": {
        "capacity": 500,
        "specialization": "Sensors and small devices"  
    },
    "ZONE_C_SECURITY": {
        "capacity": 800,
        "specialization": "Security equipment"
    },
    "ZONE_D_LIGHTING": {
        "capacity": 600,
        "specialization": "Lighting and smart bulbs"
    }
}
```

#### Key Methods
- `notify_logistics()` - Main logistics platform integration
- `_generate_pick_list()` - Creates warehouse pick instructions
- `_assign_warehouse_zones()` - Assigns items to optimal zones
- `get_warehouse_status()` - Returns current warehouse metrics

### 6. Quality Agent (Advanced Reasoning)
**File**: `backend/agents/quality_agent.py`  
**Color**: Emerald (`#059669`)  
**Type**: Advanced Reasoning Agent

#### Responsibilities
- Comprehensive quality assessment
- Product compatibility analysis
- Risk assessment and mitigation
- Customer satisfaction prediction

#### Multi-Dimensional Analysis
```python
def perform_quality_check(self, order_id):
    # 1. Product Compatibility Analysis
    compatibility = self._analyze_product_compatibility(order)
    
    # 2. Risk Assessment (Financial, Fragility, Complexity, Availability)
    risks = self._perform_risk_assessment(order)
    
    # 3. Customer Satisfaction Prediction
    satisfaction = self._predict_customer_satisfaction(order)
    
    # 4. Setup Complexity Analysis  
    complexity = self._analyze_setup_complexity(order)
    
    # 5. Packaging Optimization
    packaging = self._analyze_packaging_optimization(order)
    
    # 6. Reasoning Synthesis
    quality_reasoning = self._reason_quality_assessment(...)
    
    return comprehensive_assessment
```

#### Quality Scoring
- **Weighted Score Calculation**: Combines all factors with business-relevant weights
- **Grade Assignment**: A+ to D based on overall score
- **Intervention Flags**: Automatic escalation for quality issues
- **Recommendations**: Actionable suggestions for improvement

## Agent Communication

### Message Passing
All agents communicate through standardized `AgentResponse` objects:

```python
class AgentResponse(BaseModel):
    agent_name: str
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime
```

### Logging System
Each agent maintains detailed activity logs:

```python
class AgentLog(BaseModel):
    agent_name: str
    action: str
    message: str
    timestamp: datetime
    order_id: Optional[str] = None
    color: str  # For UI display
```

### Error Handling
- **Graceful Degradation**: Agents continue operation even if others fail
- **Comprehensive Logging**: All errors captured with context
- **Rollback Capabilities**: Failed operations can be reversed
- **Monitoring Integration**: Real-time error notifications

## Reasoning Model Integration

### Delivery Agent Reasoning
The Delivery Agent employs sophisticated reasoning logic:

1. **Constraint Analysis**: Evaluates delivery requirements and limitations
2. **Multi-factor Decision Making**: Balances cost, time, and satisfaction
3. **Optimization Algorithms**: Finds optimal parcel configurations
4. **Dynamic Adaptation**: Adjusts strategies based on real-time data

### Quality Agent Reasoning  
The Quality Agent uses advanced analytical reasoning:

1. **Pattern Recognition**: Identifies problematic order patterns
2. **Predictive Analytics**: Forecasts customer satisfaction
3. **Risk Modeling**: Quantifies and prioritizes risks
4. **Recommendation Engine**: Generates actionable insights

## Scalability Considerations

### Horizontal Scaling
- **Agent Distribution**: Agents can run on separate processes/servers
- **Load Balancing**: Distribute agent workload across instances
- **Message Queues**: Asynchronous communication for high throughput

### Performance Optimization
- **Caching Strategies**: Frequent data cached at agent level
- **Database Optimization**: Indexed queries and connection pooling
- **Lazy Loading**: On-demand data retrieval
- **Background Processing**: Non-critical tasks processed asynchronously

### Monitoring and Observability
- **Real-time Metrics**: Agent performance and health monitoring
- **Distributed Tracing**: Track requests across agent boundaries
- **Log Aggregation**: Centralized logging with correlation IDs
- **Alert Systems**: Proactive notification of issues

## Extension Points

### Adding New Agents
1. Inherit from base agent pattern
2. Implement required interfaces
3. Register with Agent Manager
4. Define agent color and characteristics
5. Add to orchestration workflow

### Custom Reasoning Models
1. Implement reasoning interface
2. Define decision factors and weights
3. Add learning capabilities
4. Integration with existing agents

### External System Integration
1. Define integration contracts
2. Implement adapter patterns
3. Add monitoring and error handling
4. Test integration scenarios

This architecture provides a robust, scalable foundation for intelligent supply chain management with clear separation of concerns and extensibility for future enhancements.