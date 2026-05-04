import streamlit as st
import pandas as pd
import plotly.express as px
import os

def load_css():
    with open("dashboard/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.set_page_config(
    page_title="Retail Dashboard", 
    layout="wide",
    initial_sidebar_state="collapsed"
    )

#loading dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rfm = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "rfm_data.csv"))
forecast = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "forecast.csv"))
data = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv"))

st.markdown(
    """
    <h1 class="main-title">RETAIL ANALYTICS DASHBOARD</h1>
    """,
    unsafe_allow_html=True
)

#sidebar filters
st.sidebar.title("Filters")

#cluster filter
clusters = st.sidebar.multiselect(
    "Select Cluster",
    options=sorted(rfm["Cluster"].unique()),
    default=sorted(rfm["Cluster"].unique())
)

rfm_filtered = rfm[rfm["Cluster"].isin(clusters)]

# Date filter
data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"])

min_date = data["InvoiceDate"].min()
max_date = data["InvoiceDate"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date]
)

# Apply date filter
filtered_data = data[
    (data["InvoiceDate"] >= pd.to_datetime(date_range[0])) &
    (data["InvoiceDate"] <= pd.to_datetime(date_range[1]))
]


#KPIs
total_revenue = filtered_data["TotalPrice"].sum()
total_customers = filtered_data["Customer ID"].nunique()

#Export button
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.download_button(
    label="Download Filtered Data",
    data=filtered_data.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)

#churn fallback logic
churn_rate = 0
if "Churn" in rfm.columns:
    churn_rate = rfm["Churn"].mean()
else:
    churn_rate = 0

#Cards
c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.metric("Revenue", f"{total_revenue:,.0f}")

with c2:
    st.metric("Customers", total_customers)

with c3:
    st.metric("Churn Rate", f"{churn_rate:.2f}")

st.markdown("<br><br>", unsafe_allow_html=True)


# ---------------01 Customer Segmentation - RFM ----------------------
st.header("Customer Segmentation")

if "Cluster" in rfm.columns:
    
    rfm_sample = (
        rfm_filtered.groupby("Cluster", group_keys=False)
        .apply(lambda x: x.sample(min(len(x), 300)))
    )
    
    fig1 = px.scatter(
        rfm_sample,
        x="Recency",
        y="Monetary",
        color="Cluster",        
        title="Customer Segmentation (RFM)",        
        color_continuous_scale="Blues",
        opacity=0.7
    )

    fig1.update_traces(
        marker=dict(size=7, line=dict(width=0))
        )

    fig1.update_layout(
        template="plotly_dark",
        height=600,
        autosize=True,
        margin=dict(l=40, r=40, t=50, b=40),
    )

    st.plotly_chart(
        fig1, 
        use_container_width=True, 
        config={
            "displayModeBar": True,
            "scrollZoom": False
            }
    )
else:
    st.warning("Segment column not found in RFM")

#st.markdown("## Customer Insights")
st.markdown("---")



# -----------------02 Sales Forecast Segment-------------------
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
        autosize=True,
        margin=dict(l=40, r=40, t=50, b=40),
        height=600
    )
    st.plotly_chart(
        fig2, 
        use_container_width=True, 
        config={
            "displayModeBar": True,
            "scrollZoom": False
        }
    )
else:
    st.warning("Check forecast column names")

#st.markdown("## Sales Forecast")
st.markdown("---")




# ---------------------03 Top Products Segment--------------------
st.header("Top Products")

if "Description" in data.columns and "TotalPrice" in data.columns:
    top_products = (
        filtered_data.groupby("Description")["TotalPrice"]
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
        #margin=dict(l=150),
        autosize=True,
        yaxis=dict(autorange="reversed"),
        margin=dict(l=40, r=40, t=50, b=40),
        height=600
    )
    st.plotly_chart(
        fig3, 
        use_container_width=True, 
        config={
            "displayModeBar": True,
            "scrollZoom": False
        }
    )
else:
    st.warning("Product columns missing")
    
#st.markdown("## Top Products")
st.markdown("---")