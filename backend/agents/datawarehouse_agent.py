"""
Datawarehouse Agent - Handles logistics platform integration for ContosoMesh orders.
This agent notifies the warehouse management system to prepare orders for shipment.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from models.schemas import Order, ParcelInfo, AgentResponse, AgentLog
from database.db import Database

class DatawarehouseAgent:
    def __init__(self, database: Database):
        self.name = "Datawarehouse Agent"
        self.color = "#ea580c"  # Orange
        self.database = database
        self.agent_logs = []
        
        # Warehouse zones and capacities
        self.warehouse_zones = {
            "ZONE_A_ELECTRONICS": {"capacity": 1000, "current_load": 245, "specialization": "Electronic devices"},
            "ZONE_B_SENSORS": {"capacity": 500, "current_load": 123, "specialization": "Sensors and small devices"},
            "ZONE_C_SECURITY": {"capacity": 800, "current_load": 167, "specialization": "Security equipment"},
            "ZONE_D_LIGHTING": {"capacity": 600, "current_load": 89, "specialization": "Lighting and smart bulbs"}
        }
        
        # Product category to zone mapping
        self.category_zone_mapping = {
            "Smart Home Hub": "ZONE_A_ELECTRONICS",
            "Smart Switch": "ZONE_A_ELECTRONICS",
            "Smart Curtain": "ZONE_A_ELECTRONICS",
            "Security Sensor": "ZONE_B_SENSORS",
            "Smart Lock": "ZONE_C_SECURITY",
            "Environmental Sensor": "ZONE_B_SENSORS",
            "Smart Lighting": "ZONE_D_LIGHTING",
            "Security Camera": "ZONE_C_SECURITY",
            "Smart Blinds": "ZONE_A_ELECTRONICS",
            "Smart Plug": "ZONE_A_ELECTRONICS"
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
    
    def notify_logistics(self, order_id: str) -> AgentResponse:
        """
        Notify the logistics platform to prepare the order for shipment.
        
        Args:
            order_id: ID of the order to prepare
            
        Returns:
            AgentResponse with logistics notification results
        """
        try:
            self.log_action("LOGISTICS_NOTIFICATION_START", f"Starting logistics notification for order {order_id}", order_id)
            
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
            
            # Generate pick list for warehouse
            pick_list = self._generate_pick_list(order)
            
            # Assign warehouse zones
            zone_assignments = self._assign_warehouse_zones(order)
            
            # Create packing instructions
            packing_instructions = self._create_packing_instructions(order)
            
            # Generate shipping labels (mock)
            shipping_labels = self._generate_shipping_labels(order)
            
            # Update warehouse capacity
            self._update_warehouse_capacity(zone_assignments)
            
            # Create logistics notification
            logistics_data = {
                "order_id": order_id,
                "pick_list": pick_list,
                "zone_assignments": zone_assignments,
                "packing_instructions": packing_instructions,
                "shipping_labels": shipping_labels,
                "priority": self._determine_order_priority(order),
                "estimated_prep_time": self._estimate_preparation_time(order),
                "notification_timestamp": datetime.now().isoformat()
            }
            
            # Simulate sending to warehouse management system
            notification_result = self._send_to_warehouse_system(logistics_data)
            
            self.log_action("LOGISTICS_NOTIFICATION_COMPLETE", 
                          f"Logistics platform notified for order {order_id} - Reference: {notification_result['reference_id']}", 
                          order_id)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Logistics platform successfully notified for order {order_id}",
                data={
                    "order_id": order_id,
                    "warehouse_reference": notification_result["reference_id"],
                    "logistics_data": logistics_data,
                    "estimated_ship_date": notification_result["estimated_ship_date"]
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Logistics notification failed for order {order_id}: {str(e)}"
            self.log_action("ERROR", error_msg, order_id)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def _generate_pick_list(self, order: Order) -> List[Dict[str, Any]]:
        """Generate a pick list for warehouse workers."""
        self.log_action("PICK_LIST_GENERATION", f"Generating pick list for {len(order.items)} items", order.id)
        
        pick_list = []
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if not product:
                continue
            
            pick_item = {
                "product_id": product.id,
                "product_name": product.name,
                "category": product.category,
                "quantity": item.quantity,
                "location": self._get_product_location(product.id, product.category),
                "handling_instructions": self._get_handling_instructions(product.category),
                "priority": "high" if item.availability_status == "available" else "normal"
            }
            pick_list.append(pick_item)
            
            self.log_action("PICK_ITEM", f"Added to pick list: {product.name} x{item.quantity} from {pick_item['location']}", order.id)
        
        # Sort by warehouse zone for efficient picking
        pick_list.sort(key=lambda x: x["location"]["zone"])
        
        return pick_list
    
    def _assign_warehouse_zones(self, order: Order) -> Dict[str, List[Dict[str, Any]]]:
        """Assign items to warehouse zones based on product categories."""
        self.log_action("ZONE_ASSIGNMENT", f"Assigning warehouse zones for order items", order.id)
        
        zone_assignments = {}
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if not product:
                continue
            
            zone = self.category_zone_mapping.get(product.category, "ZONE_A_ELECTRONICS")
            
            if zone not in zone_assignments:
                zone_assignments[zone] = []
            
            zone_assignments[zone].append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "shelf_location": f"{zone}-{product.id[-3:]}",
                "handling_priority": "fragile" if "sensor" in product.category.lower() else "standard"
            })
            
            self.log_action("ZONE_ASSIGNED", f"{product.name} assigned to {zone}", order.id)
        
        return zone_assignments
    
    def _create_packing_instructions(self, order: Order) -> Dict[str, Any]:
        """Create packing instructions based on product types and shipping requirements."""
        self.log_action("PACKING_INSTRUCTIONS", f"Creating packing instructions for order", order.id)
        
        # Analyze products for packing requirements
        fragile_items = []
        heavy_items = []
        electronic_items = []
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if not product:
                continue
            
            if "sensor" in product.category.lower() or "camera" in product.category.lower():
                fragile_items.append({"product_id": product.id, "name": product.name, "quantity": item.quantity})
            
            if product.category in ["Smart Lock", "Smart Curtain"]:
                heavy_items.append({"product_id": product.id, "name": product.name, "quantity": item.quantity})
            
            electronic_items.append({"product_id": product.id, "name": product.name, "quantity": item.quantity})
        
        instructions = {
            "general_instructions": [
                "Use anti-static packaging for all electronic items",
                "Include product manuals and quick start guides",
                "Add ContosoMesh branding materials"
            ],
            "fragile_items": fragile_items,
            "heavy_items": heavy_items,
            "electronic_items": electronic_items,
            "packaging_materials": self._select_packaging_materials(order),
            "quality_checks": [
                "Verify all items against pick list",
                "Check for product damage",
                "Ensure proper cushioning",
                "Validate shipping labels"
            ]
        }
        
        if fragile_items:
            instructions["general_instructions"].append("Use extra cushioning for fragile sensor items")
            self.log_action("PACKING_NOTE", f"Special handling required for {len(fragile_items)} fragile items", order.id)
        
        if heavy_items:
            instructions["general_instructions"].append("Use reinforced packaging for heavy items")
            self.log_action("PACKING_NOTE", f"Reinforced packaging needed for {len(heavy_items)} heavy items", order.id)
        
        return instructions
    
    def _generate_shipping_labels(self, order: Order) -> List[Dict[str, Any]]:
        """Generate shipping labels for the order parcels."""
        self.log_action("SHIPPING_LABELS", f"Generating shipping labels for order", order.id)
        
        # Mock shipping label generation
        labels = []
        
        # For this demo, create one label per order
        # In reality, this would integrate with delivery agent's parcel information
        label = {
            "label_id": f"LABEL-{order.id}",
            "tracking_number": f"CM{datetime.now().strftime('%Y%m%d')}{order.id[-4:]}",
            "shipping_address": {
                "customer_name": order.customer_name,
                "email": order.customer_email,
                # Mock address - in reality this would come from order data
                "address_line1": "123 Customer Street",
                "city": "Customer City",
                "postal_code": "12345",
                "country": "USA"
            },
            "sender_address": {
                "company": "ContosoMesh",
                "address_line1": "456 Warehouse Ave",
                "city": "Distribution Center",
                "postal_code": "54321",
                "country": "USA"
            },
            "service_type": "Standard",
            "weight": "2.5 kg",  # Mock weight
            "dimensions": "30x20x15 cm",  # Mock dimensions
            "special_instructions": []
        }
        
        # Add special instructions based on products
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product and "sensor" in product.category.lower():
                if "FRAGILE" not in label["special_instructions"]:
                    label["special_instructions"].append("FRAGILE")
        
        labels.append(label)
        
        self.log_action("LABEL_GENERATED", f"Shipping label generated: {label['tracking_number']}", order.id)
        
        return labels
    
    def _determine_order_priority(self, order: Order) -> str:
        """Determine order priority based on various factors."""
        # Check if customer is a premium customer (mock logic)
        if "premium" in order.customer_email.lower():
            return "HIGH"
        
        # Check order value
        if order.total_amount and order.total_amount > 500:
            return "HIGH"
        
        # Check for urgent items (items with low stock)
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product and product.stock <= 5:
                return "MEDIUM"
        
        return "NORMAL"
    
    def _estimate_preparation_time(self, order: Order) -> str:
        """Estimate time needed to prepare the order."""
        # Base time per item
        base_time_minutes = len(order.items) * 5
        
        # Add time for special handling
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product:
                if "sensor" in product.category.lower():
                    base_time_minutes += 3  # Extra time for fragile items
                if product.category == "Smart Lock":
                    base_time_minutes += 5  # Extra time for heavy items
        
        # Convert to hours and minutes
        hours = base_time_minutes // 60
        minutes = base_time_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _get_product_location(self, product_id: str, category: str) -> Dict[str, Any]:
        """Get warehouse location for a product."""
        zone = self.category_zone_mapping.get(category, "ZONE_A_ELECTRONICS")
        
        return {
            "zone": zone,
            "aisle": f"A{product_id[-2:]}",
            "shelf": f"S{product_id[-1]}",
            "bin": f"B{hash(product_id) % 100:02d}"
        }
    
    def _get_handling_instructions(self, category: str) -> List[str]:
        """Get handling instructions based on product category."""
        instructions = {
            "Security Sensor": ["Handle with care", "Avoid static discharge", "Keep upright"],
            "Environmental Sensor": ["Fragile - cushion well", "Avoid moisture", "Temperature sensitive"],
            "Security Camera": ["Fragile electronics", "Protect lens", "Handle with care"],
            "Smart Lock": ["Heavy item", "Secure packaging", "Check for completeness"],
            "Smart Lighting": ["Fragile bulb", "Avoid dropping", "Test before packing"]
        }
        
        return instructions.get(category, ["Standard handling", "Keep dry"])
    
    def _select_packaging_materials(self, order: Order) -> List[str]:
        """Select appropriate packaging materials based on order contents."""
        materials = ["Cardboard box", "Bubble wrap", "Packing paper"]
        
        # Add special materials based on products
        has_fragile = False
        has_heavy = False
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product:
                if "sensor" in product.category.lower() or "camera" in product.category.lower():
                    has_fragile = True
                if product.category in ["Smart Lock", "Smart Curtain"]:
                    has_heavy = True
        
        if has_fragile:
            materials.extend(["Anti-static bubble wrap", "Foam inserts"])
        
        if has_heavy:
            materials.extend(["Reinforced box", "Extra padding"])
        
        return materials
    
    def _update_warehouse_capacity(self, zone_assignments: Dict[str, List[Dict[str, Any]]]):
        """Update warehouse zone capacity (mock operation)."""
        for zone, items in zone_assignments.items():
            if zone in self.warehouse_zones:
                # Mock capacity update - in reality this would be more sophisticated
                items_count = sum(item["quantity"] for item in items)
                self.warehouse_zones[zone]["current_load"] += items_count
                
                utilization = (self.warehouse_zones[zone]["current_load"] / 
                             self.warehouse_zones[zone]["capacity"]) * 100
                
                self.log_action("CAPACITY_UPDATE", 
                              f"{zone}: +{items_count} items, {utilization:.1f}% utilization")
    
    def _send_to_warehouse_system(self, logistics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate sending data to warehouse management system."""
        # Mock integration with warehouse system
        reference_id = f"WMS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Simulate processing time and response
        estimated_ship_date = (datetime.now() + 
                             datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Log the "API call"
        self.log_action("WMS_INTEGRATION", f"Data sent to warehouse system - Reference: {reference_id}")
        
        return {
            "reference_id": reference_id,
            "status": "accepted",
            "estimated_ship_date": estimated_ship_date,
            "confirmation_timestamp": datetime.now().isoformat()
        }
    
    def get_warehouse_status(self) -> AgentResponse:
        """Get current warehouse status and capacity information."""
        try:
            self.log_action("WAREHOUSE_STATUS", "Retrieving warehouse status information")
            
            total_capacity = sum(zone["capacity"] for zone in self.warehouse_zones.values())
            total_load = sum(zone["current_load"] for zone in self.warehouse_zones.values())
            overall_utilization = (total_load / total_capacity) * 100
            
            zone_status = []
            for zone_name, zone_info in self.warehouse_zones.items():
                utilization = (zone_info["current_load"] / zone_info["capacity"]) * 100
                zone_status.append({
                    "zone": zone_name,
                    "specialization": zone_info["specialization"],
                    "capacity": zone_info["capacity"],
                    "current_load": zone_info["current_load"],
                    "utilization_percent": round(utilization, 1),
                    "status": "high" if utilization > 80 else "medium" if utilization > 60 else "normal"
                })
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message="Warehouse status retrieved successfully",
                data={
                    "overall_utilization": round(overall_utilization, 1),
                    "total_capacity": total_capacity,
                    "total_load": total_load,
                    "zone_status": zone_status,
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Failed to get warehouse status: {str(e)}"
            self.log_action("ERROR", error_msg)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )