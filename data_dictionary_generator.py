#!/usr/bin/env python3
"""
Data Dictionary Generator for CSV Files
Scans CSV files in a directory, determines appropriate datatypes for each column,
and generates a comprehensive data_dictionary.json file.
"""

import os
import json
import pandas as pd
import numpy as np
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union

def infer_data_type(series) -> str:
    """
    Infers the most appropriate data type for a pandas Series.
    Returns one of: 'uuid', 'string', 'int', 'float', 'boolean', 'timestamp', 'categorical', 'json_array'
    """
    # Check for empty series
    if series.empty:
        return "string"

    # Check for UUID format
    try:
        if all(str(x).lower() in ['nan', 'none', 'null'] or
               (isinstance(x, str) and len(x) == 36 and x.count('-') == 4)
               for x in series.dropna()):
            return "uuid"
    except:
        pass

    # Check for boolean
    unique_values = series.dropna().unique()
    if len(unique_values) <= 2 and all(isinstance(x, bool) or
                                      (isinstance(x, (str, int, float)) and str(x).lower() in ['true', 'false', '1', '0'])
                                      for x in unique_values):
        return "boolean"

    # Check for timestamp/datetime
    try:
        # Try parsing as datetime
        sample_values = series.dropna().head(10)
        if all(pd.api.types.is_datetime64_any_dtype(series) or
               (isinstance(x, str) and ('-' in x or ':' in x or 'T' in x or ' ' in x)) or
               isinstance(x, (datetime, pd.Timestamp))
               for x in sample_values):
            return "timestamp"
    except:
        pass

    # Check for categorical (low cardinality strings)
    if series.dtype == 'object':
        unique_count = series.nunique()
        total_count = len(series.dropna())
        if total_count > 0 and unique_count / total_count < 0.5:  # Less than 50% unique values
            return "categorical"

    # Check for numeric types
    if pd.api.types.is_integer_dtype(series):
        return "int"
    elif pd.api.types.is_float_dtype(series):
        return "float"

    # Check for JSON arrays (strings that look like arrays)
    try:
        if all(isinstance(x, str) and (x.startswith('[') and x.endswith(']')) or
               (isinstance(x, list))
               for x in series.dropna().head(5)):
            return "json_array"
    except:
        pass

    # Default to string
    return "string"

