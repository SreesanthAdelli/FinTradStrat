import helper
import time
import visualization

def should_refine(ho_price, rb_price, cl_price):
    """
    Determine if it is profitable to refine 30 contracts of crude oil based on crack spread.

    Args:
        ho_price (float): Price of heating oil (HO).
        rb_price (float): Price of gasoline (RB).
        cl_price (float): Price of crude oil (CL).

    Returns:
        bool: True if refining is profitable, False otherwise.
        float: Expected profit after refining costs.
    """
    REFINING_COST = 300_000
    MIN_PROFIT_THRESHOLD = 20_000
    CONTRACTS = 30
    BARRELS_PER_CONTRACT = 1000
    BBL_TO_GALLONS = 42_000

    total_revenue = (10 * ho_price * BBL_TO_GALLONS) + (20 * rb_price * BBL_TO_GALLONS)
    total_cost = (CONTRACTS * cl_price * BARRELS_PER_CONTRACT) + REFINING_COST
    total_profit = total_revenue - total_cost

    return total_profit >= MIN_PROFIT_THRESHOLD, total_profit

def try_refining(session):
    """
    Check if refining is profitable and send crude oil for refining if it is.

    Args:
        session (requests.Session): Authenticated session for API requests.

    Returns:
        dict or None: API response from use_refinery if refining, otherwise None.
    """
    ho_bid, ho_ask = helper.ticker_bid_ask(session, 'HO')
    rb_bid, rb_ask = helper.ticker_bid_ask(session, 'RB')
    cl_bid, cl_ask = helper.ticker_bid_ask(session, 'CL')

    ho_price = ho_bid
    rb_price = rb_bid
    cl_price = cl_ask

    refine_now, expected_profit = should_refine(ho_price, rb_price, cl_price)

    print(f"Expected profit from refining: ${expected_profit:,.2f}")

    # Update the live visualization with the current expected profit
    visualization.refining_expected_profit(expected_profit)

    if refine_now:
        print("Refining opportunity found!")
        helper.lease_storage(session, 'CL-STORAGE')
        helper.lease_storage(session, 'CL-STORAGE')
        helper.lease_storage(session, 'CL-STORAGE')
        print("Leased storage (3) for crude oil.")
        
        net_position = helper.get_net_position(session)
        

        if net_position > 70:
            helper.place_order(session, 'CL-2F', 30, 'SELL', 'MARKET')
            print("Placed SELL order for 30 contracts of CL-2F.")
            helper.place_order(session, 'CL', 30, 'BUY', 'MARKET')
            print("Placed BUY order for 30 contracts of CL.")
        else:
            helper.place_order(session, 'CL', 30, 'BUY', 'MARKET')
            print("Placed BUY order for 30 contracts of CL.")
            helper.place_order(session, 'CL-2F', 30, 'SELL', 'MARKET')
            print("Placed SELL order for 30 contracts of CL-2F.")


        
        '''
        helper.place_order(session, 'CL', 30, 'BUY', 'MARKET')
        print("Placed BUY order for 30 contracts of CL.")
        helper.place_order(session, 'CL-2F', 30, 'SELL', 'MARKET')
        print("Placed SELL order for 30 contracts of CL-2F.")
        '''
        helper.lease_refinery(session)
        print("Leased refinery.")
        time.sleep(.5) # Wait for lease to be confirmed
        helper.use_refinery(session, 'CL', 30)
        print("Sent crude oil for refining.")
        

        
    else:
        print("Refining not profitable. Skipping.")
        return None


def refining_model(session):
    """
    Manage refining process: check if refinery is available and attempt refining if possible.

    Args:
        session (requests.Session): Authenticated session.

    Returns:
        None
    """
    refining_now, lease_id, lease_end_tick = helper.get_refinery_lease_info(session)
    print(f"refining_now: {refining_now}")
    
    if refining_now:
        print("Refinery is being used. Continuing to next model.")
        time.sleep(1)
    else:
        positions = helper.get_positions(session)

        if positions['HO'] > 0 and positions['RB'] > 0 and positions['CL-2F'] < 0:
            print("Closing Refinery positions.")
            helper.place_order(session, 'HO', positions['HO'], 'SELL', 'MARKET')
            helper.place_order(session, 'RB', positions['RB'], 'SELL', 'MARKET')
            helper.place_order(session, 'CL-2F', 30, 'BUY', 'MARKET')
            print("Refinery is available. Attempting to refine.")
            
            
        try_refining(session)
