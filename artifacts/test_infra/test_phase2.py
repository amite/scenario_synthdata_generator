#!/usr/bin/env python3
"""
Phase 2 Performance Testing Framework
Tests the new parallel processing, advanced caching, and memory optimization implementations
"""

import time
import subprocess
import sys
import pandas as pd
from generate import SyntheticDataGenerator, ScenarioConfig, create_scenario_configs

def test_phase2_parallel_processing():
    """Test parallel processing for large datasets"""
    print("🧪 Testing Phase 2 Parallel Processing...")

    # Create test scenario for large dataset
    scenario_config = ScenarioConfig(
        name="performance_test",
        duration="24h",
        intensity_multiplier=5.0,
        special_params={
            "orders_per_hour": 10000  # Should trigger parallel processing (>100K orders)
        }
    )

    generator = SyntheticDataGenerator(output_dir="test_data", output_format="csv")

    # Generate test data
    print("  📊 Generating test customers and products...")
    customers_df = generator.generate_customers(1000, scenario_config)
    products_df = generator.generate_products(generator.generate_suppliers(), scenario_config)
    campaigns_df = pd.DataFrame()  # Empty for this test

    print("  🚀 Testing parallel order generation...")
    start_time = time.time()

    try:
        orders_df = generator.generate_orders(
            customers_df, products_df, campaigns_df, scenario_config
        )
        end_time = time.time()

        print(f"  ✅ Parallel processing completed in {end_time - start_time:.2f} seconds")
        print(f"  📈 Generated {len(orders_df)} orders")
        print(f"  📊 Performance: {len(orders_df) / (end_time - start_time):.0f} orders/second")

        return True, end_time - start_time, len(orders_df)

    except Exception as e:
        print(f"  ❌ Parallel processing failed: {e}")
        return False, 0, 0

def test_phase2_advanced_caching():
    """Test advanced caching for medium datasets"""
    print("\n🧪 Testing Phase 2 Advanced Caching...")

    # Create test scenario for medium dataset
    scenario_config = ScenarioConfig(
        name="performance_test",
        duration="12h",
        intensity_multiplier=2.5,
        special_params={
            "orders_per_hour": 5000  # Should trigger advanced caching (>50K orders)
        }
    )

    generator = SyntheticDataGenerator(output_dir="test_data", output_format="csv")

    # Generate test data
    print("  📊 Generating test customers and products...")
    customers_df = generator.generate_customers(500, scenario_config)
    products_df = generator.generate_products(generator.generate_suppliers(), scenario_config)
    campaigns_df = pd.DataFrame()  # Empty for this test

    print("  💡 Testing advanced caching order generation...")
    start_time = time.time()

    try:
        orders_df = generator.generate_orders(
            customers_df, products_df, campaigns_df, scenario_config
        )
        end_time = time.time()

        print(f"  ✅ Advanced caching completed in {end_time - start_time:.2f} seconds")
        print(f"  📈 Generated {len(orders_df)} orders")
        print(f"  📊 Performance: {len(orders_df) / (end_time - start_time):.0f} orders/second")

        return True, end_time - start_time, len(orders_df)

    except Exception as e:
        print(f"  ❌ Advanced caching failed: {e}")
        return False, 0, 0

def test_phase2_memory_optimization():
    """Test memory optimization for small datasets"""
    print("\n🧪 Testing Phase 2 Memory Optimization...")

    # Create test scenario for small dataset
    scenario_config = ScenarioConfig(
        name="performance_test",
        duration="2h",
        intensity_multiplier=1.0,
        special_params={
            "orders_per_hour": 100  # Should trigger memory optimization (<50K orders)
        }
    )

    generator = SyntheticDataGenerator(output_dir="test_data", output_format="csv")

    # Generate test data
    print("  📊 Generating test customers and products...")
    customers_df = generator.generate_customers(100, scenario_config)
    products_df = generator.generate_products(generator.generate_suppliers(), scenario_config)
    campaigns_df = pd.DataFrame()  # Empty for this test

    print("  🧠 Testing memory-optimized order generation...")
    start_time = time.time()

    try:
        orders_df = generator.generate_orders(
            customers_df, products_df, campaigns_df, scenario_config
        )
        end_time = time.time()

        print(f"  ✅ Memory optimization completed in {end_time - start_time:.2f} seconds")
        print(f"  📈 Generated {len(orders_df)} orders")
        print(f"  📊 Performance: {len(orders_df) / (end_time - start_time):.0f} orders/second")

        return True, end_time - start_time, len(orders_df)

    except Exception as e:
        print(f"  ❌ Memory optimization failed: {e}")
        return False, 0, 0

def test_cli_integration():
    """Test CLI integration with Phase 2 optimizations"""
    print("\n🧪 Testing CLI Integration...")

    try:
        # Test small dataset (memory optimization)
        result = subprocess.run([
            sys.executable, "generate.py", "baseline",
            "--duration", "1h",
            "--intensity", "1.0",
            "--output-dir", "test_data",
            "--tables", "customers,products,orders"
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("  ✅ CLI integration test passed")
            return True
        else:
            print(f"  ❌ CLI integration test failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("  ❌ CLI integration test timed out")
        return False
    except Exception as e:
        print(f"  ❌ CLI integration test failed: {e}")
        return False

def run_comprehensive_phase2_tests():
    """Run all Phase 2 tests and generate performance report"""
    print("🚀 Running Comprehensive Phase 2 Performance Tests")
    print("=" * 60)

    results = []

    # Run individual tests
    parallel_success, parallel_time, parallel_orders = test_phase2_parallel_processing()
    cached_success, cached_time, cached_orders = test_phase2_advanced_caching()
    memory_success, memory_time, memory_orders = test_phase2_memory_optimization()
    cli_success = test_cli_integration()

    results.append(("Parallel Processing", parallel_success, parallel_time, parallel_orders))
    results.append(("Advanced Caching", cached_success, cached_time, cached_orders))
    results.append(("Memory Optimization", memory_success, memory_time, memory_orders))
    results.append(("CLI Integration", cli_success, 0, 0))

    # Generate performance report
    print("\n" + "=" * 60)
    print("📊 PHASE 2 PERFORMANCE REPORT")
    print("=" * 60)

    for name, success, time_taken, order_count in results:
        status = "✅ PASS" if success else "❌ FAIL"
        if time_taken > 0:
            performance = f"{order_count / time_taken:.0f} orders/sec"
        else:
            performance = "N/A"
        print(f"{status} {name}: {time_taken:.2f}s | {order_count} orders | {performance}")

    # Calculate overall success
    total_tests = len(results)
    passed_tests = sum(1 for _, success, _, _ in results if success)

    print(f"\n📈 Overall Results: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 All Phase 2 optimizations working correctly!")
        return True
    else:
        print("⚠️  Some Phase 2 optimizations need attention")
        return False

if __name__ == "__main__":
    success = run_comprehensive_phase2_tests()
    sys.exit(0 if success else 1)