def generate_description(column_name: str, data_type: str, sample_data: pd.Series) -> str:
    """
    Generates a descriptive description for a column based on its name and data type.
    """
    descriptions = {
        # Common patterns
        'id': 'Primary key',
        'name': 'Name or title',
        'email': 'Email address',
        'phone': 'Phone number',
        'address': 'Physical address',
        'city': 'City for regional analysis',
        'state': 'State for regional analysis',
        'country': 'Country identifier',
        'price': 'Monetary value',
        'cost': 'Cost amount for margin calculation',
        'weight': 'Weight measurement',
        'quantity': 'Count or quantity',
        'amount': 'Monetary amount',
        'total': 'Total calculated value',
        'subtotal': 'Subtotal before discounts',
        'discount': 'Discount amount or percentage',
        'tax': 'Tax amount',
        'shipping': 'Shipping cost',
        'status': 'Current status',
        'type': 'Type classification',
        'category': 'Category classification',
        'subcategory': 'Subcategory for granular analysis',
        'brand': 'Product brand',
        'sku': 'Stock keeping unit',
        'timestamp': 'Timestamp',
        'date': 'Date value',
        'time': 'Time value',
        'created': 'Creation timestamp',
        'updated': 'Last update timestamp',
        'start': 'Start timestamp',
        'end': 'End timestamp',
        'expected': 'Expected timestamp',
        'actual': 'Actual timestamp',
        'is_': 'Boolean flag',
        'has_': 'Boolean flag',
        'can_': 'Boolean flag',
        'count': 'Count of items',
        'rate': 'Rate or ratio',
        'score': 'Score or rating',
        'percentage': 'Percentage value',
        'ratio': 'Ratio value',
        'multiplier': 'Multiplier factor',
        'channel': 'Channel or medium',
        'source': 'Source identifier',
        'reason': 'Reason or explanation',
        'pattern': 'Pattern classification',
        'tier': 'Tier classification',
        'cohort': 'Cohort classification',
        'segment': 'Segment classification',
        'value': 'Value measurement',
        'duration': 'Duration measurement',
        'delay': 'Delay measurement',
        'processing': 'Processing time',
        'resolution': 'Resolution time',
        'lead': 'Lead time',
        'reliability': 'Reliability score',
        'sensitivity': 'Sensitivity score',
        'intensity': 'Intensity multiplier',
        'capacity': 'Capacity measurement',
        'load': 'Load measurement',
        'utilization': 'Utilization percentage',
        'failure': 'Failure indicator',
        'breach': 'SLA breach indicator',
        'escalation': 'Escalation count',
        'priority': 'Priority level',
        'severity': 'Severity level',
        'language': 'Language identifier',
        'currency': 'Currency identifier',
        'unit': 'Unit of measurement',
        'session': 'Session identifier',
        'token': 'Authentication token',
        'key': 'Identifier key',
        'code': 'Code identifier',
        'number': 'Numeric identifier',
        'identifier': 'Unique identifier',
        'reference': 'Reference identifier',
        'parent': 'Parent reference',
        'child': 'Child reference',
        'foreign': 'Foreign key reference',
        'primary': 'Primary key',
        'secondary': 'Secondary key',
        'index': 'Index value',
        'position': 'Position value',
        'rank': 'Rank value',
        'order': 'Order value',
        'sequence': 'Sequence value',
        'version': 'Version identifier',
        'revision': 'Revision identifier',
        'metadata': 'Metadata information',
        'notes': 'Additional notes',
        'comments': 'Comments or remarks',
        'description': 'Descriptive text',
        'title': 'Title text',
        'label': 'Label text',
        'tag': 'Tag text',
        'attribute': 'Attribute value',
        'property': 'Property value',
        'feature': 'Feature value',
        'characteristic': 'Characteristic value',
        'parameter': 'Parameter value',
        'configuration': 'Configuration value',
        'setting': 'Setting value',
        'option': 'Option value',
        'choice': 'Choice value',
        'selection': 'Selection value',
        'preference': 'Preference value',
        'behavior': 'Behavior value',
        'action': 'Action value',
        'event': 'Event value',
        'activity': 'Activity value',
        'transaction': 'Transaction value',
        'operation': 'Operation value',
        'process': 'Process value',
        'workflow': 'Workflow value',
        'pipeline': 'Pipeline value',
        'system': 'System value',
        'component': 'Component value',
        'module': 'Module value',
        'function': 'Function value',
        'method': 'Method value',
        'procedure': 'Procedure value',
        'routine': 'Routine value',
        'algorithm': 'Algorithm value',
        'model': 'Model value',
        'strategy': 'Strategy value',
        'tactic': 'Tactic value',
        'approach': 'Approach value',
        'technique': 'Technique value',
        'methodology': 'Methodology value',
        'framework': 'Framework value',
        'architecture': 'Architecture value',
        'design': 'Design value',
        'implementation': 'Implementation value',
        'execution': 'Execution value',
        'performance': 'Performance value',
        'efficiency': 'Efficiency value',
        'effectiveness': 'Effectiveness value',
        'quality': 'Quality value',
        'reliability': 'Reliability value',
        'availability': 'Availability value',
        'scalability': 'Scalability value',
        'flexibility': 'Flexibility value',
        'maintainability': 'Maintainability value',
        'portability': 'Portability value',
        'usability': 'Usability value',
        'accessibility': 'Accessibility value',
        'security': 'Security value',
        'privacy': 'Privacy value',
        'compliance': 'Compliance value',
        'governance': 'Governance value',
        'management': 'Management value',
        'administration': 'Administration value',
        'operation': 'Operation value',
        'maintenance': 'Maintenance value',
        'support': 'Support value',
        'service': 'Service value',
        'assistance': 'Assistance value',
        'help': 'Help value',
        'guidance': 'Guidance value',
        'direction': 'Direction value',
        'instruction': 'Instruction value',
        'training': 'Training value',
        'education': 'Education value',
        'learning': 'Learning value',
        'development': 'Development value',
        'growth': 'Growth value',
        'improvement': 'Improvement value',
        'optimization': 'Optimization value',
        'enhancement': 'Enhancement value',
        'refinement': 'Refinement value',
        'advancement': 'Advancement value',
        'progress': 'Progress value',
        'achievement': 'Achievement value',
        'accomplishment': 'Accomplishment value',
        'success': 'Success value',
        'completion': 'Completion value',
        'fulfillment': 'Fulfillment value',
        'realization': 'Realization value',
        'attainment': 'Attainment value',
        'acquisition': 'Acquisition value',
        'obtainment': 'Obtainment value',
        'procurement': 'Procurement value',
        'purchase': 'Purchase value',
        'acquisition': 'Acquisition value',
        'obtainment': 'Obtainment value',
        'procurement': 'Procurement value',
        'purchase': 'Purchase value',
        'transaction': 'Transaction value',
        'exchange': 'Exchange value',
        'transfer': 'Transfer value',
        'movement': 'Movement value',
        'flow': 'Flow value',
        'circulation': 'Circulation value',
        'distribution': 'Distribution value',
        'allocation': 'Allocation value',
        'assignment': 'Assignment value',
        'designation': 'Designation value',
        'appointment': 'Appointment value',
        'nomination': 'Nomination value',
        'selection': 'Selection value',
        'election': 'Election value',
        'choice': 'Choice value',
        'decision': 'Decision value',
        'determination': 'Determination value',
        'resolution': 'Resolution value',
        'conclusion': 'Conclusion value',
        'judgment': 'Judgment value',
        'verdict': 'Verdict value',
        'ruling': 'Ruling value',
        'decree': 'Decree value',
        'order': 'Order value',
        'command': 'Command value',
        'instruction': 'Instruction value',
        'direction': 'Direction value',
        'guidance': 'Guidance value',
        'advice': 'Advice value',
        'counsel': 'Counsel value',
        'recommendation': 'Recommendation value',
        'suggestion': 'Suggestion value',
        'proposal': 'Proposal value',
        'offer': 'Offer value',
        'bid': 'Bid value',
        'tender': 'Tender value',
        'proposition': 'Proposition value',
        'submission': 'Submission value',
        'presentation': 'Presentation value',
        'demonstration': 'Demonstration value',
        'exhibition': 'Exhibition value',
        'display': 'Display value',
        'show': 'Show value',
        'performance': 'Performance value',
        'presentation': 'Presentation value',
        'demonstration': 'Demonstration value',
        'exhibition': 'Exhibition value',
        'display': 'Display value',
        'show': 'Show value',
        'performance': 'Performance value',
        'execution': 'Execution value',
        'implementation': 'Implementation value',
        'realization': 'Realization value',
        'achievement': 'Achievement value',
        'accomplishment': 'Accomplishment value',
        'attainment': 'Attainment value',
        'fulfillment': 'Fulfillment value',
        'completion': 'Completion value',
        'conclusion': 'Conclusion value',
        'finish': 'Finish value',
        'end': 'End value',
        'termination': 'Termination value',
        'cessation': 'Cessation value',
        'closure': 'Closure value',
        'shutdown': 'Shutdown value',
        'halt': 'Halt value',
        'stop': 'Stop value',
        'pause': 'Pause value',
        'break': 'Break value',
        'interruption': 'Interruption value',
        'disruption': 'Disruption value',
        'disturbance': 'Disturbance value',
        'interference': 'Interference value',
        'obstruction': 'Obstruction value',
        'hindrance': 'Hindrance value',
        'impediment': 'Impediment value',
        'barrier': 'Barrier value',
        'obstacle': 'Obstacle value',
        'challenge': 'Challenge value',
        'difficulty': 'Difficulty value',
        'problem': 'Problem value',
        'issue': 'Issue value',
        'concern': 'Concern value',
        'worry': 'Worry value',
        'anxiety': 'Anxiety value',
        'fear': 'Fear value',
        'dread': 'Dread value',
        'terror': 'Terror value',
        'horror': 'Horror value',
        'alarm': 'Alarm value',
        'panic': 'Panic value',
        'fright': 'Fright value',
        'scare': 'Scare value',
        'shock': 'Shock value',
        'surprise': 'Surprise value',
        'astonishment': 'Astonishment value',
        'amazement': 'Amazement value',
        'wonder': 'Wonder value',
        'awe': 'Awe value',
        'admiration': 'Admiration value',
        'respect': 'Respect value',
        'esteem': 'Esteem value',
        'regard': 'Regard value',
        'consideration': 'Consideration value',
        'attention': 'Attention value',
        'focus': 'Focus value',
        'concentration': 'Concentration value',
        'dedication': 'Dedication value',
        'commitment': 'Commitment value',
        'devotion': 'Devotion value',
        'loyalty': 'Loyalty value',
        'faithfulness': 'Faithfulness value',
        'allegiance': 'Allegiance value',
        'fidelity': 'Fidelity value',
        'constancy': 'Constancy value',
        'steadfastness': 'Steadfastness value',
        'resolve': 'Resolve value',
        'determination': 'Determination value',
        'perseverance': 'Perseverance value',
        'persistence': 'Persistence value',
        'tenacity': 'Tenacity value',
        'grit': 'Grit value',
        'resolve': 'Resolve value',
        'firmness': 'Firmness value',
        'strength': 'Strength value',
        'power': 'Power value',
        'force': 'Force value',
        'energy': 'Energy value',
        'vigor': 'Vigor value',
        'vitality': 'Vitality value',
        'liveliness': 'Liveliness value',
        'animation': 'Animation value',
        'spirit': 'Spirit value',
        'life': 'Life value',
        'existence': 'Existence value',
        'being': 'Being value',
        'entity': 'Entity value',
        'thing': 'Thing value',
        'object': 'Object value',
        'item': 'Item value',
        'article': 'Article value',
        'piece': 'Piece value',
        'part': 'Part value',
        'component': 'Component value',
        'element': 'Element value',
        'factor': 'Factor value',
        'aspect': 'Aspect value',
        'feature': 'Feature value',
        'characteristic': 'Characteristic value',
        'attribute': 'Attribute value',
        'property': 'Property value',
        'quality': 'Quality value',
        'trait': 'Trait value',
        'mark': 'Mark value',
        'sign': 'Sign value',
        'symbol': 'Symbol value',
        'indication': 'Indication value',
        'indicator': 'Indicator value',
        'signal': 'Signal value',
        'hint': 'Hint value',
        'clue': 'Clue value',
        'evidence': 'Evidence value',
        'proof': 'Proof value',
        'testimony': 'Testimony value',
        'witness': 'Witness value',
        'observation': 'Observation value',
        'perception': 'Perception value',
        'awareness': 'Awareness value',
        'consciousness': 'Consciousness value',
        'cognition': 'Cognition value',
        'knowledge': 'Knowledge value',
        'understanding': 'Understanding value',
        'comprehension': 'Comprehension value',
        'grasp': 'Grasp value',
        'apprehension': 'Apprehension value',
        'realization': 'Realization value',
        'recognition': 'Recognition value',
        'acknowledgment': 'Acknowledgment value',
        'admission': 'Admission value',
        'confession': 'Confession value',
        'avowal': 'Avowal value',
        'declaration': 'Declaration value',
        'statement': 'Statement value',
        'assertion': 'Assertion value',
        'affirmation': 'Affirmation value',
        'proclamation': 'Proclamation value',
        'announcement': 'Announcement value',
        'notification': 'Notification value',
        'communication': 'Communication value',
        'message': 'Message value',
        'information': 'Information value',
        'data': 'Data value',
        'content': 'Content value',
        'material': 'Material value',
        'substance': 'Substance value',
        'matter': 'Matter value',
        'stuff': 'Stuff value',
        'thing': 'Thing value',
        'object': 'Object value',
        'item': 'Item value',
        'article': 'Article value',
        'piece': 'Piece value',
        'part': 'Part value',
        'component': 'Component value',
        'element': 'Element value',
        'factor': 'Factor value',
        'aspect': 'Aspect value',
        'feature': 'Feature value',
        'characteristic': 'Characteristic value',
        'attribute': 'Attribute value',
        'property': 'Property value',
        'quality': 'Quality value',
        'trait': 'Trait value',
        'mark': 'Mark value',
        'sign': 'Sign value',
        'symbol': 'Symbol value',
        'indication': 'Indication value',
        'indicator': 'Indicator value',
        'signal': 'Signal value',
        'hint': 'Hint value',
        'clue': 'Clue value',
        'evidence': 'Evidence value',
        'proof': 'Proof value',
        'testimony': 'Testimony value',
        'witness': 'Witness value',
        'observation': 'Observation value',
        'perception': 'Perception value',
        'awareness': 'Awareness value',
        'consciousness': 'Consciousness value',
        'cognition': 'Cognition value',
        'knowledge': 'Knowledge value',
        'understanding': 'Understanding value',
        'comprehension': 'Comprehension value',
        'grasp': 'Grasp value',
        'apprehension': 'Apprehension value',
        'realization': 'Realization value',
        'recognition': 'Recognition value',
        'acknowledgment': 'Acknowledgment value',
        'admission': 'Admission value',
        'confession': 'Confession value',
        'avowal': 'Avowal value',
        'declaration': 'Declaration value',
        'statement': 'Statement value',
        'assertion': 'Assertion value',
        'affirmation': 'Affirmation value',
        'proclamation': 'Proclamation value',
        'announcement': 'Announcement value',
        'notification': 'Notification value',
        'communication': 'Communication value',
        'message': 'Message value',
        'information': 'Information value',
        'data': 'Data value',
        'content': 'Content value',
        'material': 'Material value',
        'substance': 'Substance value',
        'matter': 'Matter value',
        'stuff': 'Stuff value'
    }

    # Find matching patterns in column name
    column_lower = column_name.lower()
    for pattern, desc in descriptions.items():
        if pattern in column_lower:
            return desc

    # Fallback descriptions based on data type
    if data_type == "uuid":
        return "Unique identifier"
    elif data_type == "timestamp":
        return "Timestamp value"
    elif data_type == "categorical":
        return "Categorical classification"
    elif data_type == "boolean":
        return "Boolean flag"
    elif data_type == "int":
        return "Integer value"
    elif data_type == "float":
        return "Floating point value"
    elif data_type == "json_array":
        return "JSON array data"
    else:
        return "Text value"

