import helper
import time
import globals


# State to track transportation trades
transportation_trade_info_AK = {
    "active": False,
    "entry_tick": None,
    "quantity": 0
}

transportation_trade_info_NYC = {
    "active": False,
    "entry_tick": None,
    "quantity": 0
}


MIN_PROFIT_THRESHOLD = 5000 # Minimum profit threshold for transportation
TRADE_QUANTITY = 100 # Quantity of crude oil to transport
SLEEP_TIME = 0

def should_transport_AK_CS(session):
    """
    Check if the transport model should be executed based on the current tick.

    Args:
        session (requests.Session): Authenticated session object.

    Returns:
        bool: True if transport model should be executed, False otherwise.
    """

    
    # Get price data for CL-AK and CL
    cl_AK_bid, cl_AK_ask = helper.ticker_bid_ask(session, 'CL-AK')
    cl_bid, cl_ask = helper.ticker_bid_ask(session, 'CL')
    net = helper.get_net_position(session)
    Expected_profit = (10000*cl_bid - 10000*cl_AK_bid - globals.AK_CS_PIPE)

    if Expected_profit > MIN_PROFIT_THRESHOLD:
        print("Transporting from AK to CS is profitable. Expected profit: ", Expected_profit)
        return True

    else:
        print("Transporting from AK to CS is not profitable. Expected profit: ", Expected_profit)
        return False
    
def should_transport_CS_NYC(session):
    """
    Check if the transport model should be executed based on the current tick.

    Args:
        session (requests.Session): Authenticated session object.

    Returns:
        bool: True if transport model should be executed, False otherwise.
    """

    
    # Get price data for CL-AK and CL
    cl_bid, cl_ask = helper.ticker_bid_ask(session, 'CL')
    cl_nyc_bid, cl_nyc_ask = helper.ticker_bid_ask(session, 'CL-NYC')
    Expected_profit = (10000*cl_nyc_bid - 10000*cl_ask - globals.CS_NYC_PIPE)

    if Expected_profit > MIN_PROFIT_THRESHOLD:
        print("Transporting from CS to NYC is profitable. Expected profit: ", Expected_profit)
        return True

    else:
        print("Transporting from CS to NYC is not profitable. Expected profit: ", Expected_profit)
        return False
    
def try_transport_AK_CS(session):
    """
    Execute the transportation model from AK to CS if conditions are met.

    Args:
        session (requests.Session): Authenticated session object.

    Returns:
        None
    """

    global transportation_trade_info_AK

    # Check if transport is profitable
    if should_transport_AK_CS(session):

        net = helper.get_net_position(session)

        tick = helper.get_tick(session)
        current_tick = tick

        quantity = TRADE_QUANTITY

        helper.lease_storage(session, 'AK-STORAGE')

        if net < 70:
            for i in range(0, int(quantity/10)):
                helper.place_order(session, 'CL-AK', 10, 'BUY', 'MARKET')
                print(f"Bought spot position: BUY 10 CL-AK")
                helper.place_order(session, 'CL-2F', 10, 'SELL', 'MARKET')
                print(f"Shorted futures position: SELL 10 CL-2F")
                time.sleep(SLEEP_TIME)
                helper.lease_use_transport(session, 'AK-CS-PIPE', 'CL-AK', 10)
        else:
            for i in range(int(quantity/10)):
                helper.place_order(session, 'CL-2F', 10, 'SELL', 'MARKET')
                print(f"Shorted futures position: SELL 10 CL-2F")
                helper.place_order(session, 'CL-AK', 10, 'BUY', 'MARKET')
                print(f"Bought spot position: BUY 10 CL-AK")
                time.sleep(SLEEP_TIME)
                helper.lease_use_transport(session, 'AK-CS-PIPE', 'CL-AK', 10)

        transportation_trade_info_AK = {
                "active": True,
                "entry_tick": current_tick,
                "quantity": TRADE_QUANTITY
            }

def try_transport_CS_NYC(session):
    """
    Execute the transportation model from CS to NYC if conditions are met.

    Args:
        session (requests.Session): Authenticated session object.

    Returns:
        None
    """

    global transportation_trade_info_NYC
    tick = helper.get_tick(session)
    current_tick = tick
    # Check if transport is profitable
    if should_transport_CS_NYC(session):

        net = helper.get_net_position(session)

        quantity = TRADE_QUANTITY
        helper.lease_storage(session, 'CL-STORAGE')

        if net < 70:
            for i in range(int(quantity/10)):
                helper.place_order(session, 'CL', 10, 'BUY', 'MARKET')
                print(f"Bought spot position: BUY 10 CL-AK")
                helper.place_order(session, 'CL-2F', 10, 'SELL', 'MARKET')
                print(f"Shorted futures position: SELL 10 CL-2F")
                time.sleep(SLEEP_TIME)
                helper.lease_use_transport(session, 'CS-NYC-PIPE', 'CL', 10)
        else:
            for i in range(int(quantity/10)):
                helper.place_order(session, 'CL-2F', 10, 'SELL', 'MARKET')
                print(f"Shorted futures position: SELL 10 CL-2F")
                helper.place_order(session, 'CL', 10, 'BUY', 'MARKET')
                print(f"Bought spot position: BUY 10 CL")
                time.sleep(SLEEP_TIME)
                helper.lease_use_transport(session, 'CS-NYC-PIPE', 'CL', 10)

        transportation_trade_info_NYC = {
                "active": True,
                "entry_tick": current_tick,
                "quantity": TRADE_QUANTITY
            }

def transportation_model(session):
    """
    Main function to execute the transportation model.

    Args:
        session (requests.Session): Authenticated session object.

    Returns:
        None
    """
    global transportation_trade_info_AK
    global transportation_trade_info_NYC

    current_tick = helper.get_tick(session)

    net = helper.get_net_position(session)

    if transportation_trade_info_AK["active"]:
        if current_tick - transportation_trade_info_AK["entry_tick"] >= 27:
            print("Closing transportation hedge and spot position after 30 ticks.")
            quantity = transportation_trade_info_AK["quantity"]
            for i in range(int(quantity/10)):
                helper.lease_storage(session, 'CL-STORAGE')
            print("Closing AK transportation hedge and spot position after 30 ticks.")
            time.sleep(2)

            if net > 70:
                # Close the spot position first
                for i in range(0, int(quantity/10)):
                    helper.place_order(session, 'CL', 10, 'SELL', 'MARKET')
                    print(f"Closed Spot position: SELL 10 CL-2F")
                    helper.place_order(session, 'CL-2F', 10, 'BUY', 'MARKET')
                    print(f"Closed Futures position: BUY 10 CL-2F")
            else:
                for i in range(0, int(quantity/10)):
                    helper.place_order(session, 'CL-2F', 10, 'BUY', 'MARKET')
                    print(f"Closed Futures position: BUY 10 CL-2F")
                    helper.place_order(session, 'CL', 10, 'SELL', 'MARKET')
                    print(f"Closed Spot position: SELL 10 CL")

            transportation_trade_info_AK = {
                "active": False,
                "AL or NYC": None,
                "entry_tick": None,
                "quantity": 0
            }
    if transportation_trade_info_NYC["active"]:
        if current_tick - transportation_trade_info_NYC["entry_tick"] >= 27:
            quantity = transportation_trade_info_NYC["quantity"]
            for _ in range(int(quantity/10)):
                helper.lease_storage(session, 'NYC-STORAGE')
            print("Closing NYC transportation hedge and spot position after 30 ticks.")
            time.sleep(2)
            if net > 70:
                # Close the spot position first
                for i in range(0, int(transportation_trade_info_NYC["quantity"]/10)):
                    helper.place_order(session, 'CL-NYC', 10, 'SELL', 'MARKET')
                    print(f"Closed Spot position: SELL 10 CL-NYC")
                    helper.place_order(session, 'CL-2F', 10, 'BUY', 'MARKET')
                    print(f"Closed Futures position: BUY 10 CL-2F")
            else:
                for i in range(0, int(transportation_trade_info_NYC["quantity"]/10)):
                    helper.place_order(session, 'CL-2F', 10, 'BUY', 'MARKET')
                    print(f"Closed Futures position: BUY 10 CL-2F")
                    helper.place_order(session, 'CL-NYC', 10, 'SELL', 'MARKET')
                    print(f"Closed Spot position: SELL 10 CL-NYC")

            transportation_trade_info_NYC = {
                "active": False,
                "AL or NYC": None,
                "entry_tick": None,
                "quantity": 0
            }
    if transportation_trade_info_AK["active"] == False:
        try_transport_AK_CS(session)
    if transportation_trade_info_NYC["active"] == False:
        try_transport_CS_NYC(session)

    
    