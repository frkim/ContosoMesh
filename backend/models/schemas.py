from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProductCategory(str, Enum):
    SMART_HOME_HUB = "Smart Home Hub"
    SMART_SWITCH = "Smart Switch"
    SMART_CURTAIN = "Smart Curtain"
    SECURITY_SENSOR = "Security Sensor"
    SMART_LOCK = "Smart Lock"
    ENVIRONMENTAL_SENSOR = "Environmental Sensor"
    SMART_LIGHTING = "Smart Lighting"
    SECURITY_CAMERA = "Security Camera"
    SMART_BLINDS = "Smart Blinds"
    SMART_PLUG = "Smart Plug"

class Product(BaseModel):
    id: str
    name: str
    category: ProductCategory
    description: str
    price: float
    stock: int
    next_availability: Optional[str] = None
    features: List[str]
    specifications: Dict[str, Any]

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    STOCKS_CHECKED = "stocks_checked"
    PRICED = "priced"
    DELIVERY_PLANNED = "delivery_planned"
    LOGISTICS_NOTIFIED = "logistics_notified"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    availability_status: Optional[str] = None
    next_availability: Optional[str] = None

class Order(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    total_amount: Optional[float] = None
    discount_applied: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    agent_logs: List[Dict[str, Any]] = []

class ParcelInfo(BaseModel):
    parcel_id: str
    items: List[OrderItem]
    estimated_delivery: Optional[str] = None
    shipping_method: str = "standard"

class AgentResponse(BaseModel):
    agent_name: str
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime

class AgentLog(BaseModel):
    agent_name: str
    action: str
    message: str
    timestamp: datetime
    order_id: Optional[str] = None
    color: str = "#000000"  # Color for UI display