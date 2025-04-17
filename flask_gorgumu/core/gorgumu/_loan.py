import datetime
from decimal import Decimal, ROUND_HALF_UP
from ._db import session, SimpleStatement
from ...core.finance import nom_int, calculate_expiry_date

def request_loan(address, amount):
    """
    Request a loan for a wallet
    address: wallet address requesting the loan
    amount: amount of GRM requested
    """
    try:
        # Check if wallet has completed at least 20 transactions
        tx_count_query = SimpleStatement(
            f"SELECT COUNT(*) FROM Transaction WHERE sender = '{address}';"
        )
        tx_count_rows = session.execute(tx_count_query)
        
        tx_count = 0
        for row in tx_count_rows:
            tx_count = row.count
        
        if tx_count < 20:
            print("Insufficient transaction history. Minimum 20 transactions required.")
            return False
        
        # Check if wallet has outstanding loans
        loan_check_query = SimpleStatement(
            f"SELECT amount, debt FROM Loans WHERE address = '{address}';"
        )
        loan_rows = session.execute(loan_check_query)
        
        has_loan = False
        for _ in loan_rows:
            has_loan = True
        
        if has_loan:
            print("You already have an outstanding loan.")
            return False
        
        # Check if there's sufficient loan supply
        loan_supply_query = SimpleStatement(
            "SELECT loansupply FROM Loanbox WHERE total = 'MAX';"
        )
        loan_supply_rows = session.execute(loan_supply_query)
        
        loan_supply = 0
        for row in loan_supply_rows:
            loan_supply = row.loansupply
        
        if amount > loan_supply:
            print("Insufficient loan supply available.")
            return False
        
        # Check wallet credit score (iScore)
        wallet_query = SimpleStatement(f"SELECT iscore FROM wallet WHERE address = '{address}';")
        wallet_rows = session.execute(wallet_query)
        
        iscore = 0
        for row in wallet_rows:
            iscore = row.iscore
        
        if iscore < 400:
            print("Your iScore is too low to qualify for a loan.")
            return False
        
        # Calculate loan terms
        interest_rate = 0.05  # 5% interest rate
        loan_period = 120 / 365  # 120 days in years
        interest = nom_int(amount, interest_rate, loan_period)
        debt = amount + interest
        
        # Calculate expiry date
        current_date = datetime.date.today()
        expiry_date = calculate_expiry_date(current_date)
        
        # Record the loan
        insert_loan_query = SimpleStatement(
            f"INSERT INTO Loans (address, amount, debt, datetime, expire_date) "
            f"VALUES ('{address}', {amount}, {debt}, '{current_date}', '{expiry_date}');"
        )
        session.execute(insert_loan_query)
        
        # Update wallet balance
        update_wallet_query = SimpleStatement(
            f"UPDATE wallet SET balance = balance + {amount} WHERE address = '{address}';"
        )
        session.execute(update_wallet_query)
        
        # Update loan supply
        update_loan_supply_query = SimpleStatement(
            f"UPDATE Loanbox SET loansupply = loansupply - {amount} WHERE total = 'MAX';"
        )
        session.execute(update_loan_supply_query)
        
        print(f"Loan of {amount} GRM approved. Must be repaid by {expiry_date}.")
        return True
    
    except Exception as e:
        print(f"Error processing loan request: {e}")
        return False


def repay_loan(address, amount):
    """
    Repay a loan
    address: wallet address repaying the loan
    amount: amount of GRM to repay
    """
    try:
        # Check if wallet has a loan
        loan_query = SimpleStatement(f"SELECT debt FROM Loans WHERE address = '{address}';")
        loan_rows = session.execute(loan_query)
        
        debt = 0
        has_loan = False
        for row in loan_rows:
            debt = row.debt
            has_loan = True
        
        if not has_loan:
            print("You do not have an outstanding loan.")
            return False
        
        # Check if wallet has sufficient balance
        balance_query = SimpleStatement(f"SELECT balance FROM wallet WHERE address = '{address}';")
        balance_rows = session.execute(balance_query)
        
        balance = 0
        for row in balance_rows:
            balance = row.balance
        
        if balance < amount:
            print("Insufficient balance to repay loan.")
            return False
        
        # Process payment
        if amount >= debt:
            # Full repayment
            payment = debt
            remaining_debt = 0
            
            # Delete loan record
            delete_loan_query = SimpleStatement(f"DELETE FROM Loans WHERE address = '{address}';")
            session.execute(delete_loan_query)
        else:
            # Partial repayment
            payment = amount
            remaining_debt = debt - amount
            
            # Update loan record
            update_loan_query = SimpleStatement(
                f"UPDATE Loans SET debt = {remaining_debt} WHERE address = '{address}';"
            )
            session.execute(update_loan_query)
        
        # Update wallet balance
        update_wallet_query = SimpleStatement(
            f"UPDATE wallet SET balance = balance - {payment} WHERE address = '{address}';"
        )
        session.execute(update_wallet_query)
        
        # Update loan supply
        update_loan_supply_query = SimpleStatement(
            f"UPDATE Loanbox SET loansupply = loansupply + {payment} WHERE total = 'MAX';"
        )
        session.execute(update_loan_supply_query)
        
        if remaining_debt == 0:
            print(f"Loan fully repaid. Thank you!")
        else:
            print(f"Payment of {payment} GRM made. Remaining debt: {remaining_debt} GRM")
        
        return True
    
    except Exception as e:
        print(f"Error processing loan repayment: {e}")
        return False


def check_loan_expiry():
    """
    Check for expired loans and process accordingly
    """
    try:
        current_date = datetime.date.today()
        
        # Query for expired loans
        expired_loans_query = SimpleStatement(
            f"SELECT address, debt FROM Loans WHERE expire_date < '{current_date}';"
        )
        expired_loans = session.execute(expired_loans_query)
        
        for loan in expired_loans:
            address = loan.address
            debt = loan.debt
            
            # Update iScore negatively
            update_iscore_query = SimpleStatement(
                f"UPDATE wallet SET iscore = iscore - 50 WHERE address = '{address}';"
            )
            session.execute(update_iscore_query)
            
            # In a real implementation, this is where data encryption would occur
            print(f"Loan for {address} has expired with outstanding debt of {debt} GRM.")
        
        return True
    
    except Exception as e:
        print(f"Error checking loan expiry: {e}")
        return False 