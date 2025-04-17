import os
from dotenv import load_dotenv
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra.auth import PlainTextAuthProvider

# Load environment variables
load_dotenv()

# Get database credentials from environment variables
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# Initialize Cassandra connection
# For authentication, uncomment the auth_provider line if needed
try:
    # auth_provider = PlainTextAuthProvider(username=username, password=password)
    # cluster = Cluster(auth_provider=auth_provider)
    cluster = Cluster()  # For local development without authentication
    session = cluster.connect('gorgumu')
    print("Database connection established successfully")
except Exception as e:
    print(f"Error connecting to database: {e}")
    # For development purposes, create a mock session
    class MockSession:
        def execute(self, query, *args, **kwargs):
            print(f"Mock executing query: {query}")
            return []

    class MockCluster:
        def shutdown(self):
            pass

    session = MockSession()
    cluster = MockCluster()
    print("Using mock database session for development") 