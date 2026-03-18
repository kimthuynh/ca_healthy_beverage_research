"""Google Trends 12-month CA search interest chart."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

COLORS = {
    "bg": "#111827",
    "blue": "#06B6D4",
    "green": "#2C996A",
    "red": "#F58484",
    "text": "#F9FAFB",
    "muted": "#6B7280",
    "surface": "#1F2937",
}

# Distinct line colors for up to 10 brands
LINE_PALETTE = [
    "#06B6D4", "#84E0C3", "#F58484", "#F3D487", "#A78BFA",
    "#F472B6", "#609783", "#A08066", "#699EDF", "#826386",
     "#3F5168", "#6F3477", "#204C83", "#501458", "#1F3C61",
]


def render(df: pd.DataFrame, callout: str) -> None:
    """
    df must have: brand, week, interest
    """
    st.markdown("### 📈 Google Trends — CA Search Interest (12 Months)")

    brands = df["brand"].unique()
    fig = go.Figure()

    for i, brand in enumerate(brands):
        bdf = df[df["brand"] == brand].sort_values("week")
        fig.add_trace(go.Scatter(
            x=bdf["week"],
            y=bdf["interest"],
            mode="lines",
            name=brand,
            line=dict(color=LINE_PALETTE[i % len(LINE_PALETTE)], width=2),
            hovertemplate=f"<b>{brand}</b><br>%{{x}}<br>Interest: %{{y}}<extra></extra>",
        ))

    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"], family="monospace"),
        legend=dict(
            orientation="h",
            x=0, y=-0.25,
            font=dict(color=COLORS["text"], size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=COLORS["muted"]),
            tickangle=-30,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["surface"],
            tickfont=dict(color=COLORS["muted"]),
            range=[0, 100],
            title=dict(text="Search Interest", font=dict(color=COLORS["muted"], size=11)),
        ),
        margin=dict(l=10, r=10, t=20, b=120),
        height=400,
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"<p style='color:{COLORS['muted']};font-size:13px;font-style:italic;'>{callout}</p>",
        unsafe_allow_html=True,
    )
