#!/usr/bin/env python3
"""
Synthetic E-Commerce Data Generation Agent
Generates realistic, correlated e-commerce data for testing and ML training.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid
import random
import math
import numpy as np
import pandas as pd
from faker import Faker
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

@dataclass
class ScenarioConfig:
    """Configuration for different business scenarios"""
    name: str
    duration: str = "1d"
    intensity_multiplier: float = 1.0
    correlations: Optional[Dict[str, float]] = None
    special_params: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.correlations is None:
            self.correlations = {}
        if self.special_params is None:
            self.special_params = {}

class SyntheticDataGenerator:
    """Main synthetic data generation engine"""
    
    def __init__(self, output_dir: str = "data", output_format: str = "csv"):
        self.output_dir = Path(output_dir)
        self.output_format = output_format
        self.output_dir.mkdir(exist_ok=True)
        
        # Base correlation matrix from our earlier discussion
        self.base_correlations = {
            ("orders", "support_tickets"): 0.85,
            ("support_tickets", "delivery_delays"): 0.91,
            ("orders", "delivery_delays"): 0.72,
            ("orders", "cart_abandonment"): -0.43,
            ("support_tickets", "cart_abandonment"): -0.22,
            ("delivery_delays", "cart_abandonment"): -0.15,
        }
        
        # Initialize data containers
        self.data = {}
        self.scenario = None
        self.timestamp_start = datetime.now()
        
    def print_header(self, scenario_name: str):
        """Print CLI header with scenario info"""
        print("🚀 Synthetic Data Generation Agent v1.0")
        print(f"📊 Scenario: {scenario_name}")
        print(f"📁 Output Directory: {self.output_dir}")
        print(f"💾 Output Format: {self.output_format.upper()}")
        print()
        
    def generate_customers(self, count: int, scenario_config: ScenarioConfig) -> pd.DataFrame:
        """Generate customer data with realistic demographics"""
        cohorts = ["gen_z", "millennial", "gen_x", "boomer"]
        cohort_weights = [0.28, 0.35, 0.25, 0.12]  # Gen Z growing

        if scenario_config.special_params and "gen_z_growth" in scenario_config.special_params:
            print(f"  📈 Applying Gen Z growth factor: +{scenario_config.special_params['gen_z_growth']}%")
            cohort_weights[0] += scenario_config.special_params["gen_z_growth"] / 100
            # Normalize
            total = sum(cohort_weights)
            cohort_weights = [w/total for w in cohort_weights]
            
        acquisition_channels = ["organic", "paid_social", "influencer", "referral", "direct"]
        loyalty_tiers = ["Bronze", "Silver", "Gold", "Platinum"]
        
        customers = []
        for i in range(count):
            cohort = np.random.choice(cohorts, p=[float(w) for w in cohort_weights])
            
            # Cohort-specific behavior
            if cohort == "gen_z":
                acquisition_channel = np.random.choice(
                    ["paid_social", "influencer", "organic"], 
                    p=[0.4, 0.35, 0.25]
                )
                price_sensitivity = np.random.beta(2, 5)  # More price sensitive
            elif cohort == "boomer":
                acquisition_channel = np.random.choice(
                    ["direct", "organic", "referral"], 
                    p=[0.5, 0.3, 0.2]
                )
                price_sensitivity = np.random.beta(5, 2)  # Less price sensitive
            else:
                acquisition_channel = np.random.choice(acquisition_channels)
                price_sensitivity = np.random.beta(3, 3)
                
            customer = {
                "customer_id": str(uuid.uuid4()),
                "name": fake.name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "created_at": fake.date_time_between(start_date="-2y", end_date="now"),
                "loyalty_tier": np.random.choice(loyalty_tiers, p=[0.5, 0.3, 0.15, 0.05]),
                "cohort": cohort,
                "acquisition_channel": acquisition_channel,
                "city": fake.city(),
                "state": fake.state(),
                "lifetime_value": np.random.lognormal(4, 1),
                "price_sensitivity": price_sensitivity
            }
            customers.append(customer)
            
        return pd.DataFrame(customers)
    
    def generate_suppliers(self) -> pd.DataFrame:
        """Generate supplier data"""
        suppliers_data = [
            {"name": "China Main Electronics", "country": "China", "lead_time": 14, "reliability": 0.85, "primary": True},
            {"name": "India Textiles Co", "country": "India", "lead_time": 10, "reliability": 0.92, "primary": True},
            {"name": "USA Local Supply", "country": "USA", "lead_time": 3, "reliability": 0.98, "primary": False},
            {"name": "Vietnam Manufacturing", "country": "Vietnam", "lead_time": 12, "reliability": 0.88, "primary": False},
            {"name": "Bangladesh Apparel", "country": "Bangladesh", "lead_time": 16, "reliability": 0.82, "primary": False},
            {"name": "Mexico Backup", "country": "Mexico", "lead_time": 7, "reliability": 0.90, "primary": False},
            {"name": "Germany Premium", "country": "Germany", "lead_time": 8, "reliability": 0.96, "primary": False},
            {"name": "Taiwan Tech", "country": "Taiwan", "lead_time": 11, "reliability": 0.89, "primary": False}
        ]
        
        suppliers = []
        for data in suppliers_data:
            supplier = {
                "supplier_id": str(uuid.uuid4()),
                "name": data["name"],
                "country": data["country"],
                "lead_time_days": data["lead_time"],
                "reliability_score": data["reliability"],
                "is_primary": data["primary"]
            }
            suppliers.append(supplier)
            
        return pd.DataFrame(suppliers)
    
    def generate_products(self, suppliers_df: pd.DataFrame, scenario_config: ScenarioConfig) -> pd.DataFrame:
        """Generate product catalog"""
        categories = {
            "electronics": ["smartphones", "laptops", "headphones", "tablets", "smart_watches"],
            "clothing": ["shirts", "pants", "dresses", "shoes", "accessories"],
            "home": ["furniture", "kitchen", "decor", "garden", "storage"],
            "beauty": ["skincare", "makeup", "haircare", "fragrances", "tools"],
            "books": ["fiction", "non_fiction", "textbooks", "children", "technical"]
        }
        
        seasonal_patterns = {
            "electronics": "holiday",
            "clothing": "none", 
            "home": "summer",
            "beauty": "none",
            "books": "back_to_school"
        }
        
        products = []
        supplier_ids = suppliers_df["supplier_id"].tolist()
        
        # Category distribution based on scenario
        focus_category = scenario_config.special_params.get("category", None) if scenario_config.special_params else None
        product_count = scenario_config.special_params.get("product_count", 2500) if scenario_config.special_params else 2500
        
        for i in range(product_count):
            if focus_category and random.random() < 0.6:
                category = focus_category
            else:
                category = np.random.choice(list(categories.keys()), 
                                         p=[0.25, 0.25, 0.2, 0.15, 0.15])
            
            subcategory = np.random.choice(categories[category])
            
            # Price distribution (log-normal)
            if category == "electronics":
                base_price = np.random.lognormal(5.5, 0.8)  # $200-$2000
            elif category == "clothing":
                base_price = np.random.lognormal(3.5, 0.6)  # $20-$200
            else:
                base_price = np.random.lognormal(4.0, 0.7)  # $50-$500
                
            cost = base_price * np.random.uniform(0.3, 0.7)  # 30-70% margin
            
            product = {
                "product_id": str(uuid.uuid4()),
                "sku": f"{category[:2].upper()}{i:06d}",
                "name": f"{subcategory.title()} {fake.color_name()} {fake.word().title()}",
                "category": category,
                "subcategory": subcategory,
                "brand": fake.company(),
                "price": round(base_price, 2),
                "cost": round(cost, 2),
                "weight": np.random.exponential(2.0),  # kg
                "is_seasonal": seasonal_patterns[category] != "none",
                "seasonality_pattern": seasonal_patterns[category],
                "supplier_id": np.random.choice(supplier_ids)
            }
            products.append(product)
            
        return pd.DataFrame(products)
    
    def generate_campaigns(self, scenario_config: ScenarioConfig) -> pd.DataFrame:
        """Generate marketing campaigns"""
        campaigns = []
        
        if scenario_config.name == "flash_sale":
            campaign = {
                "campaign_id": str(uuid.uuid4()),
                "name": f"Flash Sale {scenario_config.special_params.get('category', 'All') if scenario_config.special_params else 'All'} {scenario_config.special_params.get('discount', 50) if scenario_config.special_params else 50}% Off",
                "campaign_type": "flash_sale",
                "start_ts": self.timestamp_start,
                "end_ts": self.timestamp_start + self._parse_duration(scenario_config.duration),
                "discount_percent": (scenario_config.special_params.get("discount", 50) if scenario_config.special_params else 50) / 100,
                "target_categories": [scenario_config.special_params.get("category", "electronics") if scenario_config.special_params else "electronics"],
                "intensity_multiplier": scenario_config.intensity_multiplier
            }
            campaigns.append(campaign)
            
        elif scenario_config.name == "viral_moment":
            campaign = {
                "campaign_id": str(uuid.uuid4()),
                "name": f"Viral {scenario_config.special_params.get('platform', 'TikTok') if scenario_config.special_params else 'TikTok'} Campaign",
                "campaign_type": "influencer",
                "start_ts": self.timestamp_start,
                "end_ts": self.timestamp_start + timedelta(hours=24),
                "discount_percent": 0.0,
                "target_categories": ["beauty"],
                "intensity_multiplier": scenario_config.intensity_multiplier
            }
            campaigns.append(campaign)
            
        elif scenario_config.name == "seasonal_planning":
            season = scenario_config.special_params.get("season", "back_to_school") if scenario_config.special_params else "back_to_school"
            campaign = {
                "campaign_id": str(uuid.uuid4()),
                "name": f"{season.replace('_', ' ').title()} 2024",
                "campaign_type": "seasonal",
                "start_ts": self.timestamp_start,
                "end_ts": self.timestamp_start + self._parse_duration(scenario_config.duration),
                "discount_percent": 0.15,  # 15% seasonal discount
                "target_categories": ["electronics", "clothing", "books"],
                "intensity_multiplier": scenario_config.intensity_multiplier
            }
            campaigns.append(campaign)
            
        return pd.DataFrame(campaigns) if campaigns else pd.DataFrame()
    
    def generate_orders(self, customers_df: pd.DataFrame, products_df: pd.DataFrame, 
                       campaigns_df: pd.DataFrame, scenario_config: ScenarioConfig) -> pd.DataFrame:
        """Generate order data with realistic patterns"""
        
        duration_hours = self._parse_duration_hours(scenario_config.duration)
        base_orders_per_hour = scenario_config.special_params.get("orders_per_hour", 800) if scenario_config.special_params else 800
        
        orders = []
        order_items = []
        
        # Time-based order generation
        current_time = self.timestamp_start
        hour_delta = timedelta(hours=1)
        
        for hour in range(int(duration_hours)):
            # Apply intensity multiplier and time-of-day patterns
            hour_multiplier = self._get_hourly_multiplier(hour, scenario_config)
            orders_this_hour = int(base_orders_per_hour * scenario_config.intensity_multiplier * hour_multiplier)
            
            # Special scenario adjustments
            if scenario_config.name == "payment_outage" and 1 <= hour <= 3:
                print(f"  ⚠️  Payment outage detected - reducing orders by 80% for hour {hour}")
                orders_this_hour = int(orders_this_hour * 0.2)  # 80% drop during outage
    
            elif scenario_config.name == "viral_moment":
                if hour <= 6:
                    viral_curve = math.exp(hour) / math.exp(6)  # Exponential growth
                    print(f"  🚀 Viral growth phase - applying {viral_curve:.2f}x multiplier for hour {hour}")
                    orders_this_hour = int(orders_this_hour * viral_curve)
                    
            for _ in range(orders_this_hour):
                order_time = current_time + timedelta(minutes=random.randint(0, 59))
                
                # Select customer based on scenario
                customer = customers_df.sample(1).iloc[0]
                
                # Channel selection based on customer cohort
                if customer["cohort"] == "gen_z":
                    channel = np.random.choice(["mobile_app", "mobile_web", "web"], p=[0.5, 0.3, 0.2])
                elif customer["cohort"] == "boomer":
                    channel = np.random.choice(["web", "mobile_web"], p=[0.7, 0.3])
                else:
                    channel = np.random.choice(["web", "mobile_web", "mobile_app"], p=[0.4, 0.35, 0.25])
                
                # Payment type based on cohort
                if customer["cohort"] == "gen_z":
                    payment_type = np.random.choice(["card", "bnpl", "upi"], p=[0.4, 0.4, 0.2])
                else:
                    payment_type = np.random.choice(["card", "upi", "cod"], p=[0.6, 0.25, 0.15])
                
                # Payment status - failures during outages
                if scenario_config.name == "payment_outage" and 1 <= hour <= 3:
                    payment_status = np.random.choice(["failed", "success"], p=[0.7, 0.3])
                    payment_failure_reason = "gateway_down" if payment_status == "failed" else None
                else:
                    payment_status = np.random.choice(["success", "failed"], p=[0.95, 0.05])
                    # Fix: Use random.choices() instead of np.random.choice() to handle None values
                    payment_failure_reason = random.choices(["insufficient_funds", "expired_card", None], weights=[0.1, 0.1, 0.8], k=1)[0]
                
                # Product selection
                if not campaigns_df.empty:
                    campaign = campaigns_df.iloc[0]
                    if campaign["target_categories"]:
                        category_products = products_df[products_df["category"].isin(campaign["target_categories"])]
                        if not category_products.empty:
                            product = category_products.sample(1).iloc[0]
                        else:
                            product = products_df.sample(1).iloc[0]
                    else:
                        product = products_df.sample(1).iloc[0]
                    campaign_id = campaign["campaign_id"]
                else:
                    product = products_df.sample(1).iloc[0]
                    campaign_id = None
                
                # Calculate pricing
                quantity = np.random.choice([1, 2, 3, 4], p=[0.6, 0.25, 0.1, 0.05])
                unit_price = product["price"]
                
                # Apply campaign discount
                discount_per_unit = 0.0
                if campaign_id and not campaigns_df.empty:
                    campaign = campaigns_df[campaigns_df["campaign_id"] == campaign_id].iloc[0]
                    discount_per_unit = unit_price * campaign["discount_percent"]
                    
                subtotal = quantity * unit_price
                total_discount = quantity * discount_per_unit
                tax = (subtotal - total_discount) * 0.08  # 8% tax
                shipping_cost = 5.99 if subtotal < 50 else 0  # Free shipping over $50
                total_amount = subtotal - total_discount + tax + shipping_cost
                
                # Delivery estimates
                expected_delivery = order_time + timedelta(days=random.randint(1, 3))
                
                # SLA breach calculation (more likely during high intensity)
                sla_breach_prob = 0.05 * scenario_config.intensity_multiplier
                if random.random() < sla_breach_prob:
                    delivery_delay_hours = random.randint(12, 72)
                    actual_delivery = expected_delivery + timedelta(hours=delivery_delay_hours)
                    is_sla_breach = True
                else:
                    delivery_delay_hours = 0
                    actual_delivery = expected_delivery + timedelta(hours=random.randint(-6, 6))
                    is_sla_breach = False
                
                # Order status progression
                if payment_status == "failed":
                    order_status = "cancelled"
                    actual_delivery = None
                else:
                    statuses = ["delivered", "shipped", "processing", "cancelled"]
                    order_status = np.random.choice(statuses, p=[0.85, 0.1, 0.03, 0.02])
                    
                    if order_status != "delivered":
                        actual_delivery = None
                        is_sla_breach = False
                        delivery_delay_hours = 0
                
                order = {
                    "order_id": str(uuid.uuid4()),
                    "customer_id": customer["customer_id"],
                    "campaign_id": campaign_id,
                    "order_ts": order_time,
                    "channel": channel,
                    "session_id": str(uuid.uuid4()),
                    "payment_type": payment_type,
                    "payment_status": payment_status,
                    "payment_failure_reason": payment_failure_reason,
                    "order_status": order_status,
                    "subtotal": round(subtotal, 2),
                    "discount": round(total_discount, 2),
                    "tax": round(tax, 2),
                    "shipping_cost": shipping_cost,
                    "total_amount": round(total_amount, 2),
                    "warehouse_id": f"WH_{random.randint(1, 5):02d}",
                    "expected_delivery_ts": expected_delivery,
                    "actual_delivery_ts": actual_delivery,
                    "is_sla_breach": is_sla_breach,
                    "delivery_delay_hours": delivery_delay_hours
                }
                orders.append(order)
                
                # Create order items
                order_item = {
                    "order_item_id": str(uuid.uuid4()),
                    "order_id": order["order_id"],
                    "product_id": product["product_id"],
                    "sku": product["sku"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_per_unit": discount_per_unit,
                    "total_price": round((unit_price - discount_per_unit) * quantity, 2)
                }
                order_items.append(order_item)
                
            current_time += hour_delta
            
        self.data["order_items"] = pd.DataFrame(order_items)
        return pd.DataFrame(orders)
    
    def generate_support_tickets(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame,
                                scenario_config: ScenarioConfig) -> pd.DataFrame:
        """Generate support tickets with realistic correlations"""
        
        # Calculate expected ticket volume based on orders (correlation = 0.85)
        total_orders = len(orders_df)
        base_ticket_rate = 0.12  # 12% of orders generate tickets
        correlation_multiplier = scenario_config.intensity_multiplier * 0.85  # Strong correlation
        
        expected_tickets = int(total_orders * base_ticket_rate * correlation_multiplier)
        
        # Special scenario adjustments
        if scenario_config.name == "returns_wave":
            print("  📞 Returns wave scenario - increasing support tickets by 2.5x")
            expected_tickets = int(expected_tickets * 2.5)  # Return-heavy support load
        elif scenario_config.name == "payment_outage":
            print("  💳 Payment outage scenario - increasing support tickets by 3.0x")
            expected_tickets = int(expected_tickets * 3.0)  # Payment issues spike
        elif scenario_config.name == "viral_moment":
            print("  📈 Viral moment scenario - increasing support tickets by 2.0x")
            expected_tickets = int(expected_tickets * 2.0)  # "Restock" inquiries
        
        tickets = []
        
        # Focus on SLA-breached orders (correlation = 0.91 with delivery delays)
        sla_breached_orders = orders_df[orders_df["is_sla_breach"] == True]
        
        # Generate tickets for SLA breaches (90% chance)
        for _, order in sla_breached_orders.iterrows():
            if random.random() < 0.9:
                customer = customers_df[customers_df["customer_id"] == order["customer_id"]].iloc[0]
                
                # Channel preference by cohort
                if customer["cohort"] == "gen_z":
                    channel = np.random.choice(["chat", "whatsapp", "social_media"], p=[0.5, 0.3, 0.2])
                elif customer["cohort"] == "boomer":
                    channel = np.random.choice(["phone", "email"], p=[0.7, 0.3])
                else:
                    channel = np.random.choice(["email", "chat", "phone"], p=[0.4, 0.4, 0.2])
                
                # Ticket timing (2-3 days after expected delivery)
                if order["expected_delivery_ts"]:
                    ticket_time = order["expected_delivery_ts"] + timedelta(days=random.randint(1, 3))
                else:
                    ticket_time = order["order_ts"] + timedelta(days=random.randint(1, 7))
                
                ticket = self._create_support_ticket(
                    customer, order, channel, ticket_time, 
                    issue_category="delivery", severity="medium",
                    scenario_config=scenario_config
                )
                tickets.append(ticket)
        
        # Generate remaining tickets for various reasons
        remaining_tickets = expected_tickets - len(tickets)
        
        for _ in range(max(0, remaining_tickets)):
            # Random customer and order
            customer = customers_df.sample(1).iloc[0]
            
            # 70% of tickets are order-related
            if random.random() < 0.7 and not orders_df.empty:
                customer_orders = orders_df[orders_df["customer_id"] == customer["customer_id"]]
                if not customer_orders.empty:
                    order = customer_orders.sample(1).iloc[0]
                else:
                    order = None
            else:
                order = None
            
            # Issue category based on scenario
            if scenario_config.name == "returns_wave":
                issue_category = np.random.choice(["refund", "product", "other"], p=[0.6, 0.3, 0.1])
            elif scenario_config.name == "payment_outage":
                issue_category = np.random.choice(["payment", "technical", "other"], p=[0.7, 0.2, 0.1])
            else:
                issue_category = np.random.choice(
                    ["delivery", "product", "refund", "payment", "technical", "other"],
                    p=[0.3, 0.2, 0.15, 0.15, 0.1, 0.1]
                )
            
            # Channel preference
            if customer["cohort"] == "gen_z":
                channel = np.random.choice(["chat", "whatsapp", "email"], p=[0.4, 0.4, 0.2])
            else:
                channel = np.random.choice(["email", "phone", "chat"], p=[0.5, 0.3, 0.2])
            
            # Random timing within scenario duration
            ticket_time = self.timestamp_start + timedelta(
                hours=random.randint(0, int(self._parse_duration_hours(scenario_config.duration)))
            )
            
            ticket = self._create_support_ticket(
                customer, order, channel, ticket_time, 
                issue_category=issue_category,
                severity=np.random.choice(["low", "medium", "high"], p=[0.6, 0.3, 0.1]),
                scenario_config=scenario_config
            )
            tickets.append(ticket)
        
        return pd.DataFrame(tickets)
    
    def _create_support_ticket(self, customer, order, channel, ticket_time, 
                              issue_category, severity, scenario_config) -> dict:
        """Create individual support ticket"""
        
        # SLA targets by severity
        sla_targets = {"low": 24, "medium": 8, "high": 2, "critical": 1}  # hours
        sla_target = sla_targets[severity]
        
        # Resolution time (higher during high load scenarios)
        load_multiplier = min(scenario_config.intensity_multiplier, 3.0)
        base_resolution_time = sla_target * 0.7  # Normally resolve within SLA
        actual_resolution_time = base_resolution_time * load_multiplier * np.random.lognormal(0, 0.5)
        
        sla_breach = actual_resolution_time > sla_target
        sla_breach_hours = max(0, int(actual_resolution_time - sla_target))
        
        # First response time
        first_response_time = actual_resolution_time * 0.1  # 10% of total time for first response
        first_response_ts = ticket_time + timedelta(hours=first_response_time)
        
        # Resolution timestamp
        if random.random() < 0.85:  # 85% get resolved
            resolved_ts = ticket_time + timedelta(hours=actual_resolution_time)
        else:
            resolved_ts = None
            sla_breach = True
        
        # Agent assignment (more automation in scenarios with high load)
        if scenario_config.intensity_multiplier > 2.0:
            agent_type = np.random.choice(["chatbot", "human"], p=[0.6, 0.4])
        else:
            agent_type = np.random.choice(["human", "chatbot"], p=[0.7, 0.3])
        
        # CSAT score (lower during high load)
        if sla_breach:
            csat = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
        else:
            csat = np.random.choice([3, 4, 5], p=[0.2, 0.3, 0.5])
        
        # Issue subcategory
        subcategories = {
            "delivery": ["delayed_delivery", "missing_package", "damaged_in_shipping", "wrong_address"],
            "product": ["defective", "wrong_item", "not_as_described", "quality_issue"],
            "refund": ["refund_delay", "refund_amount", "return_process", "exchange"],
            "payment": ["payment_failed", "double_charge", "refund_issue", "billing"],
            "technical": ["app_crash", "website_slow", "login_issue", "checkout_error"],
            "other": ["general_inquiry", "account_help", "policy_question", "complaint"]
        }
        
        subcategory = np.random.choice(subcategories.get(issue_category, ["other"]))
        
        return {
            "ticket_id": str(uuid.uuid4()),
            "customer_id": customer["customer_id"],
            "order_id": order["order_id"] if order is not None else None,
            "channel": channel,
            "language": "en",  # Simplified for now
            "issue_category": issue_category,
            "issue_subcategory": subcategory,
            "severity": severity,
            "created_ts": ticket_time,
            "first_response_ts": first_response_ts,
            "resolved_ts": resolved_ts,
            "sla_breach": sla_breach,
            "sla_breach_hours": sla_breach_hours,
            "csat": csat if resolved_ts else None,
            "agent_id": f"AGENT_{random.randint(1, 50):03d}",
            "agent_type": agent_type,
            "escalation_count": random.randint(0, 2) if severity in ["high", "critical"] else 0,
            "resolution_time_minutes": int(actual_resolution_time * 60) if resolved_ts else None
        }
    
    def generate_cart_abandonment(self, customers_df: pd.DataFrame, products_df: pd.DataFrame,
                                 orders_df: pd.DataFrame, scenario_config: ScenarioConfig) -> pd.DataFrame:
        """Generate cart abandonment data with negative correlation to orders"""
        
        # Base abandonment rate
        base_abandonment_rate = 0.25  # 25% normal abandonment
        
        # Apply negative correlation with order intensity (correlation = -0.43)
        correlation_effect = 1 - (scenario_config.intensity_multiplier - 1) * 0.43
        adjusted_rate = base_abandonment_rate * max(0.05, correlation_effect)  # Don't go below 5%
        
        # Calculate abandonment volume based on total traffic
        total_orders = len(orders_df)
        estimated_sessions = int(total_orders / (1 - adjusted_rate))  # Reverse engineer session count
        abandonment_count = int(estimated_sessions * adjusted_rate)
        
        # Special scenario adjustments
        if scenario_config.name == "payment_outage":
            print("  🛒 Payment outage scenario - increasing cart abandonment by 3.5x")
            abandonment_count = int(abandonment_count * 3.5)  # Massive spike during outage
        elif scenario_config.name == "flash_sale":
            print("  ⏰ Flash sale scenario - reducing cart abandonment by 60% (FOMO effect)")
            abandonment_count = int(abandonment_count * 0.4)  # FOMO reduces abandonment
        
        abandonments = []
        
        for _ in range(abandonment_count):
            # Random customer (can be anonymous)
            if random.random() < 0.6:  # 60% have customer accounts
                customer = customers_df.sample(1).iloc[0]
                customer_id = customer["customer_id"]
                cohort = customer["cohort"]
            else:
                customer_id = None
                cohort = np.random.choice(["gen_z", "millennial", "gen_x", "boomer"])
            
            # Channel selection
            if cohort == "gen_z":
                channel = np.random.choice(["mobile_app", "mobile_web"], p=[0.6, 0.4])
            else:
                channel = np.random.choice(["web", "mobile_web", "mobile_app"], p=[0.5, 0.3, 0.2])
            
            # Abandonment stage
            if scenario_config.name == "payment_outage":
                abandon_stage = np.random.choice(["payment", "checkout", "cart"], p=[0.7, 0.2, 0.1])
                abandon_reason = "payment_failed" if abandon_stage == "payment" else "technical_issue"
            else:
                abandon_stage = np.random.choice(["cart", "checkout", "payment"], p=[0.5, 0.3, 0.2])
                abandon_reasons = ["high_shipping", "price_shopping", "no_payment_method", "slow_site", "other"]
                abandon_reason = np.random.choice(abandon_reasons)
            
            # Cart composition
            items_count = np.random.choice([1, 2, 3, 4, 5], p=[0.4, 0.25, 0.15, 0.12, 0.08])
            cart_products = products_df.sample(items_count)
            cart_value = sum(p["price"] * random.randint(1, 2) for _, p in cart_products.iterrows())
            
            # Timing within scenario
            abandon_time = self.timestamp_start + timedelta(
                hours=random.uniform(0, self._parse_duration_hours(scenario_config.duration))
            )
            
            abandonment = {
                "abandonment_id": str(uuid.uuid4()),
                "session_id": str(uuid.uuid4()),
                "customer_id": customer_id,
                "abandon_ts": abandon_time,
                "cart_value": round(cart_value, 2),
                "items_count": items_count,
                "abandon_stage": abandon_stage,
                "abandon_reason": abandon_reason,
                "channel": channel
            }
            abandonments.append(abandonment)
        
        return pd.DataFrame(abandonments)
    
    def generate_returns(self, orders_df: pd.DataFrame, customers_df: pd.DataFrame,
                        products_df: pd.DataFrame, scenario_config: ScenarioConfig) -> pd.DataFrame:
        """Generate returns data (especially for post-holiday scenarios)"""
        
        if scenario_config.name != "returns_wave":
            # Normal return rate
            return_rate = 0.08  # 8% normal return rate
        else:
            # Post-holiday spike
            return_rate = (scenario_config.special_params.get("return_rate_multiplier", 3.0) if scenario_config.special_params else 3.0) * 0.08
        
        delivered_orders = orders_df[orders_df["order_status"] == "delivered"].copy()
        if delivered_orders.empty:
            return pd.DataFrame()
        
        returns_count = int(len(delivered_orders) * return_rate)
        
        returns = []
        return_orders = delivered_orders.sample(min(returns_count, len(delivered_orders)))
        
        for _, order in return_orders.iterrows():
            customer = customers_df[customers_df["customer_id"] == order["customer_id"]].iloc[0]
            
            # Return timing (1-14 days after delivery)
            if order["actual_delivery_ts"]:
                return_time = order["actual_delivery_ts"] + timedelta(days=random.randint(1, 14))
            else:
                return_time = order["order_ts"] + timedelta(days=random.randint(3, 21))
            
            # Return reason based on scenario and product category
            order_items = self.data["order_items"][self.data["order_items"]["order_id"] == order["order_id"]]
            
            for _, item in order_items.iterrows():
                product = products_df[products_df["product_id"] == item["product_id"]].iloc[0]
                
                # Category-specific return reasons
                if product["category"] == "clothing":
                    return_reason = np.random.choice(
                        ["wrong_size", "not_as_described", "changed_mind", "defective"],
                        p=[0.4, 0.3, 0.2, 0.1]
                    )
                elif product["category"] == "electronics":
                    return_reason = np.random.choice(
                        ["defective", "not_as_described", "changed_mind"],
                        p=[0.5, 0.3, 0.2]
                    )
                else:
                    return_reason = np.random.choice(
                        ["not_as_described", "defective", "changed_mind", "damaged_in_shipping"],
                        p=[0.3, 0.3, 0.25, 0.15]
                    )
                
                # Processing time (longer during high volume)
                base_processing_days = 3
                if scenario_config.name == "returns_wave":
                    processing_days = base_processing_days + random.randint(2, 10)  # Delays during spike
                else:
                    processing_days = base_processing_days + random.randint(0, 4)
                
                processed_time = return_time + timedelta(days=processing_days)
                
                # Return status
                if random.random() < 0.9:  # 90% get processed
                    return_status = np.random.choice(["processed", "refunded"], p=[0.3, 0.7])
                else:
                    return_status = np.random.choice(["approved", "requested"])
                
                refund_amount = item["total_price"] * 0.95  # 5% restocking fee sometimes
                
                return_record = {
                    "return_id": str(uuid.uuid4()),
                    "order_id": order["order_id"],
                    "customer_id": customer["customer_id"],
                    "product_id": product["product_id"],
                    "return_reason": return_reason,
                    "return_ts": return_time,
                    "processed_ts": processed_time if return_status in ["processed", "refunded"] else None,
                    "refund_amount": round(refund_amount, 2),
                    "return_status": return_status,
                    "processing_days": processing_days
                }
                returns.append(return_record)
        
        return pd.DataFrame(returns)
    
    def generate_system_metrics(self, scenario_config: ScenarioConfig) -> pd.DataFrame:
        """Generate system performance metrics"""
        metrics = []
        duration_hours = int(self._parse_duration_hours(scenario_config.duration))
        
        metric_names = [
            "orders_per_hour", "support_tickets_per_hour", "payment_failure_rate",
            "site_load_time", "inventory_turnover", "cart_abandonment_rate"
        ]
        
        current_time = self.timestamp_start
        
        for hour in range(duration_hours):
            for metric_name in metric_names:
                # Base values
                if metric_name == "orders_per_hour":
                    base_value = 800
                    value = base_value * scenario_config.intensity_multiplier * self._get_hourly_multiplier(hour, scenario_config)
                elif metric_name == "support_tickets_per_hour":
                    base_value = 100
                    value = base_value * scenario_config.intensity_multiplier * 0.85  # Correlated with orders
                elif metric_name == "payment_failure_rate":
                    if scenario_config.name == "payment_outage" and 1 <= hour <= 3:
                        value = 0.75  # 75% failure during outage
                    else:
                        value = 0.05  # 5% normal failure rate
                elif metric_name == "site_load_time":
                    base_value = 2.5  # seconds
                    load_factor = min(scenario_config.intensity_multiplier, 5.0)
                    value = base_value * load_factor
                elif metric_name == "cart_abandonment_rate":
                    base_value = 0.25
                    correlation_effect = 1 - (scenario_config.intensity_multiplier - 1) * 0.43
                    value = base_value * max(0.05, correlation_effect)
                else:  # inventory_turnover
                    value = random.uniform(2.0, 8.0)
                
                metric = {
                    "metric_id": str(uuid.uuid4()),
                    "timestamp": current_time,
                    "metric_name": metric_name,
                    "metric_value": round(value, 3),
                    "campaign_id": None  # Could link to campaigns if needed
                }
                metrics.append(metric)
            
            current_time += timedelta(hours=1)
        
        return pd.DataFrame(metrics)
    
    def _get_hourly_multiplier(self, hour: int, scenario_config: ScenarioConfig) -> float:
        """Get time-of-day traffic multiplier"""
        # Basic diurnal pattern
        base_pattern = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(2 * math.pi * (hour - 6) / 24))
        
        # Scenario-specific patterns
        if scenario_config.name == "flash_sale":
            # Exponential spike in first few hours
            if hour < 4:
                return base_pattern * (2.0 ** hour)
            else:
                return base_pattern * 0.5  # Decay after spike
        elif scenario_config.name == "viral_moment":
            # Viral explosion pattern
            if hour < 8:
                return base_pattern * math.exp(hour / 3)
            else:
                return base_pattern
        else:
            return base_pattern
    
    def _parse_duration(self, duration_str: str) -> timedelta:
        """Parse duration string like '4h', '14d', '30m'"""
        if duration_str.endswith('h'):
            return timedelta(hours=int(duration_str[:-1]))
        elif duration_str.endswith('d'):
            return timedelta(days=int(duration_str[:-1]))
        elif duration_str.endswith('m'):
            if 'm' == duration_str[-1]:  # months
                return timedelta(days=int(duration_str[:-1]) * 30)
            else:  # minutes
                return timedelta(minutes=int(duration_str[:-1]))
        else:
            return timedelta(hours=24)  # Default to 1 day
    
    def _parse_duration_hours(self, duration_str: str) -> float:
        """Parse duration string and return total hours"""
        delta = self._parse_duration(duration_str)
        return delta.total_seconds() / 3600
    
    def save_data(self, tables: List[str], scenario_name: str):
        """Save generated data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print("💾 Saving files:")
        print(f"  📁 Output directory: {self.output_dir}")
        saved_files = []
        
        for table in tables:
            if table in self.data and not self.data[table].empty:
                filename = f"{scenario_name}_{timestamp}_{table}.{self.output_format}"
                filepath = self.output_dir / filename
                
                if self.output_format == "csv":
                    self.data[table].to_csv(filepath, index=False)
                elif self.output_format == "parquet":
                    self.data[table].to_parquet(filepath, index=False)
                
                print(f"  ✅ {table}: {len(self.data[table])} records → {filename}")
                saved_files.append(filename)
            elif table in self.data:
                print(f"  ⚠️  {table}: Empty dataset, skipping")
            else:
                print(f"  ❌ {table}: Not generated")
        
        print(f"  ✅ All files saved successfully!")
        return saved_files
    
    def print_summary(self, scenario_config: ScenarioConfig, saved_files: List[str]):
        """Print generation summary with key insights"""
        print()
        print("📈 Key Metrics & Correlations Applied:")
        
        # Calculate actual correlations from generated data
        if "orders" in self.data and "support_tickets" in self.data:
            if not self.data["orders"].empty and not self.data["support_tickets"].empty:
                orders_count = len(self.data["orders"])
                tickets_count = len(self.data["support_tickets"])
                correlation = tickets_count / orders_count if orders_count > 0 else 0
                print(f"  - Orders ↔ Support: {correlation:.2f} correlation ({tickets_count} tickets from {orders_count} orders)")
        
        if "cart_abandonment" in self.data and not self.data["cart_abandonment"].empty:
            abandon_count = len(self.data["cart_abandonment"])
            orders_count = len(self.data["orders"]) if "orders" in self.data else 0
            if orders_count > 0:
                abandon_rate = abandon_count / (abandon_count + orders_count)
                print(f"  - Cart Abandonment Rate: {abandon_rate:.1%}")
        
        # Scenario-specific insights
        if scenario_config.name == "flash_sale":
            if "system_metrics" in self.data:
                payment_failures = self.data["system_metrics"]
                payment_failures = payment_failures[payment_failures["metric_name"] == "payment_failure_rate"]
                if not payment_failures.empty:
                    avg_failure_rate = payment_failures["metric_value"].mean()
                    print(f"  - Payment gateway stress: {avg_failure_rate:.1%} average failure rate")
        
        elif scenario_config.name == "returns_wave":
            if "returns" in self.data:
                returns_count = len(self.data["returns"])
                avg_processing = self.data["returns"]["processing_days"].mean() if returns_count > 0 else 0
                print(f"  - Return processing delays: +{avg_processing:.1f} days average")
        
        print()
        print(f"🎯 Scenario Complete: {scenario_config.name.replace('_', ' ').title()} data ready!")
        print(f"📁 {len(saved_files)} files saved to {self.output_dir}/")

