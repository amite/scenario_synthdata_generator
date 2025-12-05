# Performance Optimization Plan for Synthetic Data Generator

## 🎯 Executive Summary

The current performance bottleneck analysis reveals that **151.39 seconds execution time for large datasets is primarily due to algorithmic inefficiencies, not file I/O or format choices**. This document outlines a comprehensive optimization strategy to achieve 50-80% performance improvements.

## 📊 Current Performance Profile

### Baseline Metrics (Large Dataset: 15K customers, 374K orders)
```text
Total Execution Time: 151.39 seconds
┣━ Order Generation: 145.93s (96.4% of total)
┣━ Data Generation: 150.37s (99.3% of total)
┗━ File I/O: 0.58s (0.4% of total)
```

**Key Insight**: The bottleneck is in the data generation algorithm, not file operations.

## 🔍 Root Cause Analysis

### Performance Breakdown
| Component | Time (s) | % of Total | Optimization Potential |
|-----------|----------|------------|-----------------------|
| Order Generation | 145.93 | 96.4% | High (50-80%) |
| Customer Generation | 4.14 | 2.7% | Medium (20-40%) |
| Product Generation | 0.37 | 0.2% | Low (5-10%) |
| File I/O | 0.58 | 0.4% | Low (10-20%) |
| Campaign Generation | 0.00 | 0.0% | Minimal |

### Bottleneck Identification
```python
# Current problematic pattern in generate_orders()
for hour in range(int(duration_hours)):  # 720 iterations
    orders_this_hour = calculate_orders(hour)  # ~1000 orders/hour
    for _ in range(orders_this_hour):  # ~720,000 iterations total
        # Individual order processing - EXTREMELY SLOW
        order = create_order_individually()  # 145.93s total
```

## 🚀 Optimization Strategy

### Phase 1: Quick Wins (20-30% Improvement)
**Goal**: Reduce execution time to 105-120 seconds

#### 1. Vectorized Order Generation
```python
# Replace row-by-row with vectorized operations
def generate_orders_vectorized(customers_df, products_df, scenario_config):
    duration_hours = self._parse_duration_hours(scenario_config.duration)
    total_orders = calculate_total_orders(scenario_config)

    # Vectorized approach
    order_data = {
        'order_ts': pd.date_range(
            start=self.timestamp_start,
            periods=total_orders,
            freq='1min'
        ),
        'customer_id': np.random.choice(
            customers_df['customer_id'],
            total_orders,
            p=get_customer_weights(customers_df)
        ),
        'product_id': np.random.choice(
            products_df['product_id'],
            total_orders
        ),
        # ... other vectorized fields
    }

    return pd.DataFrame(order_data)
```

#### 2. Batch Processing
```python
BATCH_SIZE = 10000  # Process 10K orders at once

def generate_orders_batched(customers_df, products_df, scenario_config):
    orders = []
    total_orders = calculate_total_orders(scenario_config)

    for batch_start in range(0, total_orders, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total_orders)
        batch_orders = generate_order_batch(
            batch_start, batch_end,
            customers_df, products_df,
            scenario_config
        )
        orders.extend(batch_orders)

    return pd.DataFrame(orders)
```

#### 3. Basic Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_hourly_multiplier(hour, scenario_config):
    """Cache expensive hourly calculations"""
    return self._get_hourly_multiplier(hour, scenario_config)

@lru_cache(maxsize=50)
def get_customer_weights(customer_df):
    """Cache customer selection probabilities"""
    return calculate_weights_from_df(customer_df)
```

### Phase 2: Advanced Optimization (50-70% Additional Improvement)
**Goal**: Reduce execution time to 45-75 seconds

#### 1. Parallel Processing
```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def generate_orders_parallel(customers_df, products_df, scenario_config):
    num_cores = multiprocessing.cpu_count()
    duration_hours = scenario_config.duration_hours
    hours_per_core = duration_hours // num_cores

    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        for core_id in range(num_cores):
            start_hour = core_id * hours_per_core
            end_hour = (core_id + 1) * hours_per_core
            futures.append(executor.submit(
                generate_orders_batch,
                customers_df, products_df, scenario_config,
                start_hour, end_hour
            ))

        # Combine results from all processes
        orders = []
        for future in futures:
            orders.extend(future.result())

    return pd.DataFrame(orders)
```

#### 2. Memory-Efficient Generators
```python
def generate_orders_memory_efficient(customers_df, products_df, scenario_config):
    """Use generators to reduce memory footprint"""
    for hour in range(int(duration_hours)):
        orders_this_hour = calculate_hourly_orders(hour, scenario_config)
        for order_id in range(orders_this_hour):
            yield create_single_order(
                hour, order_id,
                customers_df, products_df,
                scenario_config
            )
            # Memory freed after each yield

# Convert to DataFrame at the end
orders_df = pd.DataFrame(list(generate_orders_memory_efficient(...)))
```

#### 3. Optimized Data Structures
```python
# Use numpy arrays for intermediate calculations
customer_ids = customers_df['customer_id'].values  # numpy array
product_ids = products_df['product_id'].values    # numpy array
prices = products_df['price'].values              # numpy array

