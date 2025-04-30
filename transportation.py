import helper
import time
import globals


# State to track transportation trades
transportation_trade_info_AK = {
    "active": False,
    "entry_tick": None,
    "quantity": 0,
    "current_time": None
}

transportation_trade_info_NYC = {
    "active": False,
    "entry_tick": None,
    "quantity": 0,
    "current_time": None    
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
        current_time = time.time()

        quantity = TRADE_QUANTITY

        helper.lease_storage(session, 'AK-STORAGE')

        if net < 70:
            for i in range(0, int(quantity/10)):
                helper.place_order(session, 'CL-AK', 10, 'BUY', 'MARKET')
                print(f"Bought spot position: BUY 10 CL-AK")
                helper.place_order(session, 'CL-2F', 10, 'SELL', 'MARKET')
                print(f"Shorted futures position: SELL 10 CL-2F")
                helper.lease_use_transport(session, 'AK-CS-PIPE', 'CL-AK', 10)
        else:
            for i in range(int(quantity/10)):
                helper.place_order(session, 'CL-2F', 10, 'SELL', 'MARKET')
                print(f"Shorted futures position: SELL 10 CL-2F")
                helper.place_order(session, 'CL-AK', 10, 'BUY', 'MARKET')
                print(f"Bought spot position: BUY 10 CL-AK")
                helper.lease_use_transport(session, 'AK-CS-PIPE', 'CL-AK', 10)

        transportation_trade_info_AK = {
                "active": True,
                "entry_tick": current_tick,
                "current_time": current_time,
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
    current_time = time.time()
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
                helper.lease_use_transport(session, 'CS-NYC-PIPE', 'CL', 10)
        else:
            for i in range(int(quantity/10)):
                helper.place_order(session, 'CL-2F', 10, 'SELL', 'MARKET')
                print(f"Shorted futures position: SELL 10 CL-2F")
                helper.place_order(session, 'CL', 10, 'BUY', 'MARKET')
                print(f"Bought spot position: BUY 10 CL")
                helper.lease_use_transport(session, 'CS-NYC-PIPE', 'CL', 10)

        transportation_trade_info_NYC = {
                "active": True,
                "entry_tick": current_tick,
                "current_time": current_time,
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
        if time.time() - transportation_trade_info_AK["current_time"] >= 26:
            print("Closing transportation hedge and spot position after 30 ticks.")
            print(f"{30 - (time.time() - transportation_trade_info_AK['current_time'])} seconds left in transportation") 
            if time.time() - transportation_trade_info_AK["current_time"] >= 29.5:
                print("Too late to buy storage. Incurred Distressed Prices")
            else:
                for i in range(10):
                    helper.lease_storage(session, 'CL-STORAGE')

            while not helper.get_position_ticker(session, 'CL') == 100:
                time.sleep(0.2)
                print("Waiting for position to be 100 CL")

            if net > 70:
                for i in range(1, 5):
                    helper.place_order(session, 'CL', 25, 'SELL', 'MARKET')
                    print(f"Closed Spot ({i}) position: SELL 25 CL-2F")
                    helper.place_order(session, 'CL-2F', 25, 'BUY', 'MARKET')
                    print(f"Closed Futures ({i}) position: BUY 25 CL-2F")
            else:
                for i in range(1, 5):
                    helper.place_order(session, 'CL-2F', 25, 'BUY', 'MARKET')
                    print(f"Closed Futures ({i}) position: BUY 10 CL-2F")
                    helper.place_order(session, 'CL', 25, 'SELL', 'MARKET')
                    print(f"Closed Spot ({i}) position: SELL 25 CL")

            transportation_trade_info_AK = {
                "active": False,
                "entry_tick": None,
                "quantity": 0,
                "current_time": None
            }
            return None
        else:
            print(f"{30 - (time.time() - transportation_trade_info_AK['current_time'])} seconds left in transportation") 
    if transportation_trade_info_NYC["active"]:
        if time.time() - transportation_trade_info_NYC["current_time"] >= 26:
            print("Closing transportation hedge and spot position after 30 ticks.")
            print(f"{30 - (time.time() - transportation_trade_info_NYC['current_time'])} seconds left in transportation") 
            if time.time() - transportation_trade_info_NYC["current_time"] >= 29.5:
                print("Too late to buy storage. Incurred Distressed Prices")
            else:
                for i in range(10):
                    helper.lease_storage(session, 'CL-STORAGE')

            while not helper.get_position_ticker(session, 'CL-NYC') == 100:
                time.sleep(0.2)
                print("Waiting for position to be 100 CL-NYC")

            if net > 70:
                for i in range(1, 5):
                    helper.place_order(session, 'CL-NYC', 25, 'SELL', 'MARKET')
                    print(f"Closed Spot ({i}) position: SELL 25 CL-NYC")
                    helper.place_order(session, 'CL-2F', 25, 'BUY', 'MARKET')
                    print(f"Closed Futures ({i}) position: BUY 25 CL-2F")
            else:
                for i in range(1, 5):
                    helper.place_order(session, 'CL-2F', 25, 'BUY', 'MARKET')
                    print(f"Closed Futures ({i}) position: BUY 25 CL-2F")
                    helper.place_order(session, 'CL-NYC', 25, 'SELL', 'MARKET')
                    print(f"Closed Spot ({i}) position: SELL 25 CL-NYC")


            transportation_trade_info_NYC = {
                "active": False,
                "entry_tick": None,
                "quantity": 0,
                "current_time": None
            }
            return None
        else:
            print(f"{30 - (time.time() - transportation_trade_info_NYC['current_time'])} seconds left in transportation") 
    
    if transportation_trade_info_AK["active"] == False:
        try_transport_AK_CS(session)
    if transportation_trade_info_NYC["active"] == False:
        try_transport_CS_NYC(session)

    
    