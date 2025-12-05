#!/usr/bin/env python3
"""
Fast integration tests for data generation workflows
Focused on key integration points without large data generation
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
import pandas as pd
import shutil

# Add the parent directory to Python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from generate import (
    ScenarioConfig,
    SyntheticDataGenerator,
    create_scenario_configs
)

class TestFastIntegration:
    """Fast integration tests focusing on key workflows"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = SyntheticDataGenerator(
            output_dir=self.temp_dir,
            output_format="csv"
        )

    def teardown_method(self):
        """Cleanup after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_minimal_scenario_workflow(self):
        """Test minimal scenario workflow with small data"""
        scenarios = create_scenario_configs()
        baseline_config = scenarios["baseline"]

        # Generate minimal data
        customers_df = self.generator.generate_customers(5, baseline_config)
        suppliers_df = self.generator.generate_suppliers()
        products_df = self.generator.generate_products(suppliers_df, baseline_config)

        # Test data relationships
        assert len(customers_df) == 5
        assert len(suppliers_df) == 8
        assert len(products_df) == 2500

        # Store and verify data
        self.generator.data["customers"] = customers_df
        self.generator.data["suppliers"] = suppliers_df
        self.generator.data["products"] = products_df

        assert "customers" in self.generator.data
        assert "suppliers" in self.generator.data
        assert "products" in self.generator.data

    def test_scenario_configuration_workflow(self):
        """Test scenario configuration workflow"""
        scenarios = create_scenario_configs()

        # Test scenario access
        assert len(scenarios) == 9
        assert "baseline" in scenarios
        assert "flash_sale" in scenarios

        # Test scenario properties
        baseline = scenarios["baseline"]
        assert baseline.name == "baseline"
        assert baseline.duration == "30d"
        assert baseline.intensity_multiplier == 1.0

    def test_data_saving_workflow(self):
        """Test data saving workflow with minimal data"""
        # Create minimal test data
        test_data = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["test1", "test2", "test3"],
            "value": [10, 20, 30]
        })
        self.generator.data["test_table"] = test_data

        # Save data
        saved_files = self.generator.save_data(["test_table"], "fast_test")

        # Verify save worked
        assert len(saved_files) == 1
        file_path = Path(self.temp_dir) / saved_files[0]
        assert file_path.exists()

        # Verify file content
        loaded_df = pd.read_csv(file_path)
        assert len(loaded_df) == 3
        assert list(loaded_df.columns) == ["id", "name", "value"]

    def test_cross_component_integration(self):
        """Test integration between components with minimal data"""
        from tui_app import category_mapping

        # Test category mapping integration
        test_config = ScenarioConfig(
            name="test_integration",
            duration="1h",
            intensity_multiplier=1.0,
            special_params={"category": "clothing"}
        )

        # Use TUI function to convert category
        if test_config.special_params and "category" in test_config.special_params:
            category_str = test_config.special_params["category"]
            if isinstance(category_str, str):
                numeric_category = category_mapping(category_str)
                test_config.special_params["category"] = numeric_category

        if test_config.special_params and "category" in test_config.special_params:
            assert test_config.special_params["category"] == 2

        # Test minimal generation with converted category
        customers_df = self.generator.generate_customers(3, test_config)
        assert len(customers_df) == 3

    def test_error_handling_integration(self):
        """Test error handling in integrated workflow"""
        # Test with minimal valid data
        scenarios = create_scenario_configs()
        baseline_config = scenarios["baseline"]

        # This should work fine
        customers_df = self.generator.generate_customers(2, baseline_config)
        assert len(customers_df) == 2

        # Test data storage and retrieval
        self.generator.data["test_customers"] = customers_df
        assert "test_customers" in self.generator.data
        assert len(self.generator.data["test_customers"]) == 2

    def test_performance_integration(self):
        """Test performance with very small datasets"""
        import time

        scenarios = create_scenario_configs()
        baseline_config = scenarios["baseline"]

        start_time = time.time()

        # Generate very small dataset
        customers_df = self.generator.generate_customers(3, baseline_config)
        suppliers_df = self.generator.generate_suppliers()

        end_time = time.time()
        generation_time = end_time - start_time

        # Should be very fast
        assert generation_time < 1.0  # < 1 second for tiny dataset
        assert len(customers_df) == 3
        assert len(suppliers_df) == 8

    def test_file_io_integration(self):
        """Test file I/O with minimal data"""
        # Create tiny test data
        test_data = pd.DataFrame({"id": [1], "value": [42]})
        self.generator.data["tiny"] = test_data

        # Save and verify
        saved_files = self.generator.save_data(["tiny"], "io_test")
        assert len(saved_files) == 1

        # Load and verify
        file_path = Path(self.temp_dir) / saved_files[0]
        loaded = pd.read_csv(file_path)
        assert len(loaded) == 1
        assert loaded.iloc[0]["value"] == 42

class TestScenarioSpecificIntegration:
    """Test scenario-specific integration points"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = SyntheticDataGenerator(
            output_dir=self.temp_dir,
            output_format="csv"
        )

    def teardown_method(self):
        """Cleanup after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_flash_sale_integration(self):
        """Test flash sale scenario integration"""
        scenarios = create_scenario_configs()
        flash_config = scenarios["flash_sale"]

        # Test flash sale properties
        assert flash_config.name == "flash_sale"
        assert flash_config.duration == "4h"
        assert flash_config.intensity_multiplier == 8.5

        # Test minimal generation
        customers_df = self.generator.generate_customers(2, flash_config)
        assert len(customers_df) == 2

    def test_returns_wave_integration(self):
        """Test returns wave scenario integration"""
        scenarios = create_scenario_configs()
        returns_config = scenarios["returns_wave"]

        # Test returns wave properties
        assert returns_config.name == "returns_wave"
        assert returns_config.duration == "14d"

        # Test minimal generation
        customers_df = self.generator.generate_customers(2, returns_config)
        assert len(customers_df) == 2

    def test_payment_outage_integration(self):
        """Test payment outage scenario integration"""
        scenarios = create_scenario_configs()
        outage_config = scenarios["payment_outage"]

        # Test payment outage properties
        assert outage_config.name == "payment_outage"
        assert outage_config.duration == "6h"

        # Test minimal generation
        customers_df = self.generator.generate_customers(2, outage_config)
        assert len(customers_df) == 2

class TestDataConsistencyIntegration:
    """Test data consistency across different scenarios"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = SyntheticDataGenerator(
            output_dir=self.temp_dir,
            output_format="csv"
        )

    def teardown_method(self):
        """Cleanup after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_consistent_customer_generation(self):
        """Test consistent customer generation across scenarios"""
        scenarios = create_scenario_configs()
        baseline_config = scenarios["baseline"]
        flash_config = scenarios["flash_sale"]

        # Generate same number of customers with different scenarios
        baseline_customers = self.generator.generate_customers(3, baseline_config)
        flash_customers = self.generator.generate_customers(3, flash_config)

        # Both should have same structure
        assert len(baseline_customers) == 3
        assert len(flash_customers) == 3

        # Both should have required columns
        required_cols = {"customer_id", "name", "email", "cohort"}
        assert required_cols.issubset(set(baseline_customers.columns))
        assert required_cols.issubset(set(flash_customers.columns))

    def test_supplier_consistency(self):
        """Test supplier generation consistency"""
        # Generate suppliers multiple times
        suppliers_1 = self.generator.generate_suppliers()
        suppliers_2 = self.generator.generate_suppliers()

        # Should always generate same number of suppliers
        assert len(suppliers_1) == 8
        assert len(suppliers_2) == 8

        # Should have same columns
        assert list(suppliers_1.columns) == list(suppliers_2.columns)

    def test_product_consistency(self):
        """Test product generation consistency"""
        scenarios = create_scenario_configs()
        baseline_config = scenarios["baseline"]

        # Generate products with same config
        suppliers_df = self.generator.generate_suppliers()
        products_1 = self.generator.generate_products(suppliers_df, baseline_config)
        products_2 = self.generator.generate_products(suppliers_df, baseline_config)

        # Should generate same number of products
        assert len(products_1) == 2500
        assert len(products_2) == 2500

        # Should have same structure
        assert list(products_1.columns) == list(products_2.columns)

class TestTUIIntegration:
    """Test TUI integration points"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = SyntheticDataGenerator(
            output_dir=self.temp_dir,
            output_format="csv"
        )

    def teardown_method(self):
        """Cleanup after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_category_mapping_integration(self):
        """Test category mapping function integration"""
        from tui_app import category_mapping

        # Test all valid categories
        categories = ["electronics", "clothing", "home", "beauty", "books"]
        expected_values = [1, 2, 3, 4, 5]

        for category, expected in zip(categories, expected_values):
            result = category_mapping(category)
            assert result == expected

        # Test case insensitivity
        assert category_mapping("ELECTRONICS") == 1
        assert category_mapping("Clothing") == 2

    def test_tui_generate_compatibility(self):
        """Test TUI and generate module compatibility"""
        from tui_app import category_mapping
        from generate import ScenarioConfig

        # Create config with string category
        config = ScenarioConfig(
            name="compatibility_test",
            duration="2h",
            intensity_multiplier=1.0,
            special_params={"category": "electronics"}
        )

        # Convert using TUI function
        if config.special_params and "category" in config.special_params:
            category_str = config.special_params["category"]
            if isinstance(category_str, str):
                config.special_params["category"] = category_mapping(category_str)

        # Should work with generation
        customers_df = self.generator.generate_customers(2, config)
        assert len(customers_df) == 2

class TestResourceManagementIntegration:
    """Test resource management in integration scenarios"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = SyntheticDataGenerator(
            output_dir=self.temp_dir,
            output_format="csv"
        )

    def teardown_method(self):
        """Cleanup after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_memory_efficiency(self):
        """Test memory efficiency with small datasets"""
        scenarios = create_scenario_configs()
        baseline_config = scenarios["baseline"]

        # Generate small dataset
        customers_df = self.generator.generate_customers(5, baseline_config)

        # Test memory usage is reasonable
        memory_usage = customers_df.memory_usage(deep=True).sum()
        assert memory_usage < 5000  # < 5KB for 5 customers

    def test_file_cleanup(self):
        """Test file cleanup works properly"""
        # Create and save test data
        test_data = pd.DataFrame({"id": [1, 2], "value": [10, 20]})
        self.generator.data["cleanup_test"] = test_data
        saved_files = self.generator.save_data(["cleanup_test"], "cleanup")

        # Verify file exists
        file_path = Path(self.temp_dir) / saved_files[0]
        assert file_path.exists()

        # Cleanup should work
        del self.generator.data["cleanup_test"]
        assert "cleanup_test" not in self.generator.data

        # File should still exist after data cleanup
        assert file_path.exists()

    def test_temp_directory_management(self):
        """Test temporary directory management"""
        # Verify temp directory exists
        assert Path(self.temp_dir).exists()

        # Verify it's empty initially
        initial_files = list(Path(self.temp_dir).iterdir())
        assert len(initial_files) == 0

        # Create some files
        test_data = pd.DataFrame({"test": [1]})
        self.generator.data["temp_test"] = test_data
        self.generator.save_data(["temp_test"], "temp")

        # Verify files were created
        final_files = list(Path(self.temp_dir).iterdir())
        assert len(final_files) > 0

        # Teardown will clean up automatically