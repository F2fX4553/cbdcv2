from core.gorgumu._db import *

# Database tables creation statements
tables = [
    """
    CREATE TABLE IF NOT EXISTS gorgumu.wallet (
        address TEXT PRIMARY KEY,
        balance FLOAT,
        iscore INT,
        datetime DATE,
        expire_date DATE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS gorgumu.Astronate (
        address TEXT PRIMARY KEY,
        balance FLOAT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS gorgumu.Transaction (
        hash TEXT PRIMARY KEY,
        sender TEXT,
        receiver TEXT,
        amount DECIMAL,
        datetime DATE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS gorgumu.Fractional_Reserve (
        total TEXT PRIMARY KEY,
        money_supply DECIMAL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS gorgumu.Deposite (
        address TEXT PRIMARY KEY,
        amount FLOAT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS gorgumu.Loanbox (
        total TEXT PRIMARY KEY,
        loansupply DECIMAL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS gorgumu.Loans (
        address TEXT PRIMARY KEY,
        amount DECIMAL,
        debt DECIMAL,
        datetime DATE,
        expire_date DATE
    );
    """
]

# This will be called when tables need to be created
def create_tables():
    try:
        for query in tables:
            session.execute(query)
        print("Tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False 