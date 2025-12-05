# Synthetic E-Commerce Data Generation Agent Documentation

## Overview

The `generate.py` script is a comprehensive synthetic data generation tool designed to create realistic e-commerce datasets for testing, machine learning training, and business scenario simulation. It generates correlated data across multiple business domains with configurable scenarios.

## Core Functionality

### Main Components

1. **SyntheticDataGenerator Class**: The core engine that generates all data types
2. **ScenarioConfig Dataclass**: Configuration system for different business scenarios
3. **Data Generation Methods**: Specialized functions for each data entity type

### Supported Data Entities

The system generates 10 different data entity types:

1. **Customers**: Demographic and behavioral customer data
2. **Suppliers**: Supplier information with reliability metrics
3. **Products**: Comprehensive product catalog with pricing
4. **Campaigns**: Marketing campaign data
5. **Orders**: Order transactions with payment and fulfillment details
6. **Order Items**: Individual line items within orders
7. **Support Tickets**: Customer service interactions
8. **Cart Abandonment**: Abandoned shopping cart data
9. **Returns**: Product return and refund data
10. **System Metrics**: Performance metrics and KPIs

## Business Scenarios

The system supports 9 predefined business scenarios, each with unique characteristics:

### 1. Flash Sale Scenario
- **Duration**: 4 hours
- **Intensity**: 8.5x normal traffic
- **Key Features**:
  - 70% discount on electronics
  - Exponential traffic spike in first few hours
  - High payment gateway stress
  - Short-duration, high-intensity event

### 2. Returns Wave Scenario
- **Duration**: 14 days
- **Intensity**: 1.2x normal traffic
- **Key Features**:
  - 3x normal return rate (24% vs 8%)
  - Focus on electronics and clothing categories
  - Extended return processing times
  - Post-holiday return spike simulation

### 3. Supply Disruption Scenario
- **Duration**: 14 days
- **Intensity**: 0.8x normal traffic (reduced)
- **Key Features**:
  - Simulates supplier reliability issues
  - 35 affected SKUs from primary supplier
  - 60% backup capacity utilization
  - Reduced order volume due to stock issues

### 4. Payment Outage Scenario
- **Duration**: 6 hours
- **Intensity**: 1.5x normal traffic
- **Key Features**:
  - 2-hour payment gateway outage
  - 80% order volume drop during outage
  - 75% payment failure rate during outage
  - 3.5x cart abandonment spike
  - 3x support ticket volume increase

### 5. Viral Moment Scenario
- **Duration**: 24 hours
- **Intensity**: 2.5x normal traffic
- **Key Features**:
  - TikTok-driven viral product (skincare set)
  - Exponential traffic growth pattern
  - 500 unit inventory constraint
  - 2x support ticket volume ("restock" inquiries)
  - Influencer marketing campaign

### 6. Customer Segments Scenario
- **Duration**: 180 days (6 months)
- **Intensity**: 1.0x normal traffic
- **Key Features**:
  - 15% Gen Z customer growth
  - Behavioral shifts across generations
  - Long-term demographic trends
  - Cohort-specific purchasing patterns

### 7. Seasonal Planning Scenario
- **Duration**: 60 days
- **Intensity**: 1.8x normal traffic
- **Key Features**:
  - Back-to-school season focus
  - 15% seasonal discount
  - Targets electronics, clothing, and books
  - Regional variation patterns
  - 60-day planning horizon

### 8. Multi-Channel Scenario
- **Duration**: 90 days
- **Intensity**: 1.18x normal traffic
- **Key Features**:
  - New mobile app channel introduction
  - 35% customer migration to new channel
  - 15% cannibalization of existing channels
  - Channel-specific behavior patterns

### 9. Baseline Scenario
- **Duration**: 30 days
- **Intensity**: 1.0x normal traffic
- **Key Features**:
  - 2,500 orders per day
  - 10,000 customer base
  - Normal operating conditions
  - Reference point for comparison

## Data Generation Process

### Entity Relationships and Correlations

The system implements sophisticated data correlations:

