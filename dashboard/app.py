import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.markdown(
    """
<style>
h1, h2, h3 {
    font-weight: 600;
}
</style>
    """, 
unsafe_allow_html=True
)

st.set_page_config(page_title="Retail Dashboard", layout="wide")

#loading dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rfm = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "rfm_data.csv"))
forecast = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "forecast.csv"))
data = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv"))

#KPIs
total_revenue = data["TotalPrice"].sum() if "TotalPrice" in data.columns else 0
total_customers = data["Customer ID"].nunique() if "Customer ID" in data.columns else 0

#churn fallback logic
churn_rate = 0
if "Churn" in rfm.columns:
    churn_rate = rfm["Churn"].mean()
else:
    churn_rate = 0    


st.title("Retail Analytics Dashboard")

#Cards
c1, c2, c3 = st.columns(3)

c1.metric("Revenue", f"{total_revenue:,.0f}")
c2.metric("Customers", total_customers)
c3.metric("Churn Rate", f"{churn_rate:.2f}")

st.markdown("---")



# Customer Segmentation - RFM 
st.header("Customer Segmentation")

if "Cluster" in rfm.columns:
    fig1 = px.scatter(
        rfm,
        x="Recency",
        y="Monetary",
        color="Cluster",
        title="Customer Segmentation (RFM)",
        color_continuous_scale="Blues",
        opacity=0.6
    )

    fig1.update_traces(marker=dict(size=6))

    fig1.update_layout(
        template="plotly_dark",
        height=600,
        xaxis_title="Recency (Days)",
        yaxis_title="Monetary Value",
    )

    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("Segment column not found in RFM")

st.markdown("---")



#Sales Forecast Segment
st.header("Sales Forecast")

forecast = forecast.rename(columns={
    "ds": "Date",
    "yhat": "Sales"
})

if "Date" in forecast.columns and "Sales" in forecast.columns:
    fig2 = px.line(
        forecast,
        x="Date",
        y="Sales",
        title="Sales Forecast",
    )
    
    fig2.update_traces(line=dict(width=3))

    fig2.update_layout(
        template="plotly_dark",
        title_font_size=20,
        xaxis_title="Date",
        yaxis_title="Sales",
        height=600
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("Check forecast column names")

st.markdown("---")



#Top Products Segment
st.header("Top Products")

if "Description" in data.columns and "TotalPrice" in data.columns:
    top_products = (
        data.groupby("Description")["TotalPrice"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig3 = px.bar(
        top_products,
        x="TotalPrice",
        y="Description",
        orientation="h",
        title="Top 10 Products by Revenue",
        color="TotalPrice",
        color_continuous_scale="Blues"
    )

    fig3.update_layout(
        template="plotly_dark",
        title_font_size=20,
        xaxis_title="Revenue",
        yaxis_title="Product",
        margin=dict(l=150),
        yaxis=dict(autorange="reversed"),
        height=600
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("Product columns missing")