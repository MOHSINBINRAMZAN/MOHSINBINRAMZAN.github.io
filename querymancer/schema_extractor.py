"""
Database schema extraction module for QueryMancer.
Extracts complete schema information from SQL Server databases.
"""

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    pyodbc = None
    PYODBC_AVAILABLE = False

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from .config import config_manager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ColumnInfo:
    """Information about a database column."""
    name: str
    data_type: str
    max_length: Optional[int]
    is_nullable: bool
    default_value: Optional[str]
    is_primary_key: bool = False
    is_foreign_key: bool = False
    referenced_table: Optional[str] = None
    referenced_column: Optional[str] = None


@dataclass 
class TableInfo:
    """Information about a database table."""
    name: str
    schema: str
    columns: List[ColumnInfo]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    row_count: Optional[int] = None


class SchemaExtractor:
    """Extracts schema information from SQL Server databases."""
    
    def __init__(self, client_key: str):
        """Initialize schema extractor for a specific client.
        
        Args:
            client_key: Client identifier from configuration
        """
        self.client_key = client_key
        self.config = config_manager.get_database_config(client_key)
        if not self.config:
            raise ValueError(f"No configuration found for client: {client_key}")
        
        self.connection_string = config_manager.get_connection_string(client_key)
        self.connection = None
    
    def connect(self) -> bool:
        """Establish database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not PYODBC_AVAILABLE:
            logger.error("pyodbc is not available. Install with: pip install pyodbc")
            return False
            
        try:
            self.connection = pyodbc.connect(self.connection_string)
            logger.info(f"Connected to database for client: {self.client_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database for client {self.client_key}: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info(f"Disconnected from database for client: {self.client_key}")
    
    def get_tables(self, schema_filter: Optional[str] = None) -> List[str]:
        """Get list of tables in the database.
        
        Args:
            schema_filter: Optional schema name to filter tables
            
        Returns:
            List of table names
        """
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            
            # Query to get all user tables
            query = """
                SELECT TABLE_SCHEMA, TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """
            
            if schema_filter:
                query += f" AND TABLE_SCHEMA = '{schema_filter}'"
            
            query += " ORDER BY TABLE_SCHEMA, TABLE_NAME"
            
            cursor.execute(query)
            tables = []
            
            for row in cursor.fetchall():
                table_full_name = f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}"
                tables.append(table_full_name)
            
            cursor.close()
            return tables
            
        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            return []
    
    def get_table_columns(self, table_name: str) -> List[ColumnInfo]:
        """Get column information for a specific table.
        
        Args:
            table_name: Full table name (schema.table)
            
        Returns:
            List of ColumnInfo objects
        """
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            
            # Parse schema and table name
            if '.' in table_name:
                schema, table = table_name.split('.', 1)
            else:
                schema = 'dbo'
                table = table_name
            
            # Query to get column information
            query = """
                SELECT 
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.CHARACTER_MAXIMUM_LENGTH,
                    c.IS_NULLABLE,
                    c.COLUMN_DEFAULT,
                    CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END as IS_PRIMARY_KEY
                FROM INFORMATION_SCHEMA.COLUMNS c
                LEFT JOIN (
                    SELECT ku.TABLE_SCHEMA, ku.TABLE_NAME, ku.COLUMN_NAME
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                    INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                        ON tc.CONSTRAINT_TYPE = 'PRIMARY KEY' 
                        AND tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
                        AND tc.TABLE_SCHEMA = ku.TABLE_SCHEMA
                        AND tc.TABLE_NAME = ku.TABLE_NAME
                ) pk ON c.TABLE_SCHEMA = pk.TABLE_SCHEMA 
                      AND c.TABLE_NAME = pk.TABLE_NAME 
                      AND c.COLUMN_NAME = pk.COLUMN_NAME
                WHERE c.TABLE_SCHEMA = ? AND c.TABLE_NAME = ?
                ORDER BY c.ORDINAL_POSITION
            """
            
            cursor.execute(query, (schema, table))
            columns = []
            
            for row in cursor.fetchall():
                column = ColumnInfo(
                    name=row.COLUMN_NAME,
                    data_type=row.DATA_TYPE,
                    max_length=row.CHARACTER_MAXIMUM_LENGTH,
                    is_nullable=row.IS_NULLABLE == 'YES',
                    default_value=row.COLUMN_DEFAULT,
                    is_primary_key=bool(row.IS_PRIMARY_KEY)
                )
                columns.append(column)
            
            cursor.close()
            return columns
            
        except Exception as e:
            logger.error(f"Error getting columns for table {table_name}: {e}")
            return []
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, str]]:
        """Get foreign key information for a table.
        
        Args:
            table_name: Full table name (schema.table)
            
        Returns:
            List of foreign key information dictionaries
        """
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            
            # Parse schema and table name
            if '.' in table_name:
                schema, table = table_name.split('.', 1)
            else:
                schema = 'dbo'
                table = table_name
            
            # Query to get foreign key information
            query = """
                SELECT 
                    kcu.COLUMN_NAME,
                    kcu.REFERENCED_TABLE_SCHEMA,
                    kcu.REFERENCED_TABLE_NAME,
                    kcu.REFERENCED_COLUMN_NAME,
                    rc.CONSTRAINT_NAME
                FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
                INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                    ON rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                WHERE kcu.TABLE_SCHEMA = ? AND kcu.TABLE_NAME = ?
            """
            
            cursor.execute(query, (schema, table))
            foreign_keys = []
            
            for row in cursor.fetchall():
                fk_info = {
                    'column': row.COLUMN_NAME,
                    'referenced_table': f"{row.REFERENCED_TABLE_SCHEMA}.{row.REFERENCED_TABLE_NAME}",
                    'referenced_column': row.REFERENCED_COLUMN_NAME,
                    'constraint_name': row.CONSTRAINT_NAME
                }
                foreign_keys.append(fk_info)
            
            cursor.close()
            return foreign_keys
            
        except Exception as e:
            logger.error(f"Error getting foreign keys for table {table_name}: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> Optional[TableInfo]:
        """Get complete information about a table.
        
        Args:
            table_name: Full table name (schema.table)
            
        Returns:
            TableInfo object or None if error
        """
        try:
            # Parse schema and table name
            if '.' in table_name:
                schema, table = table_name.split('.', 1)
            else:
                schema = 'dbo'
                table = table_name
            
            # Get columns
            columns = self.get_table_columns(table_name)
            if not columns:
                return None
            
            # Get foreign keys
            foreign_keys = self.get_foreign_keys(table_name)
            
            # Update column foreign key information
            for fk in foreign_keys:
                for column in columns:
                    if column.name == fk['column']:
                        column.is_foreign_key = True
                        column.referenced_table = fk['referenced_table']
                        column.referenced_column = fk['referenced_column']
                        break
            
            # Get primary keys
            primary_keys = [col.name for col in columns if col.is_primary_key]
            
            # Get approximate row count
            row_count = self.get_table_row_count(table_name)
            
            return TableInfo(
                name=table,
                schema=schema,
                columns=columns,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys,
                row_count=row_count
            )
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return None
    
    def get_table_row_count(self, table_name: str) -> Optional[int]:
        """Get approximate row count for a table.
        
        Args:
            table_name: Full table name (schema.table)
            
        Returns:
            Row count or None if error
        """
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor()
            
            # Use sys.dm_db_partition_stats for better performance on large tables
            if '.' in table_name:
                schema, table = table_name.split('.', 1)
            else:
                schema = 'dbo'
                table = table_name
            
            query = """
                SELECT SUM(p.rows) as row_count
                FROM sys.tables t
                INNER JOIN sys.partitions p ON t.object_id = p.object_id
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                WHERE s.name = ? AND t.name = ? AND p.index_id IN (0,1)
            """
            
            cursor.execute(query, (schema, table))
            result = cursor.fetchone()
            cursor.close()
            
            return result.row_count if result and result.row_count else 0
            
        except Exception as e:
            logger.error(f"Error getting row count for table {table_name}: {e}")
            return None
    
    def extract_full_schema(self, schema_filter: Optional[str] = None) -> Dict[str, TableInfo]:
        """Extract complete schema information for all tables.
        
        Args:
            schema_filter: Optional schema name to filter tables
            
        Returns:
            Dictionary mapping table names to TableInfo objects
        """
        schema_info = {}
        
        # Get all tables
        tables = self.get_tables(schema_filter)
        
        logger.info(f"Found {len(tables)} tables for client {self.client_key}")
        
        # Get information for each table
        for table_name in tables:
            logger.info(f"Extracting schema for table: {table_name}")
            table_info = self.get_table_info(table_name)
            
            if table_info:
                schema_info[table_name] = table_info
            else:
                logger.warning(f"Failed to extract schema for table: {table_name}")
        
        return schema_info
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def extract_schema_for_client(client_key: str, schema_filter: Optional[str] = None) -> Dict[str, TableInfo]:
    """Extract schema information for a specific client.
    
    Args:
        client_key: Client identifier
        schema_filter: Optional schema name to filter tables
        
    Returns:
        Dictionary mapping table names to TableInfo objects
    """
    try:
        with SchemaExtractor(client_key) as extractor:
            return extractor.extract_full_schema(schema_filter)
    except Exception as e:
        logger.error(f"Failed to extract schema for client {client_key}: {e}")
        return {}


def extract_schema_for_all_clients() -> Dict[str, Dict[str, TableInfo]]:
    """Extract schema information for all configured clients.
    
    Returns:
        Dictionary mapping client keys to their schema information
    """
    all_schemas = {}
    clients = config_manager.get_all_clients()
    
    for client_key in clients:
        logger.info(f"Extracting schema for client: {client_key}")
        schema_info = extract_schema_for_client(client_key)
        if schema_info:
            all_schemas[client_key] = schema_info
            logger.info(f"Successfully extracted schema for client {client_key}: {len(schema_info)} tables")
        else:
            logger.warning(f"No schema information extracted for client: {client_key}")
    
    return all_schemas