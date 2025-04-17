# Gorgumu CBDC - Flask Web Application

This is a web-based version of the Gorgumu CBDC (Central Bank Digital Currency) wallet, converted from the original desktop application into a Flask web application.

## What Is CBDC?
CBDC is The Central Bank Digital Currency Or The Money Of Future.

## What Is Gorgumu?
Gorgumu is a project of centralized cryptocurrency that doesn't use blockchain. It's symbolized by "GRM" and aims to be the global currency for trading.

## Features
- User authentication and wallet creation
- Send and receive transactions
- Request digital loans after completing at least 20 transactions
- Monitor transaction history
- View wallet status including balance expiration date
- Make deposits through various payment methods

## Technical Details
The web application maintains all the core functionality of the original desktop application:

- **Financial Algorithm**: The system uses a fractional reserve system with algorithms for nominal interest, real interest, and inflation calculation.
- **Cryptography**: Multiple encryption algorithms (RSA, AES, ECDSA, SHA256, RIPEMD160) ensure maximum security.
- **Database**: Apache Cassandra NoSQL database for storing wallet information and transactions.

## Installation Instructions

### Prerequisites
1. Python 3.11.4 or higher
2. Apache Cassandra NoSQL version 3.11.10

### Setup Steps
1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Run Apache Cassandra Server
6. Create a new keyspace named 'gorgumu':
   ```
   CREATE KEYSPACE gorgumu WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1} AND DURABLE_WRITES = true;
   ```
7. Create the necessary tables by running:
   ```
   python -c "from core.gorgumu._db import *; from __init__ import tables; for query in tables: session.execute(query); print('Tables created successfully')"
   ```
8. Insert initial values:
   ```
   INSERT INTO gorgumu.liquidity(total,circulating) VALUES('MAX',16000000000);
   INSERT INTO gorgumu.loanbox(total,loansupply) VALUES ('MAX',0);
   INSERT INTO gorgumu.Fractional_Reserve(total,money_supply) VALUES ('MAX',0);
   ```
9. Run the Flask application: `python app.py`
10. Access the web application at: `http://localhost:5000`

## Financial System Information
- Interest Rate: 5% by default
- Generate appropriate liquidity after supply reaches down 10k by default
- Fractional Reserve: 10% by default
- Loan Type: Ninja
- iScore: 400pt to 850pt
- Interest rates rise when inflation increases and fall during deflation

## Transaction Fees
Fees are calculated based on transaction amount:
- 0.001 - 0.99 GRM: Amount / 10
- 1 - 99 GRM: Amount / 100
- 100 - 999 GRM: Amount / 1,000
- 1,000 - 9,999 GRM: Amount / 10,000
- 10,000 - 99,999 GRM: Amount / 100,000
- 100,000 - 999,999 GRM: Amount / 1,000,000
- 1,000,000 - 99,999,999 GRM: Amount / 100,000,000
- 100,000,000 - 999,999,999 GRM: Amount / 1,000,000,000

## Note
This is the first version of the web-based wallet. Future versions will include additional features. 