import finnhub
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import Flask, render_template, request

#Transitioning to Flask application
app = Flask(__name__)

#Configuring Finnhub API
finnhub_client = finnhub.Client(api_key='cgd294pr01qum7u5r1o0cgd294pr01qum7u5r1og')

#Specifying stock based on user input
@app.route('/', methods=['GET', 'POST'])
def get_stock():
    if request.method == 'POST':
    #Get user input
        stock = request.form['stock'] #Getting symbol from form input

        #Specifying data time range
        start_date = '2021-01-01'
        end_date = '2022-01-01'

        #Retrieving the historical data from the API
        res = finnhub_client.stock_candles(stock, 'D', int(pd.Timestamp(start_date).timestamp()), int(pd.Timestamp(end_date).timestamp()))

        #Pandas dataframe from API
        df = pd.DataFrame({'Date': pd.to_datetime(res['t'], unit='s'), 'Open': res['o'], 'High': res['h'], 'Low': res['l'], 'Close': res['c'], 'Volume': res['v'] })
        df.set_index('Date', inplace=True)

        #Calculating our Bollinger bands
        window_size = 20
        df['MA'] = df['Close'].rolling(window=window_size).mean()
        df['STD'] = df['Close'].rolling(window=window_size).std()
        df['Upper Band'] = df['MA'] + 2 * df['STD']
        df['Lower Band'] = df['MA'] - 2 * df['STD']

        #Converting to HA format
        ha_open = (df['Open'].shift(1) + df['Close'].shift(1)) / 2
        ha_close = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
        ha_high = df[['High', 'Open', 'Close']].max(axis=1)
        ha_low = df[['Low', 'Open', 'Close']].min(axis=1)
        df_ha = pd.DataFrame({'HA_Open': ha_open, 'HA_High': ha_high, 'HA_Low': ha_low, 'HA_Close': ha_close})
        df_ha.index = df.index

        #Plotting HA chart with Bollinger bands
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True)

        fig.add_trace (
            go.Candlestick(x=df_ha.index, open=df_ha['HA_Open'], high=df_ha['HA_High'], low=df_ha['HA_Low'], close=df_ha['HA_Close'], name="Heiken-Ashi Chart")
        )

        fig.add_trace (
            go.Scatter(x=df.index, y=df['Upper Band'], name='Upper Band', line=dict(color='grey')), row=1, col=1
        )

        fig.add_trace (
            go.Scatter(x=df.index, y=df['Lower Band'], name='Lower Band', line=dict(color='grey')), row=1, col=1
        )

        fig.update_layout(xaxis_rangeslider_visible=True)
        return fig.to_html(full_html=False)
    else:
        return render_template('homepage.html')

if __name__ == '__main__':
    app.run(debug=True)