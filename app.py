"""Smartphone Sales Analytics — interactive Streamlit dashboard."""
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import analysis
from src.config import BRAND_COLORS, SEGMENT_COLORS, SEGMENT_ORDER
from src.data_loader import load_data

ASSETS = Path(__file__).resolve().parent / "assets"


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


def load_css(path: Path) -> None:
    st.markdown(f"<style>{path.read_text()}</style>", unsafe_allow_html=True)


def style_fig(fig: go.Figure, height: int = 320) -> go.Figure:
    """Apply the dark editorial theme to any Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", size=11, color="#B9BFC8"),
        margin=dict(l=12, r=12, t=14, b=12),
        height=height,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
            font=dict(size=10), bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor="#1B2027", bordercolor="rgba(255,255,255,0.12)",
            font=dict(family="JetBrains Mono", color="#ECEAE3", size=12),
        ),
        colorway=list(SEGMENT_COLORS.values()),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)")
    fig.update_polars(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(gridcolor="rgba(255,255,255,0.07)", color="#5B626C"),
        angularaxis=dict(gridcolor="rgba(255,255,255,0.07)", color="#B9BFC8"),
    )
    return fig


def section(title: str) -> None:
    st.markdown(
        f'<div class="section"><span class="section__bar"></span>'
        f'<span class="section__title">{title}</span>'
        f'<span class="section__line"></span></div>',
        unsafe_allow_html=True,
    )


def card_head(title: str, tag: str = "") -> None:
    st.markdown(
        f'<div class="card-head"><span class="card-title">{title}</span>'
        f'<span class="card-tag">{tag}</span></div>',
        unsafe_allow_html=True,
    )


PLOTLY_CFG = {"displayModeBar": False}

# ── Page setup ────────────────────────────────────────────────────
st.set_page_config(page_title="Smartphone Sales Analytics", page_icon="◆", layout="wide")
load_css(ASSETS / "style.css")


@st.cache_data
def get_data():
    return load_data()


df_all = get_data()

# ── Hero ──────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
      <div class="hero__mark">◆</div>
      <div>
        <div class="hero__title">Smartphone Sales Analytics</div>
        <div class="hero__sub">Top performing products by price segment</div>
      </div>
      <div class="hero__badges">
        <span class="badge">FY 2025</span>
        <span class="badge">India Market</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar filters ───────────────────────────────────────────────
st.sidebar.header("Filters")
seg_choice = st.sidebar.multiselect("Segment", SEGMENT_ORDER, default=SEGMENT_ORDER)
brand_choice = st.sidebar.multiselect("Brand", sorted(df_all["brand"].unique()), default=[])
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

# ── KPI strip ─────────────────────────────────────────────────────
k = analysis.kpis(df)
kpis = [
    ("Total Revenue", inr(k["total_revenue"]), f"Across {len(df)} products", "#F4B740"),
    ("Units Sold", units_fmt(k["total_units"]), f"{k['num_brands']} brands tracked", "#3b82f6"),
    ("Avg. Rating", f"{k['avg_rating']} ★", "All active segments", "#10b981"),
    ("Top Brand", k["top_brand"], inr(k["top_brand_revenue"]), "#8b5cf6"),
    ("Segments", str(k["num_segments"]), "Budget → Flagship", "#f59e0b"),
]
cards = "".join(
    f'<div class="kpi" style="--c:{c}"><div class="kpi__label">{label}</div>'
    f'<div class="kpi__value">{value}</div><div class="kpi__sub">{sub}</div></div>'
    for label, value, sub, c in kpis
)
st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)

# ── Revenue & market analysis ─────────────────────────────────────
section("Revenue & Market Analysis")
b = analysis.brand_rollup(df)

left, right = st.columns(2)
with left:
    with st.container(border=True):
        card_head("Brand-wise Revenue", "Revenue ranked")
        fig = px.bar(
            b, x="revenue", y="brand", orientation="h",
            color="brand", color_discrete_map=BRAND_COLORS,
        )
        fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_line_width=0, hovertemplate="%{y}<br>₹%{x:,.0f}<extra></extra>")
        st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CFG)

with right:
    with st.container(border=True):
        card_head("Revenue by Segment", "Share")
        s = analysis.segment_rollup(df)
        fig = px.pie(
            s, values="revenue", names="segment", hole=0.62,
            color="segment", color_discrete_map=SEGMENT_COLORS,
        )
        fig.update_traces(
            marker=dict(line=dict(color="#0B0D10", width=2)),
            textfont=dict(family="JetBrains Mono", size=11),
            hovertemplate="%{label}<br>₹%{value:,.0f} (%{percent})<extra></extra>",
        )
        st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CFG)

left, right = st.columns(2)
with left:
    with st.container(border=True):
        card_head("Quarterly Sales Trend", "Units by segment")
        trend = analysis.quarterly_trend(df)
        trend = trend.assign(quarter=trend["quarter"].str.upper())
        fig = px.line(
            trend, x="quarter", y="units", color="segment", markers=True,
            color_discrete_map=SEGMENT_COLORS,
        )
        fig.update_traces(line=dict(width=2.5), marker=dict(size=7),
                          hovertemplate="%{fullData.name}<br>%{y:,.0f} units<extra></extra>")
        st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CFG)

with right:
    with st.container(border=True):
        card_head("Units Sold by Brand", "Volume")
        fig = px.bar(b, x="brand", y="units", color="brand", color_discrete_map=BRAND_COLORS)
        fig.update_layout(showlegend=False, xaxis={"categoryorder": "total descending"})
        fig.update_traces(marker_line_width=0, hovertemplate="%{x}<br>%{y:,.0f} units<extra></extra>")
        st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CFG)

left, right = st.columns(2)
with left:
    with st.container(border=True):
        card_head("Price vs Rating", "Bubble = units")
        fig = px.scatter(
            df, x="price_inr", y="rating", size="units_sold", color="segment",
            color_discrete_map=SEGMENT_COLORS, size_max=42,
            custom_data=["model", "brand", "units_sold"],
        )
        fig.update_traces(
            marker=dict(line=dict(width=0.5, color="rgba(255,255,255,0.25)"), opacity=0.82),
            hovertemplate=(
                "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                "Price: ₹%{x:,.0f}<br>Rating: %{y}★<br>"
                "Units: %{customdata[2]:,}<extra></extra>"
            ),
        )
        fig.update_xaxes(title_text="Price (₹)")
        fig.update_yaxes(title_text="Rating")
        st.plotly_chart(style_fig(fig, height=340), use_container_width=True, config=PLOTLY_CFG)

with right:
    with st.container(border=True):
        card_head("Market Share by Revenue", "Top 8")
        m = analysis.market_share(df, top=8)
        fig = go.Figure(
            go.Barpolar(
                r=m["share_pct"], theta=m["brand"],
                marker_color=[BRAND_COLORS.get(x, "#888") for x in m["brand"]],
                marker_line_color="#0B0D10", marker_line_width=1.5, opacity=0.9,
                hovertemplate="%{theta}<br>%{r}%<extra></extra>",
            )
        )
        st.plotly_chart(style_fig(fig, height=340), use_container_width=True, config=PLOTLY_CFG)

# ── Segment winners ───────────────────────────────────────────────
section("Top Performers by Segment")
winners = analysis.segment_winners(df, n=3)
present = [s for s in SEGMENT_ORDER if s in winners]
win_cards = ""
for seg in present:
    rows = ""
    for i, (_, r) in enumerate(winners[seg].iterrows(), start=1):
        rows += (
            f'<div class="win-row"><span class="win-rank">{i}</span>'
            f'<span class="win-model">{r["model"]}</span>'
            f'<span class="win-rev">{inr(r["revenue"])}</span></div>'
        )
    win_cards += (
        f'<div class="win-card" style="--c:{SEGMENT_COLORS[seg]}">'
        f'<div class="win-head">{seg}</div>{rows}</div>'
    )
st.markdown(f'<div class="win-grid">{win_cards}</div>', unsafe_allow_html=True)

# ── Product catalog ───────────────────────────────────────────────
section(f"Product Catalog · {len(df)} products")
table = df[[
    "brand", "model", "segment", "price_inr", "units_sold",
    "rating", "revenue", "perf_score",
]].sort_values("revenue", ascending=False)
st.dataframe(
    table,
    hide_index=True,
    use_container_width=True,
    height=460,
    column_config={
        "brand": "Brand",
        "model": "Model",
        "segment": "Segment",
        "price_inr": st.column_config.NumberColumn("Price", format="₹%d"),
        "units_sold": st.column_config.NumberColumn("Units", format="%d"),
        "rating": st.column_config.ProgressColumn(
            "Rating", min_value=0.0, max_value=5.0, format="%.1f"
        ),
        "revenue": st.column_config.NumberColumn("Revenue", format="₹%d"),
        "perf_score": st.column_config.ProgressColumn(
            "Score", min_value=0, max_value=100, format="%d"
        ),
    },
)

st.markdown(
    '<div class="dash-foot">Smartphone Sales Analytics · illustrative FY 2025 '
    'estimates for the Indian market</div>',
    unsafe_allow_html=True,
)
