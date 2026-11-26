# QueryMancer - Automated Database Schema Mapping Generator

An automated system that generates natural language mapping JSON files from SQL Server database schemas, eliminating the need to manually create mapping files for multiple client databases.

## Overview

QueryMancer solves the problem of manually creating JSON mapping files for 30+ client databases by:

1. **Automatically extracting** complete schema information from SQL Server databases
2. **Converting** technical database names to natural language terms
3. **Generating** comprehensive mappings with synonyms and search terms
4. **Supporting** multiple client databases through a configuration system

## Features

- **Schema Extraction**: Complete table and column metadata extraction from SQL Server
- **Natural Language Processing**: Automatic conversion of technical names to user-friendly terms
- **Synonym Generation**: Built-in synonym generation for better search coverage
- **Multi-Client Support**: Configuration management for multiple client databases
- **Search Index**: Optimized search index generation for quick term lookup
- **Comprehensive Mappings**: Rich metadata including data types, relationships, and examples

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your database connections in `querymancer/config.py` or using environment variables.

## Quick Start

### Running the Demo

```bash
python demo.py
```

This will demonstrate the text processing capabilities and generate sample mapping files.

### Generating Mappings for All Clients

```python
from querymancer import generate_mappings_for_all_clients

# Generate mappings for all configured clients
mappings = generate_mappings_for_all_clients()
```

### Generating Mapping for a Specific Client

```python
from querymancer import generate_mapping_for_client

# Generate mapping for a specific client
mapping = generate_mapping_for_client('client_a')
```

## Configuration

### Environment Variables

Configure database connections using environment variables:

```bash
# Client A Configuration
export CLIENT_A_SERVER="your-server.database.windows.net"
export CLIENT_A_DATABASE="ClientA_DB"
export CLIENT_A_USERNAME="your-username"
export CLIENT_A_PASSWORD="your-password"
export CLIENT_A_PORT="1433"
export CLIENT_A_TRUSTED="false"

# Client B Configuration
export CLIENT_B_SERVER="your-server.database.windows.net"
export CLIENT_B_DATABASE="ClientB_DB"
export CLIENT_B_USERNAME="your-username"
export CLIENT_B_PASSWORD="your-password"
```

### Programmatic Configuration

```python
from querymancer import config_manager, DatabaseConfig

# Add a new client configuration
config = DatabaseConfig(
    client_name="New Client",
    server="server.database.windows.net",
    database="NewClient_DB",
    username="username",
    password="password",
    port=1433
)

config_manager.add_database_config("new_client", config)
```

## Generated Mapping Structure

The system generates comprehensive JSON mappings with the following structure:

```json
{
  "client_info": {
    "client_key": "client_a",
    "client_name": "Client A",
    "database": "ClientA_DB",
    "generation_date": "2024-01-15T10:30:00",
    "total_tables": 15,
    "total_columns": 120
  },
  "tables": {
    "dbo.Customers": {
      "technical_name": "dbo.Customers",
      "natural_name": "Customers",
      "description": "Customer information and details",
      "search_terms": ["customers", "customer", "client", "user"],
      "synonyms": ["client", "user", "person"],
      "columns": {
        "CustomerID": {
          "technical_name": "CustomerID",
          "natural_name": "Customer ID",
          "description": "Unique customer identifier (number)",
          "data_type": "int",
          "search_terms": ["customer id", "id", "identifier"],
          "category": "identifier",
          "examples": ["find by customer id", "customer number"],
          "metadata": {
            "is_primary_key": true,
            "is_nullable": false,
            "max_length": null
          }
        }
      },
      "primary_keys": ["CustomerID"],
      "foreign_keys": [],
      "row_count": 15000
    }
  },
  "search_index": {
    "customer": ["dbo.Customers", "dbo.Orders.CustomerID"],
    "name": ["dbo.Customers.FirstName", "dbo.Customers.LastName"]
  }
}
```

## Text Processing Features

### Technical Name Conversion

```python
from querymancer import convert_technical_to_natural

# Convert snake_case and camelCase to natural language
convert_technical_to_natural("tbl_Customer_Orders")  # → "Customer Orders"
convert_technical_to_natural("CustomerID")           # → "Customer ID"
convert_technical_to_natural("IsActive")             # → "Is Active"
```

### Search Term Generation

```python
from querymancer import create_search_terms

# Generate comprehensive search terms
terms = create_search_terms("CustomerID")
# Returns: ["CustomerID", "Customer ID", "Customer", "ID", "identifier", "key", "number"]
```

### Synonym Generation

```python
from querymancer import generate_synonyms

# Generate synonyms for database terms
synonyms = generate_synonyms("customer")
# Returns: ["customer", "client", "user", "person"]
```

## Architecture

The system consists of four main modules:

### 1. `config.py` - Configuration Management
- Multi-client database configuration
- Environment variable support
- Connection string generation
- Secure credential handling

### 2. `schema_extractor.py` - Database Schema Extraction
- SQL Server connection management
- Complete table and column metadata extraction
- Primary key and foreign key detection
- Row count estimation
- Relationship mapping

### 3. `mapping_generator.py` - Mapping Generation
- Natural language conversion
- Synonym and search term generation
- Category classification
- Example query generation
- Search index optimization

### 4. `utils.py` - Text Processing Utilities
- Snake_case and camelCase conversion
- Text normalization
- Similarity calculation
- Meaningful word extraction
- Field description formatting

## Use Cases

### 1. Chatbot Natural Language Processing
The generated mappings enable chatbots to understand user queries like:
- "Show me customer names" → `SELECT CustomerName FROM dbo.Customers`
- "Find orders from last month" → `SELECT * FROM dbo.Orders WHERE OrderDate >= '2024-01-01'`

### 2. Business Intelligence Tools
Enable non-technical users to query databases using natural language terms instead of technical column names.

### 3. Data Discovery
Help users discover available data by browsing natural language descriptions of database contents.

### 4. API Documentation
Auto-generate user-friendly documentation for database APIs.

## Benefits

- **Eliminates Manual Work**: No more manually creating 30+ mapping files
- **Consistent Quality**: Standardized natural language conversion
- **Automatic Updates**: Regenerate mappings when schemas change
- **Rich Metadata**: Comprehensive information for advanced query processing
- **Scalable**: Easily add new clients and databases
- **Maintainable**: Clean, modular architecture

## Example Output

When you run the system, it generates mapping files like:
- `client_a_table_mapping.json`
- `client_b_table_mapping.json`
- `retail_company_table_mapping.json`

Each file contains complete natural language mappings for that client's database schema.

## Requirements

- Python 3.7+
- pyodbc (for SQL Server connectivity)
- SQL Server databases with appropriate permissions

## Development

### Running Tests
```bash
python -m pytest tests/  # When tests are added
```

### Code Style
```bash
black querymancer/
flake8 querymancer/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the demo script for usage examples
2. Review the generated sample mappings
3. Open an issue on GitHub

---

**QueryMancer** - Transforming database schemas into natural language, one mapping at a time.