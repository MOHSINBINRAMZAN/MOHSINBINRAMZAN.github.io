#!/usr/bin/env python3
"""
QueryMancer Demo Script

Demonstrates the automated mapping generation system.
Since we can't connect to actual SQL Server databases in this environment,
this script shows how the system would work and generates sample mappings.
"""

import json
import os
import sys
from datetime import datetime

# Add the querymancer package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from querymancer import (
    config_manager,
    create_sample_mapping,
    convert_technical_to_natural,
    create_search_terms,
    format_field_description,
    generate_synonyms
)


def demo_text_processing():
    """Demonstrate text processing utilities."""
    print("=== QueryMancer Text Processing Demo ===\n")
    
    # Test technical name conversion
    technical_names = [
        "tbl_Customer_Orders",
        "CustomerID", 
        "OrderDate",
        "ProductName",
        "UnitPrice",
        "IsActive",
        "CreatedDateTime",
        "user_profile_settings"
    ]
    
    print("Technical Name -> Natural Language Conversion:")
    print("-" * 50)
    for name in technical_names:
        natural = convert_technical_to_natural(name)
        print(f"{name:25} -> {natural}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Test search term generation
    print("Search Terms Generation:")
    print("-" * 30)
    test_terms = ["CustomerID", "OrderDate", "ProductName"]
    for term in test_terms:
        search_terms = create_search_terms(term)
        print(f"{term}: {', '.join(search_terms[:6])}")  # Show first 6 terms
    
    print("\n" + "=" * 60 + "\n")
    
    # Test field description formatting
    print("Field Description Formatting:")
    print("-" * 35)
    test_fields = [
        ("Customers", "CustomerID", "int"),
        ("Orders", "OrderDate", "datetime"),
        ("Products", "UnitPrice", "decimal"),
        ("Users", "IsActive", "bit")
    ]
    
    for table, column, data_type in test_fields:
        description = format_field_description(table, column, data_type)
        print(f"{table}.{column}: {description}")


def demo_sample_mapping():
    """Demonstrate sample mapping generation."""
    print("=== Sample Mapping Generation ===\n")
    
    # Generate sample mapping
    sample_mapping = create_sample_mapping()
    
    # Display mapping summary
    client_info = sample_mapping["client_info"]
    print(f"Client: {client_info['client_name']}")
    print(f"Database: {client_info['database']}")
    print(f"Total Tables: {client_info['total_tables']}")
    print(f"Total Columns: {client_info['total_columns']}")
    print(f"Generated: {client_info['generation_date']}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Display table information
    print("Table Mappings:")
    print("-" * 20)
    for table_name, table_info in sample_mapping["tables"].items():
        print(f"\nTable: {table_name}")
        print(f"  Natural Name: {table_info['natural_name']}")
        print(f"  Description: {table_info['description']}")
        print(f"  Search Terms: {', '.join(table_info['search_terms'][:4])}")
        print(f"  Columns: {len(table_info['columns'])}")
        
        # Show first few columns
        for i, (col_name, col_info) in enumerate(table_info['columns'].items()):
            if i < 3:  # Show first 3 columns
                print(f"    {col_name}: {col_info['description']}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Display search index sample
    print("Search Index (sample entries):")
    print("-" * 35)
    search_index = sample_mapping["search_index"]
    for i, (term, paths) in enumerate(search_index.items()):
        if i < 5:  # Show first 5 entries
            print(f"  '{term}': {paths}")
    
    return sample_mapping


def save_sample_files():
    """Save sample mapping files."""
    print("=== Saving Sample Files ===\n")
    
    # Create mappings directory
    mappings_dir = os.path.join(os.path.dirname(__file__), "querymancer", "mappings")
    os.makedirs(mappings_dir, exist_ok=True)
    
    # Generate and save sample mapping
    sample_mapping = create_sample_mapping()
    
    # Save sample mapping
    sample_file = os.path.join(mappings_dir, "sample_client_table_mapping.json")
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_mapping, f, indent=2, ensure_ascii=False)
    
    print(f"Sample mapping saved to: {sample_file}")
    
    # Create a comprehensive example mapping
    comprehensive_mapping = create_comprehensive_example()
    
    comprehensive_file = os.path.join(mappings_dir, "comprehensive_example_mapping.json")
    with open(comprehensive_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_mapping, f, indent=2, ensure_ascii=False)
    
    print(f"Comprehensive example saved to: {comprehensive_file}")
    
    return sample_file, comprehensive_file


def create_comprehensive_example():
    """Create a more comprehensive example mapping."""
    return {
        "client_info": {
            "client_key": "retail_company",
            "client_name": "Retail Company Inc.",
            "database": "RetailDB",
            "generation_date": datetime.now().isoformat(),
            "total_tables": 5,
            "total_columns": 25
        },
        "tables": {
            "dbo.Customers": {
                "technical_name": "dbo.Customers",
                "natural_name": "Customers",
                "description": "Customer information and details",
                "search_terms": ["customers", "customer", "client", "user", "person"],
                "synonyms": ["client", "user", "person"],
                "columns": {
                    "CustomerID": {
                        "technical_name": "CustomerID",
                        "natural_name": "Customer ID",
                        "description": "Unique customer identifier (number)",
                        "data_type": "int",
                        "category": "identifier",
                        "examples": ["find customer by id", "customer number", "customer key"]
                    },
                    "FirstName": {
                        "technical_name": "FirstName", 
                        "natural_name": "First Name",
                        "description": "Customer's first name (text)",
                        "data_type": "varchar",
                        "category": "name",
                        "examples": ["customer first name", "given name"]
                    },
                    "LastName": {
                        "technical_name": "LastName",
                        "natural_name": "Last Name", 
                        "description": "Customer's last name (text)",
                        "data_type": "varchar",
                        "category": "name",
                        "examples": ["customer last name", "family name", "surname"]
                    },
                    "Email": {
                        "technical_name": "Email",
                        "natural_name": "Email",
                        "description": "Customer's email address (text)",
                        "data_type": "varchar",
                        "category": "email",
                        "examples": ["customer email", "email address", "contact email"]
                    },
                    "CreatedDate": {
                        "technical_name": "CreatedDate",
                        "natural_name": "Created Date",
                        "description": "When customer was created (date/time)",
                        "data_type": "datetime",
                        "category": "datetime",
                        "examples": ["when customer was added", "customer creation date", "registration date"]
                    }
                },
                "primary_keys": ["CustomerID"],
                "foreign_keys": [],
                "row_count": 15000
            },
            "dbo.Orders": {
                "technical_name": "dbo.Orders",
                "natural_name": "Orders",
                "description": "Customer orders and purchases",
                "search_terms": ["orders", "order", "purchase", "transaction", "sale"],
                "synonyms": ["purchase", "transaction", "sale"],
                "columns": {
                    "OrderID": {
                        "technical_name": "OrderID",
                        "natural_name": "Order ID",
                        "description": "Unique order identifier (number)",
                        "data_type": "int",
                        "category": "identifier",
                        "examples": ["find order by id", "order number"]
                    },
                    "CustomerID": {
                        "technical_name": "CustomerID",
                        "natural_name": "Customer ID",
                        "description": "Customer who placed the order (number)",
                        "data_type": "int",
                        "category": "reference",
                        "examples": ["which customer placed order", "order customer"]
                    },
                    "OrderDate": {
                        "technical_name": "OrderDate",
                        "natural_name": "Order Date",
                        "description": "When the order was placed (date/time)",
                        "data_type": "datetime",
                        "category": "datetime",
                        "examples": ["when was order placed", "order date", "purchase date"]
                    },
                    "TotalAmount": {
                        "technical_name": "TotalAmount",
                        "natural_name": "Total Amount",
                        "description": "Total order amount (money)",
                        "data_type": "decimal",
                        "category": "money",
                        "examples": ["order total", "how much was order", "order amount", "order value"]
                    }
                },
                "primary_keys": ["OrderID"],
                "foreign_keys": [
                    {
                        "column": "CustomerID",
                        "referenced_table": "dbo.Customers",
                        "referenced_column": "CustomerID"
                    }
                ],
                "row_count": 45000
            },
            "dbo.Products": {
                "technical_name": "dbo.Products",
                "natural_name": "Products",
                "description": "Product catalog and information",
                "search_terms": ["products", "product", "item", "goods", "merchandise"],
                "synonyms": ["item", "goods", "service", "merchandise"],
                "columns": {
                    "ProductID": {
                        "technical_name": "ProductID",
                        "natural_name": "Product ID",
                        "description": "Unique product identifier (number)",
                        "data_type": "int",
                        "category": "identifier",
                        "examples": ["find product by id", "product number"]
                    },
                    "ProductName": {
                        "technical_name": "ProductName",
                        "natural_name": "Product Name",
                        "description": "Name of the product (text)",
                        "data_type": "varchar",
                        "category": "name",
                        "examples": ["product name", "what is the product called"]
                    },
                    "UnitPrice": {
                        "technical_name": "UnitPrice",
                        "natural_name": "Unit Price",
                        "description": "Price per unit of product (money)",
                        "data_type": "decimal",
                        "category": "money",
                        "examples": ["product price", "how much does it cost", "unit price"]
                    },
                    "Category": {
                        "technical_name": "Category",
                        "natural_name": "Category",
                        "description": "Product category (text)",
                        "data_type": "varchar",
                        "category": "text",
                        "examples": ["product category", "what type of product"]
                    }
                },
                "primary_keys": ["ProductID"],
                "foreign_keys": [],
                "row_count": 2500
            }
        },
        "search_index": {
            "customer": ["dbo.Customers", "dbo.Orders.CustomerID"],
            "order": ["dbo.Orders"],
            "product": ["dbo.Products"],
            "name": ["dbo.Customers.FirstName", "dbo.Customers.LastName", "dbo.Products.ProductName"],
            "price": ["dbo.Products.UnitPrice"],
            "amount": ["dbo.Orders.TotalAmount"],
            "date": ["dbo.Customers.CreatedDate", "dbo.Orders.OrderDate"],
            "email": ["dbo.Customers.Email"],
            "category": ["dbo.Products.Category"]
        },
        "metadata": {
            "version": "1.0",
            "generator": "QueryMancer Mapping Generator",
            "schema_extraction_date": datetime.now().isoformat()
        }
    }


def demo_configuration():
    """Demonstrate configuration management."""
    print("=== Configuration Management Demo ===\n")
    
    # Show configured clients
    clients = config_manager.get_all_clients()
    print(f"Configured clients: {clients}")
    
    # Show client configurations (without sensitive data)
    for client_key in clients:
        config = config_manager.get_database_config(client_key)
        if config:
            print(f"\nClient: {client_key}")
            print(f"  Name: {config.client_name}")
            print(f"  Database: {config.database}")
            print(f"  Server: {config.server}")
            print(f"  Port: {config.port}")
            print(f"  Trusted Connection: {config.trusted_connection}")


def main():
    """Main demo function."""
    print("QueryMancer Automated Mapping Generation System")
    print("=" * 55)
    print("This demo shows how the system processes database schemas")
    print("and generates natural language mappings automatically.\n")
    
    # Run demonstrations
    demo_text_processing()
    demo_sample_mapping() 
    demo_configuration()
    
    # Save sample files
    sample_file, comprehensive_file = save_sample_files()
    
    print("\n" + "=" * 55)
    print("Demo completed successfully!")
    print("\nGenerated files:")
    print(f"  - {sample_file}")
    print(f"  - {comprehensive_file}")
    print("\nTo use the system with real databases:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure database connections in config.py")
    print("3. Run: python -c 'from querymancer import generate_mappings_for_all_clients; generate_mappings_for_all_clients()'")


if __name__ == "__main__":
    main()