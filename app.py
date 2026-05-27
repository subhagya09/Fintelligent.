import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests

# Configure ultra-wide, immersive dark-themed dashboard container
st.set_page_config(page_title="AlphaQuant Elite Terminal", layout="wide", initial_sidebar_state="expanded")

st.title("🦅 AlphaQuant Intelligence Terminal")
st.caption("Institutional Grade Quantitative Analytics • Smart Autocomplete Search Engine")

# ----------------------------------------------------
# SMART AUTOCOMPLETE SEARCH ENGINE (GROWW-STYLE)
# ----------------------------------------------------
st.sidebar.markdown("## 🎛️ Intelligent Market Search")
user_search_query = st.sidebar.text_input("Type Company Name (e.g., Rajputana, Reliance, Tata):", value="Rajputana")

selected_ticker = None
display_name = ""

if user_search_query.strip():
    try:
        # Query the global Yahoo Finance auto-suggest API to mimic a broker search bar
        search_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={user_search_query}&quotesCount=6&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers).json()
        
        search_results = response.get('quotes', [])
        
        if search_results:
            # Filter and format the results into a readable list for the dropdown box
            options_dict = {}
            for item in search_results:
                symbol = item.get('symbol', '')
                short_name = item.get('shortname', item.get('longname', 'Unknown Company'))
                exchange = item.get('exchange', '')
                
                # Create a clear option label showing company name, ticker symbol, and exchange
                label = f"{short_name} ({symbol}) [{exchange}]"
                options_dict[label] = (symbol, short_name)
            
            # Display matching results in an interactive dropdown selector
            dropdown_selection = st.sidebar.selectbox("Select Matching Asset From Registry:", list(options_dict.keys()))
            
            if dropdown_selection:
                selected_ticker, display_name = options_dict[dropdown_selection]
        else:
            st.sidebar.warning("⚠️ No matching assets found. Try adjusting your search term.")
    except Exception as search_error:
        st.sidebar.error("Autocomplete link temporarily offline. Reverting to manual entry.")
        selected_ticker = user_search_query.strip().upper()
        display_name = selected_ticker

# Fallback case if search bar is empty
if not selected_ticker:
    selected_ticker = "RELIANCE.NS"
    display_name = "Reliance Industries Limited"

