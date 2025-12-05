# Data Dictionary Generator Documentation

## Overview

The Data Dictionary Generator is a Python script that automatically scans CSV files in a directory, infers appropriate data types for each column, and generates a comprehensive `data_dictionary.json` file. This tool is particularly useful for documenting synthetic data generation outputs and providing metadata for data analysis.

## Features

### Automatic Data Type Inference
The generator intelligently determines the most appropriate data type for each column:

- **UUID**: Detects UUID-formatted primary and foreign keys
- **Timestamp**: Identifies datetime and timestamp fields
- **Categorical**: Recognizes low-cardinality string fields (enums, categories)
- **Boolean**: Detects boolean flags and indicators
- **Integer**: Identifies whole number fields
- **Float**: Recognizes decimal and floating-point values
- **JSON Array**: Detects array-structured data
- **String**: Default type for text fields

### Intelligent Description Generation
The system generates meaningful descriptions for each column based on:
- Column naming patterns (e.g., `*_id` → "Primary key")
- Data type characteristics
- Common data modeling conventions
- Business domain terminology

### Comprehensive Output
Generates a structured JSON file containing:
- Table names extracted from CSV filenames
- Column-level metadata (type, description)
- Support for "new" field flagging
- Proper JSON formatting for easy consumption

## Installation

### Prerequisites
- Python 3.8+
- Required packages: `pandas`, `numpy`

### Virtual Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install pandas numpy
```

## Usage

### Basic Usage
```bash
.venv/bin/python data_dictionary_generator.py
```

### Command Line Interface
The script accepts the following parameters:

```bash
.venv/bin/python data_dictionary_generator.py [directory_path] [output_path]
```

- `directory_path`: Path to directory containing CSV files (default: `data/flash_sale`)
- `output_path`: Path to save the JSON file (default: `data_dictionary.json` in the same directory)

### Example Usage
```bash
# Generate data dictionary for flash sale data
.venv/bin/python data_dictionary_generator.py data/flash_sale

# Generate with custom output path
.venv/bin/python data_dictionary_generator.py data/flash_sale artifacts/custom_dictionary.json
```

## Implementation Details

### Core Functions

#### `infer_data_type(series: pd.Series) -> str`
Determines the most appropriate data type for a pandas Series.

**Supported Types:**
- `uuid`: UUID-formatted identifiers
- `timestamp`: Date/time values
- `categorical`: Low-cardinality strings
- `boolean`: True/False flags
- `int`: Integer values
- `float`: Floating-point values
- `json_array`: Array-structured data
- `string`: Text values (default)

#### `generate_description(column_name: str, data_type: str, sample_data: pd.Series) -> str`
Generates descriptive text for columns based on naming patterns and data types.

**Description Patterns:**
- ID fields → "Primary key" or "Foreign key"
- Timestamp fields → "Timestamp value"
- Categorical fields → "Category classification"
- Numeric fields → Context-appropriate descriptions
- Business domain terminology support

#### `scan_csv_files(directory_path: str) -> Dict`
Scans all CSV files in a directory and builds the data dictionary structure.

**Processing Logic:**
1. Extracts table names from filenames
2. Reads CSV files with type inference
3. Analyzes each column for data type and description
4. Handles errors gracefully with informative messages

#### `save_data_dictionary(data_dict: Dict, output_path: str)`
Saves the data dictionary to a properly formatted JSON file.

**Output Format:**
```json
{
  "table_name": {
    "column_name": {
      "type": "data_type",
      "desc": "description_text",
      "new": true  // optional for new columns
    }
  }
}
```

## Generated Output

### Sample Data Dictionary Structure
```json
{
  "customers": {
    "customer_id": {
      "type": "uuid",
      "desc": "Primary key"
    },
    "name": {
      "type": "string",
      "desc": "Customer full name"
    },
    "email": {
      "type": "string",
      "desc": "Email address"
    }
  },
  "products": {
    "product_id": {
      "type": "uuid",
      "desc": "Primary key"
    },
    "price": {
      "type": "float",
      "desc": "Product price"
    }
  }
}
```

### Flash Sale Data Dictionary
The generator successfully processed 10 tables from the flash sale dataset:
- **campaigns**: Marketing campaign information
- **customers**: Customer demographic and behavioral data
- **suppliers**: Supplier information and reliability metrics
- **products**: Product catalog with pricing and attributes
- **orders**: Order transactions with payment details
- **order_items**: Individual line items within orders
- **support_tickets**: Customer service interactions
- **cart_abandonment**: Abandoned shopping cart data
- **returns**: Product return and refund information
- **system_metrics**: Performance metrics and KPIs

## Integration with Synthetic Data Generation

### Workflow
1. **Data Generation**: Run `generate.py` to create synthetic datasets
2. **Dictionary Generation**: Run `data_dictionary_generator.py` to document the schema
3. **Analysis**: Use the data dictionary for EDA, modeling, and documentation

### Example Integration
```bash
# Generate synthetic data
python generate.py flash_sale

# Generate data dictionary
.venv/bin/python data_dictionary_generator.py data/flash_sale

# Use in analysis
python notebooks/flash_sale_eda.ipynb
```

## Technical Specifications

### Performance
- Processes ~100 rows per CSV file for efficient type inference
- Handles large datasets with memory-efficient sampling
- Fast execution (< 1 second for typical datasets)

### Error Handling
- Graceful handling of missing files
- Informative error messages
- Robust type inference with fallbacks

### Compatibility
- Works with any CSV-formatted data
- Supports various timestamp formats
- Handles mixed data types gracefully

## Best Practices

### Naming Conventions
- Use descriptive column names for better description generation
- Follow consistent naming patterns (e.g., `*_id`, `*_ts`, `is_*`)
- Include business domain terminology where appropriate

### Data Quality
- Ensure CSV files have proper headers
- Use consistent data types within columns
- Include representative sample data for accurate type inference

### Documentation
- Reference the data dictionary in analysis notebooks
- Use the dictionary for API documentation
- Include in data governance materials

## Troubleshooting

### Common Issues

**Issue: "Directory not found"**
- Verify the directory path exists
- Check for typos in the path
- Ensure proper permissions

**Issue: "Invalid CSV format"**
- Check CSV file headers
- Verify proper quoting and escaping
- Ensure consistent column counts

**Issue: "Type inference errors"**
- Review sample data for consistency
- Check for mixed data types in columns
- Verify timestamp formats

### Debugging
```bash
# Run with verbose output
.venv/bin/python -v data_dictionary_generator.py

# Check specific file
.venv/bin/python -c "import pandas as pd; df = pd.read_csv('data/flash_sale/orders.csv'); print(df.head())"
```

## Future Enhancements

### Planned Features
- Support for additional data formats (Parquet, JSON)
- Custom description templates
- Data quality metrics
- Column relationship mapping
- Automated documentation generation

### Contribution Guidelines
- Follow existing code style and patterns
- Add comprehensive test cases
- Document new features thoroughly
- Maintain backward compatibility

## Support

For issues or questions, refer to the project documentation or create a GitHub issue with:
- Detailed description of the problem
- Sample data causing the issue
- Expected vs actual behavior
- Environment information (Python version, dependencies)