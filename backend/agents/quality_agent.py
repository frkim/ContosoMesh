"""
Quality Agent - Advanced reasoning agent for ContosoMesh order quality control.
This agent uses reasoning to perform comprehensive quality checks on orders,
including product compatibility, customer satisfaction analysis, and risk assessment.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from models.schemas import Order, OrderItem, AgentResponse, AgentLog
from database.db import Database

class QualityAgent:
    def __init__(self, database: Database):
        self.name = "Quality Agent"
        self.color = "#059669"  # Emerald
        self.database = database
        self.agent_logs = []
        
        # Product compatibility matrix
        self.compatibility_matrix = {
            "Smart Home Hub": {
                "enhances": ["Smart Switch", "Smart Curtain", "Security Sensor", "Smart Lock", "Environmental Sensor", "Smart Lighting", "Smart Blinds", "Smart Plug"],
                "conflicts": [],
                "requires": []
            },
            "Smart Switch": {
                "enhances": ["Smart Home Hub", "Smart Lighting"],
                "conflicts": [],
                "requires": ["Smart Home Hub"]
            },
            "Smart Curtain": {
                "enhances": ["Environmental Sensor", "Smart Blinds"],
                "conflicts": [],
                "requires": ["Smart Home Hub"]
            },
            "Security Sensor": {
                "enhances": ["Security Camera", "Smart Lock"],
                "conflicts": [],
                "requires": ["Smart Home Hub"]
            },
            "Smart Lock": {
                "enhances": ["Security Sensor", "Security Camera"],
                "conflicts": [],
                "requires": ["Smart Home Hub"]
            }
        }
        
        # Risk factors for quality assessment
        self.risk_factors = {
            "high_value_threshold": 1000.0,
            "fragile_categories": ["Security Sensor", "Environmental Sensor", "Security Camera"],
            "complex_setup_categories": ["Smart Home Hub", "Smart Lock", "Smart Curtain"],
            "compatibility_critical_categories": ["Smart Switch", "Smart Curtain", "Smart Blinds"]
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
    
    def perform_quality_check(self, order_id: str) -> AgentResponse:
        """
        Perform comprehensive quality check using advanced reasoning.
        
        Args:
            order_id: ID of the order to analyze
            
        Returns:
            AgentResponse with quality assessment results
        """
        try:
            self.log_action("QUALITY_CHECK_START", f"Starting comprehensive quality analysis for order {order_id}", order_id)
            
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
            
            # Perform multi-dimensional quality analysis
            compatibility_analysis = self._analyze_product_compatibility(order)
            risk_assessment = self._perform_risk_assessment(order)
            customer_satisfaction_prediction = self._predict_customer_satisfaction(order)
            setup_complexity_analysis = self._analyze_setup_complexity(order)
            packaging_optimization = self._analyze_packaging_optimization(order)
            
            # Use reasoning to generate overall quality score and recommendations
            quality_reasoning = self._reason_quality_assessment(
                compatibility_analysis,
                risk_assessment,
                customer_satisfaction_prediction,
                setup_complexity_analysis,
                packaging_optimization
            )
            
            # Generate quality report
            quality_report = self._generate_quality_report(order, quality_reasoning)
            
            # Determine if order requires intervention
            intervention_required = quality_reasoning["overall_score"] < 7.0 or any(
                issue["severity"] == "high" for issue in quality_reasoning["identified_issues"]
            )
            
            if intervention_required:
                self.log_action("QUALITY_ALERT", f"Order requires intervention - Score: {quality_reasoning['overall_score']}/10", order_id)
            else:
                self.log_action("QUALITY_APPROVED", f"Order meets quality standards - Score: {quality_reasoning['overall_score']}/10", order_id)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Quality check completed for order {order_id}",
                data={
                    "order_id": order_id,
                    "quality_score": quality_reasoning["overall_score"],
                    "intervention_required": intervention_required,
                    "compatibility_analysis": compatibility_analysis,
                    "risk_assessment": risk_assessment,
                    "customer_satisfaction_prediction": customer_satisfaction_prediction,
                    "setup_complexity_analysis": setup_complexity_analysis,
                    "packaging_optimization": packaging_optimization,
                    "quality_reasoning": quality_reasoning,
                    "quality_report": quality_report
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Quality check failed for order {order_id}: {str(e)}"
            self.log_action("ERROR", error_msg, order_id)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                message=error_msg,
                timestamp=datetime.now()
            )
    
    def _analyze_product_compatibility(self, order: Order) -> Dict[str, Any]:
        """Analyze product compatibility within the order."""
        self.log_action("COMPATIBILITY_ANALYSIS", "Analyzing product compatibility and ecosystem coherence", order.id)
        
        products_in_order = []
        categories_in_order = set()
        
        # Collect product information
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product:
                products_in_order.append({
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "quantity": item.quantity
                })
                categories_in_order.add(product.category)
        
        # Check for hub requirement
        has_hub = "Smart Home Hub" in categories_in_order
        needs_hub = any(
            category in self.compatibility_matrix and 
            "Smart Home Hub" in self.compatibility_matrix.get(category, {}).get("requires", [])
            for category in categories_in_order
        )
        
        compatibility_issues = []
        enhancement_opportunities = []
        missing_components = []
        
        # Check compatibility requirements
        if needs_hub and not has_hub:
            compatibility_issues.append({
                "type": "missing_hub",
                "severity": "high",
                "message": "Order contains smart devices that require a Smart Home Hub",
                "recommendation": "Add SwitchBot Hub Mini to enable all device functionality"
            })
            missing_components.append("Smart Home Hub")
        
        # Check for enhancement opportunities
        if has_hub:
            hub_compatible_categories = self.compatibility_matrix["Smart Home Hub"]["enhances"]
            for category in hub_compatible_categories:
                if category not in categories_in_order:
                    enhancement_opportunities.append({
                        "category": category,
                        "reason": f"Would complement existing {', '.join(categories_in_order)} setup"
                    })
        
        # Check for product synergies
        synergies = []
        for product in products_in_order:
            category = product["category"]
            if category in self.compatibility_matrix:
                enhances = self.compatibility_matrix[category]["enhances"]
                for other_product in products_in_order:
                    if other_product["category"] in enhances:
                        synergies.append({
                            "product1": product["name"],
                            "product2": other_product["name"],
                            "synergy_type": "functional_enhancement"
                        })
        
        compatibility_score = 10.0
        if compatibility_issues:
            compatibility_score -= len(compatibility_issues) * 2.0
        
        compatibility_score = max(1.0, min(10.0, compatibility_score))
        
        self.log_action("COMPATIBILITY_RESULT", f"Compatibility score: {compatibility_score}/10 ({len(compatibility_issues)} issues found)", order.id)
        
        return {
            "compatibility_score": compatibility_score,
            "has_hub": has_hub,
            "needs_hub": needs_hub,
            "compatibility_issues": compatibility_issues,
            "enhancement_opportunities": enhancement_opportunities[:3],  # Limit to top 3
            "synergies": synergies,
            "missing_components": missing_components
        }
    
    def _perform_risk_assessment(self, order: Order) -> Dict[str, Any]:
        """Perform comprehensive risk assessment for the order."""
        self.log_action("RISK_ASSESSMENT", "Performing multi-factor risk assessment", order.id)
        
        risks = []
        total_risk_score = 0.0
        
        # Financial risk assessment
        if order.total_amount and order.total_amount > self.risk_factors["high_value_threshold"]:
            financial_risk = {
                "type": "high_value_order",
                "severity": "medium",
                "score": 2.0,
                "description": f"High-value order (${order.total_amount:.2f}) requires extra care",
                "mitigation": "Enhanced packaging and insurance coverage recommended"
            }
            risks.append(financial_risk)
            total_risk_score += financial_risk["score"]
        
        # Product fragility risk
        fragile_count = 0
        fragile_products = []
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product and product.category in self.risk_factors["fragile_categories"]:
                fragile_count += item.quantity
                fragile_products.append(f"{product.name} x{item.quantity}")
        
        if fragile_count > 0:
            fragility_risk = {
                "type": "fragile_products",
                "severity": "high" if fragile_count > 3 else "medium",
                "score": min(3.0, fragile_count * 0.5),
                "description": f"Order contains {fragile_count} fragile items: {', '.join(fragile_products)}",
                "mitigation": "Use enhanced protective packaging and fragile handling procedures"
            }
            risks.append(fragility_risk)
            total_risk_score += fragility_risk["score"]
        
        # Setup complexity risk
        complex_setup_count = 0
        complex_products = []
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product and product.category in self.risk_factors["complex_setup_categories"]:
                complex_setup_count += item.quantity
                complex_products.append(product.name)
        
        if complex_setup_count > 2:
            complexity_risk = {
                "type": "complex_setup",
                "severity": "medium",
                "score": 1.5,
                "description": f"Multiple complex devices may challenge customer setup: {', '.join(set(complex_products))}",
                "mitigation": "Include detailed setup guide and offer installation support"
            }
            risks.append(complexity_risk)
            total_risk_score += complexity_risk["score"]
        
        # Stock availability risk
        availability_risk_count = 0
        for item in order.items:
            if item.availability_status != "available":
                availability_risk_count += 1
        
        if availability_risk_count > 0:
            availability_risk = {
                "type": "stock_availability",
                "severity": "medium" if availability_risk_count > 2 else "low",
                "score": availability_risk_count * 0.5,
                "description": f"{availability_risk_count} items have availability issues",
                "mitigation": "Consider partial shipment or customer communication about delays"
            }
            risks.append(availability_risk)
            total_risk_score += availability_risk["score"]
        
        # Calculate overall risk level
        if total_risk_score >= 5.0:
            risk_level = "high"
        elif total_risk_score >= 2.0:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        self.log_action("RISK_RESULT", f"Risk assessment: {risk_level} ({total_risk_score:.1f} points, {len(risks)} factors)", order.id)
        
        return {
            "risk_level": risk_level,
            "total_risk_score": total_risk_score,
            "risks": risks,
            "risk_factors_count": len(risks)
        }
    
    def _predict_customer_satisfaction(self, order: Order) -> Dict[str, Any]:
        """Predict customer satisfaction based on order analysis."""
        self.log_action("SATISFACTION_PREDICTION", "Predicting customer satisfaction using behavioral analysis", order.id)
        
        satisfaction_factors = []
        satisfaction_score = 8.0  # Base satisfaction score
        
        # Product ecosystem completeness
        has_hub = False
        smart_device_count = 0
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product:
                if product.category == "Smart Home Hub":
                    has_hub = True
                    satisfaction_factors.append({
                        "factor": "ecosystem_hub",
                        "impact": 1.5,
                        "description": "Smart Home Hub enables full ecosystem functionality"
                    })
                    satisfaction_score += 1.5
                
                if "Smart" in product.category:
                    smart_device_count += item.quantity
        
        # Ecosystem synergy bonus
        if smart_device_count >= 3 and has_hub:
            satisfaction_factors.append({
                "factor": "ecosystem_synergy",
                "impact": 1.0,
                "description": f"Multiple smart devices ({smart_device_count}) create comprehensive smart home"
            })
            satisfaction_score += 1.0
        
        # Price value assessment
        if order.discount_applied and order.discount_applied > 50:
            satisfaction_factors.append({
                "factor": "value_discount",
                "impact": 0.8,
                "description": f"Significant discount (${order.discount_applied:.2f}) provides excellent value"
            })
            satisfaction_score += 0.8
        
        # Product variety assessment
        unique_categories = set()
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product:
                unique_categories.add(product.category)
        
        if len(unique_categories) >= 3:
            satisfaction_factors.append({
                "factor": "product_variety",
                "impact": 0.5,
                "description": f"Diverse product selection ({len(unique_categories)} categories) indicates comprehensive needs fulfillment"
            })
            satisfaction_score += 0.5
        
        # Potential dissatisfaction factors
        dissatisfaction_risks = []
        
        # Check for missing hub when needed
        needs_hub = any(
            self.database.get_product(item.product_id) and
            self.database.get_product(item.product_id).category in self.risk_factors["compatibility_critical_categories"]
            for item in order.items
        )
        
        if needs_hub and not has_hub:
            dissatisfaction_risks.append({
                "risk": "incomplete_ecosystem",
                "impact": -2.0,
                "description": "Smart devices may not function optimally without hub"
            })
            satisfaction_score -= 2.0
        
        # Check for delayed items
        delayed_items = sum(1 for item in order.items if item.availability_status != "available")
        if delayed_items > 0:
            delay_impact = min(-1.5, -delayed_items * 0.3)
            dissatisfaction_risks.append({
                "risk": "delivery_delays",
                "impact": delay_impact,
                "description": f"{delayed_items} items delayed may impact satisfaction"
            })
            satisfaction_score += delay_impact  # Adding negative value
        
        # Normalize satisfaction score
        satisfaction_score = max(1.0, min(10.0, satisfaction_score))
        
        # Predict satisfaction category
        if satisfaction_score >= 8.5:
            predicted_satisfaction = "very_high"
        elif satisfaction_score >= 7.0:
            predicted_satisfaction = "high"
        elif satisfaction_score >= 5.5:
            predicted_satisfaction = "medium"
        elif satisfaction_score >= 4.0:
            predicted_satisfaction = "low"
        else:
            predicted_satisfaction = "very_low"
        
        self.log_action("SATISFACTION_RESULT", f"Predicted satisfaction: {predicted_satisfaction} ({satisfaction_score:.1f}/10)", order.id)
        
        return {
            "predicted_satisfaction": predicted_satisfaction,
            "satisfaction_score": satisfaction_score,
            "satisfaction_factors": satisfaction_factors,
            "dissatisfaction_risks": dissatisfaction_risks,
            "recommendations": self._generate_satisfaction_recommendations(satisfaction_factors, dissatisfaction_risks)
        }
    
    def _analyze_setup_complexity(self, order: Order) -> Dict[str, Any]:
        """Analyze the setup complexity for the customer."""
        self.log_action("SETUP_ANALYSIS", "Analyzing customer setup complexity and support requirements", order.id)
        
        complexity_levels = {
            "Smart Home Hub": 3,
            "Smart Switch": 1,
            "Smart Curtain": 4,
            "Security Sensor": 2,
            "Smart Lock": 5,
            "Environmental Sensor": 1,
            "Smart Lighting": 1,
            "Security Camera": 3,
            "Smart Blinds": 4,
            "Smart Plug": 1
        }
        
        total_complexity = 0
        complex_items = []
        setup_time_estimate = 0
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product:
                item_complexity = complexity_levels.get(product.category, 2)
                total_complexity += item_complexity * item.quantity
                setup_time_estimate += item_complexity * item.quantity * 10  # 10 minutes per complexity point
                
                if item_complexity >= 3:
                    complex_items.append({
                        "product": product.name,
                        "complexity": item_complexity,
                        "quantity": item.quantity,
                        "setup_notes": self._get_setup_notes(product.category)
                    })
        
        # Calculate average complexity
        total_items = sum(item.quantity for item in order.items)
        average_complexity = total_complexity / total_items if total_items > 0 else 0
        
        # Determine support recommendations
        support_recommendations = []
        
        if average_complexity >= 3.5:
            support_recommendations.append("Offer professional installation service")
        if len(complex_items) >= 2:
            support_recommendations.append("Provide video setup tutorials")
        if total_complexity >= 15:
            support_recommendations.append("Include priority customer support contact")
        
        complexity_assessment = {
            "complexity_level": "high" if average_complexity >= 3 else "medium" if average_complexity >= 2 else "low",
            "total_complexity_score": total_complexity,
            "average_complexity": round(average_complexity, 1),
            "estimated_setup_time_minutes": setup_time_estimate,
            "complex_items": complex_items,
            "support_recommendations": support_recommendations,
            "setup_difficulty": self._categorize_setup_difficulty(average_complexity)
        }
        
        self.log_action("SETUP_RESULT", f"Setup complexity: {complexity_assessment['complexity_level']} ({average_complexity:.1f}/5, {setup_time_estimate}min estimated)", order.id)
        
        return complexity_assessment
    
    def _analyze_packaging_optimization(self, order: Order) -> Dict[str, Any]:
        """Analyze packaging optimization opportunities."""
        self.log_action("PACKAGING_ANALYSIS", "Analyzing packaging optimization and protection requirements", order.id)
        
        fragile_items = []
        heavy_items = []
        small_items = []
        
        total_estimated_weight = 0
        total_estimated_volume = 0
        
        for item in order.items:
            product = self.database.get_product(item.product_id)
            if product:
                # Mock weight and volume calculations
                estimated_weight = self._estimate_weight(product.category) * item.quantity
                estimated_volume = self._estimate_volume(product.category) * item.quantity
                
                total_estimated_weight += estimated_weight
                total_estimated_volume += estimated_volume
                
                if product.category in self.risk_factors["fragile_categories"]:
                    fragile_items.append({"product": product.name, "quantity": item.quantity})
                
                if estimated_weight > 1.0:  # Heavy items > 1kg
                    heavy_items.append({"product": product.name, "weight": estimated_weight})
                
                if estimated_volume < 0.1:  # Small items < 0.1L
                    small_items.append({"product": product.name, "quantity": item.quantity})
        
        # Packaging recommendations
        packaging_recommendations = []
        
        if fragile_items:
            packaging_recommendations.append("Use protective bubble wrap and foam inserts")
        if heavy_items:
            packaging_recommendations.append("Use reinforced boxes for heavy items")
        if len(small_items) >= 3:
            packaging_recommendations.append("Consider consolidation packaging for small items")
        if total_estimated_weight > 5.0:
            packaging_recommendations.append("Consider splitting into multiple packages")
        
        packaging_optimization = {
            "total_estimated_weight_kg": round(total_estimated_weight, 2),
            "total_estimated_volume_liters": round(total_estimated_volume, 2),
            "fragile_items_count": len(fragile_items),
            "heavy_items_count": len(heavy_items),
            "small_items_count": len(small_items),
            "packaging_recommendations": packaging_recommendations,
            "estimated_packaging_cost": self._estimate_packaging_cost(total_estimated_weight, len(fragile_items))
        }
        
        self.log_action("PACKAGING_RESULT", f"Packaging analysis: {total_estimated_weight:.1f}kg, {len(packaging_recommendations)} recommendations", order.id)
        
        return packaging_optimization
    
    def _reason_quality_assessment(self, compatibility_analysis, risk_assessment, satisfaction_prediction, setup_analysis, packaging_analysis) -> Dict[str, Any]:
        """Use reasoning to synthesize all analyses into overall quality assessment."""
        self.log_action("QUALITY_REASONING", "Synthesizing multi-dimensional analysis using advanced reasoning")
        
        reasoning_steps = []
        identified_issues = []
        recommendations = []
        
        # Weight factors for overall score
        weights = {
            "compatibility": 0.25,
            "risk": 0.20,
            "satisfaction": 0.30,
            "setup": 0.15,
            "packaging": 0.10
        }
        
        # Score calculations with reasoning
        compatibility_score = compatibility_analysis["compatibility_score"]
        risk_score = max(1.0, 10.0 - risk_assessment["total_risk_score"])
        satisfaction_score = satisfaction_prediction["satisfaction_score"]
        setup_score = 10.0 - min(9.0, setup_analysis["average_complexity"] * 2)
        packaging_score = 8.0  # Base packaging score
        
        reasoning_steps.append(f"Compatibility score: {compatibility_score}/10 - Product ecosystem coherence")
        reasoning_steps.append(f"Risk-adjusted score: {risk_score}/10 - Multi-factor risk mitigation")
        reasoning_steps.append(f"Satisfaction prediction: {satisfaction_score}/10 - Customer experience forecast")
        reasoning_steps.append(f"Setup complexity score: {setup_score}/10 - Customer capability assessment")
        reasoning_steps.append(f"Packaging efficiency: {packaging_score}/10 - Protection and cost optimization")
        
        # Calculate weighted overall score
        overall_score = (
            compatibility_score * weights["compatibility"] +
            risk_score * weights["risk"] +
            satisfaction_score * weights["satisfaction"] +
            setup_score * weights["setup"] +
            packaging_score * weights["packaging"]
        )
        
        # Identify critical issues requiring intervention
        if compatibility_analysis["compatibility_issues"]:
            for issue in compatibility_analysis["compatibility_issues"]:
                if issue["severity"] == "high":
                    identified_issues.append({
                        "category": "compatibility",
                        "severity": "high",
                        "description": issue["message"],
                        "recommendation": issue["recommendation"]
                    })
        
        if risk_assessment["risk_level"] == "high":
            identified_issues.append({
                "category": "risk",
                "severity": "high", 
                "description": f"High risk level ({risk_assessment['total_risk_score']:.1f} points)",
                "recommendation": "Implement enhanced quality control procedures"
            })
        
        if satisfaction_prediction["predicted_satisfaction"] in ["low", "very_low"]:
            identified_issues.append({
                "category": "satisfaction",
                "severity": "medium",
                "description": f"Low predicted satisfaction ({satisfaction_prediction['satisfaction_score']:.1f}/10)",
                "recommendation": "Consider customer outreach and support enhancement"
            })
        
        # Generate strategic recommendations
        if overall_score >= 8.5:
            recommendations.append("Order exceeds quality standards - consider as reference case")
        elif overall_score < 6.0:
            recommendations.append("Order requires quality intervention before fulfillment")
        
        if compatibility_analysis["enhancement_opportunities"]:
            recommendations.append("Suggest complementary products to enhance customer ecosystem")
        
        if setup_analysis["complexity_level"] == "high":
            recommendations.append("Proactively offer installation support and setup guides")
        
        reasoning_result = {
            "overall_score": round(overall_score, 1),
            "score_breakdown": {
                "compatibility": round(compatibility_score * weights["compatibility"], 2),
                "risk": round(risk_score * weights["risk"], 2),
                "satisfaction": round(satisfaction_score * weights["satisfaction"], 2),
                "setup": round(setup_score * weights["setup"], 2),
                "packaging": round(packaging_score * weights["packaging"], 2)
            },
            "reasoning_steps": reasoning_steps,
            "identified_issues": identified_issues,
            "recommendations": recommendations,
            "quality_grade": self._assign_quality_grade(overall_score)
        }
        
        self.log_action("REASONING_COMPLETE", f"Quality reasoning complete - Grade: {reasoning_result['quality_grade']} ({overall_score:.1f}/10)")
        
        return reasoning_result
    
    def _generate_quality_report(self, order: Order, quality_reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        return {
            "report_id": f"QR-{order.id}-{datetime.now().strftime('%Y%m%d%H%M')}",
            "order_id": order.id,
            "customer": order.customer_name,
            "analysis_timestamp": datetime.now().isoformat(),
            "overall_assessment": {
                "grade": quality_reasoning["quality_grade"],
                "score": quality_reasoning["overall_score"],
                "intervention_required": quality_reasoning["overall_score"] < 7.0
            },
            "key_findings": [
                f"Quality grade: {quality_reasoning['quality_grade']}",
                f"Risk level: {quality_reasoning.get('risk_level', 'unknown')}",
                f"Predicted satisfaction: {quality_reasoning.get('predicted_satisfaction', 'unknown')}",
                f"Issues identified: {len(quality_reasoning['identified_issues'])}"
            ],
            "recommendations": quality_reasoning["recommendations"],
            "next_actions": self._determine_next_actions(quality_reasoning)
        }
    
    def _get_setup_notes(self, category: str) -> List[str]:
        """Get setup notes for a product category."""
        notes = {
            "Smart Home Hub": ["Central hub setup", "Wi-Fi configuration", "Device pairing"],
            "Smart Lock": ["Door measurement", "Installation tools required", "Security configuration"],
            "Smart Curtain": ["Curtain rail attachment", "Motor calibration", "Schedule setup"],
            "Security Camera": ["Mounting position", "Network configuration", "Privacy settings"]
        }
        return notes.get(category, ["Standard setup required"])
    
    def _categorize_setup_difficulty(self, average_complexity: float) -> str:
        """Categorize setup difficulty based on complexity score."""
        if average_complexity >= 4:
            return "Expert level - professional installation recommended"
        elif average_complexity >= 3:
            return "Advanced - technical knowledge helpful"
        elif average_complexity >= 2:
            return "Intermediate - some technical experience needed"
        else:
            return "Beginner friendly - easy setup"
    
    def _estimate_weight(self, category: str) -> float:
        """Estimate product weight by category."""
        weights = {
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
        return weights.get(category, 0.2)
    
    def _estimate_volume(self, category: str) -> float:
        """Estimate product volume by category (in liters)."""
        volumes = {
            "Smart Home Hub": 0.2,
            "Smart Switch": 0.05,
            "Smart Curtain": 1.5,
            "Security Sensor": 0.02,
            "Smart Lock": 0.8,
            "Environmental Sensor": 0.03,
            "Smart Lighting": 0.1,
            "Security Camera": 0.3,
            "Smart Blinds": 1.0,
            "Smart Plug": 0.08
        }
        return volumes.get(category, 0.1)
    
    def _estimate_packaging_cost(self, weight: float, fragile_count: int) -> float:
        """Estimate packaging cost based on weight and fragility."""
        base_cost = 5.0
        weight_cost = weight * 0.5
        fragile_cost = fragile_count * 2.0
        return round(base_cost + weight_cost + fragile_cost, 2)
    
    def _generate_satisfaction_recommendations(self, factors: List[Dict], risks: List[Dict]) -> List[str]:
        """Generate recommendations to enhance customer satisfaction."""
        recommendations = []
        
        if any(factor["factor"] == "ecosystem_hub" for factor in factors):
            recommendations.append("Highlight ecosystem benefits in communication")
        
        if any(risk["risk"] == "incomplete_ecosystem" for risk in risks):
            recommendations.append("Proactively suggest Smart Home Hub addition")
        
        if any(risk["risk"] == "delivery_delays" for risk in risks):
            recommendations.append("Communicate proactively about delivery timelines")
        
        return recommendations
    
    def _assign_quality_grade(self, score: float) -> str:
        """Assign quality grade based on overall score."""
        if score >= 9.0:
            return "A+"
        elif score >= 8.5:
            return "A"
        elif score >= 8.0:
            return "A-"
        elif score >= 7.5:
            return "B+"
        elif score >= 7.0:
            return "B"
        elif score >= 6.5:
            return "B-"
        elif score >= 6.0:
            return "C+"
        elif score >= 5.5:
            return "C"
        else:
            return "D"
    
    def _determine_next_actions(self, quality_reasoning: Dict[str, Any]) -> List[str]:
        """Determine next actions based on quality assessment."""
        actions = []
        
        if quality_reasoning["overall_score"] < 6.0:
            actions.append("Hold order for quality review")
        
        if any(issue["severity"] == "high" for issue in quality_reasoning["identified_issues"]):
            actions.append("Customer service intervention required")
        
        if quality_reasoning["overall_score"] >= 8.5:
            actions.append("Expedite order processing")
            actions.append("Consider for customer testimonial")
        
        return actions