def scan_csv_files(directory_path: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Scans all CSV files in a directory and generates a comprehensive data dictionary.

    Args:
        directory_path: Path to directory containing CSV files

    Returns:
        Dictionary containing data dictionary structure
    """
    data_dict = {}
    directory = Path(directory_path)

    # Ensure directory exists
    if not directory.exists():
        raise FileNotFoundError(f"Directory {directory_path} does not exist")

    # Process each CSV file
    for csv_file in directory.glob("*.csv"):
        try:
            # Extract table name from filename (remove timestamp and extension)
            table_name = csv_file.stem
            if "_" in table_name:
                # Remove timestamp part (format: scenario_timestamp_table)
                parts = table_name.split("_")
                if len(parts) >= 3:
                    table_name = "_".join(parts[-1:])  # Take last part as table name

            print(f"Processing {csv_file.name} as table: {table_name}")

            # Read CSV file with type inference
            df = pd.read_csv(csv_file, nrows=100)  # Sample first 100 rows for efficiency

            table_dict = {}

            # Analyze each column
            for column_name in df.columns:
                series = df[column_name]
                data_type = infer_data_type(series)
                description = generate_description(column_name, data_type, series)

                column_info: Dict[str, Union[str, bool]] = {
                    "type": data_type,
                    "desc": description
                }

                # Add "new": true for columns that might be new additions
                # This is based on the example format where some columns have this flag
                if "new" in column_name.lower() or "additional" in column_name.lower():
                    column_info["new"] = True

                table_dict[column_name] = column_info

            data_dict[table_name] = table_dict

        except Exception as e:
            print(f"⚠️  Error processing {csv_file.name}: {e}")
            continue

    return data_dict

def save_data_dictionary(data_dict: Dict, output_path: str):
    """
    Saves the data dictionary to a JSON file with proper formatting.

    Args:
        data_dict: Data dictionary to save
        output_path: Path to save the JSON file
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(data_dict, f, indent=4)
        print(f"📁 Data dictionary saved to {output_path}")
    except Exception as e:
        print(f"❌ Error saving data dictionary: {e}")
        raise

def generate_data_dictionary(directory_path: str, output_path: Optional[str] = None):
    """
    Main function to generate data dictionary from CSV files in a directory.

    Args:
        directory_path: Path to directory containing CSV files
        output_path: Optional path to save JSON file (default: data_dictionary.json in same directory)
    """
    print("🔍 Scanning CSV files and generating data dictionary...")

    # Generate data dictionary
    data_dict = scan_csv_files(directory_path)

    # Set default output path if not provided
    if output_path is None:
        output_path = os.path.join(directory_path, "data_dictionary.json")

    # Save the data dictionary
    save_data_dictionary(data_dict, output_path)

    print(f"✅ Data dictionary generation complete!")
    print(f"📊 Found {len(data_dict)} tables with column information")
    return data_dict

if __name__ == "__main__":
    # Example usage
    flash_sale_dir = "data/flash_sale"
    generate_data_dictionary(flash_sale_dir)