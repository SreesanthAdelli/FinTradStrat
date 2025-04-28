"""
helpers.py

Helper functions for interacting with the trading API,
including data retrieval, order management, leasing, storage, transportation,
and refinery operations.
"""

import requests
from config import API_BASE_URL

# --- Data Retrieval Functions ---

def get_position_ticker(session, ticker):
    """
    Get the current position (inventory) for a specific security.

    Args:
        session (requests.Session): Authenticated session for API requests.
        ticker (str): Security ticker symbol.

    Returns:
        int: Number of units currently held (can be negative for short positions).
    """

    resp = session.get(f'{API_BASE_URL}/securities')
    if not resp.ok:
        raise ApiException(f"Failed to get securities list: {resp.status_code}")
    
    securities_list = resp.json()
    for security in securities_list:
        if security['ticker'] == ticker:
            return security.get('position', 0)
    
    raise ApiException(f"Ticker {ticker} not found in securities list.")

def get_positions(session):
    """
    Retrieve the current positions for all securities.

    Args:
        session (requests.Session): Authenticated session for API requests.

    Returns:
        dict: Dictionary of ticker symbols and their corresponding positions.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.get(f'{API_BASE_URL}/securities')
    if not resp.ok:
        raise ApiException(f"Failed to get securities list: {resp.status_code}")
    
    securities_list = resp.json()
    positions = {security['ticker']: security.get('position', 0) for security in securities_list}
    
    return positions



def ticker_bid_ask(session, ticker):
    """
    Retrieve the best bid and ask prices for a given security.

    Args:
        session (requests.Session): Authenticated session for API requests.
        ticker (str): Security ticker symbol.

    Returns:
        tuple: (best_bid_price (float), best_ask_price (float)).
    
    Raises:
        ApiException: If the request fails.
    """

    params = {'ticker': ticker}
    resp = session.get(f'{API_BASE_URL}/securities/book', params=params)
    if not resp.ok:
        raise ApiException(f"Failed to get book for {ticker}: {resp.status_code}")
    
    book = resp.json()
    bids = book.get('bids', [])
    asks = book.get('asks', [])
    
    if not bids or not asks:
        raise ApiException(f"No bids or asks available for ticker {ticker}.")
    
    return bids[0]['price'], asks[0]['price']


def get_tick(session):
    """
    Get the current simulation tick (time step).

    Args:
        session (requests.Session): Authenticated session for API requests.

    Returns:
        int: Current tick number.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.get(f'{API_BASE_URL}/case')
    if not resp.ok:
        raise ApiException(f"Failed to get case info: {resp.status_code}")
    
    case_info = resp.json()
    return case_info.get('tick', 0)


def get_orders(session, status):
    """
    Retrieve a list of trader's orders filtered by their status.

    Args:
        session (requests.Session): Authenticated session for API requests.
        status (str): Order status to filter by ('OPEN', 'TRANSACTED', 'CANCELLED').

    Returns:
        list: List of orders matching the given status.
    
    Raises:
        ApiException: If the request fails.
    """

    params = {'status': status}
    resp = session.get(f'{API_BASE_URL}/orders', params=params)
    if not resp.ok:
        raise ApiException(f"Failed to get orders with status {status}: {resp.status_code}")
    
    return resp.json()


def get_nlv(session):
    """
    Get the trader's current Net Liquidation Value (NLV).

    Args:
        session (requests.Session): Authenticated session for API requests.

    Returns:
        float: Current NLV value.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.get(f'{API_BASE_URL}/trader')
    if not resp.ok:
        raise ApiException(f"Failed to get trader info: {resp.status_code}")
    
    trader_info = resp.json()
    return trader_info.get('nlv', 0.0)

def get_net_position(session):
    """
    Get the trader's current net position across all securities.

    Args:
        session (requests.Session): Authenticated session for API requests.

    Returns:
        dict: Dictionary of ticker symbols and their corresponding net positions.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.get(f'{API_BASE_URL}/limits')
    if not resp.ok:
        raise ApiException(f"Failed to get securities list: {resp.status_code}")
    
    limits = resp.json()
    
    
    return limits[0]['net']


def get_portfolio(session):
    """
    Retrieve a snapshot of the trader's current portfolio, including cash and positions.

    Args:
        session (requests.Session): Authenticated session for API requests.

    Returns:
        dict: Portfolio details including cash balance, positions, and NLV.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.get(f'{API_BASE_URL}/trader')
    if not resp.ok:
        raise ApiException(f"Failed to get trader info: {resp.status_code}")
    
    return resp.json()


# --- Order Management Functions ---

def place_order(session, ticker, quantity, action, order_type='MARKET'):
    """
    Submit a new order to the exchange.

    Args:
        session (requests.Session): Authenticated session for API requests.
        ticker (str): Security ticker symbol.
        quantity (int): Number of contracts to trade.
        side (str): 'BUY' or 'SELL'.

    Returns:
        dict: API response containing order details.
    
    Raises:
        ApiException: If the request fails.
    """

    payload = {
        'ticker': ticker,
        'quantity': quantity,
        'action': action,
        'type': order_type,
    }

    resp = session.post(f'{API_BASE_URL}/orders', params=payload)

    if not resp.ok:
        raise ApiException(f"Failed to place order for {ticker}: {resp.status_code}")
    
    return resp.json()



def cancel_order(session, order_id):
    """
    Cancel an open order.

    Args:
        session (requests.Session): Authenticated session for API requests.
        order_id (str): Unique identifier of the order to cancel.

    Returns:
        dict: API response confirming cancellation.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.delete(f'{API_BASE_URL}/orders/{order_id}')
    if not resp.ok:
        raise ApiException(f"Failed to cancel order {order_id}: {resp.status_code}")
    
    return resp.json()


# --- Storage and Refining Functions ---

def lease_storage(session, ticker):
    """
    Lease a storage tank or similar facility for a given commodity.

    Args:
        session (requests.Session): Authenticated session for API requests.
        ticker (str): Facility ticker (e.g., 'CL-STORAGE', 'AK-STORAGE').

    Returns:
        dict: API response confirming lease.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.post(f'{API_BASE_URL}/leases', params={'ticker': ticker})
    if not resp.ok:
        raise ApiException(f"Failed to lease storage for {ticker}: {resp.status_code}")
    
    return resp.json()



def lease_refinery(session):
    """
    Lease a refinery facility for crude oil refining.

    Args:
        session (requests.Session): Authenticated session for API requests.

    Returns:
        dict: API response confirming lease.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.post(f'{API_BASE_URL}/leases', params={'ticker': 'CL-REFINERY'})
    if not resp.ok:
        raise ApiException("Failed to lease refinery: {resp.status_code}")
    
    return resp.json()


def use_refinery(session, from_ticker, quantity):
    """
    Send crude oil to the leased refinery for processing.

    Args:
        session (requests.Session): Authenticated session for API requests.
        from_ticker (str): Ticker of the input commodity (e.g., 'CL').
        quantity (int): Amount to refine.

    Returns:
        dict: API response confirming processing order.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.get(f'{API_BASE_URL}/leases', params={'ticker': 'CL-REFINERY'})
    leaseinfo = resp.json()

    payload = {'from1': from_ticker, 'quantity1': quantity}
    for x in leaseinfo:
        if "CL-REFINERY" in x['ticker']:
            leaseid = x['id']
            print(leaseid)
            session.post(f'{API_BASE_URL}/leases/{leaseid}', params=payload)
    if not resp.ok:
        raise ApiException(f"Failed to use refinery for {from_ticker}: {resp.status_code}")
    
    return resp.json()




def close_unused_storage_leases(session):
    """
    Terminate storage leases where the containment usage is zero.

    Args:
        session (requests.Session): Authenticated session for API requests.

    Returns:
        list: List of successfully closed lease IDs.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.get(f'{API_BASE_URL}/leases')
    if not resp.ok:
        raise ApiException(f"Failed to get leases: {resp.status_code}")
    
    lease_info = resp.json()
    closed_lease_ids = []
    for lease in lease_info:
        if lease.get('containment_usage', 0) == 0:
            lease_id = lease['id']
            resp = session.delete(f'{API_BASE_URL}/leases/{lease_id}')
            if resp.ok:
                closed_lease_ids.append(lease_id)
    
    return closed_lease_ids



