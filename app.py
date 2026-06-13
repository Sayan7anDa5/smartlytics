"""Smartphone Sales Analytics — interactive Streamlit dashboard."""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import analysis
from src.config import BRAND_COLORS, SEGMENT_COLORS, SEGMENT_ORDER
from src.data_loader import load_data


def inr(n: float) -> str:
    if n >= 1e7:
        return f"₹{n/1e7:.2f} Cr"
    if n >= 1e5:
        return f"₹{n/1e5:.2f} L"
    return f"₹{n:,.0f}"


def units_fmt(n: float) -> str:
    if n >= 1e6:
        return f"{n/1e6:.2f}M"
    if n >= 1e3:
        return f"{n/1e3:.0f}K"
    return str(int(n))


st.set_page_config(page_title="Smartphone Sales Analytics", page_icon="📱", layout="wide")


@st.cache_data
def get_data():
    return load_data()


df_all = get_data()

st.title("📱 Smartphone Sales Analytics")
st.caption("Top performing products by price segment · FY2025 · India market")

# Sidebar filters
st.sidebar.header("Filters")
seg_choice = st.sidebar.multiselect("Segment", SEGMENT_ORDER, default=SEGMENT_ORDER)
brand_choice = st.sidebar.multiselect(
    "Brand", sorted(df_all["brand"].unique()), default=[]
)
search = st.sidebar.text_input("Search model or brand")

df = df_all[df_all["segment"].isin(seg_choice)]
if brand_choice:
    df = df[df["brand"].isin(brand_choice)]
if search:
    search_query = search.lower()
    df = df[
        df["model"].str.lower().str.contains(search_query)
        | df["brand"].str.lower().str.contains(search_query)
    ]

if df.empty:
    st.warning("No products match the current filters.")
    st.stop()

# KPI cards
k = analysis.kpis(df)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Revenue", inr(k["total_revenue"]))
c2.metric("Units Sold", units_fmt(k["total_units"]))
c3.metric("Avg. Rating", f"{k['avg_rating']} ★")
c4.metric("Top Brand", k["top_brand"])
c5.metric("Segments", k["num_segments"])

# Row 1: brand revenue + segment doughnut
left, right = st.columns(2)
with left:
    st.subheader("Brand-wise Revenue")
    b = analysis.brand_rollup(df)
    fig = px.bar(
        b, x="revenue", y="brand", orientation="h",
        color="brand", color_discrete_map=BRAND_COLORS,
    )
    fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Revenue by Segment")
    s = analysis.segment_rollup(df)
    fig = px.pie(
        s, values="revenue", names="segment", hole=0.6,
        color="segment", color_discrete_map=SEGMENT_COLORS,
    )
    st.plotly_chart(fig, use_container_width=True)

# Row 2: quarterly trend + units by brand
left, right = st.columns(2)
with left:
    st.subheader("Quarterly Sales Trend by Segment")
    trend = analysis.quarterly_trend(df)
    fig = px.line(
        trend, x="quarter", y="units", color="segment", markers=True,
        color_discrete_map=SEGMENT_COLORS,
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Units Sold by Brand")
    fig = px.bar(
        b, x="brand", y="units", color="brand", color_discrete_map=BRAND_COLORS,
    )
    fig.update_layout(showlegend=False, xaxis={"categoryorder": "total descending"})
    st.plotly_chart(fig, use_container_width=True)

# Row 3: price vs rating bubble + market share
left, right = st.columns(2)
with left:
    st.subheader("Price vs Rating (bubble size = units)")
    fig = px.scatter(
        df, x="price_inr", y="rating", size="units_sold", color="segment",
        color_discrete_map=SEGMENT_COLORS, size_max=40,
        custom_data=["model", "brand", "units_sold"],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
            "Price: ₹%{x:,.0f}<br>Rating: %{y}★<br>"
            "Units: %{customdata[2]:,}<extra></extra>"
        )
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Market Share by Revenue (Top 8)")
    m = analysis.market_share(df, top=8)
    fig = go.Figure(
        go.Barpolar(
            r=m["share_pct"], theta=m["brand"],
            marker_color=[BRAND_COLORS.get(x, "#888") for x in m["brand"]],
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# Segment winners
st.subheader("🏆 Top Performers by Segment")
winners = analysis.segment_winners(df, n=3)
present = [s for s in SEGMENT_ORDER if s in winners]
cols = st.columns(len(present))
for col, seg in zip(cols, present):
    with col:
        st.markdown(f"**{seg}**")
        for _, row in winners[seg].iterrows():
            st.write(
                f"{row['model']} — {inr(row['revenue'])} "
                f"({units_fmt(row['units_sold'])} units)"
            )

# Product table
st.subheader(f"📋 Product Catalog ({len(df)} products)")
table = df[[
    "brand", "model", "segment", "price_inr", "units_sold",
    "rating", "revenue", "perf_score",
]].sort_values("revenue", ascending=False)
st.dataframe(table, use_container_width=True, hide_index=True)
