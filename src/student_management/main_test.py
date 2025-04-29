import os
import sqlite3
import unittest
import tempfile
from main import DatabaseConnection

class TestDatabaseConnection(unittest.TestCase):
    """Test cases for database connection
    """
    def test_connect_returns_sqlite_connection(self) -> None:
        """Tests that `connect()` returns an instance of sqlite3.Connection.
        """
        test_db = "test_database.db"

        db = DatabaseConnection(test_db)
        connection = db.connect()

        self.assertIsInstance(connection, sqlite3.Connection)
        connection.close()
        os.remove(test_db)

if __name__ == "__main__":
    unittest.main()
