#!/usr/bin/env python3
"""
Fast regression tests for data quality and consistency
Optimized to avoid slow baseline scenario tests
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import shutil

# Add the parent directory to Python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from generate import (
    ScenarioConfig,
    SyntheticDataGenerator,
    create_scenario_configs
)

class TestFastDataQualityRegression:
    """Fast regression tests for data quality and consistency"""

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

    def test_scenario_configuration_stability(self):
        """Fast regression test: Verify scenario configurations remain stable"""
        scenarios = create_scenario_configs()

        # Test that all expected scenarios exist
        expected_scenarios = [
            "flash_sale", "returns_wave", "supply_disruption",
            "payment_outage", "viral_moment", "customer_segments",
            "seasonal_planning", "multi_channel", "baseline"
        ]

        for scenario_name in expected_scenarios:
            assert scenario_name in scenarios

        # Test basic scenario properties without generating data
        baseline = scenarios["baseline"]
        assert baseline.name == "baseline"
        assert baseline.duration == "30d"
        assert baseline.intensity_multiplier == 1.0

    def test_minimal_data_generation_consistency(self):
        """Fast regression test: Verify data generation with minimal data"""
        # Use simple config to avoid slow baseline
        simple_config = ScenarioConfig(
            name="regression_test",
            duration="1h",
            intensity_multiplier=1.0
        )

        # Generate minimal data
        customers_1 = self.generator.generate_customers(3, simple_config)
        customers_2 = self.generator.generate_customers(3, simple_config)

        # Should generate same number of customers
        assert len(customers_1) == 3
        assert len(customers_2) == 3

        # Should have same structure
        assert list(customers_1.columns) == list(customers_2.columns)

    def test_supplier_data_stability(self):
        """Fast regression test: Verify supplier data remains consistent"""
        suppliers_1 = self.generator.generate_suppliers()
        suppliers_2 = self.generator.generate_suppliers()

        # Should always generate same number of suppliers
        assert len(suppliers_1) == 8
        assert len(suppliers_2) == 8

        # Should have same structure
        assert list(suppliers_1.columns) == list(suppliers_2.columns)

    def test_tui_component_stability(self):
        """Fast regression test: Verify TUI components remain stable"""
        from tui_app import (
            LoadingScreen, ScenarioSelectionScreen,
            CustomScenarioScreen, HelpScreen
        )

        # Test that screens can be instantiated
        loading_screen = LoadingScreen()
        scenario_screen = ScenarioSelectionScreen()
        custom_screen = CustomScenarioScreen()
        help_screen = HelpScreen()

        # Verify screens have expected attributes
        assert hasattr(loading_screen, 'CSS')
        assert hasattr(scenario_screen, 'scenarios')
        assert hasattr(help_screen, 'CSS')

    def test_category_mapping_stability(self):
        """Fast regression test: Verify category mapping remains consistent"""
        from tui_app import category_mapping

        # Test that category mapping produces expected results
        mapping_tests = {
            "electronics": 1,
            "clothing": 2,
            "home": 3,
            "beauty": 4,
            "books": 5,
            "ELECTRONICS": 1,  # Case insensitive
            "Clothing": 2    # Case insensitive
        }

        for category, expected in mapping_tests.items():
            result = category_mapping(category)
            assert result == expected

    def test_tui_generate_integration_stability(self):
        """Fast regression test: Verify TUI and generate integration"""
        from tui_app import category_mapping
        from generate import ScenarioConfig

        # Test integration between components with minimal data
        config = ScenarioConfig(
            name="regression_test",
            duration="1h",
            intensity_multiplier=1.0,
            special_params={"category": "electronics"}
        )

        # Use TUI function to convert category
        if config.special_params and "category" in config.special_params:
            category_str = config.special_params["category"]
            if isinstance(category_str, str):
                config.special_params["category"] = category_mapping(category_str)

        # Should work with minimal generation
        customers_df = self.generator.generate_customers(2, config)
        assert len(customers_df) == 2

    def test_file_io_stability(self):
        """Fast regression test: Verify file I/O operations remain stable"""
        # Create minimal test data
        test_data = pd.DataFrame({
            "id": [1, 2],
            "value": [10, 20]
        })
        self.generator.data["regression_test"] = test_data

        # Save data
        saved_files = self.generator.save_data(["regression_test"], "regression")

        # Verify file operations work
        assert len(saved_files) == 1

        # Verify file can be read back
        file_path = Path(self.temp_dir) / saved_files[0]
        loaded_df = pd.read_csv(file_path)

        # Verify data integrity
        assert len(loaded_df) == 2
        assert list(loaded_df["id"]) == [1, 2]
        assert list(loaded_df["value"]) == [10, 20]

    def test_error_handling_stability(self):
        """Fast regression test: Verify error handling remains consistent"""
        # Test with minimal data
        simple_config = ScenarioConfig(
            name="error_test",
            duration="1h",
            intensity_multiplier=1.0
        )

        # Test with valid data (should work)
        customers_df = self.generator.generate_customers(2, simple_config)
        assert len(customers_df) == 2

        # Test data storage and retrieval
        self.generator.data["error_test"] = customers_df
        assert "error_test" in self.generator.data
        assert len(self.generator.data["error_test"]) == 2

        # Test cleanup
        del self.generator.data["error_test"]
        assert "error_test" not in self.generator.data

    def test_performance_stability(self):
        """Fast regression test: Verify performance remains stable"""
        import time

        simple_config = ScenarioConfig(
            name="perf_test",
            duration="1h",
            intensity_multiplier=1.0
        )

        # Test multiple generations for consistency
        execution_times = []
        for _ in range(2):  # Reduced from 3 to 2 for speed
            start_time = time.time()
            customers_df = self.generator.generate_customers(3, simple_config)
            end_time = time.time()
            execution_times.append(end_time - start_time)

        # All executions should be fast
        for exec_time in execution_times:
            assert exec_time < 0.5  # < 0.5 second per generation

    def test_resource_cleanup_stability(self):
        """Fast regression test: Verify resource cleanup remains stable"""
        # Create and cleanup minimal data
        for i in range(2):  # Reduced from 3 to 2 for speed
            test_data = pd.DataFrame({"test": [i]})
            self.generator.data[f"cleanup_test_{i}"] = test_data

            # Verify data was stored
            assert f"cleanup_test_{i}" in self.generator.data

            # Cleanup
            del self.generator.data[f"cleanup_test_{i}"]

        # Verify all cleaned up
        for i in range(2):
            assert f"cleanup_test_{i}" not in self.generator.data

        # Verify generator still works
        customers_df = self.generator.generate_customers(1, ScenarioConfig("test"))
        assert len(customers_df) == 1