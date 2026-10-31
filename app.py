import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
st.write("API key loaded:", bool(api_key))

st.title("Enterprise AI Data Analyst")

# Load and prepare the original data.
sales_data = pd.read_csv("data/sample_sales.csv")
sales_data["OrderDate"] = pd.to_datetime(sales_data["OrderDate"])
sales_data["Sales"] = sales_data["Quantity"] * sales_data["UnitPrice"]

# Sidebar filters.
st.sidebar.header("Filters")

date_range = st.sidebar.date_input(
    "Order date range",
    value=(
        sales_data["OrderDate"].min().date(),
        sales_data["OrderDate"].max().date(),
    ),
)

selected_region = st.sidebar.selectbox(
    "Region",
    ["All"] + sorted(sales_data["Region"].unique().tolist()),
)

selected_product = st.sidebar.selectbox(
    "Product",
    ["All"] + sorted(sales_data["Product"].unique().tolist()),
)

# Apply the selected filters without changing the original data.
filtered_data = sales_data.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_data = filtered_data[
        (filtered_data["OrderDate"].dt.date >= start_date)
        & (filtered_data["OrderDate"].dt.date <= end_date)
    ]

if selected_region != "All":
    filtered_data = filtered_data[
        filtered_data["Region"] == selected_region
    ]

if selected_product != "All":
    filtered_data = filtered_data[
        filtered_data["Product"] == selected_product
    ]

# Summary metrics.
st.subheader("Sales Summary")
total_sales = filtered_data["Sales"].sum()
st.metric("Total Sales", f"₹{total_sales:,.0f}")

col1, col2 = st.columns(2)

with col1:
    st.metric("Orders", len(filtered_data))

with col2:
    st.metric("Units Sold", int(filtered_data["Quantity"].sum()))

# Filtered data table.
st.subheader("Sales Data")
st.dataframe(filtered_data, use_container_width=True)

# Sales by region.
st.subheader("Sales by Region")
sales_by_region = filtered_data.groupby("Region")["Sales"].sum()
st.bar_chart(sales_by_region)

# Monthly sales.
st.subheader("Monthly Sales")
monthly_sales = filtered_data.groupby(
    filtered_data["OrderDate"].dt.to_period("M")
)["Sales"].sum()
monthly_sales.index = monthly_sales.index.astype(str)
st.line_chart(monthly_sales)

# Download filtered data.
csv_data = filtered_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered data",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv",
)

# Ask a question about the filtered sales data.
st.subheader("Ask a question")

question = st.text_input(
    "Ask about sales",
    placeholder="Example: Which region has the highest sales?",
)

if question:
    question_lower = question.lower()

    if "highest" in question_lower and "region" in question_lower:
        sales_by_region = filtered_data.groupby("Region")["Sales"].sum()

        if not sales_by_region.empty:
            best_region = sales_by_region.idxmax()
            best_sales = sales_by_region.max()
            st.write(f"{best_region} has the highest sales: ₹{best_sales:,.0f}")
        else:
            st.write("No sales data matches the selected filters.")

    elif "highest" in question_lower and "product" in question_lower:
        sales_by_product = filtered_data.groupby("Product")["Sales"].sum()

        if not sales_by_product.empty:
            best_product = sales_by_product.idxmax()
            best_sales = sales_by_product.max()
            st.write(f"{best_product} has the highest sales: ₹{best_sales:,.0f}")
        else:
            st.write("No sales data matches the selected filters.")

    elif "total" in question_lower and "sales" in question_lower:
        total_sales = filtered_data["Sales"].sum()
        st.write(f"Total sales: ₹{total_sales:,.0f}")

    else:
        st.write(
            "I can answer questions about highest-selling regions, "
            "highest-selling products, and total sales."
        )