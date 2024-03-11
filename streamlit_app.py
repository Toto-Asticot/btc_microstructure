import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import time

class Exchange:
    def __init__(self, name, api_url):
        self.name = name
        self.api_url = api_url

    def fetch_orderbook(self):
        raise NotImplementedError()

class Binance(Exchange):
    def fetch_orderbook(self):
        response = requests.get(self.api_url + 'api/v3/depth?symbol=BTCUSDT&limit=1000')
        data = response.json()
        bids = pd.DataFrame(data['bids'], columns=['Price', 'Size'])
        bids['Side'] = 'buy'
        asks = pd.DataFrame(data['asks'], columns=['Price', 'Size'])
        asks['Side'] = 'sell'
        return pd.concat([bids, asks], ignore_index=True)

def main():
    st.title("Real-Time Orderbook Analysis")

    binance = Binance('Binance', 'https://api.binance.com/')
    
    st.write("Fetching orderbook data from Binance API...")
    binance_orderbook = binance.fetch_orderbook()

    st.write("Orderbook Data:")
    st.write(binance_orderbook)

    # Convert 'Price' and 'Size' columns to float
    binance_orderbook['Price'] = binance_orderbook['Price'].astype(float)
    binance_orderbook['Size'] = binance_orderbook['Size'].astype(float)

    # Calculate cumulative sums for buy and sell sides
    binance_orderbook['Buy'] = binance_orderbook[binance_orderbook['Side'] == 'buy']['Size'].cumsum()
    binance_orderbook['Sell'] = binance_orderbook[binance_orderbook['Side'] == 'sell']['Size'][::-1].cumsum()

    # Get current timestamp
    current_timestamp = datetime.now()

    # Plot the orderbook
    plt.figure(figsize=(12, 6))
    plt.plot(binance_orderbook['Price'], binance_orderbook['Buy'], label='Buy')
    plt.plot(binance_orderbook['Price'], binance_orderbook['Sell'], label='Sell')
    plt.xlabel('Price')
    plt.ylabel('Cumulative Size')
    plt.title('Aggregated Orderbook BTC/USD')
    plt.legend()
    st.pyplot(plt)

    # Display current price and orderbook statistics
    current_price = binance_orderbook['Price'].iloc[0]  # Assuming 'Price' is sorted
    st.write(f"Current Price: {current_price:.2f}")
    st.write(f"Total Buy Size: {binance_orderbook['Buy'].iloc[-1]:.2f}")
    st.write(f"Total Sell Size: {binance_orderbook['Sell'].iloc[-1]:.2f}")

    # Update interval in seconds
    update_interval = 20
    while True:
        time.sleep(update_interval)
        st.write("Fetching updated orderbook data...")
        binance_orderbook = binance.fetch_orderbook()

        # Update the plot
        plt.clf()
        plt.plot(binance_orderbook['Price'], binance_orderbook['Buy'], label='Buy')
        plt.plot(binance_orderbook['Price'], binance_orderbook['Sell'], label='Sell')
        plt.xlabel('Price')
        plt.ylabel('Cumulative Size')
        plt.title('Aggregated Orderbook BTC/USD')
        plt.legend()
        st.pyplot(plt)

        # Update current price and orderbook statistics
        current_price = binance_orderbook['Price'].iloc[0]  # Assuming 'Price' is sorted
        st.write(f"Current Price: {current_price:.2f}")
        st.write(f"Total Buy Size: {binance_orderbook['Buy'].iloc[-1]:.2f}")
        st.write(f"Total Sell Size: {binance_orderbook['Sell'].iloc[-1]:.2f}")

if __name__ == "__main__":
    main()
