"""
ContosoMesh FastAPI Backend - Main application server.
Provides REST API endpoints for the multi-agent supply management system.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import os

# Import our components
from database.db import Database
from search.azure_search import AzureSearchService  
from agents.agent_manager import AgentManager
from models.schemas import Order, Product

# Initialize FastAPI app
app = FastAPI(
    title="ContosoMesh Supply Management API",
    description="Multi-agent supply management system for ContosoMesh smart home devices",
    version="1.0.0"
)

# Initialize services
database = Database()
search_service = AzureSearchService()
agent_manager = AgentManager(database, search_service)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
templates = Jinja2Templates(directory="../frontend/templates")

# Index products in search service
products = database.get_products()
search_service.index_products(products)

# WebSocket connections for real-time agent logs
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

websocket_manager = ConnectionManager()

# Pydantic models for API requests
class OrderCreateRequest(BaseModel):
    customer_name: str
    customer_email: str
    items: List[Dict[str, Any]]  # List of {product_id, quantity}

class PriceQuoteRequest(BaseModel):
    items: List[Dict[str, Any]]  # List of {product_id, quantity}

class StockUpdateRequest(BaseModel):
    updates: List[Dict[str, Any]]  # List of {product_id, new_stock}

# HTML Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with product catalog."""
    products = database.get_products()
    orders = database.get_orders()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "products": [product.dict() for product in products],
        "orders": [order.dict() for order in orders[:10]],  # Latest 10 orders
        "agent_stats": agent_manager.get_agent_statistics()
    })

# API Routes

# Product endpoints
@app.get("/api/products")
async def get_products(category: Optional[str] = None):
    """Get all products, optionally filtered by category."""
    try:
        products = database.get_products(category)
        return {"products": [product.dict() for product in products]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get a specific product by ID."""
    try:
        product = database.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/search")
async def search_products(q: str = "", category: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, in_stock: Optional[bool] = None):
    """Search products using Azure AI Search."""
    try:
        filters = {}
        if category:
            filters["category"] = category
        if min_price is not None:
            filters["min_price"] = min_price
        if max_price is not None:
            filters["max_price"] = max_price
        if in_stock is not None:
            filters["in_stock"] = in_stock
        
        results = agent_manager.search_products(q, filters)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Order endpoints
@app.post("/api/orders")
async def create_order(request: OrderCreateRequest):
    """Create a new order and process it through all agents."""
    try:
        result = agent_manager.process_order_full_workflow(
            request.customer_name,
            request.customer_email,
            request.items
        )
        
        # Broadcast agent activity to WebSocket clients
        await websocket_manager.broadcast(json.dumps({
            "type": "order_created",
            "order_id": result.get("order_id"),
            "timestamp": datetime.now().isoformat()
        }))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders")
async def get_orders():
    """Get all orders."""
    try:
        orders = database.get_orders()
        return {"orders": [order.dict() for order in orders]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """Get comprehensive order status from all agents."""
    try:
        result = agent_manager.get_order_status_comprehensive(order_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/orders/{order_id}")
async def cancel_order(order_id: str, reason: str = "Customer request"):
    """Cancel an order."""
    try:
        result = agent_manager.cancel_order(order_id, reason)
        
        # Broadcast to WebSocket clients
        await websocket_manager.broadcast(json.dumps({
            "type": "order_cancelled",
            "order_id": order_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Pricing endpoints
@app.post("/api/quote")
async def get_price_quote(request: PriceQuoteRequest):
    """Get a pricing quote without creating an order."""
    try:
        result = agent_manager.get_pricing_quote(request.items)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stock management endpoints
@app.put("/api/stocks")
async def update_stocks(request: StockUpdateRequest):
    """Update stock levels (for demo purposes)."""
    try:
        result = agent_manager.update_stock_levels(request.updates)
        
        # Broadcast to WebSocket clients
        await websocket_manager.broadcast(json.dumps({
            "type": "stocks_updated",
            "count": len(request.updates),
            "timestamp": datetime.now().isoformat()
        }))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Warehouse endpoints
@app.get("/api/warehouse/status")
async def get_warehouse_status():
    """Get current warehouse status."""
    try:
        result = agent_manager.get_warehouse_status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Agent activity endpoints
@app.get("/api/agents/logs")
async def get_agent_logs(since: Optional[str] = None):
    """Get agent activity logs."""
    try:
        if since:
            since_dt = datetime.fromisoformat(since)
            logs = agent_manager.get_agent_logs_since(since_dt)
        else:
            logs = agent_manager.get_all_agent_logs()
        
        return {"logs": [log.dict() for log in logs]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/statistics")
async def get_agent_statistics():
    """Get agent activity statistics."""
    try:
        stats = agent_manager.get_agent_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/agents/logs")
async def clear_agent_logs():
    """Clear all agent logs."""
    try:
        agent_manager.clear_agent_logs()
        return {"message": "Agent logs cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time agent activity
@app.websocket("/ws/agent-logs")
async def websocket_agent_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time agent log streaming."""
    await websocket_manager.connect(websocket)
    try:
        # Send initial agent statistics
        stats = agent_manager.get_agent_statistics()
        await websocket.send_text(json.dumps({
            "type": "agent_stats",
            "data": stats
        }))
        
        # Keep connection alive and periodically send updates
        while True:
            await asyncio.sleep(5)  # Send updates every 5 seconds
            
            # Get recent logs
            recent_logs = agent_manager.get_agent_logs_since(
                datetime.now() - datetime.timedelta(seconds=5)
            )
            
            if recent_logs:
                await websocket.send_text(json.dumps({
                    "type": "new_logs",
                    "logs": [log.dict() for log in recent_logs]
                }))
            
            # Send updated statistics
            stats = agent_manager.get_agent_statistics()
            await websocket.send_text(json.dumps({
                "type": "agent_stats_update",
                "data": stats
            }))
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "search_service": "configured",
        "agents": list(agent_manager.agents.keys())
    }

# Demo data endpoints (for testing)
@app.post("/api/demo/populate-orders")
async def populate_demo_orders():
    """Create some demo orders for testing."""
    try:
        demo_orders = [
            {
                "customer_name": "Alice Johnson",
                "customer_email": "alice.johnson@email.com",
                "items": [
                    {"product_id": "SW-001", "quantity": 1},
                    {"product_id": "SW-002", "quantity": 2},
                    {"product_id": "SW-007", "quantity": 1}
                ]
            },
            {
                "customer_name": "Bob Smith",
                "customer_email": "bob.smith@premium.com",
                "items": [
                    {"product_id": "SW-006", "quantity": 1},
                    {"product_id": "SW-004", "quantity": 3},
                    {"product_id": "SW-005", "quantity": 2}
                ]
            },
            {
                "customer_name": "Carol Williams",
                "customer_email": "carol@smarttech.com",
                "items": [
                    {"product_id": "SW-001", "quantity": 1},
                    {"product_id": "SW-003", "quantity": 1},
                    {"product_id": "SW-009", "quantity": 4},
                    {"product_id": "SW-012", "quantity": 3}
                ]
            }
        ]
        
        created_orders = []
        for order_data in demo_orders:
            result = agent_manager.process_order_full_workflow(
                order_data["customer_name"],
                order_data["customer_email"],
                order_data["items"]
            )
            created_orders.append(result.get("order_id"))
        
        return {
            "message": f"Created {len(created_orders)} demo orders",
            "order_ids": created_orders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)