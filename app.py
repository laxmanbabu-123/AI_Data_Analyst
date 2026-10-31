import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ---------- Page setup ----------
st.set_page_config(
    page_title="Enterprise AI Data Analyst",
    page_icon="📊",
    layout="wide",
)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetric"] {
        background: #F4F7FB;
        border: 1px solid #E2E8F0;
        padding: 18px 20px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #475569;
    }

    h1, h2, h3 {
        color: #152B4A;
    }

    .hero {
        padding: 24px 30px;
        border-radius: 16px;
        color: white;
        background: linear-gradient(110deg, #172554, #2563eb, #0891b2);
        margin-bottom: 22px;
    }

    .hero .eyebrow {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #bfdbfe;
        margin-bottom: 8px;
    }

    .hero h1 {
        color: white !important;
        font-size: 30px !important;
        line-height: 1.2;
        margin: 0;
    }

    .hero p {
        color: #e0f2fe;
        font-size: 15px;
        margin: 8px 0 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Load data ----------
sales_data = pd.read_csv("data/sample_sales.csv")
sales_data["OrderDate"] = pd.to_datetime(sales_data["OrderDate"])
sales_data["Sales"] = sales_data["Quantity"] * sales_data["UnitPrice"]

# ---------- Header ----------
header_col, status_col = st.columns([5, 1])

with header_col:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">SALES INTELLIGENCE</div>
            <h1>AI-Powered Sales Analytics Dashboard</h1>
            <p>Interactive business insights, powered by your sales data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with status_col:
    st.caption("AI assistant")
    st.info("API key loaded" if api_key else "Demo mode")

st.divider()

# ---------- Sidebar filters ----------
st.sidebar.title("Dashboard filters")

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

# ---------- Apply filters ----------
filtered_data = sales_data.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_data = filtered_data[
        (filtered_data["OrderDate"].dt.date >= start_date)
        & (filtered_data["OrderDate"].dt.date <= end_date)
    ]

if selected_region != "All":
    filtered_data = filtered_data[filtered_data["Region"] == selected_region]

if selected_product != "All":
    filtered_data = filtered_data[filtered_data["Product"] == selected_product]

# ---------- KPI cards ----------
st.subheader("Performance overview")

total_sales = filtered_data["Sales"].sum()
order_count = len(filtered_data)
units_sold = int(filtered_data["Quantity"].sum())
average_order_value = total_sales / order_count if order_count else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Total sales", f"₹{total_sales:,.0f}")
kpi2.metric("Orders", f"{order_count:,}")
kpi3.metric("Units sold", f"{units_sold:,}")
kpi4.metric("Average order value", f"₹{average_order_value:,.0f}")

st.divider()

# ---------- Charts ----------
chart_left, chart_right = st.columns(2)

with chart_left:
    st.subheader("Sales by region")
    sales_by_region = (
        filtered_data.groupby("Region")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(sales_by_region)

with chart_right:
    st.subheader("Monthly sales trend")
    monthly_sales = filtered_data.groupby(
        filtered_data["OrderDate"].dt.to_period("M")
    )["Sales"].sum()
    monthly_sales.index = monthly_sales.index.astype(str)
    st.line_chart(monthly_sales)

st.divider()

# ---------- Data table ----------
st.subheader("Detailed sales records")
st.caption(f"{len(filtered_data)} records match the selected filters.")

st.dataframe(
    filtered_data,
    use_container_width=True,
    hide_index=True,
)

csv_data = filtered_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered data as CSV",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv",
)

# ---------- Demo Q&A ----------
st.divider()
st.subheader("Ask the sales assistant")
st.caption("Demo answers use your filtered data; no OpenAI API call is made.")

question = st.text_input(
    "Ask a question about sales",
    placeholder="Example: Which region has the highest sales?",
)

if question:
    question_lower = question.lower()

    if "highest" in question_lower and "region" in question_lower:
        sales_by_region = filtered_data.groupby("Region")["Sales"].sum()

        if not sales_by_region.empty:
            best_region = sales_by_region.idxmax()
            best_sales = sales_by_region.max()
            st.success(
                f"{best_region} has the highest sales: ₹{best_sales:,.0f}"
            )
        else:
            st.warning("No sales data matches these filters.")

    elif "highest" in question_lower and "product" in question_lower:
        sales_by_product = filtered_data.groupby("Product")["Sales"].sum()

        if not sales_by_product.empty:
            best_product = sales_by_product.idxmax()
            best_sales = sales_by_product.max()
            st.success(
                f"{best_product} has the highest sales: ₹{best_sales:,.0f}"
            )
        else:
            st.warning("No sales data matches these filters.")

    elif "total" in question_lower and "sales" in question_lower:
        st.success(f"Total sales: ₹{total_sales:,.0f}")

    else:
        st.info(
            "Try asking about total sales, the highest-selling region, "
            "or the highest-selling product."
        )