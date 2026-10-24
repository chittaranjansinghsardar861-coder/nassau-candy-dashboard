import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Nassau Candy Profitability Analytics", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("nassau_candy_small.csv")
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Analytics Controls")
selected_divisions = st.sidebar.multiselect("Select Product Division", options=df['Division'].unique(), default=df['Division'].unique())
min_margin = st.sidebar.slider("Minimum Gross Margin (%)", float(df['Gross Margin (%)'].min()), float(df['Gross Margin (%)'].max()), 0.0)
search_query = st.sidebar.text_input("Product Search", "")

# Filter dataframe
filtered_df = df[(df['Division'].isin(selected_divisions)) & (df['Gross Margin (%)'] >= min_margin)]
if search_query:
    filtered_df = filtered_df[filtered_df['Product Name'].str.contains(search_query, case=False, na=False)]

# --- MAIN DASHBOARD ---
st.title("🍬 Nassau Candy Distributor - Profitability & Margin Performance")
st.markdown("### Executive Intelligence Dashboard | Author: Krishta Singh Sardar")

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${filtered_df['Sales'].sum():,.2f}")
col2.metric("Total Gross Profit", f"${filtered_df['Gross Profit'].sum():,.2f}")
col3.metric("Avg Gross Margin", f"{filtered_df['Gross Margin (%)'].mean():.2f}%")
col4.metric("Total Orders", f"{len(filtered_df):,}")

st.divider()

# --- TABS FOR MODULES ---
tab1, tab2, tab3, tab4 = st.tabs(["Product Overview", "Division Performance", "Cost vs Margin Diagnostics", "Profit Concentration (Pareto)"])

with tab1:
    st.subheader("Product-Level Margin Leaderboard")
    prod_agg = filtered_df.groupby(['Product Name', 'Division'])[['Sales', 'Gross Profit', 'Gross Margin (%)']].mean().reset_index()
    prod_agg = prod_agg.sort_values(by='Gross Profit', ascending=False)
    st.dataframe(prod_agg, use_container_width=True)

with tab2:
    st.subheader("Division Performance: Revenue vs Gross Profit")
    div_agg = filtered_df.groupby('Division')[['Sales', 'Gross Profit']].sum().reset_index()
    fig = px.bar(div_agg, x='Division', y=['Sales', 'Gross Profit'], barmode='group', title="Revenue vs Profit by Division")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Cost vs Sales Scatter Diagnostics")
    fig_scatter = px.scatter(filtered_df.sample(min(1000, len(filtered_df))), x='Cost', y='Sales', color='Division', hover_data=['Product Name', 'Gross Margin (%)'], title="Cost vs Sales Distribution")
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    st.subheader("Profit Concentration Analysis (Top Products)")
    top_prods = filtered_df.groupby('Product Name')['Gross Profit'].sum().reset_index().sort_values(by='Gross Profit', ascending=False).head(10)
    fig_pareto = px.bar(top_prods, x='Product Name', y='Gross Profit', title="Top 10 Profit-Driving Products")
    st.plotly_chart(fig_pareto, use_container_width=True)
