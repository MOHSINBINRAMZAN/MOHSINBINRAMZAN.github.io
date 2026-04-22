"""
Utility functions for text normalization and processing in QueryMancer.
Handles conversion between technical database names and natural language terms.
"""

import re
from typing import List, Dict, Set
from difflib import SequenceMatcher


def normalize_text(text: str) -> str:
    """Normalize text by removing special characters and converting to lowercase.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Remove special characters and replace with spaces
    normalized = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Convert to lowercase and remove extra spaces
    normalized = ' '.join(normalized.lower().split())
    
    return normalized


def snake_case_to_words(snake_case: str) -> str:
    """Convert snake_case to separate words.
    
    Args:
        snake_case: Text in snake_case format
        
    Returns:
        Space-separated words
    """
    if not snake_case:
        return ""
    
    # Replace underscores with spaces
    words = snake_case.replace('_', ' ')
    
    # Handle camelCase within the words
    words = camel_case_to_words(words)
    
    return words.strip()


def camel_case_to_words(camel_case: str) -> str:
    """Convert camelCase to separate words.
    
    Args:
        camel_case: Text in camelCase format
        
    Returns:
        Space-separated words
    """
    if not camel_case:
        return ""
    
    # Handle specific patterns first
    # Replace common abbreviations like ID, API, URL at word boundaries
    text = camel_case
    
    # Insert space before uppercase letters, but handle consecutive uppercase letters specially
    # This regex handles patterns like "CustomerID" -> "Customer ID" and "XMLHttpRequest" -> "XML Http Request"
    result = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    result = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', result)
    
    return result


def generate_synonyms(word: str) -> List[str]:
    """Generate common synonyms for database-related terms.
    
    Args:
        word: Input word to generate synonyms for
        
    Returns:
        List of synonyms including the original word
    """
    # Common database term mappings
    synonym_map = {
        'id': ['identifier', 'key', 'number'],
        'name': ['title', 'label', 'description'],
        'date': ['time', 'timestamp', 'created', 'modified'],
        'user': ['person', 'customer', 'client', 'employee'],
        'order': ['purchase', 'transaction', 'sale'],
        'product': ['item', 'goods', 'service'],
        'address': ['location', 'place'],
        'phone': ['telephone', 'mobile', 'contact'],
        'email': ['mail', 'contact'],
        'price': ['cost', 'amount', 'value'],
        'quantity': ['amount', 'count', 'number'],
        'status': ['state', 'condition'],
        'type': ['category', 'kind', 'classification'],
        'code': ['identifier', 'reference'],
        'description': ['details', 'notes', 'comments'],
        'created': ['added', 'inserted', 'made'],
        'updated': ['modified', 'changed', 'edited'],
        'deleted': ['removed', 'archived'],
        'active': ['enabled', 'current', 'valid'],
        'inactive': ['disabled', 'archived', 'old']
    }
    
    word_lower = word.lower()
    synonyms = [word]  # Include original word
    
    # Add direct synonyms
    if word_lower in synonym_map:
        synonyms.extend(synonym_map[word_lower])
    
    # Check for partial matches in synonym keys
    for key, values in synonym_map.items():
        if key in word_lower or word_lower in key:
            synonyms.extend(values)
    
    # Remove duplicates and return
    return list(set(synonyms))


def extract_meaningful_words(text: str) -> List[str]:
    """Extract meaningful words from text, filtering out common stop words.
    
    Args:
        text: Input text
        
    Returns:
        List of meaningful words
    """
    if not text:
        return []
    
    # Common stop words to filter out
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'tbl', 'table', 'db', 'database'
    }
    
    # Normalize and split text
    normalized = normalize_text(text)
    words = normalized.split()
    
    # Filter out stop words and short words
    meaningful_words = [
        word for word in words 
        if len(word) > 2 and word not in stop_words
    ]
    
    return meaningful_words


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize both texts
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    # Calculate sequence similarity
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    
    return similarity


def convert_technical_to_natural(technical_name: str) -> str:
    """Convert technical database name to natural language.
    
    Args:
        technical_name: Technical database name (table/column)
        
    Returns:
        Natural language equivalent
    """
    if not technical_name:
        return ""
    
    # Remove common prefixes/suffixes
    name = technical_name
    
    # Remove common table prefixes
    prefixes_to_remove = ['tbl_', 'tb_', 'table_', 'dbo.']
    for prefix in prefixes_to_remove:
        if name.lower().startswith(prefix):
            name = name[len(prefix):]
            break
    
    # Remove common suffixes
    suffixes_to_remove = ['_id', '_key', '_ref', '_tbl', '_table']
    for suffix in suffixes_to_remove:
        if name.lower().endswith(suffix):
            name = name[:-len(suffix)]
            break
    
    # Convert to natural language
    if '_' in name:
        natural = snake_case_to_words(name)
    else:
        natural = camel_case_to_words(name)
    
    # Capitalize first letter of each word
    natural = ' '.join(word.capitalize() for word in natural.split())
    
    return natural


def create_search_terms(technical_name: str) -> List[str]:
    """Create comprehensive search terms for a technical database name.
    
    Args:
        technical_name: Technical database name
        
    Returns:
        List of search terms and synonyms
    """
    search_terms = []
    
    # Add original name
    search_terms.append(technical_name)
    
    # Add natural language conversion
    natural = convert_technical_to_natural(technical_name)
    if natural and natural != technical_name:
        search_terms.append(natural)
    
    # Add individual meaningful words
    words = extract_meaningful_words(natural)
    search_terms.extend(words)
    
    # Add synonyms for each meaningful word
    for word in words:
        synonyms = generate_synonyms(word)
        search_terms.extend(synonyms)
    
    # Remove duplicates and empty strings
    search_terms = [term for term in set(search_terms) if term.strip()]
    
    return search_terms


def format_field_description(table_name: str, column_name: str, data_type: str = None) -> str:
    """Format a user-friendly description for a database field.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column
        data_type: Optional data type information
        
    Returns:
        Formatted description
    """
    table_natural = convert_technical_to_natural(table_name)
    column_natural = convert_technical_to_natural(column_name)
    
    description = f"{column_natural}"
    
    if table_natural and table_natural.lower() != column_natural.lower():
        description += f" from {table_natural}"
    
    if data_type:
        # Add data type info for clarity
        type_info = ""
        data_type_lower = data_type.lower()
        
        if 'int' in data_type_lower or 'numeric' in data_type_lower:
            type_info = " (number)"
        elif 'varchar' in data_type_lower or 'text' in data_type_lower:
            type_info = " (text)"
        elif 'date' in data_type_lower or 'time' in data_type_lower:
            type_info = " (date/time)"
        elif 'bit' in data_type_lower or 'bool' in data_type_lower:
            type_info = " (yes/no)"
        
        description += type_info
    
    return description