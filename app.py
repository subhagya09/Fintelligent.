import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

st.set_page_config(page_title="AlphaQuant Elite Terminal", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0a0e1a; }
    .main .block-container { padding: 1.5rem 2rem; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #1f2937; }
    .metric-card {
        background: linear-gradient(135deg, #0d1117 0%, #161b27 100%);
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    h1, h2, h3 { color: #e2e8f0 !important; }
    .stMetric label { color: #94a3b8 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
    .stMetric [data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 1.4rem !important; font-weight: 600; }
    .stMetric [data-testid="stMetricDelta"] { font-size: 0.85rem !important; }
    div[data-testid="stTable"] { background: #0d1117; border-radius: 10px; border: 1px solid #1f2937; }
    div[data-testid="stTable"] table { color: #cbd5e1; }
    div[data-testid="stTable"] thead tr th { background-color: #161b27 !important; color: #94a3b8 !important; border-bottom: 1px solid #1f2937 !important; }
    div[data-testid="stTable"] tbody tr:nth-child(even) { background-color: #0d1117; }
    div[data-testid="stTable"] tbody tr:nth-child(odd) { background-color: #111827; }
    .stSelectbox > div > div { background-color: #0d1117 !important; border: 1px solid #1f2937 !important; color: #e2e8f0 !important; }
    .stTextInput > div > div > input { background-color: #0d1117 !important; border: 1px solid #1f2937 !important; color: #e2e8f0 !important; }
    .stExpander { background-color: #0d1117; border: 1px solid #1f2937; border-radius: 10px; }
    .bull-badge { background: #064e3b; color: #34d399; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .bear-badge { background: #450a0a; color: #f87171; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .neutral-badge { background: #1c1917; color: #fbbf24; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 11])
with col_logo:
    st.markdown("<div style='font-size:2.5rem;margin-top:4px'>🦅</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin:0;font-size:1.8rem;background:linear-gradient(90deg,#60a5fa,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>AlphaQuant Elite Terminal</h1>", unsafe_allow_html=True)
    st.caption("Institutional-grade quantitative analytics · Smart autocomplete search")

st.markdown("---")

# ── SIDEBAR SEARCH ─────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎛️ Market Search")
st.sidebar.markdown("Search any company worldwide")
user_search_query = st.sidebar.text_input("Company name or ticker:", value="Reliance", placeholder="e.g. Apple, RELIANCE, Tesla")

selected_ticker, display_name = None, ""

if user_search_query.strip():
    try:
        search_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={user_search_query}&quotesCount=8&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers, timeout=5).json()
        search_results = response.get('quotes', [])

        if search_results:
            options_dict = {}
            for item in search_results:
                symbol = item.get('symbol', '')
                short_name = item.get('shortname', item.get('longname', 'Unknown'))
                exchange = item.get('exchange', '')
                label = f"{short_name} ({symbol}) [{exchange}]"
                options_dict[label] = (symbol, short_name)
            dropdown_selection = st.sidebar.selectbox("Select from results:", list(options_dict.keys()))
            if dropdown_selection:
                selected_ticker, display_name = options_dict[dropdown_selection]
        else:
            st.sidebar.warning("No results found. Try a different term.")
    except Exception:
        st.sidebar.error("Search offline. Using manual entry.")
        selected_ticker = user_search_query.strip().upper()
        display_name = selected_ticker

if not selected_ticker:
    selected_ticker = "RELIANCE.NS"
    display_name = "Reliance Industries"

st.sidebar.markdown("---")
st.sidebar.markdown("**Popular Stocks**")
popular = {
    "🇮🇳 Reliance": "RELIANCE.NS", "🇮🇳 TCS": "TCS.NS", "🇮🇳 Infosys": "INFY.NS",
    "🇮🇳 HDFC Bank": "HDFCBANK.NS", "🇺🇸 Apple": "AAPL", "🇺🇸 Tesla": "TSLA",
    "🇺🇸 Microsoft": "MSFT", "🇺🇸 Nvidia": "NVDA"
}
for name, ticker in popular.items():
    if st.sidebar.button(name, use_container_width=True, key=f"btn_{ticker}"):
        selected_ticker = ticker
        display_name = name

# ── MAIN DATA ──────────────────────────────────────────────────────────────────
if selected_ticker:
    try:
        with st.spinner(f"Loading data for {selected_ticker}..."):
            stock = yf.Ticker(selected_ticker)
            df = stock.history(period="1y")
            info = stock.info

        if df.empty:
            st.error(f"❌ No data found for '{selected_ticker}'. Try a different ticker.")
            st.stop()

        cs = "₹" if (".NS" in selected_ticker or ".BO" in selected_ticker) else "$"
        company_name = info.get('longName', display_name)
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')

        current_price = info.get('currentPrice') or df['Close'].iloc[-1]
        prev_close = info.get('previousClose') or current_price
        price_change = current_price - prev_close
        pct_change = (price_change / prev_close) * 100 if prev_close else 0
        change_emoji = "📈" if price_change >= 0 else "📉"

        # ── COMPANY HEADER ────────────────────────────────────────────────────
        h1, h2 = st.columns([8, 2])
        with h1:
            st.markdown(f"<h2 style='margin-bottom:2px'>{change_emoji} {company_name}</h2>", unsafe_allow_html=True)
            st.caption(f"**{selected_ticker}** · {sector} · {industry}")
        with h2:
            week_52_low = info.get('fiftyTwoWeekLow', df['Low'].min())
            week_52_high = info.get('fiftyTwoWeekHigh', df['High'].max())
            position_pct = ((current_price - week_52_low) / (week_52_high - week_52_low) * 100) if (week_52_high - week_52_low) else 50
            badge_class = "bull-badge" if position_pct > 60 else ("bear-badge" if position_pct < 30 else "neutral-badge")
            badge_label = "🐂 Bullish Zone" if position_pct > 60 else ("🐻 Bearish Zone" if position_pct < 30 else "⚖️ Neutral Zone")
            st.markdown(f"<div style='text-align:right;margin-top:12px'><span class='{badge_class}'>{badge_label}</span></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── KPI CARDS ─────────────────────────────────────────────────────────
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Live Price", f"{cs}{current_price:,.2f}", f"{price_change:+,.2f} ({pct_change:+.2f}%)")
        with c2:
            mcap = info.get('marketCap', 0)
            mcap_str = f"{cs}{mcap/1e12:.2f}T" if mcap > 1e12 else (f"{cs}{mcap/1e9:.1f}B" if mcap > 1e9 else (f"{cs}{mcap/1e7:.0f}Cr" if mcap else "N/A"))
            st.metric("Market Cap", mcap_str)
        with c3:
            target = info.get('targetMeanPrice')
            target_str = f"{cs}{target:,.2f}" if target else "N/A"
            upside = ((target - current_price) / current_price * 100) if target else None
            up_str = f"{upside:+.1f}% upside" if upside else ""
            st.metric("Analyst Target", target_str, up_str)
        with c4:
            st.metric("52W High", f"{cs}{week_52_high:,.2f}")
        with c5:
            st.metric("52W Low", f"{cs}{week_52_low:,.2f}")

        st.markdown("---")

        # ── CHART ─────────────────────────────────────────────────────────────
        tab1, tab2, tab3 = st.tabs(["📊 Candlestick Chart", "📉 Price & Volume", "🔥 Returns Heatmap"])

        with tab1:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                increasing_line_color='#34d399', decreasing_line_color='#f87171', name="OHLC"))
            df['MA20'] = df['Close'].rolling(20).mean()
            df['MA50'] = df['Close'].rolling(50).mean()
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#60a5fa', width=1.5), name='MA 20'))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], line=dict(color='#a78bfa', width=1.5), name='MA 50'))
            fig.update_layout(template="plotly_dark", paper_bgcolor='#0d1117', plot_bgcolor='#0d1117',
                xaxis_rangeslider_visible=False, height=450,
                legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8')),
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis=dict(gridcolor='#1f2937'), yaxis=dict(gridcolor='#1f2937'))
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig2 = go.Figure()
            colors = ['#34d399' if c >= o else '#f87171' for c, o in zip(df['Close'], df['Open'])]
            fig2.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume', yaxis='y2', opacity=0.4))
            fig2.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#60a5fa', width=2), name='Close Price'))
            fig2.update_layout(template="plotly_dark", paper_bgcolor='#0d1117', plot_bgcolor='#0d1117',
                height=420, margin=dict(l=10, r=10, t=20, b=10),
                yaxis=dict(gridcolor='#1f2937'),
                yaxis2=dict(overlaying='y', side='right', showgrid=False),
                xaxis=dict(gridcolor='#1f2937'))
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            df['Month'] = df.index.strftime('%b %Y')
            df['DayOfWeek'] = df.index.day_name()
            df['DailyReturn'] = df['Close'].pct_change() * 100
            monthly = df.groupby('Month')['DailyReturn'].mean().reset_index()
            monthly.columns = ['Month', 'Avg Daily Return (%)']
            fig3 = px.bar(monthly, x='Month', y='Avg Daily Return (%)',
                color='Avg Daily Return (%)', color_continuous_scale=['#f87171','#1f2937','#34d399'],
                title="Monthly Average Daily Return")
            fig3.update_layout(template="plotly_dark", paper_bgcolor='#0d1117', plot_bgcolor='#0d1117',
                height=380, margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(gridcolor='#1f2937', tickangle=-45), yaxis=dict(gridcolor='#1f2937'))
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")

        # ── RATIOS ────────────────────────────────────────────────────────────
        st.subheader("📈 Financial Ratios Matrix")

        def fmt(val, pct=False, mult=False):
            if val is None: return "—"
            if pct: return f"{val*100:.2f}%"
            if mult: return f"{val:.2f}×"
            return f"{val:.2f}"

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown("**🏷️ Valuation**")
            st.table(pd.DataFrame({
                "Metric": ["Trailing P/E", "Forward P/E", "PEG Ratio", "Price/Book", "EV/EBITDA", "Price/Sales"],
                "Value": [fmt(info.get('trailingPE'), mult=True), fmt(info.get('forwardPE'), mult=True),
                          fmt(info.get('pegRatio')), fmt(info.get('priceToBook'), mult=True),
                          fmt(info.get('enterpriseToEbitda'), mult=True), fmt(info.get('priceToSalesTrailing12Months'), mult=True)]
            }))
        with rc2:
            st.markdown("**🛡️ Profitability**")
            st.table(pd.DataFrame({
                "Metric": ["ROE", "ROA", "Profit Margin", "Operating Margin", "Gross Margin", "EBITDA Margin"],
                "Value": [fmt(info.get('returnOnEquity'), pct=True), fmt(info.get('returnOnAssets'), pct=True),
                          fmt(info.get('profitMargins'), pct=True), fmt(info.get('operatingMargins'), pct=True),
                          fmt(info.get('grossMargins'), pct=True), fmt(info.get('ebitdaMargins'), pct=True)]
            }))
        with rc3:
            st.markdown("**⚙️ Growth & Health**")
            div_yield = info.get('dividendYield', 0)
            st.table(pd.DataFrame({
                "Metric": ["Revenue Growth", "Earnings Growth", "Debt/Equity", "Current Ratio", "Quick Ratio", "Dividend Yield"],
                "Value": [fmt(info.get('revenueGrowth'), pct=True), fmt(info.get('earningsGrowth'), pct=True),
                          fmt(info.get('debtToEquity')), fmt(info.get('currentRatio'), mult=True),
                          fmt(info.get('quickRatio'), mult=True),
                          f"{div_yield*100:.2f}%" if div_yield else "0.00%"]
            }))

        st.markdown("---")

        # ── BUSINESS OVERVIEW ─────────────────────────────────────────────────
        with st.expander("🏢 Business Overview & Company Profile"):
            bio_col, stat_col = st.columns([3, 1])
            with bio_col:
                st.write(info.get('longBusinessSummary', 'No description available.'))
            with stat_col:
                st.markdown("**Quick Stats**")
                st.write(f"👥 Employees: {info.get('fullTimeEmployees', 'N/A'):,}" if info.get('fullTimeEmployees') else "👥 Employees: N/A")
                st.write(f"🌍 Country: {info.get('country', 'N/A')}")
                st.write(f"🌐 Website: [{info.get('website', 'N/A')}]({info.get('website', '#')})")
                st.write(f"📅 Fiscal Year End: {info.get('fiscalYearEnd', 'N/A')}")

        st.markdown("---")
        st.caption("⚠️ AlphaQuant is for informational purposes only. Not financial advice. Data via Yahoo Finance.")

    except Exception as e:
        st.error(f"Error loading data: {e}")
