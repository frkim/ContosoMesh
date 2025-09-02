"""
Stocks Agent - Handles inventory checking and availability for ContosoMesh orders.
This agent checks product availability and provides next availability dates.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from backend.models.schemas import Order, OrderItem, OrderStatus, AgentResponse, AgentLog
from backend.database.db import Database

class StocksAgent:
    def __init__(self, database: Database):
        self.name = "Stocks Agent"
        self.color = "#16a34a"  # Green
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
    
    def check_stocks(self, order_id: str) -> AgentResponse:
        """
        Check stock availability for all items in an order.
        
        Args:
            order_id: ID of the order to check
            
        Returns:
            AgentResponse with stock check results
        """
        try:
            self.log_action("STOCK_CHECK_START", f"Starting stock check for order {order_id}", order_id)
            
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
            
            stock_results = []
            all_available = True
            
            # Check each item
            for item in order.items:
                product = self.database.get_product(item.product_id)
                if not product:
                    error_msg = f"Product {item.product_id} not found"
                    self.log_action("ERROR", error_msg, order_id)
                    return AgentResponse(
                        agent_name=self.name,
                        success=False,
                        message=error_msg,
                        timestamp=datetime.now()
                    )
                
                # Check availability
                if product.stock >= item.quantity:
                    item.availability_status = "available"
                    item.next_availability = None
                    self.log_action("ITEM_AVAILABLE", f"{product.name} x{item.quantity} - In stock ({product.stock} available)", order_id)
                    
                    stock_results.append({
                        "product_id": product.id,
                        "product_name": product.name,
                        "requested_quantity": item.quantity,
                        "available_stock": product.stock,
                        "status": "available"
                    })
                else:
                    # Not enough stock
                    all_available = False
                    
                    # Calculate next availability
                    if product.next_availability:
                        item.availability_status = "out_of_stock"
                        item.next_availability = product.next_availability
                        self.log_action("ITEM_OUT_OF_STOCK", f"{product.name} x{item.quantity} - Out of stock, next available: {product.next_availability}", order_id)
                        
                        stock_results.append({
                            "product_id": product.id,
                            "product_name": product.name,
                            "requested_quantity": item.quantity,
                            "available_stock": product.stock,
                            "status": "out_of_stock",
                            "next_availability": product.next_availability
                        })
                    else:
                        # Calculate estimated availability (mock calculation)
                        estimated_days = max(1, (item.quantity - product.stock) // 10)  # Assume 10 units per day production
                        next_date = (datetime.now() + timedelta(days=estimated_days)).strftime("%Y-%m-%d")
                        
                        item.availability_status = "low_stock"
                        item.next_availability = next_date
                        self.log_action("ITEM_LOW_STOCK", f"{product.name} x{item.quantity} - Low stock ({product.stock} available), estimated restock: {next_date}", order_id)
                        
                        stock_results.append({
                            "product_id": product.id,
                            "product_name": product.name,
                            "requested_quantity": item.quantity,
                            "available_stock": product.stock,
                            "status": "low_stock",
                            "next_availability": next_date
                        })
            
            # Update order in database
            order.updated_at = datetime.now()
            self.database.update_order(order)
            
            # Prepare response
            if all_available:
                self.log_action("STOCK_CHECK_COMPLETE", f"All items available for order {order_id}", order_id)
                message = "All items are in stock and available"
            else:
                out_of_stock_count = sum(1 for result in stock_results if result["status"] != "available")
                self.log_action("STOCK_CHECK_COMPLETE", f"Stock check complete: {out_of_stock_count} items have availability issues", order_id)
                message = f"Stock check complete: {out_of_stock_count} items have availability issues"
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=message,
                data={
                    "order_id": order_id,
                    "all_available": all_available,
                    "stock_results": stock_results,
                    "total_items": len(order.items)
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Stock check failed for order {order_id}: {str(e)}"
            self.log_action("ERROR", error_msg, order_id)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def reserve_stock(self, order_id: str) -> AgentResponse:
        """
        Reserve stock for an order (reduce available stock).
        
        Args:
            order_id: ID of the order to reserve stock for
            
        Returns:
            AgentResponse with reservation results
        """
        try:
            self.log_action("STOCK_RESERVE_START", f"Starting stock reservation for order {order_id}", order_id)
            
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
            
            reserved_items = []
            
            # Reserve stock for each available item
            for item in order.items:
                if item.availability_status == "available":
                    product = self.database.get_product(item.product_id)
                    if product and product.stock >= item.quantity:
                        # Reduce stock
                        new_stock = product.stock - item.quantity
                        self.database.update_stock(item.product_id, new_stock)
                        
                        self.log_action("STOCK_RESERVED", f"Reserved {item.quantity} units of {product.name} (remaining: {new_stock})", order_id)
                        
                        reserved_items.append({
                            "product_id": product.id,
                            "product_name": product.name,
                            "quantity_reserved": item.quantity,
                            "remaining_stock": new_stock
                        })
            
            if reserved_items:
                self.log_action("STOCK_RESERVE_COMPLETE", f"Stock reservation complete for {len(reserved_items)} items", order_id)
                message = f"Successfully reserved stock for {len(reserved_items)} items"
            else:
                self.log_action("STOCK_RESERVE_NONE", "No items were available for reservation", order_id)
                message = "No items were available for stock reservation"
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=message,
                data={
                    "order_id": order_id,
                    "reserved_items": reserved_items,
                    "total_reserved": len(reserved_items)
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Stock reservation failed for order {order_id}: {str(e)}"
            self.log_action("ERROR", error_msg, order_id)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def get_stock_status(self, product_id: str) -> AgentResponse:
        """
        Get current stock status for a specific product.
        
        Args:
            product_id: ID of the product to check
            
        Returns:
            AgentResponse with stock status
        """
        try:
            product = self.database.get_product(product_id)
            if not product:
                return AgentResponse(
                    agent_name=self.name,
                    success=False,
                    message=f"Product {product_id} not found",
                    timestamp=datetime.now()
                )
            
            # Determine stock level status
            if product.stock == 0:
                stock_level = "out_of_stock"
            elif product.stock < 10:  # Threshold for low stock
                stock_level = "low_stock"
            elif product.stock < 50:
                stock_level = "medium_stock"
            else:
                stock_level = "high_stock"
            
            self.log_action("STOCK_QUERY", f"Stock status for {product.name}: {product.stock} units ({stock_level})")
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Stock status retrieved for {product.name}",
                data={
                    "product_id": product.id,
                    "product_name": product.name,
                    "current_stock": product.stock,
                    "stock_level": stock_level,
                    "next_availability": product.next_availability
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Failed to get stock status for {product_id}: {str(e)}"
            self.log_action("ERROR", error_msg)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def update_stock_levels(self, stock_updates: List[Dict[str, Any]]) -> AgentResponse:
        """
        Update stock levels for multiple products (simulates inventory replenishment).
        
        Args:
            stock_updates: List of dicts with 'product_id' and 'new_stock'
            
        Returns:
            AgentResponse with update results
        """
        try:
            self.log_action("STOCK_UPDATE_START", f"Starting bulk stock update for {len(stock_updates)} products")
            
            updated_products = []
            
            for update in stock_updates:
                product_id = update.get("product_id")
                new_stock = update.get("new_stock", 0)
                
                product = self.database.get_product(product_id)
                if product:
                    old_stock = product.stock
                    self.database.update_stock(product_id, new_stock)
                    
                    self.log_action("STOCK_UPDATED", f"{product.name}: {old_stock} → {new_stock} units")
                    
                    updated_products.append({
                        "product_id": product_id,
                        "product_name": product.name,
                        "old_stock": old_stock,
                        "new_stock": new_stock,
                        "change": new_stock - old_stock
                    })
                else:
                    self.log_action("STOCK_UPDATE_ERROR", f"Product {product_id} not found for stock update")
            
            self.log_action("STOCK_UPDATE_COMPLETE", f"Stock update complete for {len(updated_products)} products")
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Stock levels updated for {len(updated_products)} products",
                data={
                    "updated_products": updated_products,
                    "total_updated": len(updated_products)
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Bulk stock update failed: {str(e)}"
            self.log_action("ERROR", error_msg)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )