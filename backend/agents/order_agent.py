"""
Order Agent - Main orchestrator agent for ContosoMesh order processing.
This agent coordinates with other agents to process orders end-to-end.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.models.schemas import Order, OrderItem, OrderStatus, AgentResponse, AgentLog
from backend.database.db import Database

class OrderAgent:
    def __init__(self, database: Database):
        self.name = "Order Agent"
        self.color = "#2563eb"  # Blue
        self.database = database
        self.agent_logs = []
    
    def log_action(self, action: str, message: str, order_id: Optional[str] = None):
        """Log agent action."""
        log = AgentLog(
            agent_name=self.name,
            action=action,
            message=message,
            timestamp=datetime.now(),
            order_id=order_id,
            color=self.color
        )
        self.agent_logs.append(log)
        print(f"[{self.name}] {action}: {message}")
    
    def create_order(self, customer_name: str, customer_email: str, items_data: List[Dict[str, Any]]) -> AgentResponse:
        """
        Create a new order with the provided items.
        
        Args:
            customer_name: Name of the customer
            customer_email: Email of the customer
            items_data: List of dicts with 'product_id' and 'quantity'
        
        Returns:
            AgentResponse with order creation status
        """
        try:
            # Generate unique order ID
            order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            self.log_action("CREATE_ORDER", f"Creating new order {order_id} for {customer_name}", order_id)
            
            # Validate products exist
            order_items = []
            for item_data in items_data:
                product = self.database.get_product(item_data["product_id"])
                if not product:
                    error_msg = f"Product {item_data['product_id']} not found"
                    self.log_action("VALIDATION_ERROR", error_msg, order_id)
                    return AgentResponse(
                        agent_name=self.name,
                        success=False,
                        message=error_msg,
                        timestamp=datetime.now()
                    )
                
                # Validate quantity
                quantity = item_data.get("quantity", 0)
                if quantity <= 0:
                    error_msg = f"Invalid quantity {quantity} for product {product.name}"
                    self.log_action("VALIDATION_ERROR", error_msg, order_id)
                    return AgentResponse(
                        agent_name=self.name,
                        success=False,
                        message=error_msg,
                        timestamp=datetime.now()
                    )
                
                order_items.append(OrderItem(
                    product_id=product.id,
                    quantity=quantity
                ))
            
            # Create order object
            order = Order(
                id=order_id,
                customer_name=customer_name,
                customer_email=customer_email,
                items=order_items,
                status=OrderStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                agent_logs=[]
            )
            
            # Save to database
            self.database.create_order(order)
            
            self.log_action("ORDER_CREATED", f"Order {order_id} created successfully with {len(order_items)} items", order_id)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Order {order_id} created successfully",
                data={"order_id": order_id, "items_count": len(order_items)},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Failed to create order: {str(e)}"
            self.log_action("ERROR", error_msg)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def orchestrate_order_processing(self, order_id: str, agents: Dict[str, Any]) -> AgentResponse:
        """
        Orchestrate the complete order processing workflow.
        
        Args:
            order_id: ID of the order to process
            agents: Dictionary of agent instances
        
        Returns:
            AgentResponse with orchestration status
        """
        try:
            self.log_action("ORCHESTRATE_START", f"Starting order processing orchestration for {order_id}", order_id)
            
            # Get order
            order = self.database.get_order(order_id)
            if not order:
                error_msg = f"Order {order_id} not found"
                self.log_action("ERROR", error_msg, order_id)
                return AgentResponse(
                    agent_name=self.name,
                    success=False,
                    message=error_msg,
                    timestamp=datetime.now()
                )
            
            # Step 1: Check stocks
            self.log_action("ORCHESTRATE_STEP", "Delegating to Stocks Agent", order_id)
            stocks_response = agents["stocks"].check_stocks(order_id)
            
            if not stocks_response.success:
                self.log_action("ORCHESTRATE_ERROR", f"Stocks check failed: {stocks_response.message}", order_id)
                return stocks_response
            
            # Update order status
            order.status = OrderStatus.STOCKS_CHECKED
            order.updated_at = datetime.now()
            self.database.update_order(order)
            
            # Step 2: Get pricing
            self.log_action("ORCHESTRATE_STEP", "Delegating to Price Agent", order_id)
            pricing_response = agents["price"].calculate_pricing(order_id)
            
            if not pricing_response.success:
                self.log_action("ORCHESTRATE_ERROR", f"Pricing failed: {pricing_response.message}", order_id)
                return pricing_response
            
            # Update order status
            order.status = OrderStatus.PRICED
            order.updated_at = datetime.now()
            self.database.update_order(order)
            
            # Step 3: Plan delivery
            self.log_action("ORCHESTRATE_STEP", "Delegating to Delivery Agent", order_id)
            delivery_response = agents["delivery"].plan_delivery(order_id)
            
            if not delivery_response.success:
                self.log_action("ORCHESTRATE_ERROR", f"Delivery planning failed: {delivery_response.message}", order_id)
                return delivery_response
            
            # Update order status
            order.status = OrderStatus.DELIVERY_PLANNED
            order.updated_at = datetime.now()
            self.database.update_order(order)
            
            # Step 4: Notify warehouse
            self.log_action("ORCHESTRATE_STEP", "Delegating to Datawarehouse Agent", order_id)
            warehouse_response = agents["datawarehouse"].notify_logistics(order_id)
            
            if not warehouse_response.success:
                self.log_action("ORCHESTRATE_ERROR", f"Warehouse notification failed: {warehouse_response.message}", order_id)
                return warehouse_response
            
            # Step 5: Quality check (additional reasoning agent)
            if "quality" in agents:
                self.log_action("ORCHESTRATE_STEP", "Delegating to Quality Agent", order_id)
                quality_response = agents["quality"].perform_quality_check(order_id)
                
                if not quality_response.success:
                    self.log_action("ORCHESTRATE_WARNING", f"Quality check had issues: {quality_response.message}", order_id)
            
            # Final status update
            order.status = OrderStatus.LOGISTICS_NOTIFIED
            order.updated_at = datetime.now()
            self.database.update_order(order)
            
            self.log_action("ORCHESTRATE_COMPLETE", f"Order {order_id} processing completed successfully", order_id)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Order {order_id} processed successfully through all agents",
                data={"order_id": order_id, "final_status": order.status.value},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Orchestration failed for order {order_id}: {str(e)}"
            self.log_action("ORCHESTRATE_ERROR", error_msg, order_id)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def get_order_status(self, order_id: str) -> AgentResponse:
        """Get the current status of an order."""
        try:
            order = self.database.get_order(order_id)
            if not order:
                return AgentResponse(
                    agent_name=self.name,
                    success=False,
                    message=f"Order {order_id} not found",
                    timestamp=datetime.now()
                )
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Order {order_id} status retrieved",
                data={
                    "order_id": order_id,
                    "status": order.status.value,
                    "customer": order.customer_name,
                    "total_amount": order.total_amount,
                    "items_count": len(order.items),
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat()
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Failed to get order status: {str(e)}"
            self.log_action("ERROR", error_msg, order_id)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def cancel_order(self, order_id: str, reason: str = "Customer request") -> AgentResponse:
        """Cancel an order."""
        try:
            order = self.database.get_order(order_id)
            if not order:
                return AgentResponse(
                    agent_name=self.name,
                    success=False,
                    message=f"Order {order_id} not found",
                    timestamp=datetime.now()
                )
            
            if order.status == OrderStatus.COMPLETED:
                return AgentResponse(
                    agent_name=self.name,
                    success=False,
                    message=f"Cannot cancel completed order {order_id}",
                    timestamp=datetime.now()
                )
            
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.now()
            self.database.update_order(order)
            
            self.log_action("ORDER_CANCELLED", f"Order {order_id} cancelled: {reason}", order_id)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Order {order_id} cancelled successfully",
                data={"order_id": order_id, "reason": reason},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Failed to cancel order: {str(e)}"
            self.log_action("ERROR", error_msg, order_id)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )