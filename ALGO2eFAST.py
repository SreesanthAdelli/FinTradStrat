import signal
import requests
import time
from time import sleep

# this class definition allows us to print error messages and stop the program when needed
class ApiException(Exception):
    pass

# this signal handler allows for a graceful shutdown when CTRL+C is pressed
def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    shutdown = True

shutdown = False

# API Configuration
API_KEY = {'X-API-KEY': 'ZQXIW7T7'}
API_BASE_URL = 'http://localhost:9998/v1'

# Trading Parameters
TICKER = 'RY'
starttime = 0
endtime = 295
RETRY_DELAY = 0.1

# Fixed parameter values (tuned from experiment.py)
ordersize = 5000
rebalancesize = 1500
orderslimit = 6
rebalance_limit = 4000
SLEEP_TIME = 0.3

# this function obtains the current position of the security
def get_position(session, ticker):
    resp = session.get(f'{API_BASE_URL}/securities')
    securitieslist = resp.json()
    for x in securitieslist:
        if x['ticker'] == ticker:
            position = x['position']
    return position

# this function returns the bid and ask for the security
def ticker_bid_ask(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get(f'{API_BASE_URL}/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        return book['bids'][0]['price'], book['asks'][0]['price']
    raise ApiException('Response error in ticker_bid_ask')

# this function returns the current 'tick' of the running case
def get_tick(session):
    resp = session.get(f'{API_BASE_URL}/case')
    if resp.status_code == 401:
        raise ApiException('Response error in get_tick')
    case = resp.json()
    return case['tick']

# this function gets all the orders of a given type (OPEN/TRANSACTED/CANCELLED)
def get_orders(session, status):
    payload = {'status': status}
    resp = session.get(f'{API_BASE_URL}/orders', params=payload)
    if resp.status_code == 401:
        
        raise ApiException('Response error in get_orders')
    orders = resp.json()
    return orders

# Function to get the Net Liquidation Value (NLV) of the signed-in trader
def get_nlv(session):
    resp = session.get(f'{API_BASE_URL}/trader')
    if resp.status_code == 200:
        trader_info = resp.json()
        nlv = trader_info.get('nlv', 0)  # Extract the NLV value
        print(f"Net Liquidation Value (NLV): {nlv}")
        return nlv
    else:
        raise ApiException(f"Failed to get NLV. Status code: {resp.status_code}")

# this is the main method containing the actual market making strategy logic
def main():
    # creates a session to manage connections and requests to the RIT Client
    with requests.Session() as s:
        # add the API key to the session to authenticate during requests
        s.headers.update(API_KEY)
        # get the current time of the case
        tick = get_tick(s)
        
        if tick is None:
            print("Failed to get initial tick")
            return

        print(f"Starting trading session with parameters:")
        print(f"ordersize: {ordersize}, rebalancesize: {rebalancesize}")
        print(f"orderslimit: {orderslimit}, rebalance_limit: {rebalance_limit}")
        print(f"SLEEP_TIME: {SLEEP_TIME}")
        print(f"Current tick: {tick}, End time: {endtime}")

        # while the time is between starttime and endtime, do the following
        while tick >= starttime and tick < endtime:
            try:
                # get the best bid and ask price of the security
                best_bid, best_ask = ticker_bid_ask(s, TICKER)
                position = get_position(s, TICKER)

                buy_quantity = ordersize
                sell_quantity = ordersize

                # adjust order size if current position exceeds value of rebalance_limit
                if position > rebalance_limit:
                    buy_quantity = rebalancesize
                elif position < -rebalance_limit:
                    sell_quantity = rebalancesize

                # post a buy and sell limit order at bid and ask prices
                s.post(f'{API_BASE_URL}/orders', params={'ticker': TICKER, 'type': 'LIMIT', 'quantity': buy_quantity, 'action': 'BUY', 'price': best_bid - 0.01})
                s.post(f'{API_BASE_URL}/orders', params={'ticker': TICKER, 'type': 'LIMIT', 'quantity': sell_quantity, 'action': 'SELL', 'price': best_ask + 0.01})

                # get list of open orders
                orders = get_orders(s, 'OPEN')

                # delete oldest order when number of orders exceeds orderslimit
                num_orders = len(orders)
                while num_orders > orderslimit:
                    orderid = orders[num_orders-1]['order_id']
                    s.delete(f'{API_BASE_URL}/orders/{orderid}')
                    sleep(RETRY_DELAY)
                    orders = get_orders(s, 'OPEN')
                    num_orders = len(orders)
                
                sleep(SLEEP_TIME)

                # refresh the case time. THIS IS IMPORTANT FOR THE WHILE LOOP
                tick = get_tick(s)
                if tick is None:
                    print("Failed to get tick, retrying...")
                    sleep(RETRY_DELAY)
                    continue
                
                if tick % 10 == 0:  # Print progress every 10 ticks
                    print(f"Current tick: {tick}, End time: {endtime}")
                    print(f"Current position: {position}, NLV: {get_nlv(s)}")
                
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                sleep(RETRY_DELAY)
                continue
        
        # If we've reached beyond endtime, session was successful
        if tick >= endtime:
            print(f"Session completed successfully at tick {tick}")
            print(f"Final NLV: {get_nlv(s)}")
        else:
            print(f"Session ended unexpectedly at tick {tick}")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main() 