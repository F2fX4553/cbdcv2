import datetime
import hashlib
import ecdsa
import uuid
from decimal import Decimal, ROUND_HALF_UP
from ._db import session, SimpleStatement
from ...core.finance import calculate_fee

def create_transaction(sender, receiver, amount):
    """
    Create a new transaction between two wallet addresses
    sender: sender's wallet address
    receiver: receiver's wallet address
    amount: amount of GRM to send
    """
    try:
        # Check if sender exists
        sender_query = SimpleStatement(f"SELECT balance FROM wallet WHERE address = '{sender}';")
        sender_rows = session.execute(sender_query)
        
        sender_balance = 0
        for row in sender_rows:
            sender_balance = row.balance
        
        # Check if receiver exists
        receiver_query = SimpleStatement(f"SELECT balance FROM wallet WHERE address = '{receiver}';")
        receiver_rows = session.execute(receiver_query)
        
        receiver_exists = False
        for _ in receiver_rows:
            receiver_exists = True
        
        if not receiver_exists:
            print("Receiver wallet does not exist")
            return False
        
        # Calculate fee
        fee = calculate_fee(amount)
        total_amount = amount + fee
        
        # Check if sender has sufficient balance
        if sender_balance < total_amount:
            print("Insufficient balance")
            return False
        
        # Generate transaction hash
        transaction_hash = hashlib.sha256(f"{sender}{receiver}{amount}{datetime.datetime.now()}".encode()).hexdigest()
        
        # Update sender's balance
        update_sender_query = SimpleStatement(f"UPDATE wallet SET balance = balance - {total_amount} WHERE address = '{sender}';")
        session.execute(update_sender_query)
        
        # Update receiver's balance
        update_receiver_query = SimpleStatement(f"UPDATE wallet SET balance = balance + {amount} WHERE address = '{receiver}';")
        session.execute(update_receiver_query)
        
        # Record transaction
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        insert_transaction_query = SimpleStatement(
            f"INSERT INTO Transaction (hash, sender, receiver, amount, datetime) "
            f"VALUES ('{transaction_hash}', '{sender}', '{receiver}', {amount}, '{current_date}');"
        )
        session.execute(insert_transaction_query)
        
        print(f"Transaction {transaction_hash} completed successfully")
        return True
    
    except Exception as e:
        print(f"Error creating transaction: {e}")
        return False


def sign_transaction(transaction_data, private_key):
    """
    Sign a transaction with the sender's private key
    transaction_data: transaction data as string
    private_key: private key to sign with
    """
    try:
        # Convert transaction data to bytes
        data = transaction_data.encode()
        
        # Sign the data
        signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        signature = signing_key.sign(data)
        
        return signature.hex()
    
    except Exception as e:
        print(f"Error signing transaction: {e}")
        return None


def verify_transaction(transaction_data, signature, public_key):
    """
    Verify a transaction signature
    transaction_data: transaction data as string
    signature: signature to verify
    public_key: public key to verify against
    """
    try:
        # Convert transaction data to bytes
        data = transaction_data.encode()
        
        # Convert signature from hex to bytes
        signature_bytes = bytes.fromhex(signature)
        
        # Verify the signature
        verifying_key = ecdsa.VerifyingKey.from_string(public_key, curve=ecdsa.SECP256k1)
        return verifying_key.verify(signature_bytes, data)
    
    except Exception as e:
        print(f"Error verifying transaction: {e}")
        return False 