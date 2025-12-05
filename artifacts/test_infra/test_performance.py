#!/usr/bin/env python3
"""
Performance test for the vectorized order generation improvements
Tests the system with ~1M records to verify scalability
"""
import time
import pandas as pd
from generate import SyntheticDataGenerator, ScenarioConfig

def test_performance():
    """Test performance with approximately 1 million orders"""
    print("🚀 Starting performance test for ~1M orders...")
    print("=" * 50)

    # Create a scenario that will generate ~1M orders
    test_config = ScenarioConfig(
        name="performance_test",
        duration="24h",  # 24 hours
        intensity_multiplier=5.0,  # High intensity
        special_params={
            "orders_per_hour": 20000  # 20k orders/hour * 24h * 5x = ~2.4M orders
        }
    )

    generator = SyntheticDataGenerator(output_dir="test_data")

    print("📊 Test Configuration:")
    print(f"  - Duration: {test_config.duration}")
    print(f"  - Intensity Multiplier: {test_config.intensity_multiplier}")
    print(f"  - Orders per Hour: {test_config.special_params['orders_per_hour'] if test_config.special_params else 'N/A'}")
    print(f"  - Expected Total Orders: ~{20000 * 24 * 5:,}")
    print()

    # Start timing
    start_time = time.time()
    print("⏱️  Starting data generation...")

    try:
        # Generate test data
        print("👥 Generating customers...")
        customers_df = generator.generate_customers(50000, test_config)

        print("🏭 Generating suppliers...")
        suppliers_df = generator.generate_suppliers()

        print("📦 Generating products...")
        products_df = generator.generate_products(suppliers_df, test_config)

        print("🛒 Generating orders (this is the vectorized part we're testing)...")
        orders_start = time.time()
        orders_df = generator.generate_orders(customers_df, products_df, pd.DataFrame(), test_config)
        orders_time = time.time() - orders_start

        end_time = time.time()
        total_execution_time = end_time - start_time

        print()
        print("🏁 Performance Results:")
        print(f"  - Total Execution Time: {total_execution_time:.2f} seconds")
        print(f"  - Orders Generation Time: {orders_time:.2f} seconds")
        print(f"  - Total Orders Generated: {len(orders_df):,}")
        print(f"  - Performance Rate: {len(orders_df)/orders_time:.0f} orders/second")
        print(f"  - Overall Rate: {len(orders_df)/total_execution_time:.0f} orders/second (including setup)")

        # Performance classification
        if len(orders_df) >= 1_000_000:
            print("  - 🎯 SUCCESS: Generated 1M+ orders!")
        else:
            print(f"  - ⚠️  Generated {len(orders_df):,} orders (less than 1M)")

        return total_execution_time, orders_time, len(orders_df)

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None, 0

if __name__ == "__main__":
    exec_time, orders_time, order_count = test_performance()
    print()
    print("📊 Test Summary:")
    print(f"  - Generated {order_count:,} orders")
    print(f"  - Orders generation took {orders_time:.2f} seconds")
    print(f"  - Overall process took {exec_time:.2f} seconds")
    print(f"  - Peak performance: {order_count/orders_time:.0f} orders/second" if orders_time else "  - Peak performance: N/A (test failed)")