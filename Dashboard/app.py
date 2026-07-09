import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIGURATION

st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    layout="centered"
)

# CUSTOM CSS

st.markdown(
    """
    <style>

    .main {
    background-color: #f8f9fa;
    }

    .title-card {
    background: linear-gradient(135deg, #6fe37, #d2691e);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    color: white;
    margin-bottom: 25px;
    } 

    .metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
    }

    h2, h3 {
    color: #4b2e2e;
    }

    #MainMenu {
        visibility:hidden;
    }

    footer {
       visibility:hidden;
    }


    </style>
    """,
    unsafe_allow_html=True
)

# LOAD DATASET
df = pd.read_csv(
    "Data/final_nassau_dashboard_data.csv"
)

# CONVERT DATA COLUMN

df['Order Date'] = pd.to_datetime(
    df['Order Date']
)

# DASHBOARD TITLE

st.markdown(
    """
    <div class="title-card">

    <h1>🍬 Nassau Candy Analytics Dashboard</h1>

    <h4>
    Product Line Profitability & Margin Performance Analysis
    </h4>

    </div>
    """,
    unsafe_allow_html=True
)

# SIDEBAR FILTERS (moved above dataset preview so filtered_df is defined)

st.sidebar.title(
    " 🍫Nassau Controls "
)

st.sidebar.write(
    " Filter Dashboard Insights "
)

st.sidebar.divider()

st.sidebar.header(" 🔎Dashboard Filters ")

# DATE RANGE FILTER

date_range = st.sidebar.date_input(
    " Select Date Range ",
    [
        df['Order Date'].min(),
        df['Order Date'].max()
    ]

)

division = st.sidebar.multiselect(
    "Select Division",
    options=df['Division'].unique(),
    default=df['Division'].unique()
)

# PRODUCT SEARCH

product_search = st.sidebar.text_input(
    "Search Product"
)

filtered_df = df[
    df['Division'].isin(division)
]

if product_search:
    filtered_df = filtered_df[
        filtered_df['Product Name']
        .str.contains(
            product_search,
            case=False
        )
    ]

# MARGIN THRESHOLD SLIDER

margin_limit = st.sidebar.slider(
    "Minimum Gross Margin %",
    0,
    100,
    0
)

filtered_df = filtered_df[
    filtered_df['Gross Margin %']
    >= margin_limit
]

# APPLY DATE FILTERS

if len(date_range) == 2:

    start_date = pd.to_datetime(
        date_range[0]
    )

    end_date = pd.to_datetime(
        date_range[1]
    )
filtered_df = filtered_df[
    (filtered_df['Order Date'] >= start_date)
    &
    (filtered_df['Order Date'] <= end_date)
]    

# DATASET PREVIEW

with st.expander("🗂️ View Preview"):
   st.dataframe(filtered_df.head(20))

# KPI CALCULATIONS

total_revenue = filtered_df['Sales'].sum()

total_profit = filtered_df['Gross Profit'].sum()

average_margin = filtered_df['Gross Margin %'].mean()

total_units = filtered_df['Units'].sum()


# KPI CARDS

st.subheader(
    "## 📌 Business Performance Overview "
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💲Revenue ",
        f"${total_revenue:,.0f}"
    )
with col2:
    st.metric(
        " 📈Profit ",
        f"${total_profit:,.0f}"
    )    
with col3:
    st.metric(
        " 📊Margin ",
        f"{average_margin:.2f}%"
    )
with col4:
    st.metric(
        " 📦Units ",
        f"{total_units:,}"
    )        

# DIVISION PERFORMANCE ANALYSIS

st.divider()

st.subheader(" 🗂️Division Performance Analysis ")

division_summary = filtered_df.groupby(
    'Division',
    as_index=False
).agg(
    {
        'Sales':'sum',
        'Gross Profit':'sum'
    }
)

division_summary.rename(
    columns={
        'Sales':'Revenue',
        'Gross Profit':'Profit'
    },
    inplace=True
)

