"""
Mapping generation module for QueryMancer.
Generates comprehensive JSON mappings from database schema information.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from .schema_extractor import TableInfo, ColumnInfo, extract_schema_for_client, extract_schema_for_all_clients
from .utils import (
    convert_technical_to_natural, 
    create_search_terms, 
    format_field_description,
    generate_synonyms
)
from .config import config_manager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MappingGenerator:
    """Generates natural language mappings from database schema."""
    
    def __init__(self, client_key: str):
        """Initialize mapping generator for a specific client.
        
        Args:
            client_key: Client identifier
        """
        self.client_key = client_key
        self.config = config_manager.get_database_config(client_key)
        if not self.config:
            raise ValueError(f"No configuration found for client: {client_key}")
    
    def generate_table_mapping(self, table_info: TableInfo) -> Dict[str, Any]:
        """Generate mapping for a single table.
        
        Args:
            table_info: Table information object
            
        Returns:
            Dictionary containing table mapping
        """
        table_name = f"{table_info.schema}.{table_info.name}"
        natural_name = convert_technical_to_natural(table_info.name)
        
        # Generate search terms for the table
        search_terms = create_search_terms(table_info.name)
        
        # Generate column mappings
        columns = {}
        for column in table_info.columns:
            column_mapping = self.generate_column_mapping(table_info, column)
            columns[column.name] = column_mapping
        
        # Create table mapping
        table_mapping = {
            "technical_name": table_name,
            "natural_name": natural_name,
            "description": f"Data from the {natural_name} table",
            "search_terms": search_terms,
            "synonyms": generate_synonyms(table_info.name),
            "columns": columns,
            "primary_keys": table_info.primary_keys,
            "foreign_keys": table_info.foreign_keys,
            "row_count": table_info.row_count,
            "metadata": {
                "schema": table_info.schema,
                "table_name": table_info.name,
                "column_count": len(table_info.columns),
                "has_primary_key": len(table_info.primary_keys) > 0,
                "has_foreign_keys": len(table_info.foreign_keys) > 0
            }
        }
        
        return table_mapping
    
    def generate_column_mapping(self, table_info: TableInfo, column: ColumnInfo) -> Dict[str, Any]:
        """Generate mapping for a single column.
        
        Args:
            table_info: Table information
            column: Column information object
            
        Returns:
            Dictionary containing column mapping
        """
        natural_name = convert_technical_to_natural(column.name)
        description = format_field_description(table_info.name, column.name, column.data_type)
        search_terms = create_search_terms(column.name)
        
        # Determine column category based on name and type
        category = self.determine_column_category(column)
        
        # Generate examples based on column type and name
        examples = self.generate_column_examples(column)
        
        column_mapping = {
            "technical_name": column.name,
            "natural_name": natural_name,
            "description": description,
            "data_type": column.data_type,
            "search_terms": search_terms,
            "synonyms": generate_synonyms(column.name),
            "category": category,
            "examples": examples,
            "metadata": {
                "max_length": column.max_length,
                "is_nullable": column.is_nullable,
                "default_value": column.default_value,
                "is_primary_key": column.is_primary_key,
                "is_foreign_key": column.is_foreign_key,
                "referenced_table": column.referenced_table,
                "referenced_column": column.referenced_column
            }
        }
        
        return column_mapping
    
    def determine_column_category(self, column: ColumnInfo) -> str:
        """Determine the category of a column based on its name and type.
        
        Args:
            column: Column information
            
        Returns:
            Category string
        """
        name_lower = column.name.lower()
        type_lower = column.data_type.lower()
        
        # Primary key category
        if column.is_primary_key:
            return "identifier"
        
        # Foreign key category
        if column.is_foreign_key:
            return "reference"
        
        # Date/time category
        if any(term in name_lower for term in ['date', 'time', 'created', 'modified', 'updated']) or \
           any(term in type_lower for term in ['date', 'time', 'timestamp']):
            return "datetime"
        
        # Numeric category
        if any(term in type_lower for term in ['int', 'decimal', 'numeric', 'float', 'money']):
            if any(term in name_lower for term in ['price', 'cost', 'amount', 'value', 'total']):
                return "money"
            elif any(term in name_lower for term in ['quantity', 'count', 'number']):
                return "quantity"
            else:
                return "numeric"
        
        # Boolean category
        if any(term in type_lower for term in ['bit', 'bool']) or \
           any(term in name_lower for term in ['is_', 'has_', 'active', 'enabled']):
            return "boolean"
        
        # Text categories
        if any(term in type_lower for term in ['varchar', 'text', 'char']):
            if any(term in name_lower for term in ['email', 'mail']):
                return "email"
            elif any(term in name_lower for term in ['phone', 'telephone', 'mobile']):
                return "phone"
            elif any(term in name_lower for term in ['address', 'street', 'city', 'state', 'zip']):
                return "address"
            elif any(term in name_lower for term in ['name', 'title', 'label']):
                return "name"
            elif any(term in name_lower for term in ['description', 'notes', 'comment']):
                return "description"
            else:
                return "text"
        
        # Default category
        return "general"
    
    def generate_column_examples(self, column: ColumnInfo) -> List[str]:
        """Generate example queries for a column.
        
        Args:
            column: Column information
            
        Returns:
            List of example query phrases
        """
        natural_name = convert_technical_to_natural(column.name)
        name_lower = column.name.lower()
        
        examples = []
        
        # Add basic examples
        examples.append(f"show me {natural_name}")
        examples.append(f"what is the {natural_name}")
        examples.append(f"find {natural_name}")
        
        # Add type-specific examples
        if column.is_primary_key:
            examples.extend([
                f"find by {natural_name}",
                f"get record with {natural_name}",
                f"lookup {natural_name}"
            ])
        
        elif 'date' in name_lower or 'time' in name_lower:
            examples.extend([
                f"when was {natural_name}",
                f"show {natural_name} after",
                f"filter by {natural_name}"
            ])
        
        elif any(term in name_lower for term in ['price', 'cost', 'amount', 'value', 'total']):
            examples.extend([
                f"how much is {natural_name}",
                f"total {natural_name}",
                f"average {natural_name}",
                f"{natural_name} greater than",
                f"{natural_name} less than"
            ])
        
        elif any(term in name_lower for term in ['quantity', 'count', 'number']):
            examples.extend([
                f"how many {natural_name}",
                f"count of {natural_name}",
                f"sum of {natural_name}"
            ])
        
        elif any(term in name_lower for term in ['name', 'title']):
            examples.extend([
                f"find by {natural_name}",
                f"search {natural_name}",
                f"{natural_name} contains",
                f"{natural_name} starts with"
            ])
        
        elif any(term in name_lower for term in ['status', 'state', 'type', 'category']):
            examples.extend([
                f"where {natural_name} is",
                f"filter by {natural_name}",
                f"group by {natural_name}"
            ])
        
        # Add synonyms as examples
        synonyms = generate_synonyms(column.name)
        for synonym in synonyms[:3]:  # Limit to first 3 synonyms
            if synonym != column.name:
                examples.append(f"show me {synonym}")
        
        return examples[:10]  # Limit to 10 examples
    
    def generate_database_mapping(self, schema_info: Dict[str, TableInfo]) -> Dict[str, Any]:
        """Generate complete mapping for a database.
        
        Args:
            schema_info: Dictionary of table information
            
        Returns:
            Complete database mapping
        """
        if not schema_info:
            logger.warning(f"No schema information provided for client {self.client_key}")
            return {}
        
        # Generate table mappings
        tables = {}
        for table_name, table_info in schema_info.items():
            logger.info(f"Generating mapping for table: {table_name}")
            table_mapping = self.generate_table_mapping(table_info)
            tables[table_name] = table_mapping
        
        # Generate global search index
        search_index = self.generate_search_index(schema_info)
        
        # Create complete mapping
        mapping = {
            "client_info": {
                "client_key": self.client_key,
                "client_name": self.config.client_name,
                "database": self.config.database,
                "generation_date": datetime.now().isoformat(),
                "total_tables": len(tables),
                "total_columns": sum(len(table["columns"]) for table in tables.values())
            },
            "tables": tables,
            "search_index": search_index,
            "metadata": {
                "version": "1.0",
                "generator": "QueryMancer Mapping Generator",
                "schema_extraction_date": datetime.now().isoformat()
            }
        }
        
        return mapping
    
    def generate_search_index(self, schema_info: Dict[str, TableInfo]) -> Dict[str, List[str]]:
        """Generate a search index for quick term lookup.
        
        Args:
            schema_info: Dictionary of table information
            
        Returns:
            Search index mapping terms to table.column paths
        """
        search_index = {}
        
        for table_name, table_info in schema_info.items():
            # Add table-level search terms
            table_search_terms = create_search_terms(table_info.name)
            for term in table_search_terms:
                term_lower = term.lower()
                if term_lower not in search_index:
                    search_index[term_lower] = []
                search_index[term_lower].append(table_name)
            
            # Add column-level search terms
            for column in table_info.columns:
                column_search_terms = create_search_terms(column.name)
                column_path = f"{table_name}.{column.name}"
                
                for term in column_search_terms:
                    term_lower = term.lower()
                    if term_lower not in search_index:
                        search_index[term_lower] = []
                    if column_path not in search_index[term_lower]:
                        search_index[term_lower].append(column_path)
        
        return search_index
    
    def save_mapping_to_file(self, mapping: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Save mapping to JSON file.
        
        Args:
            mapping: Mapping dictionary to save
            output_path: Optional custom output path
            
        Returns:
            Path to saved file
        """
        if not output_path:
            output_dir = os.path.join(os.path.dirname(__file__), "mappings")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{self.client_key}_table_mapping.json")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Mapping saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving mapping to file: {e}")
            raise


