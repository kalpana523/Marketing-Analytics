import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Marketing Campaign Intelligence",
    page_icon="hq",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI polish
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
    }
    .stWarning {
        background-color: #fff3cd;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA GENERATION & NOISE INJECTION
# ==========================================

@st.cache_data
def generate_marketing_data(n_rows=500):
    """Generates a realistic synthetic marketing dataset."""
    np.random.seed(42)
    dates = [datetime(2025, 1, 1) + timedelta(days=x) for x in range(n_rows)]
    channels = ['Facebook', 'Google Ads', 'Email', 'Instagram', 'LinkedIn']
    
    data = []
    for date in dates:
        channel = np.random.choice(channels)
        if channel == 'Email':
            impressions, spend_range = np.random.randint(1000, 5000), (50, 200)
            ctr_range, conv_range = (0.05, 0.10), (0.05, 0.15)
        elif channel == 'Google Ads':
            impressions, spend_range = np.random.randint(5000, 20000), (500, 1500)
            ctr_range, conv_range = (0.02, 0.05), (0.03, 0.08)
        else:
            impressions, spend_range = np.random.randint(3000, 10000), (200, 800)
            ctr_range, conv_range = (0.01, 0.04), (0.02, 0.06)
            
        spend = np.random.uniform(*spend_range)
        clicks = int(impressions * np.random.uniform(*ctr_range))
        conversions = int(clicks * np.random.uniform(*conv_range))
        revenue = conversions * np.random.uniform(50, 150)
        
        data.append([date, channel, spend, impressions, clicks, conversions, revenue])
        
    df = pd.DataFrame(data, columns=['Date', 'Channel', 'Spend', 'Impressions', 'Clicks', 'Conversions', 'Revenue'])
    return df

def inject_noise(df):
    """
    Intentionally corrupts data to demonstrate cleaning capabilities.
    Adds duplicates, NaNs, and string formatting errors.
    """
    df_dirty = df.copy()
    
    # 1. Add Duplicates (duplicate random 5% of rows)
    n_dupes = int(len(df) * 0.05)
    duplicates = df.sample(n_dupes)
    df_dirty = pd.concat([df_dirty, duplicates], ignore_index=True)
    
    # 2. Add Null Values (randomly set 5% of Spend/Revenue to NaN)
    for col in ['Spend', 'Revenue', 'Clicks']:
        mask = np.random.random(len(df_dirty)) < 0.05
        df_dirty.loc[mask, col] = np.nan

    # 3. Add String/Formatting Errors (e.g., "$100.00" instead of 100.00)
    # Convert some random Spend values to strings with '$'
    mask_currency = np.random.random(len(df_dirty)) < 0.05
    df_dirty.loc[mask_currency, 'Spend'] = df_dirty.loc[mask_currency, 'Spend'].apply(lambda x: f"${x:.2f}" if pd.notnull(x) else x)
    
    return df_dirty

# ==========================================
# 3. DATA CLEANING MODULE
# ==========================================

def clean_data_pipeline(df):
    """
    The core cleaning logic.
    Returns: cleaned_df, cleaning_log (list of strings describing actions)
    """
    log = []
    df_clean = df.copy()
    
    # 1. Remove Duplicates
    orig_rows = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    new_rows = len(df_clean)
    if orig_rows > new_rows:
        log.append(f"✅ Removed {orig_rows - new_rows} duplicate rows.")
    
    # 2. Handle Currency Strings (Cleaning "$", ",")
    cols_to_clean = ['Spend', 'Revenue']
    for col in cols_to_clean:
        if df_clean[col].dtype == 'object':
            # Convert to string, strip symbols, convert to numeric
            df_clean[col] = df_clean[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            log.append(f"✅ Fixed formatting in '{col}' column (removed currency symbols).")

    # 3. Handle Missing Values
    # Fill numeric NaNs with 0 (assuming missing spend/revenue means 0)
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    null_counts = df_clean[numeric_cols].isnull().sum().sum()
    if null_counts > 0:
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
        log.append(f"✅ Filled {null_counts} missing values with 0.")

    # 4. Standardize Date
    if 'Date' in df_clean.columns:
        df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')
        # Drop rows where date failed to parse
        date_nulls = df_clean['Date'].isnull().sum()
        if date_nulls > 0:
            df_clean = df_clean.dropna(subset=['Date'])
            log.append(f"⚠️ Dropped {date_nulls} rows with invalid dates.")

    if not log:
        log.append("✅ Data appears clean. No changes needed.")
        
    return df_clean, log

def calculate_kpis(df):
    """Calculates enriched metrics for analysis."""
    # Ensure standard types just in case
    for col in ['Spend', 'Impressions', 'Clicks', 'Conversions', 'Revenue']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['CTR'] = np.where(df['Impressions'] > 0, df['Clicks'] / df['Impressions'], 0)
    df['Conversion_Rate'] = np.where(df['Clicks'] > 0, df['Conversions'] / df['Clicks'], 0)
    df['CPC'] = np.where(df['Clicks'] > 0, df['Spend'] / df['Clicks'], 0)
    df['ROI'] = np.where(df['Spend'] > 0, (df['Revenue'] - df['Spend']) / df['Spend'], 0)
    return df

# ==========================================
# 4. SIDEBAR & DATA LOADING
# ==========================================
st.sidebar.header("🗂️ Data Controls")

data_source = st.sidebar.radio("Select Data Source", ["Generate Synthetic Data", "Upload CSV"])
raw_df = None

if data_source == "Generate Synthetic Data":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Simulation Settings")
    
    # Feature to add dirty data
    add_noise = st.sidebar.checkbox("Inject Random Errors", help="Adds duplicates, missing values, and formatting errors to demonstrate data cleaning.")
    
    if st.sidebar.button("Generate Data"):
        raw_df = generate_marketing_data()
        if add_noise:
            raw_df = inject_noise(raw_df)
            st.session_state['data_generated'] = True
            st.session_state['raw_df'] = raw_df
            st.session_state['is_dirty'] = True
        else:
            st.session_state['data_generated'] = True
            st.session_state['raw_df'] = raw_df
            st.session_state['is_dirty'] = False
            
elif data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload Campaign CSV", type=['csv'])
    if uploaded_file:
        raw_df = pd.read_csv(uploaded_file)
        st.session_state['raw_df'] = raw_df
        st.session_state['is_dirty'] = True # Assume uploaded data might need cleaning

# Retrieve from session state if available
if 'raw_df' in st.session_state:
    df_working = st.session_state['raw_df']
else:
    df_working = None

# ==========================================
# 5. MAIN UI LAYOUT
# ==========================================

st.title("🚀 Marketing Campaign Intelligence System")

# Only show dashboard if data exists
if df_working is not None:
    
    # --- STEP 1: DATA CLEANING SECTION ---
    with st.expander("🧹 Data Cleaning & Preprocessing", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Raw Data Preview")
            st.dataframe(df_working.head(), height=150)
            
            # Show Health Stats
            n_rows = len(df_working)
            n_dupes = df_working.duplicated().sum()
            n_nulls = df_working.isnull().sum().sum()
            
            st.markdown(f"""
            **Health Check:**
            - Total Rows: `{n_rows}`
            - Duplicates: `{n_dupes}` {( "⚠️" if n_dupes > 0 else "✅")}
            - Missing Values: `{n_nulls}` {( "⚠️" if n_nulls > 0 else "✅")}
            """)

        with col2:
            st.subheader("Cleaning Pipeline")
            st.write("The pipeline performs: Deduplication, Numeric Standardization, Null Imputation (0), and Date Parsing.")
            
            if st.button("Run Auto-Clean Pipeline", key="clean_btn"):
                cleaned_df, logs = clean_data_pipeline(df_working)
                st.session_state['clean_df'] = cleaned_df
                st.session_state['clean_logs'] = logs
                st.rerun()

        # Show Cleaning Results if Cleaned
        if 'clean_df' in st.session_state:
            st.success("Data Successfully Cleaned!")
            for msg in st.session_state['clean_logs']:
                st.write(msg)
            
            # Use the cleaned data for the rest of the app
            final_df = calculate_kpis(st.session_state['clean_df'])
        else:
            st.warning("Using Raw Data (Data might be dirty). Click 'Run Auto-Clean Pipeline' above.")
            final_df = calculate_kpis(df_working)

    st.divider()

    # --- STEP 2: DASHBOARD (Uses final_df) ---
    # Global Filters
    st.sidebar.header("🔍 Analysis Filters")
    channels = final_df['Channel'].unique()
    selected_channels = st.sidebar.multiselect("Filter Channels", channels, default=channels)
    
    if selected_channels:
        final_df = final_df[final_df['Channel'].isin(selected_channels)]

    # Top Level Metrics
    total_spend = final_df['Spend'].sum()
    total_revenue = final_df['Revenue'].sum()
    total_roi = (total_revenue - total_spend) / total_spend if total_spend > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Spend", f"${total_spend:,.0f}")
    m2.metric("Total Revenue", f"${total_revenue:,.0f}")
    m3.metric("ROI", f"{total_roi:.2%}", delta_color="normal")
    m4.metric("Conversion Rate", f"{final_df['Conversion_Rate'].mean():.2%}")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Performance Analysis", "📉 Trends", "💾 Data Export"])

    with tab1:
        st.subheader("Channel Efficiency Analysis")
        
        c_grp = final_df.groupby('Channel').agg({
            'Spend': 'sum', 'Revenue': 'sum', 'ROI': 'mean', 'CTR': 'mean'
        }).reset_index()
        
        col_a, col_b = st.columns(2)
        with col_a:
            fig_roi = px.bar(c_grp, x='Channel', y='ROI', title="ROI by Channel", color='ROI', color_continuous_scale='RdBu')
            st.plotly_chart(fig_roi, use_container_width=True)
        
        with col_b:
            fig_scat = px.scatter(final_df, x='CTR', y='Conversion_Rate', color='Channel', size='Spend', 
                                title="CTR vs Conversion Rate (Size = Spend)", hover_data=['ROI'])
            st.plotly_chart(fig_scat, use_container_width=True)

    with tab2:
        st.subheader("Time Series Analysis")
        # Ensure date sorting
        ts_df = final_df.sort_values('Date')
        metric = st.selectbox("Select Metric", ['Revenue', 'Spend', 'Conversions', 'Clicks'])
        
        fig_line = px.line(ts_df, x='Date', y=metric, color='Channel', title=f"Daily {metric} Trends")
        st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.subheader("Automated Reporting")
        st.write("Download the cleaned, processed dataset for further analysis.")
        
        csv_buffer = io.StringIO()
        final_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Cleaned Data (CSV)",
            data=csv_buffer.getvalue(),
            file_name="cleaned_marketing_data.csv",
            mime="text/csv"
        )

else:
    st.info("👈 Use the sidebar to Generate Data or Upload a CSV to begin.")