# TUI Application Documentation

## Overview
This document provides comprehensive documentation of the work done on the TUI (Textual User Interface) application for the Synthetic E-Commerce Data Generator. It covers bug fixes, feature enhancements, and technical implementation details.

## Table of Contents
1. [Bug Fixes](#bug-fixes)
2. [Feature Enhancements](#feature-enhancements)
3. [Technical Implementation](#technical-implementation)
4. [Testing and Validation](#testing-and-validation)
5. [Usage Examples](#usage-examples)

## Bug Fixes

### Issue: Type Mismatch in special_params Dictionary (Line 508)

**Problem Description:**
The application encountered a type mismatch error when trying to assign string values to the `special_params` dictionary in the `CustomParametersScreen` class. The error message was:
```
Argument of type "str" cannot be assigned to parameter "value" of type "int" in function "__setitem__"
```

**Root Cause:**
The `special_params` dictionary was expected to contain only integer values, but the `category` parameter (representing product categories like "electronics", "clothing", etc.) was being stored as a string.

**Solution Implemented:**
1. **Category Mapping System**: Created a numeric mapping for product categories:
   ```python
   category_mapping = {
       "electronics": 1,
       "clothing": 2,
       "home": 3,
       "beauty": 4,
       "books": 5
   }
   ```

2. **Type Conversion**: Modified the `CustomParametersScreen.handle_continue` method to convert string categories to numeric values:
   ```python
   special_params["category"] = category_mapping.get(category.lower(), 1)
   ```

3. **Backward Compatibility**: Updated the `generate.py` file to handle numeric category values by converting them back to strings when needed:
   ```python
   # Category mapping for numeric to string conversion
   category_mapping = {
       1: "electronics",
       2: "clothing",
       3: "home",
       4: "beauty",
       5: "books"
   }

   # Convert numeric category back to string
   if isinstance(focus_category, int):
       focus_category = category_mapping.get(focus_category, "electronics")
   ```

**Files Modified:**
- `tui_app.py`: Lines 508-516 (category mapping and conversion)
- `generate.py`: Lines 208-221 (category conversion in product generation)
- `generate.py`: Lines 269-283 (category conversion in campaign generation)
- `generate.py`: Lines 1270-1281 (command-line argument handling)
- `generate.py`: Line 1102 (predefined scenario category values)

**Impact:**
- Resolved the type mismatch error
- Maintained backward compatibility with existing code
- Improved type consistency throughout the application
- All category references now use numeric representation internally while preserving string functionality

## Feature Enhancements

### Custom Directory Path Option

**Feature Description:**
Added the ability for users to specify custom output directories for generated data files, with automatic directory creation.

**Implementation Details:**

1. **UI Addition**: Added an input field in the confirmation screen:
   ```python
   with Vertical(classes="input-group"):
       yield Label("Output Directory (relative to data/):", classes="input-label")
       yield Input(placeholder="e.g., custom_scenario", id="input-output-dir", value="")
   ```

2. **CSS Styling**: Added proper styling for input fields:
   ```css
   .input-group {
       margin: 1 0;
   }

   .input-label {
       color: $text;
       margin-bottom: 0;
   }

   Input {
       width: 100%;
   }
   ```

3. **Directory Handling**: Enhanced the `GenerationScreen` class:
   ```python
   def __init__(self, scenario_name: str, scenario_config: ScenarioConfig, output_dir: str = "data"):
       # ... existing code ...
       self.output_dir = output_dir

   # Directory creation logic
   output_path = Path(self.output_dir)
   if not output_path.exists():
       output_path.mkdir(parents=True, exist_ok=True)
   ```

4. **Path Resolution**: Modified the confirmation screen to handle custom paths:
   ```python
   # Get custom output directory if specified
   output_dir_input = self.query_one("#input-output-dir", Input)
   custom_subdir = output_dir_input.value.strip() if output_dir_input else ""

   # Create full output directory path
   if custom_subdir:
       output_dir = f"data/{custom_subdir}"
   else:
       output_dir = "data"
   ```

**Features:**
- **Default Behavior**: Uses "data" directory when no custom path is specified
- **Custom Paths**: Supports paths like "custom_scenario" → saves to "data/custom_scenario/"
- **Nested Paths**: Supports nested paths like "test/nested/path" with automatic parent directory creation
- **Automatic Creation**: Creates specified directories if they don't exist
- **Validation**: All paths are relative to the "data" directory as requested

**Files Modified:**
- `tui_app.py`: Lines 717-724 (input field and CSS)
- `tui_app.py`: Lines 776-788 (path resolution logic)
- `tui_app.py`: Lines 832-837 (constructor update)
- `tui_app.py`: Lines 861-873 (directory creation)
- `tui_app.py`: Line 989 (output path display)

## Technical Implementation

### Category Mapping System

**Design Pattern**: Strategy Pattern with Mapping
- Created bidirectional mapping between string category names and numeric IDs
- Implemented conversion functions in both directions (string→int and int→string)
- Maintained consistency across all category references

**Type Safety**:
- Ensured all `special_params` dictionary values are integers
- Added type checking with `isinstance()` before conversions
- Provided default values for missing or invalid categories

### Directory Management

**Path Handling**:
- Used `pathlib.Path` for cross-platform path manipulation
- Implemented `parents=True` for nested directory creation
- Added existence checks before directory operations

**Error Handling**:
- Graceful handling of missing directories
- Automatic creation of parent directories
- Clear user feedback about directory operations

## Testing and Validation

### Test Coverage

**Type Fix Testing**:
1. Verified predefined scenarios use numeric category values
2. Tested category mapping in both directions
3. Confirmed the fix resolves the original type mismatch error

**Directory Feature Testing**:
1. Tested default directory behavior
2. Verified custom directory creation
3. Validated nested path handling
4. Confirmed automatic directory creation

### Test Results

**Type Fix Tests**:
```
✅ Predefined scenario test passed!
✅ Custom scenario test passed!
🎉 All tests passed!
```

**Directory Tests**:
```
✅ Created directory: data/custom_scenario
✅ Created directory: data/flash_sale_results
✅ Created directory: data/test/nested/path
✅ All directory creation tests passed!
✅ Path validation tests passed!
🎉 All custom directory tests passed!
```

## Usage Examples

### Default Directory Usage
```python
# No custom directory specified - uses default "data" directory
app.push_screen(GenerationScreen("flash_sale", config))
# Files saved to: ./data/
```

### Custom Directory Usage
```python
# Custom directory specified
app.push_screen(GenerationScreen("flash_sale", config, "data/custom_scenario"))
# Files saved to: ./data/custom_scenario/
```

### Nested Directory Usage
```python
# Nested directory path
app.push_screen(GenerationScreen("flash_sale", config, "data/2024/flash_sale"))
# Files saved to: ./data/2024/flash_sale/
# Automatically creates "2024" parent directory
```

## Code Examples

### Category Conversion
```python
# String to numeric conversion (TUI)
category_mapping = {
    "electronics": 1,
    "clothing": 2,
    "home": 3,
    "beauty": 4,
    "books": 5
}
special_params["category"] = category_mapping.get(category.lower(), 1)

# Numeric to string conversion (Generator)
category_mapping = {
    1: "electronics",
    2: "clothing",
    3: "home",
    4: "beauty",
    5: "books"
}
if isinstance(focus_category, int):
    focus_category = category_mapping.get(focus_category, "electronics")
```

### Directory Creation
```python
# Ensure output directory exists
output_path = Path(self.output_dir)
if not output_path.exists():
    output_path.mkdir(parents=True, exist_ok=True)
    self.add_log(f"Created output directory: {self.output_dir}")

# Initialize generator with custom directory
self.generator = SyntheticDataGenerator(
    output_dir=self.output_dir,
    output_format="csv"
)
```

## Summary

This documentation covers all the significant work done on the TUI application:

1. **Critical Bug Fix**: Resolved the type mismatch issue in the `special_params` dictionary
2. **Feature Enhancement**: Added custom directory path functionality with automatic creation
3. **Technical Improvements**: Implemented robust category mapping and directory management systems
4. **Testing**: Comprehensive testing of all new functionality
5. **Documentation**: Complete usage examples and code samples

The application now provides a more flexible and user-friendly experience while maintaining type safety and backward compatibility.