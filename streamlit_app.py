import pandas as pd
import requests
import streamlit as st
import time
from datetime import datetime
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource

class Exchange:
    def __init__(self, name, api_url):
        self.name = name
        self.api_url = api_url

    def fetch_orderbook(self):
        raise NotImplementedError()

class Coinbase(Exchange):
    def fetch_orderbook(self):
        response = requests.get(self.api_url + 'products/BTC-USD/book?level=2')
        data = response.json()
        bids = pd.DataFrame(data['bids'], columns=['Price', 'Size', '_'])
        bids['Side'] = 'buy'
        asks = pd.DataFrame(data['asks'], columns=['Price', 'Size', '_'])
        asks['Side'] = 'sell'
        return pd.concat([bids, asks], ignore_index=True)

def main():
    # Initialize exchange objects
    binance = Coinbase('Coinbase', 'https://api.pro.coinbase.com/')
    # Fetch orderbook data
    binance_orderbook = binance.fetch_orderbook()
    binance_orderbook = binance_orderbook[['Price', 'Size', 'Side']]
    # Select only the relevant columns for each DataFrame
    # Concatenate the modified DataFrames
    orderbook = binance_orderbook.sort_values(by=['Price'], ascending=False).reset_index(drop=True)
    orderbook['Price'] = orderbook['Price'].astype(float)
    orderbook['Size'] = orderbook['Size'].astype(float)

    return orderbook

def plot_orderbook(orderbook):
    p = figure(title="Aggregated Orderbook BTC/USD", x_axis_label='Price', y_axis_label='Cumulative Size', width=800, height=400)
    p.line(x='Price', y='Buy', source=orderbook, legend_label='Buy', line_color='blue')
    p.line(x='Price', y='Sell', source=orderbook, legend_label='Sell', line_color='red')
    p.legend.location = "top_left"
    p.xaxis.ticker = list(range(int(min(orderbook['Price'])), int(max(orderbook['Price'])) + 1, 25))
    st.bokeh_chart(p, use_container_width=True)

if __name__ == "__main__":
    st.title("Binance Orderbook Analysis")
    delay = 0.2
    price_range = 50
    while True:
        orderbook = main()
        orderbook['Buy'] = orderbook[orderbook['Side'] == 'buy']['Size'].cumsum()
        orderbook['Sell'] = orderbook[orderbook['Side'] == 'sell']['Size'][::-1].cumsum()
        current_price =float(requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot").json()["data"]["amount"])   
        price_min = current_price - price_range
        price_max = current_price + price_range
        buy_size = orderbook[(orderbook['Price'] >= price_min) & (orderbook['Price'] <= price_max) & (orderbook['Side'] == 'buy')]['Size'].sum()
        sell_size = orderbook[(orderbook['Price'] >= price_min) & (orderbook['Price'] <= price_max) & (orderbook['Side'] == 'sell')]['Size'].sum()
        best_ask = orderbook[pd.notna(orderbook["Sell"])]['Price'].min()
        best_bid = orderbook[pd.notna(orderbook["Buy"])]['Price'].max()
        current_timestamp = datetime.now()
        data_spread = {'Best_Bid': [best_bid], 'Best_Ask': [best_ask], 'Timestamp': [current_timestamp]}
        data_volume = {'Bid': [buy_size], 'Ask': [sell_size], 'Timestamp': [current_timestamp]}
        df_spread = pd.DataFrame(data_spread)
        df_volume = pd.DataFrame(data_volume)
        st.text("Plotting Orderbook")
        plot_orderbook(orderbook)
        time.sleep(delay)

        # st.text("Plotting Spread")
        # plt.figure(figsize=(12, 6))
        # plt.plot(df_spread['Timestamp'], df_spread['Best_Bid'], label='Best_Bid')
        # plt.plot(df_spread['Timestamp'], df_spread['Best_Ask'], label='Best_Ask')
        # st.pyplot(plt)
        # st.text("Plotting Volume")
        # plt.figure(figsize=(12, 6))
        # plt.plot(df_volume['Timestamp'], df_volume['Bid'], label='Bid Volume')
        # plt.plot(df_volume['Timestamp'], df_volume['Ask'], label='Ask Volume')
        # st.pyplot(plt)
        # time.sleep(delay)
