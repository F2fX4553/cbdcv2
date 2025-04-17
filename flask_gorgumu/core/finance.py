import datetime
from decimal import Decimal, ROUND_HALF_UP

# Mock exchange rate for GRM
Gorgumu_Price = 0.056  # USD per GRM

def nom_int(principal, rate, time):
    """
    Calculate nominal interest
    principal: loan amount
    rate: interest rate (as decimal, e.g. 0.05 for 5%)
    time: time period in years
    """
    return principal * rate * time

def calc_inflation(exchange_rates):
    """
    Calculate inflation based on exchange rates
    exchange_rates: list of exchange rate values
    """
    return sum(exchange_rates)

def real_int(nominal_interest, inflation):
    """
    Calculate real interest
    nominal_interest: calculated nominal interest
    inflation: calculated inflation
    """
    return nominal_interest - inflation

def generate_liquidity(circulating_supply, unit_price_with_inflation, multiplier=4):
    """
    Generate new units based on the fractional reserve algorithm
    circulating_supply: current circulating supply
    unit_price_with_inflation: unit price adjusted for inflation
    multiplier: multiplier factor (default 4)
    """
    return circulating_supply / unit_price_with_inflation * multiplier

def calculate_fee(amount):
    """
    Calculate transaction fee based on the amount
    amount: transaction amount in GRM
    """
    if amount >= 0.001 and amount < 1:
        fee = amount / 10
    elif amount >= 1 and amount < 100:
        fee = amount / 100
    elif amount >= 100 and amount < 1000:
        fee = amount / 1000
    elif amount >= 1000 and amount < 10000:
        fee = amount / 10000
    elif amount >= 10000 and amount < 100000:
        fee = amount / 100000
    elif amount >= 100000 and amount < 1000000:
        fee = amount / 1000000
    elif amount >= 1000000 and amount < 100000000:
        fee = amount / 100000000
    elif amount >= 100000000 and amount < 1000000000:
        fee = amount / 1000000000
    else:
        fee = 0
    
    # Format to 8 decimal places
    fee_decimal = Decimal(str(fee)).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
    return float(fee_decimal)

def calculate_expiry_date(from_date=None, days=120):
    """
    Calculate the expiry date for wallet balances
    from_date: starting date (default is today)
    days: number of days until expiry (default 120)
    """
    if from_date is None:
        from_date = datetime.date.today()
    
    return from_date + datetime.timedelta(days=days) 