"""
main.py

Entry point for running the trading system,
initializing sessions, strategies, and visual dashboards.
"""

import requests
import helper
import refining
import fundamental
import transportation
import storage
import time
from config import API_KEY, API_BASE_URL


def initialize_session():
    """
    Initialize and authenticate a requests session for API communication.

    Returns:
        requests.Session: Authenticated session object.
    """
    session = requests.Session()
    session.headers.update({'X-API-Key': API_KEY})
    return session

def main():
    """
    Main orchestration function for running the trading system.

    - Initialize session
    - Run each strategy

    Returns:
        None
    """
    session = initialize_session()
    tick = helper.get_tick(session)
    
    while True:
        print("")
        tick = helper.get_tick(session)
        helper.close_empty_leases(session)
        net_position = helper.get_net_position(session)
        print(f"Net position: {net_position}")
        print(f"Tick: {tick}")

        # Refining Model

        refining.refining_model(session)
    
        # Fundamental Model

        fundamental.fundamental_model(session)

        # Transportation Model

        transportation.transportation_model(session)
        
        # Storage Model

        storage.storage_model(session)

        # Extra
        
        time.sleep(.6)

if __name__ == "__main__":
    main()