# ----------------------------------------------------
# MAIN ENGINE ANALYTICS INGESTION
# ----------------------------------------------------
if selected_ticker:
    try:
        # Fetch data streams via selected asset ticker
        stock = yf.Ticker(selected_ticker)
        df_math = stock.history(period="1y")
        info = stock.info
        
        if df_math.empty:
            st.error(f"❌ Market feed for '{selected_ticker}' is currently empty or unlisted.")
            st.stop()

        # Dynamic currency localized formatting
        currency_symbol = "₹" if ".NS" in selected_ticker or ".BO" in selected_ticker else "$"
        company_final_title = info.get('longName', display_name)
        
        st.header(f"📊 {company_final_title} ({selected_ticker})")
        
        # Core Price Calculation Logic
        current_price = info.get('currentPrice') if info.get('currentPrice') is not None else df_math['Close'].iloc[-1]
        prev_close = info.get('previousClose') if info.get('previousClose') is not None else current_price
        price_change = current_price - prev_close
        pct_change = (price_change / prev_close) * 100 if prev_close else 0
        
        # Top-Row Core Summary Metrics Cards
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Live Execution Price", f"{currency_symbol}{current_price:,.2f}", f"{price_change:+,.2f} ({pct_change:+.2f}%)")
        with m_col2:
            st.metric("Market Capitalization", f"{currency_symbol}{info.get('marketCap', 0):,}" if info.get('marketCap') else "N/A")
        with m_col3:
            target_mean = info.get('targetMeanPrice', 'N/A')
            target_display = f"{currency_symbol}{target_mean:,.2f}" if isinstance(target_mean, (int, float)) else "N/A"
            st.metric("Consensus Target Estimate", target_display)
        with m_col4:
            div_rate = info.get('dividendYield', 0)
            div_display = f"{div_rate * 100:.2f}%" if div_rate else "0.00%"
            st.metric("Trailing Dividend Yield", div_display)

        st.markdown("---")

        # ----------------------------------------------------
        # EXPANDED RATIOS MATRIX SECTION
        # ----------------------------------------------------
        st.subheader("📈 Institutional Valuation & Core Financial Ratios")
        
        ratio_col1, ratio_col2 = st.columns(2)
        
        with ratio_col1:
            st.markdown("#### 🏷️ Valuation & Pricing Multiples")
            
            # Helper function to clean up and structure ratio displays cleanly
            def format_ratio(val, is_pct=False, is_multiplier=False):
                if val is None or val == 'N/A': return "N/A"
                if is_pct: return f"{val * 100:.2f}%"
                if is_multiplier: return f"{val:.2f}x"
                return f"{val:.2f}"

            valuation_ratios = {
                "Trailing Price-to-Earnings (P/E Ratio)": format_ratio(info.get('trailingPE'), is_multiplier=True),
                "Forward P/E Ratio (1-Year Projection)": format_ratio(info.get('forwardPE'), is_multiplier=True),
                "Price-to-Earnings-Growth (PEG Ratio)": format_ratio(info.get('pegRatio')),
                "Price-to-Book Value (P/B Ratio)": format_ratio(info.get('priceToBook'), is_multiplier=True),
                "Enterprise Value-to-EBITDA (EV/EBITDA)": format_ratio(info.get('enterpriseToEbitda'), is_multiplier=True),
                "Price-to-Sales (P/S Ratio)": format_ratio(info.get('priceToSales'), is_multiplier=True),
                "Trailing Dividend Yield Percentage": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "0.00%"
            }
            
            val_df = pd.DataFrame({
                "Valuation Metric Analysis Vector": list(valuation_ratios.keys()),
                "Current Registry Value": list(valuation_ratios.values())
            })
            st.table(val_df)

        with ratio_col2:
            st.markdown("#### 🛡️ Solvency, Profitability & Efficiency Ratios")
            
            efficiency_solvency_ratios = {
                "Return on Equity (ROE Core)": format_ratio(info.get('returnOnEquity'), is_pct=True),
                "Return on Assets (ROA Core)": format_ratio(info.get('returnOnAssets'), is_pct=True),
                "Net Corporate Profit Margins": format_ratio(info.get('profitMargins'), is_pct=True),
                "Operating Profit Margins (EBIT)": format_ratio(info.get('operatingMargins'), is_pct=True),
                "Total Debt-to-Equity Multiplier (D/E)": format_ratio(info.get('debtToEquity')),
                "Current Liquidity Ratio": format_ratio(info.get('currentRatio'), is_multiplier=True),
                "Year-over-Year Revenue Growth Velocity": format_ratio(info.get('revenueGrowth'), is_pct=True)
            }
            
            eff_df = pd.DataFrame({
                "Financial Health Analysis Vector": list(efficiency_solvency_ratios.keys()),
                "Current Registry Value": list(efficiency_solvency_ratios.values())
            })
            st.table(eff_df)

        st.markdown("---")

        # ----------------------------------------------------
        # OPERATIONAL ROADMAP & CHARTING
        # ----------------------------------------------------
        st.subheader("🏢 Corporate Operational Blueprint & Macro Profile")
        with st.expander("👁️ Click to view full business overview roadmap", expanded=False):
            st.write(info.get('longBusinessSummary', 'Corporate operational blueprint description not currently filed in public registry.'))

        st.markdown("### 📈 Live Structural Candlestick Framework (1-Year Core Window)")
        chart_figure = go.Figure(data=[go.Candlestick(
            x=df_math.index,
            open=df_math['Open'],
            high=df_math['High'],
            low=df_math['Low'],
            close=df_math['Close'],
            name="Candlestick"
        )])
        chart_figure.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(chart_figure)

    except Exception as e:
        st.error(f"Platform core engine encountered an extraction error. Trace: {e}")
        