def create_scenario_configs():
    """Define all supported scenarios"""
    scenarios = {
        "flash_sale": ScenarioConfig(
            name="flash_sale",
            duration="4h",
            intensity_multiplier=8.5,
            special_params={
                "discount": 70,
                "category": "electronics",
                "orders_per_hour": 1000
            }
        ),
        
        "returns_wave": ScenarioConfig(
            name="returns_wave",
            duration="14d",
            intensity_multiplier=1.2,
            special_params={
                "return_rate_multiplier": 3.0,
                "categories": ["electronics", "clothing"]
            }
        ),
        
        "supply_disruption": ScenarioConfig(
            name="supply_disruption",
            duration="14d",
            intensity_multiplier=0.8,
            special_params={
                "supplier": "china_main",
                "affected_skus": 35,
                "backup_capacity": 60
            }
        ),
        
        "payment_outage": ScenarioConfig(
            name="payment_outage", 
            duration="6h",
            intensity_multiplier=1.5,
            special_params={
                "outage_duration": 2,
                "backup_capacity": 40,
                "peak_traffic": True
            }
        ),
        
        "viral_moment": ScenarioConfig(
            name="viral_moment",
            duration="24h", 
            intensity_multiplier=2.5,
            special_params={
                "product": "skincare_set",
                "inventory": 500,
                "platform": "tiktok",
                "viral_coefficient": 2.5
            }
        ),
        
        "customer_segments": ScenarioConfig(
            name="customer_segments",
            duration="180d",  # 6 months
            intensity_multiplier=1.0,
            special_params={
                "gen_z_growth": 15,
                "behavioral_shift": True
            }
        ),
        
        "seasonal_planning": ScenarioConfig(
            name="seasonal_planning",
            duration="60d",
            intensity_multiplier=1.8,
            special_params={
                "season": "back_to_school",
                "year": 2024,
                "regional_variation": True
            }
        ),
        
        "multi_channel": ScenarioConfig(
            name="multi_channel",
            duration="90d",
            intensity_multiplier=1.18,
            special_params={
                "new_channel": "mobile_app",
                "migration_rate": 35,
                "cannibalization": 15
            }
        ),
        
        "baseline": ScenarioConfig(
            name="baseline",
            duration="30d",
            intensity_multiplier=1.0,
            special_params={
                "orders_per_day": 2500,
                "customers": 10000
            }
        )
    }
    return scenarios

