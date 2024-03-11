import pandas as pd
import requests
import matplotlib.pyplot as plt
import time
import subprocess
from PyQt5 import QtWidgets, QtCore
from threading import Thread
from IPython.display import clear_output
import numpy as np
from datetime import datetime

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
    # Initialize exchange objects
    binance = Binance('Binance', 'https://api.binance.com/')

    # Fetch orderbook data
    binance_orderbook = binance.fetch_orderbook()

    # Select only the relevant columns for each DataFrame

    binance_orderbook = binance_orderbook[['Price', 'Size', 'Side']]

    # Concatenate the modified DataFrames
    orderbook=binance_orderbook

    # You may want to sort the orderbook based on price
    orderbook = orderbook.sort_values(by=['Price'], ascending=False).reset_index(drop=True)
    
    orderbook['Price']=orderbook['Price'].astype(float)
    orderbook['Size']=orderbook['Size'].astype(float)

    # Save the orderbook to a csv file
    return orderbook

# Set the time delay in seconds between each iteration
delay = 0.1
price_range = 50  # Price range for analysis
spread=pd.DataFrame(columns=['Best_Bid','Best_Ask',"Timestamp"])
volume=pd.DataFrame(columns=['Bid','Ask',"Timestamp"])

while True:
    # Execute the main.py script to update the CSV data
    orderbook=main()
    # Calculate cumulative sums for buy and sell sides
    orderbook['Buy'] = orderbook[orderbook['Side'] == 'buy']['Size'].cumsum()
    orderbook['Sell'] = orderbook[orderbook['Side'] == 'sell']['Size'][::-1].cumsum()

    # Get the current BTC price from binance
    response = requests.get('https://api.binance.com/api/v3/ticker/price', params={'symbol': 'BTCUSDT'})
    current_price = float(response.json()['price'])
    
    # Analyze the buy and sell sides within the price range
    price_min = current_price - price_range
    price_max = current_price + price_range
    buy_size = orderbook[(orderbook['Price'] >= price_min) & (orderbook['Price'] <= price_max) & (orderbook['Side'] == 'buy')]['Size'].sum()
    sell_size = orderbook[(orderbook['Price'] >= price_min) & (orderbook['Price'] <= price_max) & (orderbook['Side'] == 'sell')]['Size'].sum()

    #Calculate best ask and best bid
    
    best_ask=orderbook[pd.notna(orderbook["Sell"])]['Price'].min()
    best_bid=orderbook[pd.notna(orderbook["Buy"])]['Price'].max()
    bid_vol=buy_size
    ask_vol=sell_size
    
    current_timestamp = datetime.now()
    # spread = spread.append({'Best_Bid': best_bid, 'Best_Ask': best_ask, 'Timestamp': current_timestamp}, ignore_index=True)
    
    # volume = volume.append({'Bid': bid_vol, 'Ask': ask_vol, 'Timestamp': current_timestamp}, ignore_index=True)

    # Assuming spread and volume are your DataFrames
    data_spread = {'Best_Bid': [best_bid], 'Best_Ask': [best_ask], 'Timestamp': [current_timestamp]}
    data_volume = {'Bid': [bid_vol], 'Ask': [ask_vol], 'Timestamp': [current_timestamp]}
    
    # Convert dictionaries to DataFrames
    df_spread = pd.DataFrame(data_spread)
    df_volume = pd.DataFrame(data_volume)
    
    # Concatenate with existing DataFrames
    spread = pd.concat([spread, df_spread], ignore_index=True)
    volume = pd.concat([volume, df_volume], ignore_index=True)

    # Clear the previous plot
    clear_output(wait=True)
    plt.figure(figsize=(12,6))
    plt.title("Aggregated Orderbook BTC/USD")
    # Plot the updated cumulative sums for buy and sell sides
    plt.plot(orderbook['Price'], orderbook['Buy'], label='Buy')
    plt.plot(orderbook['Price'], orderbook['Sell'], label='Sell')
    
    
    plt.xlabel('Price')
    plt.ylabel('Cumulative Size')
    plt.legend()

    # Set the tick interval for the price axis to 25 dollars
    plt.xticks(range(int(min(orderbook['Price'])), int(max(orderbook['Price'])) + 1, 25))

    # Add text to display current price and buy/sell analysis within the price range
    plt.text(0.9, 0.8, f'Current Price: {current_price:.2f}', transform=plt.gca().transAxes, ha='right')
    plt.text(0.9, 0.75, f'Best Bid: {best_bid:.2f}', transform=plt.gca().transAxes, ha='right')
    plt.text(0.9, 0.7, f'Best Ask: {best_ask:.2f}', transform=plt.gca().transAxes, ha='right')
    plt.text(0.9, 0.65, f'Buy Size: {buy_size:.2f}', transform=plt.gca().transAxes, ha='right')
    plt.text(0.9, 0.6, f'Sell Size: {sell_size:.2f}', transform=plt.gca().transAxes, ha='right')

    plt.draw()
    
#     plt.pause(0.01)  # Add a small delay to allow the plot to update
    plt.figure(figsize=(12,6))
    plt.plot(spread['Timestamp'], spread['Best_Bid'], label='Best_Bid')
    plt.plot(spread['Timestamp'], spread['Best_Ask'], label='Best_Bid')

    plt.show()
    plt.pause(0.01)  # Add a small delay to allow the plot to update

    plt.figure(figsize=(12,6))
    plt.plot(volume['Timestamp'], volume['Bid'], label='Bid Volume')
    plt.plot(volume['Timestamp'], volume['Ask'], label='Ask Volume')

    plt.show()
    plt.pause(0.01)  # Add a small delay to allow the plot to update

    # Wait for the specified delay before the next iteration
    time.sleep(delay)
