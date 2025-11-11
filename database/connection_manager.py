"""DuckDB Connection Manager with access control and auditing."""
import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import duckdb
import logging

logger = logging.getLogger(__name__)


class DuckDBConnectionManager:
    """
    DuckDB Connection Manager with authentication-like features.
    
    Since DuckDB is file-based and doesn't have traditional authentication,
    this class provides:
    - Connection pooling and management
    - Access control through API keys
    - Audit logging
    - Connection validation
    - Schema initialization
    """
    
    def __init__(
        self,
        database_path: str = "/app/data/analytics.duckdb",
        init_scripts_dir: str = "/app/database/init",
        max_connections: int = 10
    ):
        self.database_path = Path(database_path)
        self.init_scripts_dir = Path(init_scripts_dir)
        self.max_connections = max_connections
        self._connections: Dict[str, duckdb.DuckDBPyConnection] = {}
        self._api_keys: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        
        # Ensure database directory exists
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database if needed
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with schemas and tables."""
        if self._initialized:
            return
        
        try:
            conn = self._get_admin_connection()
            
            
            # Standard DuckDB initialization
            logger.info("Initializing DuckDB database...")
            
            # Run initialization scripts in order
            init_files = sorted(self.init_scripts_dir.glob("*.sql"))
            
            for init_file in init_files:
                logger.info(f"Running initialization script: {init_file.name}")
                with open(init_file, 'r') as f:
                    sql_content = f.read()
                
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                for statement in statements:
                    try:
                        conn.execute(statement)
                    except Exception as e:
                        logger.warning(f"Error executing statement in {init_file.name}: {e}")
            
            logger.info("Database initialization completed")
            self._initialized = True
            conn.close()
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def create_api_key(
        self,
        user_id: str,
        permissions: List[str] = None,
        description: str = ""
    ) -> str:
        """
        Create an API key for database access.
        
        Args:
            user_id: Unique identifier for the user
            permissions: List of permissions ('read', 'write', 'admin')
            description: Description of the API key usage
            
        Returns:
            Generated API key
        """
        if permissions is None:
            permissions = ['read']
        
        # Generate API key
        key_data = f"{user_id}:{datetime.now().isoformat()}:{uuid.uuid4()}"
        api_key = hashlib.sha256(key_data.encode()).hexdigest()[:32]
        
        # Store API key metadata
        self._api_keys[api_key] = {
            'user_id': user_id,
            'permissions': permissions,
            'description': description,
            'created_at': datetime.now(),
            'last_used': None,
            'active': True
        }
        
        logger.info(f"Created API key for user {user_id} with permissions: {permissions}")
        return api_key
    
    def validate_api_key(self, api_key: str, required_permission: str = 'read') -> bool:
        """
        Validate API key and check permissions.
        
        Args:
            api_key: API key to validate
            required_permission: Required permission level
            
        Returns:
            True if valid and has permission
        """
        if api_key not in self._api_keys:
            return False
        
        key_info = self._api_keys[api_key]
        
        if not key_info['active']:
            return False
        
        if required_permission not in key_info['permissions'] and 'admin' not in key_info['permissions']:
            return False
        
        # Update last used timestamp
        key_info['last_used'] = datetime.now()
        return True
    
    @contextmanager
    def get_connection(
        self,
        api_key: Optional[str] = None,
        connection_type: str = 'read',
        client_info: str = "unknown"
    ):
        """
        Get a database connection with access control.
        
        Args:
            api_key: API key for authentication (None for admin access)
            connection_type: Type of connection ('read', 'write', 'admin')
            client_info: Information about the client
            
        Yields:
            DuckDB connection
        """
        # Validate API key if provided
        if api_key and not self.validate_api_key(api_key, connection_type):
            raise PermissionError(f"Invalid API key or insufficient permissions for {connection_type}")
        
        connection_id = str(uuid.uuid4())
        user_id = self._api_keys.get(api_key, {}).get('user_id', 'admin') if api_key else 'admin'
        
        try:
            # Create connection
            conn = duckdb.connect(str(self.database_path))
            self._connections[connection_id] = conn
            
            # Log connection
            self._log_connection_audit(
                connection_type=connection_type,
                user_identifier=user_id,
                client_info=client_info,
                operation='CONNECT',
                success=True
            )
            
            logger.info(f"Connection {connection_id} established for user {user_id}")
            yield conn
            
        except Exception as e:
            # Log failed connection
            self._log_connection_audit(
                connection_type=connection_type,
                user_identifier=user_id,
                client_info=client_info,
                operation='CONNECT',
                success=False,
                error_message=str(e)
            )
            raise
        finally:
            # Clean up connection
            if connection_id in self._connections:
                self._connections[connection_id].close()
                del self._connections[connection_id]
                logger.info(f"Connection {connection_id} closed")
    
    def _get_admin_connection(self):
        """Get admin connection for internal operations."""
        conn = duckdb.connect(str(self.database_path))
        try:
            # Load UI extension for admin connections
            conn.execute("LOAD ui;")
        except Exception:
            # UI extension might not be available, continue without it
            pass
        return conn
    
    def _log_connection_audit(
        self,
        connection_type: str,
        user_identifier: str,
        client_info: str,
        operation: str,
        success: bool = True,
        table_accessed: str = None,
        error_message: str = None
    ):
        """Log connection audit information."""
        try:
            with self._get_admin_connection() as conn:
                audit_id = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO metadata.connection_audit (
                        audit_id, connection_type, user_identifier, client_info,
                        database_name, table_accessed, operation, timestamp,
                        success, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    audit_id, connection_type, user_identifier, client_info,
                    str(self.database_path), table_accessed, operation,
                    datetime.now(), success, error_message
                ])
        except Exception as e:
            logger.error(f"Failed to log audit information: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            'active_connections': len(self._connections),
            'max_connections': self.max_connections,
            'api_keys_count': len(self._api_keys),
            'database_path': str(self.database_path),
            'initialized': self._initialized
        }
    
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key."""
        if api_key in self._api_keys:
            self._api_keys[api_key]['active'] = False
            logger.info(f"API key revoked for user {self._api_keys[api_key]['user_id']}")
            return True
        return False
    


# Global connection manager instance
connection_manager = DuckDBConnectionManager()


def get_connection_manager() -> DuckDBConnectionManager:
    """Get the global connection manager instance."""
    return connection_manager
