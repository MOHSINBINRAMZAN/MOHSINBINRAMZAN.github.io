"""
QueryMancer - Automated Database Schema to Natural Language Mapping Generator

This package provides tools for automatically generating natural language mappings
from SQL Server database schemas, eliminating the need for manual mapping file creation.

Modules:
- config: Configuration management for multiple client databases
- schema_extractor: Database schema extraction from SQL Server
- mapping_generator: JSON mapping generation from schema information  
- utils: Text normalization and natural language processing utilities
"""

from .config import config_manager, ConfigManager, DatabaseConfig
from .schema_extractor import SchemaExtractor, extract_schema_for_client, extract_schema_for_all_clients
from .mapping_generator import MappingGenerator, generate_mapping_for_client, generate_mappings_for_all_clients, create_sample_mapping
from .utils import (
    normalize_text,
    snake_case_to_words,
    camel_case_to_words,
    generate_synonyms,
    extract_meaningful_words,
    calculate_similarity,
    convert_technical_to_natural,
    create_search_terms,
    format_field_description
)

__version__ = "1.0.0"
__author__ = "QueryMancer Team"
__email__ = "info@querymancer.com"

__all__ = [
    # Configuration
    'config_manager',
    'ConfigManager', 
    'DatabaseConfig',
    
    # Schema Extraction
    'SchemaExtractor',
    'extract_schema_for_client',
    'extract_schema_for_all_clients',
    
    # Mapping Generation
    'MappingGenerator',
    'generate_mapping_for_client', 
    'generate_mappings_for_all_clients',
    'create_sample_mapping',
    
    # Utilities
    'normalize_text',
    'snake_case_to_words',
    'camel_case_to_words',
    'generate_synonyms',
    'extract_meaningful_words',
    'calculate_similarity',
    'convert_technical_to_natural',
    'create_search_terms',
    'format_field_description'
]