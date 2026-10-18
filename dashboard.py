import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from market_calendar_tool import scrape_calendar

st.set_page_config(page_title="Market Dash", layout="centered")
st.title("📈 Live Market Dashboard")

st.subheader("CBOE Volatility Index (VIX)")
vix = yf.Ticker("^VIX")
vix_data = vix.history(period="1d", interval="1m")

if not vix_data.empty:
    current_vix = vix_data['Close'].iloc[-1]
    st.metric(label="Current VIX", value=f"{current_vix:.2f}")
    
    fig = go.Figure(data=[go.Scatter(x=vix_data.index, y=vix_data['Close'], mode='lines', line=dict(color='purple'))])
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("📅 US Economic Calendar")
try:
    calendar_data = scrape_calendar() 
    if calendar_data and hasattr(calendar_data, 'base'):
        st.dataframe(calendar_data.base, use_container_width=True)
    else:
        st.info("No major economic events found for today.")
except Exception as e:
    st.error(f"Calendar data currently unavailable: {e}")