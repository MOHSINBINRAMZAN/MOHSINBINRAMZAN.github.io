"""
Configuration management for QueryMancer multi-client database system.
Supports multiple client database configurations for automated mapping generation.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configuration for a single client database."""
    client_name: str
    server: str
    database: str
    username: str
    password: str
    port: int = 1433
    driver: str = "ODBC Driver 17 for SQL Server"
    trusted_connection: bool = False


class ConfigManager:
    """Manages configurations for multiple client databases."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), "client_configs.json")
        self.databases: Dict[str, DatabaseConfig] = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """Load database configurations from file or environment variables."""
        # Load from environment variables for now (can be extended to JSON file)
        # This allows for secure configuration without hardcoding credentials
        
        # Example configuration for demonstration
        self.databases = {
            "client_a": DatabaseConfig(
                client_name="Client A",
                server=os.getenv("CLIENT_A_SERVER", "localhost"),
                database=os.getenv("CLIENT_A_DATABASE", "ClientA_DB"),
                username=os.getenv("CLIENT_A_USERNAME", "sa"),
                password=os.getenv("CLIENT_A_PASSWORD", "password"),
                port=int(os.getenv("CLIENT_A_PORT", "1433")),
                trusted_connection=os.getenv("CLIENT_A_TRUSTED", "false").lower() == "true"
            ),
            "client_b": DatabaseConfig(
                client_name="Client B", 
                server=os.getenv("CLIENT_B_SERVER", "localhost"),
                database=os.getenv("CLIENT_B_DATABASE", "ClientB_DB"),
                username=os.getenv("CLIENT_B_USERNAME", "sa"),
                password=os.getenv("CLIENT_B_PASSWORD", "password"),
                port=int(os.getenv("CLIENT_B_PORT", "1433")),
                trusted_connection=os.getenv("CLIENT_B_TRUSTED", "false").lower() == "true"
            )
        }
    
    def get_database_config(self, client_key: str) -> Optional[DatabaseConfig]:
        """Get database configuration for a specific client.
        
        Args:
            client_key: The client identifier
            
        Returns:
            DatabaseConfig if found, None otherwise
        """
        return self.databases.get(client_key)
    
    def get_all_clients(self) -> List[str]:
        """Get list of all configured client keys.
        
        Returns:
            List of client keys
        """
        return list(self.databases.keys())
    
    def add_database_config(self, client_key: str, config: DatabaseConfig):
        """Add a new database configuration.
        
        Args:
            client_key: Unique identifier for the client
            config: Database configuration
        """
        self.databases[client_key] = config
    
    def get_connection_string(self, client_key: str) -> Optional[str]:
        """Generate SQL Server connection string for a client.
        
        Args:
            client_key: The client identifier
            
        Returns:
            Connection string if client found, None otherwise
        """
        config = self.get_database_config(client_key)
        if not config:
            return None
        
        if config.trusted_connection:
            return (
                f"Driver={{{config.driver}}};"
                f"Server={config.server},{config.port};"
                f"Database={config.database};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"Driver={{{config.driver}}};"
                f"Server={config.server},{config.port};"
                f"Database={config.database};"
                f"UID={config.username};"
                f"PWD={config.password};"
            )


# Global configuration instance
config_manager = ConfigManager()