- **Orders ↔ Support Tickets**: 0.85 correlation
- **Support Tickets ↔ Delivery Delays**: 0.91 correlation
- **Orders ↔ Delivery Delays**: 0.72 correlation
- **Orders ↔ Cart Abandonment**: -0.43 correlation (negative)
- **Support Tickets ↔ Cart Abandonment**: -0.22 correlation (negative)
- **Delivery Delays ↔ Cart Abandonment**: -0.15 correlation (negative)

### Customer Cohort Behavior

The system models 4 generational cohorts with distinct behaviors:

1. **Gen Z (28%)**
   - Acquisition: 40% paid social, 35% influencer, 25% organic
   - Channels: 50% mobile app, 30% mobile web, 20% web
   - Payment: 40% card, 40% BNPL, 20% UPI
   - Support: 50% chat, 30% WhatsApp, 20% social media

2. **Millennials (35%)**
   - Acquisition: Balanced across channels
   - Channels: 40% web, 35% mobile web, 25% mobile app
   - Payment: 60% card, 25% UPI, 15% COD
   - Support: 40% email, 40% chat, 20% phone

3. **Gen X (25%)**
   - Mixed behavior between younger and older cohorts

4. **Boomers (12%)**
   - Acquisition: 50% direct, 30% organic, 20% referral
   - Channels: 70% web, 30% mobile web
   - Payment: 60% card, 25% UPI, 15% COD
   - Support: 70% phone, 30% email

## Technical Implementation

### Key Features

- **Probabilistic Data Generation**: Uses numpy and random libraries for realistic distributions
- **Temporal Patterns**: Implements diurnal patterns and scenario-specific time curves
- **Correlation Engine**: Maintains statistical relationships between data entities
- **Configurable Scenarios**: JSON-based configuration system for custom scenarios
- **Multiple Output Formats**: Supports CSV and Parquet formats
- **Comprehensive Logging**: Detailed generation summaries and metrics

### Data Quality Features

- **Realistic Distributions**: Log-normal pricing, exponential weights, beta distributions
- **Temporal Realism**: Time-based patterns, delivery estimates, SLA calculations
- **Behavioral Realism**: Cohort-specific behaviors, channel preferences, payment methods
- **Error Injection**: Realistic failure rates, delays, and exceptions
- **Correlation Maintenance**: Statistical relationships between business metrics

## Usage Examples

### Basic Usage
```bash
python generate.py flash_sale
python generate.py returns_wave --output parquet
```

### Custom Scenario
```bash
python generate.py custom --config custom_scenario.json
```

### Specific Tables
```bash
python generate.py baseline --tables customers,orders,returns
```

### Parameter Overrides
```bash
python generate.py flash_sale --discount 60 --duration 8h --intensity 10.0
```

## Output Structure

Generated files follow this naming convention:
```
{scenario_name}_{timestamp}_{table_name}.{format}
```

Example:
```
flash_sale_20241205_143022_orders.csv
returns_wave_20241205_143545_support_tickets.parquet
```

## Advanced Features

### Dynamic Intensity Scaling
- Traffic patterns scale with intensity_multiplier
- Support ticket volume correlates with order volume (0.85)
- System metrics reflect load conditions

### Scenario-Specific Logic
- Payment outage: Gateway failures and cart abandonment spikes
- Viral moments: Exponential growth curves and inventory constraints
- Returns waves: Extended processing times and reason distributions
- Flash sales: Time-limited discounts and traffic spikes

### Correlation Engine
- Maintains statistical relationships between business metrics
- Implements negative correlations (e.g., orders vs cart abandonment)
- Generates realistic business dynamics

## Integration Capabilities

The generated data can be used for:

- **Machine Learning**: Training models for demand forecasting, fraud detection, customer segmentation
- **Business Intelligence**: Dashboard development, KPI tracking, trend analysis
- **System Testing**: Load testing, failure scenario simulation, performance benchmarking
- **Process Optimization**: Supply chain analysis, customer service improvement, marketing effectiveness

## Technical Specifications

- **Language**: Python 3.8+
- **Dependencies**: numpy, pandas, faker, dataclasses
- **Output Formats**: CSV, Parquet
- **Data Volume**: Configurable from small test datasets to large-scale simulations
- **Reproducibility**: Fixed random seeds for consistent results

This documentation provides a comprehensive reference for understanding, using, and extending the synthetic data generation system.