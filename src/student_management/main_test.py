import os
import sqlite3
import unittest
import tempfile
from main import DatabaseConnection

class TestDatabaseConnection(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to act as the database
        self.temp_db_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db_path = self.temp_db_file.name
        self.temp_db_file.close()

    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_connection_and_create_table(self):
        db = DatabaseConnection(self.temp_db_path)
        connection = db.connect()

        # Verify that the connection object is of correct type
        self.assertIsInstance(connection, sqlite3.Connection)

        cursor = connection.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        connection.commit()

        # Check table was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "test")

        connection.close()

if __name__ == "__main__":
    unittest.main()
