"""
Price Agent - Handles pricing calculations and discounts for ContosoMesh orders.
This agent calculates item prices, applies quantity discounts, and determines final order totals.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.models.schemas import Order, OrderItem, OrderStatus, AgentResponse, AgentLog
from backend.database.db import Database

class PriceAgent:
    def __init__(self, database: Database):
        self.name = "Price Agent"
        self.color = "#dc2626"  # Red
        self.database = database
        self.agent_logs = []
        
        # Discount tiers based on quantity
        self.quantity_discounts = {
            10: 0.05,   # 5% for 10+ units total
            25: 0.08,   # 8% for 25+ units total
            50: 0.12,   # 12% for 50+ units total
            100: 0.15,  # 15% for 100+ units total
            200: 0.20   # 20% for 200+ units total
        }
        
        # Category discounts for bulk orders
        self.category_discounts = {
            "Smart Home Hub": 0.03,
            "Security Sensor": 0.05,
            "Smart Lighting": 0.04,
            "Environmental Sensor": 0.06
        }
    
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
    
    def calculate_pricing(self, order_id: str) -> AgentResponse:
        """
        Calculate pricing for all items in an order, including discounts.
        
        Args:
            order_id: ID of the order to price
            
        Returns:
            AgentResponse with pricing results
        """
        try:
            self.log_action("PRICING_START", f"Starting pricing calculation for order {order_id}", order_id)
            
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
            
            pricing_details = []
            subtotal = 0.0
            total_quantity = 0
            category_quantities = {}
            
            # Calculate base pricing for each item
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
                
                # Base pricing
                item.unit_price = product.price
                item.total_price = product.price * item.quantity
                subtotal += item.total_price
                total_quantity += item.quantity
                
                # Track category quantities for category discounts
                if product.category not in category_quantities:
                    category_quantities[product.category] = 0
                category_quantities[product.category] += item.quantity
                
                self.log_action("ITEM_PRICED", f"{product.name} x{item.quantity} @ ${product.price:.2f} = ${item.total_price:.2f}", order_id)
                
                pricing_details.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "category": product.category,
                    "unit_price": product.price,
                    "quantity": item.quantity,
                    "line_total": item.total_price
                })
            
            # Calculate quantity discount
            quantity_discount_rate = self._calculate_quantity_discount(total_quantity)
            quantity_discount_amount = subtotal * quantity_discount_rate
            
            # Calculate category discounts
            category_discount_amount = self._calculate_category_discounts(pricing_details, category_quantities)
            
            # Total discount
            total_discount = quantity_discount_amount + category_discount_amount
            final_total = subtotal - total_discount
            
            # Update order
            order.total_amount = final_total
            order.discount_applied = total_discount
            order.updated_at = datetime.now()
            self.database.update_order(order)
            
            self.log_action("PRICING_COMPLETE", f"Pricing complete: ${subtotal:.2f} - ${total_discount:.2f} = ${final_total:.2f}", order_id)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Pricing calculated for order {order_id}",
                data={
                    "order_id": order_id,
                    "subtotal": round(subtotal, 2),
                    "quantity_discount": {
                        "rate": quantity_discount_rate,
                        "amount": round(quantity_discount_amount, 2),
                        "reason": f"{total_quantity} total units"
                    },
                    "category_discount": {
                        "amount": round(category_discount_amount, 2),
                        "details": self._get_category_discount_details(category_quantities)
                    },
                    "total_discount": round(total_discount, 2),
                    "final_total": round(final_total, 2),
                    "pricing_details": pricing_details
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Pricing calculation failed for order {order_id}: {str(e)}"
            self.log_action("ERROR", error_msg, order_id)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def _calculate_quantity_discount(self, total_quantity: int) -> float:
        """Calculate quantity-based discount rate."""
        discount_rate = 0.0
        
        # Find the highest applicable discount tier
        for quantity_threshold in sorted(self.quantity_discounts.keys(), reverse=True):
            if total_quantity >= quantity_threshold:
                discount_rate = self.quantity_discounts[quantity_threshold]
                self.log_action("DISCOUNT_APPLIED", f"Quantity discount: {discount_rate*100:.1f}% for {total_quantity} units")
                break
        
        return discount_rate
    
    def _calculate_category_discounts(self, pricing_details: List[Dict], category_quantities: Dict[str, int]) -> float:
        """Calculate category-based discounts."""
        total_category_discount = 0.0
        
        for category, quantity in category_quantities.items():
            if category in self.category_discounts and quantity >= 5:  # Minimum 5 units for category discount
                discount_rate = self.category_discounts[category]
                
                # Calculate discount for this category
                category_subtotal = sum(
                    detail["line_total"] for detail in pricing_details 
                    if detail["category"] == category
                )
                category_discount = category_subtotal * discount_rate
                total_category_discount += category_discount
                
                self.log_action("CATEGORY_DISCOUNT", f"{category}: {discount_rate*100:.1f}% on ${category_subtotal:.2f} = ${category_discount:.2f}")
        
        return total_category_discount
    
    def _get_category_discount_details(self, category_quantities: Dict[str, int]) -> List[Dict]:
        """Get details about category discounts applied."""
        details = []
        
        for category, quantity in category_quantities.items():
            if category in self.category_discounts and quantity >= 5:
                details.append({
                    "category": category,
                    "quantity": quantity,
                    "discount_rate": self.category_discounts[category],
                    "reason": f"{quantity} units in {category}"
                })
        
        return details
    
    def calculate_custom_pricing(self, order_id: str, custom_discounts: Dict[str, float]) -> AgentResponse:
        """
        Calculate pricing with custom discounts (for special customers or promotions).
        
        Args:
            order_id: ID of the order to price
            custom_discounts: Dict of product_id to discount_rate
            
        Returns:
            AgentResponse with custom pricing results
        """
        try:
            self.log_action("CUSTOM_PRICING_START", f"Starting custom pricing for order {order_id}", order_id)
            
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
            
            custom_pricing_details = []
            total_custom_discount = 0.0
            subtotal = 0.0
            
            for item in order.items:
                product = self.database.get_product(item.product_id)
                if not product:
                    continue
                
                base_line_total = product.price * item.quantity
                subtotal += base_line_total
                
                # Apply custom discount if available
                if item.product_id in custom_discounts:
                    discount_rate = custom_discounts[item.product_id]
                    discount_amount = base_line_total * discount_rate
                    final_line_total = base_line_total - discount_amount
                    total_custom_discount += discount_amount
                    
                    item.unit_price = product.price * (1 - discount_rate)
                    item.total_price = final_line_total
                    
                    self.log_action("CUSTOM_DISCOUNT", f"{product.name}: {discount_rate*100:.1f}% discount applied", order_id)
                    
                    custom_pricing_details.append({
                        "product_id": product.id,
                        "product_name": product.name,
                        "original_price": product.price,
                        "discount_rate": discount_rate,
                        "discounted_price": item.unit_price,
                        "quantity": item.quantity,
                        "line_total": final_line_total
                    })
                else:
                    item.unit_price = product.price
                    item.total_price = base_line_total
            
            final_total = subtotal - total_custom_discount
            order.total_amount = final_total
            order.discount_applied = total_custom_discount
            order.updated_at = datetime.now()
            self.database.update_order(order)
            
            self.log_action("CUSTOM_PRICING_COMPLETE", f"Custom pricing complete: ${final_total:.2f} (${total_custom_discount:.2f} discount)", order_id)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Custom pricing applied to order {order_id}",
                data={
                    "order_id": order_id,
                    "subtotal": round(subtotal, 2),
                    "custom_discount_total": round(total_custom_discount, 2),
                    "final_total": round(final_total, 2),
                    "custom_pricing_details": custom_pricing_details
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Custom pricing failed for order {order_id}: {str(e)}"
            self.log_action("ERROR", error_msg, order_id)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def get_pricing_quote(self, items_data: List[Dict[str, Any]]) -> AgentResponse:
        """
        Get a pricing quote without creating an order.
        
        Args:
            items_data: List of dicts with 'product_id' and 'quantity'
            
        Returns:
            AgentResponse with pricing quote
        """
        try:
            self.log_action("QUOTE_START", f"Generating pricing quote for {len(items_data)} items")
            
            quote_details = []
            subtotal = 0.0
            total_quantity = 0
            category_quantities = {}
            
            for item_data in items_data:
                product = self.database.get_product(item_data["product_id"])
                if not product:
                    self.log_action("QUOTE_WARNING", f"Product {item_data['product_id']} not found, skipping")
                    continue
                
                quantity = item_data.get("quantity", 1)
                line_total = product.price * quantity
                subtotal += line_total
                total_quantity += quantity
                
                if product.category not in category_quantities:
                    category_quantities[product.category] = 0
                category_quantities[product.category] += quantity
                
                quote_details.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "category": product.category,
                    "unit_price": product.price,
                    "quantity": quantity,
                    "line_total": line_total,
                    "in_stock": product.stock >= quantity
                })
            
            # Calculate potential discounts
            quantity_discount_rate = self._calculate_quantity_discount(total_quantity)
            quantity_discount_amount = subtotal * quantity_discount_rate
            
            category_discount_amount = self._calculate_category_discounts(quote_details, category_quantities)
            
            total_discount = quantity_discount_amount + category_discount_amount
            final_total = subtotal - total_discount
            
            self.log_action("QUOTE_COMPLETE", f"Quote generated: ${final_total:.2f} (${total_discount:.2f} discount)")
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message="Pricing quote generated successfully",
                data={
                    "quote_details": quote_details,
                    "subtotal": round(subtotal, 2),
                    "quantity_discount": {
                        "rate": quantity_discount_rate,
                        "amount": round(quantity_discount_amount, 2)
                    },
                    "category_discount": round(category_discount_amount, 2),
                    "total_discount": round(total_discount, 2),
                    "final_total": round(final_total, 2),
                    "total_items": len(quote_details),
                    "total_quantity": total_quantity
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Quote generation failed: {str(e)}"
            self.log_action("ERROR", error_msg)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )