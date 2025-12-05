import pytest
from tui_app import category_mapping

def test_category_mapping_valid_categories():
    """Test valid category mapping"""
    test_cases = [
        ("electronics", 1),
        ("clothing", 2),
        ("home", 3),
        ("beauty", 4),
        ("books", 5)
    ]

    for category, expected_num in test_cases:
        assert category_mapping(category) == expected_num

def test_category_mapping_invalid_category():
    """Test invalid category defaults to electronics (1)"""
    assert category_mapping("invalid") == 1
    assert category_mapping("") == 1
    assert category_mapping("unknown") == 1
