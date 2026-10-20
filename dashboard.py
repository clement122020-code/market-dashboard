import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Market Dash", layout="centered")
st.title("📈 Live Market Dashboard")

st.subheader("CBOE Volatility Index (VIX)")

# 1. Fetch maximum historical data
vix = yf.Ticker("^VIX")
vix_data = vix.history(period="max")

if not vix_data.empty:
    current_vix = vix_data['Close'].iloc[-1]
    st.metric(label="Current VIX", value=f"{current_vix:.2f}")
    
    # 2. Build the interactive Plotly chart
    fig = go.Figure(data=[go.Scatter(
        x=vix_data.index, 
        y=vix_data['Close'], 
        mode='lines', 
        line=dict(color='purple', width=2),
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Price: %{y:.2f}<extra></extra>' 
    )])
    
    # 3. Configure time frame buttons and mobile crosshairs
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=7, label="1W", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=5, label="5Y", step="year", stepmode="backward"),
                    dict(step="all", label="Max")
                ]),
                font=dict(size=10) # Smaller font for mobile screens
            ),
            type="date",
            showspikes=True, # Shows vertical line
            spikemode="across",
            spikesnap="cursor",
            showline=True,
        ),
        yaxis=dict(
            fixedrange=False, # Allows vertical zooming if needed
        ),
        hovermode="x unified", # Essential for the mobile tap-and-drag tooltip
        height=400, 
        margin=dict(l=10, r=10, t=10, b=10),
        dragmode="pan" # Makes dragging chart easier on mobile
    )
    
    # config={'displayModeBar': False} hides the top-right tool menu for a cleaner mobile look
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.subheader("📅 US Economic Calendar")

@st.cache_data(ttl=3600) # Cache data for 1 hour to save API credits
def get_fmp_calendar():
    # Get today's date formatted as YYYY-MM-DD
    today = datetime.today().strftime('%Y-%m-%d')
    api_key = "yuxjXWrEB64h28szh2cQgdUPPRvQyNyL"
    
    # Query the FMP API for today's events
    url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={today}&to={today}&apikey={api_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            # Filter for US events only and select relevant columns
            us_events = df[df['country'] == 'US']
            if not us_events.empty:
                # Clean up the dataframe for display
                us_events = us_events[['date', 'event', 'actual', 'estimate', 'previous', 'impact']]
                us_events.rename(columns={
                    'date': 'Time', 'event': 'Event', 'actual': 'Actual', 
                    'estimate': 'Estimate', 'previous': 'Previous', 'impact': 'Impact'
                }, inplace=True)
                return us_events
    return pd.DataFrame()

try:
    calendar_df = get_fmp_calendar()
    if not calendar_df.empty:
        st.dataframe(calendar_df, use_container_width=True, hide_index=True)
    else:
        st.info("No US economic events scheduled for today.")
except Exception as e:
    st.error(f"Failed to fetch calendar data: {e}")