def get_refinery_lease_info(session):
    """
    Get refinery lease ID and next lease renewal tick.

    Args:
        session (requests.Session): Authenticated session for API requests.

    Returns:
        tuple: (lease_id (int), next_lease_tick (int)).
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.get(f'{API_BASE_URL}/leases')
    if not resp.ok:
        raise ApiException(f"Failed to get leases: {resp.status_code}")
    
    lease_info = resp.json()
    for lease in lease_info:
        if lease['ticker'] == 'CL-REFINERY':
            lease_id = lease['id']
            lease_finish = lease['next_lease_tick']
            return True, lease_id, lease_finish
    else:
        return False, None, None  # No refinery lease found
    



def wait_and_close_refinery(session, lease_id, lease_finish_tick):
    """
    Wait until one tick before refinery lease renewal and then close the lease.

    Args:
        session (requests.Session): Authenticated session for API requests.
        lease_id (int): ID of the refinery lease to close.
        lease_finish_tick (int): Next renewal tick.

    Returns:
        dict: API response confirming lease closure.
    
    Raises:
        ApiException: If the request fails.
    """

    current_tick = get_tick(session)
    while current_tick < lease_finish_tick - 1:
        current_tick = get_tick(session)
    
    resp = session.delete(f'{API_BASE_URL}/leases/{lease_id}')
    if not resp.ok:
        raise ApiException(f"Failed to close refinery lease {lease_id}: {resp.status_code}")
    
    return resp.json()

def close_refinery(session, lease_id):
    """
    Close the refinery lease.

    Args:
        session (requests.Session): Authenticated session for API requests.
        lease_id (int): ID of the refinery lease to close.

    Returns:
        dict: API response confirming lease closure.
    
    Raises:
        ApiException: If the request fails.
    """
    if lease_id is None:
        resp = session.get(f'{API_BASE_URL}/leases')
        if not resp.ok:
            raise ApiException(f"Failed to get leases: {resp.status_code}")
        
        lease_info = resp.json()
        for lease in lease_info:
            if lease['ticker'] == 'CL-REFINERY':
                lease_id = lease['id']
                resp = session.delete(f'{API_BASE_URL}/leases/{lease_id}')
    
    else:
        resp = session.delete(f'{API_BASE_URL}/leases/{lease_id}')
        if not resp.ok:
            raise ApiException(f"Failed to close refinery lease {lease_id}: {resp.status_code}")
    
    return resp.json()

def close_empty_leases(session):
    """
    Close any empty leases in the system.

    Args:
        session (requests.Session): Authenticated session for API requests.

    Returns:
        list: List of successfully closed lease IDs.
    
    Raises:
        ApiException: If the request fails.
    """

    resp = session.get(f'{API_BASE_URL}/leases')
    if not resp.ok:
        raise ApiException(f"Failed to get leases: {resp.status_code}")
    
    lease_info = resp.json()
    closed_lease_ids = []
    for lease in lease_info:
        if lease.get('containment_usage', 0) == None:
            lease_id = lease['id']
            resp = session.delete(f'{API_BASE_URL}/leases/{lease_id}')
            if resp.ok:
                closed_lease_ids.append(lease_id)
        if lease.get('containment_usage', 0) == 0:
            lease_id = lease['id']
            resp = session.delete(f'{API_BASE_URL}/leases/{lease_id}')
            if resp.ok:
                closed_lease_ids.append(lease_id)
    return closed_lease_ids

# -- Fundamental (News) Functions --

def extract_number_from_text(text):
    """
    Helper function to extract the first floating-point or integer number from a string.

    Args:
        text (str): Input text.

    Returns:
        float: Extracted number.
    """
    import re
    match = re.search(r"[-+]?\d*\.\d+|\d+", text)
    if match:
        return float(match.group())
    else:
        raise ValueError(f"No number found in text: {text}")

def get_latest_news(session):
    """
    Fetch the most recent news items.

    Args:
        session (requests.Session): Authenticated session.

    Returns:
        list: List of news dictionaries.
    """
    resp = session.get(f"{API_BASE_URL}/news")
    resp.raise_for_status()
    return resp.json()
def fundamental_EIA_report(session):
    """
    Parse the latest EIA report headline and return the difference between actual and forecast.

    Args:
        session (requests.Session): Authenticated session.

    Returns:
        float: Difference between actual draw/build and forecasted draw/build.
               Positive if bigger draw than expected, negative if smaller draw or a build.
        None: If no valid EIA report is found.
    """
    news_items = get_latest_news(session)

    for news in news_items:
        headline = news.get("headline", "").upper()

        if "ACTUAL" in headline and "FORECAST" in headline:
            try:
                # Example format: "WEEK 1 ACTUAL DRAW 14 MLN BBLS VS FORECAST DRAW 5 MLN BBLS"
                actual_str = headline.split("ACTUAL")[1].split("VS")[0].strip()
                forecast_str = headline.split("FORECAST")[1].strip()

                # Find numbers in each section
                actual_number = extract_number_from_text(actual_str)
                forecast_number = extract_number_from_text(forecast_str)

                # Determine if it was a DRAW or BUILD
                if "DRAW" in actual_str:
                    actual = -actual_number  # Draw = negative
                else:
                    actual = actual_number   # Build = positive

                if "DRAW" in forecast_str:
                    forecast = -forecast_number
                else:
                    forecast = forecast_number

                return actual - forecast

            except Exception as e:
                print(f"Failed to parse EIA report: {e}")
                return None

    return None


# --- Transportation Functions ---

def lease_use_transport(session, ticker, quantity):
    """
    Lease a pipeline for transporting a commodity.

    Args:
        session (requests.Session): Authenticated session for API requests.
        from_ticker (str): Ticker of commodity to transport (e.g., 'CL-AK').
        quantity (int): Number of units to transport.
        pipeline_ticker (str): Ticker for the pipeline lease (e.g., 'AK-CS-PIPE').

    Returns:
        dict: API response confirming lease order.
    
    Raises:
        ApiException: If the request fails.
    """

    payload = {
        'ticker': ticker,
        'quantity1': quantity,
    }

    resp = session.post(f'{API_BASE_URL}/leases', params=payload)
    if not resp.ok:
        raise ApiException(f"Failed to lease transport for {ticker}: {resp.status_code}")
    
    return resp.json()



# --- Error Handling Class ---

class ApiException(Exception):
    """
    Custom exception class to handle API-related errors.
    """
    pass