def main():
    parser = argparse.ArgumentParser(description="Synthetic E-Commerce Data Generation Agent")
    
    # Scenario selection
    scenarios = create_scenario_configs()
    parser.add_argument(
        "scenario", 
        choices=list(scenarios.keys()) + ["custom"],
        help="Business scenario to simulate"
    )
    
    # Output options
    parser.add_argument(
        "--output", 
        choices=["csv", "parquet"], 
        default="csv",
        help="Output format (default: csv)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Output directory (default: data)"
    )
    
    parser.add_argument(
        "--tables",
        default="all",
        help="Tables to generate: comma-separated list or 'all' (default: all)"
    )
    
    # Scenario customization options
    parser.add_argument("--discount", type=int, help="Discount percentage for sales")
    parser.add_argument("--duration", help="Scenario duration (e.g., 4h, 14d, 30m)")
    parser.add_argument("--intensity", type=float, help="Traffic intensity multiplier")
    parser.add_argument("--category", help="Target product category")
    parser.add_argument("--customers", type=int, help="Number of customers to generate")
    parser.add_argument("--orders-per-day", type=int, help="Orders per day for baseline")
    
    # Custom scenario
    parser.add_argument("--config", help="JSON config file for custom scenarios")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = SyntheticDataGenerator(
        output_dir=args.output_dir,
        output_format=args.output
    )
    
    # Load scenario configuration
    if args.scenario == "custom":
        if not args.config:
            print("❌ Custom scenario requires --config parameter")
            sys.exit(1)
        
        try:
            with open(args.config, 'r') as f:
                custom_config = json.load(f)
            scenario_config = ScenarioConfig(**custom_config)
        except Exception as e:
            print(f"❌ Error loading custom config: {e}")
            sys.exit(1)
    else:
        scenario_config = scenarios[args.scenario]
    
    # Apply command line overrides
    if args.discount:
        if scenario_config.special_params is None:
            scenario_config.special_params = {}
        scenario_config.special_params["discount"] = args.discount
    if args.duration:
        scenario_config.duration = args.duration
    if args.intensity:
        scenario_config.intensity_multiplier = args.intensity
    if args.category:
        if scenario_config.special_params is None:
            scenario_config.special_params = {}
        scenario_config.special_params["category"] = args.category
    if args.customers:
        if scenario_config.special_params is None:
            scenario_config.special_params = {}
        scenario_config.special_params["customers"] = args.customers
    if args.orders_per_day:
        if scenario_config.special_params is None:
            scenario_config.special_params = {}
        scenario_config.special_params["orders_per_day"] = args.orders_per_day
    
    # Determine tables to generate
    all_tables = [
        "customers", "suppliers", "products", "campaigns", "orders", "order_items",
        "support_tickets", "cart_abandonment", "returns", "system_metrics"
    ]
    
    if args.tables == "all":
        tables_to_generate = all_tables
    else:
        tables_to_generate = [t.strip() for t in args.tables.split(",")]
        invalid_tables = [t for t in tables_to_generate if t not in all_tables]
        if invalid_tables:
            print(f"❌ Invalid tables: {invalid_tables}")
            print(f"Available tables: {all_tables}")
            sys.exit(1)
    
    # Print header
    generator.print_header(scenario_config.name.replace("_", " ").title())
    
    print("Generating data...")
    print("📋 Generation Plan:")
    print(f"  - Scenario: {scenario_config.name.replace('_', ' ').title()}")
    print(f"  - Duration: {scenario_config.duration}")
    print(f"  - Intensity: {scenario_config.intensity_multiplier}x")
    print(f"  - Tables: {', '.join(tables_to_generate)}")
    print()
    
    # Generate data step by step
    try:
        # Core entities first
        if "customers" in tables_to_generate:
            print("👥 Generating customer data...")
            customer_count = scenario_config.special_params.get("customers", 15000) if scenario_config.special_params else 15000
            generator.data["customers"] = generator.generate_customers(customer_count, scenario_config)
            print(f"  ✅ Generated {len(generator.data['customers'])} customers")

        if "suppliers" in tables_to_generate:
            print("🏭 Generating supplier data...")
            generator.data["suppliers"] = generator.generate_suppliers()
            print(f"  ✅ Generated {len(generator.data['suppliers'])} suppliers")

        if "products" in tables_to_generate:
            print("📦 Generating product catalog...")
            suppliers_df = generator.data.get("suppliers", generator.generate_suppliers())
            generator.data["products"] = generator.generate_products(suppliers_df, scenario_config)
            print(f"  ✅ Generated {len(generator.data['products'])} products")

        if "campaigns" in tables_to_generate:
            print("🎯 Generating marketing campaigns...")
            generator.data["campaigns"] = generator.generate_campaigns(scenario_config)
            if not generator.data["campaigns"].empty:
                print(f"  ✅ Generated {len(generator.data['campaigns'])} campaigns")
            else:
                print("  ✅ No campaigns generated for this scenario")

        # Dependent entities
        if "orders" in tables_to_generate:
            print("🛒 Generating order data...")
            customers_df = generator.data.get("customers", generator.generate_customers(15000, scenario_config))
            products_df = generator.data.get("products", generator.generate_products(
                generator.data.get("suppliers", generator.generate_suppliers()), scenario_config
            ))
            campaigns_df = generator.data.get("campaigns", generator.generate_campaigns(scenario_config))

            generator.data["orders"] = generator.generate_orders(
                customers_df, products_df, campaigns_df, scenario_config
            )
            print(f"  ✅ Generated {len(generator.data['orders'])} orders")

        if "support_tickets" in tables_to_generate:
            print("💬 Generating support tickets...")
            customers_df = generator.data.get("customers")
            orders_df = generator.data.get("orders")
            if customers_df is not None and orders_df is not None:
                generator.data["support_tickets"] = generator.generate_support_tickets(
                    customers_df, orders_df, scenario_config
                )
                print(f"  ✅ Generated {len(generator.data['support_tickets'])} support tickets")
            else:
                print("  ⚠️  Skipping support tickets - missing customer/order data")

        if "cart_abandonment" in tables_to_generate:
            print("🛑 Generating cart abandonment data...")
            customers_df = generator.data.get("customers")
            products_df = generator.data.get("products")
            orders_df = generator.data.get("orders")
            if customers_df is not None and products_df is not None and orders_df is not None:
                generator.data["cart_abandonment"] = generator.generate_cart_abandonment(
                    customers_df, products_df, orders_df, scenario_config
                )
                print(f"  ✅ Generated {len(generator.data['cart_abandonment'])} abandoned carts")
            else:
                print("  ⚠️  Skipping cart abandonment - missing required data")

        if "returns" in tables_to_generate:
            print("🔄 Generating returns data...")
            orders_df = generator.data.get("orders")
            customers_df = generator.data.get("customers")
            products_df = generator.data.get("products")
            if orders_df is not None and customers_df is not None and products_df is not None:
                generator.data["returns"] = generator.generate_returns(
                    orders_df, customers_df, products_df, scenario_config
                )
                print(f"  ✅ Generated {len(generator.data['returns'])} returns")
            else:
                print("  ⚠️  Skipping returns - missing required data")

        if "system_metrics" in tables_to_generate:
            print("📊 Generating system metrics...")
            generator.data["system_metrics"] = generator.generate_system_metrics(scenario_config)
            print(f"  ✅ Generated {len(generator.data['system_metrics'])} metric records")
        
        # Save generated data
        saved_files = generator.save_data(tables_to_generate, args.scenario)
        
        # Print summary
        generator.print_summary(scenario_config, saved_files)
        
    except Exception as e:
        print(f"❌ Error during data generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()