def generate_mapping_for_client(client_key: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Generate mapping for a specific client.
    
    Args:
        client_key: Client identifier
        output_path: Optional custom output path
        
    Returns:
        Generated mapping dictionary
    """
    try:
        logger.info(f"Generating mapping for client: {client_key}")
        
        # Extract schema information
        schema_info = extract_schema_for_client(client_key)
        if not schema_info:
            logger.error(f"No schema information extracted for client: {client_key}")
            return {}
        
        # Generate mapping
        generator = MappingGenerator(client_key)
        mapping = generator.generate_database_mapping(schema_info)
        
        # Save to file
        if mapping:
            generator.save_mapping_to_file(mapping, output_path)
        
        logger.info(f"Successfully generated mapping for client {client_key}")
        return mapping
        
    except Exception as e:
        logger.error(f"Error generating mapping for client {client_key}: {e}")
        return {}


def generate_mappings_for_all_clients(output_dir: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Generate mappings for all configured clients.
    
    Args:
        output_dir: Optional custom output directory
        
    Returns:
        Dictionary mapping client keys to their mappings
    """
    all_mappings = {}
    clients = config_manager.get_all_clients()
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    for client_key in clients:
        logger.info(f"Generating mapping for client: {client_key}")
        
        output_path = None
        if output_dir:
            output_path = os.path.join(output_dir, f"{client_key}_table_mapping.json")
        
        mapping = generate_mapping_for_client(client_key, output_path)
        if mapping:
            all_mappings[client_key] = mapping
            logger.info(f"Successfully generated mapping for client {client_key}")
        else:
            logger.warning(f"Failed to generate mapping for client: {client_key}")
    
    logger.info(f"Generated mappings for {len(all_mappings)} out of {len(clients)} clients")
    return all_mappings


def create_sample_mapping() -> Dict[str, Any]:
    """Create a sample mapping structure for demonstration purposes.
    
    Returns:
        Sample mapping dictionary
    """
    sample_mapping = {
        "client_info": {
            "client_key": "sample_client",
            "client_name": "Sample Client",
            "database": "SampleDB",
            "generation_date": datetime.now().isoformat(),
            "total_tables": 2,
            "total_columns": 8
        },
        "tables": {
            "dbo.Customers": {
                "technical_name": "dbo.Customers",
                "natural_name": "Customers",
                "description": "Data from the Customers table",
                "search_terms": ["customers", "customer", "client", "user"],
                "synonyms": ["client", "user", "person"],
                "columns": {
                    "CustomerID": {
                        "technical_name": "CustomerID",
                        "natural_name": "Customer ID",
                        "description": "Customer ID from Customers (number)",
                        "data_type": "int",
                        "search_terms": ["customer id", "id", "identifier", "key"],
                        "synonyms": ["identifier", "key", "number"],
                        "category": "identifier",
                        "examples": ["find by customer id", "get customer id", "show customer id"],
                        "metadata": {
                            "max_length": None,
                            "is_nullable": False,
                            "default_value": None,
                            "is_primary_key": True,
                            "is_foreign_key": False,
                            "referenced_table": None,
                            "referenced_column": None
                        }
                    },
                    "CustomerName": {
                        "technical_name": "CustomerName",
                        "natural_name": "Customer Name",
                        "description": "Customer Name from Customers (text)",
                        "data_type": "varchar",
                        "search_terms": ["customer name", "name", "title"],
                        "synonyms": ["title", "label", "description"],
                        "category": "name",
                        "examples": ["find by customer name", "search customer name", "show customer name"],
                        "metadata": {
                            "max_length": 100,
                            "is_nullable": False,
                            "default_value": None,
                            "is_primary_key": False,
                            "is_foreign_key": False,
                            "referenced_table": None,
                            "referenced_column": None
                        }
                    }
                },
                "primary_keys": ["CustomerID"],
                "foreign_keys": [],
                "row_count": 1000,
                "metadata": {
                    "schema": "dbo",
                    "table_name": "Customers",
                    "column_count": 2,
                    "has_primary_key": True,
                    "has_foreign_keys": False
                }
            }
        },
        "search_index": {
            "customer": ["dbo.Customers", "dbo.Customers.CustomerID", "dbo.Customers.CustomerName"],
            "name": ["dbo.Customers.CustomerName"],
            "id": ["dbo.Customers.CustomerID"]
        },
        "metadata": {
            "version": "1.0",
            "generator": "QueryMancer Mapping Generator",
            "schema_extraction_date": datetime.now().isoformat()
        }
    }
    
    return sample_mapping