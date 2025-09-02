"""
Delivery Agent - Advanced reasoning agent for ContosoMesh delivery planning.
This agent uses reasoning to create optimal delivery parcels based on product availability.
Uses reasoning to decide when to split orders into multiple parcels.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from models.schemas import Order, OrderItem, ParcelInfo, AgentResponse, AgentLog
from database.db import Database

class DeliveryAgent:
    def __init__(self, database: Database):
        self.name = "Delivery Agent"
        self.color = "#7c3aed"  # Purple
        self.database = database
        self.agent_logs = []
        
        # Reasoning parameters
        self.max_delay_threshold = 3  # Days - split if any item has >3 days delay
        self.optimal_parcel_weight = 5.0  # kg - target weight per parcel
        self.max_parcel_weight = 10.0  # kg - maximum weight per parcel
        self.shipping_methods = {
            "express": {"max_weight": 5.0, "cost_per_kg": 8.0, "delivery_days": 1},
            "standard": {"max_weight": 10.0, "cost_per_kg": 3.0, "delivery_days": 3},
            "economy": {"max_weight": 15.0, "cost_per_kg": 1.5, "delivery_days": 7}
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
    
    def plan_delivery(self, order_id: str) -> AgentResponse:
        """
        Plan delivery using reasoning to optimize parcel creation and shipping.
        
        Args:
            order_id: ID of the order to plan delivery for
            
        Returns:
            AgentResponse with delivery plan
        """
        try:
            self.log_action("DELIVERY_PLANNING_START", f"Starting intelligent delivery planning for order {order_id}", order_id)
            
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
            
            # Analyze order items and their availability
            delivery_analysis = self._analyze_delivery_requirements(order)
            
            # Use reasoning to determine optimal delivery strategy
            delivery_strategy = self._reason_delivery_strategy(delivery_analysis)
            
            # Create delivery parcels based on reasoning
            parcels = self._create_delivery_parcels(order, delivery_strategy)
            
            # Calculate delivery costs and timelines
            delivery_summary = self._calculate_delivery_summary(parcels)
            
            self.log_action("DELIVERY_PLANNING_COMPLETE", 
                          f"Created {len(parcels)} parcels with {delivery_strategy['strategy_name']} strategy", 
                          order_id)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Delivery plan created for order {order_id}",
                data={
                    "order_id": order_id,
                    "delivery_strategy": delivery_strategy,
                    "delivery_analysis": delivery_analysis,
                    "parcels": [parcel.dict() for parcel in parcels],
                    "delivery_summary": delivery_summary,
                    "total_parcels": len(parcels)
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Delivery planning failed for order {order_id}: {str(e)}"
            self.log_action("ERROR", error_msg, order_id)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def _analyze_delivery_requirements(self, order: Order) -> Dict[str, Any]:
        """Analyze order items to understand delivery requirements."""
        self.log_action("REASONING", "Analyzing delivery requirements and constraints", order.id)
        
        available_items = []
        delayed_items = []
        total_weight = 0.0
        max_delay_days = 0
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if not product:
                continue
            
            # Estimate product weight (mock calculation based on category)
            estimated_weight = self._estimate_product_weight(product.category) * item.quantity
            total_weight += estimated_weight
            
            item_analysis = {
                "product_id": product.id,
                "product_name": product.name,
                "category": product.category,
                "quantity": item.quantity,
                "estimated_weight": estimated_weight,
                "availability_status": item.availability_status,
                "next_availability": item.next_availability
            }
            
            if item.availability_status == "available":
                available_items.append(item_analysis)
                self.log_action("ANALYSIS", f"✓ {product.name} - Available immediately", order.id)
            else:
                # Calculate delay days
                if item.next_availability:
                    try:
                        next_date = datetime.strptime(item.next_availability, "%Y-%m-%d")
                        delay_days = (next_date - datetime.now()).days
                        item_analysis["delay_days"] = delay_days
                        max_delay_days = max(max_delay_days, delay_days)
                        delayed_items.append(item_analysis)
                        self.log_action("ANALYSIS", f"⏱ {product.name} - Delayed {delay_days} days", order.id)
                    except ValueError:
                        self.log_action("ANALYSIS", f"⚠ {product.name} - Invalid availability date", order.id)
        
        analysis = {
            "available_items": available_items,
            "delayed_items": delayed_items,
            "total_weight": total_weight,
            "max_delay_days": max_delay_days,
            "items_available_now": len(available_items),
            "items_delayed": len(delayed_items),
            "total_items": len(available_items) + len(delayed_items)
        }
        
        self.log_action("ANALYSIS_COMPLETE", 
                       f"Analysis: {len(available_items)} available, {len(delayed_items)} delayed (max {max_delay_days} days)", 
                       order.id)
        
        return analysis
    
    def _reason_delivery_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use reasoning to determine the optimal delivery strategy."""
        self.log_action("REASONING", "Applying intelligent reasoning to determine delivery strategy", analysis.get("order_id"))
        
        # Reasoning logic
        strategy_name = ""
        reasoning_steps = []
        split_decision = False
        
        # Step 1: Analyze delay impact
        if analysis["max_delay_days"] > self.max_delay_threshold:
            reasoning_steps.append(f"Maximum delay ({analysis['max_delay_days']} days) exceeds threshold ({self.max_delay_threshold} days)")
            split_decision = True
        else:
            reasoning_steps.append(f"Maximum delay ({analysis['max_delay_days']} days) is within acceptable threshold")
        
        # Step 2: Analyze weight distribution
        if analysis["total_weight"] > self.max_parcel_weight:
            reasoning_steps.append(f"Total weight ({analysis['total_weight']:.1f}kg) exceeds single parcel limit ({self.max_parcel_weight}kg)")
            split_decision = True
        else:
            reasoning_steps.append(f"Total weight ({analysis['total_weight']:.1f}kg) fits in single parcel")
        
        # Step 3: Customer satisfaction reasoning
        if analysis["items_available_now"] > 0 and analysis["items_delayed"] > 0:
            satisfaction_benefit = analysis["items_available_now"] / analysis["total_items"]
            if satisfaction_benefit >= 0.6:  # 60% of items available
                reasoning_steps.append(f"Customer satisfaction benefit: {satisfaction_benefit:.1%} of items can ship immediately")
                split_decision = True
            else:
                reasoning_steps.append(f"Limited benefit ({satisfaction_benefit:.1%}) from immediate shipping")
        
        # Step 4: Economic reasoning
        if split_decision:
            estimated_shipping_cost = self._estimate_shipping_costs(analysis, split=True)
            single_shipping_cost = self._estimate_shipping_costs(analysis, split=False)
            cost_impact = estimated_shipping_cost - single_shipping_cost
            
            if cost_impact > 20:  # $20 threshold
                reasoning_steps.append(f"Split shipping adds ${cost_impact:.2f} cost - reconsidering")
                if analysis["max_delay_days"] <= 5:  # Only reconsider for moderate delays
                    split_decision = False
                    reasoning_steps.append("Choosing single shipment for cost efficiency")
            else:
                reasoning_steps.append(f"Split shipping cost impact (${cost_impact:.2f}) is acceptable")
        
        # Final strategy determination
        if split_decision:
            if analysis["items_available_now"] > 0:
                strategy_name = "smart_split_immediate_and_delayed"
            else:
                strategy_name = "weight_based_split"
        else:
            strategy_name = "single_shipment_when_ready"
        
        strategy = {
            "strategy_name": strategy_name,
            "split_shipment": split_decision,
            "reasoning_steps": reasoning_steps,
            "decision_factors": {
                "delay_threshold_exceeded": analysis["max_delay_days"] > self.max_delay_threshold,
                "weight_limit_exceeded": analysis["total_weight"] > self.max_parcel_weight,
                "customer_satisfaction_priority": analysis["items_available_now"] > 0,
                "cost_consideration": True
            }
        }
        
        self.log_action("REASONING_COMPLETE", f"Strategy decided: {strategy_name}", analysis.get("order_id"))
        for step in reasoning_steps:
            self.log_action("REASONING_STEP", step, analysis.get("order_id"))
        
        return strategy
    
    def _create_delivery_parcels(self, order: Order, strategy: Dict[str, Any]) -> List[ParcelInfo]:
        """Create delivery parcels based on the determined strategy."""
        parcels = []
        
        if strategy["split_shipment"]:
            if strategy["strategy_name"] == "smart_split_immediate_and_delayed":
                parcels = self._create_split_parcels_by_availability(order)
            else:
                parcels = self._create_split_parcels_by_weight(order)
        else:
            parcels = self._create_single_parcel(order)
        
        # Assign shipping methods and delivery dates
        for i, parcel in enumerate(parcels):
            parcel.shipping_method = self._select_optimal_shipping_method(parcel)
            parcel.estimated_delivery = self._calculate_delivery_date(parcel)
            
            self.log_action("PARCEL_CREATED", 
                          f"Parcel {parcel.parcel_id}: {len(parcel.items)} items, {parcel.shipping_method} shipping", 
                          order.id)
        
        return parcels
    
    def _create_split_parcels_by_availability(self, order: Order) -> List[ParcelInfo]:
        """Create parcels split by item availability."""
        immediate_items = []
        delayed_items = []
        
        for item in order.items:
            if item.availability_status == "available":
                immediate_items.append(item)
            else:
                delayed_items.append(item)
        
        parcels = []
        
        if immediate_items:
            parcel = ParcelInfo(
                parcel_id=f"{order.id}-IMMEDIATE",
                items=immediate_items
            )
            parcels.append(parcel)
        
        if delayed_items:
            parcel = ParcelInfo(
                parcel_id=f"{order.id}-DELAYED",
                items=delayed_items
            )
            parcels.append(parcel)
        
        return parcels
    
    def _create_split_parcels_by_weight(self, order: Order) -> List[ParcelInfo]:
        """Create parcels split by weight optimization."""
        parcels = []
        current_parcel_items = []
        current_weight = 0.0
        parcel_count = 1
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if not product:
                continue
            
            item_weight = self._estimate_product_weight(product.category) * item.quantity
            
            if current_weight + item_weight > self.max_parcel_weight and current_parcel_items:
                # Create current parcel
                parcel = ParcelInfo(
                    parcel_id=f"{order.id}-PARCEL-{parcel_count}",
                    items=current_parcel_items.copy()
                )
                parcels.append(parcel)
                
                # Start new parcel
                current_parcel_items = [item]
                current_weight = item_weight
                parcel_count += 1
            else:
                current_parcel_items.append(item)
                current_weight += item_weight
        
        # Add final parcel
        if current_parcel_items:
            parcel = ParcelInfo(
                parcel_id=f"{order.id}-PARCEL-{parcel_count}",
                items=current_parcel_items
            )
            parcels.append(parcel)
        
        return parcels
    
    def _create_single_parcel(self, order: Order) -> List[ParcelInfo]:
        """Create a single parcel for all items."""
        parcel = ParcelInfo(
            parcel_id=f"{order.id}-SINGLE",
            items=order.items
        )
        return [parcel]
    
    def _estimate_product_weight(self, category: str) -> float:
        """Estimate product weight based on category (mock calculation)."""
        weight_estimates = {
            "Smart Home Hub": 0.3,
            "Smart Switch": 0.1,
            "Smart Curtain": 0.8,
            "Security Sensor": 0.05,
            "Smart Lock": 1.2,
            "Environmental Sensor": 0.08,
            "Smart Lighting": 0.15,
            "Security Camera": 0.4,
            "Smart Blinds": 0.6,
            "Smart Plug": 0.12
        }
        return weight_estimates.get(category, 0.2)  # Default 200g
    
    def _select_optimal_shipping_method(self, parcel: ParcelInfo) -> str:
        """Select optimal shipping method based on parcel characteristics."""
        # Calculate total weight
        total_weight = sum(
            self._estimate_product_weight(
                self.database.get_product(item.product_id).category
            ) * item.quantity
            for item in parcel.items
            if self.database.get_product(item.product_id)
        )
        
        # Check if any items are delayed
        has_delays = any(item.availability_status != "available" for item in parcel.items)
        
        # Select method
        if total_weight <= 2.0 and not has_delays:
            return "express"
        elif total_weight <= 7.0:
            return "standard"
        else:
            return "economy"
    
    def _calculate_delivery_date(self, parcel: ParcelInfo) -> str:
        """Calculate estimated delivery date for a parcel."""
        # Find the latest availability date
        latest_date = datetime.now()
        
        for item in parcel.items:
            if item.next_availability:
                try:
                    item_date = datetime.strptime(item.next_availability, "%Y-%m-%d")
                    latest_date = max(latest_date, item_date)
                except ValueError:
                    pass
        
        # Add shipping time
        shipping_days = self.shipping_methods[parcel.shipping_method]["delivery_days"]
        delivery_date = latest_date + timedelta(days=shipping_days)
        
        return delivery_date.strftime("%Y-%m-%d")
    
    def _estimate_shipping_costs(self, analysis: Dict[str, Any], split: bool) -> float:
        """Estimate shipping costs for cost-benefit reasoning."""
        if split:
            # Assume 2 parcels for split shipment
            return 15.0 + 12.0  # Express + Standard
        else:
            # Single shipment
            if analysis["total_weight"] <= 5.0:
                return 12.0  # Standard
            else:
                return 8.0   # Economy
    
    def _calculate_delivery_summary(self, parcels: List[ParcelInfo]) -> Dict[str, Any]:
        """Calculate summary information for the delivery plan."""
        total_cost = 0.0
        earliest_delivery = None
        latest_delivery = None
        
        for parcel in parcels:
            # Mock cost calculation
            method = self.shipping_methods[parcel.shipping_method]
            parcel_weight = sum(
                self._estimate_product_weight(
                    self.database.get_product(item.product_id).category
                ) * item.quantity
                for item in parcel.items
                if self.database.get_product(item.product_id)
            )
            cost = parcel_weight * method["cost_per_kg"]
            total_cost += cost
            
            # Track delivery dates
            delivery_date = datetime.strptime(parcel.estimated_delivery, "%Y-%m-%d")
            if earliest_delivery is None or delivery_date < earliest_delivery:
                earliest_delivery = delivery_date
            if latest_delivery is None or delivery_date > latest_delivery:
                latest_delivery = delivery_date
        
        return {
            "total_shipping_cost": round(total_cost, 2),
            "earliest_delivery": earliest_delivery.strftime("%Y-%m-%d") if earliest_delivery else None,
            "latest_delivery": latest_delivery.strftime("%Y-%m-%d") if latest_delivery else None,
            "delivery_span_days": (latest_delivery - earliest_delivery).days if earliest_delivery and latest_delivery else 0,
            "parcels_count": len(parcels)
        }