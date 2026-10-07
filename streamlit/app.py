import os
import streamlit as st
import duckdb
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="E-Commerce Trend & Quality Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Clean Custom Styling ---
st.markdown("""
<style>
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- DuckDB Connection (Read-Only) ---
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "dbt_ecommerce" / "dev.duckdb"
db_path = os.getenv("DUCKDB_PATH", str(DEFAULT_DB_PATH))

# --- Load Data from Physical Mart Tables (Sub-millisecond local disk query) ---
@st.cache_data(ttl=600)
def load_all_data():
    if not os.path.exists(db_path):
        st.error(f"Database not found at: `{db_path}`. Please run `dbt run` first!")
        st.stop()

    q_trends = """
        SELECT 
            category,
            review_year,
            review_month,
            CAST(review_month_date AS DATE) AS month_date,
            total_reviews,
            positive_count,
            negative_count,
            uncertain_count
        FROM fct_category_monthly_trend
        WHERE review_year = 2023
        ORDER BY month_date ASC
    """
    q_products = """
        SELECT 
            parent_asin,
            category,
            title,
            main_category,
            total_reviews,
            negative_count,
            negative_rate,
            avg_rating
        FROM fct_product_sentiment_summary
    """
    q_spikes = """
        SELECT 
            parent_asin,
            category,
            title,
            CAST(review_month_date AS DATE) AS month_date,
            monthly_reviews,
            monthly_negative_count,
            monthly_neg_rate,
            baseline_avg_neg_rate,
            z_score,
            neg_rate_jump_pts,
            alert_severity
        FROM fct_product_spike_alert
        WHERE is_negative_spike = 1
        ORDER BY z_score DESC
    """
    with duckdb.connect(database=db_path, read_only=True) as con:
        df_t = con.execute(q_trends).df()
        df_p = con.execute(q_products).df()
        df_s = con.execute(q_spikes).df()
    return df_t, df_p, df_s

df_trends, df_products, df_spikes = load_all_data()

# --- Sidebar Controls ---
st.sidebar.title("Filters & Settings")
categories = ["All Categories"] + sorted(df_trends["category"].unique().tolist())
selected_cat = st.sidebar.selectbox("Select Category:", categories)

st.sidebar.markdown("---")
st.sidebar.markdown("**System Architecture:**")
st.sidebar.markdown("- **Data Lake:** MinIO S3 (Parquet)")
st.sidebar.markdown("- **Engine:** Apache Spark & Linear SVM")
st.sidebar.markdown("- **Data Marts:** dbt-DuckDB")
st.sidebar.markdown("- **Query Latency:** Sub-millisecond (Local Disk)")

if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Filter datasets by selected category
if selected_cat != "All Categories":
    f_trends = df_trends[df_trends["category"] == selected_cat]
    f_products = df_products[df_products["category"] == selected_cat]
    f_spikes = df_spikes[df_spikes["category"] == selected_cat]
else:
    f_trends = df_trends
    f_products = df_products
    f_spikes = df_spikes

# --- Main Dashboard Header ---
st.markdown('<div class="main-title">E-Commerce Review Trend & Quality Intelligence Dashboard</div>', unsafe_allow_html=True)

# --- Top Level KPIs ---
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
total_reviews = f_trends["total_reviews"].sum()
total_pos = f_trends["positive_count"].sum()
total_neg = f_trends["negative_count"].sum()
pos_rate = round((total_pos / total_reviews) * 100, 1) if total_reviews > 0 else 0
neg_rate = round((total_neg / total_reviews) * 100, 1) if total_reviews > 0 else 0

col_kpi1.metric("Total Reviews", f"{total_reviews:,.0f}")
col_kpi2.metric("Positive Sentiment", f"{pos_rate:.1f}%")
col_kpi3.metric("Negative Sentiment", f"{neg_rate:.1f}%")
col_kpi4.metric("Active Defect Spikes", f"{len(f_spikes):,d}", delta_color="inverse")

# --- Tabs Navigation ---
tab1, tab2, tab3 = st.tabs([
    "1. Monthly Trends",
    "2. Top Defective Products",
    "3. Defect Spike Alerts"
])

with tab1:
    target_cats = sorted(f_trends["category"].unique().tolist())
    for cat in target_cats:
        st.markdown(f"#### Category: `{cat}` (Year 2023)")
        cat_df = f_trends[f_trends["category"] == cat].sort_values(by="month_date").copy()
        cat_df["total_reviews"] = pd.to_numeric(cat_df["total_reviews"], errors="coerce").fillna(0).astype(int)
        cat_df["positive_count"] = pd.to_numeric(cat_df["positive_count"], errors="coerce").fillna(0).astype(int)
        cat_df["negative_count"] = pd.to_numeric(cat_df["negative_count"], errors="coerce").fillna(0).astype(int)
        
        # Line chart with exactly 3 lines
        fig_cat = go.Figure()
        
        # Line 1: Total reviews
        fig_cat.add_trace(go.Scatter(
            x=cat_df["month_date"],
            y=cat_df["total_reviews"],
            mode="lines+markers",
            name="1. Total Reviews",
            line=dict(color="#2563eb", width=3)
        ))
        
        # Line 2: Positive reviews
        fig_cat.add_trace(go.Scatter(
            x=cat_df["month_date"],
            y=cat_df["positive_count"],
            mode="lines+markers",
            name="2. Positive Reviews",
            line=dict(color="#16a34a", width=2.5)
        ))
        
        # Line 3: Negative reviews
        fig_cat.add_trace(go.Scatter(
            x=cat_df["month_date"],
            y=cat_df["negative_count"],
            mode="lines+markers",
            name="3. Negative Reviews",
            line=dict(color="#dc2626", width=2.5)
        ))
        
        fig_cat.update_layout(
            title=f"Monthly Review Dynamics (2023) - {cat}",
            xaxis_title="Month",
            yaxis_title="Review Count",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=50, b=20)
        )
        st.plotly_chart(fig_cat, width="stretch")
        
        # Detailed table for category
        with st.expander(f"View Detailed Monthly Table - {cat}"):
            cat_table = cat_df[["month_date", "total_reviews", "positive_count", "negative_count"]].copy()
            cat_table.columns = ["Month", "Total Reviews", "Positive Reviews", "Negative Reviews"]
            st.dataframe(cat_table, width="stretch")
        

with tab2:
    top10_neg = f_products.sort_values(by="negative_count", ascending=False).head(10).copy()
    top10_neg["negative_count"] = pd.to_numeric(top10_neg["negative_count"], errors="coerce").fillna(0).astype(int)
    top10_neg["total_reviews"] = pd.to_numeric(top10_neg["total_reviews"], errors="coerce").fillna(0).astype(int)
    top10_neg["negative_rate"] = pd.to_numeric(top10_neg["negative_rate"], errors="coerce").fillna(0.0).astype(float)
    top10_neg["avg_rating"] = pd.to_numeric(top10_neg["avg_rating"], errors="coerce").fillna(0.0).astype(float)
    
    # Y-axis displays ASIN code only
    top10_neg["label"] = top10_neg["parent_asin"]
    
    # Bar text: Negative count / Total reviews (Rate %)
    top10_neg["bar_text"] = [
        f" {n:,d}/ {t:,d}/ ({r:.1f}%)"
        for n, t, r in zip(top10_neg["negative_count"], top10_neg["total_reviews"], top10_neg["negative_rate"])
    ]
    
    # Horizontal Bar Chart
    fig_top10 = go.Figure()
    fig_top10.add_trace(go.Bar(
        y=top10_neg["label"],
        x=top10_neg["negative_count"],
        orientation="h",
        text=top10_neg["bar_text"],
        textposition="outside",
        marker=dict(color="#ef4444"),
        hoverinfo="text",
        hovertext=[
            f"ASIN: {asin}<br>Product: {title}<br>Negative Reviews: {n:,d}<br>Total Reviews: {t:,d}<br>Negative Rate: {r:.1f}%<br>Avg Rating: {rating:.2f}"
            for asin, title, n, t, r, rating in zip(
                top10_neg["parent_asin"], top10_neg["title"], 
                top10_neg["negative_count"], top10_neg["total_reviews"], top10_neg["negative_rate"],
                top10_neg["avg_rating"]
            )
        ]
    ))
    
    fig_top10.update_layout(
        title="Top 10 Products with Highest Negative Review Volume",
        xaxis_title="Negative Review Count",
        yaxis_title="Product ASIN",
        yaxis=dict(autorange="reversed"),
        height=520,
        margin=dict(l=10, r=220, t=40, b=30)
    )
    st.plotly_chart(fig_top10, width="stretch")
    
    # Detailed Table
    st.markdown("##### Detailed Top 10 Defective Products Table")
    display_top10 = top10_neg[[
        "parent_asin", "title", "category", "negative_count", "total_reviews", "negative_rate", "avg_rating"
    ]].copy().reset_index(drop=True)
    display_top10.index = display_top10.index + 1
    display_top10.index.name = "Rank"
    
    st.dataframe(
        display_top10,
        width="stretch",
        column_config={
            "parent_asin": st.column_config.TextColumn("ASIN", width="small"),
            "title": st.column_config.TextColumn("Product Title", width="large"),
            "category": st.column_config.TextColumn("Category"),
            "negative_count": st.column_config.NumberColumn("Negative Reviews"),
            "total_reviews": st.column_config.NumberColumn("Total Reviews"),
            "negative_rate": st.column_config.NumberColumn("Negative Rate (%)", format="%.2f%%"),
            "avg_rating": st.column_config.NumberColumn("Avg Rating", format="%.2f ⭐")
        }
    )

with tab3:
    col_s1, col_s2, col_s3 = st.columns(3)
    num_crit = len(f_spikes[f_spikes["alert_severity"] == "CRITICAL_SURGE"])
    num_warn = len(f_spikes[f_spikes["alert_severity"] == "WARNING_SPIKE"])
    avg_jump = f_spikes["neg_rate_jump_pts"].mean() if len(f_spikes) > 0 else 0
    
    col_s1.metric("Critical Surges", f"{num_crit:,d}", help="Z-score >= 3.0, severe defect surge")
    col_s2.metric("Warning Spikes", f"{num_warn:,d}", help="Z-score >= 2.0, abnormal complaint spike")
    col_s3.metric("Avg Negative Rate Jump", f"+{avg_jump:.1f}%", help="Percentage point increase over 3-month baseline")

    st.markdown("##### Real-Time Product Defect Spike Incidents")
    
    # Spike table
    st.dataframe(
        f_spikes[[
            "alert_severity", "month_date", "parent_asin", "title",
            "monthly_reviews", "monthly_neg_rate", "baseline_avg_neg_rate", "neg_rate_jump_pts", "z_score"
        ]],
        width="stretch",
        column_config={
            "alert_severity": st.column_config.TextColumn("Severity Level"),
            "month_date": st.column_config.DateColumn("Spike Month"),
            "parent_asin": st.column_config.TextColumn("ASIN"),
            "title": st.column_config.TextColumn("Product Title", width="large"),
            "monthly_reviews": st.column_config.NumberColumn("Monthly Reviews"),
            "monthly_neg_rate": st.column_config.NumberColumn("Current Neg Rate", format="%.1f%%"),
            "baseline_avg_neg_rate": st.column_config.NumberColumn("3-Month Baseline Rate", format="%.1f%%"),
            "neg_rate_jump_pts": st.column_config.NumberColumn("Jump (pts)", format="+%.1f%%"),
            "z_score": st.column_config.NumberColumn("Z-Score", format="%.2f")
        }
    )

st.markdown("---")
st.caption("E-Commerce User Review Sentiment & Trend Intelligence | Powered by Apache Spark, Linear SVM, dbt-DuckDB & Streamlit")
