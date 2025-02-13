import yfinance as yf
import pandas as pd
import ta
import time
import streamlit as st
import plotly.graph_objects as go

def get_period(interval):
    """Adjust period based on selected interval."""
    if interval == "1m":
        return "7d"  # Max 7 days for 1-minute data
    elif interval in ["5m", "15m"]:
        return "30d"
    elif interval in ["1h", "1d"]:
        return "60d"
    else:
        return "60d"

def fetch_data(symbol="BTC-USD", timeframe="1h", limit=100):
    try:
        period = get_period(timeframe)
        df = yf.download(symbol, period=period, interval=timeframe)
        if df.empty:
            raise ValueError("No data available for the selected timeframe.")
        df.reset_index(inplace=True)
        df.rename(columns={"Datetime": "timestamp", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}, inplace=True)
        return df[-limit:]
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def apply_indicators(df):
    if df.empty:
        return df
    df['SMA_50'] = ta.trend.sma_indicator(df['close'], window=50)
    df['SMA_200'] = ta.trend.sma_indicator(df['close'], window=200)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    df['MACD'] = ta.trend.macd(df['close'])
    return df

def generate_signal(df):
    if df.empty:
        return "NO DATA"
    latest = df.iloc[-1]
    if latest['RSI'] < 30 and latest['close'] > latest['SMA_200']:
        return "BUY"
    elif latest['RSI'] > 70 and latest['close'] < latest['SMA_50']:
        return "SELL"
    else:
        return "HOLD"

def plot_chart(df):
    if df.empty:
        st.warning("No data available to plot.")
        return
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Candlestick'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['SMA_50'], mode='lines', name='SMA 50'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['SMA_200'], mode='lines', name='SMA 200'))
    st.plotly_chart(fig)

def main():
    st.set_page_config(page_title="Crypto Trading Dashboard", layout="wide")
    st.title("📈 Crypto Trading Dashboard")
    
    symbol = st.selectbox("Select Symbol", ["BTC-USD", "ETH-USD", "BNB-USD"])
    timeframe = st.selectbox("Select Timeframe", ["1m", "5m", "15m", "1h", "1d"])
    
    with st.spinner("Fetching data..."):
        df = fetch_data(symbol, timeframe)
        df = apply_indicators(df)
        signal = generate_signal(df)
    
    st.subheader("💡 Trading Signal")
    st.success(f"Current Signal: **{signal}**")
    
    st.subheader("📊 Price Chart")
    plot_chart(df)
    
    st.subheader("📜 Indicator Values")
    if not df.empty:
        st.dataframe(df[['timestamp', 'close', 'SMA_50', 'SMA_200', 'RSI', 'MACD']].tail(10))
    else:
        st.warning("No data available.")

if __name__ == "__main__":
    main()
