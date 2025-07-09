import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

st.set_page_config(page_title="Meteo Bari Candlestick", layout="wide")
st.title("📈 Grafico Meteo – Candlestick a Timeframe Variabile")
timeframe = st.selectbox("Timeframe", ["1H (orario)", "1D (giornaliero)", "1W (settimanale)", "1M (mensile)"])

# ======== Scarica dati meteo da Open-Meteo (ultimi 30 giorni) ========
lat, lon = 41.1171, 16.8719  # Bari
url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&timezone=Europe%2FRome&past_days=30"
data = requests.get(url).json()

# Costruisci DataFrame
df = pd.DataFrame({
    "time": pd.to_datetime(data["hourly"]["time"]),
    "temp": data["hourly"]["temperature_2m"]
})
df.set_index("time", inplace=True)

# ======== Aggregazione per Timeframe ========
if timeframe == "1H (orario)":
    ohlc = df.resample("1H").agg({'temp': ['first', 'max', 'min', 'last']})
elif timeframe == "1D (giornaliero)":
    ohlc = df.resample("1D").agg({'temp': ['first', 'max', 'min', 'last']})
elif timeframe == "1W (settimanale)":
    ohlc = df.resample("1W").agg({'temp': ['first', 'max', 'min', 'last']})
else:
    ohlc = df.resample("1M").agg({'temp': ['first', 'max', 'min', 'last']})

ohlc.columns = ["open", "high", "low", "close"]
ohlc.dropna(inplace=True)

# ======== Converti la data in formato numerico (Unix timestamp) ========
ohlc['timestamp'] = ohlc.index.astype(int) / 10**9  # Unix timestamp

# ======== Grafico Candlestick con colori personalizzati e tooltip in italiano ========
threshold = 25  # Soglia per il caldo (ad esempio, 25°C)
colors = ['red' if x > threshold else 'blue' for x in ohlc['close']]  # Colore rosso per temperature alte, blu per basse

fig = go.Figure(data=[go.Candlestick(
    x=ohlc['timestamp'],  # Usando il timestamp numerico
    open=ohlc['open'],
    high=ohlc['high'],
    low=ohlc['low'],
    close=ohlc['close'],
    increasing_line_color='red',  # Rosso per temperatura alta
    decreasing_line_color='blue',  # Blu per temperatura bassa
    hovertemplate='<b>Data</b>: %{x|%d-%m-%Y %H:%M}<br><b>Temperatura</b>: %{y}°C<br>'  # Tooltip in italiano con formato data
)])

fig.update_layout(
    xaxis_title='Data',
    yaxis_title='Temperatura (°C)',
    template='plotly_dark',
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)