fig_division = px.bar(
    division_summary,
    x='Division',
    y=['Revenue','Profit'],
    barmode='group',
    title=" 💰Revenue vs Profit by Division ",
    template="plotly_white"
)

fig_division.update_layout(
    height=450,
    xaxis_title="Product Division",
    yaxis_title="Amount ($)"
)

st.plotly_chart(
    fig_division,
    use_container_width=True
)

# PRODUCT PROFIT LEADERBOARD

st.divider()

st.subheader(" 🏆Top Product Profitability Ranking")

top_products = (
    filtered_df.groupby(
        'Product Name',
        as_index=False
    )
    .agg(
        Revenue=('Sales','sum'),
        Profit=('Gross Profit', 'sum'),
        Avg_Margin=('Gross Margin %','mean')
    )
    .sort_values(
        by='Profit',
        ascending=False
    )
    .head(10)
)

st.dataframe(top_products)

fig_product = px.bar(
    top_products,
    x="Profit",
    y="Product Name",
    orientation="h",
    title=" 🏆Top 10 Products by Gross Profit ",
    template="plotly_white"
)

fig_product.update_layout(
    height=500,
    xaxis_title="Gross Profit ($)",
    yaxis_title="Products"
)

st.plotly_chart(
    fig_product,
    use_container_width=True
)

# COST vs MARGIN DIAGNOSTICS

st.divider()

st.subheader(" 🚩Cost vs Margin Diagnostics")

fig_cost_margin = px.scatter(
    filtered_df,
    x="Cost",
    y="Sales",
    size="Gross Profit",
    color="Margin Status",
    hover_data=[
        "Product Name",
        "Division",
        "Gross Margin %"
    ],
    title=" 🚩Cost vs Sales  Margin Diagnotics ",
    template="plotly_white"
)

fig_cost_margin.update_layout(
    height=500,
    xaxis_title="Manfacturing Cost",
    yaxis_title="Sales Revenue"
)

st.plotly_chart(
    fig_cost_margin,
    use_container_width=True
)

# PARETO PROFIT ANALYSIS

st.divider()

st.subheader(" 📈Pareto 80/20 Profit Analysis")

pareto = (
    filtered_df.groupby(
        'Product Name',
        as_index=False
    )
    ['Gross Profit']
    .sum()
)

pareto = pareto.sort_values(
    by = 'Gross Profit',
    ascending = False
)

pareto['Cumulative Profit %'] = (
    pareto['Gross Profit'].cumsum()
    /
    pareto['Gross Profit'].sum()
) * 100

fig_pareto = px.line(
    pareto,
    x="Product Name",
    y="Cumulative Profit %",
    markers=True,
    title=" 📈Pareto 80/20 Profit Contribution ",
    template="plotly_white"
)

fig_pareto.update_layout(
    height=450,
    xaxis_title="Products",
    yaxis_title="Cumulative Profit %"
)

st.plotly_chart(
    fig_pareto,
    use_container_width=True
)

# BUSINESS RECOMMENDATIONS

st.divider()

st.subheader("💡Business Recommendations")

st.success(
"""
High margin products should recieve stronger promotion
& inventory priority.
"""    
)

st.warning(
"""
Low margin products require pricing review,
supplier negotitation, or cost optimization.
"""    
)

st.info(
"""
Pareto analysis helps identyfy products responsible
for majority profit contribution and reduces dependency risk
"""    
)


# DASHBOARD FOOTER

st.divider()

st.markdown(
    """
    <div style='text-align:center; padding:20px;'>

    <h4>🍬 Nassau Candy Profitability Analytics Dashboard</h4>

    <p>
    Developed by <b>Deepanshu Bisht</b>
    </p>

    <p>
    Domain: Data Analytics | Business Intelligence
    </p>

    <p>
    Tools: Python • Pandas • Plotly • Streamlit
    </p>

    </div>
    """,
    unsafe_allow_html=True
)