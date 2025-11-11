#!/usr/bin/env python3
"""Initialize DuckDB database with schemas and sample data."""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, '/app')

from database.connection_manager import get_connection_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize the DuckDB database."""
    try:
        logger.info("Starting DuckDB database initialization...")
        
        # Get connection manager (this will initialize the database)
        conn_mgr = get_connection_manager()
        
        # Check for API keys in environment variables first
        admin_key = os.getenv("ADMIN_API_KEY")
        readonly_key = os.getenv("READONLY_API_KEY") 
        write_key = os.getenv("WRITE_API_KEY")
        api_keys_file = Path("/app/data/api_keys.txt")  # Define this here for scope
        
        if admin_key and readonly_key and write_key:
            logger.info("Using API keys from environment variables...")
            
            # Register keys in connection manager
            conn_mgr._api_keys[admin_key] = {
                'user_id': 'admin',
                'permissions': ['read', 'write', 'admin'],
                'description': 'Administrator access key (from env)',
                'created_at': datetime.now(),
                'last_used': None,
                'active': True
            }
            conn_mgr._api_keys[readonly_key] = {
                'user_id': 'analytics_user',
                'permissions': ['read'],
                'description': 'Read-only access for analytics (from env)',
                'created_at': datetime.now(),
                'last_used': None,
                'active': True
            }
            conn_mgr._api_keys[write_key] = {
                'user_id': 'ingestion_service',
                'permissions': ['read', 'write'],
                'description': 'Data ingestion service key (from env)',
                'created_at': datetime.now(),
                'last_used': None,
                'active': True
            }
            
            logger.info(f"Admin key from env: {admin_key}")
            logger.info(f"Readonly key from env: {readonly_key}")
            logger.info(f"Write key from env: {write_key}")
            
        else:
            # Fallback to file-based keys
            logger.info("No environment API keys found, checking file...")
            
            if api_keys_file.exists():
                logger.info("API keys already exist, loading existing keys...")
                
                # Load existing keys
                admin_key = None
                readonly_key = None
                write_key = None
                
                with open(api_keys_file, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key_name, key_value = line.strip().split('=', 1)
                            if key_name == "ADMIN_API_KEY":
                                admin_key = key_value
                                logger.info(f"Loaded existing admin key: {admin_key}")
                                # Re-register the key in the connection manager
                                conn_mgr._api_keys[admin_key] = {
                                    'user_id': 'admin',
                                    'permissions': ['read', 'write', 'admin'],
                                    'description': 'Administrator access key',
                                    'created_at': conn_mgr._api_keys.get(admin_key, {}).get('created_at'),
                                    'last_used': None,
                                    'active': True
                                }
                            elif key_name == "READONLY_API_KEY":
                                readonly_key = key_value
                                logger.info(f"Loaded existing readonly key: {readonly_key}")
                                # Re-register the key in the connection manager
                                conn_mgr._api_keys[readonly_key] = {
                                    'user_id': 'analytics_user',
                                    'permissions': ['read'],
                                    'description': 'Read-only access for analytics',
                                    'created_at': conn_mgr._api_keys.get(readonly_key, {}).get('created_at'),
                                    'last_used': None,
                                    'active': True
                                }
                            elif key_name == "WRITE_API_KEY":
                                write_key = key_value
                                logger.info(f"Loaded existing write key: {write_key}")
                                # Re-register the key in the connection manager
                                conn_mgr._api_keys[write_key] = {
                                    'user_id': 'ingestion_service',
                                    'permissions': ['read', 'write'],
                                    'description': 'Data ingestion service key',
                                    'created_at': conn_mgr._api_keys.get(write_key, {}).get('created_at'),
                                    'last_used': None,
                                    'active': True
                                }
            
                # Validate that we have all required keys
                if not all([admin_key, readonly_key, write_key]):
                    logger.warning("Some API keys missing from file, will create missing ones...")
                    
            else:
                logger.info("No existing API keys found, creating new ones...")
                admin_key = None
                readonly_key = None
                write_key = None
        
        # Create missing keys
        if not admin_key:
            admin_key = conn_mgr.create_api_key(
                user_id="admin",
                permissions=["read", "write", "admin"],
                description="Administrator access key"
            )
            logger.info(f"Admin API key created: {admin_key}")
        
        if not readonly_key:
            readonly_key = conn_mgr.create_api_key(
                user_id="analytics_user",
                permissions=["read"],
                description="Read-only access for analytics"
            )
            logger.info(f"Read-only API key created: {readonly_key}")
        
        if not write_key:
            write_key = conn_mgr.create_api_key(
                user_id="ingestion_service",
                permissions=["read", "write"],
                description="Data ingestion service key"
            )
            logger.info(f"Write API key created: {write_key}")
        
        # Test database connectivity
        logger.info("Testing database connectivity...")
        with conn_mgr.get_connection(api_key=admin_key, connection_type="admin") as conn:
            # Test basic query
            result = conn.execute("SELECT 'Database initialized successfully' as message").fetchone()
            logger.info(f"Database test result: {result[0]}")
            
            # Show schemas (DuckDB syntax)
            schemas = conn.execute("SELECT schema_name FROM information_schema.schemata").fetchall()
            logger.info(f"Available schemas: {[schema[0] for schema in schemas]}")
            
            # Show tables in raw schema (DuckDB syntax)
            tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'raw'").fetchall()
            logger.info(f"Tables in raw schema: {[table[0] for table in tables]}")
        
        # Get connection stats
        stats = conn_mgr.get_connection_stats()
        logger.info(f"Connection manager stats: {stats}")
        
        logger.info("DuckDB database initialization completed successfully!")
        
        # Keep the container running
        logger.info("Database service is ready. Keeping container alive...")
        
        # Write API keys to file (only if file doesn't exist or keys were created/updated)
        if not api_keys_file.exists() or any([
            not api_keys_file.exists(),
            admin_key and admin_key not in open(api_keys_file, 'r').read() if api_keys_file.exists() else True
        ]):
            logger.info("Updating API keys file...")
            with open(api_keys_file, 'w') as f:
                f.write(f"ADMIN_API_KEY={admin_key}\n")
                f.write(f"READONLY_API_KEY={readonly_key}\n")
                f.write(f"WRITE_API_KEY={write_key}\n")
            logger.info(f"API keys written to {api_keys_file}")
        else:
            logger.info("API keys file is up to date, no changes needed")
        
        # Simple HTTP server to keep container alive and provide health check
        import http.server
        import socketserver
        from functools import partial
        
        class HealthHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress logging for broken pipe errors and normal health checks
                if "Broken pipe" not in str(args) and "BrokenPipeError" not in str(args):
                    super().log_message(format, *args)
            
            def do_GET(self):
                try:
                    if self.path == '/health':
                        try:
                            stats = conn_mgr.get_connection_stats()
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            import json
                            self.wfile.write(json.dumps(stats).encode())
                        except Exception as e:
                            self.send_response(500)
                            self.send_header('Content-type', 'text/plain')
                            self.end_headers()
                            self.wfile.write(f"Health check failed: {str(e)}".encode())
                    else:
                        self.send_response(404)
                        self.end_headers()
                except (BrokenPipeError, ConnectionResetError):
                    # Client disconnected - this is normal for health checks, just log and continue
                    logger.debug("Client disconnected during response")
                except Exception as e:
                    logger.error(f"Unexpected error in handler: {e}")
        
        PORT = 8080
        with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
            logger.info(f"Database service running on port {PORT}")
            logger.info("Health check available at http://localhost:8080/health")
            httpd.serve_forever()
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
