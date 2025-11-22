"""
Configuration package
"""

from .database import connect_db, close_db, get_database, get_collection

__all__ = ['connect_db', 'close_db', 'get_database', 'get_collection']