# Vectorized operations on numpy arrays
selected_customers = np.random.choice(customer_ids, total_orders)
selected_products = np.random.choice(product_ids, total_orders)
order_prices = prices[selected_products]
```

### Phase 3: I/O and Format Optimization (10-15% Additional Improvement)
**Goal**: Reduce execution time to 40-65 seconds

#### 1. Feather Format (Fastest Pandas I/O)
```python
def save_data_feather(tables, scenario_name):
    """Use Feather format for fastest pandas I/O"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for table in tables:
        if table in self.data and not self.data[table].empty:
            filename = f"{scenario_name}_{timestamp}_{table}.feather"
            filepath = self.output_dir / filename

            # Feather is 2-3x faster than Parquet for pandas
            self.data[table].reset_index(drop=True).to_feather(filepath)
```

#### 2. Async File Operations
```python
import aiofiles
import asyncio

async def save_data_async(tables, scenario_name):
    """Non-blocking async file operations"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    async def save_table(table_name):
        if table_name in self.data and not self.data[table_name].empty:
            filename = f"{scenario_name}_{timestamp}_{table_name}.parquet"
            filepath = self.output_dir / filename

            # Async file write
            data = self.data[table_name].to_parquet()
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(data)

    await asyncio.gather(*[save_table(table) for table in tables])
```

#### 3. Compression Tuning
```python
def save_data_optimized_compression(tables, scenario_name):
    """Optimize Parquet compression levels"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for table in tables:
        if table in self.data and not self.data[table].empty:
            filename = f"{scenario_name}_{timestamp}_{table}.parquet"
            filepath = self.output_dir / filename

            # Use 'snappy' compression for best speed/size balance
            self.data[table].to_parquet(
                filepath,
                compression='snappy',  # Fastest compression
                index=False
            )
```

## 📈 Expected Performance Improvements

### Performance Projection Table
| Optimization Phase | Expected Time | Improvement | Cumulative Improvement |
|-------------------|---------------|-------------|-----------------------|
| Baseline (Current) | 151.39s | - | - |
| Phase 1 (Quick Wins) | 105-120s | 20-30% | 20-30% |
| Phase 2 (Advanced) | 45-75s | 50-70% | 50-75% |
| Phase 3 (I/O) | 40-65s | 55-75% | 55-75% |

### Visual Performance Roadmap
```
Current:     [==========] 151.39s (100%)
Phase 1:     [=====     ] 105-120s (20-30% faster)
Phase 2:     [==        ] 45-75s (50-70% faster)
Phase 3:     [=         ] 40-65s (55-75% faster)
```

## 🎯 Implementation Recommendations

### Priority Order
1. **Phase 1: Vectorization + Batch Processing** (Biggest immediate impact)
2. **Phase 1: Caching** (Eliminates redundant calculations)
3. **Phase 2: Parallel Processing** (Utilizes multi-core CPUs)
4. **Phase 2: Memory Optimization** (Reduces memory overhead)
5. **Phase 3: Format Optimization** (Feather format for I/O)

### Code Complexity vs Performance Gain
```text
Low Complexity, High Gain:
┣━ Vectorized operations
┣━ Batch processing
┗━ Basic caching

Medium Complexity, Medium Gain:
┣━ Parallel processing
┗━ Memory optimization

High Complexity, Low Gain:
┗━ Format optimization
```

## 🔧 Implementation Plan

### Week 1: Phase 1 Implementation
- **Day 1-2**: Vectorize order generation loop
- **Day 3**: Implement batch processing
- **Day 4**: Add basic caching mechanisms
- **Day 5**: Testing and validation

### Week 2: Phase 2 Implementation
- **Day 6-7**: Implement parallel processing
- **Day 8**: Add memory-efficient generators
- **Day 9**: Optimize data structures
- **Day 10**: Testing and validation

### Week 3: Phase 3 Implementation
- **Day 11**: Implement Feather format
- **Day 12**: Add async I/O operations
- **Day 13**: Tune compression settings
- **Day 14**: Final testing and benchmarking

## 📊 Success Metrics

### Target Performance Goals
- **Phase 1 Success**: < 120 seconds (20% improvement)
- **Phase 2 Success**: < 75 seconds (50% improvement)
- **Phase 3 Success**: < 65 seconds (57% improvement)
- **Stretch Goal**: < 50 seconds (67% improvement)

### Validation Methodology
```python
# Performance validation function
def validate_performance_improvement():
    start_time = time.time()
    generator.run_large_scenario()
    execution_time = time.time() - start_time

    if execution_time < 120:
        print(f"✅ Phase 1 Success: {execution_time:.1f}s (< 120s target)")
    elif execution_time < 75:
        print(f"✅ Phase 2 Success: {execution_time:.1f}s (< 75s target)")
    elif execution_time < 65:
        print(f"✅ Phase 3 Success: {execution_time:.1f}s (< 65s target)")
    else:
        print(f"⚠️  Needs Optimization: {execution_time:.1f}s")

    return execution_time
```

## 🎓 Key Takeaways

1. **The bottleneck is algorithmic, not I/O-related**
2. **Vectorization provides the biggest single improvement**
3. **Parallel processing scales well with multi-core CPUs**
4. **Format optimization has diminishing returns**
5. **Incremental approach ensures stable performance gains**

This optimization plan provides a clear roadmap to reduce execution time from 151 seconds to under 65 seconds through systematic, data-driven improvements.