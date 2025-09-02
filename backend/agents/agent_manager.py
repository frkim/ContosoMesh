"""
Agent Manager - Coordinates all ContosoMesh agents and provides a unified interface.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from database.db import Database
from search.azure_search import AzureSearchService
from agents.order_agent import OrderAgent
from agents.stocks_agent import StocksAgent
from agents.price_agent import PriceAgent
from agents.delivery_agent import DeliveryAgent
from agents.datawarehouse_agent import DatawarehouseAgent
from agents.quality_agent import QualityAgent
from models.schemas import AgentLog

class AgentManager:
    def __init__(self, database: Database, search_service: AzureSearchService):
        self.database = database
        self.search_service = search_service
        self.agent_logs = []
        
        # Initialize all agents
        self.agents = {
            "order": OrderAgent(database),
            "stocks": StocksAgent(database),
            "price": PriceAgent(database),
            "delivery": DeliveryAgent(database),
            "datawarehouse": DatawarehouseAgent(database),
            "quality": QualityAgent(database)
        }
        
        # Agent colors for UI
        self.agent_colors = {
            "order": "#2563eb",      # Blue
            "stocks": "#16a34a",     # Green
            "price": "#dc2626",      # Red
            "delivery": "#7c3aed",   # Purple
            "datawarehouse": "#ea580c", # Orange
            "quality": "#059669"     # Emerald
        }
    
    def get_all_agent_logs(self) -> List[AgentLog]:
        """Get logs from all agents."""
        all_logs = []
        
        for agent_name, agent in self.agents.items():
            for log in agent.agent_logs:
                all_logs.append(log)
        
        # Sort by timestamp
        all_logs.sort(key=lambda x: x.timestamp)
        return all_logs
    
    def get_agent_logs_since(self, since: datetime) -> List[AgentLog]:
        """Get agent logs since a specific timestamp."""
        all_logs = self.get_all_agent_logs()
        return [log for log in all_logs if log.timestamp > since]
    
    def clear_agent_logs(self):
        """Clear logs from all agents."""
        for agent in self.agents.values():
            agent.agent_logs.clear()
    
    def process_order_full_workflow(self, customer_name: str, customer_email: str, items_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a complete order workflow through all agents.
        
        Args:
            customer_name: Customer name
            customer_email: Customer email  
            items_data: List of items with product_id and quantity
            
        Returns:
            Complete workflow result
        """
        workflow_start = datetime.now()
        
        # Step 1: Create order
        order_result = self.agents["order"].create_order(customer_name, customer_email, items_data)
        
        if not order_result.success:
            return {
                "success": False,
                "message": f"Order creation failed: {order_result.message}",
                "timestamp": workflow_start
            }
        
        order_id = order_result.data["order_id"]
        
        # Step 2: Run full orchestration
        orchestration_result = self.agents["order"].orchestrate_order_processing(order_id, self.agents)
        
        # Collect all results
        workflow_result = {
            "success": orchestration_result.success,
            "order_id": order_id,
            "workflow_start": workflow_start,
            "workflow_end": datetime.now(),
            "order_creation": order_result.dict(),
            "orchestration": orchestration_result.dict(),
            "agent_logs": [log.dict() for log in self.get_all_agent_logs()],
            "final_order_status": self.agents["order"].get_order_status(order_id).dict()
        }
        
        return workflow_result
    
    def get_order_status_comprehensive(self, order_id: str) -> Dict[str, Any]:
        """Get comprehensive order status from all relevant agents."""
        results = {}
        
        # Order status
        results["order"] = self.agents["order"].get_order_status(order_id).dict()
        
        # Get order for additional checks
        order = self.database.get_order(order_id)
        if order:
            # Stock status for each item
            stock_statuses = []
            for item in order.items:
                stock_result = self.agents["stocks"].get_stock_status(item.product_id)
                if stock_result.success:
                    stock_statuses.append(stock_result.data)
            results["stock_statuses"] = stock_statuses
            
            # Quality assessment if not already done
            if order.status.value in ["priced", "delivery_planned", "logistics_notified"]:
                quality_result = self.agents["quality"].perform_quality_check(order_id)
                results["quality"] = quality_result.dict()
        
        results["agent_logs"] = [log.dict() for log in self.get_all_agent_logs()]
        
        return results
    
    def get_pricing_quote(self, items_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get pricing quote without creating an order."""
        return self.agents["price"].get_pricing_quote(items_data).dict()
    
    def search_products(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search products using Azure AI Search."""
        return self.search_service.search_products(query, filters)
    
    def get_warehouse_status(self) -> Dict[str, Any]:
        """Get current warehouse status."""
        return self.agents["datawarehouse"].get_warehouse_status().dict()
    
    def update_stock_levels(self, stock_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update stock levels (for demo purposes)."""
        return self.agents["stocks"].update_stock_levels(stock_updates).dict()
    
    def cancel_order(self, order_id: str, reason: str = "Customer request") -> Dict[str, Any]:
        """Cancel an order."""
        return self.agents["order"].cancel_order(order_id, reason).dict()
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get statistics about agent activity."""
        stats = {
            "total_logs": len(self.get_all_agent_logs()),
            "agent_activity": {},
            "recent_activity_count": 0
        }
        
        # Count logs per agent
        all_logs = self.get_all_agent_logs()
        for log in all_logs:
            agent_name = log.agent_name
            if agent_name not in stats["agent_activity"]:
                stats["agent_activity"][agent_name] = {
                    "total_actions": 0,
                    "recent_actions": 0,
                    "color": self.agent_colors.get(agent_name.lower().replace(" ", ""), "#000000")
                }
            
            stats["agent_activity"][agent_name]["total_actions"] += 1
            
            # Count recent activity (last 10 minutes)
            if (datetime.now() - log.timestamp).total_seconds() < 600:
                stats["agent_activity"][agent_name]["recent_actions"] += 1
                stats["recent_activity_count"] += 1
        
        return stats